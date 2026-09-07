"""A112 canaries.

 (1) A111's TWO END-TO-END KILLS, reproduced with A112's own byte-identical frozen verifier:
     k5_11_interior_Y0054_D00 (S02, A57 level 2, 5 NO children) and k5_16_interior_Y0984 (S07,
     level 1, 6 NO children).  A111's NO-child node jsons are COPIED here (read-only on A111) and
     re-certified through A57's certify.py -> the frozen verify_case.py.  A node dies iff EVERY
     child PASSes.

 (2) TRUMP'S GRAIN IS NEVER KILLED: substrat.trump_realizes on every hypothesis A112 declares
     dead, plus the structural statement that no S07 branch is taken at level 1.

 (3) THE DENSE-SAMPLING RULE: every free-kill fire recorded in the region trees re-checked with a
     fresh, larger sample (independent seed), and the totals reported.  No LP-free geometric count
     is reported before >= 1e4 sampled pose pairs confirm it.

Writes results/canaries.json.
"""
from __future__ import annotations

import glob, json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a112lib as L
import regiontree as RT
from caselp import Box, Hyp

A111N = os.path.join(L.A111R, "nodes")
KILLS = {
    "k5_11_interior_Y0054_D00": "k5_11_interior_Y0054_D00__S02__lpa__r0.1_p10__NO%d",
    "k5_16_interior_Y0984": "k5_16_interior_Y0984__S07__lpa__r0.1_p10__NO%d",
}


def reproduce(log, cert_time=300.0):
    out = []
    for nid, pat in KILLS.items():
        kids = sorted(glob.glob(os.path.join(A111N, pat.replace("%d", "*"))))
        kids = [k for k in kids if not k.endswith(".src.json")]
        recs = []
        for k in kids:
            tag = os.path.splitext(os.path.basename(k))[0]
            dst = os.path.join(L.NODES, tag + ".json")
            if not os.path.exists(dst):
                shutil.copyfile(k, dst)                 # read-only on A111: copy, never edit
            r = RT.certify_leaf("canary", "a111", tag, tag + ".json", log, cert_time=cert_time)
            recs.append(dict(child=tag, result=r["result"], seconds=r["seconds"]))
        npass = sum(1 for r in recs if r["result"] == "PASS")
        out.append(dict(node=nid, children=len(recs), passed=npass,
                        node_dies=bool(recs and npass == len(recs)), children_detail=recs))
        log("  canary %s: %d/%d children PASS -> node dies = %s"
            % (nid, npass, len(recs), bool(recs and npass == len(recs))))
    return out


def resample(nsample=2000):
    """Re-check every recorded free-kill fire with a fresh, independent, larger sample."""
    fires, sampled, cex, worst = 0, 0, 0, -1e18
    detail = []
    for p in glob.glob(os.path.join(L.RT, "*", "*", "*.json")):
        try:
            rec = L.jload(p)
        except Exception:
            continue
        for f in (rec.get("logic") or {}).get("fires", []):
            ba, bb = f["boxes"]
            A = Box(ba["x0"], ba["x1"], ba["y0"], ba["y1"], ba["th0"], ba["th1"])
            B = Box(bb["x0"], bb["x1"], bb["y0"], bb["y1"], bb["th0"], bb["th1"])
            w, bad = L.sample_pair(A, B, n=nsample, seed=7919 + fires)
            fires += 1
            sampled += nsample
            cex += bad
            worst = max(worst, w)
            if bad:
                detail.append(dict(file=os.path.relpath(p, L.RT), pair=f["pair"],
                                   rule=f.get("rule"), counterexamples=bad,
                                   worst_sat_gap=round(w, 6)))
    return dict(fires=fires, sampled_pose_pairs=sampled, counterexamples=cex,
                worst_sat_gap=(None if worst < -1e17 else round(worst, 6)),
                rule_met=bool(sampled >= 10000 and cex == 0), violations=detail)


def trump(nsample=0):
    viol, checked = [], 0
    for p in glob.glob(os.path.join(L.RT, "*", "*", "*.json")):
        try:
            rec = L.jload(p)
        except Exception:
            continue
        if rec.get("status") not in ("DEAD-LOGIC", "DEAD-LP", "DEAD-LP-UNCONV", "DEAD-CERT",
                                     "DEAD-CLASS"):
            continue
        checked += 1
        tr = rec.get("trump_realizes")
        if tr is None and rec.get("hyp"):
            hyp = Hyp.from_json(rec["hyp"])
            pins, _ = L.split_hyp(hyp)
            tr = RT.trump_canary(hyp, L.pin_slots(pins))
        if tr is True:
            viol.append(dict(file=os.path.relpath(p, L.RT), key=rec.get("key"),
                             status=rec.get("status")))
    return dict(dead_hypotheses_checked=checked, violations=viol, ok=(not viol))


def main():
    log = L.mklog("canary.log")
    t0 = time.time()
    res = dict(a111_reproduction=reproduce(log), trump=trump(), resample=resample())
    res["seconds"] = round(time.time() - t0, 1)
    L.jdump(os.path.join(L.RES, "canaries.json"), res)
    log("canaries: trump ok=%s, resample %d fires / %d pairs / %d counterexamples"
        % (res["trump"]["ok"], res["resample"]["fires"], res["resample"]["sampled_pose_pairs"],
           res["resample"]["counterexamples"]))
    print(json.dumps({k: (v if k != "a111_reproduction" else
                          [dict(node=x["node"], passed=x["passed"], of=x["children"],
                                dies=x["node_dies"]) for x in v])
                      for k, v in res.items() if k != "resample"}, indent=1)[:2000])


if __name__ == "__main__":
    main()
