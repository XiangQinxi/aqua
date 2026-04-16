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
        from . import genesis
        return genesis.Backend
    else:
        raise NotImplementedError("Other backends not supported yet in early dev.")


if __name__ == "__main__":
    print("This is for development testing only.")
    print("Trying to load backend Genesis...")
    # try: # This section will always fail due to attempting relative import without parent package
    #     backend = load_backend("genesis")
    #     print(f"===> Loaded backend with name: {backend.friendly_name}")
    # except Exception as e:
    #     print(e)
    #     print("===> Failed")