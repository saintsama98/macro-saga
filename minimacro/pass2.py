from typing import Dict, List, Tuple

from .errors import ErrorReporter
from .tables import Tables


def run(tables: Tables, errors: ErrorReporter) -> List[str]:
    """Walk intermediate code; for each macro call, substitute actuals into MDT body and emit expanded lines."""
    expanded: List[str] = []
    for line in tables.intermediate:
        head, _, rest = line.partition(" ")
        op = head.strip()
        macro = tables.find_macro(op)
        if macro is None:
            expanded.append(line)
            continue

        pos_actuals, kw_actuals = _parse_actuals(rest.strip())

        if len(pos_actuals) != macro.num_pp:
            errors.add(
                f"Call to {op}: expected {macro.num_pp} positional arg(s), "
                f"got {len(pos_actuals)} -- call skipped"
            )
            continue

        known_kw = {tables.kpdtab[macro.kpdt_ptr + j].name for j in range(macro.num_kp)}
        for k in kw_actuals:
            if k not in known_kw:
                errors.add(f"Call to {op}: unknown keyword '{k}' (ignored)")

        total = macro.num_pp + macro.num_kp
        resolved: List[str] = [""] * (total + 1)
        for j in range(macro.num_pp):
            resolved[j + 1] = pos_actuals[j]
        for j in range(macro.num_kp):
            kp = tables.kpdtab[macro.kpdt_ptr + j]
            resolved[macro.num_pp + j + 1] = kw_actuals.get(kp.name, kp.default)

        p = macro.mdt_ptr
        while p < len(tables.mdt) and tables.mdt[p].text.upper() != "MEND":
            body = tables.mdt[p].text
            for k in range(total, 0, -1):  # high-to-low so #10 is replaced before #1
                body = body.replace("#" + str(k), resolved[k])
            expanded.append(body)
            p += 1
    return expanded


def _parse_actuals(arg_str: str) -> Tuple[List[str], Dict[str, str]]:
    positionals: List[str] = []
    keywords: Dict[str, str] = {}
    if not arg_str:
        return positionals, keywords
    for raw in arg_str.split(","):
        a = raw.strip()
        if not a:
            continue
        if "=" in a:
            k, v = a.split("=", 1)
            keywords[k.strip()] = v.strip()
        else:
            positionals.append(a)
    return positionals, keywords
