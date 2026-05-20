import re


from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Definition:
    name: str
    line: int
    character: int
    kind: str  # "variable", "function", "macro", or "argument"
    description: Optional[str] = None
    args: List[str] = field(default_factory=list)
    signatures: List[str] = field(default_factory=list)


class Scope:
    def __init__(self, parent: Optional["Scope"] = None):
        self.variables: dict[str, Definition] = {}
        self.parent = parent
        # For macros, arguments shadow variables but are not true variables.
        # We store the old definitions to restore them when the macro scope ends.
        self.macro_stack: list[dict[str, Optional[Definition]]] = []


class ScopeTracker:
    def __init__(self, globals: Optional[dict[str, Definition]] = None):
        self.stack = [Scope()]
        if globals:
            self.stack[0].variables.update(globals)

    @property
    def current(self) -> Scope:
        return self.stack[-1]

    def push_scope(self):
        self.stack.append(Scope(self.current))

    def pop_scope(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def push_implicit_args(self, line: int, character: int):
        for arg in ["ARGC", "ARGV", "ARGN"]:
            self.current.variables[arg] = Definition(
                name=arg, line=line, character=character, kind="argument"
            )

    def push_macro_args(self, args: list[str], line: int, character: int):
        old_defs = {}
        # Include implicit args in macro stack
        all_args = args + ["ARGC", "ARGV", "ARGN"]
        for arg in all_args:
            # Store old definition if it exists
            old_defs[arg] = self.current.variables.get(arg)
            # Define it as an argument
            self.current.variables[arg] = Definition(
                name=arg, line=line, character=character, kind="argument"
            )
        self.current.macro_stack.append(old_defs)

    def pop_macro_args(self):
        if self.current.macro_stack:
            old_defs = self.current.macro_stack.pop()
            for name, old_def in old_defs.items():
                if old_def is None:
                    if name in self.current.variables:
                        del self.current.variables[name]
                else:
                    self.current.variables[name] = old_def

    def set_variable(
        self, name: str, definition: Definition, parent_scope: bool = False
    ):
        if parent_scope:
            if len(self.stack) > 1:
                self.stack[-2].variables[name] = definition
            # Do nothing if at file scope
        else:
            self.current.variables[name] = definition

    def unset_variable(self, name: str, parent_scope: bool = False):
        if parent_scope:
            if len(self.stack) > 1:
                if name in self.stack[-2].variables:
                    del self.stack[-2].variables[name]
            # Do nothing if at file scope
        else:
            if name in self.current.variables:
                del self.current.variables[name]

    def lookup(self, name: str) -> Optional[Definition]:
        # Check macro args first (shadowing)
        # Note: In our current simplified tracker, we put them in variables too.
        # But we need to handle the "leakage" correctly.

        curr: Optional[Scope] = self.current
        while curr is not None:
            if name in curr.variables:
                return curr.variables[name]
            curr = curr.parent
        return None

    def is_defined(self, name: str) -> bool:
        return self.lookup(name) is not None

    def all_visible_variables(self) -> dict[str, Definition]:
        res = {}
        # Iterate from root to current to let inner scopes override outer
        for scope in self.stack:
            res.update(scope.variables)
        return res


def extract_definitions(source: str, position_line: Optional[int] = None):
    """
    Scans the source code for variable, function, and macro definitions.

    If position_line is provided, only considers definitions appearing
    BEFORE that line.
    """
    tracker = ScopeTracker()

    lines = source.splitlines()
    limit = len(lines)
    if position_line is not None:
        limit = min(limit, position_line)

    # Regex patterns
    # We need more sophisticated argument extraction for function/macro
    cmd_pattern = re.compile(r"([A-Za-z0-9_.-]+)\s*\(([^)]*)\)", re.IGNORECASE)

    in_bracket_comment = False
    bracket_level = 0

    # For capturing descriptions and signatures
    last_line_comment = None
    pending_signatures = []

    for i in range(limit):
        line = lines[i]
        j = 0

        # Check for meta commands first
        meta_match = re.match(r"^\s*##cmake-ls:\s*(.*)$", line)
        if meta_match:
            cmd_payload = meta_match.group(1).strip()
            if cmd_payload.startswith("define "):
                var_spec = cmd_payload[len("define ") :].strip()
                # Check for NS{VAR}
                ns_match = re.match(
                    r"^([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}$|([A-Za-z0-9_.-]+)", var_spec
                )
                if ns_match:
                    namespace = ns_match.group(1) or ""
                    var_name = ns_match.group(2) or ns_match.group(3)

                    # Only handle default namespace for extract_definitions usually,
                    # but let's support others if they are specified clearly.
                    if namespace == "":
                        tracker.set_variable(
                            var_name,
                            Definition(
                                name=var_name,
                                line=i,
                                character=line.find(var_name),
                                kind="variable",
                                description=last_line_comment,
                            ),
                        )
            elif cmd_payload.startswith("signature "):
                sig_text = cmd_payload[len("signature ") :].strip()
                pending_signatures.append(sig_text)
            else:
                last_line_comment = None  # Reset for unknown meta commands
            continue

        while j < len(line):
            if not in_bracket_comment:
                # Check for start of bracket comment
                bracket_match = re.match(r"#\[(=*)\[", line[j:])
                if bracket_match:
                    in_bracket_comment = True
                    bracket_level = len(bracket_match.group(1))
                    j += bracket_match.end()
                    last_line_comment = None
                    continue

                # Check for line comment
                if line[j] == "#":
                    # Capture line comment as potential description for NEXT thing
                    comment_text = line[j + 1 :].strip()
                    if not comment_text.startswith("#cmake-ls:"):
                        last_line_comment = comment_text
                    break  # Skip rest of line

                # Try to match a command call
                match = cmd_pattern.match(line[j:])
                if match:
                    cmd_name = match.group(1).lower()
                    args_raw = match.group(2)
                    args = re.findall(r"\"[^\"]*\"|\S+", args_raw)
                    args = [t.strip("\"'") for t in args]

                    if cmd_name == "set":
                        if args:
                            var_name = args[0]
                            parent_scope = "PARENT_SCOPE" in args
                            tracker.set_variable(
                                var_name,
                                Definition(
                                    name=var_name,
                                    line=i,
                                    character=line.find(var_name, j),
                                    kind="variable",
                                    description=last_line_comment,
                                ),
                                parent_scope=parent_scope,
                            )
                    elif cmd_name == "unset":
                        if args:
                            var_name = args[0]
                            parent_scope = "PARENT_SCOPE" in args
                            tracker.unset_variable(var_name, parent_scope=parent_scope)
                    elif cmd_name == "function":
                        if args:
                            func_name = args[0]
                            func_args = args[1:]
                            tracker.set_variable(
                                func_name.lower(),
                                Definition(
                                    name=func_name,
                                    line=i,
                                    character=line.find(func_name, j),
                                    kind="function",
                                    description=last_line_comment,
                                    args=func_args,
                                    signatures=pending_signatures.copy(),
                                ),
                            )
                            pending_signatures = []
                            tracker.push_scope()
                            tracker.push_implicit_args(i, line.find(func_name, j))
                            if len(args) > 1:
                                for arg in args[1:]:
                                    tracker.set_variable(
                                        arg,
                                        Definition(
                                            name=arg,
                                            line=i,
                                            character=line.find(arg, j),
                                            kind="argument",
                                        ),
                                    )
                    elif cmd_name == "endfunction":
                        tracker.pop_scope()
                    elif cmd_name == "macro":
                        if args:
                            macro_name = args[0]
                            macro_args = args[1:]
                            tracker.set_variable(
                                macro_name.lower(),
                                Definition(
                                    name=macro_name,
                                    line=i,
                                    character=line.find(macro_name, j),
                                    kind="macro",
                                    description=last_line_comment,
                                    args=macro_args,
                                    signatures=pending_signatures.copy(),
                                ),
                            )
                            pending_signatures = []
                            if len(args) > 1:
                                tracker.push_macro_args(
                                    args[1:], i, line.find(args[1], j)
                                )
                    elif cmd_name == "endmacro":
                        tracker.pop_macro_args()
                    elif cmd_name == "foreach":
                        if args:
                            loop_var = args[0]
                            tracker.push_scope()
                            tracker.set_variable(
                                loop_var,
                                Definition(
                                    name=loop_var,
                                    line=i,
                                    character=line.find(loop_var, j),
                                    kind="variable",  # loop vars behave like variables
                                ),
                            )
                    elif cmd_name == "endforeach":
                        tracker.pop_scope()
                    elif cmd_name == "block":
                        tracker.push_scope()
                    elif cmd_name == "endblock":
                        tracker.pop_scope()

                    last_line_comment = None
                    pending_signatures = []
                    j += match.end()
                    continue

                j += 1
            else:
                # Inside bracket comment, look for closing: ]=]
                closing_pattern = f']{"=" * bracket_level}]'
                found_closing = line.find(closing_pattern, j)
                if found_closing != -1:
                    in_bracket_comment = False
                    j = found_closing + len(closing_pattern)
                else:
                    break  # Rest of line is comment

    return tracker.all_visible_variables()


def is_in_comment(source: str, line_index: int, character_index: int) -> bool:
    """
    Determines if a given position is within a comment (line or bracket).
    """
    lines = source.splitlines()
    if line_index >= len(lines):
        return False

    # Check for line comment on the current line first
    current_line = lines[line_index]

    # We need to be careful with bracket comments that span multiple lines
    # Let's do a full scan of the source up to the position to be accurate

    in_bracket_comment = False
    bracket_level = 0

    for i in range(line_index + 1):
        line = lines[i]
        j = 0
        while j < len(line):
            if i == line_index and j >= character_index:
                return in_bracket_comment

            if not in_bracket_comment:
                # Start of line comment?
                if line[j] == "#":
                    # Check for bracket comment start: #[[ or #[=[
                    bracket_match = re.match(r"#\[(=*)\[", line[j:])
                    if bracket_match:
                        in_bracket_comment = True
                        bracket_level = len(bracket_match.group(1))
                        j += bracket_match.end()
                        continue
                    else:
                        # Simple line comment
                        if i == line_index:
                            return True
                        break  # Rest of line is comment
                j += 1
            else:
                # Inside bracket comment, look for closing: ]=]
                closing_pattern = f']{"=" * bracket_level}]'
                found_closing = line.find(closing_pattern, j)
                if found_closing != -1:
                    if (
                        i == line_index
                        and found_closing + len(closing_pattern) > character_index
                    ):
                        return True
                    in_bracket_comment = False
                    j = found_closing + len(closing_pattern)
                else:
                    if i == line_index:
                        return True
                    break  # Still in bracket comment for rest of line

    return False
