import typing

from ..object import CharmyObject

if typing.TYPE_CHECKING:
    from ..backend.template import Backend


class _LinePath(CharmyObject):
    def __init__(self, points: list[tuple[int, int]], backend: Backend):
        """Initialize the line.
        
        Args:
            points: List of points that determines the line.
            backend: The backend used
        """
        self.type: str = "line_path_class"
        self.points: list[tuple[int, int]] = points
        self.backend = backend

    def draw(self, window):
        """Draw the line"""
        if self.class_name == "_LinePath":
            raise TypeError("_LinePath class is a template, cannot be drawn.")
        else:
            if self.type in self.backend.LineBase.supports:
                NotImplemented
    

class PolyLine(_LinePath):