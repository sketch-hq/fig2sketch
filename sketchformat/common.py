class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_json(self):
        return f"{{{self.x}, {self.y}}}"

    def from_array(array):
        return Point(x=array[0], y=array[1])

    def __eq__(self, other):
        if (isinstance(other, Point)):
            return self.x == other.x and self.y == other.y
        return False
