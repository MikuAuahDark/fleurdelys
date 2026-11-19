import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from lsprotocol.types import CompletionParams, Position, TextDocumentIdentifier
from pygls.workspace import TextDocument

from fleurdelys.analysis import analyze
from fleurdelys.options import AnnotationOptions, configuration
from fleurdelys.server import CMakeLanguageServer, completions, configuration_changed, initialize


class EnvironmentExpansionTests(unittest.TestCase):
    def test_cli_and_snapshot_validation(self):
        from fleurdelys.__main__ import main

        with patch("fleurdelys.__main__.server") as server:
            main(["--expand-env-variable"])
            self.assertTrue(server.annotation_defaults.expand_env_variable)
            server.start_io.assert_called_once()
            main([])
            self.assertFalse(server.annotation_defaults.expand_env_variable)
        defaults = AnnotationOptions(expand_env_variable=True)
        self.assertEqual(configuration({}, defaults), defaults)
        self.assertFalse(configuration({"fleurdelys": {"expandEnvVariable": False}}, defaults).expand_env_variable)
        warnings = []
        for value in ("true", 1, None, []):
            self.assertTrue(configuration({"fleurdelys": {"expandEnvVariable": value}},
                                          defaults, warn=warnings.append).expand_env_variable)
        self.assertEqual(len(warnings), 4)

    def test_include_expansion_is_opt_in_and_missing_names_stay_unresolved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "pack.cmake").write_text("## set(IMPORTED)\n", encoding="utf-8")
            uri = (root / "main.cmake").as_uri()
            source = 'set(ROOT "$ENV{FLEURDELYS_TEST_ROOT}")\ninclude("${ROOT}/pack.cmake")\n'
            with patch.dict(os.environ, {"FLEURDELYS_TEST_ROOT": root.as_posix()}, clear=True):
                disabled = analyze(source, uri=uri)
                enabled = analyze(source, uri=uri, options=AnnotationOptions(expand_env_variable=True))
                self.assertNotIn("IMPORTED", disabled.definitions)
                self.assertIn("IMPORTED", enabled.definitions)
                direct = analyze('include("$ENV{FLEURDELYS_TEST_ROOT}/pack.cmake")\n', uri=uri,
                                 options=AnnotationOptions(expand_env_variable=True))
                self.assertIn("IMPORTED", direct.definitions)
                missing = analyze('set(X "$ENV{FLEURDELYS_MISSING}")\ninclude("${X}/pack.cmake")\n',
                                  uri=uri, options=AnnotationOptions(expand_env_variable=True))
                self.assertEqual(missing.definitions["X"].value, "$ENV{FLEURDELYS_MISSING}")
                self.assertFalse(missing.issues)

    def test_literal_and_other_namespace_references_are_not_expanded(self):
        source = 'set(A [=[$ENV{VALUE}]=])\nset(B "\\$ENV{VALUE}")\nset(C "$CACHE{VALUE}")\nset(D "$ENV{EMPTY}")\n'
        with patch.dict(os.environ, {"VALUE": "secret", "EMPTY": ""}, clear=True):
            result = analyze(source, options=AnnotationOptions(expand_env_variable=True))
        self.assertEqual(result.definitions["A"].value, "$ENV{VALUE}")
        self.assertEqual(result.definitions["B"].value, "\\$ENV{VALUE}")
        self.assertEqual(result.definitions["C"].value, "$CACHE{VALUE}")
        self.assertEqual(result.definitions["D"].value, "")

    def test_initialization_and_changes_update_environment_completions(self):
        ls = CMakeLanguageServer()
        ls.protocol._workspace = MagicMock()
        doc = TextDocument(uri="file:///test.cmake", source="message($ENV{")
        ls.workspace.get_text_document.return_value = doc
        ls.workspace.text_documents = {doc.uri: doc}
        params = CompletionParams(text_document=TextDocumentIdentifier(uri=doc.uri),
                                  position=Position(line=0, character=len(doc.source)))
        initialize(ls, SimpleNamespace(initialization_options={"fleurdelys": {"expandEnvVariable": True}},
                                       workspace_folders=[], root_uri=None, root_path=None))
        with patch.dict(os.environ, {"FLEURDELYS_PRIVATE": "secret-value"}, clear=True):
            items = completions(ls, params).items
            item = next(item for item in items if item.label == "FLEURDELYS_PRIVATE")
            self.assertNotIn("secret-value", str(item))
            with patch("fleurdelys.server.revalidate_all") as refresh:
                configuration_changed(ls, SimpleNamespace(settings={"fleurdelys": {"expandEnvVariable": False}}))
                self.assertNotIn("FLEURDELYS_PRIVATE", [item.label for item in completions(ls, params).items])
                self.assertFalse(ls.analysis_options(doc.uri).expand_env_variable)
                refresh.assert_called_once_with(ls)
                ls.annotation_defaults = AnnotationOptions(expand_env_variable=True)
                configuration_changed(ls, SimpleNamespace(settings={}))
                self.assertTrue(ls.analysis_options(doc.uri).expand_env_variable)


if __name__ == "__main__":
    unittest.main()
