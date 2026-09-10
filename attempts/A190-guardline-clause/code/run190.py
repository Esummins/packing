"""A190 driver: the guard-line LP + v5 certificate on (a) the 23 S01 pages and the 11 S03 pages (A187/A188 lists,
records = the a57v4 gallery's A57 / A60 node records) and (b) A144's 20 in-vitro nodes as the control.  ONE
process (LP in-process, verify_case_v5 as a child: <= 2 lab pythons), per-node wall `--wall` (default 1,500 s):
LP cap `--cap`, then the certificate loop inside what is left.  Appends results/run190.jsonl (resumable: ids
already there are skipped unless --redo); the LP result of every node goes to results/lpres_<id>.json.

    python run190.py [--which s01|s03|control|all] [--only ID,ID] [--cap 420] [--wall 1500] [--lines 8]
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)
sys.path.insert(0, HERE)
import prio190                                                   # noqa: E402
import emit190 as E                                              # noqa: E402
import lines190 as LN                                            # noqa: E402
import guardline as G                                            # noqa: E402  (A144)
from caselp import warm_from_result                              # noqa: E402  (A57)
from warm57 import merged_warm                                   # noqa: E402  (A57)

OUT = os.path.join(RES, "run190.jsonl")
CONTROL_ORDER = ["k5_16_interior_Y0101", "k5_11_interior_Y0376", "k5_16_interior_Y0458", "k5_16_interior_Y0191"]


def load_pages(which):
    """[(id, family, cls, record rel path, best (orient, c), stored tau, sup_full)] in run order."""
    gal = {}
    for w in ("a57v4", "k0v4"):
        for e in json.load(open(os.path.join(ATT, "A148-gallery-v4", "results", "gallery148_%s.json" % w), encoding="utf-8")):
            gal[e["id"]] = e
    pages = []
    for ln in open(os.path.join(ATT, "A188-s01-basin", "results", "consumer188.jsonl"), encoding="utf-8"):
        if not ln.strip():
            continue
        r = json.loads(ln)
        if r.get("family") not in ("S01", "S03") or r.get("error"):
            continue
        b = r.get("best") or {}
        g = gal.get(r["nid"]) or {}
        pages.append(dict(id=r["nid"], family=r["family"], cls=r["cls"], record=g.get("record"),
                          best=((b["orient"], b["c"]) if b else None), tau_stored=g.get("tau"),
                          sup_full=b.get("support_full"), consumer_minchord=b.get("minchord")))
    # S01 first, the pages whose support already carries >= 3 full chords first, Y0147 first of all
    pages.sort(key=lambda p: (p["family"] != "S01", -(p["sup_full"] or 0), p["id"] != "k5_11_interior_Y0147", p["id"]))
    ctrl = []
    seen = set(p["id"] for p in pages)
    for f in ("invitro144_s0.jsonl", "invitro144_s1.jsonl"):
        for ln in open(os.path.join(ATT, "A144-guard-lines", "results", f), encoding="utf-8"):
            if ln.strip():
                r = json.loads(ln)
                if r["id"] in seen:
                    continue
                arms = r.get("arms") or {}
                ctrl.append(dict(id=r["id"], family="control", cls=r.get("cls"), record=r.get("record"), best=None,
                                 tau_stored=(r.get("control") or {}).get("tau"), sup_full=None,
                                 a144=dict(base=(arms.get("base") or {}).get("tau"), guard=(arms.get("guard") or {}).get("tau"))))
    ctrl.sort(key=lambda p: (p["id"] not in CONTROL_ORDER, CONTROL_ORDER.index(p["id"]) if p["id"] in CONTROL_ORDER else 0, p["id"]))
    out = []
    if which in ("s01", "all"):
        out += [p for p in pages if p["family"] == "S01"]
    if which in ("s03", "all"):
        out += [p for p in pages if p["family"] == "S03"]
    if which in ("control", "all"):
        out += ctrl
    return out


def emit(rec):
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print("%-26s %-7s tau %s -> %s (budget %s) conv=%s z>0:%s %s %ss" % (
        rec["id"], rec.get("family"), rec.get("tau_stored"), rec.get("tau"), rec.get("budget"), rec.get("converged"),
        rec.get("n_active"), rec.get("verdict"), rec.get("wall_s")), flush=True)


def one(p, a, warms):
    t0 = time.time()
    deadline = t0 + a.wall
    rec = dict(id=p["id"], family=p["family"], cls=p["cls"], record=p["record"], tau_stored=p["tau_stored"],
               a144=p.get("a144"), cap=a.cap, when=time.strftime("%Y-%m-%d %H:%M"))
    d = json.load(open(os.path.join(ROOT, p["record"].replace("\\", os.sep)), encoding="utf-8"))
    pins, hbox = G.node_boxes(d)
    bud = int(d.get("budget") or 5)
    rec.update(budget=bud, box=hbox.to_json(), n_pins=len(pins))
    fam, pcv = LN.family(pins, hbox, best=p.get("best"))
    lines, rows, nfam = LN.select(d, pins, hbox, fam, pcv, k=a.lines)
    rec.update(n_family=nfam, lines=rows)
    H = E.ExactHyp(pins + [hbox], [])
    rec["exact_cores"] = dict(ok=H.exact_ok, min_gap=H.exact_gap, a_exact=H.a_exact, a_stock=H.a_stock)
    cls = "trump5" if p["cls"].startswith("trump5") else p["cls"]
    if cls not in warms:
        if cls == "trump5":
            w = warm_from_result(d)
            w["rows"] = w["rows"][:a.warm_rows]
            warms[cls] = w
        else:
            warms[cls] = merged_warm(cls, max_rows=a.warm_rows)[0]
    warm = dict(atoms=list(warms[cls]["atoms"]), rows=list(warms[cls]["rows"]))
    w0 = warm_from_result(d)                                     # the record's own rows and atoms first
    warm["rows"] = list(w0["rows"]) + warm["rows"]
    warm["atoms"] = list(w0["atoms"]) + warm["atoms"]
    ok, mem = prio190.wait_box(own=0, max_wait=6 * 3600)
    rec["gate"] = mem
    if not ok:
        rec.update(verdict="[P] box gate (LP not run)", wall_s=round(time.time() - t0, 1))
        return rec
    try:
        res, z = E.solve_guarded(H, bud, lines, warm, a.cap)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return rec
    tau = res.get("tau")
    json.dump(dict(tau=tau, converged=res.get("converged"), atoms_all=res.get("atoms_all"), rows_all=res.get("rows_all"),
                   packing=res.get("packing"), n_rows=res.get("n_rows"), minmass=res.get("minmass"), hyp=res.get("hyp"),
                   z=z, lines=[L.to_json() for L in lines]),
              open(os.path.join(RES, "lpres_%s.json" % p["id"]), "w"))
    rec.update(tau=tau, eta=(tau - bud) if tau is not None else None, converged=bool(res.get("converged")),
               minmass=res.get("minmass"), maxcov=res.get("maxcov"), n_rows=res.get("n_rows"), support=len(res.get("packing") or []),
               z=[dict(line=L.to_json(), z=zz, rhs=float(L.rhs_exact)) for L, zz in zip(lines, z)],
               n_active=sum(1 for zz in z if zz > 1e-6), lp_s=round(time.time() - t0, 1),
               kills=bool(tau is not None and tau < bud - 1e-3))
    rec["packing_rows"] = [[q["cx"], q["cy"], q["theta"], q["y"]] for q in (res.get("packing") or [])][:200]
    if rec["kills"]:
        v, lg, path = E.certify_v5(res, z, H, lines, p["id"], deadline, rounds=a.rounds)
        rec.update(certified=v, cert_log=lg, cert=os.path.relpath(path, ROOT).replace("\\", "/"))
    rec["verdict"] = ("DEAD(LP, v5 certified) [C under v5 ONLY]" if rec.get("certified") == "PASS"
                      else ("LP-dead, v5 certificate %s (kill candidate)" % rec.get("certified") if rec["kills"] else "ALIVE(LP, guard lines)"))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="all")
    ap.add_argument("--only", default="")
    ap.add_argument("--cap", type=float, default=420.0)
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--lines", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--warm-rows", type=int, default=30000)
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--max-nodes", type=int, default=10 ** 6)
    a = ap.parse_args()
    pages = load_pages(a.which)
    if a.only:
        want = set(x.strip() for x in a.only.split(",") if x.strip())
        pages = [p for p in pages if p["id"] in want]
    done = set()
    if os.path.exists(OUT) and not a.redo:
        for ln in open(OUT, encoding="utf-8"):
            try:
                r = json.loads(ln)
                if not str(r.get("verdict", "")).startswith(("[P]", "ERROR")):
                    done.add(r["id"])
            except Exception:                                    # noqa: BLE001
                pass
    pages = [p for p in pages if p["id"] not in done][:a.max_nodes]
    print("run190: %d nodes (%d done before), cap %.0f wall %.0f lines %d" % (len(pages), len(done), a.cap, a.wall, a.lines), flush=True)
    warms = {}
    for p in pages:
        if os.path.exists(os.path.join(BASE, "PAUSE")):
            print("A190 PAUSE sentinel set; stopping cleanly", flush=True)
            break
        try:
            rec = one(p, a, warms)
        except Exception as e:                                   # noqa: BLE001
            rec = dict(id=p["id"], family=p["family"], error=repr(e)[:300], verdict="ERROR")
        emit(rec)


if __name__ == "__main__":
    main()
