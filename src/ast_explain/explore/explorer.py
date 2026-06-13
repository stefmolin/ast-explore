"""Traverse the AST to provide information on desired nodes."""

import ast
import itertools
import os
from collections.abc import Sequence
from pathlib import Path


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
    interactive : bool, default ``False``
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
        print(f'Processing {file_path}:')

        self._source_code = file_path.read_text()
        self.tree = ast.parse(self._source_code)

        self._nodes_to_explore = nodes_to_explore
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
        should_explore = (
            self._nodes_to_explore is None
            or node_name in self._nodes_to_explore
            or node_class in self._nodes_to_explore
        ) and (
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
                f'(https://docs.python.org/3/library/ast.html#{node_class})'
            )

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
        print(f'\nAST nodes encountered during depth-first traversal\n{"-" * 64}\n')
        self.visit(self.tree)
