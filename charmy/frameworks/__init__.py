from os import environ

# from .ui import window_framework_map
# from .drawing import drawing_framework_map
# from .backend import backend_framework_map
# from ..const import Drawing, UI, Backends

import importlib


class Frameworks:
    backend_name = environ.get("CHARMY_BACKEND", "genesis")
    backend = importlib.import_module(f"charmy-backend-{backend_name}")
