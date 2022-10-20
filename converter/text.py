from . import base
import utils
import itertools
from .context import context
import copy

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

TEXT_BEHAVIOUR = {
    'NONE': 2,
    'WIDTH_AND_HEIGHT': 0,
    'HEIGHT': 1,
}

# Forces a mask on resizingContraints if the text is set to auto-width/height
CONSTRAINT_MASK_FOR_AUTO_RESIZE = {
    'NONE': 0b111111,
    'WIDTH_AND_HEIGHT': 0b101101,
    'HEIGHT': 0b101111,
}

# Sketch (CoreText?) scales up emojis for small font sizes.
# This table undoes this conversation, so we can match Figma better
EMOJI_SIZE_ADJUST = {
    2: 1.5,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 5.5,
    8: 6,
    9: 7,
    10: 7.5,
    11: 8,
    12: 9,
    13: 10,
    14: 10.5,
    15: 11,
    16: 12,
    17: 13,
    18: 13.5,
    19: 14,
    20: 15,
    21: 16,
    22: 18,
    23: 20,
    24: 22,
    25: 24
}

EMOJI_FONT = 'AppleColorEmoji'


def convert(figma_text):
    text_resize = figma_text.get('textAutoResize', 'NONE')
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
        # No good way to calculate this, so we overestimate by setting the frame
        'glyphBounds': f'{{{{0, 0}}, {utils.point_to_string(figma_text["size"])}}}',
        'lineSpacingBehaviour': 2,
        'textBehaviour': TEXT_BEHAVIOUR[text_resize]
    }
    obj['resizingConstraint'] &= CONSTRAINT_MASK_FOR_AUTO_RESIZE[text_resize]

    # TODO: Implement TextStyle
    obj['style'].textStyle = text_style(figma_text)

    if len(obj['attributedString']['attributes']) > 1:
        obj['style'].fills = []

    return obj


def text_style(figma_text):
    if figma_text['fontName']['family'] != EMOJI_FONT:
        context.record_font(figma_text['fontName'])

    fills = figma_text.get('fillPaints', [{}])
    if not fills:
        # Set a transparent fill if no fill is set
        fills = [{
            'color': {
                'r': 0,
                'g': 0,
                'b': 0,
                'a': 0
            }
        }]

    obj = {
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
                'red': fills[0].get('color', {}).get('r', 0),
                'green': fills[0].get('color', {}).get('g', 0),
                'blue': fills[0].get('color', {}).get('b', 0),
                'alpha': fills[0].get('color', {}).get('a', 1)
            },
            'textStyleVerticalAlignmentKey': AlignVertical[figma_text['textAlignVertical']],
            **text_decoration(figma_text),
            'kerning': kerning(figma_text),
            'paragraphStyle': {
                '_class': 'paragraphStyle',
                'alignment': AlignHorizontal[figma_text['textAlignHorizontal']],
                **line_height(figma_text),
            }
        },
        'verticalAlignment': AlignVertical[figma_text['textAlignVertical']],
    }

    if figma_text.get('paragraphSpacing', 0) != 0:
        obj['encodedAttributes']['paragraphStyle']['paragraphSpacing'] = figma_text[
            'paragraphSpacing']

    return obj


def override_characters_style(figma_text):
    # The attributes of the Sketch string, our output
    attributes = []

    # Map from Figma styleID to the overridden properties
    override_table = utils.get_style_table_override(figma_text['textData'])

    # List of character styles. For each style, points to the appropriate styleID
    character_styles = figma_text['textData'].get('characterStyleIDs', [])
    all_character_styles = itertools.chain(character_styles, itertools.repeat(0))

    # List of glyphs, taken in pairs (AB, BC, CD). Used to know when to switch from
    # one glyph to another. Used to identify emojis that can span multiple codepoints
    # Add a fake glyph to the end that never gets reached for iteration purposes
    glyph_pairs = itertools.pairwise(figma_text['textData']['glyphs'] + [{'firstCharacter': -1}])
    current_glyph, next_glyph = next(glyph_pairs)

    # Keep track of what the previous style was and when it started
    last_style = text_style(figma_text)
    first_pos = 0

    # Lengths in Figma are given in codepoints. In Sketch, they are given in UTF16 code-units
    # So we keep the Sketch position independently, taking into account UTF16 encoding
    sketch_pos = 0

    # Iterate over all characters in Figma input, including their style id and position
    for pos, (style_id, character) in enumerate(
            zip(all_character_styles, figma_text['textData']['characters'])):
        # Check if we are still in the same glyph or we have to advance
        # We always advance except in multi-codepoint emojis (e.g: families)
        if pos == next_glyph['firstCharacter']:
            current_glyph, next_glyph = next(glyph_pairs)

        # Compute the override for this character. Aside from Figma style override,
        # we have to set the emoji font if this is an emoji (Figma doesn't expose this change)
        style_override = copy.deepcopy(override_table[style_id])
        override_fills = override_table[current_glyph['styleID']].get('fillPaints', [{}])
        is_emoji = override_fills and override_fills[0].get('type') == 'EMOJI'

        if is_emoji:
            style_override['fontName'] = {'family': EMOJI_FONT, 'postscript': EMOJI_FONT}
            # The following makes Sketch follow Figma a bit more closely visually
            font_size = style_override.get('fontSize', figma_text['fontSize'])
            scaled_font_size = EMOJI_SIZE_ADJUST.get(font_size)
            if scaled_font_size:
                style_override['fontSize'] = scaled_font_size

        # If the style changed (as seen by Sketch), convert the previous style run
        current_style = text_style({**figma_text, **style_override})
        if current_style != last_style and pos != 0:
            attributes.append({
                '_class': 'stringAttribute',
                'location': first_pos,
                'length': sketch_pos - first_pos,
                'attributes': last_style['encodedAttributes']
            })
            first_pos = sketch_pos

        last_style = current_style

        # Characters from supplementary planes are encoded in UTF16 as 2 code units
        # Advance the Sketch position accordingly
        if ord(character) > 0xFFFF:
            sketch_pos += 2
        else:
            sketch_pos += 1

    # Save the last style run
    attributes.append({
        '_class': 'stringAttribute',
        'location': first_pos,
        'length': sketch_pos - first_pos,
        'attributes': last_style['encodedAttributes']
    })

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
        match figma_text['letterSpacing']:
            case {'units': 'PIXELS', 'value': pixels}:
                return pixels
            case {'units': 'PERCENT', 'value': percent}:
                return figma_text['fontSize'] * percent / 100
            case _:
                raise Exception(f'Unknown letter spacing unit')
    else:
        return 0


def line_height(figma_text):
    if 'lineHeight' in figma_text:
        match figma_text['lineHeight']['units']:
            case 'PIXELS':
                # Fixed line height
                return {
                    'maximumLineHeight': figma_text['lineHeight']['value'],
                    'minimumLineHeight': figma_text['lineHeight']['value']
                }
            case 'PERCENT':
                # Relative to normal line height. We only see this in Figma as 100% when
                # in Auto mode (natural baselines)
                if figma_text['lineHeight']['value'] != 100:
                    raise Exception(
                        f"Unexpected lineHeight = {figma_text['lineHeight']['value']} PERCENT")
                return {}
            case 'RAW':
                # Relative to font size of each line.
                # TODO: Sketch does not support this if text sizes change over lines.
                # We just set constant baseline as appropriate for the first line.
                # We can do better using figma.textData.baselines information (applying lineHeight
                # overrides to our attributedString)

                # TODO: If < 1, Figma and Sketch calculate the first line position differently
                # Sketch seems to set it to min(lineHeight, lineAscent). In Figma, you can check
                # baselines[0][position]
                # Maybe we should change the frame position in Sketch to account for this?
                line_height = round(figma_text['fontSize'] * figma_text['lineHeight']['value'])
                return {
                    'maximumLineHeight': line_height,
                    'minimumLineHeight': line_height
                }
            case _:
                raise Exception(f'Unknown line height unit')
    else:
        return 0


def text_transformation(figma_text):
    if 'textCase' in figma_text:
        return ({'MSAttributedStringTextTransformAttribute': TextCase[figma_text['textCase']]})
    else:
        return {}
