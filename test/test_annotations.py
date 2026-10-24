import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from lsprotocol.types import (
    CompletionParams, DefinitionParams, HoverParams, Position,
    SignatureHelpParams, TextDocumentIdentifier,
)
from pygls.workspace import TextDocument

from fleurdelys.analysis import analyze, command_overloads
from fleurdelys.linting import lint_cmake
from fleurdelys.server import completions, definition, hover, signature_help
from fleurdelys.signatures import SignatureMatcher, SignatureParser
from fleurdelys.syntax import in_comment


class GrammarTests(unittest.TestCase):
    def matcher(self, signature):
        return SignatureMatcher(SignatureParser(signature).parse())

    def test_literals_and_choices(self):
        matcher = self.matcher("FEXPR <?expression> [PRECISION < DEFAULT | FULL >]")
        for args in (["FEXPR", "1+2"], ["FEXPR", "1+2", "PRECISION", "FULL"]):
            self.assertTrue(matcher.match(args).success)
        for args in (["fexpr", "1+2"], ["FEXPR", "1+2", "PRECISION"], ["FEXPR", "1+2", "FULL"]):
            self.assertFalse(matcher.match(args).success)
        self.assertEqual(matcher.get_completions(["FEXPR", "x"]), ["PRECISION"])
        self.assertEqual(matcher.get_completions(["FEXPR", "x", "PRECISION"]), ["DEFAULT", "FULL"])

    def test_groups_and_repetition(self):
        matcher = self.matcher("[FOO [BAR]] [ FOO | BAR ]")
        for args in ([], ["FOO"], ["FOO", "BAR"], ["FOO", "BAR", "BAR"]):
            self.assertTrue(matcher.match(args).success)
        self.assertEqual(self.matcher("< FOO >").match(["FOO"]).success, self.matcher("FOO").match(["FOO"]).success)
        self.assertFalse(self.matcher("<?item>...").match([]).success)
        self.assertTrue(self.matcher("[?item]...").match([]).success)
        self.assertTrue(self.matcher("[?item]... END").match(["a", "b", "END"]).success)
        self.assertEqual(self.matcher("[FOO BAR]...").get_completions(["FOO"]), ["BAR"])

    def test_backtracking_and_ambiguous_effects(self):
        matcher = self.matcher("[&output] [?input]")
        self.assertEqual(matcher.match(["X"]).definitions, set())
        self.assertEqual(matcher.match(["X", "Y"]).definitions, {0})
        self.assertEqual(self.matcher("[?arg]... END").get_completions(["a"]), ["END"])

    def test_dynamic_and_quoted_arguments(self):
        matcher = self.matcher("FOO <&output>")
        self.assertTrue(matcher.match(["${mode}", "X"]).success)
        self.assertTrue(matcher.match(['"FOO"', "X"]).success)
        for arg in ('"X"', "${X}", "prefix_${X}", "[[X]]", "123", "foo/bar"):
            result = matcher.match(["FOO", arg])
            self.assertTrue(result.success)
            self.assertFalse(result.definitions)
        self.assertEqual(matcher.get_completions(["FOO"], ["EXISTING"]), ["EXISTING"])
        self.assertFalse(matcher.match(["[[${mode}]]", "X"]).success)
        self.assertFalse(matcher.match([r"\${mode}", "X"]).success)

    def test_malformed(self):
        for signature in ("<>", "[]", "[FOO", "<FOO]", "FOO |", "<FOO | ?arg>", "FOO...", "[[FOO]]...", "<?>"):
            with self.subTest(signature=signature), self.assertRaises(ValueError):
                self.matcher(signature)


class AnalysisTests(unittest.TestCase):
    def test_markdown_and_overloads(self):
        source = """## # First overload
##
##     indented code
## function(Mixed FOO <?input>)
## Second overload.
## function(mixed BAR)
function(MIXED A1 A2)
  message("${A1} ${A2} ${ARGC}")
endfunction()
"""
        result = analyze(source)
        d = result.commands["mixed"]
        self.assertEqual(d.name, "Mixed")
        self.assertEqual(d.signatures, ["FOO <?input>", "BAR"])
        self.assertEqual(d.overloads[0].description, "# First overload\n\n    indented code")
        self.assertEqual(d.line, 6)
        self.assertNotIn("A1", result.definitions)
        self.assertFalse(result.issues)
        inside = analyze(source, position_line=7)
        self.assertTrue({"A1", "A2", "ARGC", "ARGV", "ARGN"} <= inside.definitions.keys())

    def test_boundaries_and_ignored_comments(self):
        source = """## Kept description.
### function(wrong FOO)
## function(right BAR)
## Detached description.

set(UNRELATED 1)
#[[
## function(hidden FOO)
]]
set(TEXT "## function(also_hidden FOO)")
"""
        result = analyze(source)
        self.assertEqual(set(result.commands), {"right"})
        self.assertEqual(result.commands["right"].description, "Kept description.")
        self.assertIsNone(result.definitions["UNRELATED"].description)
        source = '#"unterminated quote in a line comment\n## function(visible FOO)\n'
        self.assertIn("visible", analyze(source).commands)
        self.assertFalse(in_comment("#[[]]f(FOO)", 5))

    def test_documented_variables(self):
        result = analyze("## **Flag**.\n##\n## set(FLAG 1)\n## Actual value.\nset(LOCAL 2)\n")
        self.assertEqual(result.definitions["FLAG"].description, "**Flag**.\n")
        self.assertEqual(result.definitions["LOCAL"].description, "Actual value.")
        ordinary = analyze("## Ordinary comment.\nfunction(plain ARG)\nendfunction()\n")
        self.assertIsNone(ordinary.commands["plain"].description)

    def test_effects_specificity_and_scope(self):
        source = """## function(assign <&var> [?value])
## function(assign <?var> <?value> PARENT_SCOPE)
assign(GLOBAL 1)
function(test ARG)
  assign(LOCAL 2)
  assign(PARENT 2 PARENT_SCOPE)
  message(${LOCAL})
endfunction()
assign("QUOTED" 1)
assign(prefix_${dynamic} 1)
"""
        result = analyze(source)
        self.assertIn("GLOBAL", result.definitions)
        self.assertNotIn("LOCAL", result.definitions)
        self.assertNotIn("PARENT", result.definitions)
        self.assertNotIn("QUOTED", result.definitions)
        self.assertFalse(any("'LOCAL'" in i.message for i in result.issues))
        source = "## function(f <&var>)\n## function(f <?var>)\nf(X)\n"
        self.assertNotIn("X", analyze(source).definitions)
        source = "## function(f <&var>)\n## function(f LITERAL)\nf(LITERAL)\n"
        self.assertNotIn("LITERAL", analyze(source).definitions)

    def test_existing_definition_and_shadowing(self):
        source = """## function(create <&var>)
## Original.
set(X 1)
create(X)
function(test)
create(X)
"""
        global_result = analyze(source, position_line=4)
        self.assertEqual(global_result.definitions["X"].description, "Original.")
        self.assertEqual(global_result.definitions["X"].line, 2)
        local_result = analyze(source)
        self.assertEqual(local_result.definitions["X"].line, 5)

    def test_inferred_signature_and_macro_arguments(self):
        result = analyze("function(plain ARG)\nendfunction()\nplain(X)\nmacro(m A)\nmessage(${A})\nendmacro()\n")
        self.assertEqual(result.commands["plain"].overloads[0].signature, "<?ARG>")
        self.assertNotIn("A", result.definitions)
        self.assertFalse(result.issues)

    def test_annotation_after_implementation_keeps_implementation_location(self):
        source = "function(foo A)\nendfunction()\n## function(Foo BAR)\n"
        d = analyze(source).commands["foo"]
        self.assertEqual(d.name, "Foo")
        self.assertEqual(d.line, 0)
        self.assertEqual(d.signatures, ["BAR"])

    def test_parent_scope_and_macro_restoration(self):
        source = "set(X 1)\nfunction(f)\nset(PARENT 2 PARENT_SCOPE)\nendfunction()\nmacro(m X)\nset(LEAKED 1)\nendmacro()\n"
        result = analyze(source)
        self.assertTrue({"X", "PARENT", "LEAKED"} <= result.definitions.keys())
        self.assertEqual(result.definitions["X"].line, 0)

    def test_multiline_quoted_and_bracket_syntax(self):
        source = '''## function(f <?input> <&output>)
f(
  "text ) # not a comment"
  OUT
)
message([[${not_a_reference} # comment]])
'''
        result = analyze(source)
        self.assertIn("OUT", result.definitions)
        self.assertEqual(result.definitions["OUT"].line, 3)
        self.assertFalse(result.issues)

    def test_annotation_warnings_and_old_metadata_ignored(self):
        diagnostics = lint_cmake("## function(f [FOO)\n## set()\n## function()\n")
        self.assertEqual(len(diagnostics), 3)
        self.assertTrue(all(d.severity == 2 for d in diagnostics))
        result = analyze("##cmake-ls: define OLD\n##cmake-ls: signature <OLD>\nfunction(f ARG)\nendfunction()\n")
        self.assertNotIn("OLD", result.definitions)
        self.assertEqual(result.commands["f"].overloads[0].signature, "<?ARG>")

    def test_case_sensitive_validation(self):
        diagnostics = lint_cmake("## function(F FOO)\nf(foo)\nF(FOO)\n")
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0].range.start.line, 1)


class IncludeTests(unittest.TestCase):
    def test_transitive_relative_cycle_and_deduplication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sub").mkdir()
            (root / "sub" / "a.cmake").write_text('## include(../b.cmake)\n## function(imported FOO)\nfunction(ordinary X)\nset(HIDDEN 1)\nendfunction()\n', encoding="utf-8")
            (root / "b.cmake").write_text('## include(sub/a.cmake)\n## Description.\n## set(IMPORTED 1)\n', encoding="utf-8")
            source = '## include(sub/a.cmake)\ninclude("sub/a.cmake")\nimported(FOO)\n'
            result = analyze(source, uri=(root / "main.cmake").as_uri())
            self.assertEqual(set(result.commands), {"imported", "ordinary"})
            self.assertEqual(len(result.commands["imported"].overloads), 1)
            self.assertIn("IMPORTED", result.definitions)
            self.assertNotIn("HIDDEN", result.definitions)
            self.assertEqual(result.commands["imported"].uri, (root / "sub" / "a.cmake").as_uri())
            self.assertFalse(result.issues)

    def test_dynamic_and_missing_includes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.cmake").write_text("## function(loaded FOO)\n", encoding="utf-8")
            source = 'set(PATH a.cmake)\ninclude(${PATH})\ninclude(${unknown})\ninclude(missing.cmake OPTIONAL)\n'
            result = analyze(source, uri=(root / "main.cmake").as_uri())
            self.assertIn("loaded", result.commands)
            self.assertFalse(any("Cannot read" in i.message for i in result.issues))
            diagnostics = lint_cmake("include(missing.cmake)\n", uri=(root / "main.cmake").as_uri())
            self.assertEqual(len(diagnostics), 1)
            self.assertEqual(diagnostics[0].severity, 2)

    def test_include_visibility_and_live_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            uri = (Path(directory) / "main.cmake").as_uri()
            loader = lambda _: "## function(local FOO)\n"
            source = "function(test)\n## include(a.cmake)\nlocal(FOO)\nendfunction()\n"
            result = analyze(source, uri=uri, loader=loader)
            self.assertNotIn("local", result.commands)
            inside = analyze(source, uri=uri, position_line=2, loader=loader)
            self.assertIn("local", inside.commands)
            self.assertNotIn("local", analyze("", uri=uri, loader=loader).commands)

    def test_current_list_directory_and_repeated_import_in_distinct_scopes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.cmake").write_text("## function(local FOO)\n", encoding="utf-8")
            uri = (root / "main.cmake").as_uri()
            source = 'function(first)\ninclude("${CMAKE_CURRENT_LIST_DIR}/a.cmake")\nendfunction()\nfunction(second)\ninclude("${CMAKE_CURRENT_LIST_DIR}/a.cmake")\n'
            result = analyze(source, uri=uri, position_line=5)
            self.assertIn("local", result.commands)
            self.assertFalse(result.issues)


class LspTests(unittest.TestCase):
    def call(self, handler, params_type, source, line=None, character=None, uri="file:///test.cmake", documents=None):
        doc = TextDocument(uri=uri, source=source)
        ls = MagicMock()
        ls.workspace.get_text_document.return_value = doc
        ls.workspace.text_documents = documents or {}
        lines = source.split("\n")
        if line is None:
            line = len(lines) - 1
        if character is None:
            character = len(lines[line].encode("utf-16-le")) // 2
        params = params_type(text_document=TextDocumentIdentifier(uri=uri), position=Position(line=line, character=character))
        return handler(ls, params)

    def test_incomplete_completion(self):
        prefix = "## function(math FEXPR <?expression> [PRECISION <DEFAULT|FULL>])\n"
        result = self.call(completions, CompletionParams, prefix + "math(FEXPR x ")
        self.assertEqual([i.label for i in result.items], ["PRECISION"])
        result = self.call(completions, CompletionParams, prefix + "math(FEXPR x PRECISION ")
        self.assertEqual([i.label for i in result.items], ["DEFAULT", "FULL"])

    def test_completion_union_and_variables(self):
        source = "## function(f FOO)\n## function(f BAR)\nf("
        result = self.call(completions, CompletionParams, source)
        self.assertEqual([i.label for i in result.items], ["BAR", "FOO"])
        source = "## function(f <&var>)\nset(EXISTING 1)\nf("
        result = self.call(completions, CompletionParams, source)
        self.assertIn("EXISTING", [i.label for i in result.items])

    def test_custom_signature_and_hover_markdown(self):
        source = "## **First**.\n## function(Mixed FOO)\n## Second.\n## function(mixed BAR)\nfunction(mixed A B)\nendfunction()\nMIXED("
        result = self.call(signature_help, SignatureHelpParams, source)
        self.assertEqual([s.label for s in result.signatures], ["Mixed(FOO)", "Mixed(BAR)"])
        self.assertEqual(result.signatures[0].documentation.value, "**First**.")
        result = self.call(hover, HoverParams, source, character=2)
        self.assertIn("**First**.", result.contents.value)
        self.assertIn("Second.", result.contents.value)

    def test_imported_definition_and_unsaved_annotation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            uri = (root / "main.cmake").as_uri()
            imported_uri = (root / "a.cmake").as_uri()
            documents = {imported_uri: TextDocument(uri=imported_uri, source="## **Imported**.\n## function(Imported FOO)\n")}
            source = "## include(a.cmake)\nImported(FOO)"
            result = self.call(definition, DefinitionParams, source, character=2, uri=uri, documents=documents)
            self.assertEqual(result.uri, imported_uri)
            self.assertEqual(result.range.start.line, 1)
            self.assertEqual(result.range.start.character, 12)

    def test_comments_and_parentheses_in_strings(self):
        source = '## function(f <?arg> [FOO])\nf("text ) #" '
        result = self.call(completions, CompletionParams, source)
        self.assertEqual([i.label for i in result.items], ["FOO"])
        self.assertIsNotNone(self.call(signature_help, SignatureHelpParams, source))
        source += "# comment"
        self.assertFalse(self.call(completions, CompletionParams, source).items)

    def test_whitespace_inside_unfinished_quote_does_not_advance_argument(self):
        source = '## function(f <?arg> [FOO])\nf("unfinished '
        result = self.call(completions, CompletionParams, source)
        self.assertEqual(result.items, [])


if __name__ == "__main__":
    unittest.main()
