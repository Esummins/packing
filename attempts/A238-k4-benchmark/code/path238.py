"""A238 -- the import path, enforced.

Two attempt directories carry modules with the SAME names: A211's (`tree211`, `tree206`, `tree209`, `coarse211`,
`leaves211`, `poly204`, `load211`, `stage209`, `run211` -- the LIVE k5 toolkit, with A220 / A221 / A224 / A230) and
A212's frozen copies of the same files from 2026-09-11 (before all four).  A238 must run the LIVE toolkit and take
ONLY `trump212` (the Trump image + the containment gate) from A212, so the order has to be

    [ A238/code , A211/code , ... , A212/code ]

and it has to be re-imposed after every import that inserts its own directory at position 0 (A198's fastprop, A178's
geo178, A212's loaders all do).  `fix()` is idempotent; call it before importing any of the shared names."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
A212 = os.path.join(ROOT, "attempts", "A212-trump5-tree", "code")


def fix():
    while A212 in sys.path:
        sys.path.remove(A212)
    sys.path.append(A212)                       # LAST: only `trump212` may come from here
    for p in (A211, HERE):
        while p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)                   # HERE first, then the live A211 toolkit
    return sys.path


def check():
    """assert every shared module actually came from A211 (or A238), and trump212 from A212."""
    bad = []
    for name in ("tree211", "tree206", "tree209", "coarse211", "leaves211", "poly204", "load211", "stage209", "run211"):
        m = sys.modules.get(name)
        if m is not None and os.path.dirname(os.path.abspath(m.__file__)) != A211:
            bad.append((name, m.__file__))
    m = sys.modules.get("trump212")
    if m is not None and os.path.dirname(os.path.abspath(m.__file__)) != A212:
        bad.append(("trump212", m.__file__))
    return bad


fix()
