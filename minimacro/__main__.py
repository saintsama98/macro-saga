import sys
from typing import List

from . import pass1, pass2, printer
from .errors import ErrorReporter
from .tables import Tables


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("usage: python -m minimacro <input.mac>", file=sys.stderr)
        return 1

    with open(argv[1]) as f:
        source = f.read().splitlines()

    tables = Tables()
    errors = ErrorReporter()

    pass1.run(source, tables, errors)
    printer.print_tables(tables)
    expanded = pass2.run(tables, errors)
    printer.print_expanded(expanded)
    printer.print_errors(errors)

    return 0 if not errors.has_errors() else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
