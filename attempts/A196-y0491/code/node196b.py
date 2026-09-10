"""A196 step 1 driver: record -> base node -> the cases at TR(0,1) -> unit propagation -> meet clip -> sharp
fixed point -> invariant -> no-room leaf -> results/node_<nid>.json (one entry per surviving case).

    python node196b.py <nid> [--nsub 4 --refine 2 --sharp 8/3 --deadline 700]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, HERE)
import node196 as N                                              # noqa: E402
import geo178 as G                                               # noqa: E402  READ-ONLY (A178)
sys.path.insert(0, os.path.join(N.ATT, "A189-noroom", "code"))
import noroom189 as NR                                           # noqa: E402  READ-ONLY (A189)

os.makedirs(RES, exist_ok=True)


def find_record(nid):
    import glob
    for p in glob.glob(os.path.join(N.ATT, "A57-shadow-trees", "results", "tree", "*", nid + ".json")):
        return os.path.relpath(p, N.ROOT).replace("\\", "/")
    return None


def build(nid, record=None, nsub=4, refine=2, sharp=(8, 3), deadline=700.0, log=print, noroom=True):
    t0 = time.time()
    record = record or find_record(nid)
    rec = G.load_record(record)
    cls = G.class_of_record(rec)
    base = G.base_roles(rec)
    pinroles = {k: v for k, v in base.items() if k.startswith("P")}
    items = {it["cell"]: it for it in G.forced_items(cls, rec)}
    item = items[N.CELL]
    out = dict(nid=nid, cls=cls, record=record, budget=rec["budget"], n_pins=len(rec["pins"]), H=list(base["H"]),
               cell=N.CELL, wbox=item["wbox"], window=item["window"], nsub=nsub, refine=refine, sharp=list(sharp),
               when=time.strftime("%Y-%m-%d %H:%M"), steps=[])
    # ---- 1a base node (pins + H)
    nd0, info0 = G.run_node(base, nsub=nsub, refine=refine, label="base")
    out["steps"].append(dict(step="base", premise="pins + H normalise (A171 fixed point)", dead=info0.get("dead"),
                             seconds=info0["seconds"], kept=info0.get("kept")))
    if info0["dead"]:
        out.update(verdict="DEAD", leaf="base node dead (A171 pair leaf: %s)" % info0["dead"], seconds=round(time.time() - t0, 1))
        return out
    hull = {"H": N._hull(nd0, "H")}
    out["base"] = N.snapshot(nd0, info0, base)
    # ---- 1b who can reach TR(0,1): pins never (Theorem FC: NON-pin meeters); H by A161's exact test
    m = nd0.misses_cell(tuple(item["wbox"]))
    h_misses = bool(m["H"]["misses"])
    out["steps"].append(dict(step="reach", premise="A161 exact miss test of H's fixed-point box vs B+(TR(0,1))",
                             H_misses=h_misses, result=("H provably misses B+: both meeters are FREE" if h_misses
                                                        else "H may meet B+: the H-meets case is open")))
    log("  reach: H %s B+" % ("misses" if h_misses else "may meet"))
    # ---- 1c the cases (geo178b pair test) at nsub/refine
    cases, crep = N.cases_at_cell(rec, cls, item, hull, pinroles, nsub, refine, log)
    sub = {s["case"]: s for s in crep["pair_test"]["subcases"]}
    out["steps"].append(dict(step="pair-test", premise="geo178b slot_pair_test at %d/%d (H-meets vs two-free cell pairs, Lemma A1)" % (nsub, refine),
                             subcases=crep["pair_test"]["subcases"], seconds=crep["pair_test"]["seconds"], cases=crep["cases"],
                             result=("TR(0,1) FORCES the H-meets case: H is a meeter and exactly one free square F1" if crep["cases"] == ["H-meets"]
                                     else ("two-free only" if crep["cases"] and all(c.startswith("two-free") for c in crep["cases"])
                                           else ("no case alive" if not crep["cases"] else "several cases: %s" % crep["cases"])))))
    out["pair_test"] = crep["pair_test"]
    if not cases:
        out.update(verdict="DEAD", leaf="two-meeter requirement at TR(0,1): H-meets dead/vacuous and no Lemma A1 cell pair alive (A178 geo178b)",
                   seconds=round(time.time() - t0, 1))
        return out
    # ---- 1d per case: propagation, meet clip, sharp, invariant, no-room
    out["cases"] = []
    for case in cases:
        log("== case %s" % case["label"])
        c = dict(label=case["label"], why=case["why"], members=case["members"], roles_in={k: list(v) for k, v in case["roles"].items()})
        pr = N.propagate_case(rec, cls, case, nsub, refine, log, deadline_s=deadline)
        c["propagation"] = {k: v for k, v in pr.items() if k not in ("steps", "roles")}
        c["prop_steps"] = [{k: v for k, v in s.items() if k not in ("hull",)} for s in pr["steps"]]
        if pr["verdict"] == "DEAD":
            c.update(verdict="DEAD", leaf=pr["leaf"])
            out["cases"].append(c)
            continue
        roles = {k: tuple(v) for k, v in pr["roles"].items()}
        must = {}
        for cell, mem in pr["assign"].items():
            for r in mem:
                must.setdefault(r, []).append(tuple(items[cell]["wbox"]))
        c["must_meet"] = {r: [list(x) for x in v] for r, v in must.items()}
        t1 = time.time()
        nd, info, mrep = N.meet_clip(roles, must, nsub, refine, log, label=case["label"] + "/meet")
        c["meet_clip"] = dict(rounds=mrep, seconds=round(time.time() - t1, 1))
        if nd is None:
            c.update(verdict="DEAD", leaf="meet clip / pair leaf: %s" % info.get("dead"))
            out["cases"].append(c)
            continue
        roles = {k: tuple(N._hull(nd, k)) for k in nd.boxes}
        t2 = time.time()
        nds, infos = G.run_node(roles, nsub=sharp[0], refine=sharp[1], label=case["label"] + "/sharp")
        c["sharp"] = dict(dead=infos.get("dead"), seconds=infos["seconds"], kept=infos.get("kept"), invariant=infos.get("invariant"),
                          failures=infos.get("failures"))
        if infos["dead"]:
            c.update(verdict="DEAD", leaf="sharp node dead (A171 pair leaf at %d/%d: %s)" % (sharp[0], sharp[1], infos["dead"]))
            out["cases"].append(c)
            continue
        nd, info = nds, infos                                    # [T] both passes sound; keep the sharper
        c["node"] = N.snapshot(nd, info, roles)
        c["k"] = len(roles)
        c["free"] = 11 - len(roles)
        log("  sharp fixed point: kept %s  invariant %s  (%.0f s)" % ({k: v for k, v in info["kept"].items() if not k.startswith("P")},
                                                                     info["invariant"], time.time() - t2))
        if noroom:
            t3 = time.time()
            try:
                r = NR.noroom(roles, nd=nd, budget=dict(total_deadline=400.0, lane_deadline=120.0))
            except Exception as e:                               # noqa: BLE001
                r = dict(verdict="ERROR", reason=repr(e)[:200])
            r["seconds"] = round(time.time() - t3, 1)
            c["noroom"] = {k: v for k, v in r.items() if k != "bisect"}
            c["noroom"]["bisect"] = {k: v for k, v in (r.get("bisect") or {}).items() if k not in ("pieces",)} if isinstance(r.get("bisect"), dict) else r.get("bisect")
            log("  no-room: %s (%s; %.0f s)" % (r.get("verdict"), r.get("reason"), r["seconds"]))
            if r.get("verdict") == "DEAD":
                c.update(verdict="DEAD", leaf="NO-ROOM (A189 Lemma 1): %s" % r.get("reason"))
                out["cases"].append(c)
                continue
        c["verdict"] = "OPEN"
        out["cases"].append(c)
    alive = [c for c in out["cases"] if c["verdict"] != "DEAD"]
    out["verdict"] = "OPEN" if alive else "DEAD"
    if not alive:
        out["leaf"] = "every case dead: " + "; ".join("%s: %s" % (c["label"], c["leaf"]) for c in out["cases"])
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--sharp", default="8/3")
    ap.add_argument("--deadline", type=float, default=700.0)
    ap.add_argument("--no-noroom", action="store_true")
    a = ap.parse_args()
    sh = tuple(int(v) for v in a.sharp.split("/"))
    out = build(a.nid, nsub=a.nsub, refine=a.refine, sharp=sh, deadline=a.deadline, noroom=not a.no_noroom)
    p = os.path.join(RES, "node_%s.json" % a.nid)
    json.dump(out, open(p, "w", encoding="utf-8"), indent=0)
    print("== %s: %s %s (%.0f s) -> %s" % (a.nid, out["verdict"], out.get("leaf") or "", out["seconds"], p), flush=True)


if __name__ == "__main__":
    main()
