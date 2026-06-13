"""Traverse the AST to provide information on desired nodes."""

import ast
import os
from pathlib import Path


class NodeExplorer(ast.NodeVisitor):
    """
    Node visitor capable of interactively exploring nodes of the AST during traversal.

    Parameters
    ----------
    source_code_file_path : str | os.PathLike[str]
        Path to the Python source code to explore. The code must be valid Python syntax.
    """

    def __init__(
        self,
        source_code_file_path: str | os.PathLike[str],
    ) -> None:
        file_path = Path(source_code_file_path).resolve()
        print(f'Processing {file_path}:')

        self._source_code = file_path.read_text()
        self.tree = ast.parse(self._source_code)

    def _explore(self, node: ast.AST) -> None:
        """
        Explore an AST node.

        Parameters
        ----------
        node : ast.AST
            The node to explore.
        """
        node_name = node.__class__.__name__
        node_class = f'ast.{node_name}'

        print(
            f'Encountered {node_class} '
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
        self.visit(self.tree)
