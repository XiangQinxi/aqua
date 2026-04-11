import typing

from ..cmm import CharmyManager
from ..const import MANAGER_ID, DrawingMode
from ..event import Event, EventHandling
from ..object import CharmyObject
from ..pos import Pos
from ..size import Size


class WindowBase(EventHandling, CharmyObject):
    """WindowBase is a base class for window.

    Args:
        parent: The CharmyManager object,
        title: The title of the window,
        size: The size of the window,
        fha: Whether to force hardware acceleration
        drawing_mode: The drawing mode of the window,
    """

    def __init__(
        self,
        parent: CharmyManager | None = None,
        *,
        title: str = "Charmy GUI",
        size: tuple[int, int] = (100, 100),
        fha: bool = True,
        drawing_mode: DrawingMode = DrawingMode.RETAINED,
    ):
        super().__init__()

        # Init parent attribute
        if parent is None:
            parent = self.get_obj(MANAGER_ID)

        if isinstance(parent, CharmyManager):
            self.manager = parent
        elif isinstance(parent, WindowBase):
            self.manager = parent.manager
        self.manager.add_window(self)

        # Init Attributes
        self.ui_draw_func = None
        self.frameworks = self.cget("frameworks")
        self.drawing_mode = drawing_mode

        match self.frameworks.ui_name:
            case "GLFW":
                self.glfw = self.frameworks.ui.glfw
            case _:
                raise ValueError(f"Unknown UI Framework: {self.frameworks.ui_name}")

        match self.frameworks.drawing_name:
            case "SKIA":
                self.skia = self.frameworks.drawing.skia
                self.drawing_surface = None
            case _:
                raise ValueError(
                    f"Unknown Drawing Framework: {self.frameworks.drawing_name}"
                )

        match self.frameworks.backend_name:
            case "OPENGL":
                self.opengl = self.frameworks.backend.opengl
                self.opengl_GL = self.frameworks.backend.opengl_GL
                self.backend_context = None
            case _:
                raise ValueError(
                    f"Unknown Backend Framework: {self.frameworks.backend_name}"
                )

        self.pos = (0, 0)  # Always (0, 0)
        self.canvas_pos = (0, 0)  # Always (0, 0)
        self.root_pos = (0, 0)  # The position of the window
        self._size = (size[0], size[1])  # The size of the window
        self._title = title  # The title of the window

        self.is_dirty: bool = True
        self.is_force_hardware_acceleration: bool = fha
        self.is_visible: bool = False  # Is the window visible
        self.is_alive: bool = False  # Is the window alive

        self.the_window = self.create()  # GLFW/SDL Window

        self.create_event_bounds()

        self.bind("move", self._on_move)
        self.bind("resize", self._on_resize)

    def create(self):
        """Create the window."""
        arg = self.frameworks.ui.create(
            size=self.size,
            title=self.title,
            fha=self.is_force_hardware_acceleration,
        )

        _root_point = self.root_pos = (arg["pos"][0], arg["pos"][1])

        self.is_visible = True
        self.is_alive = True

        return arg["window"]

    def create_event_bounds(self):
        """Create event bounds."""
        self.frameworks.ui.create_event_bounds(the_window=self.the_window, window_class=self)

    def update(self):
        """Update the window. When is_dirty is True, draw the window."""
        if self.is_visible:
            match self.drawing_mode:
                case DrawingMode.IMMEDIATE:
                    self.draw()
                case DrawingMode.RETAINED:
                    if self.is_dirty:
                        self.draw()
                        self.is_dirty = False

    import contextlib

    @contextlib.contextmanager
    def skia_surface(self, arg: typing.Any):
        """Create a Skia surface for the window.

        :param arg: GLFW or SDL2 Window/Surface
        :return: Skia Surface
        """
        match self.cget("ui.framework.name"):
            case "GLFW":
                if not self.glfw.get_current_context() or self.glfw.window_should_close(arg):
                    yield None
                    return

                match self.cget("backend.framework.name"):
                    case "OPENGL":
                        match self.cget("drawing.framework.name"):
                            case "SKIA":
                                self.backend_context = self.skia.GrDirectContext.MakeGL()
                                fb_width, fb_height = self.glfw.get_framebuffer_size(arg)
                                backend_render_target = self.skia.GrBackendRenderTarget(
                                    fb_width,
                                    fb_height,
                                    0,
                                    0,
                                    self.skia.GrGLFramebufferInfo(0, self.opengl_GL.GL_RGBA8),
                                )
                                surface = self.skia.Surface.MakeFromBackendRenderTarget(
                                    self.backend_context,
                                    backend_render_target,
                                    self.skia.kBottomLeft_GrSurfaceOrigin,
                                    self.skia.kRGBA_8888_ColorType,
                                    self.skia.ColorSpace.MakeSRGB(),
                                )
                                self.backend_context.setResourceCacheLimit(16 * 1024 * 1024)

                                if surface is None:
                                    raise RuntimeError("Failed to create Skia surface")

                                yield surface

            case "SDL":
                import ctypes

                width, height = arg.w, arg.h
                pixels_ptr = arg.pixels
                pitch = arg.pitch

                # SDL 像素包装成 buffer
                buf_type = ctypes.c_uint8 * (pitch * height)
                buf = buf_type.from_address(pixels_ptr)  # NOQA

                imageinfo = self.skia.ImageInfo.MakeN32Premul(width, height)  # NOQA
                surface = self.skia.Surface.MakeRasterDirect(imageinfo, buf, pitch)

                if surface is None:
                    raise RuntimeError("Failed to create Skia surface")

                yield surface  # ⚠️ 必须用 yield，不要 return

    def draw(self, event: Event | None = None) -> None:  # NOQA
        """Draw the window.

        Args:
            event (CEvent, optional): The event that triggered the draw. Defaults to None.
        """
        if self.is_visible:
            # Set the current context for each arg
            # 【为该窗口设置当前上下文】
            match self.cget("ui.framework.name"):
                case "GLFW":
                    self.frameworks.ui.make_context_current(self.the_window)

                    match self.cget("drawing.framework.name"):
                        case "SKIA":
                            # Create a Surface and hand it over to this arg.
                            # 【创建Surface，交给该窗口】
                            with self.skia_surface(self.the_window) as self.drawing_surface:  # NOQA
                                if self.drawing_surface:
                                    with self.drawing_surface as canvas:
                                        # Determine and call the drawing function of this arg.
                                        # 【判断并调用该窗口的绘制函数】
                                        if self.ui_draw_func:
                                            self.ui_draw_func(canvas)

                                    self.drawing_surface.flushAndSubmit()
                case "SDL":
                    import sdl2  # NOQA

                    surface = sdl2.SDL_GetWindowSurface(self.the_window).contents

                    with self.skia_surface(surface) as self.drawing_surface:  # NOQA
                        if self.drawing_surface:
                            with self.drawing_surface as canvas:
                                if self.ui_draw_func:
                                    self.ui_draw_func(canvas)

                    sdl2.SDL_UpdateWindowSurface(self.the_window)  # NOQA

            if self.is_alive:
                self.frameworks.ui.swap_buffers(self.the_window)

        if self.backend_context:
            self.backend_context.freeGpuResources()
            self.backend_context.releaseResourcesAndAbandonContext()
        # for child in self.children:
        #    child.need_redraw = False
        self.trigger(Event(self, "draw"))

    def dirty(self):
        """Set the dirty flag."""
        self.is_dirty = True

    def cancel_dirty(self):
        """Cancel the dirty flag."""
        self.is_dirty = False

    def destroy(self) -> None:
        """Destroy the window.

        :return: None
        """
        # self._event_init = False
        # print(self.id)
        try:
            self.frameworks.ui.destroy(the_window=self.the_window)
        except TypeError:
            pass
        finally:
            self.is_alive = False
            # self.draw_func = None
            self.the_window = None  # Clear the reference

    def can_be_close(self, value: bool | None = None) -> typing.Self | bool:
        """Set whether the window can be closed.

        Prevent users from closing the window, which can be used in conjunction with prompts like "Save before closing?"

        >>> def delete(_: SkEvent):  # NOQA
        >>>     window.can_be_close(False)  # NOQA
        >>> window.bind("delete_window", delete)  # NOQA


        :param value: Whether the window can be closed
        :return: None
        """
        match self.cget("ui.framework.name"):
            case "GLFW":
                import glfw

                if value is not None:
                    glfw.set_window_should_close(self.the_window, value)
                    return self
                else:
                    if self.the_window:
                        return glfw.window_should_close(self.the_window)
                    else:
                        return False
        return True

    # region Property
    @property
    def title(self) -> str | None:
        """Get the title of the window.

        Returns:
            str | None: Title of the window
        """
        return self._title

    @title.setter
    def title(self, text: str) -> None:
        """Set the title of the window.

        Args:
            text (str): Title to set
        Returns:
            None
        """
        self.frameworks.ui.set_title(the_window=self.the_window, title=text)

    @property
    def size(self) -> tuple[int | float, int | float]:
        """Get the size of the window.

        Returns:
            Size: Size of the window
        """
        return self._size

    @size.setter
    def size(self, size: Size | tuple[int, int]) -> None:
        """Resize the window to the given size.

        Args:
            size: Size to resize.
        Returns:
            None
        """
        self.frameworks.ui.set_size(the_window=self.the_window, size=size)

    def move(self, pos: Pos | tuple[int, int]) -> None:
        """Move the window to the given position.

        Args:
            pos: Position to move
        Returns:
            None
        """
        self.frameworks.ui.set_pos(the_window=self.the_window, pos=pos)

    # endregion

    # region Events

    def _on_move(self, event: Event):
        """Handle the move event.

        Args:
            event (Event): The move event.
        """
        _root_point = self.root_pos
        _root_point = (event["x_root"], event["y_root"])

    def _on_resize(self, event: Event):
        """Handle the resize event.

        Args:
            event (Event): The resize event.
        """
        self.size = (event["width"], event["height"])
        self.dirty()

    # endregion
