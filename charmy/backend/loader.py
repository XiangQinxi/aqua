from __future__ import annotations as _
import typing

import importlib.metadata

if typing.TYPE_CHECKING:
    from .template import Backend


def list_backends_ep() -> list[importlib.metadata.EntryPoint]:
    """Lists all available backends extentions entry point."""
    return [entry_point for entry_point in \
            importlib.metadata.entry_points(group="charmy.backends")]

def load_backend(name: str) -> Backend:
    if name == "genesis":
        import genesis
        return genesis.Backend
    else:
        raise NotImplementedError("Other backends not supported yet in early dev.")