from converter import utils
from . import style
from sketchformat.document import Swatch
from typing import Optional


def convert(fig_style: dict) -> Optional[Swatch]:
    match fig_style:
        # Fill with a single fill -> color variable
        case {"styleType": "FILL", "fillPaints": [{"type": "SOLID"} as paint]}:
            # Linking a paint to a variable looks nodes up through the context, which
            # imports this module
            from . import variable

            # A style whose colour is a variable's links to the variable's swatches, as
            # any paint bound to it does, so it needs none of its own
            if variable.linked_variable(paint) is not None:
                return None

            uuid = utils.gen_object_id(fig_style["guid"])
            color = style.convert_color(paint["color"], paint["opacity"])
            color.swatchID = uuid
            return Swatch(do_objectID=uuid, name=fig_style["name"], value=color)
        case _:
            return None
