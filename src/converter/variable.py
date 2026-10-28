import dataclasses
from . import style
from .context import context
from .errors import Fig2SketchWarning
from converter import utils
from sketchformat.document import Swatch
from sketchformat.style import Color
from typing import Dict, FrozenSet, Iterable, Iterator, Optional, Sequence, Tuple

ModeID = Tuple[int, ...]


def convert(fig_variable: dict) -> Dict[ModeID, Swatch]:
    """Converts a fig colour variable into a Sketch swatch for each of its modes.

    A swatch holds a single colour, while a variable holds one for every mode of its
    collection, so each mode becomes a swatch of its own. Swatches are grouped by
    collection and then by mode, as in Theme/Dark/Surface. A collection with a single
    mode has no modes to tell apart, so its swatches sit directly in the collection's
    group.
    """
    if fig_variable.get("variableResolvedType") != "COLOR":
        return {}

    fig_collection = collection(fig_variable)
    if fig_collection is None:
        return {}

    modes = context.variable_modes(fig_collection)
    swatches = {}
    for mode in modes:
        mode_id = tuple(mode["id"])
        fig_color = resolve_color(fig_variable, mode_id)
        if fig_color is None:
            continue

        uuid = utils.gen_object_id(tuple(fig_variable["guid"]) + mode_id, b"swatch")
        name = fig_variable["name"]
        if len(modes) > 1:
            name = f"{mode['name']}/{name}"
        name = f"{fig_collection['name']}/{name}"

        color = style.convert_color(fig_color)
        color.swatchID = uuid
        swatches[mode_id] = Swatch(do_objectID=uuid, name=name, value=color)

    return swatches


def convert_all(fig_nodes: Iterable[dict]) -> None:
    """Converts every colour variable of a file into swatches, whether used or not."""
    for fig_node in fig_nodes:
        if fig_node["type"] == "VARIABLE" and not fig_node.get("isSoftDeleted"):
            context.variable_swatches(fig_node)


def collection(fig_variable: dict) -> Optional[dict]:
    return context.fig_node_by_ref(fig_variable["variableSetID"])


def default_mode(fig_collection: dict) -> Optional[ModeID]:
    modes = context.variable_modes(fig_collection)
    if not modes:
        return None

    return tuple(modes[0]["id"])


def mode_value(fig_variable: dict, mode_id: Sequence[int]) -> Optional[dict]:
    for entry in fig_variable.get("variableDataValues", {}).get("entries", []):
        if tuple(entry["modeID"]) == tuple(mode_id):
            return entry["variableData"]["value"]

    return None


def resolve_color(
    fig_variable: dict, mode_id: Sequence[int], seen: FrozenSet[Sequence[int]] = frozenset()
) -> Optional[dict]:
    """Resolves the colour a variable takes in a mode, following any aliases."""
    value = mode_value(fig_variable, mode_id)
    if value is None:
        return None

    if "colorValue" in value:
        return value["colorValue"]

    if "alias" not in value:
        return None

    target = context.fig_node_by_ref(value["alias"])
    seen = seen | {tuple(fig_variable["guid"])}
    if target is None or tuple(target["guid"]) in seen:
        return None

    target_collection = collection(target)
    if target_collection is None:
        return None

    # An alias within its own collection resolves in the same mode. One into another
    # collection resolves in whatever mode a layer picks for that collection, which a
    # swatch cannot follow, so it takes that collection's default mode instead
    if target_collection is collection(fig_variable):
        target_mode: Optional[Sequence[int]] = mode_id
    else:
        target_mode = default_mode(target_collection)

    if target_mode is None:
        return None

    return resolve_color(target, target_mode, seen)


def parent_node(fig_node: dict) -> Optional[dict]:
    parent = fig_node.get("parent")
    if parent is None:
        return None

    try:
        return context.fig_node(tuple(parent["guid"]))
    except Fig2SketchWarning:
        return None


def ancestors(fig_node: dict) -> Iterator[dict]:
    """The node followed by the layers it sits in, nearest first."""
    node: Optional[dict] = fig_node
    while node is not None:
        yield node
        node = parent_node(node)


def active_mode(mode_scope: Iterable[dict], fig_collection: dict) -> Optional[ModeID]:
    """Finds the mode a layer resolves the variables of a collection in.

    That is the mode set for the collection by the first node in the layer's mode scope
    that sets one, or the collection's default mode where none does. A layer's mode
    scope is its ancestors, unless it is reached through an instance.
    """
    for node in mode_scope:
        for entry in node.get("variableModeBySetMap", {}).get("entries", []):
            if context.fig_node_by_ref(entry["variableSetID"]) is fig_collection:
                return tuple(entry["variableModeID"])

    return default_mode(fig_collection)


def paint_variable(fig_paint: dict) -> Optional[dict]:
    if fig_paint.get("type") != "SOLID":
        return None

    alias = fig_paint.get("colorVar", {}).get("value", {}).get("alias")
    if alias is None:
        return None

    return context.fig_node_by_ref(alias)


def linked_variable(fig_paint: dict) -> Optional[Tuple[dict, dict]]:
    """The variable a paint's colour links to, along with its collection.

    A linked colour has nowhere to keep an opacity of its own, so a paint with one
    links to none.
    """
    if fig_paint.get("opacity", 1) != 1:
        return None

    fig_variable = paint_variable(fig_paint)
    if fig_variable is None:
        return None

    fig_collection = collection(fig_variable)
    if fig_collection is None:
        return None

    return fig_variable, fig_collection


def linked_color(color: Color, fig_paint: dict, mode_scope: Iterable[dict]) -> Color:
    """Links a colour converted from a paint to a swatch of the variable it is bound to.

    The swatch is the one for the mode the paint's layer resolves the variable in, from
    the layer's mode scope (see active_mode). The paint stores a colour as well, but
    only as a cache of the last one resolved, which can be out of date, so the linked
    colour is the swatch's own. A paint that links to no variable (see linked_variable)
    keeps the colour it was converted to.
    """
    linked = linked_variable(fig_paint)
    if linked is None:
        return color

    fig_variable, fig_collection = linked
    mode_id = active_mode(mode_scope, fig_collection)
    swatch = context.variable_swatches(fig_variable).get(mode_id) if mode_id else None
    if swatch is None:
        return color

    return dataclasses.replace(swatch.value)
