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
from fleurdelys.constants import CORE_ANNOTATIONS
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
        self.assertEqual(matcher.match(["X", "Y"]).definitions, {("", 0)})
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

    def test_namespaces_and_suggestions(self):
        symbols = {"t": {"app"}, "v": {"ordinary_symbol"}}
        for signature, expected in (("<:value>", ["LOCAL"]), ("<&value>", ["LOCAL"]), ("<t:target>", ["app"]), ("<v:value>", ["ordinary_symbol"]), ("<?value>", []), ("<t&target>", ["app"])):
            with self.subTest(signature=signature):
                matcher = self.matcher(signature)
                self.assertEqual(matcher.get_completions([], ["LOCAL"], symbols), expected)
                self.assertTrue(matcher.match(["unknown"]).success)
        self.assertEqual(self.matcher("<t&target>").match(["pkg::target"]).definitions, {("t", 0)})
        self.assertFalse(self.matcher("<t&target>").match(['"app"']).definitions)
        self.assertFalse(self.matcher("<t&target>").match(["${name}"]).definitions)
        for signature in ("<:>", "<t&>", "<t?name>", "<t:bad:name>", "<FOO|t:name>"):
            with self.subTest(signature=signature), self.assertRaises(ValueError):
                self.matcher(signature)


class AnalysisTests(unittest.TestCase):
    def test_documented_symbol_annotations(self):
        source = "## **Application** target.\n## symbol(t app)\nfunction(f)\n## Dependency.\n## symbol(t pkg::library)\nendfunction()\n## symbol(v app)\n"
        result = analyze(source, uri="file:///test.cmake")
        app = result.symbols["t"]["app"]
        self.assertEqual(app.description, "**Application** target.")
        self.assertEqual((app.line, app.character, app.uri), (1, 12, "file:///test.cmake"))
        self.assertIn("pkg::library", result.symbols["t"])
        self.assertIn("app", result.symbols["v"])
        self.assertNotIn("app", result.definitions)
        self.assertFalse(result.issues)

    def test_symbol_annotation_validation_and_replacement(self):
        for declaration in ("symbol()", "symbol(t)", "symbol(t app extra)", 'symbol("t" app)', "symbol(t ${name})", 'symbol(t "app")', "symbol(t [[app]])", "symbol(bad-name app)"):
            with self.subTest(declaration=declaration):
                result = analyze("## " + declaration + "\n")
                self.assertEqual(len(result.issues), 1)
                self.assertFalse(result.symbols)
        result = analyze("## function(create <t&name>)\ncreate(app)\n## Documented.\n## symbol(t app)\ncreate(app)\n")
        self.assertEqual(result.symbols["t"]["app"].description, "Documented.")
        self.assertEqual(result.symbols["t"]["app"].line, 3)

    def test_symbols_are_global_and_separate_from_variables(self):
        source = """## function(create <t&name>)
## function(other <v&name>)
function(f)
set(LOCAL 1)
create(app)
other(app)
endfunction()
"""
        result = analyze(source)
        self.assertEqual(set(result.symbols), {"t", "v"})
        self.assertIn("app", result.symbols["t"])
        self.assertIn("app", result.symbols["v"])
        self.assertNotIn("app", result.definitions)
        self.assertNotIn("LOCAL", result.definitions)
        self.assertFalse(result.issues)
        ambiguous = analyze("## function(f <t&name>)\n## function(f <v&name>)\nf(app)\n")
        self.assertFalse(ambiguous.symbols)

    def test_cmake_target_annotations(self):
        annotations = CORE_ANNOTATIONS.with_name("cmake.cmake")
        source = f'## include("{annotations.as_posix()}")\nadd_executable(foo WIN32 program.cpp)\ntarget_compile_definitions(foo PRIVATE FLAG)\n'
        result = analyze(source, uri=Path("main.cmake").resolve().as_uri())
        self.assertIn("foo", result.symbols["t"])
        self.assertNotIn("foo", result.definitions)
        self.assertFalse(result.issues)

    def test_core_preloaded_for_each_unit_and_cursor(self):
        for options in ({}, {"uri": "untitled:example"}, {"position_offset": 0}, {"position_line": 0}):
            with self.subTest(options=options):
                result = analyze("", **options)
                self.assertIn("string", result.commands)
                self.assertIn("cmake_path", result.commands)
                self.assertEqual(result.commands["string"].uri, CORE_ANNOTATIONS.as_uri())
                self.assertFalse(result.issues)
        result = analyze('string(TOUPPER text OUTPUT)\nmessage(${OUTPUT})\n')
        self.assertIn("OUTPUT", result.definitions)
        self.assertFalse(result.issues)
        self.assertNotIn("OUTPUT", analyze("").definitions)

    def test_core_include_is_not_duplicated(self):
        baseline = analyze("").commands["string"].signatures
        source = f'## include("{CORE_ANNOTATIONS.as_posix()}")\n'
        self.assertEqual(analyze(source, uri="file:///main.cmake").commands["string"].signatures, baseline)

    def test_unsaved_core_annotations_are_loaded(self):
        core_uri = CORE_ANNOTATIONS.as_uri()
        loader = lambda target: "## function(updated FOO)\n" if target == core_uri else None
        result = analyze("updated(FOO)\n", loader=loader)
        self.assertEqual(result.commands["updated"].uri, core_uri)
        self.assertFalse(result.issues)

    def test_local_annotations_replace_core_signatures(self):
        result = analyze("## function(math CUSTOM)\nmath(CUSTOM)\n")
        self.assertEqual(result.commands["math"].signatures, ["CUSTOM"])
        self.assertEqual(result.commands["math"].line, 0)
        self.assertFalse(result.issues)
        self.assertNotEqual(analyze("").commands["math"].signatures, ["CUSTOM"])

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
        self.assertEqual(set(result.commands) - set(analyze("").commands), {"right"})
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
            root = Path(directory).resolve()
            (root / "sub").mkdir()
            (root / "sub" / "a.cmake").write_text('## include(../b.cmake)\n## function(imported FOO)\nfunction(ordinary X)\nset(HIDDEN 1)\nendfunction()\n', encoding="utf-8")
            (root / "b.cmake").write_text('## include(sub/a.cmake)\n## Description.\n## set(IMPORTED 1)\n', encoding="utf-8")
            source = '## include(sub/a.cmake)\ninclude("sub/a.cmake")\nimported(FOO)\n'
            result = analyze(source, uri=(root / "main.cmake").as_uri())
            self.assertEqual(set(result.commands) - set(analyze("").commands), {"imported", "ordinary"})
            self.assertEqual(len(result.commands["imported"].overloads), 1)
            self.assertIn("IMPORTED", result.definitions)
            self.assertNotIn("HIDDEN", result.definitions)
            self.assertEqual(result.commands["imported"].uri, (root / "sub" / "a.cmake").as_uri())
            self.assertFalse(result.issues)

    def test_dynamic_and_missing_includes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
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
            uri = (Path(directory).resolve() / "main.cmake").as_uri()
            loader = lambda target: None if target == CORE_ANNOTATIONS.as_uri() else "## function(local FOO)\n"
            source = "function(test)\n## include(a.cmake)\nlocal(FOO)\nendfunction()\n"
            result = analyze(source, uri=uri, loader=loader)
            self.assertNotIn("local", result.commands)
            inside = analyze(source, uri=uri, position_line=2, loader=loader)
            self.assertIn("local", inside.commands)
            self.assertNotIn("local", analyze("", uri=uri, loader=loader).commands)

    def test_current_list_directory_and_repeated_import_in_distinct_scopes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "a.cmake").write_text("## function(local FOO)\n", encoding="utf-8")
            uri = (root / "main.cmake").as_uri()
            source = 'function(first)\ninclude("${CMAKE_CURRENT_LIST_DIR}/a.cmake")\nendfunction()\nfunction(second)\ninclude("${CMAKE_CURRENT_LIST_DIR}/a.cmake")\n'
            result = analyze(source, uri=uri, position_line=5)
            self.assertIn("local", result.commands)
            self.assertFalse(result.issues)


class LspTests(unittest.TestCase):
    def test_variable_documentation_comes_from_annotations(self):
        result = self.call(completions, CompletionParams, "message($ENV{")
        self.assertEqual([item.label for item in result.items], ["LD_LIBRARY_PATH", "PATH"])
        self.assertTrue(all(item.documentation.value for item in result.items))
        source = "message($ENV{PATH})"
        info = self.call(hover, HoverParams, source, character=14)
        self.assertIn("System search path", info.contents.value)
        location = self.call(definition, DefinitionParams, source, character=14)
        self.assertEqual(location.uri, CORE_ANNOTATIONS.as_uri())
        result = self.call(completions, CompletionParams, "message(${PROJECT_")
        self.assertNotIn("PROJECT_NAME", [item.label for item in result.items])
        self.assertIsNone(self.call(hover, HoverParams, "message(${PROJECT_NAME})", character=15))

    def test_namespaced_variable_annotations(self):
        prefix = "## Cache docs.\n## set(CACHE{FOO} value)\n## Custom docs.\n## set(FOO{BAR})\n"
        result = analyze(prefix + "message($FOO{BAR} $CACHE{FOO})\n")
        self.assertFalse(result.issues)
        self.assertNotIn("BAR", result.definitions)
        self.assertEqual(result.variable_namespaces["CACHE"]["FOO"].value, "value")
        self.assertEqual(result.variable_namespaces["FOO"]["BAR"].description, "Custom docs.")
        items = self.call(completions, CompletionParams, prefix + "message($FOO{").items
        self.assertEqual([item.label for item in items], ["BAR"])
        self.assertEqual(items[0].documentation.value, "Custom docs.")
        items = self.call(completions, CompletionParams, prefix + "message($").items
        self.assertIn("FOO{", [item.label for item in items])
        source = prefix + "message($FOO{BAR})"
        info = self.call(hover, HoverParams, source, character=14)
        self.assertIn("Custom docs.", info.contents.value)
        location = self.call(definition, DefinitionParams, source, character=14)
        self.assertEqual((location.range.start.line, location.range.start.character), (3, 11))

    def test_variable_namespace_scope_and_validation(self):
        source = "function(f)\n## set(FOO{BAR})\nmessage($FOO{BAR})\nendfunction()\nmessage($FOO{BAR})\n"
        result = analyze(source)
        self.assertNotIn("FOO", result.variable_namespaces)
        self.assertEqual([i.line for i in result.issues if "Unknown variable namespace" in i.message], [4])
        self.assertNotIn("FOO", analyze("").variable_namespaces)
        for target in ("FOO{}", "FOO{${BAR}}", "1FOO{BAR}", '"FOO{BAR}"', "FOO{BAR}{BAZ}"):
            with self.subTest(target=target):
                result = analyze(f"## set({target})\n")
                self.assertTrue(any("literal variable name" in i.message for i in result.issues))

    def test_imported_variable_namespace_is_separate_from_symbols(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "pack.cmake").write_text("## Imported docs.\n## set(FOO{BAR})\n", encoding="utf-8")
            source = "## include(pack.cmake)\n## symbol(FOO target)\nmessage($FOO{BAR})\n"
            result = analyze(source, uri=(root / "main.cmake").as_uri())
            self.assertFalse(result.issues)
            self.assertEqual(set(result.variable_namespaces["FOO"]), {"BAR"})
            self.assertEqual(set(result.symbols["FOO"]), {"target"})
            self.assertEqual(result.variable_namespaces["FOO"]["BAR"].uri, (root / "pack.cmake").as_uri())

    def test_declared_symbol_completion(self):
        source = "## symbol(t app)\n## symbol(v other)\n## function(use <t:name>)\nuse("
        result = self.call(completions, CompletionParams, source)
        self.assertEqual([item.label for item in result.items], ["app"])

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

    def test_core_completion_and_hover_without_include(self):
        result = self.call(completions, CompletionParams, "string(")
        self.assertIn("TOUPPER", [item.label for item in result.items])
        result = self.call(hover, HoverParams, "string(", character=2)
        self.assertIn("string(", result.contents.value)
        self.assertIn("https://cmake.org/", result.contents.value)

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
        source = "## function(f <:var>)\nset(EXISTING 1)\nf("
        result = self.call(completions, CompletionParams, source)
        self.assertIn("EXISTING", [i.label for i in result.items])

    def test_symbol_completions_across_documents_and_edits(self):
        uri = "file:///targets.cmake"
        documents = {uri: TextDocument(uri=uri, source="## function(create <t&name>)\nfunction(f)\ncreate(app)\nendfunction()\n")}
        source = "## function(use <t:name>)\nset(VARIABLE 1)\nuse("
        result = self.call(completions, CompletionParams, source, documents=documents)
        self.assertEqual([i.label for i in result.items], ["app"])
        documents[uri] = TextDocument(uri=uri, source="")
        result = self.call(completions, CompletionParams, source, documents=documents)
        self.assertEqual(result.items, [])

    def test_closed_document_symbols_are_retained_until_edited(self):
        uri = "file:///targets.cmake"
        doc = TextDocument(uri=uri, source="## function(use <t:name>)\nuse(")
        ls = MagicMock()
        ls.workspace.get_text_document.return_value = doc
        ls.workspace.text_documents = {
            "file:///other.cmake": TextDocument(uri="file:///other.cmake", source="## function(create <t&name>)\ncreate(app)\n")
        }
        params = CompletionParams(text_document=TextDocumentIdentifier(uri=uri), position=Position(line=1, character=4))
        self.assertEqual([item.label for item in completions(ls, params).items], ["app"])
        ls.workspace.text_documents = {}
        self.assertEqual([item.label for item in completions(ls, params).items], ["app"])
        ls.workspace.text_documents = {"file:///other.cmake": TextDocument(uri="file:///other.cmake", source="")}
        self.assertEqual(completions(ls, params).items, [])

    def test_variable_suggestions_respect_scope(self):
        source = "## function(use <:name>)\nfunction(f)\nset(LOCAL 1)\nendfunction()\nuse("
        result = self.call(completions, CompletionParams, source)
        self.assertNotIn("LOCAL", [i.label for i in result.items])

    def test_definition_placeholders_also_suggest(self):
        for operator in ("&", ":"):
            source = f"## function(create <t&name>)\n## function(use <t{operator}name>)\ncreate(app)\nuse("
            result = self.call(completions, CompletionParams, source)
            self.assertEqual([i.label for i in result.items], ["app"])

    def test_symbols_visible_before_cursor_and_from_imports(self):
        uri = Path("main.cmake").resolve().as_uri()
        imported_uri = Path("targets.cmake").resolve().as_uri()
        documents = {imported_uri: TextDocument(uri=imported_uri, source="## function(create <t&name>)\ncreate(imported)\n")}
        source = "## function(use <t:name>)\nuse(\n)\n## include(targets.cmake)\n"
        result = self.call(completions, CompletionParams, source, line=1, character=4, uri=uri, documents=documents)
        self.assertEqual([i.label for i in result.items], ["imported"])

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
            root = Path(directory).resolve()
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
