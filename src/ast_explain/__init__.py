"""Tools for explaining the AST of given Python source code."""

import ast
import importlib.metadata
import sys
from collections.abc import Iterator

__version__ = importlib.metadata.version(__name__)


PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}'


def ast_node_types_generator() -> Iterator[str]:
    """
    Generator for getting the names of all the AST node types.

    Yields
    ------
    Iterator[str]
        Names of each of the AST node types.
    """
    seen = set()

    def subclass_generator(base_class: type) -> Iterator[str]:
        """
        Generator for getting the names of all of a class's subclasses recursively.

        Parameters
        ----------
        base_class : type
            The class for which to grab all subclasses.

        Yields
        ------
        Iterator[str]
            Names of each subclass, regardless of how many levels deep.
        """
        for subclass in base_class.__subclasses__():
            if subclass not in seen:
                seen.add(subclass)
                yield subclass.__name__
                yield from subclass_generator(subclass)

    yield from subclass_generator(ast.AST)


__all__ = ['PYTHON_VERSION', '__version__', 'ast_node_types_generator']
