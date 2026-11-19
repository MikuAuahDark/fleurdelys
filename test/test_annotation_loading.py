import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fleurdelys.analysis import analyze
from fleurdelys.options import AnnotationOptions, configuration
from fleurdelys.server import CMakeLanguageServer, initialize, configuration_changed
from types import SimpleNamespace


class AnnotationLoadingTests(unittest.TestCase):
    def test_variable_catalogues_follow_annotation_pack_loading(self):
        core = analyze("")
        combined = analyze("", options=AnnotationOptions(True))
        self.assertIn("CMAKE_CURRENT_LIST_DIR", core.definitions)
        self.assertIn("CMAKE_CURRENT_LIST_FILE", core.definitions)
        self.assertEqual(set(core.variable_namespaces["ENV"]), {"PATH", "LD_LIBRARY_PATH"})
        cmake_names = {
            "CMAKE_SOURCE_DIR", "CMAKE_BINARY_DIR", "PROJECT_NAME", "PROJECT_SOURCE_DIR",
            "PROJECT_BINARY_DIR", "CMAKE_VERSION", "CMAKE_COMMAND", "WIN32", "UNIX",
            "APPLE", "MSVC", "CMAKE_CXX_COMPILER", "CMAKE_C_COMPILER", "BUILD_SHARED_LIBS",
            "CMAKE_BUILD_TYPE",
        }
        self.assertTrue(cmake_names.isdisjoint(core.definitions))
        self.assertTrue(cmake_names <= combined.definitions.keys())
        self.assertNotIn("CACHE", core.variable_namespaces)
        self.assertEqual(set(combined.variable_namespaces["CACHE"]), {
            "CMAKE_INSTALL_PREFIX", "BUILD_SHARED_LIBS", "CMAKE_EXPORT_COMPILE_COMMANDS",
        })
        self.assertEqual(set(combined.variable_namespaces["ENV"]), {
            "PATH", "LD_LIBRARY_PATH", "CMAKE_PREFIX_PATH", "CXX", "CC", "CFLAGS", "CXXFLAGS", "LDFLAGS",
        })
        source = "message(${PROJECT_NAME})\n"
        self.assertTrue(any("may be undefined" in i.message for i in analyze(source).issues))
        self.assertFalse(analyze(source, options=AnnotationOptions(True)).issues)

    def test_disabled_or_missing_packs_have_no_hardcoded_variable_fallback(self):
        with patch("fleurdelys.analysis.CORE_ANNOTATIONS", Path("missing-core.cmake").resolve()):
            result = analyze("message(${CMAKE_CURRENT_LIST_DIR})\n", report=lambda message: None)
        self.assertNotIn("CMAKE_CURRENT_LIST_DIR", result.definitions)
        self.assertFalse(result.variable_namespaces)
        self.assertTrue(any("may be undefined" in i.message for i in result.issues))

    def test_bundled_cmake_extends_core_overloads(self):
        core = analyze("")
        combined = analyze("", options=AnnotationOptions(True))
        for name, command in core.commands.items():
            with self.subTest(command=name):
                self.assertEqual(combined.commands[name].signatures[:len(command.signatures)],
                                 command.signatures)
        self.assertGreater(len(combined.commands["message"].signatures),
                           len(core.commands["message"].signatures))
        for args in (["STATUS", '"hello"'], ["AUTHOR_WARNING", '"hello"'],
                     ["CHECK_START", '"checking"']):
            with self.subTest(args=args):
                self.assertTrue(any(overload.matcher.match(args).success
                                    for overload in combined.commands["message"].overloads))
        source = Path(__file__).with_name("hello.cmake").read_text(encoding="utf-8")
        result = analyze(source, options=AnnotationOptions(True))
        self.assertFalse(any(issue.message == "Invalid arguments for 'message'."
                             for issue in result.issues))

    def test_external_packs_extend_bundled_overloads_and_local_can_override(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = Path(directory) / "pack.cmake"
            pack.write_text("## function(message EXTERNAL)\n", encoding="utf-8")
            options = AnnotationOptions(True, (pack,))
            bundled = analyze("", options=AnnotationOptions(True)).commands["message"].signatures
            self.assertEqual(analyze("", options=options).commands["message"].signatures,
                             bundled + ["EXTERNAL"])
            result = analyze("## function(message LOCAL)\n", options=options)
            self.assertEqual(result.commands["message"].signatures, ["LOCAL"])

    def test_secondary_analysis_uses_its_workspace_without_leaking_defaults(self):
        from fleurdelys.server import at_cursor
        from pygls.workspace import TextDocument
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            roots = [root / "one", root / "two"]
            documents = {}
            for index, folder in enumerate(roots):
                folder.mkdir()
                (folder / "pack.cmake").write_text(f"## symbol(t pack{index})\n## function(create <t&name>)\n", encoding="utf-8")
                doc = TextDocument(uri=(folder / "consumer.cmake").as_uri(), source=f"create(local{index})\n")
                documents[doc.uri] = doc
            ls = CMakeLanguageServer()
            ls.protocol._workspace = MagicMock()
            ls.workspace.text_documents = documents
            ls.annotation_roots = roots
            ls.annotation_settings = {"fleurdelys": {"additionalAnnotations": ["pack.cmake"]}}
            doc = next(iter(documents.values()))
            result = at_cursor(ls, SimpleNamespace(text_document=SimpleNamespace(uri=doc.uri)), doc, 0)
            self.assertIn("pack0", result.symbols["t"])
            self.assertNotIn("pack1", result.symbols["t"])
            self.assertIn("local1", result.symbols["t"])

    def test_annotation_lifecycle_and_warning_deduplication(self):
        from fleurdelys.server import did_close, watched_files_changed, at_cursor
        from pygls.workspace import TextDocument
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            pack = root / "pack.cmake"
            pack.write_text("## function(use <t:name>)\n## symbol(t disk)\n", encoding="utf-8")
            consumer = TextDocument(uri=(root / "consumer.cmake").as_uri(), source="use(")
            ls = CMakeLanguageServer()
            ls.protocol._workspace = MagicMock()
            documents = {consumer.uri: consumer, pack.as_uri(): TextDocument(uri=pack.as_uri(), source="## symbol(t buffer)\n")}
            ls.workspace.text_documents = documents
            ls.workspace.get_text_document.side_effect = documents.__getitem__
            ls.annotation_defaults = AnnotationOptions(False, (pack,))
            params = SimpleNamespace(text_document=SimpleNamespace(uri=consumer.uri))
            self.assertIn("buffer", at_cursor(ls, params, consumer, 4).symbols["t"])
            documents.pop(pack.as_uri())
            with patch("fleurdelys.server.revalidate_all") as refresh:
                did_close(ls, SimpleNamespace(text_document=SimpleNamespace(uri=pack.as_uri())))
                result = at_cursor(ls, params, consumer, 4)
                self.assertIn("disk", result.symbols["t"])
                self.assertNotIn("buffer", result.symbols["t"])
                pack.write_text("## symbol(t changed)\n", encoding="utf-8")
                watched_files_changed(ls, SimpleNamespace(changes=[SimpleNamespace(uri=pack.as_uri())]))
                self.assertIn("changed", at_cursor(ls, params, consumer, 4).symbols["t"])
                self.assertEqual(refresh.call_count, 2)
            ls.annotation_defaults = AnnotationOptions(False, (root / "missing.cmake",))
            with patch.object(ls, "window_log_message") as log:
                at_cursor(ls, params, consumer, 4)
                at_cursor(ls, params, consumer, 4)
                self.assertEqual(log.call_count, 1)

    def test_cli_order_defaults_and_transport(self):
        from fleurdelys.__main__ import main
        with patch("fleurdelys.__main__.server") as server:
            main(["--enable-cmake-annotations", "--annotation", "one.cmake", "--annotation", "two.cmake"])
            self.assertTrue(server.annotation_defaults.enable_cmake_annotations)
            self.assertEqual(server.annotation_defaults.additional_annotations, (Path("one.cmake").resolve(), Path("two.cmake").resolve()))
            server.start_io.assert_called_once()
            main(["--tcp", "--host", "localhost", "--port", "1234"])
            server.start_tcp.assert_called_once_with("localhost", 1234)

    def test_pack_variables_symbols_and_malformed_scope_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first, second = root / "first.cmake", root / "second.cmake"
            first.write_text("## set(PACK_VALUE first)\n## symbol(t app)\nfunction(unclosed)\n", encoding="utf-8")
            second.write_text("## set(PACK_VALUE second)\n## Later symbol.\n## symbol(t app)\n## function(visible SECOND)\n", encoding="utf-8")
            result = analyze("", options=AnnotationOptions(False, (first, second)), report=lambda message: None)
            self.assertEqual(result.definitions["PACK_VALUE"].value, "second")
            self.assertEqual(result.symbols["t"]["app"].description, "Later symbol.")
            self.assertIn("visible", result.commands)
            self.assertFalse(result.source_symbols["t"])

    def test_optional_cmake_and_cursor_defaults(self):
        self.assertNotIn("add_executable", analyze("").commands)
        result = analyze("", position_offset=0, options=AnnotationOptions(True))
        self.assertIn("add_executable", result.commands)
        self.assertIn("set", result.commands)
        self.assertIn("CMAKE_ROOT", result.definitions)
        self.assertIn("app", analyze("add_executable(app main.c)", options=AnnotationOptions(True)).symbols["t"])
        self.assertNotIn("add_executable", analyze("").commands)

    def test_missing_bundled_and_invalid_encoding_are_actionable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            bad = root / "bad.cmake"
            bad.write_bytes(b"\xff\xff")
            warnings = []
            with patch("fleurdelys.analysis.CORE_ANNOTATIONS", root / "core.cmake"):
                result = analyze("## function(local LOCAL)\n", options=AnnotationOptions(False, (bad,)), report=warnings.append)
            self.assertIn("local", result.commands)
            self.assertEqual(len(warnings), 2)
            self.assertIn("repair the installation", warnings[0])
            self.assertIn(str(bad), warnings[1])

    def test_order_overloads_transitive_includes_and_navigation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first, second, child = [root / name for name in ("first.cmake", "second.cmake", "child.cmake")]
            first.write_text("## function(example FIRST)\n", encoding="utf-8")
            child.write_text("## function(example SECOND)\n## function(example THIRD)\n## include(second.cmake)\n", encoding="utf-8")
            second.write_text("## include(child.cmake)\n", encoding="utf-8")
            options = AnnotationOptions(False, (first, second, second))
            result = analyze("", options=options)
            self.assertEqual(result.commands["example"].signatures, ["FIRST", "SECOND", "THIRD"])
            self.assertEqual(result.commands["example"].uri, first.as_uri())
            self.assertEqual(result.commands["example"].overloads[1].uri, child.as_uri())
            result = analyze("## function(example LOCAL)\nfunction(example x)\nendfunction()\n", uri=(root / "consumer.cmake").as_uri(), options=options)
            self.assertEqual(result.commands["example"].signatures, ["LOCAL"])
            self.assertEqual(result.commands["example"].line, 1)
            result = analyze("function(example x)\nendfunction()\n", options=options)
            self.assertEqual(result.commands["example"].overloads[0].signature, "<?x>")

    def test_optional_failures_and_unsaved_buffers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            missing, valid = root / "missing.cmake", root / "space ü.cmake"
            valid.write_text("## function(example DISK)\n", encoding="utf-8")
            warnings = []
            result = analyze("", options=AnnotationOptions(False, (missing, valid)),
                             loader=lambda uri: "## function(example BUFFER)\n## function()\n" if uri == valid.as_uri() else None,
                             report=warnings.append)
            self.assertEqual(result.commands["example"].signatures, ["BUFFER"])
            self.assertEqual(result.commands["example"].uri, valid.as_uri())
            self.assertEqual(len(warnings), 2)

    def test_snapshot_defaults_validation_and_path_base(self):
        root = Path(tempfile.gettempdir()).resolve()
        defaults = AnnotationOptions(True, (root / "startup.cmake",))
        self.assertEqual(configuration({}, defaults), defaults)
        self.assertEqual(configuration({"fleurdelys": {"enableCMakeAnnotations": False, "additionalAnnotations": []}}, defaults), AnnotationOptions())
        warnings = []
        self.assertEqual(configuration({"fleurdelys": {"enableCMakeAnnotations": "false", "additionalAnnotations": "file"}}, defaults, warn=warnings.append), defaults)
        self.assertEqual(len(warnings), 2)
        self.assertEqual(configuration({"fleurdelys": {"additionalAnnotations": ["pack.cmake", "./pack.cmake"]}}, base=root).additional_annotations, (root / "pack.cmake",))
        self.assertFalse(configuration({"fleurdelys": {"additionalAnnotations": ["pack.cmake"]}}, warn=warnings.append).additional_annotations)

    def test_server_initialization_snapshot_and_workspace_bases(self):
        root = Path(tempfile.gettempdir()).resolve()
        ls = CMakeLanguageServer()
        ls.annotation_defaults = AnnotationOptions(True)
        initialize(ls, SimpleNamespace(initialization_options={"fleurdelys": {"additionalAnnotations": ["pack.cmake"]}}, workspace_folders=[SimpleNamespace(uri=root.as_uri())], root_uri=None, root_path=None))
        self.assertEqual(ls.analysis_options((root / "consumer.cmake").as_uri()).additional_annotations, (root / "pack.cmake",))
        with patch("fleurdelys.server.revalidate_all") as refresh:
            configuration_changed(ls, SimpleNamespace(settings={"fleurdelys": {"enableCMakeAnnotations": False, "additionalAnnotations": []}}))
            self.assertFalse(ls.analysis_options(None).enable_cmake_annotations)
            configuration_changed(ls, SimpleNamespace(settings={}))
            self.assertTrue(ls.analysis_options(None).enable_cmake_annotations)
            self.assertEqual(refresh.call_count, 2)


if __name__ == "__main__":
    unittest.main()

