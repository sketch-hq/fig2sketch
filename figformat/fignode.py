import math
import numpy as np

class FigNode(dict):
    @property
    def x(self):
        return self['transform'][0,2]

    @property
    def y(self):
        return self['transform'][1,2]

    @property
    def rotation(self):
        return math.degrees(math.atan2(
            -self['transform'][1,0],
            self['transform'][0,0]
        ))

    # Allows node.patata to work the same as node['patata']
    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self[name]
            except KeyError:
                raise AttributeError
