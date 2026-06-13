"""CLI for exploring an AST of Python source code."""

import argparse
from collections.abc import Sequence

from .. import __version__
from .explorer import NodeExplorer


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
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """
    Explore the AST of a given Python source code module.

    Parameters
    ----------
    argv : Sequence[str] | None, optional
        The arguments passed on the command line.
    """
    args = get_parser().parse_args(argv)

    visitor = NodeExplorer(args.source_code_file_path, args.types)
    visitor.run()


if __name__ == '__main__':
    raise SystemExit(main())
