"""Traverse the AST to provide information on desired nodes."""

import ast
import contextlib
import itertools
import os
import reprlib
import time
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from .. import PYTHON_VERSION, ast_node_types_generator
from .display import print_header, print_section_divider, print_source_code


class NodeExplorer(ast.NodeVisitor):
    """
    Node visitor capable of interactively exploring nodes of the AST during traversal.

    Parameters
    ----------
    source_code_file_path : str | os.PathLike[str]
        Path to the Python source code to explore. The code must be valid Python syntax.
    nodes_to_explore : Sequence[str] | Sequence[type[ast.AST]] | None
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
        nodes_to_explore: Sequence[str] | Sequence[type[ast.AST]] | None,
        interactive: bool = False,
    ) -> None:
        self._nodes_visited = itertools.count(1)

        file_path = Path(source_code_file_path).resolve()
        print(f'📖 Reading Python source code from {file_path}...')

        try:
            self._source_code = file_path.read_text()
        except FileNotFoundError as exc:
            print(f'⚠️  {exc.strerror}')
            raise

        print(f'🔍 Parsing into a Python {PYTHON_VERSION} AST...')
        try:
            self.tree = ast.parse(self._source_code)
        except SyntaxError:
            print('⚠️  Input source code is not syntactically-correct')
            raise

        match nodes_to_explore:
            case None:
                self._nodes_to_explore = set(ast_node_types_generator())
            case [str(), *other_node_types] if all(
                isinstance(node_type, str) for node_type in other_node_types
            ):
                self._nodes_to_explore = {
                    node_type.removeprefix('ast.') for node_type in nodes_to_explore
                }
            case [type(), *other_node_types] if all(
                issubclass(node_type, ast.AST) for node_type in other_node_types
            ):
                self._nodes_to_explore = {
                    cast('str', node_type.__name__) for node_type in nodes_to_explore
                }
            case _:
                raise TypeError(
                    'nodes_to_explore must be a sequence of strings or AST classes, if not None'
                )

        self._interactive = interactive

    def _prompt_user(self, prompt: str) -> bool:
        """
        Prompt user (when in interactive mode) or return ``True``.

        Parameters
        ----------
        prompt : str
            The prompt. Supported options will be appended automatically.

        Returns
        -------
        bool
            Whether the user wants to explore further.

        Raises
        ------
        SystemExit
            This is raised when the user requests to quit.
        """
        if self._interactive:
            user_input = (
                input(f'❓ {prompt} [y]es [n]o [q]uit: ').casefold().strip()[:1]
            )

            match user_input:
                case 'q':
                    print('🛑 Quitting...')
                    raise SystemExit(0)
                case 'n':
                    return False
                case 'y' | '':
                    print()
                    return True
                case _:
                    print(f'🫤  Invalid response "{user_input}"')
                    time.sleep(1)
                    return self._prompt_user(prompt)

        return True

    def _show_source_code(self, node: ast.AST) -> None:
        """
        Show the source code for a given node (if applicable).

        Parameters
        ----------
        node : ast.AST
            The node to explore.
        """
        try:
            print_source_code(self._source_code, node)

            if self._prompt_user('Show location fields?'):
                location_fields = [
                    'lineno',
                    'end_lineno',
                    'col_offset',
                    'end_col_offset',
                ]
                gap = max(len(field) for field in location_fields)
                print(
                    '📍 Location in the source code:',
                    *[
                        f'   - {key:<{gap + 1}}: {getattr(node, key)}'
                        for key in location_fields
                    ],
                    sep='\n',
                    end='\n\n',
                )
        except (AttributeError, TypeError):
            print('📍 This node type does not have any line number information.\n')

    def _show_node_specific_fields(self, node: ast.AST) -> None:
        """
        Show node-specific fields and their values.

        Parameters
        ----------
        node : ast.AST
            The node to explore.
        """
        if self._prompt_user('Do you want more information on this node?'):
            match node:
                case ast.Load() | ast.Store() | ast.Del():
                    print(
                        '💡 This node specifies the context in which a variable',
                        '(ast.Name) is used.',
                    )
                case ast.Module():
                    print('📝', end=' ')
                    if docstring := ast.get_docstring(node):
                        print(f'Module docstring: {reprlib.repr(docstring)}')
                    else:
                        print('Docstring is missing.')
                    print()
                case _:
                    with contextlib.suppress(TypeError):
                        if not ast.get_docstring(node):  # type: ignore[arg-type]
                            print('📝 Docstring is missing.\n')

            if node_specific_fields := [
                (key, reprlib.repr(value)) for key, value in ast.iter_fields(node)
            ]:
                gap = max(len(key) for key, _ in node_specific_fields)
                print(
                    '✨ AST node-specific fields and their values:',
                    *[
                        f'   - {key:<{gap + 1}}: {value}'
                        for key, value in node_specific_fields
                    ],
                    sep='\n',
                )

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

        if node_name in self._nodes_to_explore:
            list_item = (
                f'{next(self._nodes_visited)}. {node_name} '
                f'(https://docs.python.org/{PYTHON_VERSION}/library/ast.html#{node_class})'
            )
            print(list_item, '-' * len(list_item), sep='\n')

            self._show_source_code(node)
            self._show_node_specific_fields(node)
            print_section_divider()

            if not self._prompt_user('Continue traversal?'):
                print('🛑 Stopping traversal...')
                raise SystemExit(0)

            if self._interactive:
                print(f'🚀 Leaving {node_class} node...')
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
        print('✅ Ready to explore the AST!\n')
        print_header('AST nodes encountered during depth-first traversal')
        self.visit(self.tree)
        print('🏆 Traversal completed!')
