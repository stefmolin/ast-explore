"""CLI for exploring an AST of Python source code."""

import argparse
import difflib
from collections.abc import Sequence
from typing import cast

from .. import __version__, ast_node_types_generator
from .explorer import NodeExplorer


def validate_node_type(node_type: str) -> str:
    """
    Validate node type is an AST node.

    Parameters
    ----------
    node_type : str
        The node type to validate.

    Returns
    -------
    str
        The node type, if it is valid.

    Raises
    ------
    argparse.ArgumentTypeError
        This is raised when the node type is not valid, and an attempt will be made to
        suggest a close match for a valid node type (if one exists).
    """
    if (
        not node_type
        or (node_name := node_type.removeprefix('ast.')) in ast_node_types_generator()
    ):
        return node_type

    msg = f'Unknown AST node type "{node_name}".'
    if did_you_mean := difflib.get_close_matches(
        node_name, ast_node_types_generator(), n=1
    ):
        msg += f' Did you mean "{did_you_mean[0]}"?'
    raise argparse.ArgumentTypeError(msg)


def get_parser() -> argparse.ArgumentParser:
    """
    Get an argument parser for the AST explorer CLI.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description='Traverse the AST of the input source code and explain the nodes encountered',
    )

    parser.add_argument(
        '-v', '--version', action='version', version=f'%(prog)s {__version__}'
    )

    parser.add_argument(
        metavar='source_code',
        dest='source_code_file_path',
        help='Source code file to analyze',
    )

    parser.add_argument(
        '--types',
        nargs='*',
        help=(
            'node types to explain (e.g., --types Try ExceptionHandler). '
            "If you don't provide any specific types, all will be explained."
        ),
        type=validate_node_type,
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help=(
            'whether to run in interactive mode, which allows the user to decide '
            'whether they want to visit a given node.'
        ),
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    Explore the AST of a given Python source code module.

    Parameters
    ----------
    argv : Sequence[str] | None, optional
        The arguments passed on the command line.

    Returns
    -------
    int
        Exit code for the process. Non-zero exit codes mean something went wrong.
    """
    args = get_parser().parse_args(argv)

    try:
        NodeExplorer(args.source_code_file_path, args.types, args.interactive).run()
    except KeyboardInterrupt:
        return 0
    except SystemExit as exit:
        return cast('int', exit.code)
    except (FileNotFoundError, SyntaxError):
        return 1
    except Exception as exc:
        print(exc)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
