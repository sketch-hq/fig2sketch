import math


class FigNode(dict):
    @property
    def x(self):
        return self['transform']['m02']

    @property
    def y(self):
        return self['transform']['m12']

    @property
    def rotation(self):
        return math.degrees(math.atan2(
            -self["transform"]["m10"],
            self["transform"]["m00"]
        ))

    # Allows node.patata to work the same as node['patata']
    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return self[name]
