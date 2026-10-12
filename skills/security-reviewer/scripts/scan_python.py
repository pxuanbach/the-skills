#!/usr/bin/env python3
"""
scan_python.py - Built-in AST security scanner for Python / FastAPI code (stdlib `ast` only).

Rules: SQL injection via f-string/format/concat, shell injection, eval/exec, unsafe
deserialization (pickle, yaml.load), weak hashes and non-crypto random for secrets,
JWT decode without verification, permissive CORS, debug mode, TLS verify off,
secrets in logs, HTML responses built from strings, and FastAPI routes without an
auth dependency (route, router, include_router or app level).

Usage (standalone):
    python scan_python.py <dir-or-file> [...]      # prints findings as JSON
Normally called by run_scan.py with the project's profile settings.
"""

import ast
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_common import finding, is_test_path, line_text, read_text  # noqa: E402
from plan_scan import glob_match  # noqa: E402

SQL_SINKS = {"execute", "executemany", "executescript", "exec_driver_sql", "text", "raw", "mogrify"}
SUBPROCESS = {"run", "call", "Popen", "check_output", "check_call", "getoutput", "getstatusoutput"}
DESERIALIZE = {"pickle.loads", "pickle.load", "cPickle.loads", "marshal.loads", "dill.loads", "jsonpickle.decode"}
RANDOM_FUNCS = {"random", "randint", "randrange", "choice", "choices", "getrandbits", "sample"}
ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "api_route", "websocket"}
MUTATING = {"post", "put", "patch", "delete", "api_route"}
SECRETISH = re.compile(r"(?i)token|secret|passw|otp|nonce|salt|api_?key|session|reset_code")
SENSITIVE_NAME = re.compile(r"(?i)password|passwd|secret|token|api_?key|authorization|credit_?card|ssn")
DEFAULT_AUTH_PATTERN = r"(?i)auth|current_user|jwt|bearer|token|permission|require_|verify_"


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return dotted(node.func)
    return ""


def kwarg(call, name):
    return next((k.value for k in call.keywords if k.arg == name), None)


def is_const(node, value):
    return isinstance(node, ast.Constant) and node.value is value


def is_dynamic_str(node):
    """f-string with placeholders, "..." % x, "..." + x, or "...".format(x)."""
    if isinstance(node, ast.JoinedStr):
        return any(isinstance(v, ast.FormattedValue) for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mod, ast.Add)):
        sides = (node.left, node.right)
        has_str = any(isinstance(s, ast.Constant) and isinstance(s.value, str) or is_dynamic_str(s) for s in sides)
        has_var = any(not isinstance(s, ast.Constant) for s in sides)
        return has_str and has_var
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        return isinstance(node.func.value, ast.Constant) and bool(node.args or node.keywords)
    return False


class AuthIndex:
    """Project-wide facts gathered before the per-file pass."""

    def __init__(self, is_auth):
        self.is_auth = is_auth
        self.protected_modules = set()   # module stems mounted with include_router(..., dependencies=[auth])
        self.app_protected = False       # FastAPI(dependencies=[auth]) somewhere

    def deps_have_auth(self, node):
        for call in (n for n in ast.walk(node) if isinstance(n, ast.Call)):
            if dotted(call.func).rsplit(".", 1)[-1] in ("Depends", "Security") and call.args:
                if self.is_auth(dotted(call.args[0])):
                    return True
        return False

    def collect(self, tree):
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                stem = node.module.rsplit(".", 1)[-1]
                for a in node.names:
                    # `from app.routers import items` -> items; `from .items import router as r` -> items
                    aliases[a.asname or a.name] = a.name if a.name != "router" else stem
            if not isinstance(node, ast.Call):
                continue
            name = dotted(node.func)
            deps = kwarg(node, "dependencies")
            if name.endswith("include_router") and node.args and deps is not None and self.deps_have_auth(deps):
                head = dotted(node.args[0]).split(".")[0]
                self.protected_modules.add(aliases.get(head, head))
            if name.rsplit(".", 1)[-1] == "FastAPI" and deps is not None and self.deps_have_auth(deps):
                self.app_protected = True


class FileScanner(ast.NodeVisitor):
    def __init__(self, rel, text, settings, index):
        self.rel, self.text, self.index = rel, text, index
        self.public_routes = settings.get("public_routes", [])
        self.protected_owners = set()
        self.context = []          # enclosing function / assignment names, for "is this a secret?" checks
        self.in_route = False
        self.findings = []

    def add(self, rule, cat, sev, node, msg):
        self.findings.append(finding(rule, cat, sev, self.rel, node.lineno, msg, line_text(self.text, node.lineno)))

    def secret_context(self):
        return any(SECRETISH.search(c) for c in self.context)

    # ---- structure
    def visit_Module(self, node):
        for stmt in ast.walk(node):  # routers created with dependencies=[auth]
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                ctor = dotted(stmt.value.func).rsplit(".", 1)[-1]
                deps = kwarg(stmt.value, "dependencies")
                if ctor in ("APIRouter", "FastAPI") and deps is not None and self.index.deps_have_auth(deps):
                    self.protected_owners.update(dotted(t) for t in stmt.targets)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        is_route = self.check_route(node)
        self.context.append(node.name)
        prev, self.in_route = self.in_route, self.in_route or is_route
        self.generic_visit(node)
        self.in_route = prev
        self.context.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node):
        self.context.extend(dotted(t) for t in node.targets)
        self.generic_visit(node)
        del self.context[-len(node.targets):]

    # ---- FastAPI auth
    def check_route(self, fn):
        found = False
        for dec in fn.decorator_list:
            if not (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr in ROUTE_METHODS):
                continue
            found = True
            path_node = dec.args[0] if dec.args else kwarg(dec, "path")
            path = path_node.value if isinstance(path_node, ast.Constant) else ""
            owner = dotted(dec.func.value)
            if any(glob_match(path, p) for p in self.public_routes) or self.has_auth(fn, dec, owner):
                continue
            method = dec.func.attr
            sev = "high" if method in MUTATING else "medium"
            self.add("PY-ROUTE-NOAUTH", "authz", sev, dec,
                     f"{method.upper()} {path or '?'} has no auth dependency (route, router, include_router or app). "
                     "Confirm it is meant to be public or add the project's auth name to `auth_dependencies`.")
        return found

    def has_auth(self, fn, dec, owner):
        if self.index.app_protected or owner in self.protected_owners:
            return True
        if os.path.splitext(os.path.basename(self.rel))[0] in self.index.protected_modules:
            return True
        deps = kwarg(dec, "dependencies")
        if deps is not None and self.index.deps_have_auth(deps):
            return True
        a = fn.args
        params = a.posonlyargs + a.args + a.kwonlyargs
        return any(self.index.deps_have_auth(n) for n in a.defaults + [d for d in a.kw_defaults if d is not None]) \
            or any(p.annotation is not None and self.index.deps_have_auth(p.annotation) for p in params)

    # ---- call-level rules
    def visit_Call(self, node):
        name = dotted(node.func)
        last = name.rsplit(".", 1)[-1]
        args = node.args

        if last in SQL_SINKS and args and is_dynamic_str(args[0]):
            self.add("PY-SQLI", "injection", "high", node, f"SQL built with string formatting passed to {last}(); use bound parameters.")
        if name.startswith("subprocess.") and last in SUBPROCESS and is_const(kwarg(node, "shell"), True):
            sev = "low" if args and isinstance(args[0], ast.Constant) else "high"
            self.add("PY-CMDI", "injection", sev, node, "subprocess with shell=True; pass an argument list without a shell.")
        if name in ("os.system", "os.popen") and args and not isinstance(args[0], ast.Constant):
            self.add("PY-CMDI", "injection", "high", node, f"{name}() with a dynamic command.")
        if name in ("eval", "exec") and args and not isinstance(args[0], ast.Constant):
            self.add("PY-EVAL", "rce", "high", node, f"{name}() on dynamic input.")
        if name in DESERIALIZE:
            self.add("PY-DESER", "rce", "high", node, f"{name}() can execute code when the data is attacker-controlled.")
        loader = kwarg(node, "Loader") or (args[1] if len(args) > 1 else None)
        if name == "yaml.unsafe_load" or (name == "yaml.load" and "Safe" not in (dotted(loader) if loader else "")):
            self.add("PY-YAML", "rce", "high", node, "yaml.load without SafeLoader; use yaml.safe_load().")
        if name in ("hashlib.md5", "hashlib.sha1") and not is_const(kwarg(node, "usedforsecurity"), False):
            sev = "medium" if self.secret_context() else "low"
            self.add("PY-WEAKHASH", "crypto", sev, node, f"{name} is not collision-resistant; use sha256+ (or bcrypt/argon2 for passwords).")
        if name.startswith("random.") and last in RANDOM_FUNCS and self.secret_context():
            self.add("PY-RANDOM", "crypto", "medium", node, "`random` is predictable; use the `secrets` module for tokens.")
        if name.endswith("jwt.decode"):
            self.check_jwt(node)
        if last == "add_middleware" and args and dotted(args[0]).endswith("CORSMiddleware"):
            self.check_cors(node)
        if last == "FastAPI" and is_const(kwarg(node, "debug"), True):
            self.add("PY-DEBUG", "config", "medium", node, "FastAPI(debug=True) returns tracebacks to clients.")
        if name.split(".")[0] in ("requests", "httpx") and is_const(kwarg(node, "verify"), False):
            self.add("PY-TLS", "config", "medium", node, "TLS certificate verification disabled.")
        if name.split(".")[0] in ("requests", "httpx") and last in ("get", "post", "put", "request", "stream") \
                and self.in_route and args and not isinstance(args[0], ast.Constant):
            self.add("PY-SSRF", "injection", "low", node, "Outbound request with a dynamic URL inside a route; check it is not user-controlled (SSRF).")
        if (name.split(".")[0] in ("logger", "logging", "log") or name == "print") and self.logs_secret(node):
            self.add("PY-LOGSECRET", "data_exposure", "medium", node, "Sensitive value written to logs.")
        if last in ("HTMLResponse", "Markup") and args and is_dynamic_str(args[0]):
            self.add("PY-XSS", "xss", "medium", node, f"{last} built from a formatted string; escape user input or use templates with autoescape.")
        self.generic_visit(node)

    def check_jwt(self, node):
        options = kwarg(node, "options")
        verify_off = is_const(kwarg(node, "verify"), False)
        if isinstance(options, ast.Dict):
            for k, v in zip(options.keys, options.values):
                if isinstance(k, ast.Constant) and k.value == "verify_signature" and is_const(v, False):
                    verify_off = True
        if verify_off:
            self.add("PY-JWT", "authz", "high", node, "jwt.decode with signature verification disabled.")
        elif kwarg(node, "algorithms") is None:
            self.add("PY-JWT", "authz", "medium", node, "jwt.decode without algorithms=[...]; pin the expected algorithm.")

    def check_cors(self, node):
        origins = kwarg(node, "allow_origins")
        regex = kwarg(node, "allow_origin_regex")
        wildcard = (isinstance(origins, (ast.List, ast.Tuple)) and any(is_const_str(e, "*") for e in origins.elts)) \
            or (isinstance(regex, ast.Constant) and regex.value in (".*", "*", "^.*$"))
        if wildcard:
            creds = is_const(kwarg(node, "allow_credentials"), True)
            self.add("PY-CORS", "config", "high" if creds else "low", node,
                     "CORS allows any origin" + (" with credentials" if creds else "") + ".")

    def logs_secret(self, node):
        for arg in node.args:
            for n in ast.walk(arg):
                ident = n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else None
                if ident and SENSITIVE_NAME.search(ident):
                    return True
        return False


def is_const_str(node, value):
    return isinstance(node, ast.Constant) and node.value == value


def make_auth_matcher(settings):
    names = set(settings.get("auth_dependencies", []))
    pattern = re.compile(settings.get("auth_pattern", DEFAULT_AUTH_PATTERN))
    return lambda dep: bool(dep) and (dep.rsplit(".", 1)[-1] in names or pattern.search(dep) is not None)


def scan(target, files, settings):
    """Scan the given repo-relative .py files; returns a list of findings."""
    trees, findings = {}, []
    index = AuthIndex(make_auth_matcher(settings))
    for rel in files:
        if not rel.endswith(".py") or is_test_path(rel):
            continue
        text = read_text(os.path.join(target, rel))
        if text is None:
            continue
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError as exc:
            findings.append(finding("PY-PARSE", "config", "low", rel, exc.lineno or 1, f"Could not parse: {exc.msg}"))
            continue
        trees[rel] = (tree, text)
        index.collect(tree)
    for rel, (tree, text) in trees.items():
        fs = FileScanner(rel, text, settings, index)
        fs.visit(tree)
        findings.extend(fs.findings)
    return findings


def _expand(paths):
    for p in paths:
        if os.path.isdir(p):
            for d, dirs, names in os.walk(p):
                dirs[:] = [x for x in dirs if x not in (".venv", "venv", "__pycache__", "node_modules", ".git")]
                yield from (os.path.relpath(os.path.join(d, n)).replace(os.sep, "/") for n in names)
        else:
            yield p.replace(os.sep, "/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    print(json.dumps(scan(".", list(_expand(sys.argv[1:])), {}), indent=2))
