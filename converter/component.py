from . import style
import utils


def convert(figma_style):
    match figma_style:
        # Fill with a single fill
        case {'styleType': 'FILL', 'fillPaints': [{'type': 'SOLID'} as paint]}:
            color = style.convert_color(paint['color'], paint['opacity'])
            color.swatchID = utils.gen_object_id(figma_style['guid'])
            return {
                '_class': 'swatch',
                'do_objectID': color.swatchID,
                'name': figma_style['name'],
                'value': color
            }
        case _:
            return None
