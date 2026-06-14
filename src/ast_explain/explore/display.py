"""Display utilities."""

import ast
import itertools
import math
import shutil

TERMINAL_WIDTH, TERMINAL_HEIGHT = shutil.get_terminal_size()


def print_header(title: str) -> None:
    """
    Print a header section with the title centered.

    Parameters
    ----------
    title : str
        The title of the section.
    """
    symbol = '='
    line = symbol * TERMINAL_WIDTH
    title_line = f'{title:^{TERMINAL_WIDTH}}'

    if len(title) < TERMINAL_WIDTH - 6:
        border = symbol * 2
        title_line = border + title_line[2:-2] + border

    print(line, title_line, line, sep='\n', end='\n\n')


def print_section_divider() -> None:
    """Print section divider."""
    print(f'\n{"*" * TERMINAL_WIDTH}\n')


def print_source_code(
    source_code: str, node: ast.AST, max_lines: int | None = None
) -> None:
    """
    Print a source code segment with line numbers.

    Parameters
    ----------
    source_code : str
        The source code.
    node : ast.AST
        The AST node.
    max_lines : int | None, optional
        The maximum number of lines to show. By default, show as many lines as can fit
        in the terminal window.
    """
    code_lines = source_code.splitlines()

    start_line_number = node.lineno
    highlight_line_number = None

    arrow = ''
    underline = None
    if node.lineno == node.end_lineno:
        highlight_line_number = node.lineno
        start_line_number = max(1, start_line_number - 2)

        code_segment = list(
            itertools.dropwhile(
                lambda line: not line,
                code_lines[start_line_number - 1 : highlight_line_number],
            )
        )

        if (width := node.end_col_offset - node.col_offset) < len(code_segment[-1]):
            underline = '^' * width
    else:
        code_segment = (
            ast.get_source_segment(source_code, node, padded=True)
        ).splitlines()

    if (num_lines := len(code_segment)) > 1 and (
        num_lines > (node.end_lineno - node.lineno + 1)
    ):
        arrow = '-> '

    end_line_number = num_lines + start_line_number

    digits = math.ceil(math.log10(end_line_number))
    if arrow:
        digits += len(arrow)

    padding = digits + 1
    separator = ' | '

    print('\nSource code represented by the node:')
    print(
        *(
            [
                f'{f"{arrow}{line_number}" if node.lineno <= line_number <= node.end_lineno else line_number:>{padding}}{separator}{code}'
                for line_number, code in zip(
                    range(start_line_number, end_line_number),
                    code_segment[: max_lines or TERMINAL_HEIGHT],
                    strict=False,
                )
            ]
        ),
        sep='\n',
        end='\n',
    )

    if underline:
        print(f'{" ":>{(padding + len(separator)) + node.col_offset}}{underline}')
    print()
