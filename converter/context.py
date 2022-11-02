from . import component, page


class Context:
    def init(self, components_page, id_map):
        self._figma_components = {node['guid']: node for node in components_page['children']}
        self._sketch_components = {}
        self.symbols_page = None
        self._node_by_id = id_map
        self._used_fonts = set()

        # Where to position symbols of the specified width
        # width -> (x, y)
        self._symbol_position = {0: [0, 0]}

    def component(self, cid):
        figma_component = self._figma_components.get(cid)
        if figma_component is None:
            return None

        # See if we can convert this component to a Sketch swatch
        sketch_component = self._sketch_components.get(cid)
        if not sketch_component:
            sketch_component = component.convert(figma_component)
            if sketch_component is not None:
                self._sketch_components[cid] = sketch_component

        return figma_component, sketch_component

    def sketch_components(self):
        return self._sketch_components.values()

    def add_symbol(self, sketch_symbol):
        if not self.symbols_page:
            self.symbols_page = page.symbols_page()

        self.symbols_page.layers.append(sketch_symbol)
        self._position_symbol(sketch_symbol)

    def figma_node(self, fid):
        return self._node_by_id[fid]

    def record_font(self, figma_font_name):
        font_descriptor = (figma_font_name['family'], figma_font_name['style'])
        self._used_fonts.add(font_descriptor)

    def used_fonts(self):
        return self._used_fonts

    def _position_symbol(self, sketch_symbol):
        # Mimics Sketch positioning algorith:
        #   All symbols of the same width go in the same column
        #   Each different width goes into a new column
        frame = sketch_symbol['frame']
        width = frame['width']

        position = self._symbol_position.get(width)
        if position:
            # Already have a column for this width, add it at the bottom
            frame['x'] = position[0]
            frame['y'] = position[1]
            position[1] += frame['height'] + 100
        else:
            # Create a new column at the end
            [last_width, [x, _]] = max(self._symbol_position.items(), key=lambda item: item[1][0])
            new_x = x + last_width + 100
            frame['x'] = new_x
            frame['y'] = 0
            self._symbol_position[width] = [new_x, frame['height'] + 100]


context = Context()
