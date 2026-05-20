import re
from typing import List, Optional, Tuple, Union


class SignatureMatchResult:
    def __init__(self, success: bool, message: str = "", arg_index: int = -1):
        self.success = success
        self.message = message
        self.arg_index = arg_index


class SignatureElement:
    pass


class Literal(SignatureElement):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return self.value


class Choice(SignatureElement):
    def __init__(self, choices: List[str]):
        self.choices = choices

    def __repr__(self):
        return "|".join(self.choices)


class Placeholder(SignatureElement):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"<{self.name}>"


class Group(SignatureElement):
    def __init__(
        self, elements: List[SignatureElement], required: bool, repeated: bool = False
    ):
        self.elements = elements
        self.required = required
        self.repeated = repeated

    def __repr__(self):
        inner = " ".join(map(str, self.elements))
        if self.repeated:
            inner += " ..."
        return f"<{inner}>" if self.required else f"[{inner}]"


class SignatureParser:
    def __init__(self, sig: str):
        # Normalize: ensure spaces around punctuation for easy splitting
        # But | should stay with its neighbors if they are literals
        sig = re.sub(r"([\[\]<>])", r" \1 ", sig)
        self.tokens = sig.split()
        self.pos = 0

    def parse(self) -> List[SignatureElement]:
        elements = []
        while self.pos < len(self.tokens):
            elements.append(self.parse_element())
        return elements

    def parse_element(self, in_placeholder_group: bool = False) -> SignatureElement:
        token = self.tokens[self.pos]
        if token == "[":
            self.pos += 1
            inner = []
            while self.pos < len(self.tokens) and self.tokens[self.pos] != "]":
                inner.append(self.parse_element(in_placeholder_group))

            repeated = False
            if self.pos < len(self.tokens) and self.tokens[self.pos] == "]":
                self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos] == "...":
                    repeated = True
                    self.pos += 1

            return Group(inner, required=False, repeated=repeated)

        elif token == "<":
            self.pos += 1
            inner = []
            while self.pos < len(self.tokens) and self.tokens[self.pos] != ">":
                inner.append(self.parse_element(True))

            repeated = False
            if self.pos < len(self.tokens) and self.tokens[self.pos] == ">":
                self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos] == "...":
                    repeated = True
                    self.pos += 1

            # Match at least once if inner is a Choice
            if len(inner) == 1 and isinstance(inner[0], Choice):
                return Group(inner, required=True, repeated=repeated)

            return Group(inner, required=True, repeated=repeated)

        elif "|" in token:
            self.pos += 1
            return Choice(token.split("|"))

        else:
            self.pos += 1
            # Check for repetition
            if self.pos < len(self.tokens) and self.tokens[self.pos] == "...":
                self.pos += 1
                return Group(
                    [
                        (
                            Placeholder(token)
                            if (in_placeholder_group or not token.isupper())
                            else Literal(token)
                        )
                    ],
                    required=True,
                    repeated=True,
                )

            if in_placeholder_group or not token.isupper():
                return Placeholder(token)
            return Literal(token)


class SignatureMatcher:
    def __init__(self, elements: List[SignatureElement]):
        self.elements = elements

    def match(self, args: List[str]) -> SignatureMatchResult:
        success, next_arg_idx = self._match_group(self.elements, args, 0)
        if not success:
            return SignatureMatchResult(False, "Signature mismatch", next_arg_idx)

        if next_arg_idx < len(args):
            return SignatureMatchResult(False, "Too many arguments", next_arg_idx)

        return SignatureMatchResult(True)

    def _match_group(
        self, elements: List[SignatureElement], args: List[str], arg_idx: int
    ) -> Tuple[bool, int]:
        current_arg_idx = arg_idx
        for i, el in enumerate(elements):
            if isinstance(el, Group) and el.repeated:
                # Match at least once if required
                matched_once = False

                # Lookahead for anchoring: if the NEXT element in the signature
                # is a Literal or Choice that MUST match, we should stop repeating
                # when we hit it.
                next_el = elements[i + 1] if i + 1 < len(elements) else None

                while current_arg_idx < len(args):
                    if next_el and matched_once:
                        # If next element matches, and it's a Literal/Choice, stop greedily consuming
                        if isinstance(
                            next_el, (Literal, Choice)
                        ) and self._match_element(next_el, args[current_arg_idx]):
                            break
                        # Also stop if next_el is a required group that matches
                        if isinstance(next_el, Group) and next_el.required:
                            success_next, _ = self._match_group(
                                next_el.elements, args, current_arg_idx
                            )
                            if success_next:
                                break

                    success, next_idx = self._match_group(
                        el.elements, args, current_arg_idx
                    )
                    if success:
                        matched_once = True
                        current_arg_idx = next_idx
                    else:
                        break

                if el.required and not matched_once:
                    return False, current_arg_idx
            elif isinstance(el, Group):
                success, next_idx = self._match_group(
                    el.elements, args, current_arg_idx
                )
                if success:
                    current_arg_idx = next_idx
                elif el.required:
                    return False, current_arg_idx
            else:
                if current_arg_idx >= len(args):
                    return False, current_arg_idx

                success = self._match_element(el, args[current_arg_idx])
                if success:
                    current_arg_idx += 1
                else:
                    return False, current_arg_idx

        return True, current_arg_idx

    def _match_element(self, el: SignatureElement, arg: str) -> bool:
        # Ignore variable references in validation
        if arg.startswith("${") and arg.endswith("}"):
            return True

        if isinstance(el, Literal):
            return arg.upper() == el.value.upper()
        elif isinstance(el, Choice):
            return arg.upper() in [c.upper() for c in el.choices]
        elif isinstance(el, Placeholder):
            return True
        return False

    def get_completions(self, args: List[str]) -> List[str]:
        completions = set()
        self._collect_completions(self.elements, args, 0, completions)
        return sorted(list(completions))

    def _collect_completions(
        self,
        elements: List[SignatureElement],
        args: List[str],
        arg_idx: int,
        completions: set,
    ):
        if arg_idx > len(args):
            return

        current_arg_idx = arg_idx
        for i, el in enumerate(elements):
            if current_arg_idx == len(args):
                # We are at the position where we need suggestions
                self._add_element_completions(el, completions)
                # If this element is not required, we also need to look at the next element
                if isinstance(el, Group) and not el.required:
                    continue
                else:
                    return

            # Try to match current argument
            if isinstance(el, Group):
                if el.repeated:
                    # Match multiple times
                    while current_arg_idx < len(args):
                        # Use lookahead if needed, but for completions we just try to move forward
                        success, next_idx = self._match_group(
                            el.elements, args, current_arg_idx
                        )
                        if success:
                            if next_idx == len(args):
                                # We matched exactly up to here, so we could repeat this group
                                # or move to the next element
                                self._add_element_completions(el, completions)
                                # Continue to next element because this one might be finished
                                current_arg_idx = next_idx
                                break
                            current_arg_idx = next_idx
                        else:
                            break
                    # If we broke out, continue to next element
                else:
                    success, next_idx = self._match_group(
                        el.elements, args, current_arg_idx
                    )
                    if success:
                        current_arg_idx = next_idx
                    elif el.required:
                        return
                    else:
                        # Optional group didn't match, skip to next element
                        continue
            else:
                if current_arg_idx >= len(args):
                    return
                if self._match_element(el, args[current_arg_idx]):
                    current_arg_idx += 1
                else:
                    # Mismatch
                    return

    def _add_element_completions(self, el: SignatureElement, completions: set):
        if isinstance(el, Literal):
            completions.add(el.value)
        elif isinstance(el, Choice):
            for c in el.choices:
                completions.add(c)
        elif isinstance(el, Group):
            # The first possible literals of a group
            for inner_el in el.elements:
                self._add_element_completions(inner_el, completions)
                if isinstance(inner_el, Group) and not inner_el.required:
                    continue
                if isinstance(inner_el, Placeholder):
                    # Placeholder doesn't give completion but might allow next element
                    continue
                break
