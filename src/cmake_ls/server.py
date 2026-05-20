from pygls.lsp.server import LanguageServer
import re
from .constants import (
    ALL_COMMANDS,
    BUILTIN_VARIABLES,
    COMMAND_SPECS,
    VARIABLE_NAMESPACES,
    COMMAND_SIGNATURES,
)
from .utils import extract_definitions, is_in_comment
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionParams,
    CompletionList,
    CompletionItem,
    CompletionItemKind,
    CompletionOptions,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_SIGNATURE_HELP,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    PublishDiagnosticsParams,
    SignatureHelpParams,
    SignatureHelp,
    SignatureInformation,
    SignatureHelpOptions,
    TEXT_DOCUMENT_DEFINITION,
    DefinitionParams,
    Location,
    Range,
    Position,
    TEXT_DOCUMENT_HOVER,
    HoverParams,
    Hover,
    MarkupContent,
    MarkupKind,
)


class CMakeLanguageServer(LanguageServer):
    def __init__(self):
        super().__init__("cmake-ls", "0.1.0")


server = CMakeLanguageServer()


@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["{"]))
def completions(ls: CMakeLanguageServer, params: CompletionParams):
    """
    Provide completion for CMake commands and variables.
    """
    doc = ls.workspace.get_text_document(params.text_document.uri)

    # Hide suggestions in comments
    if is_in_comment(doc.source, params.position.line, params.position.character):
        return CompletionList(is_incomplete=False, items=[])

    line = doc.lines[params.position.line]
    before_cursor = line[: params.position.character]

    match = re.search(r"([A-Za-z0-9_]+)\s*\(\s*(.*)$", before_cursor)
    if match:
        cmd_name = match.group(1).lower()
        args_str = match.group(2)
        # Parse arguments (basic splitting)
        args = re.findall(r"\"[^\"]*\"|\S+", args_str)
        # If it doesn't end with a space, we are completing the last argument
        # unless there are no arguments yet.
        if args and not args_str.endswith(" "):
            # We are completing the current last arg, so we need suggestions for its position
            args = args[:-1]

        items = []
        if cmd_name in COMMAND_SPECS:
            from .signatures import SignatureParser, SignatureMatcher

            all_keywords = set()
            for ov in COMMAND_SPECS[cmd_name]:
                parser = SignatureParser(ov["sig"])
                elements = parser.parse()
                matcher = SignatureMatcher(elements)
                keywords = matcher.get_completions(args)
                for k in keywords:
                    all_keywords.add(k)

            items = [
                CompletionItem(label=k, kind=CompletionItemKind.EnumMember)
                for k in sorted(list(all_keywords))
            ]

        # If no keywords found, maybe it's just a general command or custom function
        if not items:
            # Check if it was an empty call string( -> suggest subcommands
            if not args and cmd_name in COMMAND_SPECS:
                # This should have been caught by get_completions but let's be safe
                pass

        if items:
            return CompletionList(is_incomplete=False, items=items)

    # Check for $NAMESPACE{PREFIX
    var_match = re.search(r"\$([A-Za-z_]*)\{([A-Za-z0-9_.-]*)$", before_cursor)

    if var_match:
        namespace = var_match.group(1)
        # prefix = var_match.group(2) # not strictly needed for lsprotocol CompletionList unless filtering

        from .constants import VARIABLE_NAMESPACES

        if namespace not in VARIABLE_NAMESPACES:
            return CompletionList(is_incomplete=False, items=[])

        items = []
        if namespace == "":
            # Standard scoped + built-in variables
            defs = extract_definitions(doc.source, params.position.line)
            for name, d in defs.items():
                if d.kind in ("variable", "argument"):
                    items.append(
                        CompletionItem(
                            label=name,
                            kind=CompletionItemKind.Variable,
                            documentation=d.description if d.description else None,
                        )
                    )
            # Add built-ins
            for name, desc in BUILTIN_VARIABLES.items():
                items.append(
                    CompletionItem(
                        label=name,
                        kind=CompletionItemKind.Variable,
                        documentation=desc,
                        detail="Built-in variable",
                    )
                )
        else:
            # Other namespaces (ENV, CACHE)
            for name, desc in VARIABLE_NAMESPACES[namespace].items():
                items.append(
                    CompletionItem(
                        label=name,
                        kind=CompletionItemKind.Variable,
                        documentation=desc,
                        detail=f"{namespace} variable",
                    )
                )
        return CompletionList(is_incomplete=False, items=items)

    # Check for $ at the end to suggest namespaces
    if before_cursor.endswith("$"):
        from .constants import VARIABLE_NAMESPACES

        items = []
        for ns in VARIABLE_NAMESPACES.keys():
            if ns == "":
                items.append(CompletionItem(label="{", kind=CompletionItemKind.Keyword))
            else:
                items.append(
                    CompletionItem(label=f"{ns}{{", kind=CompletionItemKind.Keyword)
                )
        return CompletionList(is_incomplete=False, items=items)

    # Command completion (default)
    items = []
    # Add standard commands
    for cmd in ALL_COMMANDS:
        items.append(CompletionItem(label=cmd, kind=CompletionItemKind.Function))

    # Add custom functions and macros
    defs = extract_definitions(doc.source, params.position.line)
    for name, d in defs.items():
        if d.kind in ("function", "macro"):
            kind = (
                CompletionItemKind.Function
                if d.kind == "function"
                else CompletionItemKind.Snippet
            )
            items.append(
                CompletionItem(
                    label=name,
                    kind=kind,
                    documentation=d.description if d.description else None,
                )
            )

    return CompletionList(is_incomplete=False, items=items)


@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: CMakeLanguageServer, params: DefinitionParams):
    """
    Go to definition for variables and functions.
    """
    doc = ls.workspace.get_text_document(params.text_document.uri)
    line = doc.lines[params.position.line]

    # Find the word under cursor
    # This is a bit basic: look for variable ${VAR} or command(

    # 1. Check for variable usage $NAMESPACE{VAR}
    # We look at the line and find the variable around the cursor
    var_matches = re.finditer(r"\$([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}", line)
    for match in var_matches:
        if match.start() <= params.position.character <= match.end():
            namespace = match.group(1)
            var_name = match.group(2)

            # Scoped variables only in empty namespace
            if namespace == "":
                defs = extract_definitions(doc.source, params.position.line)
                if var_name in defs:
                    d = defs[var_name]
                    return Location(
                        uri=params.text_document.uri,
                        range=Range(
                            start=Position(line=d.line, character=d.character),
                            end=Position(
                                line=d.line, character=d.character + len(d.name)
                            ),
                        ),
                    )
            elif namespace == "CACHE":
                # Check for CACHE variable definitions
                defs = extract_definitions(doc.source, params.position.line)
                if var_name in defs:
                    d = defs[var_name]
                    return Location(
                        uri=params.text_document.uri,
                        range=Range(
                            start=Position(line=d.line, character=d.character),
                            end=Position(
                                line=d.line, character=d.character + len(d.name)
                            ),
                        ),
                    )

    # 2. Check for function/macro call: func(
    # Or just the word itself if it's a command
    word_match = re.search(
        r"([A-Za-z0-9_.-]+)",
        line[params.position.character - 20 : params.position.character + 20],
    )
    # Better approach: find the full word at position

    # Let's use a simpler "word at position"
    pos = params.position.character
    start = pos
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] in "_.-"):
        start -= 1
    end = pos
    while end < len(line) and (line[end].isalnum() or line[end] in "_.-"):
        end += 1

    word = line[start:end]
    if word:
        defs = extract_definitions(doc.source, params.position.line)
        # Check case-insensitive for functions/macros
        if word.lower() in defs:
            d = defs[word.lower()]
            return Location(
                uri=params.text_document.uri,
                range=Range(
                    start=Position(line=d.line, character=d.character),
                    end=Position(line=d.line, character=d.character + len(d.name)),
                ),
            )

    return None


@server.feature(
    TEXT_DOCUMENT_SIGNATURE_HELP, SignatureHelpOptions(trigger_characters=["(", ","])
)
def signature_help(ls: CMakeLanguageServer, params: SignatureHelpParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)

    # Guard against IndexError: doc.lines is a tuple and might be out of sync
    if params.position.line >= len(doc.lines):
        return None

    # Hide signature help in comments
    if is_in_comment(doc.source, params.position.line, params.position.character):
        return None

    # We need to find the command we are currently in.
    # We look backwards from the cursor for the nearest "command("
    # that hasn't been closed yet.

    offset = doc.offset_at_position(params.position)
    source_before = doc.source[:offset]

    # Simplified approach: find the last occurrence of something that looks like a command start
    # We search for "name(" and then check if it's closed before the cursor.
    # Note: this doesn't handle nested calls perfectly but should be better than what we had.

    # Finding all command starts: [a-zA-Z0-9_]+\s*\(
    matches = list(re.finditer(r"([A-Za-z0-9_]+)\s*\(", source_before))
    if not matches:
        return None

    # Iterate backwards from the last match
    for match in reversed(matches):
        cmd_name = match.group(1).lower()
        if cmd_name not in COMMAND_SIGNATURES:
            continue

        # Check if this command is closed before the cursor
        start_index = match.end()
        content_after_open = source_before[start_index:]

        # Count parentheses to see if we are still inside
        paren_balance = 1
        is_closed = False
        for char in content_after_open:
            if char == "(":
                paren_balance += 1
            elif char == ")":
                paren_balance -= 1
            if paren_balance == 0:
                is_closed = True
                break

        if not is_closed:
            # We are inside this command!
            signatures = []

            # 1. Check if it's a custom function/macro from extract_definitions
            defs = extract_definitions(doc.source, params.position.line)
            if cmd_name in defs:
                d = defs[cmd_name]
                if d.kind in ("function", "macro"):
                    if d.signatures:
                        for s in d.signatures:
                            signatures.append(
                                SignatureInformation(
                                    label=f"{cmd_name}({s})",
                                    documentation=MarkupContent(
                                        kind=MarkupKind.Markdown,
                                        value=d.description or f"Custom {d.kind}",
                                    ),
                                )
                            )
                    else:
                        # Fallback: create signature from args
                        sig_str = " ".join(d.args) if d.args else ""
                        signatures.append(
                            SignatureInformation(
                                label=f"{cmd_name}({sig_str})",
                                documentation=MarkupContent(
                                    kind=MarkupKind.Markdown,
                                    value=d.description or f"Custom {d.kind}",
                                ),
                            )
                        )

            # 2. Check built-in commands
            if not signatures:
                if cmd_name in COMMAND_SPECS:
                    for ov in COMMAND_SPECS[cmd_name]:
                        signatures.append(
                            SignatureInformation(
                                label=f"{cmd_name}({ov['sig']})",
                                documentation=MarkupContent(
                                    kind=MarkupKind.Markdown, value=ov["desc"]
                                ),
                            )
                        )
                elif cmd_name in COMMAND_SIGNATURES:
                    signatures = [
                        SignatureInformation(label=sig)
                        for sig in COMMAND_SIGNATURES[cmd_name]
                    ]

            if signatures:
                return SignatureHelp(
                    signatures=signatures, active_signature=0, active_parameter=0
                )

    return None


@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: CMakeLanguageServer, params: HoverParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    line = doc.lines[params.position.line]

    # Find word at position
    pos = params.position.character
    start = pos
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] in "_.-"):
        start -= 1
    end = pos
    while end < len(line) and (line[end].isalnum() or line[end] in "_.-"):
        end += 1

    word = line[start:end]

    # Check for variable usage with namespace: $NS{VAR}
    from .constants import VARIABLE_NAMESPACES

    var_matches = re.finditer(r"\$([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}", line)
    for match in var_matches:
        if match.start() <= params.position.character <= match.end():
            namespace = match.group(1)
            var_name = match.group(2)

            if (
                namespace in VARIABLE_NAMESPACES
                and var_name in VARIABLE_NAMESPACES[namespace]
            ):
                label = f"${namespace}{{{var_name}}}"
                return Hover(
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=f"**{label}**\n\n{VARIABLE_NAMESPACES[namespace][var_name]}",
                    )
                )

    if word in BUILTIN_VARIABLES:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"**{word}**\n\n{BUILTIN_VARIABLES[word]}",
            )
        )

    return None


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: CMakeLanguageServer, params: DidOpenTextDocumentParams):
    validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: CMakeLanguageServer, params: DidChangeTextDocumentParams):
    validate(ls, params.text_document.uri)


def validate(ls: CMakeLanguageServer, uri: str):
    from .linting import lint_cmake

    doc = ls.workspace.get_text_document(uri)
    diagnostics = lint_cmake(doc.source)
    ls.text_document_publish_diagnostics(
        PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
    )
