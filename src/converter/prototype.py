from .context import context
from .errors import *
from converter import utils
from sketchformat.layer_common import AbstractLayer
from sketchformat.layer_group import AbstractLayerGroup, GroupBehavior, Page
from sketchformat.prototype import *
from typing import Iterator, List, TypedDict, Tuple, Optional

# A link back to wherever the prototype came from, rather than to a layer
BACK_DESTINATION = "back"

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
    for interaction in fig_node.get("prototypeInteractions", []):
        if interaction["isDeleted"]:
            continue

        if "event" not in interaction or interaction["event"] == {}:
            continue

        interaction_type = interaction["event"].get("interactionType")
        if interaction_type != "ON_CLICK":
            utils.log_conversion_warning("PRT001", fig_node, props=[interaction_type])
            continue

        for action in interaction["actions"]:
            if flow is not None:
                utils.log_conversion_warning("PRT002", fig_node)
                continue

            # There can be  empty interactions in the model, we just ignore them
            if action == {}:
                continue

            if action.get("navigationType", "NAVIGATE") not in ["NAVIGATE", "SCROLL", "OVERLAY"]:
                utils.log_conversion_warning("PRT003", fig_node, props=[action["navigationType"]])
                continue

            try:
                destination, overlay_settings = get_destination_settings_if_any(action)
            except Fig2SketchWarning as w:
                utils.log_conversion_warning(w.code, fig_node, props=[action["connectionType"]])
                continue

            if destination is not None:
                flow = FlowConnection(
                    destinationArtboardID=destination,
                    animationType=ANIMATION_TYPE[
                        action.get("transitionType", "INSTANT_TRANSITION")
                    ],
                    maintainScrollPosition=action.get("transitionPreserveScroll", False),
                    overlaySettings=overlay_settings,
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


def prototyping_information(fig_frame: dict) -> _PrototypingInformation:
    # Some information about the prototype is in the canvas/page
    fig_canvas = context.fig_node(fig_frame["parent"]["guid"])

    if "prototypeDevice" not in fig_canvas:
        return {
            "isFlowHome": False,
            "overlayBackgroundInteraction": OverlayBackgroundInteraction.NONE,
            "presentationStyle": PresentationStyle.SCREEN,
        }

    # TODO: Overflow scrolling means making the artboard bigger (fit the child bounds)
    if fig_frame.get("scrollDirection", "NONE") != "NONE":
        utils.log_conversion_warning("PRT005", fig_frame)

    if "overlayBackgroundInteraction" in fig_frame:
        return {
            "isFlowHome": False,
            "overlayBackgroundInteraction": OVERLAY_INTERACTION[
                fig_frame["overlayBackgroundInteraction"]
            ],
            "presentationStyle": PresentationStyle.OVERLAY,
            "overlaySettings": FlowOverlaySettings.Positioned(
                fig_frame.get("overlayPositionType", "CENTER")
            ),
        }
    else:
        return {
            "isFlowHome": fig_frame.get("prototypeStartingPoint", {}).get("name", "") != "",
            "prototypeViewport": PrototypeViewport(
                name=fig_canvas["prototypeDevice"]["presetIdentifier"],
                size=Point.from_dict(fig_canvas["prototypeDevice"]["size"]),
            ),
            "overlayBackgroundInteraction": OverlayBackgroundInteraction.NONE,
            "presentationStyle": PresentationStyle.SCREEN,
            "overlaySettings": FlowOverlaySettings.RegularArtboard(),
        }


def get_destination_settings_if_any(
    action: dict,
) -> Tuple[Optional[str], Optional[FlowOverlaySettings]]:
    overlay_settings = None
    destination: Optional[str]

    connection_type = action.get("connectionType")
    transition_node_id = action.get("transitionNodeID", None)

    if connection_type == "BACK":
        destination = BACK_DESTINATION
    elif connection_type == "INTERNAL_NODE" and transition_node_id is None:
        destination = None
    elif connection_type == "INTERNAL_NODE" and transition_node_id is not None:
        if utils.is_invalid_ref(transition_node_id):
            destination = None
        else:
            destination = utils.gen_object_id(transition_node_id)
            transition_node = context.fig_node(transition_node_id)

            if "overlayBackgroundInteraction" in transition_node:
                offset = action.get("overlayRelativePosition", {"x": 0, "y": 0})

                overlay_settings = FlowOverlaySettings.Positioned(
                    transition_node.get("overlayPositionType", "CENTER"),
                    Point.from_dict(offset),
                )
    elif connection_type == "NONE":
        destination = None
    else:
        raise Fig2SketchWarning("PRT004")

    return destination, overlay_settings


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
