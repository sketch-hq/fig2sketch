from . import style
import utils

def convert(figma_style):
    match figma_style:
        # Fill with a single fill
        case {'styleType': 'FILL', 'fillPaints': [{'type': 'SOLID'} as paint]}:
            return {
                '_class': 'swatch',
                'do_objectID': utils.gen_object_id(figma_style.id),
                'name': figma_style.name,
                'value': {
                    '_class': 'color',
                    **style.convert_color(paint)
                }
            }
        case _:
            raise Exception(f"Unsupported shared style: '{figma_style['styleType']}'")
