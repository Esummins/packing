"""A117 T1 -- survey the NO-side (nofam-carrying) certificates of A111 and A112.  Read-only."""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def main():
    out = []
    for camp in ("A111-loadpath-branch", "A112-dual-branching"):
        for p in sorted(glob.glob(os.path.join(ROOT, "attempts", camp, "certs", "*.json"))):
            b = os.path.basename(p)
            if any(b.endswith(x) for x in (".report.json", ".witnesses.json", ".certify.json",
                                           ".param.json")) or ".resolve" in b:
                continue                    # derived artefacts, not certificates
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if d.get("format") != "case-measure-certificate-v1":
                continue
            nf = (d.get("hypotheses") or {}).get("nofams") or []
            rp = p[:-5] + ".report.json"
            rd = json.load(open(rp)) if os.path.exists(rp) else {}
            out.append(dict(camp=camp, cert=rel(p), name=b[:-5],
                            s=str(d.get("s")), n=d.get("n"), budget=d.get("budget"),
                            atoms=len(d.get("atoms", [])),
                            cores=len((d.get("hypotheses") or {}).get("cores") or []),
                            nofams=len(nf),
                            result=rd.get("result"), fixed_seconds=rd.get("time_s"),
                            depth=rd.get("depth"), jobs=rd.get("jobs"),
                            boxes=(rd.get("stats") or {}).get("boxes")))
    json.dump(out, open(os.path.join(HERE, "..", "results", "no_survey.json"), "w"), indent=1)
    n_nf = [r for r in out if r["nofams"]]
    print("case certificates: %d   with NO-families: %d" % (len(out), len(n_nf)))
    for camp in ("A111-loadpath-branch", "A112-dual-branching"):
        rows = [r for r in n_nf if r["camp"] == camp]
        p = [r for r in rows if r["result"] == "PASS"]
        f = [r for r in rows if r["result"] == "FAIL"]
        u = [r for r in rows if r["result"] is None]
        print("  %-22s nofam certs %3d  PASS %3d  FAIL %3d  no-report %3d  fixed wall %s s"
              % (camp, len(rows), len(p), len(f), len(u),
                 round(sum(r["fixed_seconds"] or 0 for r in rows), 1)))
    for r in n_nf:
        print("   %-24s %-58s nofams=%d cores=%d atoms=%3d %s %s s"
              % (r["camp"][:22], r["name"][:58], r["nofams"], r["cores"], r["atoms"],
                 r["result"], round(r["fixed_seconds"], 1) if r["fixed_seconds"] else "-"))


if __name__ == "__main__":
    main()
