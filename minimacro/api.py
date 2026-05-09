from typing import Any, Dict

from . import pass1, pass2
from .errors import ErrorReporter
from .tables import Tables


def process(source: str) -> Dict[str, Any]:
    """Run both passes and return a JSON-serializable view of all outputs."""
    tables = Tables()
    errors = ErrorReporter()
    pass1.run(source.splitlines(), tables, errors)
    expanded = pass2.run(tables, errors)
    return {
        "mnt": [
            {
                "name": m.name,
                "num_pp": m.num_pp,
                "num_kp": m.num_kp,
                "mdt_ptr": m.mdt_ptr,
                "kpdt_ptr": m.kpdt_ptr,
                "ala_ptr": m.ala_ptr,
            }
            for m in tables.mnt
        ],
        "mdt": [{"text": e.text} for e in tables.mdt],
        "kpdtab": [{"name": k.name, "default": k.default} for k in tables.kpdtab],
        "ala": [{"formal": a.formal, "actual": a.actual} for a in tables.ala],
        "intermediate": list(tables.intermediate),
        "expanded": expanded,
        "errors": list(errors.errors),
    }
