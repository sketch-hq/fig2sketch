import copy
import dataclasses
import math
from .positioning import Vector, Matrix
from converter import utils
from sketchformat.style import *
from .utils import safe_div
from typing import List, TypedDict, Optional
from .errors import Fig2SketchNodeChanged

BORDER_POSITION = {
    "CENTER": BorderPosition.CENTER,
    "INSIDE": BorderPosition.INSIDE,
    "OUTSIDE": BorderPosition.OUTSIDE,
}

LINE_CAP_STYLE = {
    "NONE": LineCapStyle.BUTT,
    "ROUND": LineCapStyle.ROUND,
    "SQUARE": LineCapStyle.SQUARE,
    "LINE_ARROW": LineCapStyle.SQUARE,
    "ARROW_LINES": LineCapStyle.SQUARE,
    "TRIANGLE_ARROW": LineCapStyle.SQUARE,
    "TRIANGLE_FILLED": LineCapStyle.SQUARE,
}

LINE_JOIN_STYLE = {
    "MITER": LineJoinStyle.MITER,
    "ROUND": LineJoinStyle.ROUND,
    "BEVEL": LineJoinStyle.BEVEL,
}

PATTERN_FILL_TYPE = {
    "STRETCH": PatternFillType.STRETCH,
    "FIT": PatternFillType.FIT,
    "FILL": PatternFillType.FILL,
    "TILE": PatternFillType.TILE,
}

BLEND_MODE = {
    "PASS_THROUGH": BlendMode.NORMAL,
    "NORMAL": BlendMode.NORMAL,
    "DARKEN": BlendMode.DARKEN,
    "MULTIPLY": BlendMode.MULTIPLY,
    "LINEAR_BURN": BlendMode.PLUS_DARKER,
    "COLOR_BURN": BlendMode.COLOR_BURN,
    "LIGHTEN": BlendMode.LIGHTEN,
    "SCREEN": BlendMode.SCREEN,
    "LINEAR_DODGE": BlendMode.PLUS_LIGHTER,
    "COLOR_DODGE": BlendMode.COLOR_DODGE,
    "OVERLAY": BlendMode.OVERLAY,
    "SOFT_LIGHT": BlendMode.SOFT_LIGHT,
    "HARD_LIGHT": BlendMode.HARD_LIGHT,
    "DIFFERENCE": BlendMode.DIFFERENCE,
    "EXCLUSION": BlendMode.EXCLUSION,
    "HUE": BlendMode.HUE,
    "SATURATION": BlendMode.SATURATION,
    "COLOR": BlendMode.COLOR,
    "LUMINOSITY": BlendMode.LUMINOSITY,
}


def convert(fig_node: dict) -> Style:
    sketch_style = Style(
        do_objectID=utils.gen_object_id(fig_node["guid"], b"style"),
        borderOptions=BorderOptions(
            lineCapStyle=(
                LINE_CAP_STYLE[fig_node.get("strokeCap", "NONE")]
                if "strokeCap" in fig_node
                else BorderOptions.__dict__["lineCapStyle"]
            ),
            lineJoinStyle=(
                LINE_JOIN_STYLE[fig_node["strokeJoin"]]
                if "strokeJoin" in fig_node
                else BorderOptions.__dict__["lineCapStyle"]
            ),
            dashPattern=fig_node.get("dashPattern", []),
        ),
        borders=[convert_border(fig_node, b) for b in fig_node.get("strokePaints", [])],
        fills=[convert_fill(fig_node, f) for f in fig_node.get("fillPaints", [])],
        **convert_effects(fig_node),
        contextSettings=context_settings(fig_node),
        corners=convert_corners(fig_node),
    )
    return sketch_style


def convert_corners(fig_node: dict) -> Optional[StyleCorners]:
    # Return None if no corner radius is specified
    if not fig_node.get("cornerRadius", False) and not fig_node.get(
        "rectangleTopLeftCornerRadius", False
    ):
        return None

    base_radius = float(fig_node.get("cornerRadius", 0))

    # Get individual corner radii, defaulting to base radius if not specified
    top_left = fig_node.get("rectangleTopLeftCornerRadius", base_radius)
    top_right = fig_node.get("rectangleTopRightCornerRadius", base_radius)
    bottom_left = fig_node.get("rectangleBottomLeftCornerRadius", base_radius)
    bottom_right = fig_node.get("rectangleBottomRightCornerRadius", base_radius)

    corner_style = CornerStyle.SMOOTH if fig_node.get("cornerSmoothing") else CornerStyle.ROUNDED

    return StyleCorners(
        radii=[top_left, top_right, bottom_right, bottom_left],
        style=corner_style,
    )


def convert_border(fig_node: dict, fig_border: dict) -> Border:
    return Border.from_fill(
        convert_fill(fig_node, fig_border),
        position=BORDER_POSITION[fig_node.get("strokeAlign", "CENTER")],
        thickness=fig_node["strokeWeight"],
    )


def convert_fill(fig_node: dict, fig_fill: dict) -> Fill:
    match fig_fill:
        case {"type": "EMOJI"}:
            raise Exception("Unsupported fill: EMOJI")
        case {"type": "SOLID"}:
            # Solid color backgrounds do not support specifying the opacity
            # Instead, it must be set in the color itself
            return Fill.Color(
                convert_color(fig_fill["color"], fig_fill["opacity"]),
                isEnabled=fig_fill["visible"],
                blendMode=BLEND_MODE[fig_fill.get("blendMode", "NORMAL")],
            )
        case {"type": "IMAGE"}:
            if is_cropped_image(fig_fill) and not fig_node.get("f2s_cropped_image"):
                # Extract images to a separate layer and retrigger conversion
                convert_crop_image_to_mask(fig_node)

            if "paintFilter" in fig_fill:
                utils.log_conversion_warning("STY005", fig_node)

            return Fill.Image(
                f'images/{fig_fill["image"]["filename"]}',
                patternFillType=PATTERN_FILL_TYPE[fig_fill["imageScaleMode"]],
                patternTileScale=fig_fill.get("scale", 1),
                isEnabled=fig_fill["visible"],
                opacity=fig_fill.get("opacity", 1),
                blendMode=BLEND_MODE[fig_fill.get("blendMode", "NORMAL")],
            )
        case _:
            return Fill.Gradient(
                convert_gradient(fig_node, fig_fill),
                isEnabled=fig_fill["visible"],
                opacity=fig_fill.get("opacity", 1),
                blendMode=BLEND_MODE[fig_fill.get("blendMode", "NORMAL")],
            )


def is_cropped_image(fig_fill: dict) -> bool:
    return (
        fig_fill.get("type") == "IMAGE"
        and "transform" in fig_fill
        and fig_fill["transform"] != Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    )


def convert_crop_image_to_mask(fig_node: dict) -> None:
    content = copy.deepcopy(fig_node)
    cropped_images = []
    other_fills = []
    for idx, fill in enumerate(content.get("fillPaints", [])):
        if is_cropped_image(fill):
            image_layer = cropped_image_layer(fig_node, fill)
            image_layer["guid"] = fig_node["guid"] + (1, idx)
            cropped_images.append(image_layer)
        else:
            other_fills.append(fill)

    content["fillPaints"] = other_fills
    content["transform"] = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    old = copy.copy(fig_node)
    fig_node.clear()
    fig_node.update(
        {
            "type": "FRAME",
            "name": f'{old["name"]} (crop group)',
            "guid": old["guid"] + (0, 0),
            "size": old["size"],
            "transform": old["transform"],
            "locked": old.get("locked", False),
            "visible": old.get("visible", True),
            "horizontalConstraint": old.get("horizontalConstraint", "MIN"),
            "verticalConstraint": old.get("verticalConstraint", "MIN"),
            "blendMode": old.get("blendMode", "NORMAL"),
            "opacity": old.get("opacity", 1),
            "resizeToFit": True,
            "children": [
                {
                    **content,
                    "mask": True,
                    "maskType": "OUTLINE",
                    "f2s_cropped_image": True,
                },
                *cropped_images,
            ],
        }
    )
    raise Fig2SketchNodeChanged


def cropped_image_layer(fig_node: dict, fill: dict) -> dict:
    invmat = fill["transform"].inv()

    iw = fill.get("originalImageWidth", fig_node["size"]["x"])
    ih = fill.get("originalImageHeight", fig_node["size"]["y"])
    image_scale = Matrix.scale(safe_div(1.0, iw), safe_div(1.0, ih))
    layer_scale = Matrix.scale(fig_node["size"]["x"], fig_node["size"]["y"])

    transform = layer_scale * invmat * image_scale

    height = transform.dot2([0, ih]).length()
    width = transform.dot2([iw, 0]).length()

    normalize_scale = Matrix.scale(safe_div(iw, width), safe_div(ih, height))

    image_layer = {
        "type": "RECTANGLE",
        "name": f'{fig_node["name"]} (cropped image)',
        "size": {"x": width, "y": height},
        "transform": transform * normalize_scale,
        "locked": fig_node.get("locked", False),
        "visible": fig_node.get("visible", True),
        "horizontalConstraint": fig_node.get("horizontalConstraint", "MIN"),
        "verticalConstraint": fig_node.get("verticalConstraint", "MIN"),
        "blendMode": fig_node.get("blendMode", "NORMAL"),
        "opacity": fig_node.get("opacity", 1),
        "fillPaints": [fill],
    }
    del image_layer["fillPaints"][0]["transform"]

    return image_layer


def convert_color(color: dict, opacity: Optional[float] = None) -> Color:
    return Color(
        red=color["r"],
        green=color["g"],
        blue=color["b"],
        alpha=color["a"] if opacity is None else opacity,
    )


def convert_gradient(fig_node: dict, fig_fill: dict) -> Gradient:
    # Convert positions depending on the gradient type
    mat = fig_fill["transform"]

    invmat = mat.inv()

    rotation_offset = 0.0
    if fig_fill["type"] == "GRADIENT_LINEAR":
        # Linear gradients always go from (0, .5) to (1, .5)
        # We just apply the transform to get the coordinates (in a 1x1 square)
        return Gradient.Linear(
            from_=Point.from_array(invmat.dot([0, 0.5, 1])),
            to=Point.from_array(invmat.dot([1, 0.5, 1])),
            stops=convert_stops(fig_fill["stops"]),
        )
    elif fig_fill["type"] in ["GRADIENT_RADIAL", "GRADIENT_DIAMOND"]:
        if fig_fill["type"] == "GRADIENT_DIAMOND":
            utils.log_conversion_warning("STY002", fig_node)

        # Angular gradients have the center at (.5, .5), the vertex at (1, .5)
        # and the co-vertex at (.5, 1). We transform them to the coordinates in a 1x1 square
        point_from = invmat.dot([0.5, 0.5, 1])  # Center
        point_to = invmat.dot([1, 0.5, 1])
        point_ellipse = invmat.dot([0.5, 1, 1])

        # Sketch defines the ratio between axis in the item reference point (not the 1x1 square)
        # So we scale the 1x1 square coordinates to fit the ratio of the item frame before
        # calculating the ellipse's ratio
        stroke = fig_node.get("strokeWeight", 0)
        try:
            x_scale = (fig_node["size"]["x"] + 2 * stroke) / (fig_node["size"]["y"] + 2 * stroke)
        except:
            x_scale = 1

        ellipse_ratio = safe_div(
            scaled_distance(point_from, point_ellipse, x_scale),
            scaled_distance(point_from, point_to, x_scale),
        )

        return Gradient.Radial(
            from_=Point.from_array(point_from),
            to=Point.from_array(point_to),
            elipseLength=ellipse_ratio,
            stops=convert_stops(fig_fill["stops"]),
        )
    else:
        # Angular gradients don't allow positioning, but we can at least rotate them
        rotation_offset = (
            math.atan2(-fig_fill["transform"][1][0], fig_fill["transform"][0][0]) / 2 / math.pi
        )

        return Gradient.Angular(stops=convert_stops(fig_fill["stops"], rotation_offset))


def convert_stops(fig_stops: List[dict], rotation_offset: float = 0.0) -> List[GradientStop]:
    stops = [
        GradientStop(
            color=convert_color(stop["color"]),
            position=rotated_stop(stop["position"], rotation_offset),
        )
        for stop in fig_stops
    ]

    if rotation_offset:
        # When we have a rotated angular gradient, stops at 0 and 1 both convert
        # to the exact same position and that confuses Sketch. Force a small difference
        stops[-1].position -= 0.00001
    else:
        # Always add a stop at 0 and 1 if needed
        if stops[0].position != 0:
            stops.insert(0, dataclasses.replace(stops[0], position=0))

        if stops[-1].position != 1:
            stops.append(dataclasses.replace(stops[-1], position=1))

    return stops


def scaled_distance(a: Vector, b: Vector, x_scale: float) -> float:
    v = a - b
    return ((v[0] * x_scale) ** 2 + v[1] ** 2) ** 0.5


def rotated_stop(position: float, offset: float) -> float:
    pos = position + offset
    if pos > 1:
        pos -= 1
    elif pos < 0:
        pos += 1
    if pos < 0:
        pos += 1
    return pos


class _Effects(TypedDict):
    blurs: List[Blur]
    shadows: List[Shadow]


def convert_effects(fig_node: dict) -> _Effects:
    sketch: _Effects = {"blurs": [], "shadows": []}

    for e in fig_node.get("effects", []):
        if e["type"] == "INNER_SHADOW":
            sketch["shadows"].append(
                Shadow(
                    blurRadius=e["radius"],
                    offsetX=e["offset"]["x"],
                    offsetY=e["offset"]["y"],
                    spread=e.get("spread", 0),
                    color=convert_color(e["color"]),
                    isInnerShadow=True,
                    isEnabled=e.get("visible"),
                )
            )

        elif e["type"] == "DROP_SHADOW":
            sketch["shadows"].append(
                Shadow(
                    blurRadius=e["radius"],
                    offsetX=e["offset"]["x"],
                    offsetY=e["offset"]["y"],
                    spread=e.get("spread", 0),
                    color=convert_color(e["color"]),
                    isEnabled=e.get("visible"),
                )
            )

        elif e["type"] == "FOREGROUND_BLUR":
            if (
                len(sketch["blurs"])
                and hasattr(sketch["blurs"][0], "isEnabled")
                and sketch["blurs"][0].isEnabled
            ):
                utils.log_conversion_warning("STY001", fig_node)
                continue

            sketch["blurs"].append(
                Blur(
                    radius=e["radius"] / 2,  # Looks best dividing by 2, no idea why,
                    type=BlurType.GAUSSIAN,
                )
            )

        elif e["type"] == "BACKGROUND_BLUR":
            if (
                len(sketch["blurs"])
                and hasattr(sketch["blurs"][0], "isEnabled")
                and sketch["blurs"][0].isEnabled
            ):
                utils.log_conversion_warning("STY001", fig_node)
                continue

            sketch["blurs"].append(
                Blur(
                    radius=e["radius"] / 2,  # Looks best dividing by 2, no idea why,
                    type=BlurType.BACKGROUND,
                )
            )

        else:
            raise Exception(f'Unsupported effect: {e["type"]}')

    return sketch


def context_settings(fig_node: dict) -> ContextSettings:
    blend_mode = BLEND_MODE[fig_node.get("blendMode", "NORMAL")]
    opacity = fig_node.get("opacity", 1)

    # Figma's default blend mode is pass-through, but its not expressed as a
    # value in the fig model. When "NORMAL" is set explicity we need to tweak Sketch'
    # opacity to avoid pass-through.
    if fig_node.get("blendMode") == "NORMAL" and opacity == 1:
        # Sketch interprets normal at 100% opacity as pass-through
        opacity = 0.99

    return ContextSettings(blendMode=blend_mode, opacity=opacity)
