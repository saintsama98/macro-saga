import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from minimacro import pass1, pass2
from minimacro.errors import ErrorReporter
from minimacro.tables import Tables


def run_full(src: str):
    tables = Tables()
    errors = ErrorReporter()
    pass1.run(src.splitlines(), tables, errors)
    expanded = pass2.run(tables, errors)
    return tables, errors, expanded


class TestPass1(unittest.TestCase):
    def test_simple_definition(self):
        src = "MACRO\nINCR &X, &Y\nADD &X, &Y\nMEND\nSTART\nEND\n"
        tables, errors, _ = run_full(src)
        self.assertEqual(len(tables.mnt), 1)
        self.assertEqual(tables.mnt[0].name, "INCR")
        self.assertEqual(tables.mnt[0].num_pp, 2)
        self.assertEqual(tables.mnt[0].num_kp, 0)
        self.assertEqual([e.text for e in tables.mdt], ["ADD #1, #2", "MEND"])
        self.assertFalse(errors.has_errors())

    def test_keyword_param_with_default(self):
        src = "MACRO\nOP &X, &KW=ADD\n&KW &X\nMEND\n"
        tables, errors, _ = run_full(src)
        self.assertEqual(tables.mnt[0].num_pp, 1)
        self.assertEqual(tables.mnt[0].num_kp, 1)
        self.assertEqual(tables.kpdtab[0].name, "KW")
        self.assertEqual(tables.kpdtab[0].default, "ADD")
        self.assertFalse(errors.has_errors())

    def test_unterminated_macro(self):
        src = "MACRO\nFOO &X\nADD &X\n"
        _, errors, _ = run_full(src)
        self.assertTrue(any("not terminated" in e for e in errors.errors))

    def test_comment_and_blank_lines_ignored(self):
        src = "; header\n\nMACRO\nFOO &X\nADD &X\nMEND\n"
        tables, errors, _ = run_full(src)
        self.assertEqual(len(tables.mnt), 1)
        self.assertFalse(errors.has_errors())


class TestPass2(unittest.TestCase):
    def test_positional_expansion(self):
        src = "MACRO\nINCR &X, &Y\nADD &X, &Y\nMEND\nINCR P, Q\n"
        _, errors, expanded = run_full(src)
        self.assertEqual(expanded, ["ADD P, Q"])
        self.assertFalse(errors.has_errors())

    def test_keyword_default_used_when_omitted(self):
        src = "MACRO\nOP &X, &KW=ADD\n&KW &X\nMEND\nOP P\n"
        _, errors, expanded = run_full(src)
        self.assertEqual(expanded, ["ADD P"])
        self.assertFalse(errors.has_errors())

    def test_keyword_override(self):
        src = "MACRO\nOP &X, &KW=ADD\n&KW &X\nMEND\nOP P, KW=SUB\n"
        _, errors, expanded = run_full(src)
        self.assertEqual(expanded, ["SUB P"])

    def test_wrong_positional_count_reports_error(self):
        src = "MACRO\nINCR &X, &Y\nADD &X, &Y\nMEND\nINCR P\n"
        _, errors, expanded = run_full(src)
        self.assertEqual(expanded, [])
        self.assertTrue(any("expected 2 positional" in e for e in errors.errors))

    def test_unknown_keyword_warns_but_continues(self):
        src = "MACRO\nOP &X, &KW=ADD\n&KW &X\nMEND\nOP P, BAD=ZZZ\n"
        _, errors, expanded = run_full(src)
        self.assertEqual(expanded, ["ADD P"])
        self.assertTrue(any("unknown keyword" in e for e in errors.errors))

    def test_non_macro_lines_pass_through(self):
        src = "MACRO\nINCR &X\nADD &X\nMEND\nSTART\nINCR P\nEND\n"
        _, _, expanded = run_full(src)
        self.assertEqual(expanded, ["START", "ADD P", "END"])


if __name__ == "__main__":
    unittest.main()
