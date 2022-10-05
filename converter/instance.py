from . import base
import utils

def convert(figma_instance):
    return {
        **base.base_shape(figma_instance),
        "_class": "symbolInstance",
        'name': figma_instance.name,
        'symbolID': utils.gen_object_id((figma_instance['symbolData']['symbolID']['sessionID'], figma_instance['symbolData']['symbolID']['localID']))
    }


def master_instance(figma_symbol):
    return {
        **base.base_shape(figma_symbol),
        "_class": "symbolInstance",
        'do_objectID': utils.gen_object_id(figma_symbol.id, b'master_instance'),
        'name': figma_symbol.name,
        'symbolID': utils.gen_object_id(figma_symbol.id)
    }
