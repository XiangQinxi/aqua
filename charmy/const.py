"""Charmy constants."""
import typing
import dataclasses
# import sys
from os import environ
from enum import Enum

if typing.TYPE_CHECKING:
    from . import cmm



@dataclasses.dataclass
class Configs():
    single_manager_mode = environ.get("CHARMY_SINGLE_MANAGER", False)
    default_manager     = environ.get("CHARMY_BACKEND", "auto")


class Common():
    managers_instances: list[cmm.CharmyManager] = []
    if Configs.single_manager_mode:
        NotImplemented
        managers_instances.append(NotImplemented)


class ID(Enum):
    """ID is an enum to store object ID.

    AUTO: Auto generate ID.
    NONE: No ID.
    """

    AUTO = 0
    NONE = 1


# @dataclasses.dataclass
# class Backends:
#     OPENGL = opengl = "OPENGL"


# @dataclasses.dataclass
# class UI:
#     GLFW = glfw = "GLFW"
#     SDL = sdl = "SDL"


# @dataclasses.dataclass
# class Drawing:
#     SKIA = skia = "SKIA"


class DrawingMode(Enum):
    """DrawingMode is an enum to store drawing mode.
    IMMEDIATE(immediate): IMMEDIATE is an enum to store drawing mode.
    RETAINED(retained): RETAINED is an enum to store drawing mode.
    """

    IMMEDIATE = immediate = "IMMEDIATE"
    RETAINED = retained = "READIED"


MANAGER_ID = "manager"


class Orient(Enum):
    HORIZONTAL = H = "h"
    VERTICAL = V = "v"


# if sys.platform.startswith("darwin"):
#     PLATFORM = "macos"
# elif sys.platform == "win32":
#     PLATFORM = "windows"
