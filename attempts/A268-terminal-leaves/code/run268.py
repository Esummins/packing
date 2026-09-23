"""A268 -- driver: A211's run211.py (k5) or A256's run256.py (trump5) VERBATIM, with A268's flag-gated levers installed
by module-attribute patches (no A211 / A256 file is edited; the frozen verifiers are untouched):

  A268_COUNT=1   count268.count_search replaces tree205.count_search (Lemma COUNT-PRUNE + the wall; notes s.2)
  A268_FORCE=1   leaf268 wraps Tree211.leaf_rules: Lemma ROLE-SPLIT forced at a genuine fixed point (notes s.3)
  A268_TIMING=1  per-stage wall accounting (cascade rounds, candidates / anon_needed, each leaf rule), printed at exit

    python run268.py k5|trump5 page <nid> --pads g1 --wall 1800 --start LABEL --cert-dir D --results R [--no-fig]
    python run268.py seam --phase siblings --only-sibling R.1.2.1 --wall-sib 1800 --journal J   (A257's pilot257)
"""
import atexit
import os
import runpy
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
A256 = os.path.join(ROOT, "attempts", "A256-trump5-passes", "code")
TIMES = {}


def timed(mod, name, key):
    f = getattr(mod, name)

    def w(*a, **kw):
        t0 = time.time()
        try:
            return f(*a, **kw)
        finally:
            n, s = TIMES.get(key, (0, 0.0))
            TIMES[key] = (n + 1, s + time.time() - t0)
    setattr(mod, name, w)


def install_timing():
    import tree205 as T5
    import tree205b as TB
    import tree206 as N6
    import tree209 as N9
    import tree211 as N11
    import leaves211 as L11
    import rsplit211 as RS
    import count268 as C68
    # the count: wrap the module function every caller reaches (count268's when installed)
    f = T5.count_search

    def cs(pg, *a, **kw):
        t0 = time.time()
        r = f(pg, *a, **kw)
        k = "count[capped]" if r.capped else ("count[feasible]" if r.feasible else "count[INFEASIBLE]")
        n, s = TIMES.get(k, (0, 0.0))
        TIMES[k] = (n + 1, s + time.time() - t0)
        return r
    T5.count_search = cs
    timed(TB, "anon_needed", "candidates: anon_needed (bar-anon counts)")
    timed(TB, "candidates", "candidates (option-table read)")
    timed(TB, "cascade", "cascade rounds (all)")
    timed(N9, "noroom_at", "leaf (b) no-room")
    timed(L11, "cc_rows", "leaf (a) rule CC")
    # N6.ns_candidates is NOT wrapped: tree211 reads its __globals__["SOFT_ALL"]
    timed(RS, "candidates", "leaf (d') ROLE-SPLIT candidates")
    timed(N11.Tree211, "leaf_rules", "leaf_rules (total)")
    del C68

    def report():
        print("   A268 TIMING (calls, seconds) -- the count rows are included in the cascade / candidates rows:", flush=True)
        for k, (n, s) in sorted(TIMES.items(), key=lambda kv: -kv[1][1]):
            print("     %-48s %5d  %9.1f" % (k, n, s), flush=True)
    atexit.register(report)


def install_levers():
    while HERE in sys.path:
        sys.path.remove(HERE)
    sys.path.append(HERE)                                          # AFTER the chain dirs: never shadows a chain module
    import count268
    count268.install()
    if (os.environ.get("A268_FORCE") or "") == "1":
        import leaf268
        leaf268.install()
    if (os.environ.get("A268_TIMING") or "") == "1":
        install_timing()


def main():
    argv = list(sys.argv[1:])
    chain = argv.pop(0)
    sys.path.insert(0, HERE)
    if chain == "seam":                                            # A257's pilot, one sibling: levers after its setup()
        sys.path.insert(0, os.path.join(ROOT, "attempts", "A257-trump5-window", "code"))
        import pilot257
        orig = pilot257.setup

        def setup():
            S9 = orig()
            install_levers()
            return S9
        pilot257.setup = setup
        sys.argv = ["pilot257.py"] + argv
        pilot257.main()
        return
    if chain == "trump5":
        sys.path.insert(0, A256)
        import run256
        for extra, val in (("--cert-dir", run256.CERTS), ("--results", run256.RES)):
            if not any(a.startswith(extra) for a in argv):
                argv += [extra, val]
        if "--no-fig" not in argv:
            argv += ["--no-fig"]
        got = run256.install_shadows()
        print("   A256 shadows: %s" % sorted(got), flush=True)
    else:
        sys.path.insert(0, A211)
    install_levers()
    sys.argv = [os.path.join(A211, "run211.py")] + argv
    runpy.run_path(sys.argv[0], run_name="__main__")


if __name__ == "__main__":
    main()
