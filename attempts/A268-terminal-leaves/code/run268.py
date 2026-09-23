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
        finish("seam", ["page", "synth257_d001_h002_t2", "--pads", argv[argv.index("--pad") + 1] if "--pad" in argv else "g1",
                        "--start", argv[argv.index("--only-sibling") + 1] if "--only-sibling" in argv else None], journal=pilot257.JOURNAL)
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
    finish(chain, argv)


def verify_dumps(paths):
    """the COUNT268 verifier clause, IN PROCESS (no extra python): verify268 on every new dump, appended to
    results/verify268.jsonl; returns (n verified, n failed)."""
    import json
    import verify268
    ok = bad = 0
    out = os.environ.get("A268_VERIFY_OUT") or os.path.join(HERE, "..", "results", "verify268.jsonl")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    for p in paths:
        try:
            r = verify268.verify(p)
        except Exception as e:                                      # noqa: BLE001
            r = dict(path=p, verdict="FAILED (verifier error %r)" % (e,))
        ok += r["verdict"].startswith("VERIFIED")
        bad += not r["verdict"].startswith("VERIFIED")
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, default=str) + chr(10))
    return ok, bad


def finish(chain, argv, journal=None):
    """after run211: stamp the certificate with what A268 changed (flags, every count268 call, the dumps of every
    INFEASIBLE count = the COUNT268 verifier clause's inputs, the forced splits) and append A268's own row."""
    import json
    import count268
    get = lambda k: argv[argv.index(k) + 1] if k in argv else None      # noqa: E731
    nid, pad, suf = argv[1], get("--pads"), get("--cert-suffix")
    cert = os.path.join(os.path.abspath(get("--cert-dir") or "."), "coarsetree211_%s%s.json" % (nid, ("__" + suf) if suf else ""))
    st = count268.STATS
    force = None
    if "leaf268" in sys.modules:
        force = dict(sys.modules["leaf268"].REP)
    a268 = dict(count=count268.ON, force=force, node_cap=count268.NODE_CAP, budget=count268.BUDGET,
                calls=len(st), capped=sum(1 for r in st if r["capped"]), infeasible=sum(1 for r in st if not r["feasible"]),
                count_seconds=round(sum(r["seconds"] for r in st), 1), max_nodes=max([r["nodes"] for r in st] or [0]),
                dumps=[r["dump"] for r in st if r.get("dump")],
                verifier="[V: attempts/A268-terminal-leaves/code/verify268.py <dump>] for every JOINT COUNT kill decided by "
                         "count268 (Lemma COUNT-PRUNE, notes/terminal268.md s.2); forced splits: Lemma ROLE-SPLIT (s.3)")
    a268["verified"], a268["verify_failed"] = verify_dumps(a268["dumps"])
    verdict = None
    if journal:                                                     # seam: the pilot's journal row is the record
        run = {}
        try:
            rows = [json.loads(x) for x in open(journal, encoding="utf-8") if x.strip()]
            r = [x for x in rows if x.get("phase") == "sibling" and x.get("only") == get("--start")][-1]
            verdict, run = r.get("verdict"), dict(seconds=r.get("run_seconds"), n_nodes=r.get("n_nodes"), wall=r.get("wall_hit"))
        except Exception:                                           # noqa: BLE001
            pass
        cert = journal
    try:
        if journal:
            raise StopIteration
        doc = json.load(open(cert, encoding="utf-8"))
        doc.setdefault("a268", []).append(dict(a268, pad=pad, start=get("--start"), when=time.strftime("%Y-%m-%d %H:%M:%S")))
        tmp = cert + ".a268tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, default=str)
        os.replace(tmp, cert)
        verdict = (doc.get("verdicts") or {}).get(pad)
        run = (doc.get("runs") or {}).get("%s_page" % pad) or {}
    except StopIteration:
        pass
    except Exception as e:                                          # noqa: BLE001
        print("   A268 finish: certificate not stamped (%r)" % (e,), flush=True)
        run = {}
    row = dict(chain=chain, nid=nid, pad=pad, start=get("--start"), verdict=verdict, seconds=run.get("seconds"),
               n_nodes=run.get("n_nodes"), max_depth=run.get("max_depth"), wall=run.get("wall"), cert=cert.replace("\\", "/"),
               when=time.strftime("%Y-%m-%d %H:%M:%S"), **{k: v for k, v in a268.items() if k != "verifier"})
    out = os.environ.get("A268_RESULTS") or os.path.join(HERE, "..", "results", "terminal268.jsonl")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, default=str) + chr(10))
    print("   A268: %s %s %s -> %s; count268 %d call(s), %d capped, %d INFEASIBLE (dumps %d: %d VERIFIED, %d FAILED), %.1f s; forced %s" % (
        nid, pad, get("--start"), verdict, row["calls"], row["capped"], row["infeasible"], len(row["dumps"]), row["verified"], row["verify_failed"],
        a268["count_seconds"] or 0, force), flush=True)


if __name__ == "__main__":
    main()
