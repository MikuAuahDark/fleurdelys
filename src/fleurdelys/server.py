import re

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_SIGNATURE_HELP,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    CompletionParams,
    CompletionList,
    CompletionItem,
    CompletionItemKind,
    CompletionOptions,
    DefinitionParams,
    HoverParams,
    Hover,
    MarkupContent,
    MarkupKind,
    SignatureHelpParams,
    SignatureHelp,
    SignatureInformation,
    SignatureHelpOptions,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    PublishDiagnosticsParams,
    Location,
    Range,
    Position,
)

from .analysis import analyze, command_overloads
from .constants import ALL_COMMANDS, BUILTIN_VARIABLES, COMMAND_SIGNATURES, VARIABLE_NAMESPACES
from .syntax import active_command, in_comment, line_starts


class CMakeLanguageServer(LanguageServer):
    def __init__(self):
        super().__init__("cmake-ls", "0.1.0")


server = CMakeLanguageServer()


def markdown(value):
    return MarkupContent(kind=MarkupKind.Markdown, value=value or "")


def document_offset(doc, position):
    starts = line_starts(doc.source)
    if position.line >= len(starts):
        return None
    # LSP positions use UTF-16 code units by default.
    line = doc.source[starts[position.line] :].split("\n", 1)[0]
    prefix = line.encode("utf-16-le")[: position.character * 2].decode("utf-16-le", errors="ignore")
    return starts[position.line] + len(prefix)


def document_loader(ls):
    def load(uri):
        documents = getattr(ls.workspace, "text_documents", {})
        if isinstance(documents, dict):
            doc = documents.get(uri)
            if doc is not None and isinstance(doc.source, str):
                return doc.source
        return None

    return load


def context(ls, params):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    offset = document_offset(doc, params.position)
    return doc, offset


def at_cursor(ls, params, doc, offset):
    return analyze(doc.source, uri=params.text_document.uri, position_offset=offset, loader=document_loader(ls))


@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["{", "(", " "]))
def completions(ls: CMakeLanguageServer, params: CompletionParams):
    doc, offset = context(ls, params)
    if offset is None or in_comment(doc.source, offset):
        return CompletionList(is_incomplete=False, items=[])
    result = at_cursor(ls, params, doc, offset)
    before = doc.source[:offset]
    variable = re.search(r"\$([A-Za-z_]*)\{([A-Za-z0-9_.-]*)$", before)
    if variable:
        namespace = variable.group(1)
        definitions = VARIABLE_NAMESPACES.get(namespace, {})
        descriptions = dict(definitions)
        if namespace == "":
            descriptions.update({name: d.description for name, d in result.definitions.items()})
        return CompletionList(
            is_incomplete=False,
            items=[
                CompletionItem(label=name, kind=CompletionItemKind.Variable, documentation=markdown(desc))
                for name, desc in sorted(descriptions.items())
            ],
        )
    if before.endswith("$"):
        return CompletionList(
            is_incomplete=False,
            items=[CompletionItem(label=f"{ns}{{", kind=CompletionItemKind.Keyword) for ns in VARIABLE_NAMESPACES],
        )
    command, args = active_command(doc.source, offset)
    if command:
        name = command.name.lower()
        specs = command_overloads(name, result.commands.get(name))
        variables = set(BUILTIN_VARIABLES) | set(result.definitions)
        keywords = set()
        for overload in specs:
            keywords.update(overload.matcher.get_completions(args, variables))
        return CompletionList(
            is_incomplete=False,
            items=[
                CompletionItem(
                    label=word, kind=CompletionItemKind.Variable if word in variables else CompletionItemKind.EnumMember
                )
                for word in sorted(keywords)
            ],
        )
    items = {name: CompletionItem(label=name, kind=CompletionItemKind.Function) for name in ALL_COMMANDS}
    for name, d in result.commands.items():
        items[name] = CompletionItem(
            label=d.name, kind=CompletionItemKind.Function, documentation=markdown(d.description)
        )
    return CompletionList(is_incomplete=False, items=list(items.values()))


def word_at(source, offset):
    start, end = offset, offset
    while start > 0 and (source[start - 1].isalnum() or source[start - 1] in "_.-"):
        start -= 1
    while end < len(source) and (source[end].isalnum() or source[end] in "_.-"):
        end += 1
    return source[start:end]


def symbol_at(result, source, offset):
    word = word_at(source, offset)
    # Variable references and bare argument names use the variable namespace.
    line_start = source.rfind("\n", 0, offset) + 1
    line_end = source.find("\n", offset)
    line = source[line_start : line_end if line_end >= 0 else len(source)]
    for match in re.finditer(r"\$([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}", line):
        if match.start() <= offset - line_start <= match.end():
            return result.definitions.get(match.group(2)) if match.group(1) in ("", "CACHE") else None
    after = source[offset:]
    command_position = re.match(r"[A-Za-z0-9_.-]*\s*\(", after)
    if command_position:
        return result.commands.get(word.lower())
    return result.definitions.get(word) or result.commands.get(word.lower())


@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: CMakeLanguageServer, params: DefinitionParams):
    doc, offset = context(ls, params)
    if offset is None or in_comment(doc.source, offset):
        return None
    result = at_cursor(ls, params, doc, offset)
    d = symbol_at(result, doc.source, offset)
    if d is None:
        return None
    # Source columns are code points; convert them to protocol columns.
    target_source = doc.source if not d.uri or d.uri == params.text_document.uri else document_loader(ls)(d.uri)
    if target_source is None:
        from .analysis import path_from_uri

        target_path = path_from_uri(d.uri)
        try:
            target_source = target_path.read_text(encoding="utf-8-sig") if target_path is not None else ""
        except (OSError, UnicodeError):
            target_source = ""
    lines = target_source.splitlines()
    prefix = lines[d.line][: d.character] if d.line < len(lines) else ""
    character = len(prefix.encode("utf-16-le")) // 2
    return Location(
        uri=d.uri or params.text_document.uri,
        range=Range(
            start=Position(line=d.line, character=character),
            end=Position(line=d.line, character=character + len(d.name)),
        ),
    )


@server.feature(TEXT_DOCUMENT_SIGNATURE_HELP, SignatureHelpOptions(trigger_characters=["(", " ", ","]))
def signature_help(ls: CMakeLanguageServer, params: SignatureHelpParams):
    doc, offset = context(ls, params)
    if offset is None or in_comment(doc.source, offset):
        return None
    command, args = active_command(doc.source, offset)
    if command is None:
        return None
    result = at_cursor(ls, params, doc, offset)
    name = command.name.lower()
    d = result.commands.get(name)
    specs = command_overloads(name, d)
    signatures = [
        SignatureInformation(
            label=f"{d.name if d else command.name}({ov.signature})", documentation=markdown(ov.description)
        )
        for ov in specs
    ]
    if not signatures:
        signatures = [SignatureInformation(label=sig) for sig in COMMAND_SIGNATURES.get(name, [])]
    if not signatures:
        return None
    scores = []
    for ov in specs:
        states, _ = ov.matcher._walk(args)
        scores.append(max((score for score, _ in states.values()), default=-1))
    active = max(range(len(scores)), key=scores.__getitem__) if scores else 0
    return SignatureHelp(signatures=signatures, active_signature=active, active_parameter=0)


@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: CMakeLanguageServer, params: HoverParams):
    doc, offset = context(ls, params)
    if offset is None or in_comment(doc.source, offset):
        return None
    result = at_cursor(ls, params, doc, offset)
    d = symbol_at(result, doc.source, offset)
    if d:
        if d.kind in ("function", "macro"):
            content = "\n\n---\n\n".join(
                f"```cmake\n{d.name}({ov.signature})\n```\n\n{ov.description}" for ov in d.overloads
            )
        else:
            content = f"**{d.name}**\n\n{d.description or ''}"
        return Hover(contents=markdown(content))
    word = word_at(doc.source, offset)
    # Namespace variables retain their built-in documentation.
    for match in re.finditer(r"\$([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}", doc.source):
        if match.start() <= offset <= match.end():
            namespace, name = match.groups()
            desc = VARIABLE_NAMESPACES.get(namespace, {}).get(name)
            if desc:
                return Hover(contents=markdown(f"**${namespace}{{{name}}}**\n\n{desc}"))
    if word in BUILTIN_VARIABLES:
        return Hover(contents=markdown(f"**{word}**\n\n{BUILTIN_VARIABLES[word]}"))
    return None


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: CMakeLanguageServer, params: DidOpenTextDocumentParams):
    validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: CMakeLanguageServer, params: DidChangeTextDocumentParams):
    validate(ls, params.text_document.uri)
    # An edited annotation file may change any open consumer's diagnostics.
    documents = getattr(ls.workspace, "text_documents", {})
    if isinstance(documents, dict):
        for uri in list(documents):
            if uri != params.text_document.uri:
                validate(ls, uri)


def validate(ls: CMakeLanguageServer, uri: str):
    from .linting import lint_cmake

    doc = ls.workspace.get_text_document(uri)
    diagnostics = lint_cmake(doc.source, uri=uri, loader=document_loader(ls))
    ls.text_document_publish_diagnostics(PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics))
