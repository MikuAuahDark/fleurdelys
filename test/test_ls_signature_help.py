import unittest
from unittest.mock import MagicMock
from lsprotocol.types import SignatureHelpParams, TextDocumentIdentifier, Position
from pygls.workspace import TextDocument, Workspace
from cmake_ls.server import signature_help, CMakeLanguageServer


class TestSignatureHelp(unittest.TestCase):
    def setUp(self):
        self.ls = MagicMock(spec=CMakeLanguageServer)
        self.ls.workspace = MagicMock(spec=Workspace)

    def get_signature_help(self, source, line, character):
        uri = "file:///test.cmake"
        doc = TextDocument(uri=uri, source=source)
        self.ls.workspace.get_text_document.return_value = doc

        params = SignatureHelpParams(
            text_document=TextDocumentIdentifier(uri=uri),
            position=Position(line=line, character=character),
        )
        return signature_help(self.ls, params)

    def test_basic_signature(self):
        source = "project(foo)"
        # Inside project(
        res = self.get_signature_help(source, 0, 8)
        self.assertIsNotNone(res)
        self.assertEqual(
            res.signatures[0].label,
            "project(<projectname> [VERSION <major>[.<minor>[.<patch>[.<tweak>]]]] [LANGUAGES <language>...])",
        )

    def test_closed_signature(self):
        source = "project(foo)"
        # After project(foo)
        res = self.get_signature_help(source, 0, 12)
        self.assertIsNone(res)

    def test_multiline_signature(self):
        source = "target_link_libraries(\n    mytarget\n    PUBLIC\n    other\n)"
        # Inside on second line
        res = self.get_signature_help(source, 1, 4)
        self.assertIsNotNone(res)
        self.assertTrue(any("target_link_libraries" in s.label for s in res.signatures))

        # Inside on third line
        res = self.get_signature_help(source, 2, 4)
        self.assertIsNotNone(res)

        # After closing paren on last line
        res = self.get_signature_help(source, 4, 1)
        self.assertIsNone(res)

    def test_index_error_guard(self):
        source = "project(foo)"
        # Position beyond file length
        res = self.get_signature_help(source, 5, 0)
        self.assertIsNone(res)

    def test_in_comment(self):
        source = "project(foo) # cursor here ("
        res = self.get_signature_help(source, 0, 27)
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
