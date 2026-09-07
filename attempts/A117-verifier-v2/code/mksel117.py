"""A117 T1 -- build the equivalence selection: >= 20 EXISTING v1 certificates spanning both
classes, levels 1-3, PASS and FAIL, plus A96 resolver cells (narrow slabs at depth 56), the
protected-class pilots (A100 k3_02/k4_11), the A99 level-3 tree nodes, and A61's stragglers.
Read-only; writes results/selection.json."""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
W = "969271/250000"
LO = "191/50"


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def a96_rows():
    rows = []
    for f in glob.glob(os.path.join(ROOT, "attempts", "A96-a57-parametric", "certs", "param",
                                    "*", "*.report.json")):
        d = json.load(open(f))
        if d.get("slo") is None:
            continue
        cert = f.replace(".report.json", ".param.json")
        if not os.path.exists(cert):
            continue
        nm = os.path.basename(cert)
        rows.append(dict(cert=cert, cls="k5_11" if nm.startswith("k5_11") else "k5_16",
                         side=os.path.basename(os.path.dirname(f)).split("_")[-1],
                         level=1 + nm.count("_D"), result=d["result"], t=d.get("time_s") or 0.0,
                         slo=d["slo"], shi=d["shi"], depth=d["depth"], split=d["split"],
                         tscale=str(d["tscale"]), sscale=str(d["sscale"])))
    return rows


def main():
    rows = a96_rows()
    sel = []

    def pick(cls, side, level, res, k, maxt=90.0):
        c = [r for r in rows if r["cls"] == cls and r["side"] == side and r["level"] == level
             and r["result"] == res and r["t"] < maxt]
        c.sort(key=lambda r: r["t"])
        return c[:k]

    plan = [("k5_11", "G1", 1, "PASS", 3), ("k5_11", "G1", 1, "FAIL", 2),
            ("k5_11", "G1", 2, "PASS", 2), ("k5_11", "G1", 2, "FAIL", 2),
            ("k5_11", "L1", 2, "PASS", 2), ("k5_11", "L1", 2, "FAIL", 1),
            ("k5_16", "G1", 1, "PASS", 3), ("k5_16", "G1", 1, "FAIL", 2),
            ("k5_16", "L1", 2, "PASS", 1, 250.0), ("k5_16", "L1", 2, "FAIL", 1, 250.0)]
    for row in plan:
        cls, side, level, res, k = row[:5]
        for r in pick(cls, side, level, res, k, *row[5:]):
            sel.append(dict(cert=rel(r["cert"]), slo=r["slo"], shi=r["shi"], depth=r["depth"],
                            split=r["split"], tscale=r["tscale"], sscale=r["sscale"],
                            tag="A96 %s %s level%d %s" % (cls, side, level, res)))

    # A96 resolver cells: the SAME certificate on a narrow slab at depth 56 (cheapest two)
    res_rows = []
    for f in glob.glob(os.path.join(ROOT, "attempts", "A96-a57-parametric", "certs", "resolve",
                                    "*.report.json")):
        d = json.load(open(f))
        c = d.get("cert")
        if not c or not os.path.exists(c):
            continue
        res_rows.append((d.get("time_s") or 9e9, c, d))
    res_rows.sort()
    seen_res = set()
    res_pick = []
    for t, c, d in res_rows:
        if c in seen_res:
            continue
        seen_res.add(c)
        res_pick.append((t, c, d))
        if len(res_pick) == 3:
            break
    for t, c, d in res_pick:
        sel.append(dict(cert=rel(c), slo=d["slo"], shi=d["shi"], depth=d["depth"],
                        split=d["split"], tscale=str(d["tscale"]), sscale=str(d["sscale"]),
                        tag="A96 resolver cell (narrow slab, depth 56)"))

    # other campaigns: protected-class pilots, the A99 level-3 tree nodes, A57, A95, A61
    extra = []
    for pat, tag, depth in (
            ("attempts/A100-protected-pilot/certs/param/k3_02/*.param.json",
             "A100 protected class k3_02", 48),
            ("attempts/A100-protected-pilot/certs/param/k4_11/*.param.json",
             "A100 protected class k4_11", 48),
            ("attempts/A99-k0-tree-v2/certs/param/*.param.json",
             "A99 k0 tree level 3", 48),
            ("attempts/A57-shadow-trees/certs/param/*.param.json", "A57 param", 48),
            ("attempts/A95-a57-shortcuts/results/param/*.param.json", "A95 param", 48),
            ("attempts/A61-window-stragglers/certs/*.param.json", "A61 straggler", 48)):
        got = sorted(glob.glob(os.path.join(ROOT, pat.replace("/", os.sep))))
        n = 2 if "A99" in tag or "A100" in tag else 1
        for p in got[:n]:
            extra.append(dict(cert=rel(p), slo=LO, shi=W, depth=depth, split=3,
                              tscale="2", sscale="8", tag=tag))
    sel.extend(extra)

    seen, out = set(), []
    for e in sel:
        if e["cert"] in seen:
            continue
        seen.add(e["cert"])
        out.append(e)
    json.dump(out, open(os.path.join(RES, "selection.json"), "w"), indent=1)
    print("selection: %d certificates" % len(out))
    for e in out:
        print("  %-46s %s" % (e["tag"], os.path.basename(e["cert"])))


if __name__ == "__main__":
    main()
