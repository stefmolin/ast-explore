"""Display utilities."""

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

    print(line, title_line, line, sep='\n')


def print_section_divider() -> None:
    """Print section divider."""
    print(f'\n{"-" * TERMINAL_WIDTH}\n')


def print_source_code(
    code_segment: str, start_line_number: int = 1, max_lines: int | None = None
) -> None:
    """
    Print a source code segment with line numbers.

    Parameters
    ----------
    code_segment : str
        The source code.
    start_line_number : int, default=1
        The starting line number.
    max_lines : int | None, optional
        The maximum number of lines to show. By default, show as many lines as can fit
        in the terminal window.
    """
    code_lines = code_segment.splitlines()
    end_line_number = len(code_lines) + start_line_number

    digits = math.ceil(math.log10(end_line_number))
    print(
        '\n'.join(
            [
                f'{line_number:>{digits + 1}} | {code}'
                for line_number, code in zip(
                    range(
                        start_line_number,
                        end_line_number,
                    ),
                    code_lines[: max_lines or TERMINAL_HEIGHT],
                    strict=False,
                )
            ]
        ),
        end='\n\n',
    )
