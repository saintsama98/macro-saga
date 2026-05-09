MiniMacro is a two-pass macroprocessor for a small assembly-style language, built for the SPCC lab. Pass 1 scans the source, registers
macro definitions, and produces the four classical tables (MNT, MDT, KPDTAB, ALA) plus intermediate code. Pass 2 walks the intermediate
stream, resolves positional and keyword arguments against the tables, and emits the expanded code along with any diagnostics.

The engine is a modular Python package with no third-party runtime dependencies, paired with a Flask web UI for live editing,
processing, and table inspection. Run python -m minimacro samples/sample.mac for the CLI, or python web/app.py to launch the browser
Stage 1 (MACRO/MEND with positional + keyword args and full error reporting) is shipped- LCL, AIF, and AGO
are reserved for Stage 2.
