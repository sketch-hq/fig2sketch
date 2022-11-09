from . import style
from sketchformat.document import Swatch, Color
import utils
from typing import Optional


def convert(figma_style: dict) -> Optional[Swatch]:
    match figma_style:
        # Fill with a single fill -> color variable
        case {'styleType': 'FILL', 'fillPaints': [{'type': 'SOLID'} as paint]}:
            uuid = utils.gen_object_id(figma_style['guid'])
            color = style.convert_color(paint['color'], paint['opacity'])
            color.swatchID = uuid
            return Swatch(
                do_objectID=uuid,
                name=figma_style['name'],
                value=color
            )
        case _:
            return None
