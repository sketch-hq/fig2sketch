from . import component, page

class Context:
    def init(self, components_page):
        self._figma_components = { node.id: node for node in components_page.children }
        self._sketch_components = {}
        self.symbols_page = None

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


context = Context()
