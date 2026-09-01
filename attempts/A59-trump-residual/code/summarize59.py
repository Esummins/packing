"""A59 pilot: turn results/pilot_zonetree.jsonl into the report tables."""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
J = os.path.join(BASE, "results", "pilot_zonetree.jsonl")
H = 3.7e-3


def rows():
    return [json.loads(l) for l in open(J)]


def main():
    R = rows()
    print("records:", len(R))
    print(collections.Counter(r["verdict"].split("(")[0].strip() for r in R))
    print("wall: LP %.1f s + cert %.1f s = %.1f s"
          % (sum(r.get("lp_s") or 0 for r in R), sum(r.get("cert_s") or 0 for r in R),
             sum((r.get("lp_s") or 0) + (r.get("cert_s") or 0) for r in R)))

    print("\n== M1-shallow (budget 5, 5 pins + 1 sibling core) ==")
    print("| tag | a | at | pinguard | tau | eta | conv | LP s | cert s | verdict |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in R:
        if r["tag"].startswith("m1s"):
            print("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["tag"], r.get("a"), (None if r.get("at") is None else round(r["at"], 6)),
                r.get("pinguard"), (None if r.get("tau") is None else round(r["tau"], 6)),
                (None if r.get("eta") is None else round(r["eta"], 4)), r.get("converged"),
                r.get("lp_s"), r.get("cert_s"), r["verdict"]))

    print("\n== M1-mid (budget 2, 5 pins + 3 cores + 1 sibling core) ==")
    for r in R:
        if r["tag"].startswith("m1m"):
            print("| %s | a=%s | tau=%s | eta=%s | conv=%s | LP %s s | cert %s s | %s |" % (
                r["tag"], r.get("a"), (None if r.get("tau") is None else round(r["tau"], 6)),
                (None if r.get("eta") is None else round(r["eta"], 4)), r.get("converged"),
                r.get("lp_s"), r.get("cert_s"), r["verdict"]))

    print("\n== M1-deep, LP-gated route (budget 1) ==")
    for r in R:
        if r["tag"].startswith("m1d"):
            print("| %s | hw-family | a=%s | at=%s | tau=%s | LP %s s | cert %s s | %s |" % (
                r["tag"], r.get("a"), r.get("at"),
                (None if r.get("tau") is None else round(r["tau"], 6)),
                r.get("lp_s"), r.get("cert_s"), r["verdict"]))

    for pref, name, path in (("rk", "centre-only (full theta)", "rkill_deep.json"),
                             ("rb", "A36 sup-norm box", "rkill_box.json")):
        print("\n== M1-deep, exact vacuity route -- r_kill, %s ==" % name)
        p = os.path.join(BASE, "results", path)
        if os.path.exists(p):
            d = json.load(open(p))
            print("| hw | ht | largest FAIL a | smallest PASS a | r_kill/hw | r_kill/h |")
            print("|---|---|---|---|---|---|")
            for k in sorted(d, key=lambda k: -float(k)):
                e = d[k]
                if e["pass_at"] is None:
                    print("| %g | %g | - | none <= 1.5 | - | - |" % (e["hw"], e["ht"]))
                    continue
                print("| %g | %.5g | %.6g | %.6g | %.3f | %.2f |" % (
                    e["hw"], e["ht"], e["fail_at"], e["pass_at"], e["pass_at"] / e["hw"],
                    e["pass_at"] / H))
        n = [r for r in R if r["tag"].startswith(pref + "_")]
        if n:
            cs = [r["cert_s"] for r in n]
            print("  %d vacuity certificates, cert wall %.1f s total, mean %.2f s, max %.2f s"
                  % (len(n), sum(cs), sum(cs) / len(cs), max(cs)))

    print("\n== cost distribution by kind ==")
    by = collections.defaultdict(list)
    for r in R:
        by[(r.get("kind"), r.get("budget"), r["verdict"].split("(")[0].strip())].append(
            (r.get("lp_s") or 0) + (r.get("cert_s") or 0))
    print("| kind | budget | verdict | n | mean s | max s |")
    print("|---|---|---|---|---|---|")
    for k in sorted(by, key=lambda k: str(k)):
        v = by[k]
        print("| %s | %s | %s | %d | %.1f | %.1f |" % (k[0], k[1], k[2], len(v),
                                                       sum(v) / len(v), max(v)))


if __name__ == "__main__":
    main()
