import re
import os
from pathlib import Path

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
    INITIALIZE,
    WORKSPACE_DID_CHANGE_CONFIGURATION,
    WORKSPACE_DID_CHANGE_WATCHED_FILES,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_DID_CLOSE,
    MessageType,
    LogMessageParams,
)

from .analysis import analyze, command_overloads
from .syntax import active_command, in_comment, line_starts
from .options import AnnotationOptions, configuration
from .analysis import path_from_uri


class CMakeLanguageServer(LanguageServer):
    def __init__(self):
        super().__init__("cmake-ls", "0.1.0")
        self.annotation_defaults = AnnotationOptions()
        self.annotation_settings = {}
        self.annotation_roots = []
        self.annotation_warnings = set()
        self.watch_dependencies = False
        self.annotation_dependencies = set()

    def annotation_dependency(self, uri):
        if self.watch_dependencies and uri not in self.annotation_dependencies:
            self.annotation_dependencies.add(uri)
            self.protocol.notify("fleurdelys/watchDependency", {"uri": uri})

    def annotation_warning(self, message):
        if message not in self.annotation_warnings:
            self.annotation_warnings.add(message)
            self.window_log_message(LogMessageParams(type=MessageType.Warning, message=message))

    def analysis_options(self, uri):
        path = path_from_uri(uri)
        roots = []
        if path is not None:
            path = path.resolve()
            for root in self.annotation_roots:
                try:
                    path.relative_to(root)
                    roots.append(root)
                except ValueError:
                    pass
        base = max(roots, key=lambda root: len(root.parts)) if roots else None
        return configuration(self.annotation_settings, self.annotation_defaults, base, self.annotation_warning)


server = CMakeLanguageServer()


def analysis_arguments(ls, uri):
    if isinstance(ls, CMakeLanguageServer):
        return {"options": ls.analysis_options(uri), "report": ls.annotation_warning,
                "dependency": ls.annotation_dependency}
    return {}


@server.feature(INITIALIZE)
def initialize(ls, params):
    ls.annotation_settings = params.initialization_options or {}
    ls.watch_dependencies = isinstance(ls.annotation_settings, dict) and ls.annotation_settings.get("fleurdelysWatchDependencies") is True
    folders = params.workspace_folders or []
    uris = [folder.uri for folder in folders]
    if not uris and params.root_uri:
        uris = [params.root_uri]
    elif not uris and params.root_path:
        uris = [Path(params.root_path).resolve().as_uri()]
    ls.annotation_roots = [path_from_uri(uri).resolve() for uri in uris if path_from_uri(uri) is not None]


def revalidate_all(ls):
    documents = getattr(ls.workspace, "text_documents", {})
    for uri in list(documents):
        validate(ls, uri)


@server.feature(WORKSPACE_DID_CHANGE_CONFIGURATION)
def configuration_changed(ls, params):
    ls.annotation_settings = params.settings
    ls.annotation_warnings.clear()
    revalidate_all(ls)


def refresh_remembered_source(ls, uri):
    sources = getattr(ls, "_symbol_sources", {})
    if uri not in sources:
        return
    path = path_from_uri(uri)
    try:
        sources[uri] = path.read_text(encoding="utf-8-sig") if path else ""
    except (OSError, UnicodeError, ValueError):
        sources.pop(uri, None)


@server.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES)
def watched_files_changed(ls, params):
    ls.annotation_warnings.clear()
    for change in params.changes:
        refresh_remembered_source(ls, change.uri)
    revalidate_all(ls)


@server.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls, params):
    ls.annotation_warnings.clear()
    revalidate_all(ls)


@server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls, params):
    refresh_remembered_source(ls, params.text_document.uri)
    ls.annotation_warnings.clear()
    revalidate_all(ls)


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
            if doc is None:
                # Editor URIs may encode drive delimiters differently from
                # Path.as_uri(); still use the open buffer for the same file.
                target = path_from_uri(uri)
                if target is not None:
                    doc = next((item for key, item in documents.items()
                                if path_from_uri(key) == target), None)
            if doc is not None and isinstance(doc.source, str):
                return doc.source
        return None

    return load


def context(ls, params):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    offset = document_offset(doc, params.position)
    return doc, offset


def symbol_sources(ls, doc):
    sources = getattr(ls, "_symbol_sources", None)
    if not isinstance(sources, dict):
        sources = {}
        ls._symbol_sources = sources
    documents = getattr(ls.workspace, "text_documents", {})
    if isinstance(documents, dict):
        sources.update({uri: item.source for uri, item in documents.items() if isinstance(item.source, str)})
    sources[doc.uri] = doc.source
    return sources


def at_cursor(ls, params, doc, offset):
    loader = document_loader(ls)
    result = analyze(doc.source, uri=params.text_document.uri, position_offset=offset, loader=loader,
                     **analysis_arguments(ls, doc.uri))
    # Keep the last seen source of closed documents, but refresh live sources so
    # edits remove stale names. Symbols are independent of scopes and cursor position.
    for uri, source in symbol_sources(ls, doc).items():
        for namespace, symbols in analyze(source, uri=uri, loader=loader, **analysis_arguments(ls, uri)).source_symbols.items():
            result.symbols.setdefault(namespace, {}).update(symbols)
    return result


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
        definitions = result.variable_namespaces.get(namespace, {}) if namespace else result.definitions
        descriptions = {name: d.description for name, d in definitions.items()}
        if namespace == "ENV" and isinstance(ls, CMakeLanguageServer) and ls.analysis_options(doc.uri).expand_env_variable:
            for name in os.environ:
                descriptions.setdefault(name, None)
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
            items=[CompletionItem(label=f"{ns}{{", kind=CompletionItemKind.Keyword)
                   for ns in ["", *result.variable_namespaces]],
        )
    command, args = active_command(doc.source, offset)
    if command:
        name = command.name.lower()
        specs = command_overloads(name, result.commands.get(name))
        variables = set(result.definitions)
        keywords = set()
        for overload in specs:
            keywords.update(overload.matcher.get_completions(args, variables, result.symbols))
        return CompletionList(
            is_incomplete=False,
            items=[
                CompletionItem(
                    label=word, kind=CompletionItemKind.Variable if word in variables else CompletionItemKind.EnumMember
                )
                for word in sorted(keywords)
            ],
        )
    items = {}
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
            namespace, name = match.groups()
            if not namespace:
                return result.definitions.get(name)
            return result.variable_namespaces.get(namespace, {}).get(name)
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
    return None


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: CMakeLanguageServer, params: DidOpenTextDocumentParams):
    revalidate_all(ls)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: CMakeLanguageServer, params: DidChangeTextDocumentParams):
    if isinstance(ls, CMakeLanguageServer):
        ls.annotation_warnings.clear()
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
    symbol_sources(ls, doc)
    diagnostics = lint_cmake(doc.source, uri=uri, loader=document_loader(ls), **analysis_arguments(ls, uri))
    ls.text_document_publish_diagnostics(PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics))
