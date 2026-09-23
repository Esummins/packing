"""A269 -- driver: A211's run211.py VERBATIM over the re-emitted trump5 records, with

  * A256's shadows (run256.install_shadows: load211 / poly204 / stage209 / inherit211) -- the trump5 chain;
  * A269's loader (load269) and pad "tube" = s0/3.832084 registered in quick200.PADS / ray256.PADS (pads269);
  * stage 0 read from / written to A269's certs only (stage209.CERTS / READ_DIRS);
  * A268's levers: count268 (Lemma COUNT-PRUNE, A268_COUNT=1) and leaf268 (forced ROLE-SPLIT, A268_FORCE=1),
    imported from attempts/A268-terminal-leaves/code, never edited; A268's finish() stamps the certificate and runs
    verify268 on every INFEASIBLE-count dump IN PROCESS (A268_RESULTS / A268_VERIFY_OUT point at A269's results);
  * A257's Tree257 (A269_TUBE=1, default): the trump5 GATE, the ALIGNED split, the slot-ray TUBE-KILL with A257's
    three fixes (free-role box test, min over the pins' delta_pin, the leaf text).

Why a SHIM and not `N11.Tree211 = Tree257` (A256's install_tube): Tree256 / Tree257 call their base as
`N11.Tree211.<method>(self, ...)` through the MODULE attribute, so rebinding tree211.Tree211 to the subclass makes
every such call recurse into itself (A256's --tube has never run; it would not).  Here tree256.N11 / tree257.N11 are
pointed at a proxy whose Tree211 is the REAL class (with leaf268's wrapper already installed on it), and only then is
tree211.Tree211 -- the name run211 constructs -- rebound to Tree257.

    python run269.py page <nid> --pads window --wall 1800 [--start LABEL --cert-suffix TAG]
"""
import os
import runpy
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
A256 = os.path.join(ROOT, "attempts", "A256-trump5-passes", "code")
A257 = os.path.join(ROOT, "attempts", "A257-trump5-window", "code")
A268 = os.path.join(ROOT, "attempts", "A268-terminal-leaves", "code")
CERTS = os.path.join(ATT, "certs")
RES = os.path.join(ATT, "results", "reemit269.jsonl")


def setup():
    os.environ["A229_CERT_DIR"] = CERTS
    os.environ.setdefault("A268_RESULTS", os.path.join(ATT, "results", "terminal269.jsonl"))
    os.environ.setdefault("A268_VERIFY_OUT", os.path.join(ATT, "results", "verify268_a269.jsonl"))
    os.environ.setdefault("A268_DUMP_DIR", os.path.join(CERTS, "count268"))   # count268's dumps: A269's certs, never A268's
    os.environ.setdefault("A256_A212_CERT_DIR", CERTS)            # A212's certs are for OTHER nids: never a source here
    sys.path.insert(0, A256)
    import run256                                                  # READ-ONLY (A256)
    got = run256.install_shadows()
    for p in (A257, A268, HERE):                                   # AFTER the chain dirs: they never shadow a chain module
        while p in sys.path:
            sys.path.remove(p)
        sys.path.append(p)
    import stage209
    stage209.CERTS = CERTS
    stage209.READ_DIRS = [CERTS]
    import pads269
    pads = pads269.install()
    import load269
    load269.install()
    import count268                                                # READ-ONLY (A268)
    count268.install()
    if (os.environ.get("A268_FORCE") or "") == "1":
        import leaf268
        leaf268.install()
    tube = (os.environ.get("A269_TUBE") or "1") == "1"
    if tube:
        import tree211 as N11
        import tree256 as N56
        import tree257 as N57
        real = N11.Tree211
        shim = types.ModuleType("tree211_real")
        shim.__dict__.update(N11.__dict__)
        shim.Tree211 = real
        N56.N11 = shim
        N57.N11 = shim
        N11.Tree211 = N57.Tree257
    print("   A269: shadows %s; pads %s; loader load269; count268 %s; leaf268 %s; Tree257 (gate + aligned split + TUBE-KILL) %s"
          % (sorted(got), pads, True, (os.environ.get("A268_FORCE") or "") == "1", tube), flush=True)


def main():
    argv = list(sys.argv[1:])
    for extra, val in (("--cert-dir", CERTS), ("--results", RES)):
        if not any(a.startswith(extra) for a in argv):
            argv += [extra, val]
    if "--no-fig" not in argv:
        argv += ["--no-fig"]
    if len(argv) > 1:
        os.environ["A268_NID"] = argv[1]
    setup()
    sys.argv = [os.path.join(A211, "run211.py")] + argv
    runpy.run_path(sys.argv[0], run_name="__main__")
    import run268                                                  # READ-ONLY (A268): stamp + verify268 + its row
    run268.finish("trump5-r269", argv)


if __name__ == "__main__":
    main()
