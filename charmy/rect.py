import typing

from .object import CharmyObject


class Rect(CharmyObject):
    """Rect is a class to store the position and size of a rectangle.

    Attributes:
        pos (Pos): the position of the rectangle.
        size (Size): the size of the rectangle.
    """

    def __init__(self):
        super().__init__()
        # 默认是XYWH坐标系
        self.pos = (0, 0)
        self.size = (0, 0)

    def make_XYWH(self, 
                  x: int | float = 0, 
                  y: int | float = 0, 
                  w: int | float = 0, 
                  h: int | float = 0) -> typing.Self:
        self.pos = (x, y)
        self.size = (w, h)
        return self

    def make_LTRB(self, 
                  left: int | float = 0, 
                  top: int | float = 0, 
                  right: int | float = 0, 
                  bottom: int | float = 0) -> typing.Self:
        self.pos = (left, top)
        self.size = (right - left, bottom - top)
        return self

    def __str__(self):
        """Return position in string."""
        return f"Rect({self.pos[0]}, {self.pos[1]}, {self.size[0]}, {self.size[1]})"

    # region Attributes set/get

    @property
    def left(self):
        return self.pos[0]

    @property
    def top(self):
        return self.pos[1]

    @property
    def right(self):
        return self.pos[0] + self.size[0]

    @property
    def bottom(self):
        return self.pos[1] + self.size[1]

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    # endregion
