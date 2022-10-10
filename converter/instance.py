from . import base, tree
import utils
from .context import context
import copy

def convert(figma_instance):
    sketch_overrides = convert_overrides(figma_instance)

    if sketch_overrides is None:
        # Modify Figma tree in place, with the dettached symbol subtree
        dettach_symbol(figma_instance)
        obj = {
            **base.base_shape(figma_instance),
            "_class": "group",
            'name': figma_instance.name
        }
        del obj['style']
        return obj
    else:
        obj = {
            **base.base_shape(figma_instance),
            "_class": "symbolInstance",
            'name': figma_instance.name,
            'symbolID': utils.gen_object_id((figma_instance['symbolData']['symbolID']['sessionID'], figma_instance['symbolData']['symbolID']['localID'])),
            'overrideValues': sketch_overrides
        }
        del obj['style']
        return obj


def master_instance(figma_symbol):
    obj = {
        **base.base_shape(figma_symbol),
        "_class": "symbolInstance",
        'do_objectID': utils.gen_object_id(figma_symbol.id, b'master_instance'),
        'name': figma_symbol.name,
        'symbolID': utils.gen_object_id(figma_symbol.id)
    }
    del obj['style']
    return obj

def convert_overrides(figma_instance):
    sketch_overrides = []
    for override in figma_instance['symbolData']['symbolOverrides']:
        # This happen when overriding something in a nested symbol instance (override something
        # in the nested symbol. First GUID is nested symbol instance, Second GUID is layer
        # inside the nested symbol
        # TODO
        assert len(override['guidPath']['guids']) == 1
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

    figma_master = context.figma_node((figma_instance['symbolData']['symbolID']['sessionID'], figma_instance['symbolData']['symbolID']['localID']))
    for prop in figma_instance.get('componentPropAssignments', []):
        # TODO: propdef.type needed?
        # prop_def = [d for d in figma_master.componentPropDefs if d['id'] == prop['defID']]

        ref_prop, ref_node = find_ref(figma_master, prop['defID'])
        uuid = utils.gen_object_id(ref_node['id'])
        if ref_prop['componentPropNodeField'] == 'OVERRIDDEN_SYMBOL_ID':
            symbol_id = utils.gen_object_id((prop['value']['guidValue']['sessionID'], prop['value']['guidValue']['localID']))
            sketch_overrides.append({
                "_class": "overrideValue",
                "overrideName": f"{uuid}_symbolID",
                "value": symbol_id
            })
        elif ref_prop['componentPropNodeField'] == 'TEXT_DATA':
            sketch_overrides.append({
                "_class": "overrideValue",
                "overrideName": f"{uuid}_stringValue",
                "value": prop['value']['textValue']['characters']
            })
        else: # VISIBLE / INHERIT_FILL_STYLE_ID
            # TODO: Implement dettaching of properties
            print(f"Unsupported property: {ref_prop['componentPropNodeField']}. Will dettach")
            return None

    return sketch_overrides


def find_ref(node, ref_id):
    refs = [ref for ref in node.get('componentPropRefs', []) if ref['defID'] == ref_id]
    if refs:
        return refs[0], node

    for ch in node['children']:
        r = find_ref(ch, ref_id)
        if r:
            return r

    return None



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
