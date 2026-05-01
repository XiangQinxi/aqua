# The Genesis Backend
# 2026 by XiangQinXi & rgzz666

# This is a backend for early development only! 
# It is also used as an example of developing a Charmy backend.

# Under dev

import typing

from dataclasses import dataclass
import sdl2
import sdl2.ext
import cairo
import sys
import ctypes
import math

from . import template

import charmy

# if typing.TYPE_CHECKING:
#     import charmy.styles.shape as charmy.shape
#     import charmy.styles.texture as cm_texture


class Backend(template.Backend):
    """The Genesis backend."""

    name: typing.ClassVar[str] =            "genesis"
    friendly_name: typing.ClassVar[str] =   "Genesis (early development)"
    version: typing.ClassVar[str] =         "0.1.0"
    author: typing.ClassVar[list[str]] =    ["XiangQinXi", "rgzz666"]

    def __init__(self):
        """APIs are aliased here."""
        super().__init__()

        self.WindowBase: type[WindowBase] = WindowBase
        self.LineBase: type[LineBase] = LineBase
        self.ShapeBase: type[ShapeBase] = ShapeBase
        self.TextureBase: type[TextureBase] = TextureBase
    
    def backend_init(self, **kwargs) -> None:
        sdl2.ext.init()


class WindowBackdropSupportState(template.WindowBackdropSupportState):
    """Represents support states of backdrop effects of windows held by this backend."""
    color                   : bool = True
    gradient                : bool = False
    image                   : bool = False
    transparent             : bool = False
    alpha                   : bool = False
    blur                    : bool = False
    transformation          : bool = False
    any_filter              : bool = False

class WindowSupportState(template.WindowSupportState):
    """Flags all supported window features."""
    set_title               : bool = True
    set_icon                : bool = True
    resize                  : bool = True
    set_scale_mode          : bool = True
    set_background          : bool = True
    translucent             : bool = True
    backdrop                : type[WindowBackdropSupportState] = WindowBackdropSupportState
    set_state               : bool = True
    fullscreen              : bool = True
    customize_titlebar      : bool = True

class WindowBase(template.WindowBase):
    """Window APIs in Genesis backend."""
    supports = WindowSupportState
    Backend = Backend

    def __init__(self, backend: template.Backend):
        """Creates a window.
        
        :param backend: The backend that this window uses (can be get from CharmyManager)
        """
        super().__init__(backend)

        self.title = "Charmy SDL2 Window"
        self.size = (540, 480)


        # create window
        self.window: typing.Any = sdl2.SDL_CreateWindow(
            self.title.encode('utf-8'),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            self.size[0], self.size[1],
            sdl2.SDL_WINDOW_SHOWN,
        )

        if not self.window:
            raise RuntimeError("Can't create window")
        self._window_surface = sdl2.SDL_GetWindowSurface(self.window)

        if self.window == None:
            raise RuntimeError("Can't create window")

        # Initialize Cairo canvas
        self.surface: cairo.ImageSurface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.size[0], self.size[1])
        self.cairo_context: cairo.Context = cairo.Context(self.surface)
        self.cairo_context.set_source_rgba(0, 0, 0, 0)  # Transparent back
        self.cairo_context.paint()

    def show(self) -> typing.Self:
        """Show the window.

        :return self: The WindowBase itself
        """
        # self.window.show()
        return self

    def set_title(self, new: str) -> typing.Self:
        """Set window title."""
        self.window.title = new
        return self
    
    def update(self):
        """Update the window.
        
        :return self: The WindowBase itself
        """
        self.draw_frame(self.drawing_list)

        # Following Vibed with Deepseek

        # Get Cairo data（memoryview）
        cairo_data = self.surface.get_data()

        # Get SDL2 window surface
        self._window_surface = sdl2.SDL_GetWindowSurface(self.window)
        # Lock the surface
        sdl2.SDL_LockSurface(self._window_surface)

        # Get pixels pointer
        pixels_ptr = self._window_surface.contents.pixels
        # Improvement: Get lower level pointer directly to avoid tobytes() copy
        # Calc data size
        pitch = self._window_surface.contents.pitch
        data_size = pitch * self.size[1]
        # Convert memoryview to ctypes data
        cairo_ptr = ctypes.cast(
            (ctypes.c_char * data_size).from_buffer(cairo_data),
            ctypes.c_void_p
        )

        # Copy data
        ctypes.memmove(pixels_ptr, cairo_ptr, data_size)
        # Unlock surface
        sdl2.SDL_UnlockSurface(self._window_surface)

        # Update display
        sdl2.SDL_UpdateWindowSurface(self.window)

        # Handle events
        for event in sdl2.ext.get_events():
            match event.type:
                case sdl2.SDL_QUIT:
                    sys.exit(0)
                    NotImplemented

    def draw_frame(self, 
                   drawing_list: list[charmy.shape.DrawnShape | charmy.shape.DrawnLine]) -> None:
        """Draw a frame for the window.
        
        :param drawing_list: The list of the objects to draw
        """
        for drawing_obj in drawing_list:
            if isinstance(drawing_obj, charmy.shape.DrawnLine):
                LineBase.draw_line(drawing_obj.line, self, drawing_obj.texture)
            else:
                template.not_implemented_func(Backend.friendly_name)
        # # Test code for drawing, vibed with Doubao or Deepseek (whatever, I forgot)

        # self.cairo_context.set_source_rgba(1, 1, 1, 0)
        # self.cairo_context.paint()
        
        # # 绘制红色圆形
        # self.cairo_context.set_source_rgb(1, 0, 0)  # 完全不透明的红色
        # self.cairo_context.arc(270, 240, 80, 0, 6.28)
        # self.cairo_context.fill()
        
        # # 可选：添加边框让圆形更明显
        # self.cairo_context.set_source_rgb(0, 0, 0)
        # self.cairo_context.arc(270, 240, 80, 0, 6.28)
        # self.cairo_context.set_line_width(2)
        # self.cairo_context.stroke()
    
    def mainloop(self):
        while True:
            self.update()


@dataclass
class LineSupportState(template.LineSupportState):
    """Flags all supported line types."""
    line                : bool = True
    polyline            : bool = True
    circle_arc          : bool = True
    ellipse_arc         : bool = False
    quadratic_bezier    : bool = False
    cubic_bezier        : bool = True

class LineBase(template.LineBase):
    """Represents lines in backend."""
    supports: LineSupportState = LineSupportState()

    @staticmethod
    def draw_line(line: charmy.shape.LinePath, window: WindowBase, 
                  texture: charmy.texture.Texture, line_width: int = 5):
        """To draw a line on a specific window.

        Args:
            line: The line to be drawn
            window: The WindowBase to draw line
        """
        # Detect wrong backend
        if window.Backend != Backend:
            raise RuntimeError(
                "Wrong backend for draw_line()! Asked to draw on a window held by "
                f"{window.backend.friendly_name} but I serve backend {Backend.friendly_name}!"
                )
        # Set texture & line width
        if isinstance(texture, charmy.texture.Color):
            window.cairo_context.set_source_rgba(*[v / 255 for v in texture])
        else:
            template.not_implemented_func(Backend.friendly_name)
        window.cairo_context.set_line_width(line_width)
        # Draw line
        if isinstance(line, charmy.shape.Line):
            window.cairo_context.move_to(*line.points[0])
            window.cairo_context.line_to(*line.points[1])
        elif isinstance(line, charmy.shape.PolyLine):
            window.cairo_context.move_to(*line.points[0])
            for point in line.points:
                window.cairo_context.line_to(*point)
        elif isinstance(line, charmy.shape.CircleArc):
            # window.cairo_context.move_to(*line.center)
            start_orient_rad = line.start_orient * (math.pi / 180)
            end_orient_rad = line.end_orient * (math.pi / 180)
            window.cairo_context.arc(line.center[0], line.center[1], line.radius, 
                                     start_orient_rad, end_orient_rad)
        elif isinstance(line, charmy.shape.CubicBezier):
            window.cairo_context.move_to(*line.points[0])
            window.cairo_context.curve_to(
                *line.points[1], *line.points[2], *line.points[3]
                )
        else:
            template.not_implemented_func(Backend.friendly_name)
        # Draw line
        window.cairo_context.stroke()


class ShapeBase(template.ShapeBase):
    pass

class TextureBase(template.TextureBase):
    pass