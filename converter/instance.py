from . import base
import utils

def convert(figma_instance):
    sketch_overrides = convert_overrides(figma_instance)

    if sketch_overrides is None:
        return dettach_symbol(figma_instance)
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
                # TODO: Handle changes only in styleOverrides (dettach?)
                # TODO: Make sure the override works with multistyle text
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

    # Apply overrides. Can we use derivedSymbolData?

    # Convert to Sketch

    # Adjust positioning (frame vs group)
    pass
