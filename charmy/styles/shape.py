from __future__ import annotations as _

import typing

import warnings
from dataclasses import dataclass
import math

from ..object import CharmyObject

if typing.TYPE_CHECKING:
    from .texture import Texture
    from ..widgets.window import Window


# Type Point
Point = tuple[int, int]


# region Lines

@dataclass
class LinePath():
    """Base class of all line paths."""

    type: typing.ClassVar[str] = "line_path_class"

    def draw(self, window: Window, texture: Texture, width: int = 5) -> typing.Self:
        """Draw the line.

        :param window: The window to draw line to
        :param texture: The texture of the line
        :param width: Line width in pixels
        """
        backend = window.backend_base.backend
        # 👆 Alias to avoid path to backend properties getting too long. 😅
        if self.type == "line_path_class":
            raise TypeError("LinePath class is a template, cannot be drawn.")
        else:
            if self.type in backend.LineBase.supports:
                # If supported by the windows' backend.
                window.backend_base.drawing_list.append(
                    DrawnLine(self, texture, width)
                    )
                # backend.LineBase.draw_line(self, window, texture)
            else:
                warnings.warn(f"Line type {self.type} is not supported by "
                              f"backend {backend.friendly_name}")
        return self

    @property
    def start_point(self) -> tuple[int, int]:
        raise NotImplementedError

    @property
    def end_point(self) -> tuple[int, int]:
        raise NotImplementedError


@dataclass
class Line(LinePath):
    """Represents lines.

    :param points: List of the 2 points that determines the line
    """
    type: typing.ClassVar[str] = "line"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) != 2:
            raise ValueError("A line must be defined with and only with 2 points.")

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]

@dataclass
class PolyLine(LinePath):
    """Represents polylines.

    :param points: List of points that determines the line(s)
    """
    type: typing.ClassVar[str] = "polyline"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) <= 1:
            raise ValueError("At least 2 points are required to form a (poly)line.")
        # elif len(self.points) == 2:
        #     warnings.warn(
        #         "Consider using Line for exactly 2 points (although using PolyLine still works).",
        #         stacklevel=2
        #     )

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]

@dataclass
class CircleArc(LinePath):
    """Represents circle arcs.

    :param center: Coordinates of the center of the circle
    :param radius: Radius of the circle, in integer
    :param start_orient: Starting orientation in integer degrees
    :param end_orient: Ending orientation in integer degrees
    """
    center: tuple[int, int]
    type: typing.ClassVar[str] = "circle_arc"
    radius: int
    start_orient: int
    end_orient: int

    @property
    def start_point(self) -> tuple[int, int]:
        # Vibed with VSCode Copilot, model GPT-5 mini
        # Compute start point from center, radius and start_orient (degrees).
        theta = math.radians(self.start_orient)
        x = self.center[0] + int(round(self.radius * math.cos(theta)))
        y = self.center[1] + int(round(self.radius * math.sin(theta)))
        return (x, y)

    @property
    def end_point(self) -> tuple[int, int]:
        # Vibed with VSCode Copilot, model GPT-5 mini
        # Compute end point from center, radius and end_orient (degrees).
        theta = math.radians(self.end_orient)
        x = self.center[0] + int(round(self.radius * math.cos(theta)))
        y = self.center[1] + int(round(self.radius * math.sin(theta)))
        return (x, y)

    def draw(self, window:Window, texture: Texture, width: int = 5) -> typing.Self:
        """Draw the circle arc, convert to Bezier curves if backend does not support.
        
        :param window: The window to draw line to
        :param texture: The texture of the line
        :param width: Line width in pixels
        """
        if window.backend_base.backend.LineBase.supports.circle_arc:
            LinePath.draw(self, window, texture, width)
        else:
            # If backend reports circle arc not supported, then use cubic bezier to simulate
            beziers = self._arc_to_beziers()
            for bezier in beziers:
                bezier.draw(window, texture, width)
        return self

    def _arc_to_beziers(self) -> list[CubicBezier]:
        """Convert an circle arc into a list of cubic Bézier curves.

        This function is vibed with ChatGPT.

        Coordinate system assumptions:
        - 0° is at the top (positive Y direction)
        - Angles increase clockwise

        :return cubic_beziers: List of the cubic beziers
        """

        cx, cy = self.center

        # --- Convert custom angle system to standard math radians ---
        # Math system: 0 rad at +X axis, CCW positive
        def to_math_rad(deg: float) -> float:
            return math.radians(90 - deg)

        start = to_math_rad(self.start_orient)
        end = to_math_rad(self.end_orient)

        # --- Ensure clockwise traversal ---
        # In math coordinates, clockwise means decreasing angle
        delta = end - start
        if delta > 0:
            delta -= 2 * math.pi

        # Clamp to at most one full circle
        if delta < -2 * math.pi:
            delta = -2 * math.pi

        # # Handle full circles
        # if self.start_orient == self.end_orient:
        #     delta = -2 * math.pi

        # --- Split into segments (max 90° each) ---
        max_step = math.pi / 2
        segments = max(1, int(math.ceil(abs(delta) / max_step)))
        step = delta / segments

        beziers: list[CubicBezier] = []

        for i in range(segments):
            t0 = start + i * step
            t1 = start + (i + 1) * step
            dt = t1 - t0

            # Cubic Bézier approximation factor
            alpha = 4 / 3 * math.tan(dt / 4)

            cos0, sin0 = math.cos(t0), math.sin(t0)
            cos1, sin1 = math.cos(t1), math.sin(t1)

            # Endpoints
            x0: int = int(round(cx + self.radius * cos0, 0))
            y0: int = int(round(cy - self.radius * sin0, 0))

            x3: int = int(round(cx + self.radius * cos1, 0))
            y3: int = int(round(cy - self.radius * sin1, 0))

            # Tangent directions
            dx0, dy0 = -sin0, cos0
            dx1, dy1 = -sin1, cos1

            # Control points
            x1: int = int(round(x0 + alpha * self.radius * dx0, 0))
            y1: int = int(round(y0 - alpha * self.radius * dy0, 0))

            x2: int = int(round(x3 - alpha * self.radius * dx1))
            y2: int = int(round(y3 + alpha * self.radius * dy1))

            beziers.append(
                CubicBezier([(x0, y0), (x1, y1), (x2, y2), (x3, y3)])
                )

        return beziers

@dataclass
class EllipseArc(LinePath):
    """Represents arcs trimmed from ellipses.

    :param center: Coordinates of the center of the oval
    :param v_radius: Vertical radius in integer
    :param h_radius: Horizontal radius in integer
    :param rotation: Rotation in integer degrees
    :param start_orient: Starting orientation in integer degrees
    :param end_orient: Ending orientation in integer degrees
    """
    center: tuple[int, int]
    type: typing.ClassVar[str] = "ellipse_arc"
    v_radius: int
    h_radius: int
    rotation: int
    start_orient: int
    end_orient: int

    def __post_init__(self):
        raise NotImplementedError("Ellipse arc is not fully implemented yet.")
        if not -360 < self.rotation < 360:
            self.rotation = self.rotation % 360

@dataclass
class QuadraticBezier(LinePath):
    """Represents quadratic Bezier curves."""
    type: typing.ClassVar[str] = "quadratic_bezier"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) != 3:
            raise ValueError("Quadratic Bezier curves must be defined with and only with 3 points!")

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]
    
    def draw(self, window: Window, texture: Texture, width: int = 5):
        """Draw the quadratic Bezier, convert to cubic Bezier curves if backend does not support.
        
        :param window: The window to draw line to
        :param texture: The texture of the line
        :param width: Line width in pixels
        """
        if window.backend_base.backend.LineBase.supports.quadratic_bezier:
            LinePath.draw(self, window, texture, width)
        else:
            # Use cubic Beziers to express, vibed with ChatGPT
            p0, p1, p2 = self.points
            k = 2/3
            CubicBezier([
                p0,
                (int(round(p0[0] + k*(p1[0] - p0[0]), 0)), 
                 int(round(p0[1] + k*(p1[1] - p0[1]), 0))),
                (int(round(p2[0] + k*(p1[0] - p2[0]), 0)), 
                 int(round(p2[1] + k*(p1[1] - p2[1]), 0))),
                p2
            ]).draw(window, texture, width)

@dataclass
class CubicBezier(LinePath):
    """Represents cubic Bezier curves."""
    type: typing.ClassVar[str] = "cubic_bezier"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) != 4:
            raise ValueError("Cubic Bezier curves must be defined with and only with 4 points!")

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]

# endregion

# region Shapes

class CharmyShapeError(Exception): ...

class AnyShape(CharmyObject):
    """Base class of all shapes."""

    def __init__(self, lines: list[LinePath]):
        """To represent a shape.

        :param lines: List of lines forming the shape.
        """
        super().__init__()

        self.lines: list[LinePath] = lines

        if not self._validate_lines():
            raise CharmyShapeError("Specified lines do not form a valid closed shape.")

    def _validate_lines(self):
        """Validate if lines form a valid closed shape."""
        last_line_end: tuple[int, int] = self.lines[-1].end_point
        # 👆 Set last_line_end to end point of the last line, a valid shape must be closed.
        for line in self.lines:
            if line.start_point != last_line_end:
                return False
            last_line_end = line.end_point
            # 👆 Set last_line_end to end point of current line, lines must be connected.
        return True

    def draw(self):
        """Draw the shape using backend."""
        NotImplemented

# endregion

# region Drawn Lines / Shapes

@dataclass
class DrawnLine():
    """A class used to represent lines drawn to windows."""
    line: LinePath
    texture: Texture
    width: int = 5

@dataclass
class DrawnShape():
    """A Class used to represent shapes drawn to windows"""
    shape: AnyShape
    texture: Texture
    border_width: int = 0
    border_texture: Texture | None = None

# endregion