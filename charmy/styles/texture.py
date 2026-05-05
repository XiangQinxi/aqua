import typing

# from ..const import Drawing
# from ..object import CharmyObject as _CharmyObject


# region Texture base class

class Texture:
    pass

# endregion

# region Color

# Color types
RGB: typing.TypeAlias = tuple[int, int, int]
RGBA: typing.TypeAlias = tuple[int, int, int, int]
HEX: typing.TypeAlias = str

class Color(Texture):
    """Represents pure colors."""

    # @typing.overload
    # def __init__(self, r: int, g: int, b: int, a: int = 255): ... # RGB(A)
    # @typing.overload
    # def __init__(self, color: tuple[int, int, int, int] | \
    #              tuple[int, int, int]): ... # Single RGB(A) tuple
    # @typing.overload
    # def __init__(self, color: str): ... # Single HEX string (RRGGBB / RRGGBBAA)

    def __init__(self, color: RGB | RGBA | HEX):
        """Initialize a color object.
        
        :param color: The RGB(A) tuple or the HEX string that represents the color
        """

        self.color: RGBA = (0, 255, 0, 255)

        if isinstance(color, tuple): # Expressed by int tuple
            if len(color) == 4: # RGBA
                self.color = color
            elif len(color) == 3: # RGB
                self.color = (*color, 255)
        elif isinstance(color, str):
            if color[0] == "#": # Remove leading hash if exists
                color = color[1:]
            if len(color) == 6:
                NotImplemented

    def __iter__(self):
        return iter(self.color)

    @property
    def r(self) -> int:
        return self.color[0]
    @property
    def g(self) -> int:
        return self.color[1]
    @property
    def b(self) -> int:
        return self.color[2]
    @property
    def a(self) -> int:
        return self.color[3]

ColorLike: typing.TypeAlias = RGB | RGBA | HEX

# endregion

# region Transparent

class Transparent(Texture):
    """Represents transparent.

    Note that, in actual rendering, items with Transparent texture should be skipped.
    """

    def __init__(self):
        """Initialize a Transparent object."""
        self.color = (0, 0, 0, 0)

    def __iter__(self):
        return iter(self.color)

TransparentLike: typing.TypeAlias = None | tuple[int, int, int, typing.Literal[0]]

# endregion


# region ensure_texture

TextureLike: typing.TypeAlias = ColorLike | TransparentLike

def ensure_texture(texture_like: Texture | TextureLike) -> Texture:
    """Convert TextureLike types into Texture objects."""
    if isinstance(texture_like, Texture):
        result = texture_like
    else:
        # Convert into texture
        if isinstance(texture_like, tuple): # RGB(A)
            if len(texture_like) == 4: # RGBA
                if texture_like[-1] == 0: # Transparent
                    result = Transparent()
                else: # RGBA, not transparent
                    result = Color(texture_like)
            elif len(texture_like) == 3: # RGB
                result = Color(texture_like)
        elif isinstance(texture_like, str): # HEX
            result = Color(texture_like)
        elif texture_like is None: # Transparent
            result = Transparent()
    return result

# endregion