from lsprotocol.types import Diagnostic, DiagnosticSeverity, Range, Position

from .analysis import analyze


def lint_cmake(source, uri=None, loader=None):
    result = analyze(source, uri=uri, loader=loader)
    lines = source.splitlines()

    def protocol_character(issue):
        prefix = lines[issue.line][:issue.character] if issue.line < len(lines) else ""
        return len(prefix.encode("utf-16-le")) // 2

    return [
        Diagnostic(
            range=Range(
                start=Position(line=issue.line, character=protocol_character(issue)),
                end=Position(line=issue.line, character=protocol_character(issue) + 1),
            ),
            message=issue.message,
            severity=DiagnosticSeverity.Warning if issue.warning else DiagnosticSeverity.Error,
        )
        for issue in result.issues
        if issue.uri == uri
    ]
