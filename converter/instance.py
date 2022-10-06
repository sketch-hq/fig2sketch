from . import base, tree
import utils
from .context import context
import copy

def convert(figma_instance):
    sketch_overrides = convert_overrides(figma_instance)

    if sketch_overrides is None:
        # Modify Figma tree in place, with the dettached symbol subtree
        dettach_symbol(figma_instance)
        return {
            **base.base_shape(figma_instance),
            "_class": "group",
            'name': figma_instance.name
        }
    else:
        return {
            **base.base_shape(figma_instance),
            "_class": "symbolInstance",
            'name': figma_instance.name,
            'symbolID': utils.gen_object_id((figma_instance['symbolData']['symbolID']['sessionID'], figma_instance['symbolData']['symbolID']['localID'])),
            'overrideValues': sketch_overrides
        }


def master_instance(figma_symbol):
    return {
        **base.base_shape(figma_symbol),
        "_class": "symbolInstance",
        'do_objectID': utils.gen_object_id(figma_symbol.id, b'master_instance'),
        'name': figma_symbol.name,
        'symbolID': utils.gen_object_id(figma_symbol.id)
    }

def convert_overrides(figma_instance):
    sketch_overrides = []
    for override in figma_instance['symbolData']['symbolOverrides']:
        assert len(override['guidPath']['guids']) == 1 # What does it mean to have multiple guids here?
        guid = override['guidPath']['guids'][0]
        uuid = utils.gen_object_id((guid['sessionID'], guid['localID']))

        for property, value in override.items():
            if property == 'guidPath':
                continue
            if property == 'textData':
                # Text override.
                if 'styleOverrideTable' in value:
                    # Sketch does not support multiple styles in text overrides -> dettach
                    print(f'Unsupported override: text with mixed styles. Will dettach')
                    return None

                sketch_overrides.append({
                    "_class": "overrideValue",
                    "overrideName": f"{uuid}_stringValue",
                    "value": value['characters']
                })
            elif property == 'size':
                pass # I think we can ignore this (the frame will pick up the change)
            else:
                # Unknown override
                print(f'Unsupported override: {property}. Will dettach')
                return None

    return sketch_overrides

def dettach_symbol(figma_instance):
    # Find symbol master
    figma_master = context.figma_node((figma_instance['symbolData']['symbolID']['sessionID'], figma_instance['symbolData']['symbolID']['localID']))
    dettached_children = copy.deepcopy(figma_master['children'], {})

    # Apply overrides. Can we use derivedSymbolData?
    overrides = {
        (o["guidPath"]["guids"][0]["sessionID"], o["guidPath"]["guids"][0]["localID"]): o
        for o in figma_instance['symbolData']['symbolOverrides']
    }
    for c in dettached_children:
        apply_overrides(c, figma_instance.id, overrides)

    figma_instance['children'] = dettached_children

def apply_overrides(figma, instance_id, overrides):
    ov = overrides.get(figma.id)
    if ov:
        figma.update(ov)

    # Generate a unique ID by concatenating instance_id + node_id
    figma['id'] = (*instance_id, *figma['id'])

    for c in figma.children:
        apply_overrides(c, overrides)
