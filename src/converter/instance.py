import copy, logging
from . import base, group, shape_path as shape_path_converter, style as style_converter
from .context import context
from .config import config
from converter import utils
from sketchformat.layer_group import SymbolInstance, OverrideValue
from sketchformat.style import Style
from typing import List, Tuple
from .errors import Fig2SketchNodeChanged, Fig2SketchWarning

GRADIENT_PAINT_TYPES = {
    "GRADIENT_LINEAR",
    "GRADIENT_RADIAL",
    "GRADIENT_ANGULAR",
    "GRADIENT_DIAMOND",
}


def convert(fig_instance):
    if utils.is_invalid_ref(fig_instance["symbolData"]["symbolID"]):
        # Broken instance, return a placeholder in its place
        utils.log_conversion_warning("SYM001", fig_instance)
        return group.convert(fig_instance)

    all_overrides = get_all_overrides(fig_instance)
    all_overrides = apply_root_overrides_to_instance(fig_instance, all_overrides)
    sketch_overrides, unsupported = convert_overrides(all_overrides, fig_instance)
    if unsupported:
        if config.can_detach:
            utils.log_conversion_warning("SYM003", fig_instance, props=unsupported)

            # Modify input tree in place, with the detached symbol subtree
            detach_symbol(fig_instance, all_overrides)

            # Raise an exception to trigger conversion of the detached node
            raise Fig2SketchNodeChanged()
        else:
            utils.log_conversion_warning("SYM002", fig_instance, props=unsupported)

    # Use always the GUID of the master for the symbolID
    # The instance symbolID can refer to the overrideKey instead
    fig_master = context.find_symbol(fig_instance["symbolData"]["symbolID"])
    obj = SymbolInstance(
        **base.base_styled(fig_instance),
        symbolID=utils.gen_object_id(fig_master["guid"]),
        scale=instance_scale(fig_instance, fig_master),
        overrideValues=sketch_overrides,
    )
    # Replace style
    obj.style = Style(do_objectID=utils.gen_object_id(fig_instance["guid"], b"style"))
    obj.style.contextSettings.opacity = fig_instance.get("opacity", 1)

    return obj


def instance_scale(fig_instance: dict, fig_master: dict) -> float:
    scale_x = utils.safe_div(fig_instance["size"]["x"], fig_master["size"]["x"])
    scale_y = utils.safe_div(fig_instance["size"]["y"], fig_master["size"]["y"])

    if not scale_x:
        return scale_y or 1
    if not scale_y:
        return scale_x

    return scale_x


def post_process(fig_instance, sketch_instance):
    if sketch_instance._class == "group":
        return group.post_process_frame(fig_instance, sketch_instance)
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
    sketch_overrides = []
    unsupported_overrides = []
    for override in all_overrides:
        sk, us = convert_override(override, fig_instance)
        sketch_overrides += sk
        unsupported_overrides += us

    return sketch_overrides, unsupported_overrides


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
            if prop == "opacity":
                fig_instance["opacity"] = value
            else:
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
        elif prop == "fillPaints":
            sk, us = convert_style_part_overrides(
                sketch_path_str,
                "fill",
                value,
                fig_nodes[-1],
            )
            sketch_overrides += sk
            unsupported_overrides += [f"fillPaints.{p}" for p in us]
        elif prop == "strokePaints":
            sk, us = convert_style_part_overrides(
                sketch_path_str,
                "border",
                value,
                fig_nodes[-1],
            )
            sketch_overrides += sk
            unsupported_overrides += [f"strokePaints.{p}" for p in us]
        elif prop == "styleIdForFill":
            sk, us = convert_style_ref_override(
                sketch_path_str,
                "fill",
                value,
                fig_nodes[-1],
            )
            sketch_overrides += sk
            unsupported_overrides += [f"styleIdForFill.{p}" for p in us]
        elif prop == "styleIdForStroke":
            sk, us = convert_style_ref_override(
                sketch_path_str,
                "border",
                value,
                fig_nodes[-1],
            )
            sketch_overrides += sk
            unsupported_overrides += [f"styleIdForStroke.{p}" for p in us]
        elif prop == "effects":
            sk, us = convert_effect_overrides(sketch_path_str, value)
            sketch_overrides += sk
            unsupported_overrides += [f"effects.{p}" for p in us]
        elif prop in ["size", "pluginData", "name", "exportSettings", "targetAspectRatio"]:
            # Size is handled by applying derivedSymbolData
            # The rest are surely not worth detaching for
            pass
        else:
            # Unknown override
            unsupported_overrides.append(prop)

    return sketch_overrides, unsupported_overrides


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
) -> Tuple[List[OverrideValue], List[str]]:
    asset_ref = style_ref.get("assetRef")
    if asset_ref is None:
        return [], []

    try:
        fig_style = context.fig_node_by_key(asset_ref["key"])
    except (Fig2SketchWarning, KeyError):
        return [], ["assetRef"]

    if "fillPaints" not in fig_style:
        return [], ["fillPaints"]

    return convert_style_part_overrides(
        sketch_path_str,
        sketch_part,
        fig_style["fillPaints"],
        master_node,
    )


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
) -> Tuple[List[OverrideValue], List[str]]:
    sketch_overrides = []
    unsupported_overrides = []
    master_part_paints = master_paints(master_node, sketch_part)

    for index, paint in enumerate(paints):
        part_path = f"{sketch_part}-{index}"
        master_paint = master_part_paints[index] if index < len(master_part_paints) else {}

        if "color" in paint:
            if paint.get("type") == "SOLID":
                color = style_converter.convert_color(paint["color"])
                master_color = (
                    style_converter.convert_color(master_paint["color"])
                    if "color" in master_paint
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

        if "opacity" in paint and paint["opacity"] != master_paint.get("opacity", 1):
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

    Properties listed below are supported or intentionally dropped becuase Sketch has no
    equivalent override representation. Any remaining fields are reported as unsupported
    so the instance can detach rather than silently losing data the converter does not
    understand.
    """
    ignored_props = {"blendMode", "color", "opacity", "type", "visible"}
    if paint.get("type") == "SOLID":
        return [prop for prop in paint if prop not in ignored_props]

    if paint.get("type") in GRADIENT_PAINT_TYPES:
        gradient_props = {
            "interpolationColorSpace",
            "interpolationHueMethod",
            "stops",
            "stopsVar",
            "transform",
        }
        return [prop for prop in paint if prop not in ignored_props and prop not in gradient_props]

    return [
        prop
        for prop in paint
        if prop not in ignored_props and prop not in ["image", "imageScaleMode", "scale"]
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
            if ref_prop["componentPropNodeField"] == "OVERRIDDEN_SYMBOL_ID":
                override = {"overriddenSymbolID": prop["value"]["guidValue"]}
            elif ref_prop["componentPropNodeField"] == "TEXT_DATA":
                override = {"textData": prop["value"]["textValue"]}
            elif ref_prop["componentPropNodeField"] == "VISIBLE":
                override = {"visible": prop["value"]["boolValue"]}
            else:  # INHERIT_FILL_STYLE_ID
                raise Exception(f"Unexpected property {ref_prop['componentPropNodeField']}")

            overrides.append({**override, "guidPath": {"guids": guid_path + [ref_guid]}})

    return overrides


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
    for c in detached_children:
        apply_overrides(
            c, fig_instance["guid"], all_overrides, fig_instance.get("derivedSymbolData", [])
        )

    fig_instance["children"] = detached_children
    fig_instance["type"] = "FRAME"
    fig_instance["f2s_detached"] = True


def apply_overrides(fig_node, instance_id, overrides, derived_symbol_data):
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

    # If it's an instance, pass the overrides down. Otherwise, convert the children
    if fig_node["type"] == "INSTANCE":
        fig_node["symbolData"]["symbolOverrides"] += child_overrides
        fig_node["derivedSymbolData"] += child_derived_data
    else:
        if fig_node.get("f2s_detached"):
            # This was previously an instance that was detached before this usage
            # We didn't change the override keys of children, and they are still relative
            # to the symbol, so we have to pass the key without our guid prefix
            overrides = child_overrides
            derived_symbol_data = child_derived_data

        for c in fig_node.get("children", []):
            apply_overrides(c, instance_id, overrides, derived_symbol_data)
