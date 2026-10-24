"""Annotation grammar and a nondeterministic matcher shared by all LSP features."""

import re
from dataclasses import dataclass, field
from typing import List


class SignatureElement:
    pass


@dataclass
class Literal(SignatureElement):
    value: str


@dataclass
class Choice(SignatureElement):
    choices: List[str]


@dataclass
class Placeholder(SignatureElement):
    name: str
    defines_variable: bool = False


@dataclass
class Group(SignatureElement):
    elements: List[SignatureElement]
    required: bool
    repeated: bool = False


class SignatureParser:
    def __init__(self, sig: str, legacy: bool = False):
        self.tokens = re.findall(r"\.\.\.|[<>\[\]|]|[^\s<>\[\]|]+?(?=\.\.\.|[\s<>\[\]|]|$)", sig)
        self.pos = 0
        self.legacy = legacy

    def parse(self):
        elements = self._sequence()
        if self.pos != len(self.tokens):
            raise ValueError("Unexpected closing delimiter")
        return elements

    def _sequence(self, closing=None, angle=False):
        elements = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token in (">", "]"):
                break
            self.pos += 1
            if token in ("<", "["):
                end = ">" if token == "<" else "]"
                inner = self._sequence(end, token == "<")
                if self.pos >= len(self.tokens) or self.tokens[self.pos] != end:
                    raise ValueError(f"Missing '{end}'")
                self.pos += 1
                if not inner:
                    raise ValueError("Empty signature group")
                element = Group(inner, token == "<")
            elif token in ("|", "..."):
                raise ValueError(f"Unexpected '{token}'")
            elif token.startswith(("?", "&")):
                if not re.fullmatch(r"[?&][A-Za-z_][A-Za-z0-9_.-]*", token):
                    raise ValueError("Invalid argument name")
                element = Placeholder(token[1:], token.startswith("&"))
            elif self.legacy and ((angle and "|" not in self.tokens[self.pos: self._closing_index()]) or not token.isupper()):
                element = Placeholder(token)
            else:
                element = Literal(token)

            if self.pos < len(self.tokens) and self.tokens[self.pos] == "|":
                if not isinstance(element, Literal):
                    raise ValueError("Alternatives must be literals")
                choices = [element.value]
                while self.pos < len(self.tokens) and self.tokens[self.pos] == "|":
                    self.pos += 1
                    if self.pos >= len(self.tokens):
                        raise ValueError("Missing alternative")
                    alternative = self.tokens[self.pos]
                    if alternative in ("<", ">", "[", "]", "|", "...") or alternative.startswith(("?", "&")):
                        raise ValueError("Alternatives must be literals")
                    choices.append(alternative)
                    self.pos += 1
                element = Choice(choices)

            if self.pos < len(self.tokens) and self.tokens[self.pos] == "...":
                if not isinstance(element, Group):
                    if not self.legacy:
                        raise ValueError("Repetition must follow '<...>' or '[...]'")
                    element = Group([element], True)
                if self._nullable(element.elements):
                    raise ValueError("A repeated group must consume an argument")
                element.repeated = True
                self.pos += 1
            elements.append(element)
        return elements

    def _closing_index(self):
        return next((i for i in range(self.pos, len(self.tokens)) if self.tokens[i] in (">", "]")), len(self.tokens))

    @staticmethod
    def _nullable(elements):
        return all(isinstance(e, Group) and (not e.required or SignatureParser._nullable(e.elements)) for e in elements)


def argument_value(arg):
    if arg.startswith('"') and arg.endswith('"'):
        return arg[1:-1]
    bracket = re.fullmatch(r"\[(=*)\[(.*)\]\1\]", arg, re.DOTALL)
    return bracket.group(2) if bracket else arg


def variable_candidate(arg):
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", arg))


def dynamic_argument(arg):
    if re.match(r"\[(=*)\[", arg):
        return False
    return bool(re.search(r"(?<!\\)\$(?:\{|[A-Za-z_]+\{)", arg))


@dataclass
class SignatureMatchResult:
    success: bool
    message: str = ""
    arg_index: int = -1
    score: int = 0
    definitions: set = field(default_factory=set)


class SignatureMatcher:
    def __init__(self, elements):
        self.elements = elements
        self.edges = {}
        self._next_state = 0
        self.start = self._state()
        self.end = self._state()
        self._compile(elements, self.start, self.end)

    def _state(self):
        state = self._next_state
        self._next_state += 1
        self.edges[state] = []
        return state

    def _compile(self, elements, start, end):
        current = start
        for i, element in enumerate(elements):
            target = end if i == len(elements) - 1 else self._state()
            if isinstance(element, Group):
                entry, exit = self._state(), self._state()
                self.edges[current].append((None, entry))
                self._compile(element.elements, entry, exit)
                self.edges[exit].append((None, target))
                if not element.required:
                    self.edges[current].append((None, target))
                if element.repeated:
                    self.edges[exit].append((None, entry))
            else:
                self.edges[current].append((element, target))
            current = target
        if not elements:
            self.edges[start].append((None, end))

    def _closure(self, states):
        states = dict(states)
        pending = list(states)
        while pending:
            state = pending.pop()
            score, definitions = states[state]
            for element, target in self.edges[state]:
                if element is None and self._merge(states, target, score, definitions):
                    pending.append(target)
        return states

    @staticmethod
    def _merge(states, target, score, definitions):
        old = states.get(target)
        if old is None or score > old[0]:
            states[target] = (score, frozenset(definitions))
            return True
        if score == old[0]:
            common = old[1].intersection(definitions)
            if common != old[1]:
                states[target] = (score, common)
                return True
        return False

    def _walk(self, args):
        states = self._closure({self.start: (0, frozenset())})
        for index, arg in enumerate(args):
            next_states = {}
            value = argument_value(arg)
            dynamic = dynamic_argument(arg)
            for state, (score, definitions) in states.items():
                for element, target in self.edges[state]:
                    if element is None:
                        continue
                    literal = isinstance(element, (Literal, Choice))
                    matches = isinstance(element, Placeholder) or dynamic
                    if isinstance(element, Literal):
                        matches = matches or value == element.value
                    elif isinstance(element, Choice):
                        matches = matches or value in element.choices
                    if matches:
                        effects = definitions
                        if isinstance(element, Placeholder) and element.defines_variable and variable_candidate(arg):
                            effects = definitions | {index}
                        self._merge(next_states, target, score + int(literal and not dynamic), effects)
            states = self._closure(next_states)
            if not states:
                return states, index
        return states, len(args)

    def match(self, args):
        states, index = self._walk(args)
        if self.end not in states:
            return SignatureMatchResult(False, "Signature mismatch", index)
        score, definitions = states[self.end]
        return SignatureMatchResult(True, score=score, definitions=set(definitions))

    def get_completions(self, args, variables=()):
        states, _ = self._walk(args)
        result = set()
        for state in states:
            for element, _ in self.edges[state]:
                if isinstance(element, Literal):
                    result.add(element.value)
                elif isinstance(element, Choice):
                    result.update(element.choices)
                elif isinstance(element, Placeholder) and element.defines_variable:
                    result.update(variables)
        return sorted(result)
