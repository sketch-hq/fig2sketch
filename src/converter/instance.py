import copy, dataclasses, logging, math
from . import base, group, shape_path as shape_path_converter, style as style_converter, variable
from .context import context
from .config import config
from converter import utils
from sketchformat.layer_group import SymbolInstance, OverrideValue
from sketchformat.style import Style
from typing import Dict, List, Optional, Sequence, Tuple
from .errors import Fig2SketchNodeChanged

GRADIENT_PAINT_TYPES = {
    "GRADIENT_LINEAR",
    "GRADIENT_RADIAL",
    "GRADIENT_ANGULAR",
    "GRADIENT_DIAMOND",
}

# Overrides on the symbol root describe the instance layer itself. These are converted
# from the instance node, so they are applied to it rather than becoming Sketch overrides
INSTANCE_LAYER_PROPS = {
    "opacity",
    "stackPositioning",
    "stackChildAlignSelf",
    "stackChildPrimaryGrow",
}

# Paint overrides, mapped to the Sketch style part they convert to. Sketch overrides cannot
# reach a master's own style, so on the symbol root these are checked against the instance
# node instead (see unsupported_root_paints)
PAINT_PROPS = {
    "fillPaints": "fill",
    "styleIdForFill": "fill",
    "strokePaints": "border",
    "styleIdForStrokeFill": "border",
}

# Size is handled by applying derivedSymbolData. The rest are surely not worth detaching
# for. Text hyperlinks are not converted for plain text layers either
IGNORED_OVERRIDE_PROPS = {
    "size",
    "pluginData",
    "name",
    "exportSettings",
    "targetAspectRatio",
    "hyperlink",
    "overrideLevel",
    "textExplicitLayoutVersion",
    "textUserLayoutVersion",
}

# Paint fields converted or intentionally dropped on paint overrides, see
# unsupported_paint_override_props
IGNORED_PAINT_PROPS = {
    "authoredColor",
    "blendMode",
    "color",
    "colorVar",
    "opacity",
    "opacityVar",
    "type",
    "visible",
}
GRADIENT_PAINT_PROPS = {
    "authoredStops",
    "interpolationColorSpace",
    "interpolationHueMethod",
    "stops",
    "stopsVar",
    "transform",
}
IMAGE_PAINT_PROPS = {"image", "imageScaleMode", "scale"}

# Component property fields, mapped to the override they convert to and the keys holding the
# value in the assignment's `value` and in its `varValue`
PROPERTY_OVERRIDE_FIELDS = {
    "OVERRIDDEN_SYMBOL_ID": ("overriddenSymbolID", "guidValue", "symbolIdValue"),
    "TEXT_DATA": ("textData", "textValue", "textDataValue"),
    "VISIBLE": ("visible", "boolValue", "boolValue"),
}


def convert(fig_instance):
    if utils.is_invalid_ref(fig_instance["symbolData"]["symbolID"]):
        # Broken instance, return a placeholder in its place
        utils.log_conversion_warning("SYM001", fig_instance)
        return group.convert(fig_instance)

    # Use always the GUID of the master for the symbolID
    # The instance symbolID can refer to the overrideKey instead
    fig_master = context.find_symbol(fig_instance["symbolData"]["symbolID"])

    all_overrides = get_all_overrides(fig_instance)
    unsupported_root = unsupported_root_paints(fig_instance, fig_master, all_overrides)
    all_overrides = apply_root_overrides_to_instance(fig_instance, all_overrides)
    sketch_overrides, unsupported = convert_overrides(all_overrides, fig_instance)
    # Props overridden on the symbol root belong to the instance layer itself
    unsupported += [(prop, fig_instance["name"]) for prop in unsupported_root]

    opacity = instance_opacity(fig_instance, fig_master)
    if opacity is None:
        unsupported.append(("opacity", fig_instance["name"]))

    if unsupported:
        layers = unsupported_layers(unsupported)
        if config.can_detach:
            utils.log_conversion_warning("SYM003", fig_instance, props=list(layers), layers=layers)

            # Modify input tree in place, with the detached symbol subtree
            detach_symbol(fig_instance, all_overrides)

            # Raise an exception to trigger conversion of the detached node
            raise Fig2SketchNodeChanged()
        else:
            utils.log_conversion_warning("SYM002", fig_instance, props=list(layers), layers=layers)

    obj = SymbolInstance(
        **base.base_styled(fig_instance),
        symbolID=utils.gen_object_id(fig_master["guid"]),
        scale=instance_scale(fig_instance),
        overrideValues=sketch_overrides,
    )
    # Replace style
    obj.style = Style(do_objectID=utils.gen_object_id(fig_instance["guid"], b"style"))
    obj.style.contextSettings.opacity = 1 if opacity is None else opacity

    return obj


def instance_opacity(fig_instance: dict, fig_master: dict) -> Optional[float]:
    """Sketch draws an instance with its master's opacity on top of the instance's own,
    while in the fig format the instance's opacity replaces the master's.

    Returns the Sketch instance opacity that gives the same result, or None when the
    instance is more opaque than its master, which Sketch cannot draw.
    """
    opacity = fig_instance.get("opacity", 1)
    master_opacity = fig_master.get("opacity", 1)

    if math.isclose(opacity, master_opacity, abs_tol=1e-6):
        return 1
    if opacity < master_opacity:
        return opacity / master_opacity

    return None


def instance_scale(fig_instance: dict) -> float:
    """The factor the instance was scaled by as a whole, text and borders included.

    Sketch's scale works the same way: the master is laid out at the instance size divided
    by the scale, then drawn scaled. Any other resize, even a proportional one, only changes
    the size the master is laid out at, so it leaves the scale at 1.
    """
    return fig_instance["symbolData"].get("uniformScaleFactor", 1)


def post_process(fig_instance, sketch_instance):
    if sketch_instance._class == "group":
        return group.post_process_frame_as_group(fig_instance, sketch_instance)
    else:
        return sketch_instance


def master_instance(fig_symbol):
    obj = SymbolInstance(
        **base.base_styled(fig_symbol),
        symbolID=utils.gen_object_id(fig_symbol["guid"]),
    )
    obj.do_objectID = utils.gen_object_id(fig_symbol["guid"], b"master_instance")

    # Replace style
    obj.style = Style(
        do_objectID=utils.gen_object_id(fig_symbol["guid"], b"master_instance_style")
    )

    return obj


def convert_overrides(all_overrides, fig_instance):
    """Convert overrides, pairing each unsupported prop with the layer it overrides."""
    sketch_overrides = []
    unsupported_overrides = []
    for override in all_overrides:
        sk, us = convert_override(override, fig_instance)
        sketch_overrides += sk
        if us:
            layer = override_layer_path(override, fig_instance)
            unsupported_overrides += [(prop, layer) for prop in us]

    return sketch_overrides, unsupported_overrides


def override_layer_path(override: dict, fig_instance: dict) -> str:
    """Name path of the overridden layer, starting at the instance."""
    fig_master = context.find_symbol(fig_instance["symbolData"]["symbolID"])
    root_guid = fig_master.get("overrideKey", fig_master["guid"])
    names = [
        context.fig_node(guid)["name"]
        for guid in override["guidPath"]["guids"]
        if guid != root_guid
    ]
    return "/".join([fig_instance["name"], *names])


def unsupported_layers(unsupported: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Group unsupported props by name, listing each overridden layer once."""
    layers: Dict[str, List[str]] = {}
    for prop, layer in unsupported:
        prop_layers = layers.setdefault(prop, [])
        if layer not in prop_layers:
            prop_layers.append(layer)
    return layers


def unsupported_root_paints(
    fig_instance: dict, fig_master: dict, all_overrides: list
) -> List[str]:
    """Report root paint overrides that leave the instance styled unlike its master.

    The override holds the paint as it was authored, which can be stale: a paint bound to
    a variable resolves differently under another variable mode. The instance node holds
    the paints it ends up with, so those are compared against the master's.
    """
    root_guid = fig_master.get("overrideKey", fig_master["guid"])
    parts = {
        PAINT_PROPS[prop]
        for override in all_overrides
        if override["guidPath"]["guids"] == [root_guid]
        for prop in override
        if prop in PAINT_PROPS
    }

    unsupported = []
    for part in sorted(parts):
        prop = "strokePaints" if part == "border" else "fillPaints"
        paints = fig_instance.get(prop, [])
        mode_scope = override_mode_scope(fig_instance, [fig_master])
        sk, us = convert_style_part_overrides("", part, paints, fig_master, mode_scope)
        if sk or us or len(paints) != len(master_paints(fig_master, part)):
            unsupported.append(prop)

    return unsupported


def apply_root_overrides_to_instance(fig_instance: dict, all_overrides: list) -> list:
    fig_master = context.find_symbol(fig_instance["symbolData"]["symbolID"])
    root_guid = fig_master.get("overrideKey", fig_master["guid"])
    remaining_overrides = []

    for override in all_overrides:
        if override["guidPath"]["guids"] != [root_guid]:
            remaining_overrides.append(override)
            continue

        remaining_root_override = {"guidPath": override["guidPath"]}
        for prop, value in override.items():
            if prop == "guidPath":
                continue
            if prop in INSTANCE_LAYER_PROPS:
                fig_instance[prop] = value
            elif prop not in PAINT_PROPS:
                remaining_root_override[prop] = value

        if len(remaining_root_override) > 1:
            remaining_overrides.append(remaining_root_override)

    return remaining_overrides


def get_all_overrides(fig_instance):
    """Gets all overrides of a symbol, including component assignments"""

    # Convert top-level properties to overrides
    fig_master = context.find_symbol(fig_instance["symbolData"]["symbolID"])
    all_overrides = convert_properties_to_overrides(
        fig_master, fig_instance.get("componentPropAssignments", [])
    )

    # Sort overrides by length of path. This ensures top level overrides are processed before
    # nested ones which is required because a top override may change the symbol instance that is
    # used by child overrides
    for override in sorted(
        fig_instance["symbolData"]["symbolOverrides"],
        key=lambda x: len(x["guidPath"]["guids"]),
    ):
        guid_path = override["guidPath"]["guids"]
        new_override = {"guidPath": override["guidPath"]}
        for prop, value in override.items():
            if prop == "componentPropAssignments":
                nested_master = find_symbol_master(fig_master, guid_path, all_overrides)
                all_overrides += convert_properties_to_overrides(nested_master, value, guid_path)
            else:
                new_override[prop] = value

        all_overrides.append(new_override)

    # Do a pass to eliminate duplicate overrides, we use an ordered dict to keep them sorted
    unique_overrides = []
    for ov in all_overrides:
        guid = ov["guidPath"]["guids"]
        existing = [i for i in unique_overrides if i["guidPath"]["guids"] == guid]
        if existing:
            # Add properties to the previous override. Priority goes to the first item
            # because we want to prioritize prop assignments which we always convert first
            for k, v in ov.items():
                if k == "guidPath":
                    continue
                if k not in existing[0]:
                    existing[0][k] = v
        else:
            unique_overrides.append(ov)

    return unique_overrides


def convert_override(override: dict, fig_instance: dict) -> Tuple[List[OverrideValue], List[str]]:
    sketch_overrides = []
    unsupported_overrides = []

    try:
        fig_nodes = [context.fig_node(guid) for guid in override["guidPath"]["guids"]]
        # Convert uuids in the path from top symbol to child instance
        sketch_path = [sketch_override_object_id(fig_node) for fig_node in fig_nodes]
        sketch_path_str = "/".join(sketch_path)
    except KeyError as e:
        # Cannot find where to apply override
        utils.log_conversion_warning("SYM004", fig_instance, node_ref=e.args[0])
        return [], []

    for prop, value in override.items():
        if prop == "guidPath":
            continue
        if prop == "textData":
            # Text override.
            if "styleOverrideTable" in value:
                unsupported_overrides.append("textData.styleOverrideTable")
                continue

            sketch_overrides.append(
                OverrideValue(
                    overrideName=f"{sketch_path_str}_stringValue",
                    value=value["characters"],
                )
            )
        elif prop == "overriddenSymbolID":
            sketch_overrides.append(
                OverrideValue(
                    overrideName=f"{sketch_path_str}_symbolID",
                    value=utils.gen_object_id(value),
                )
            )
        elif prop in ("fillPaints", "strokePaints") and paints_follow_style(override, prop):
            # The style ref alongside converts in their place
            continue
        elif prop in PAINT_PROPS:
            convert_paints = (
                convert_style_ref_override
                if prop.startswith("styleId")
                else convert_style_part_overrides
            )
            mode_scope = override_mode_scope(fig_instance, fig_nodes)
            sk, us = convert_paints(
                sketch_path_str, PAINT_PROPS[prop], value, fig_nodes[-1], mode_scope
            )
            if sk and splits_into_regions(fig_nodes[-1]):
                # The override would land on the group holding the region layers, which
                # carry the paints, so it would have no effect
                sk, us = [], us + ["regions"]
            sketch_overrides += sk
            unsupported_overrides += [f"{prop}.{p}" for p in us]
        elif prop == "effects":
            sk, us = convert_effect_overrides(sketch_path_str, value)
            sketch_overrides += sk
            unsupported_overrides += [f"effects.{p}" for p in us]
        elif prop in IGNORED_OVERRIDE_PROPS:
            pass
        else:
            # Unknown override
            unsupported_overrides.append(prop)

    return sketch_overrides, unsupported_overrides


def splits_into_regions(fig_node: dict) -> bool:
    """Whether a vector converts to a group of one layer per region"""
    return (
        fig_node["type"] == "VECTOR"
        and "vectorNetwork" in fig_node
        and len(shape_path_converter.get_all_segments(fig_node["vectorNetwork"])) > 1
    )


def paints_follow_style(override: dict, paints_key: str) -> bool:
    """Whether an override's paints are only a copy of the style it also applies.

    A layer using a style carries a copy of the style's paints, which can be out of
    date, so the style is what decides them.
    """
    _, ref_key = base.PAINT_STYLE_KEYS[paints_key]
    style_ref = override.get(ref_key)
    return style_ref is not None and not utils.is_invalid_style_ref(style_ref)


def override_mode_scope(fig_instance: dict, fig_nodes: List[dict]) -> List[dict]:
    """The nodes that can set the variable modes an override resolves in, nearest first.

    The override's path leads through any nested instances to a node in a master. Modes
    set within a master apply first, then one set on the instance using it, then one set
    on the master itself, and then those of wherever the instance sits.
    """
    mode_scope: List[dict] = []
    node: Optional[dict] = fig_nodes[-1]
    # Each node on the path sits in the master of the instance before it
    for instance in reversed([fig_instance, *fig_nodes[:-1]]):
        while node is not None and node["type"] != "SYMBOL":
            mode_scope.append(node)
            node = variable.parent_node(node)

        mode_scope.append(instance)
        if node is not None:
            mode_scope.append(node)

        node = variable.parent_node(instance)

    if node is not None:
        mode_scope += variable.ancestors(node)

    return mode_scope


def sketch_override_object_id(fig_node: dict) -> str:
    if fig_node["type"] != "VECTOR" or "vectorNetwork" not in fig_node:
        return utils.gen_object_id(fig_node["guid"])

    regions = shape_path_converter.get_all_segments(fig_node["vectorNetwork"])
    if len(regions) != 1:
        return utils.gen_object_id(fig_node["guid"])

    if len(regions[0]["loops"]) == 1:
        return utils.gen_object_id(fig_node["guid"], b"region0loop0")

    return utils.gen_object_id(fig_node["guid"], b"region0")


def convert_effect_overrides(
    sketch_path_str: str, effects: list
) -> Tuple[List[OverrideValue], List[str]]:
    sketch_overrides = []
    unsupported_overrides = []
    effect_indexes = {"shadow": 0, "innershadow": 0}

    for effect in effects:
        if effect["type"] == "DROP_SHADOW":
            part = "shadow"
        elif effect["type"] == "INNER_SHADOW":
            part = "innershadow"
        else:
            unsupported_overrides.append(effect["type"])
            continue

        part_path = f"{part}-{effect_indexes[part]}"
        effect_indexes[part] += 1

        if "color" in effect:
            sketch_overrides.append(
                OverrideValue(
                    overrideName=f"{sketch_path_str}_color:{part_path}",
                    value=style_converter.convert_color(effect["color"]),
                )
            )

    return sketch_overrides, unsupported_overrides


def convert_style_ref_override(
    sketch_path_str: str,
    sketch_part: str,
    style_ref: dict,
    master_node: dict,
    mode_scope: Sequence[dict],
) -> Tuple[List[OverrideValue], List[str]]:
    # A detached style leaves the paints carried on the override to convert instead
    if utils.is_invalid_style_ref(style_ref):
        return [], []

    fig_style = context.fig_node_by_ref(style_ref)
    if fig_style is None:
        return [], ["assetRef|guid"]

    if "fillPaints" not in fig_style:
        return [], ["fillPaints"]

    sketch_overrides, unsupported_overrides = convert_style_part_overrides(
        sketch_path_str,
        sketch_part,
        fig_style["fillPaints"],
        master_node,
        mode_scope,
    )

    # Link the colour to the style's swatch, as for a layer using the style. The swatch
    # holds the style paint's opacity in its alpha, which an override sets on its own,
    # so the two have to agree
    _, swatch = context.component(fig_style["guid"])
    if swatch is not None:
        color_override_name = f"{sketch_path_str}_color:{sketch_part}-0"
        for sketch_override in sketch_overrides:
            if (
                sketch_override.overrideName == color_override_name
                and sketch_override.value.alpha == swatch.value.alpha
            ):
                sketch_override.value = dataclasses.replace(swatch.value)

    return sketch_overrides, unsupported_overrides


def master_paints(fig_node: dict, sketch_part: str) -> list:
    if sketch_part == "border":
        return fig_node.get("strokePaints", [])

    if fig_node["type"] == "VECTOR" and "vectorNetwork" in fig_node:
        regions = shape_path_converter.get_all_segments(fig_node["vectorNetwork"])
        if len(regions) == 1:
            return regions[0]["style"].get("fillPaints", fig_node.get("fillPaints", []))

    return fig_node.get("fillPaints", [])


def convert_style_part_overrides(
    sketch_path_str: str,
    sketch_part: str,
    paints: list,
    master_node: dict,
    mode_scope: Sequence[dict],
) -> Tuple[List[OverrideValue], List[str]]:
    """Converts override paints into the Sketch overrides that differ from the master's.

    The override's colours resolve their variables in mode_scope, where the instance is.
    The master's resolve them where the master is, as they do when the master converts.
    """
    sketch_overrides = []
    unsupported_overrides = []
    master_part_paints = master_paints(master_node, sketch_part)

    for index, paint in enumerate(paints):
        part_path = f"{sketch_part}-{index}"
        master_paint = master_part_paints[index] if index < len(master_part_paints) else {}

        if "color" in paint:
            if paint.get("type") == "SOLID":
                # Like convert_fill, fold the paint opacity into the color alpha: Sketch
                # ignores an _opacity override on a solid fill or border
                color = variable.linked_color(
                    style_converter.convert_color(paint["color"], paint.get("opacity", 1)),
                    paint,
                    mode_scope,
                )
                master_color = (
                    variable.linked_color(
                        style_converter.convert_color(
                            master_paint["color"], master_paint.get("opacity", 1)
                        ),
                        master_paint,
                        variable.ancestors(master_node),
                    )
                    if master_paint.get("type") == "SOLID" and "color" in master_paint
                    else None
                )
                if color != master_color:
                    sketch_overrides.append(
                        OverrideValue(
                            overrideName=f"{sketch_path_str}_color:{part_path}",
                            value=color,
                        )
                    )
            else:
                unsupported_overrides.append("color")

        if paint.get("type") in GRADIENT_PAINT_TYPES and "stops" in paint and "transform" in paint:
            gradient = style_converter.convert_gradient(master_node, paint)
            master_gradient = (
                style_converter.convert_gradient(master_node, master_paint)
                if master_paint.get("type") in GRADIENT_PAINT_TYPES
                and "stops" in master_paint
                and "transform" in master_paint
                else None
            )
            if gradient != master_gradient:
                sketch_overrides.append(
                    OverrideValue(
                        overrideName=f"{sketch_path_str}_color:{part_path}",
                        value=gradient,
                    )
                )

        blend_mode = style_converter.BLEND_MODE[paint.get("blendMode", "NORMAL")]
        master_blend_mode = style_converter.BLEND_MODE[master_paint.get("blendMode", "NORMAL")]
        if "blendMode" in paint and blend_mode != master_blend_mode:
            sketch_overrides.append(
                OverrideValue(
                    overrideName=f"{sketch_path_str}_blendMode:{part_path}",
                    value=blend_mode,
                )
            )

        if (
            paint.get("type") != "SOLID"
            and "opacity" in paint
            and paint["opacity"] != master_paint.get("opacity", 1)
        ):
            sketch_overrides.append(
                OverrideValue(
                    overrideName=f"{sketch_path_str}_opacity:{part_path}",
                    value=paint["opacity"],
                )
            )

        unsupported_overrides += unsupported_paint_override_props(paint)

    return sketch_overrides, unsupported_overrides


def unsupported_paint_override_props(paint: dict) -> List[str]:
    """Return paint override fields that are unsafe to keep on an attached instance.

    Properties in the *_PAINT_PROPS sets are supported or intentionally dropped because
    Sketch has no equivalent override representation. Any remaining fields are reported as
    unsupported so the instance can detach rather than silently losing data the converter does
    not understand.

    Variable bindings (colorVar, opacityVar) and authored colors sit alongside the resolved
    color and opacity, which is what gets converted, same as for paints outside overrides.
    """
    if paint.get("type") == "SOLID":
        return [prop for prop in paint if prop not in IGNORED_PAINT_PROPS]

    if paint.get("type") in GRADIENT_PAINT_TYPES:
        return [
            prop
            for prop in paint
            if prop not in IGNORED_PAINT_PROPS and prop not in GRADIENT_PAINT_PROPS
        ]

    return [
        prop for prop in paint if prop not in IGNORED_PAINT_PROPS and prop not in IMAGE_PAINT_PROPS
    ]


def find_symbol_master(root_symbol, guid_path, overrides):
    current_symbol = root_symbol
    path = []
    for guid in guid_path:
        path.append(guid)
        # See if we have overriden the symbol_id
        symbol_id = [
            o["overriddenSymbolID"]
            for o in overrides
            if o["guidPath"]["guids"] == path and "overriddenSymbolID" in o
        ]
        if symbol_id:
            symbol_id = symbol_id[0]
        else:
            # Otherwise, find the instance
            instance = context.fig_node(guid)
            symbol_id = instance["symbolData"]["symbolID"]

        current_symbol = context.find_symbol(symbol_id)

    return current_symbol


def convert_properties_to_overrides(fig_master, properties, guid_path=[]):
    """Convert .fig property assignments to overrides.
    This makes it easier to work with them in a unified way."""
    overrides = []

    for prop in properties:
        for ref_prop, ref_guid in find_refs(fig_master, prop["defID"]):
            field = ref_prop["componentPropNodeField"]
            if field not in PROPERTY_OVERRIDE_FIELDS:  # INHERIT_FILL_STYLE_ID
                raise Exception(f"Unexpected property {field}")

            value = property_value(prop, field)
            # Without a value (e.g. bound to a variable) the layer keeps the master's value
            if value is None:
                continue

            override_prop = PROPERTY_OVERRIDE_FIELDS[field][0]
            overrides.append({override_prop: value, "guidPath": {"guids": guid_path + [ref_guid]}})

    return overrides


def property_value(prop, field):
    """Get the value of a property assignment for a node field.

    Older files store it in `value`. Newer ones may leave `value` out or empty and only store
    it in `varValue`, the same way variables store their values."""
    _, legacy_key, var_key = PROPERTY_OVERRIDE_FIELDS[field]
    if legacy_key in prop.get("value", {}):
        return prop["value"][legacy_key]

    value = prop.get("varValue", {}).get("value", {}).get(var_key)
    if var_key == "symbolIdValue" and value is not None:
        return value.get("guid")
    return value


def find_refs(node, ref_id):
    """Find all usages of a property in a symbol, recursively"""
    refs = [
        (ref, node.get("overrideKey", node["guid"]))
        for ref in node.get("componentPropRefs", [])
        if (
            ("defID" in ref and ref["defID"] == ref_id)
            or ("zombieFallbackName" in ref and ref["zombieFallbackName"] == ref_id)
        )
        and not ref.get("isDeleted", False)
    ]

    for ch in node.get("children", []):
        refs += find_refs(ch, ref_id)

    return refs


def detach_symbol(fig_instance, all_overrides):
    # Find symbol master
    fig_master = context.fig_node(fig_instance["symbolData"]["symbolID"])
    detached_children = copy.deepcopy(fig_master["children"], {})

    # Apply overrides to children
    scale = instance_scale(fig_instance)
    for c in detached_children:
        apply_overrides(
            c,
            fig_instance["guid"],
            fig_instance["guid"],
            all_overrides,
            fig_instance.get("derivedSymbolData", []),
            scale,
        )

    fig_instance["children"] = detached_children
    fig_instance["type"] = "FRAME"
    fig_instance["f2s_detached"] = True


def apply_overrides(fig_node, instance_id, parent_id, overrides, derived_symbol_data, scale=1):
    guid = fig_node.get("overrideKey", fig_node["guid"])

    # Apply overrides
    child_overrides = []
    for override in overrides:
        guids = override["guidPath"]["guids"]
        if guids[0] != guid:
            continue
        if len(guids) > 1:
            child_overrides.append({**override, "guidPath": {"guids": guids[1:]}})
        else:
            for k, v in override.items():
                if k == "guidPath":
                    continue
                elif k == "overriddenSymbolID":
                    fig_node["symbolData"]["symbolID"] = v
                else:
                    fig_node[k] = v

    # Recalculate size
    child_derived_data = []
    for derived in derived_symbol_data:
        guids = derived["guidPath"]["guids"]
        if guids[0] != guid:
            continue
        if len(guids) > 1:
            child_derived_data.append({**derived, "guidPath": {"guids": guids[1:]}})
        else:
            if "size" in derived:
                fig_node["size"] = derived["size"]
            if "transform" in derived:
                fig_node["transform"] = derived["transform"]
            # Should we do all properties instead?
            # A lot of them can be potentially set by derived data
            # by things like scaling the instance
            if "strokeWeight" in derived:
                fig_node["strokeWeight"] = derived["strokeWeight"]

    # Generate a unique ID by concatenating instance_id + node_id
    fig_node["guid"] = tuple(j for i in (instance_id, fig_node["guid"]) for j in i)

    # The copy sits in the instance, so walking up from it, for the variable modes or auto
    # layout that apply, passes through the instance and the layers around it
    fig_node["parent"] = {**fig_node.get("parent", {}), "guid": parent_id}
    context.add_fig_node(fig_node)

    # If it's an instance, pass the overrides down. Otherwise, convert the children
    if fig_node["type"] == "INSTANCE":
        fig_node["symbolData"]["symbolOverrides"] += child_overrides
        fig_node["derivedSymbolData"] += child_derived_data
        # Its derived size includes the scale of the instance being detached, so its own
        # scale has to as well
        fig_node["symbolData"]["uniformScaleFactor"] = instance_scale(fig_node) * scale
    else:
        if fig_node.get("f2s_detached"):
            # This was previously an instance that was detached before this usage
            # We didn't change the override keys of children, and they are still relative
            # to the symbol, so we have to pass the key without our guid prefix
            overrides = child_overrides
            derived_symbol_data = child_derived_data

        for c in fig_node.get("children", []):
            apply_overrides(
                c, instance_id, fig_node["guid"], overrides, derived_symbol_data, scale
            )
