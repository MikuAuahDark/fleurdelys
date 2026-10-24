"""Small, lossless CMake scanner; quoted text and bracket comments stay opaque."""

import re
from bisect import bisect_right
from dataclasses import dataclass


@dataclass
class Token:
    text: str
    start: int
    end: int


@dataclass
class Command:
    name: str
    args: list
    start: int
    opening: int
    end: int
    complete: bool


@dataclass
class Comment:
    text: str
    start: int
    end: int
    annotation: bool
    ignored: bool = False
    payload_start: int = 0


def line_starts(source):
    return [0] + [m.end() for m in re.finditer("\n", source)]


def position(starts, offset):
    line = bisect_right(starts, offset) - 1
    return line, offset - starts[line]


def _opaque_end(source, start):
    if source[start] == '"':
        i = start + 1
        while i < len(source):
            if source[i] == "\\":
                i += 2
            elif source[i] == '"':
                return i + 1
            else:
                i += 1
        return len(source)
    bracket = re.match(r"\[(=*)\[", source[start:])
    if bracket:
        end = source.find("]" + bracket.group(1) + "]", start + bracket.end())
        return len(source) if end < 0 else end + len(bracket.group(1)) + 2
    return None


def comment_end(source, start):
    bracket_end = _opaque_end(source, start + 1) if re.match(r"#\[(=*)\[", source[start:]) else None
    if bracket_end is not None:
        return bracket_end
    end = source.find("\n", start)
    return len(source) if end < 0 else end


def scan(source):
    """Yield top-level commands and full-line comments, including unfinished calls."""
    i = 0
    while i < len(source):
        if source[i] == "#":
            end = comment_end(source, i)
            full_line = not source[source.rfind("\n", 0, i) + 1:i].strip()
            if full_line:
                text = source[i:end].rstrip("\r")
                annotation = bool(re.match(r"##(?!#)", text))
                payload = text[2:]
                if payload.startswith(" "):
                    payload = payload[1:]
                prefix_length = 3 if text.startswith("## ") else 2
                yield Comment(payload, i, end, annotation, text.startswith("###"), i + prefix_length)
            i = end
            continue
        opaque = _opaque_end(source, i)
        if opaque is not None:
            i = opaque
            continue
        match = re.match(r"([A-Za-z_][A-Za-z0-9_.-]*)\s*\(", source[i:])
        if match:
            start, opening = i, i + match.end() - 1
            name = match.group(1)
            i = opening + 1
            depth, token_start, args = 1, None, []
            while i < len(source):
                char = source[i]
                if char == "#":
                    if token_start is not None:
                        args.append(Token(source[token_start:i], token_start, i))
                        token_start = None
                    i = comment_end(source, i)
                    continue
                if char.isspace() and depth == 1:
                    if token_start is not None:
                        args.append(Token(source[token_start:i], token_start, i))
                        token_start = None
                    i += 1
                    continue
                if char == ")" and depth == 1:
                    if token_start is not None:
                        args.append(Token(source[token_start:i], token_start, i))
                    i += 1
                    depth = 0
                    break
                if token_start is None:
                    token_start = i
                opaque = _opaque_end(source, i)
                if opaque is not None:
                    i = opaque
                    continue
                if char == "\\":
                    i = min(len(source), i + 2)
                    continue
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                i += 1
            if depth and token_start is not None:
                args.append(Token(source[token_start:i], token_start, i))
            yield Command(name, args, start, opening, i, depth == 0)
            continue
        i += 1


def active_command(source, offset):
    """Return the unfinished command and fully entered arguments at a cursor."""
    events = list(scan(source[:offset]))
    if not events or not isinstance(events[-1], Command) or events[-1].complete:
        return None, []
    command = events[-1]
    args = command.args
    if args and args[-1].end == offset:
        args = args[:-1]
    return command, [a.text for a in args]


def in_comment(source, offset):
    i = 0
    while i < min(len(source), offset + 1):
        if source[i] == "#":
            end = comment_end(source, i)
            bracket = re.match(r"#\[(=*)\[", source[i:])
            if i <= offset < end or (offset == end and not bracket):
                return True
            i = end
        else:
            opaque = _opaque_end(source, i)
            if opaque is not None:
                i = opaque
            elif source[i] == "\\":
                i += 2
            else:
                i += 1
    return False
