import typing

from ..rect import Rect
from .container import Container
from .. import const

if typing.TYPE_CHECKING:
    from ..cmm import CharmyManager

class Window(Container):
    """Window class."""

    def __init__(self, 
                 parent: CharmyManager | None = None, 
                 size: tuple[int | float, int | float] = (540, 480), 
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store parent maanger
        if parent != None: # Parent manager already specified
            self.parent = parent
        else:
            if not const.Configs.single_manager_mode:
                raise RuntimeError(
                    "No manager specified for window, while single manager mode is off. "
                    )
            self.parent = const.Common.managers_instances[0]
        # Handle size
        self.size = size
        if type(self.size[0]) is float or type(self.size[1]) is float:
            self.size = (int(self.size[0]), int(self.size[1]))
        # Initialize the WindowBase
        self.backend_base = self.parent.backend.class_WindowBase()
        self.show()
    
    def show(self):
        self.backend_base.show()