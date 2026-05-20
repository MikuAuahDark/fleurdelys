import re
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Range,
    Position,
)


from cmake_ls.constants import COMMAND_SPECS, BUILTIN_VARIABLES
from cmake_ls.signatures import SignatureParser, SignatureMatcher
from cmake_ls.utils import ScopeTracker, Definition


def lint_cmake(source: str):
    diagnostics = []
    lines = source.splitlines()

    # State
    initial_defs = {
        name: Definition(name=name, line=-1, character=-1, kind="variable")
        for name in BUILTIN_VARIABLES
    }
    tracker = ScopeTracker(globals=initial_defs)

    control_stack = []  # Stack of (command, start_line_index)

    # Regex to capture command start: name(
    cmd_start_regex = re.compile(r"^\s*([A-Za-z0-9_]+)\s*\(", re.IGNORECASE)

    # Regex to capture variable usage: $NAMESPACE{VAR}
    var_usage_regex = re.compile(r"\$([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}")

    # Simplified argument tokenizer for multi-line support would be better,
    # but for now we follow the existing line-by-line pattern.
    # We capture everything inside (...)
    args_regex = re.compile(r"\((.*)\)", re.IGNORECASE)

    # Check cmake_minimum_required
    found_min_req = False
    in_bracket_comment = False
    bracket_level = 0

    # Cache for parsed matchers
    matcher_cache = {}

    # Meta command state
    pending_signatures = []
    last_line_comment = None
    custom_command_specs = {}  # cmd_name -> list of specs

    for i, line in enumerate(lines):
        # Check for meta commands first
        meta_match = re.match(r"^\s*##cmake-ls:\s*(.*)$", line)
        if meta_match:
            cmd_payload = meta_match.group(1).strip()
            if cmd_payload.startswith("define "):
                var_spec = cmd_payload[len("define ") :].strip()
                ns_match = re.match(
                    r"^([A-Za-z_]*)\{([A-Za-z0-9_.-]+)\}$|([A-Za-z0-9_.-]+)", var_spec
                )
                if ns_match:
                    namespace = ns_match.group(1) or ""
                    var_name = ns_match.group(2) or ns_match.group(3)
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
                cmd_payload_split = cmd_payload.split()
                if len(cmd_payload_split) > 0:
                    meta_command = cmd_payload_split[0]
                else:
                    meta_command = ""

                diagnostics.append(
                    Diagnostic(
                        range=Range(
                            start=Position(line=i, character=line.find("##cmake-ls:")),
                            end=Position(line=i, character=len(line)),
                        ),
                        message=f"Unknown meta command '{meta_command}'.",
                        severity=DiagnosticSeverity.Warning,
                    )
                )
            last_line_comment = None
            continue

        # Regular line processing
        line_content = ""
        j = 0
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
                    break  # Rest of line is comment

                line_content += line[j]
                j += 1
            else:
                # Inside bracket comment, look for closing: ]=]
                closing_pattern = f']{"=" * bracket_level}]'
                found_closing = line.find(closing_pattern, j)
                if found_closing != -1:
                    in_bracket_comment = False
                    j = found_closing + len(closing_pattern)
                else:
                    break  # Rest of line is inside comment

        if not line_content.strip():
            continue

        # Check minimum required
        if "cmake_minimum_required" in line_content.lower():
            match = re.search(r"VERSION\s+([0-9.]+)", line_content, re.IGNORECASE)
            if match:
                version_str = match.group(1)
                try:
                    ver = float(version_str)
                    if ver < 3.5:
                        diagnostics.append(
                            Diagnostic(
                                range=Range(
                                    start=Position(line=i, character=0),
                                    end=Position(line=i, character=len(line)),
                                ),
                                message=f"CMake 4.0 policy requires cmake_minimum_required version to be at least 3.5 (current: {ver})",
                                severity=DiagnosticSeverity.Error,
                            )
                        )
                except ValueError:
                    pass  # Complex version string ignored for now
            found_min_req = True

        # Check variable usages
        for match in var_usage_regex.finditer(line_content):
            namespace = match.group(1)
            var_name = match.group(2)

            from cmake_ls.constants import VARIABLE_NAMESPACES

            if namespace not in VARIABLE_NAMESPACES:
                diagnostics.append(
                    Diagnostic(
                        range=Range(
                            start=Position(line=i, character=match.start()),
                            end=Position(line=i, character=match.end()),
                        ),
                        message=f"Unknown variable namespace '{namespace}'.",
                        severity=DiagnosticSeverity.Error,
                    )
                )
            elif namespace == "":
                if not tracker.is_defined(var_name):
                    diagnostics.append(
                        Diagnostic(
                            range=Range(
                                start=Position(line=i, character=match.start()),
                                end=Position(line=i, character=match.end()),
                            ),
                            message=f"Variable '{var_name}' may be undefined.",
                            severity=DiagnosticSeverity.Warning,
                        )
                    )
            # For other namespaces (ENV, CACHE), we don't warn about unknown variables yet
            # because we don't have an exhaustive list and they are often user-defined.

        # Command Validation with Signatures
        cmd_match = cmd_start_regex.search(line_content)
        if cmd_match:
            cmd = cmd_match.group(1).lower()
            cmd_start_pos = cmd_match.start(1)

            # Extract arguments for both validation and scoping
            args = []
            args_match = args_regex.search(line_content, cmd_match.start())
            if args_match:
                args_str = args_match.group(1)
                tokens = re.findall(r"\"[^\"]*\"|\S+", args_str)
                args = [t.strip("\"'") for t in tokens]

            # Handle scoping before validation (to catch PARENT_SCOPE and args)
            if cmd == "set" and args:
                var_name = args[0]
                parent_scope = "PARENT_SCOPE" in args
                tracker.set_variable(
                    var_name,
                    Definition(
                        name=var_name,
                        line=i,
                        character=cmd_start_pos,
                        kind="variable",
                        description=last_line_comment,
                    ),
                    parent_scope=parent_scope,
                )
            elif cmd == "unset" and args:
                var_name = args[0]
                parent_scope = "PARENT_SCOPE" in args
                tracker.unset_variable(var_name, parent_scope=parent_scope)

            # Check if this command should consume pending signatures
            if cmd in ("function", "macro"):
                if pending_signatures:
                    if args:
                        target_name = args[0].lower()
                        custom_command_specs[target_name] = [
                            {"sig": sig, "desc": f"Custom {cmd}"}
                            for sig in pending_signatures
                        ]
                        pending_signatures = []
                # Define func/macro (always, even without signature)
                if args:
                    target_name = args[0]
                    kind = "function" if cmd == "function" else "macro"
                    tracker.set_variable(
                        target_name.lower(),
                        Definition(
                            name=target_name,
                            line=i,
                            character=cmd_start_pos,
                            kind=kind,
                            description=last_line_comment,
                            args=args[1:],
                        ),
                    )
                    if cmd == "function":
                        tracker.push_scope()
                        tracker.push_implicit_args(i, cmd_start_pos)
                    else:
                        tracker.push_macro_args(args[1:], i, cmd_start_pos)

                    # Define args for local scope
                    for arg in args[1:]:
                        tracker.set_variable(
                            arg,
                            Definition(
                                name=arg,
                                line=i,
                                character=cmd_start_pos,
                                kind="argument",
                            ),
                        )
            else:
                # Any other command consumes pending signatures with a warning
                if pending_signatures:
                    diagnostics.append(
                        Diagnostic(
                            range=Range(
                                start=Position(line=i, character=0),
                                end=Position(line=i, character=len(line)),
                            ),
                            message="Signature override must be followed by function or macro.",
                            severity=DiagnosticSeverity.Warning,
                        )
                    )
                    pending_signatures = []

            if cmd == "endfunction":
                tracker.pop_scope()
            elif cmd == "endmacro":
                tracker.pop_macro_args()
            elif cmd == "block":
                tracker.push_scope()
            elif cmd == "endblock":
                tracker.pop_scope()

            # Command Validation
            specs = custom_command_specs.get(cmd) or COMMAND_SPECS.get(cmd)
            if not specs:
                # If not in built-in or custom overridden specs, check if it's a known custom function/macro
                # and generate a spec for it.
                d = tracker.lookup(cmd)
                if d and d.kind in ("function", "macro"):
                    sig_str = " ".join([f"<{a}>" for a in d.args])
                    specs = [{"sig": sig_str, "desc": f"Custom {d.kind}"}]

            if specs:
                if args_match:
                    tokens = args  # reuse extracted args
                    matched = False
                    errors = []

                    for ov in specs:
                        sig_str = ov["sig"]
                        if sig_str not in matcher_cache:
                            parser = SignatureParser(sig_str)
                            matcher_cache[sig_str] = SignatureMatcher(parser.parse())

                        matcher = matcher_cache[sig_str]
                        res = matcher.match(tokens)
                        if res.success:
                            matched = True
                            break
                        else:
                            errors.append(res.message)

                    if not matched:
                        # If multiple overloads exist, just say signature mismatch.
                        # If one, we can be more specific.
                        msg = f"Invalid arguments for '{cmd}'."
                        if len(errors) == 1:
                            msg = f"Invalid arguments: {errors[0]}"

                        diagnostics.append(
                            Diagnostic(
                                range=Range(
                                    start=Position(line=i, character=cmd_start_pos),
                                    end=Position(line=i, character=args_match.end()),
                                ),
                                message=msg,
                                severity=DiagnosticSeverity.Error,
                            )
                        )
            last_line_comment = None

            # Block counting
            if cmd in ["if", "while", "foreach", "function", "macro", "block"]:
                control_stack.append((cmd, i))

            # Close blocks
            elif cmd == "endif":
                _check_pop(control_stack, "if", i, diagnostics, "endif")
            elif cmd == "endwhile":
                _check_pop(control_stack, "while", i, diagnostics, "endwhile")
            elif cmd == "endforeach":
                _check_pop(control_stack, "foreach", i, diagnostics, "endforeach")
            elif cmd == "endfunction":
                _check_pop(control_stack, "function", i, diagnostics, "endfunction")
            elif cmd == "endmacro":
                _check_pop(control_stack, "macro", i, diagnostics, "endmacro")
            elif cmd == "endblock":
                _check_pop(control_stack, "block", i, diagnostics, "endblock")

    # End of file checks
    for cmd, start_line in control_stack:
        diagnostics.append(
            Diagnostic(
                range=Range(
                    start=Position(line=start_line, character=0),
                    end=Position(line=start_line, character=10),
                ),
                message=f"Unclosed block '{cmd}' (started at line {start_line + 1})",
                severity=DiagnosticSeverity.Error,
            )
        )

    return diagnostics


def _check_pop(stack, expected_cmd, current_line, diagnostics, close_cmd):
    if not stack:
        diagnostics.append(
            Diagnostic(
                range=Range(
                    start=Position(line=current_line, character=0),
                    end=Position(line=current_line, character=len(close_cmd)),
                ),
                message=f"'{close_cmd}' without matching opening block.",
                severity=DiagnosticSeverity.Error,
            )
        )
        return

    last_cmd, _ = stack[-1]
    if last_cmd == expected_cmd:
        stack.pop()
    else:
        # Mismatch
        diagnostics.append(
            Diagnostic(
                range=Range(
                    start=Position(line=current_line, character=0),
                    end=Position(line=current_line, character=len(close_cmd)),
                ),
                message=f"'{close_cmd}' encountered, but expected end of '{last_cmd}'.",
                severity=DiagnosticSeverity.Error,
            )
        )
