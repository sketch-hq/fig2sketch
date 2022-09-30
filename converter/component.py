from . import style
import utils


def convert(figma_style):
    match figma_style:
        case {'styleType': 'FILL'}:

            return convert_fill(figma_style, figma_style['fillPaints'][0])
        case _:
            raise Exception(f"Unsupported shared style: '{figma_style['styleType']}'")


def convert_fill(figma_style, figma_fill):
    match figma_fill:
        case {'type': 'SOLID'}:
            return {
                '_class': 'swatch',
                'do_objectID': utils.gen_object_id(figma_style.id),
                'name': figma_style.name,
                'value': {
                    '_class': 'color',
                    **style.convert_color(figma_style['fillPaints'][0])
                }
            }
        case _:
            return {}
