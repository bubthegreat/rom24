import ast
import re


class Resolver:
    def __init__(self, defines: dict):
        self.defines = defines

    def num(self, token: str) -> int:
        expr = str(token)
        for _ in range(len(self.defines) + 1):
            names = set(re.findall(r"[A-Za-z_]\w*", expr))
            subst = {n: self.defines[n] for n in names if n in self.defines}
            if not subst:
                break
            for n, v in subst.items():
                expr = re.sub(rf"\b{n}\b", f"({v})", expr)
        else:
            raise ValueError(f"circular #define expansion in {token!r}")
        expr = re.sub(r"'(.)'", lambda m: str(ord(m.group(1))), expr)
        node = ast.parse(expr, mode="eval")
        for sub in ast.walk(node):
            if not isinstance(sub, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                                    ast.BitOr, ast.BitAnd, ast.LShift, ast.RShift, ast.Add,
                                    ast.Sub, ast.Mult, ast.USub, ast.Invert)):
                raise ValueError(f"unsupported C expr: {token!r}")
        return eval(compile(node, "<cexpr>", "eval"))  # noqa: S307 - AST-whitelisted

    def value(self, token):
        if isinstance(token, tuple) and token[0] == "str":
            return token[1]
        if token == "TRUE":
            return True
        if token == "FALSE":
            return False
        return self.num(token)

    def slot(self, token: str) -> int:
        tok = str(token).strip()
        m = re.fullmatch(r"SLOT\s*\((.*)\)", tok)
        return self.num((m.group(1) if m else tok).strip())

    def gsn_name(self, token: str):
        m = re.fullmatch(r"&\s*gsn_(\w+)", str(token).strip())
        return m.group(1) if m else None

    def spell_name(self, token: str):
        tok = str(token).strip()
        if tok in ("NULL", "0", "spell_null"):
            return None
        m = re.fullmatch(r"spell_(\w+)", tok)
        return m.group(1).replace("_", " ") if m else None
