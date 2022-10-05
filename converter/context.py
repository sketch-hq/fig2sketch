from . import component, page

class Context:
    def init(self, components_page):
        self._figma_components = { node.id: node for node in components_page.children }
        self._sketch_components = {}
        self.symbols_page = None

        # Where to position symbols of the specified width
        # width -> (x, y)
        self._symbol_position = {0: [0, 0]}

    def component(self, cid):
        figma_component = self._figma_components[cid]

        # See if we can convert this component to a Sketch swatch
        sketch_component = self._sketch_components.get(cid)
        if not sketch_component:
            try:
                sketch_component = component.convert(figma_component)
            except:
                pass
            if sketch_component is not None:
                self._sketch_components[cid] = sketch_component

        return figma_component, sketch_component

    def sketch_components(self):
        return self._sketch_components.values()

    def add_symbol(self, sketch_symbol):
        if not self.symbols_page:
            self.symbols_page = page.symbols_page()

        self.symbols_page['layers'].append(sketch_symbol)
        self._position_symbol(sketch_symbol)

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
