from typing import List, Tuple

from .errors import ErrorReporter
from .tables import ALAEntry, KPDTabEntry, MDTEntry, MNTEntry, Tables


def run(source: List[str], tables: Tables, errors: ErrorReporter) -> None:
    """Scan source, register macro definitions in tables, emit non-definition lines as intermediate code."""
    i = 0
    while i < len(source):
        line = _strip_comment(source[i]).strip()
        if not line:
            i += 1
            continue

        if line.upper() == "MACRO":
            i += 1
            if i >= len(source):
                errors.add("MACRO directive at end of file with no prototype")
                return
            formals = _process_definition(source[i].strip(), tables, errors)
            macro_name = tables.mnt[-1].name
            i += 1

            while i < len(source) and _strip_comment(source[i]).strip().upper() != "MEND":
                body = _strip_comment(source[i]).strip()
                if body:
                    tables.mdt.append(MDTEntry(text=_rewrite_body(body, formals)))
                i += 1

            if i >= len(source):
                errors.add(f"Macro {macro_name} not terminated by MEND")
                return
            tables.mdt.append(MDTEntry(text="MEND"))
            i += 1
        else:
            tables.intermediate.append(line)
            i += 1


def _process_definition(proto: str, tables: Tables, errors: ErrorReporter) -> List[str]:
    """Parse 'NAME &X, &Y, &KW=DEFAULT', register MNT/KPDTAB/ALA, return formals in declaration order."""
    if " " in proto.strip():
        name, param_str = proto.split(None, 1)
    else:
        name, param_str = proto.strip(), ""

    if tables.find_macro(name) is not None:
        errors.add(f"Macro {name} redefined; second definition still recorded")

    positionals, keywords = _parse_params(param_str)

    entry = MNTEntry(
        name=name,
        num_pp=len(positionals),
        num_kp=len(keywords),
        mdt_ptr=len(tables.mdt),
        kpdt_ptr=len(tables.kpdtab),
        ala_ptr=len(tables.ala),
    )

    formal_order: List[str] = []
    for p in positionals:
        tables.ala.append(ALAEntry(formal="&" + p, actual="-"))
        formal_order.append(p)
    for kname, default in keywords:
        tables.kpdtab.append(KPDTabEntry(name=kname, default=default))
        tables.ala.append(ALAEntry(formal="&" + kname, actual=default))
        formal_order.append(kname)

    tables.mnt.append(entry)
    return formal_order


def _parse_params(param_str: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    positionals: List[str] = []
    keywords: List[Tuple[str, str]] = []
    if not param_str.strip():
        return positionals, keywords
    for raw in param_str.split(","):
        p = raw.strip()
        if p.startswith("&"):
            p = p[1:]
        if not p:
            continue
        if "=" in p:
            n, d = p.split("=", 1)
            keywords.append((n.strip(), d.strip()))
        else:
            positionals.append(p)
    return positionals, keywords


def _rewrite_body(body: str, formals: List[str]) -> str:
    # Longest-first prevents prefix collisions (&AB before &A)
    result = body
    for f in sorted(formals, key=len, reverse=True):
        idx = formals.index(f) + 1
        result = result.replace("&" + f, "#" + str(idx))
    return result


def _strip_comment(line: str) -> str:
    semi = line.find(";")
    return line if semi < 0 else line[:semi]
