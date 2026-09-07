"""A115 Trump canary.

(1) EXACT corner data of the Trump packing: per D4 image and per corner, the number of placements
    with mu_c <= a_w(delta) and the smallest mu_c (crowdfam92.image_crowd_counts, exact Fractions
    on the A85 class85 images).  An image REALISES the corner-crowd hypothesis iff every corner has
    >= 2 such placements -- in which case a certificate that killed it would be false.
(2) the three Trump-image cells (A38 l1 idx 21 / 152 / 153) must SURVIVE wherever Trump realises
    the hypothesis.  Their T2 records are read from results/rec/.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a115lib as L
import crowdfam92 as CF

CFGS = {"d0": 0.0, "d0.05": 0.05, "d0.1": 0.1}
CELLS = ("node_021", "node_152", "node_153")
OUT = os.path.join(L.RES, "canary115.json")


def main():
    log = L.logger("canary.log")
    rows = {}
    for cfg, delta in CFGS.items():
        fam = L.get_fam(delta, log=lambda *a: None)
        r = CF.image_crowd_counts(fam["a"])
        real = [x["image"] for x in r if x["realises"]]
        rows[cfg] = dict(delta=delta, a_w=str(fam["a"]), a_w_f=float(fam["a"]),
                         counts=[{k: x[k] for k in ("image", "BL", "BR", "TL", "TR", "realises")}
                                 for x in r],
                         fmin=[{k: x[k] for k in ("image", "BL_fmin", "BR_fmin", "TL_fmin",
                                                  "TR_fmin")} for x in r],
                         realising=real)
        log("%s a_w=%.6f realising=%s" % (cfg, float(fam["a"]), real or "NONE"))
        log("   counts %s" % ";".join("%s[%d%d%d%d]" % (x["image"], x["BL"], x["BR"], x["TL"],
                                                        x["TR"]) for x in r))

    cells = {}
    recd = os.path.join(L.RES, "rec")
    for nid in CELLS:
        cells[nid] = {}
        for cfg in CFGS:
            hit = [f for f in os.listdir(recd) if f.startswith(nid + "__" + cfg + "__")]
            for f in hit:
                d = json.load(open(os.path.join(recd, f)))
                cells[nid][cfg + "|e" + d["e"]] = dict(cfg=cfg, tau=d.get("tau"),
                                          budget=d.get("budget"),
                                          eta=d.get("eta"), converged=d.get("converged"),
                                          verdict=d.get("verdict"), lp_s=d.get("lp_s"))
    certs = {}
    p = os.path.join(L.RES, "t2_certs.jsonl")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try:
                c = json.loads(line)
            except Exception:
                continue
            for nid in CELLS:
                if c["tag"].startswith(nid + "__"):
                    certs[c["tag"]] = c["result"]

    verdict = "PASS"
    notes = []
    for cfg in CFGS:
        realising = bool(rows[cfg]["realising"])
        for nid in CELLS:
            for e, d in cells[nid].items():
                if d["cfg"] != cfg:
                    continue
                killed = any(k.startswith(nid + "__" + cfg + "__") and v == "PASS"
                             for k, v in certs.items())
                if realising and killed:
                    verdict = "FAIL"
                    notes.append("%s %s CERTIFIED DEAD while Trump realises the hypothesis" %
                                 (nid, cfg))
                elif realising:
                    notes.append("%s %s survives (Trump realises: must not die) -- OK" % (nid, cfg))
                else:
                    notes.append("%s %s: Trump does NOT realise the hypothesis at this a_w, so a "
                                 "kill here would be sound (verdict %s)" % (nid, cfg, d["verdict"]))
    out = dict(images=rows, cells=cells, certs=certs, verdict=verdict, notes=notes)
    json.dump(out, open(OUT, "w"), indent=1)
    for n in notes:
        log("  " + n)
    log("CANARY VERDICT: %s" % verdict)


if __name__ == "__main__":
    main()
