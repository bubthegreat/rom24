"""Minimal C-initializer parsing: comments, #defines, balanced-brace table extraction."""
import re


def strip_comments(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i : j + 1])
            i = j + 1
        elif text.startswith("/*", i):
            i = text.index("*/", i) + 2
        elif text.startswith("//", i):
            i = text.index("\n", i) if "\n" in text[i:] else n
        else:
            out.append(c)
            i += 1
    return "".join(out)


def parse_defines(text: str) -> dict:
    defines = {}
    for m in re.finditer(r"^[ \t]*#define[ \t]+(\w+)[ \t]+(.+?)[ \t]*$",
                         strip_comments(text), re.MULTILINE):
        defines[m.group(1)] = m.group(2).strip()
    return defines


def extract_initializer(text: str, name: str) -> str:
    text = strip_comments(text)
    m = re.search(re.escape(name) + r"(?:\s*\[[^\]]*\])+\s*=\s*\{", text)
    if not m:
        raise ValueError(f"initializer for {name!r} not found")
    start = m.end() - 1  # at the '{'
    depth, i = 0, start
    while i < len(text):
        c = text[i]
        if c == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
        i += 1
    raise ValueError(f"unbalanced braces in {name!r}")


def parse_braces(block: str):
    """block starts at '{' and ends at matching '}'. Returns nested lists;
    C strings -> ('str', value) tuples; other tokens -> stripped strings."""
    pos = [1]  # skip opening '{'

    def parse_list():
        items, token = [], []
        last_was_string = False

        def flush():
            nonlocal last_was_string
            tok = "".join(token).strip()
            token.clear()
            if tok:
                items.append(tok)
            last_was_string = False

        while True:
            c = block[pos[0]]
            if c == '"':
                chars, j = [], pos[0] + 1
                while block[j] != '"':
                    if block[j] == "\\":
                        chars.append({"n": "\n", "r": "\r", "t": "\t"}.get(block[j + 1], block[j + 1]))
                        j += 2
                    else:
                        chars.append(block[j])
                        j += 1
                # adjacent C string literals concatenate (only if last item was also a string, not after comma)
                if items and isinstance(items[-1], tuple) and not "".join(token).strip() and last_was_string:
                    # Pending whitespace in token is deliberately left for next flush() to discard
                    items[-1] = ("str", items[-1][1] + "".join(chars))
                else:
                    flush()
                    items.append(("str", "".join(chars)))
                    last_was_string = True
                pos[0] = j + 1
            elif c == "{":
                flush()
                pos[0] += 1
                items.append(parse_list())
            elif c == "}":
                flush()
                pos[0] += 1
                return items
            elif c == ",":
                flush()
                pos[0] += 1
            else:
                token.append(c)
                pos[0] += 1

    return parse_list()
