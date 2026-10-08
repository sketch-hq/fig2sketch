from . import style as converter_style
from .context import context
from .errors import *
from converter import utils
from sketchformat.layer_common import AbstractLayer
from sketchformat.layer_common import PrototypeScrolling
from sketchformat.layer_group import AbstractLayerGroup, GroupBehavior, Page
from sketchformat.prototype import *
from sketchformat.style import Fill, LayeringType
from typing import Iterable, Iterator, List, TypedDict, Tuple, Optional

# A link back to wherever the prototype came from, rather than to a layer. Followed
# from inside an overlay, Sketch closes the overlay instead
BACK_DESTINATION = "back"

# Connection types that leave the current screen or overlay rather than go to a layer
BACK_CONNECTIONS = ("BACK", "CLOSE")

# Navigation types that open their destination as an overlay. A swap replaces the
# overlay that is open, which Sketch does by closing the open overlays first
OVERLAY_NAVIGATIONS = ("OVERLAY", "SWAP")

# Mouse enter is not quite hover: it opens the destination and leaves it open. Files
# often pair it with a mouse leave that closes it again, which together act like hovering
INTERACTION_TRIGGER = {
    "ON_CLICK": InteractionTrigger.CLICK,
    "ON_HOVER": InteractionTrigger.HOVER,
    "MOUSE_IN": InteractionTrigger.HOVER,
    "MOUSE_ENTER": InteractionTrigger.HOVER,
    "ON_PRESS": InteractionTrigger.PRESS,
}

OVERLAY_INTERACTION = {
    "NONE": OverlayBackgroundInteraction.NONE,
    "CLOSE_ON_CLICK_OUTSIDE": OverlayBackgroundInteraction.CLOSES_OVERLAY,
}

ANIMATION_TYPE = {
    "INSTANT_TRANSITION": AnimationType.NONE,
    "SLIDE_FROM_LEFT": AnimationType.SLIDE_FROM_LEFT,
    "SLIDE_FROM_RIGHT": AnimationType.SLIDE_FROM_RIGHT,
    "SLIDE_FROM_TOP": AnimationType.SLIDE_FROM_TOP,
    "SLIDE_FROM_BOTTOM": AnimationType.SLIDE_FROM_BOTTOM,
    "PUSH_FROM_LEFT": AnimationType.SLIDE_FROM_LEFT,
    "PUSH_FROM_RIGHT": AnimationType.SLIDE_FROM_RIGHT,
    "PUSH_FROM_TOP": AnimationType.SLIDE_FROM_TOP,
    "PUSH_FROM_BOTTOM": AnimationType.SLIDE_FROM_BOTTOM,
    "MOVE_FROM_LEFT": AnimationType.SLIDE_FROM_LEFT,
    "MOVE_FROM_RIGHT": AnimationType.SLIDE_FROM_RIGHT,
    "MOVE_FROM_TOP": AnimationType.SLIDE_FROM_TOP,
    "MOVE_FROM_BOTTOM": AnimationType.SLIDE_FROM_BOTTOM,
    "SLIDE_OUT_TO_LEFT": AnimationType.SLIDE_FROM_LEFT,
    "SLIDE_OUT_TO_RIGHT": AnimationType.SLIDE_FROM_RIGHT,
    "SLIDE_OUT_TO_TOP": AnimationType.SLIDE_FROM_TOP,
    "SLIDE_OUT_TO_BOTTOM": AnimationType.SLIDE_FROM_BOTTOM,
    "MOVE_OUT_TO_LEFT": AnimationType.SLIDE_FROM_LEFT,
    "MOVE_OUT_TO_RIGHT": AnimationType.SLIDE_FROM_RIGHT,
    "MOVE_OUT_TO_TOP": AnimationType.SLIDE_FROM_TOP,
    "MOVE_OUT_TO_BOTTOM": AnimationType.SLIDE_FROM_BOTTOM,
    "MAGIC_MOVE": AnimationType.NONE,
    "SMART_ANIMATE": AnimationType.NONE,
    "SCROLL_ANIMATE": AnimationType.NONE,
    "DISSOLVE": AnimationType.NONE,
}


class _Flow(TypedDict, total=False):
    flow: FlowConnection


# TODO: Is this called from every node type (groups?)
def convert_flow(fig_node: dict) -> _Flow:
    flow = None
    # Sketch keeps one link per layer. A click goes first, since that is how the
    # prototype moves between screens, where other triggers tend to add extras on top,
    # like a tooltip on hover
    fig_interactions = sorted(
        fig_node.get("prototypeInteractions", []),
        key=lambda interaction: interaction.get("event", {}).get("interactionType") != "ON_CLICK",
    )
    for interaction in fig_interactions:
        if interaction["isDeleted"]:
            continue

        if "event" not in interaction or interaction["event"] == {}:
            continue

        interaction_type = interaction["event"].get("interactionType")
        trigger = INTERACTION_TRIGGER.get(interaction_type)
        if trigger is None:
            utils.log_conversion_warning("PRT001", fig_node, props=[interaction_type])
            continue

        for action in interaction["actions"]:
            if flow is not None:
                utils.log_conversion_warning("PRT002", fig_node)
                continue

            # There can be  empty interactions in the model, we just ignore them
            if action == {}:
                continue

            navigation_type = action.get("navigationType", "NAVIGATE")
            if navigation_type not in ["NAVIGATE", "SCROLL", *OVERLAY_NAVIGATIONS]:
                utils.log_conversion_warning("PRT003", fig_node, props=[navigation_type])
                continue

            try:
                destination, settings = get_destination_settings_if_any(action)
            except Fig2SketchWarning as w:
                utils.log_conversion_warning(w.code, fig_node, props=[action["connectionType"]])
                continue

            if destination is None:
                continue

            if settings is None and opens_overlay_as_screen(action):
                utils.log_conversion_warning("PRT008", fig_node)

            flow = FlowConnection(
                destinationArtboardID=destination,
                animationType=ANIMATION_TYPE[action.get("transitionType", "INSTANT_TRANSITION")],
                maintainScrollPosition=action.get("transitionPreserveScroll", False),
                overlaySettings=settings,
                shouldCloseExistingOverlays=navigation_type == "SWAP",
                interactionTrigger=None if trigger == InteractionTrigger.CLICK else trigger,
            )

    if flow is None:
        return {}

    context.register_flow(fig_node, flow)
    return {"flow": flow}


class _PrototypingInformation(TypedDict, total=False):
    isFlowHome: bool
    overlayBackgroundInteraction: OverlayBackgroundInteraction
    presentationStyle: PresentationStyle
    overlaySettings: FlowOverlaySettings
    prototypeViewport: PrototypeViewport


def is_fixed_to_viewport(fig_node: dict) -> bool:
    behavior = fig_node.get("scrollBehavior", "SCROLLS")
    if behavior in ("SCROLLS", "FIXED_WHEN_CHILD_OF_SCROLLING_FRAME", "FIXED"):
        return behavior != "SCROLLS"
    utils.log_conversion_warning("PRT005", fig_node, props=[behavior])
    return False


SCROLL_DIRECTIONS = {
    "HORIZONTAL": PrototypeScrolling.HORIZONTAL,
    "VERTICAL": PrototypeScrolling.VERTICAL,
    "BOTH": PrototypeScrolling.BOTH,
    "HORIZONTAL_AND_VERTICAL": PrototypeScrolling.BOTH,
}


def prototype_scrolling(fig_node: dict) -> PrototypeScrolling:
    direction = fig_node.get("scrollDirection", "NONE")
    if direction == "NONE":
        return PrototypeScrolling.NONE

    mapped = SCROLL_DIRECTIONS.get(direction)
    if mapped is None:
        utils.log_conversion_warning("PRT005", fig_node, props=[direction])
        return PrototypeScrolling.NONE
    return mapped


def mark_overlay_destinations(fig_nodes: Iterable[dict]) -> None:
    """Records which frames the prototype opens as overlays.

    In the fig format, being an overlay is a property of the link: a link opens its
    destination as an overlay, or swaps the open overlay for it. The destination itself
    is only marked by the overlay settings it carries, and those are left out when they
    hold their defaults, so a frame with default settings looks like any other. Sketch
    makes it a property of the frame instead, so every link is read up front, before
    the frames it points at are converted.

    Interactions that are not converted still count: they show how the frame was
    designed to be shown, even if the link itself does not survive.
    """
    for fig_node in fig_nodes:
        for interaction in fig_node.get("prototypeInteractions", []):
            if interaction.get("isDeleted", False):
                continue

            for action in interaction.get("actions", []):
                destination = action.get("transitionNodeID")
                if (
                    action.get("navigationType") in OVERLAY_NAVIGATIONS
                    and action.get("connectionType") == "INTERNAL_NODE"
                    and destination is not None
                    and not utils.is_invalid_ref(destination)
                ):
                    context.mark_overlay_destination(destination)


def opens_overlay_as_screen(action: dict) -> bool:
    """Whether a link navigates to a frame that other links open as an overlay.

    Sketch decides how to present a frame from the frame alone, so it opens one the
    same way for every link to it. A frame that is an overlay anywhere becomes one,
    and this link will open it as an overlay too.
    """
    destination = action.get("transitionNodeID")
    return (
        action.get("connectionType") == "INTERNAL_NODE"
        and destination is not None
        and context.is_overlay_destination(destination)
    )


def canvas_of(fig_frame: dict) -> Optional[dict]:
    """The page a frame sits on, if it is one of the page's own frames.

    A section only groups frames, so one inside a section, however deeply, still
    belongs to the page. A frame promoted to a section is treated the same, since it
    is a section by the time Sketch sees it. A frame inside any other layer is not a
    screen of its own, and gets no page.
    """
    fig_parent = context.fig_node(fig_frame["parent"]["guid"])
    while fig_parent["type"] == "SECTION" or context.is_promoted_to_section(fig_parent["guid"]):
        fig_parent = context.fig_node(fig_parent["parent"]["guid"])

    return fig_parent if fig_parent["type"] == "CANVAS" else None


def overlay_settings(fig_overlay: dict, action: Optional[dict] = None) -> FlowOverlaySettings:
    """Where an overlay appears, from its own settings and, if given, the link's.

    The position type belongs to the overlay, and a manual position is relative to the
    layer that opens it. Its offset is stored on the link, since each one can open the
    overlay at a different spot, and the fig format ignores it for the other types.
    """
    position = fig_overlay.get("overlayPositionType", "CENTER")
    if position == "MANUAL" and action is not None:
        offset = Point.from_dict(action.get("overlayRelativePosition", {"x": 0, "y": 0}))
        return FlowOverlaySettings.Positioned(position, offset)

    return FlowOverlaySettings.Positioned(position)


def prototyping_information(fig_frame: dict) -> _PrototypingInformation:
    info: _PrototypingInformation = {}

    if context.is_overlay_destination(fig_frame["guid"]):
        info.update(
            {
                "isFlowHome": False,
                "overlayBackgroundInteraction": OVERLAY_INTERACTION[
                    fig_frame.get("overlayBackgroundInteraction", "NONE")
                ],
                "presentationStyle": PresentationStyle.OVERLAY,
                "overlaySettings": overlay_settings(fig_frame),
            }
        )
        return info

    # Some information about the prototype is in the canvas/page
    fig_canvas = canvas_of(fig_frame)

    if fig_canvas is None or "prototypeDevice" not in fig_canvas:
        info.update(
            {
                "isFlowHome": False,
                "overlayBackgroundInteraction": OverlayBackgroundInteraction.NONE,
                "presentationStyle": PresentationStyle.SCREEN,
            }
        )
        return info

    info.update(
        {
            "isFlowHome": fig_frame.get("prototypeStartingPoint", {}).get("name", "") != "",
            "prototypeViewport": PrototypeViewport(
                name=fig_canvas["prototypeDevice"]["presetIdentifier"],
                size=Point.from_dict(fig_canvas["prototypeDevice"]["size"]),
            ),
            "overlayBackgroundInteraction": OverlayBackgroundInteraction.NONE,
            "presentationStyle": PresentationStyle.SCREEN,
            "overlaySettings": FlowOverlaySettings.RegularArtboard(),
        }
    )
    return info


def overlay_backdrop(fig_frame: dict) -> Optional[Fill]:
    """The backdrop a frame draws around itself while it is open as an overlay.

    Sketch keeps it as a fill in the frame's own style, marked as backdrop so it is
    drawn behind the overlay rather than as the frame's background.
    """
    if not context.is_overlay_destination(fig_frame["guid"]):
        return None

    appearance = fig_frame.get("overlayBackgroundAppearance", {})
    if appearance.get("backgroundType") != "SOLID_COLOR":
        return None

    fill = Fill.Color(converter_style.convert_color(appearance["backgroundColor"]))
    fill.layeringType = LayeringType.BACKDROP
    return fill


def add_overlay_backdrop(fig_frame: dict, sketch_frame: AbstractLayerGroup) -> None:
    backdrop = overlay_backdrop(fig_frame)
    if backdrop is not None:
        sketch_frame.style.fills.append(backdrop)


def get_destination_settings_if_any(
    action: dict,
) -> Tuple[Optional[str], Optional[FlowOverlaySettings]]:
    settings = None
    destination: Optional[str]

    connection_type = action.get("connectionType")
    transition_node_id = action.get("transitionNodeID", None)

    if connection_type in BACK_CONNECTIONS:
        destination = BACK_DESTINATION
    elif connection_type == "INTERNAL_NODE" and transition_node_id is None:
        destination = None
    elif connection_type == "INTERNAL_NODE" and transition_node_id is not None:
        if utils.is_invalid_ref(transition_node_id):
            destination = None
        else:
            destination = utils.gen_object_id(transition_node_id)

            if action.get("navigationType") in OVERLAY_NAVIGATIONS:
                transition_node = context.fig_node(transition_node_id)
                settings = overlay_settings(transition_node, action)
    elif connection_type == "NONE":
        destination = None
    else:
        raise Fig2SketchWarning("PRT004")

    return destination, settings


def _descendants(group: AbstractLayerGroup) -> Iterator[AbstractLayer]:
    for layer in group.layers:
        yield layer
        if isinstance(layer, AbstractLayerGroup):
            yield from _descendants(layer)


def _is_section(layer: AbstractLayer) -> bool:
    return isinstance(layer, AbstractLayerGroup) and layer.groupBehavior == GroupBehavior.SECTION


def drop_invalid_flows(pages: List[Page]) -> None:
    """Removes prototype links that point somewhere Sketch cannot navigate to.

    A link is converted from the destination's id alone, without knowing what that
    id becomes, so two kinds of broken link can reach the output: one pointing at a
    section, which Sketch does not allow as a destination, and one pointing at a
    layer that never made it into the document, since conversion skips a subtree
    that fails and drops unsupported layer types.

    Neither is known before every page is converted, which is why this runs at the
    end rather than as a check while converting. Only those two cases are dropped: a
    fig link can point at a group or another non-frame layer, and those are left
    alone.
    """
    layers = [layer for page in pages for layer in _descendants(page)]
    # Pages are left out on purpose. A page is not a destination, so a link naming
    # one is as broken as a link naming nothing.
    section_ids = {layer.do_objectID for layer in layers if _is_section(layer)}
    layer_ids = {layer.do_objectID for layer in layers}

    # Flows are matched by object identity, since two links to the same destination
    # compare equal. The context holds a reference to each one, so the ids stay valid.
    source_nodes = {id(flow): fig_node for fig_node, flow in context.flows()}

    for layer in layers:
        flow = layer.flow
        if flow is None or flow.destinationArtboardID == BACK_DESTINATION:
            continue

        if flow.destinationArtboardID in section_ids:
            warning_code = "PRT006"
        elif flow.destinationArtboardID not in layer_ids:
            warning_code = "PRT007"
        else:
            continue

        layer.flow = None

        fig_node = source_nodes.get(id(flow))
        if fig_node is not None:
            utils.log_conversion_warning(warning_code, fig_node)
