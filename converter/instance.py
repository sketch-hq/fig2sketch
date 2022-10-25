from . import base, tree, style, group
import utils
from .context import context
import copy
from sketchformat.style import Style


def convert(figma_instance):
    sketch_overrides = convert_overrides(figma_instance)

    if sketch_overrides is None:
        # Modify Figma tree in place, with the detached symbol subtree
        detach_symbol(figma_instance)
        return group.convert(figma_instance)
    else:
        obj = {
            **base.base_shape(figma_instance),
            '_class': 'symbolInstance',
            'symbolID': utils.gen_object_id(figma_instance['symbolData']['symbolID']),
            'overrideValues': sketch_overrides,
            'preservesSpaceWhenHidden': False,
            'scale': 1
        }
        obj['style'] = Style(do_objectID=utils.gen_object_id(figma_instance['guid'], b'style'))
        return obj


def master_instance(figma_symbol):
    obj = {
        **base.base_shape(figma_symbol),
        '_class': 'symbolInstance',
        'do_objectID': utils.gen_object_id(figma_symbol['guid'], b'master_instance'),
        'symbolID': utils.gen_object_id(figma_symbol['guid']),
        'preservesSpaceWhenHidden': False,
        'overrideValues': [],
        'scale': 1
    }
    obj['style'] = Style(
        do_objectID=utils.gen_object_id(figma_symbol['guid'], b'master_instance_style'))
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
        uuid = utils.gen_object_id(guid)

        for property, value in override.items():
            if property == 'guidPath':
                continue
            if property == 'textData':
                # Text override.
                if 'styleOverrideTable' in value:
                    # Sketch does not support multiple styles in text overrides -> detach
                    print(f"Unsupported override: text with mixed styles. Will detach")
                    return None

                sketch_overrides.append({
                    '_class': 'overrideValue',
                    'overrideName': f'{uuid}_stringValue',
                    'value': value['characters']
                })
            elif property == 'size':
                pass  # I think we can ignore this (the frame will pick up the change)
            else:
                # Unknown override
                print(f"Unsupported override: {property}. Will detach")
                return None

    figma_master = context.figma_node(figma_instance['symbolData']['symbolID'])
    for prop in figma_instance.get('componentPropAssignments', []):
        # TODO: propdef.type needed?
        # prop_def = [d for d in figma_master['componentPropDefs'] if d['id'] == prop['defID']]

        ref_prop, ref_node = find_ref(figma_master, prop['defID'])
        uuid = utils.gen_object_id(ref_node['guid'])
        if ref_prop['componentPropNodeField'] == 'OVERRIDDEN_SYMBOL_ID':
            symbol_id = utils.gen_object_id(prop['value']['guidValue'])
            sketch_overrides.append({
                '_class': 'overrideValue',
                'overrideName': f'{uuid}_symbolID',
                'value': symbol_id
            })
        elif ref_prop['componentPropNodeField'] == 'TEXT_DATA':
            sketch_overrides.append({
                '_class': 'overrideValue',
                'overrideName': f'{uuid}_stringValue',
                'value': prop['value']['textValue']['characters']
            })
        else:  # VISIBLE / INHERIT_FILL_STYLE_ID
            # TODO: Implement detaching of properties
            print(f"Unsupported property: {ref_prop['componentPropNodeField']}. Will detach")
            return None

    return sketch_overrides


def find_ref(node, ref_id):
    refs = [ref for ref in node.get('componentPropRefs', []) if
            ref['defID'] == ref_id and not ref['isDeleted']]
    if refs:
        return refs[0], node

    for ch in node['children']:
        r = find_ref(ch, ref_id)
        if r:
            return r

    return None


def detach_symbol(figma_instance):
    # Find symbol master
    figma_master = context.figma_node(figma_instance['symbolData']['symbolID'])
    detached_children = copy.deepcopy(figma_master['children'], {})

    # Apply overrides. Can we use derivedSymbolData?
    overrides = {
        o['guidPath']['guids'][0]: o
        for o in figma_instance['symbolData']['symbolOverrides']
    }
    for c in detached_children:
        apply_overrides(c, figma_instance['guid'], overrides)

    figma_instance['children'] = detached_children


def apply_overrides(figma, instance_id, overrides):
    ov = overrides.get(figma['guid'])
    if ov:
        figma.update(ov)

    # Generate a unique ID by concatenating instance_id + node_id
    figma['guid'] = (*instance_id, *figma['guid'])

    for c in figma['children']:
        apply_overrides(c, overrides)
