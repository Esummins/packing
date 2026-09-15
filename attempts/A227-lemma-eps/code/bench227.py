"""A227 -- run A211's run211.py with Rule EPS wired in WITHOUT editing tree211.py / leaves211.py: the patched copies
in code/patched/ (exactly integration227.diff applied) are imported FIRST, so run211's own `import tree211` finds
them in sys.modules.  Everything else is A211's, byte for byte.

    A227_EPS=1 python bench227.py page <nid> --pads g1 --wall 420 --no-fig --cert-dir <isolated> --results <jsonl>
    python bench227.py --check          # import the patched modules and report which files were loaded
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
PATCHED = os.path.join(HERE, "patched")

sys.path.insert(0, A211)
import load211                                                 # noqa: E402,F401  A211's own path set-up
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "attempts", "A224-snap-rule", "code"))   # tree211 computes this from ITS file


def _load(name, path):
    """register the PATCHED file under the module's plain name BEFORE anything imports it by name (the import chain
    below tree211 reshuffles sys.path, so a path-order trick is not enough)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


leaves211 = _load("leaves211", os.path.join(PATCHED, "leaves211.py"))
tree211 = _load("tree211", os.path.join(PATCHED, "tree211.py"))
for m in (leaves211, tree211):
    assert os.path.abspath(m.__file__).startswith(PATCHED), m.__file__
assert tree211.L11 is leaves211

if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        print("patched leaves211:", leaves211.__file__, "EPS_ON =", leaves211.EPS_ON)
        print("patched tree211:  ", tree211.__file__, "has eps_try =", hasattr(tree211.Tree211, "eps_try") if hasattr(tree211, "Tree211") else "?")
        sys.exit(0)
    sys.argv = [os.path.join(A211, "run211.py")] + sys.argv[1:]
    runpy.run_path(sys.argv[0], run_name="__main__")
