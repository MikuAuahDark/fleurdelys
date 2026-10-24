"""File-local annotation, include, scope and call analysis."""

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from .constants import BUILTIN_VARIABLES, COMMAND_SPECS, VARIABLE_NAMESPACES
from .signatures import SignatureParser, SignatureMatcher, argument_value, variable_candidate
from .syntax import Command, Comment, scan, line_starts, position
from .utils import Definition, ScopeTracker


@dataclass
class Overload:
    signature: str
    description: str
    matcher: SignatureMatcher
    uri: str | None = None
    line: int = 0
    character: int = 0


@dataclass
class Issue:
    uri: str
    line: int
    character: int
    message: str
    warning: bool = True


@dataclass
class Analysis:
    definitions: dict = field(default_factory=dict)
    commands: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)


@lru_cache(maxsize=256)
def make_matcher(signature, legacy=False):
    return SignatureMatcher(SignatureParser(signature, legacy=legacy).parse())


def command_overloads(name, definition=None):
    if definition and definition.kind in ("function", "macro"):
        return definition.overloads
    return [
        Overload(ov["sig"], ov["desc"], make_matcher(ov["sig"], True)) for ov in COMMAND_SPECS.get(name.lower(), [])
    ]


def path_from_uri(uri):
    if not uri:
        return None
    parsed = urlparse(uri)
    if parsed.scheme == "file":
        path = url2pathname(parsed.path)
        if parsed.netloc:
            path = "//" + parsed.netloc + path
        return Path(path)
    if len(parsed.scheme) <= 1:
        return Path(uri)
    return None


def analyze(source, uri=None, position_line=None, loader=None, position_offset=None):
    result = Analysis()
    tracker = ScopeTracker()
    visiting, imported, declarations = set(), set(), set()

    def issue(file_uri, starts, offset, message, warning=True):
        line, character = position(starts, offset)
        result.issues.append(Issue(file_uri, line, character, message, warning))

    def definition(name, kind, event, starts, file_uri, description=None):
        offset = event.start
        if isinstance(event, Command) and event.args:
            offset = event.args[0].start
        line, character = position(starts, offset)
        return Definition(name, line, character, kind, description=description, uri=file_uri)

    def expand(value, file_uri):
        current_path = path_from_uri(file_uri)

        def substitute(match):
            name = match.group(1)
            if current_path and name == "CMAKE_CURRENT_LIST_DIR":
                return str(current_path.parent)
            if current_path and name == "CMAKE_CURRENT_LIST_FILE":
                return str(current_path)
            found = tracker.lookup(name)
            return found.value if found and found.value is not None else match.group(0)

        for _ in range(10):
            replacement = re.sub(r"\$\{([^{}]+)\}", substitute, value)
            if replacement == value:
                break
            value = replacement
        return value

    def include(args, event, starts, file_uri):
        if not args:
            issue(file_uri, starts, event.start, "include() requires a path.")
            return
        target = expand(argument_value(args[0]), file_uri)
        current_path = path_from_uri(file_uri)
        if "$" in target or current_path is None:
            return
        try:
            path = Path(target)
            if not path.is_absolute():
                path = current_path.parent / path
            path = path.resolve()
            target_uri = path.as_uri()
        except (OSError, ValueError):
            issue(file_uri, starts, event.start, f"Invalid include path '{target}'.")
            return
        key = (target_uri, tracker.current)
        if target_uri in visiting or key in imported:
            return
        try:
            content = loader(target_uri) if loader else None
            if content is None:
                content = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError, ValueError):
            if "OPTIONAL" not in args:
                issue(file_uri, starts, event.start, f"Cannot read included file '{target}'.")
            return
        imported.add(key)
        visit(content, target_uri)

    def add_annotation(payload, description, event, starts, file_uri):
        match = re.fullmatch(r"\s*(function|set|include)\s*\((.*)\)\s*", payload, re.IGNORECASE)
        if not match:
            issue(file_uri, starts, event.start, "Malformed annotation declaration.")
            return
        command, body = match.group(1).lower(), match.group(2)
        if command == "include":
            parsed = next(iter(scan("include(" + body + ")")), None)
            if not isinstance(parsed, Command) or not parsed.complete:
                issue(file_uri, starts, event.start, "Malformed include annotation.")
                return
            include([a.text for a in parsed.args], event, starts, file_uri)
            return
        if command == "set":
            parsed = next(iter(scan("set(" + body + ")")), None)
            if not isinstance(parsed, Command) or not parsed.complete:
                issue(file_uri, starts, event.start, "Malformed variable annotation.")
                return
            args = [a.text for a in parsed.args]
            if not args or not variable_candidate(args[0]):
                issue(file_uri, starts, event.start, "Variable annotation requires a literal variable name.")
                return
            d = definition(args[0], "variable", event, starts, file_uri, description)
            d.line, d.character = position(starts, event.payload_start + payload.find(args[0], payload.find("(")))
            d.value = argument_value(args[1]) if len(args) == 2 else None
            tracker.set_variable(d.name, d)
            return
        name_match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_.-]*)(?:\s+(.*?))?\s*", body)
        if not name_match:
            issue(file_uri, starts, event.start, "Function annotation requires a name.")
            return
        name, signature = name_match.group(1), name_match.group(2) or ""
        try:
            matcher = make_matcher(signature)
        except (ValueError, RecursionError) as error:
            issue(file_uri, starts, event.start, f"Malformed function annotation: {error}")
            return
        key = (file_uri, event.start, tracker.current)
        if key in declarations:
            return
        declarations.add(key)
        previous = tracker.current.commands.get(name.lower())
        if previous is None or not previous.signatures:
            d = definition(name, "function", event, starts, file_uri, description)
            d.line, d.character = position(starts, event.payload_start + payload.find(name, payload.find("(")))
            if previous is not None:
                d.line, d.character, d.uri = previous.line, previous.character, previous.uri
            tracker.current.commands[name.lower()] = d
        else:
            d = previous
        d.signatures.append(signature)
        line, character = position(starts, event.start)
        d.overloads.append(Overload(signature, description, matcher, file_uri, line, character))

    def visit(text, file_uri, limit=None):
        visiting.add(file_uri)
        starts = line_starts(text)
        pending, previous_end = [], None
        blocks = []
        for event in scan(text):
            if limit is not None and event.start >= limit:
                break
            if previous_end is not None and text[previous_end : event.start].count("\n") > 1:
                pending = []
            previous_end = event.end
            if isinstance(event, Comment):
                if event.ignored:
                    continue
                if not event.annotation:
                    pending = []
                    continue
                if re.match(r"\s*(?:function|set|include)\s*\(", event.text, re.IGNORECASE):
                    add_annotation(event.text, "\n".join(pending), event, starts, file_uri)
                    pending = []
                else:
                    pending.append(event.text)
                continue
            description = "\n".join(pending) if pending else None
            pending = []
            cmd = event.name.lower()
            if cmd != "set":
                description = None
            args = [a.text for a in event.args]
            values = [argument_value(a) for a in args]
            # Variable references are checked before the command's effects.
            for token in event.args:
                if re.match(r"\[(=*)\[", token.text):
                    continue
                for match in re.finditer(r"(?<!\\)\$([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}", token.text):
                    namespace, name = match.groups()
                    if namespace not in VARIABLE_NAMESPACES:
                        issue(
                            file_uri,
                            starts,
                            token.start + match.start(),
                            f"Unknown variable namespace '{namespace}'.",
                            False,
                        )
                    elif namespace == "" and not tracker.is_defined(name) and name not in BUILTIN_VARIABLES:
                        issue(file_uri, starts, token.start + match.start(), f"Variable '{name}' may be undefined.")
            if not event.complete or (limit is not None and event.end > limit):
                continue
            specs = command_overloads(cmd, tracker.command(cmd))
            matches = [ov.matcher.match(args) for ov in specs]
            matches = [m for m in matches if m.success]
            if specs and not matches:
                issue(file_uri, starts, event.start, f"Invalid arguments for '{event.name}'.", False)
            if matches:
                score = max(m.score for m in matches)
                best = [m.definitions for m in matches if m.score == score]
                effects = set.intersection(*best)
                for index in effects:
                    name = args[index]
                    if name not in tracker.current.variables:
                        token = event.args[index]
                        line, character = position(starts, token.start)
                        tracker.set_variable(name, Definition(name, line, character, "variable", uri=file_uri))

            if cmd == "include":
                include(args, event, starts, file_uri)
            elif cmd == "set" and args and variable_candidate(args[0]):
                d = definition(args[0], "variable", event, starts, file_uri, description)
                d.value = expand(values[1], file_uri) if len(values) == 2 else None
                parent = len(args) > 1 and args[-1] == "PARENT_SCOPE"
                destination = tracker.stack[-2] if parent and len(tracker.stack) > 1 else tracker.current
                old = destination.variables.get(d.name)
                if old and d.description is None:
                    d.description = old.description
                tracker.set_variable(d.name, d, parent_scope=parent)
            elif cmd == "unset" and args and variable_candidate(args[0]):
                tracker.unset_variable(args[0], parent_scope=len(args) > 1 and args[-1] == "PARENT_SCOPE")
            elif cmd in ("function", "macro") and args:
                name = values[0]
                existing = tracker.command(name)
                d = definition(name, cmd, event, starts, file_uri, description)
                d.args = values[1:]
                if existing and existing.signatures:
                    # Keep the public annotation, but navigate to its implementation.
                    existing.line, existing.character, existing.uri = d.line, d.character, d.uri
                else:
                    signature = " ".join(f"<?{arg}>" for arg in d.args)
                    try:
                        d.overloads = [Overload(signature, description or "", make_matcher(signature))]
                    except ValueError:
                        d.overloads = []
                    tracker.current.commands[name.lower()] = d
                if cmd == "function":
                    tracker.push_scope()
                    tracker.push_implicit_args(d.line, d.character)
                else:
                    tracker.push_macro_args(values[1:], d.line, d.character)
                for token, arg in zip(event.args[1:], values[1:]):
                    line, character = position(starts, token.start)
                    tracker.set_variable(arg, Definition(arg, line, character, "argument", uri=file_uri))
            elif cmd == "endfunction":
                tracker.pop_scope()
            elif cmd == "endmacro":
                tracker.pop_macro_args()
            elif cmd in ("block", "foreach"):
                tracker.push_scope()
                if cmd == "foreach" and args and variable_candidate(args[0]):
                    tracker.set_variable(args[0], definition(args[0], "variable", event, starts, file_uri))
            elif cmd in ("endblock", "endforeach"):
                tracker.pop_scope()
            elif cmd == "cmake_minimum_required" and "VERSION" in values:
                index = values.index("VERSION") + 1
                if index < len(values):
                    match = re.match(r"^(\d+)\.(\d+)", values[index])
                    if match and tuple(map(int, match.groups())) < (3, 5):
                        issue(
                            file_uri,
                            starts,
                            event.start,
                            "CMake 4.0 policy requires cmake_minimum_required version to be at least 3.5.",
                            False,
                        )

            if cmd in ("if", "while", "foreach", "function", "macro", "block"):
                blocks.append((cmd, event.start))
            elif cmd in ("endif", "endwhile", "endforeach", "endfunction", "endmacro", "endblock"):
                expected = cmd[3:]
                if not blocks:
                    issue(file_uri, starts, event.start, f"'{cmd}' without matching opening block.", False)
                elif blocks[-1][0] != expected:
                    issue(
                        file_uri,
                        starts,
                        event.start,
                        f"'{cmd}' encountered, but expected end of '{blocks[-1][0]}'.",
                        False,
                    )
                else:
                    blocks.pop()
        if limit is None:
            for name, offset in blocks:
                issue(file_uri, starts, offset, f"Unclosed block '{name}'.", False)
        visiting.discard(file_uri)

    limit = position_offset
    if position_line is not None:
        starts = line_starts(source)
        limit = starts[position_line] if position_line < len(starts) else len(source)
    visit(source, uri, limit)
    result.definitions = tracker.all_visible_variables()
    result.commands = tracker.all_visible_commands()
    return result
