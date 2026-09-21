"""A256 -- the trump5 driver: A211's CURRENT run211.py, run VERBATIM over the trump5 population.

Why a launcher and not a fork (notes/trump5_closure.md s.1).  A212 froze a COPY of A211's chain at b06a8203 and the
chain has moved since: A220 (exact-first / NOROOM_INHERIT), A221 (lane), A224 (Rule SNAP), A228's guards, A229's
--start / --cert-suffix shards and A230's Rule EPS all live in tree211.py / leaves211.py, none of them in A212's
copy.  Diffing A212's copy against A211 at b06a8203 shows the trump5 work touched exactly THREE files and, in two of
them, exactly one line:
  * load211.py   -- A60's frontier records answered by FP.load_page (+48 lines);
  * stage209.py  -- `c["roles"]["H"]` -> the first `H*` key (the f1_L10_0003 2-H record);
  * poly204.py   -- the same one line in load_start.
So A256 SHADOWS those three files (plus inherit211, which only adds A212's certificates as a source) and runs A211's
own run211.py unchanged: the chain is never forked again, and every lever the k5 loop gained comes for free.

    python run256.py page <nid> --pads zero --wall 1800 [--start LABEL] [--cert-suffix TAG] [--tube]

Every flag is run211.py's; --cert-dir / --results / --no-fig default to A256's own directories, so A211's
certificates, results, logs and pages are never written.  --tube additionally swaps Tree211 for Tree256 (the gate,
Lemma TUBE-LEAF and Lemma TUBE-KILL, notes/trump5_closure.md s.3): OFF by default, because the triage of
results/triage256.json puts all 149 nodes in class (a) -- no node's hypothesis admits a contracted Trump image, so
the tube leaves have an empty domain on this population and the plain chain is the sharper instrument.
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "trump5passes256.jsonl"))
RUN211 = os.path.join(A211, "run211.py")


def install_shadows():
    """put A256's code dir FIRST and pre-import the four shadowed modules under their real names.

    run211.py does `sys.path.insert(0, HERE)` with HERE = A211's code dir before it imports anything, so path order
    alone would not shadow: the modules are imported HERE, land in sys.modules, and run211's own imports find them."""
    os.environ.setdefault("A229_CERT_DIR", CERTS)                  # inherit211 merges A256's certs (page + shards)
    for p in (A211, HERE):
        while p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, A211)
    sys.path.insert(0, HERE)
    import load256                                                 # noqa: E402  (imports the shadowed load211)
    load256.install()
    import poly204                                                 # noqa: E402,F401
    import stage209                                                # noqa: E402,F401
    import inherit211                                              # noqa: E402,F401
    got = {m: os.path.dirname(os.path.abspath(sys.modules[m].__file__)) for m in ("load211", "poly204", "stage209", "inherit211")}
    bad = {m: d for m, d in got.items() if os.path.normcase(d) != os.path.normcase(HERE)}
    if bad:
        raise SystemExit("A256: the shadowed modules did not install (%s)" % bad)
    return got


def install_tube():
    """--tube: Tree256 (gate + Lemma TUBE-LEAF + Lemma TUBE-KILL) in place of Tree211, for a class-(b) node."""
    import tree211 as N11
    import tree256 as N56
    N11.Tree211 = N56.Tree256
    print("   A256: Rule TUBE installed -- Tree256 (gate + Lemma TUBE-LEAF + Lemma TUBE-KILL)", flush=True)


def main():
    argv = list(sys.argv[1:])
    tube = "--tube" in argv
    argv = [a for a in argv if a != "--tube"]
    if not any(a.startswith("--cert-dir") for a in argv):
        argv += ["--cert-dir", CERTS]
    if not any(a.startswith("--results") for a in argv):
        argv += ["--results", RES]
    if "--no-fig" not in argv:                                     # A211's gallery / campaign pages are never written
        argv += ["--no-fig"]
    got = install_shadows()
    print("   A256 shadows: %s" % {m: os.path.relpath(d, ROOT).replace("\\", "/") for m, d in got.items()}, flush=True)
    if tube:
        install_tube()
    sys.argv = [RUN211] + argv
    runpy.run_path(RUN211, run_name="__main__")


if __name__ == "__main__":
    main()
