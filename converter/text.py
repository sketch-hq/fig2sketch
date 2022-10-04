from . import base
import utils
from . import fonts

AlignVertical = {
    'TOP': 0,
    'CENTER': 1,
    'BOTTOM': 2
}

AlignHorizontal = {
    'LEFT': 0,
    'CENTER': 2,
    'RIGHT': 1,
    'JUSTIFIED': 3
}

TextCase = {
    'ORIGINAL': 0,
    'UPPER': 1,
    'LOWER': 2,
    'TITLE': 0
}


def convert(figma_text):
    obj = {
        '_class': 'text',
        **base.base_shape(figma_text),
        'name': figma_text['name'],
        'automaticallyDrawOnUnderlyingPath': False,
        'dontSynchroniseWithSymbol': False,
        'attributedString': {
            '_class': 'attributedString',
            'string': figma_text['textData']['characters'],
            'attributes': override_characters_style(figma_text),
        },
        'glyphBounds': '{{5, 15}, {122, 55}}',
        'lineSpacingBehaviour': 2,
        'textBehaviour': 2,
        'layers': []
    }

    obj['style']['textStyle'] = text_style(figma_text)

    if len(obj['attributedString']['attributes']) > 1:
        obj['style']['fills'] = []

    return obj


def text_style(figma_text):
    fonts.record_figma_font(figma_text['fontName']['family'], figma_text['fontName']['style'])
    return {
        '_class': 'textStyle',
        'encodedAttributes': {
            **text_transformation(figma_text),
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': figma_text['fontName']['postscript'] or figma_text['fontName'][
                        'family'],
                    'size': figma_text['fontSize']
                }
            },
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'red': figma_text.get('fillPaints', [{}])[0].get('color', {}).get('r', 0),
                'green': figma_text.get('fillPaints', [{}])[0].get('color', {}).get('g', 0),
                'blue': figma_text.get('fillPaints', [{}])[0].get('color', {}).get('b', 0),
                'alpha': figma_text.get('fillPaints', [{}])[0].get('color', {}).get('a', 1)
            },
            'textStyleVerticalAlignmentKey': AlignVertical[figma_text['textAlignVertical']],
            **text_decoration(figma_text),
            'kerning': kerning(figma_text),
            'paragraphStyle': {
                '_class': 'paragraphStyle',
                'alignment': AlignHorizontal[figma_text['textAlignHorizontal']],
                'maximumLineHeight': line_height(figma_text),
                'minimumLineHeight': line_height(figma_text),
                'paragraphSpacing': figma_text['paragraphSpacing'] if 'paragraphSpacing' in figma_text else 0
            }
        },
        'verticalAlignment': AlignVertical[figma_text['textAlignVertical']],
    }


def override_characters_style(figma_text):
    attributes = []
    char_length = len(figma_text['textData']['characters'])

    if 'styleOverrideTable' in figma_text['textData']:
        override_table = utils.get_style_table_override(figma_text['textData'])

        last_style = 0
        count = 0
        first_pos = 0

        # We need an extra iteration to create the 'stringAttribute' for the last group
        for pos in range(0, char_length + 1):
            try:
                style_id = figma_text['textData']['characterStyleIDs'][pos]
            except IndexError:
                style_id = 0 if pos < char_length else -1

            if style_id == last_style or pos == 0:
                count += 1
            else:
                attributes.append({
                    '_class': 'stringAttribute',
                    'location': first_pos,
                    'length': count,
                    'attributes':
                        text_style({**figma_text, **override_table[last_style]})[
                            'encodedAttributes']
                })
                count = 1
                first_pos = pos

            last_style = style_id

    if len(attributes) == 0:
        attributes = [{
            '_class': 'stringAttribute',
            'location': 0,
            'length': char_length,
            'attributes': text_style(figma_text)['encodedAttributes']
        }]

    return attributes


def text_decoration(figma_text):
    decoration = {}

    if 'textDecoration' in figma_text:
        match figma_text['textDecoration']:
            case 'UNDERLINE':
                decoration = {'underlineStyle': 1}
            case 'STRIKETHROUGH':
                decoration = {'strikethroughStyle': 1}

    return decoration

def kerning(figma_text):
    if 'letterSpacing' in figma_text:
        match figma_text['letterSpacing']['units']:
            case 'PIXELS':
                return figma_text['letterSpacing']['value']
            case 'PERCENT':
                return figma_text['fontSize'] * (figma_text['letterSpacing']['value'] / 100)
            case _:
                raise Exception(f'Unknown letter spacing unit')
    else:
        return 0

def line_height(figma_text):
    if 'lineHeight' in figma_text:
        match figma_text['lineHeight']['units']:
            case 'PIXELS':
                return figma_text['lineHeight']['value']
            case 'PERCENT':
                # Relative to normal line height
                return round(figma_text['textData']['baselines'][0]['lineHeight'] * (figma_text['lineHeight']['value'] / 100))
            case 'RAW':
                # Relative to font size
                # TODO: If < 1, Figma and Sketch calculate the first line position differently
                # Sketch seems to set it to min(lineHeight, lineAscent). In Figma, you can check baselines[0][position]
                # Maybe we should change the frame position in Sketch to account for this?
                return round(figma_text['fontSize'] * figma_text['lineHeight']['value'])
            case _:
                raise Exception(f'Unknown line height unit')
    else:
        return 0

def text_transformation(figma_text):
    if 'textCase' in figma_text:
        return({'MSAttributedStringTextTransformAttribute': TextCase[figma_text['textCase']]})
    else:
        return {}
