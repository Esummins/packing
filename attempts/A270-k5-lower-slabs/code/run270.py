"""A270 -- driver: A211's run211.py VERBATIM over the re-emitted k5 records at a lower pad, with

  * A270's loader (load270) and the pads g2 / g3 / g4 registered in quick200.PADS (pads270.install);
  * stage 0 written to A270's certs only (stage209.CERTS), Lemma INHERIT reading A270's certs only (A229_CERT_DIR):
    the re-emitted records are NEW hypotheses (wider pins) -- no certificate of the source nid inherits to them;
  * A268's levers imported, never edited: count268 (Lemma COUNT-PRUNE, A268_COUNT=1) and leaf268 (forced
    ROLE-SPLIT, A268_FORCE=1); A268's finish() stamps the certificate and runs verify268 on every INFEASIBLE-count
    dump IN PROCESS (A268_RESULTS / A268_VERIFY_OUT point at A270's results).

    python run270.py page <nid>_r270g2 --pads g2 --wall 1800 [--start LABEL --cert-suffix TAG]"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
A268 = os.path.join(ROOT, "attempts", "A268-terminal-leaves", "code")
CERTS = os.path.join(ATT, "certs")
RES = os.path.join(ATT, "results", "slab270.jsonl")


def setup():
    os.environ["A229_CERT_DIR"] = CERTS
    os.environ.setdefault("A268_RESULTS", os.path.join(ATT, "results", "terminal270.jsonl"))
    os.environ.setdefault("A268_VERIFY_OUT", os.path.join(ATT, "results", "verify268_a270.jsonl"))
    os.environ.setdefault("A268_DUMP_DIR", os.path.join(CERTS, "count268"))     # the COUNT268 dumps stay in A270's certs
    os.makedirs(os.environ["A268_DUMP_DIR"], exist_ok=True)
    sys.path.insert(0, A211)
    for p in (A268, HERE):                                          # AFTER the chain dirs: they never shadow a chain module
        while p in sys.path:
            sys.path.remove(p)
        sys.path.append(p)
    import stage209
    stage209.CERTS = CERTS
    import pads270
    pads = pads270.install()
    import load270
    load270.install()
    import count268                                                 # READ-ONLY (A268)
    count268.install()
    if (os.environ.get("A268_FORCE") or "") == "1":
        import leaf268
        leaf268.install()
    print("   A270: pads %s; loader load270; count268 True; leaf268 %s; certs %s" % (
        pads, (os.environ.get("A268_FORCE") or "") == "1", os.path.relpath(CERTS, ROOT)), flush=True)


def main():
    argv = list(sys.argv[1:])
    for extra, val in (("--cert-dir", CERTS), ("--results", RES)):
        if not any(a.startswith(extra) for a in argv):
            argv += [extra, val]
    if "--no-fig" not in argv:
        argv += ["--no-fig"]
    setup()
    sys.argv = [os.path.join(A211, "run211.py")] + argv
    runpy.run_path(sys.argv[0], run_name="__main__")
    import run268                                                   # READ-ONLY (A268): stamp + verify268 + its row
    run268.finish("k5-r270", argv)


if __name__ == "__main__":
    main()
