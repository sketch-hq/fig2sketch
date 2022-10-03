from . import component

class Context:
    def init(self, components_page):
        self._figma_components = { node.id: node for node in components_page.children }
        self._sketch_components = {}

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

context = Context()
