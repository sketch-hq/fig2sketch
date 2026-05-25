import logging
from urllib.error import HTTPError
from . import component, page, font
from .errors import Fig2SketchWarning
from sketchformat.document import Swatch
from sketchformat.layer_common import AbstractLayer
from sketchformat.layer_group import Page
from typing import Sequence, Tuple, Optional, Dict, IO, List, Set


def find_node_ids(node: Optional[dict]) -> List[Sequence[int]]:
    if not node:
        return []

    found = [node["guid"]]
    for child in node.get("children", []):
        found += find_node_ids(child)

    return found


def find_symbols(node: Optional[dict]) -> List[Sequence[int]]:
    if not node:
        return []

    if node["type"] == "SYMBOL":
        return [node["guid"]]

    found = []
    for child in node.get("children", []):
        found += find_symbols(child)

    return found


class Context:
    def init(
        self, components_page: Optional[dict], id_map: Dict[Sequence[int], dict], color_space: str
    ) -> None:
        self._color_space = color_space
        self._sketch_components: Dict[Sequence[int], Swatch] = {}
        self.symbols_page: Optional[Page] = None
        self._node_by_id = id_map
        self._used_fonts: Dict[Tuple[str, str], Tuple[IO[bytes], str]] = {}
        self._component_symbols = (
            {s: False for s in find_symbols(components_page)} if components_page else {}
        )
        self._component_nodes: Set[Sequence[int]] = set(find_node_ids(components_page))
        self._converted_component_sets: Set[Sequence[int]] = set()

        # Where to position symbols of the specified width
        # width -> (x, y)
        self._symbol_position: Dict[float, List[float]] = {0.0: [0.0, 0.0]}

    def color_space(self) -> int:
        return 2 if self._color_space == "DISPLAY_P3" else 1

    def component(self, cid: Sequence[int]) -> Tuple[dict, Optional[Swatch]]:
        fig_component = self.fig_node(cid)

        # See if we can convert this component to a Sketch swatch
        sketch_component = self._sketch_components.get(cid)
        if not sketch_component:
            sketch_component = component.convert(fig_component)
            if sketch_component is not None:
                self._sketch_components[cid] = sketch_component

        return fig_component, sketch_component

    def sketch_components(self) -> List[Swatch]:
        return list(self._sketch_components.values())

    def add_symbol(self, sketch_symbol: AbstractLayer) -> None:
        if not self.symbols_page:
            self.symbols_page = page.symbols_page()

        self.symbols_page.layers.append(sketch_symbol)
        self._position_symbol(sketch_symbol)

    def fig_node(self, fid: Sequence[int]) -> dict:
        if fid in self._node_by_id:
            return self._node_by_id[fid]
        else:
            raise Fig2SketchWarning("NOD001")

    def record_font(self, fig_font_name):
        font_descriptor = (fig_font_name["family"], fig_font_name["style"])
        font_info = self._used_fonts.get(font_descriptor)
        if font_info:
            return font_info[1]

        try:
            font_file, font_name = font.get_webfont(*font_descriptor)
        except Exception as e:
            if isinstance(e, font.FontNotFoundError) or (
                isinstance(e, HTTPError) and (e.code == 404 or e.code == 400)
            ):
                logging.warning(f"Could not find font {font_descriptor} via Google Fonts")
            else:
                logging.warning(f"Could not download font {font_descriptor}: {e}")

            font_file = None
            if fig_font_name["postscript"]:
                font_name = fig_font_name["postscript"]
            else:
                font_name = f"{fig_font_name['family']}-{fig_font_name['style']}"

        self._used_fonts[font_descriptor] = (font_file, font_name)
        return font_name

    def used_fonts(self) -> Dict[Tuple[str, str], Tuple[IO[bytes], str]]:
        return self._used_fonts

    def is_component_page_symbol(self, sid: Sequence[int]) -> bool:
        return sid in self._component_symbols

    def component_set_for_symbol(self, sid: Sequence[int]) -> Optional[dict]:
        if sid not in self._component_symbols:
            return None

        symbol = self.fig_node(sid)
        parent_id = symbol.get("parent", {}).get("guid")
        if parent_id not in self._component_nodes:
            return None

        parent = self.fig_node(parent_id)
        if parent.get("isStateGroup", False):
            return parent

        return None

    def find_symbol(self, sid: Sequence[int]) -> dict:
        symbol = self.fig_node(sid)
        sid = symbol["guid"]

        if not self._component_symbols.get(sid, True):
            # The symbol is in the component page and has not been converted yet, do it now
            from . import tree

            component_set = self.component_set_for_symbol(sid)
            if component_set:
                component_set_id = component_set["guid"]
                if component_set_id not in self._converted_component_sets:
                    self.add_symbol(tree.convert_node(component_set, ""))
                    self._converted_component_sets.add(component_set_id)
                    for child_symbol_id in find_symbols(component_set):
                        self._component_symbols[child_symbol_id] = True
            else:
                tree.convert_node(symbol, "")
                self._component_symbols[sid] = True

        return symbol

    def _position_symbol(self, sketch_symbol: AbstractLayer) -> None:
        # Mimics Sketch positioning algorithm:
        #   All symbols of the same width go in the same column
        #   Each different width goes into a new column
        frame = sketch_symbol.frame
        width = frame.width

        position = self._symbol_position.get(width)
        if position:
            # Already have a column for this width, add it at the bottom
            frame.x = position[0]
            frame.y = position[1]
            position[1] += frame.height + 100
        else:
            # Create a new column at the end
            [last_width, [x, _]] = max(self._symbol_position.items(), key=lambda item: item[1][0])
            new_x = x + last_width + 100
            frame.x = new_x
            frame.y = 0
            self._symbol_position[width] = [new_x, frame.height + 100]


context = Context()
