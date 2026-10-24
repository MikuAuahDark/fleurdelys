from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Definition:
    name: str
    line: int
    character: int
    kind: str
    description: Optional[str] = None
    args: List[str] = field(default_factory=list)
    signatures: List[str] = field(default_factory=list)
    overloads: list = field(default_factory=list)
    uri: Optional[str] = None
    value: Optional[str] = None


class Scope:
    def __init__(self, parent=None):
        self.variables = {}
        self.commands = {}
        self.parent = parent
        self.macro_stack = []


class ScopeTracker:
    def __init__(self, globals=None):
        self.stack = [Scope()]
        if globals:
            self.current.variables.update(globals)

    @property
    def current(self):
        return self.stack[-1]

    def push_scope(self):
        self.stack.append(Scope(self.current))

    def pop_scope(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def push_implicit_args(self, line, character):
        for arg in ("ARGC", "ARGV", "ARGN"):
            self.current.variables[arg] = Definition(arg, line, character, "argument")

    def push_macro_args(self, args, line, character):
        names = list(args) + ["ARGC", "ARGV", "ARGN"]
        self.current.macro_stack.append({name: self.current.variables.get(name) for name in names})
        for name in names:
            self.current.variables[name] = Definition(name, line, character, "argument")

    def pop_macro_args(self):
        if self.current.macro_stack:
            for name, previous in self.current.macro_stack.pop().items():
                if previous is None:
                    self.current.variables.pop(name, None)
                else:
                    self.current.variables[name] = previous

    def set_variable(self, name, definition, parent_scope=False):
        if parent_scope:
            if len(self.stack) > 1:
                self.stack[-2].variables[name] = definition
        else:
            self.current.variables[name] = definition

    def unset_variable(self, name, parent_scope=False):
        if parent_scope:
            if len(self.stack) > 1:
                self.stack[-2].variables.pop(name, None)
        else:
            self.current.variables.pop(name, None)

    def lookup(self, name):
        for scope in reversed(self.stack):
            if name in scope.variables:
                return scope.variables[name]
        return None

    def command(self, name):
        for scope in reversed(self.stack):
            if name.lower() in scope.commands:
                return scope.commands[name.lower()]
        return None

    def is_defined(self, name):
        return self.lookup(name) is not None

    def all_visible_variables(self):
        result = {}
        for scope in self.stack:
            result.update(scope.variables)
        return result

    def all_visible_commands(self):
        result = {}
        for scope in self.stack:
            result.update(scope.commands)
        return result


def extract_definitions(source, position_line=None, uri=None, loader=None):
    from .analysis import analyze

    result = analyze(source, uri=uri, position_line=position_line, loader=loader)
    return {**result.commands, **result.definitions}


def is_in_comment(source, line_index, character_index):
    from .syntax import in_comment, line_starts

    starts = line_starts(source)
    if line_index >= len(starts):
        return False
    return in_comment(source, starts[line_index] + character_index)
