from typing import List

from .errors import ErrorReporter
from .tables import Tables


def print_tables(tables: Tables) -> None:
    print("=== MNT (Macro Name Table) ===")
    print(f"{'#':<3} {'NAME':<12} {'#PP':>4} {'#KP':>4} {'MDT#':>5} {'KPDT#':>6} {'ALA#':>5}")
    for i, m in enumerate(tables.mnt):
        print(f"{i:<3} {m.name:<12} {m.num_pp:>4} {m.num_kp:>4} {m.mdt_ptr:>5} {m.kpdt_ptr:>6} {m.ala_ptr:>5}")

    print("\n=== MDT (Macro Definition Table) ===")
    for i, e in enumerate(tables.mdt):
        print(f"{i:>3}  {e.text}")

    print("\n=== KPDTAB (Keyword Param Default Table) ===")
    print(f"{'#':<3} {'NAME':<12} DEFAULT")
    if not tables.kpdtab:
        print("    (empty)")
    for i, k in enumerate(tables.kpdtab):
        print(f"{i:<3} {k.name:<12} {k.default}")

    print("\n=== ALA (Argument List Array) ===")
    print(f"{'#':<3} {'FORMAL':<12} ACTUAL")
    for i, a in enumerate(tables.ala):
        print(f"{i:<3} {a.formal:<12} {a.actual}")

    print("\n=== INTERMEDIATE CODE (Pass 1 output) ===")
    for s in tables.intermediate:
        print(s)


def print_expanded(expanded: List[str]) -> None:
    print("\n=== EXPANDED CODE (Pass 2 output) ===")
    for line in expanded:
        print(line)


def print_errors(errors: ErrorReporter) -> None:
    if not errors.has_errors():
        print("\n=== ERRORS ===\n  (none)")
        return
    print("\n=== ERRORS ===")
    for e in errors.errors:
        print(f"  - {e}")
