"""Traverse the AST to provide information on desired nodes."""

import ast
import contextlib
import itertools
import os
import reprlib
from collections.abc import Sequence
from pathlib import Path
from textwrap import dedent

from .. import PYTHON_VERSION, ast_node_types_generator
from .display import print_header, print_section_divider, print_source_code


class NodeExplorer(ast.NodeVisitor):
    """
    Node visitor capable of interactively exploring nodes of the AST during traversal.

    Parameters
    ----------
    source_code_file_path : str | os.PathLike[str]
        Path to the Python source code to explore. The code must be valid Python syntax.
    nodes_to_explore : Sequence[str] | Sequence[ast.AST] | None
        The types of nodes to explore. When set to ``None``, the traversal will explore
        each node encountered. Provide a sequence of strings (*e.g.*, ``['Try', 'Assert']``)
        or :mod:`ast` types (*e.g.*, ``[ast.Try, ast.Assert]``) to only explore specific
        node types.
    interactive : bool, default=False
        Whether to explore the AST interactively, in which case the traversal will stop
        to show you information about the node and wait for you to decide the next step.
    """

    def __init__(
        self,
        source_code_file_path: str | os.PathLike[str],
        nodes_to_explore: Sequence[str] | Sequence[ast.AST] | None,
        interactive: bool = False,
    ) -> None:
        self._nodes_visited = itertools.count(1)

        file_path = Path(source_code_file_path).resolve()
        print(f'Reading Python source code from {file_path}...')

        try:
            self._source_code = file_path.read_text()
        except FileNotFoundError as exc:
            print(f'[ERROR] {exc.strerror}: {file_path}')
            raise

        print(f'Parsing into a Python {PYTHON_VERSION} AST...')
        try:
            self.tree = ast.parse(self._source_code)
        except SyntaxError:
            print('[ERROR] Input source code is not syntactically-correct')
            raise

        match nodes_to_explore:
            case None:
                self._nodes_to_explore = set(ast_node_types_generator())
            case [*items]:
                if all(isinstance(item, str) for item in items):
                    self._nodes_to_explore = {
                        node_type.removeprefix('ast.') for node_type in nodes_to_explore
                    }
                elif all(issubclass(item, ast.AST) for item in items):
                    self._nodes_to_explore = {
                        node_type.__name__ for node_type in nodes_to_explore
                    }
            case _:
                raise TypeError(
                    'nodes_to_explore must be a sequence of strings or AST classes, if not None'
                )

        self._interactive = interactive

    def _explore(self, node: ast.AST) -> None:
        """
        Explore an AST node.

        Parameters
        ----------
        node : ast.AST
            The node to explore.
        """
        node_name = node.__class__.__name__
        node_class = f'{node.__module__}.{node_name}'

        user_input = None
        should_explore = (node_name in self._nodes_to_explore) and (
            (
                user_input := input(
                    f'Currently at an {node_class} node. '
                    'Do you want to explore it? [y]es [n]o [q]uit '
                ).casefold()
            )
            in ['y', '']
            if self._interactive
            else True
        )

        if user_input == 'q':
            print('Quitting...')
            raise SystemExit(0)

        if should_explore:
            print(
                f'{next(self._nodes_visited)}. {node_class} '
                f'(https://docs.python.org/{PYTHON_VERSION}/library/ast.html#{node_class})'
            )

            if isinstance(node, ast.Module):
                print(
                    '\nModule docstring:', reprlib.repr(ast.get_docstring(node)), '\n'
                )

            with contextlib.suppress(AttributeError, TypeError):
                code_segment = dedent(
                    ast.get_source_segment(self._source_code, node, padded=True)
                )

                print('\nSource code represented by the node:')
                print_source_code(code_segment, node.lineno)

                print(
                    'Location in the source code:',
                    *[
                        f'- {key}: {getattr(node, key)}'
                        for key in [
                            'lineno',
                            'end_lineno',
                            'col_offset',
                            'end_col_offset',
                        ]
                    ],
                    sep='\n',
                    end='\n\n',
                )

            if node_specific_fields := [
                f'- {key}: {reprlib.repr(value)}'
                for key, value in ast.iter_fields(node)
            ]:
                print(
                    'AST node-specific fields and their values:',
                    *node_specific_fields,
                    sep='\n',
                )
                print_section_divider()

    def generic_visit(self, node: ast.AST) -> None:
        """
        Visit each node, with the option to explore before continuing the traversal.

        Parameters
        ----------
        node : ast.AST
            The AST node to visit.
        """
        self._explore(node)
        super().generic_visit(node)

    def run(self) -> None:
        """Traverse the AST from the root to the leaves."""
        print('Ready to explore the AST!')
        print_header('AST nodes encountered during depth-first traversal')
        self.visit(self.tree)
