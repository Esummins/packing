"""A184 E3(d) -- the LP with the wastage folded in, three forms on the sample's S3 survivors:

  plain  lp183.PiecesHyp: one square core per role, the union-box A135 exact core GROWN inside
         K'(role) (four corners vertex_ok on every surviving piece), budget 11 - #roles; the frozen
         verifier's v1 clause (A183.4).
  zone   plain + U as NO-families: the zone Z = {c : dist(c, U) <= 1/2} (waste184.zone_rects, inner
         rects, all tilts).  A unit square with centre in Z contains a point of U, and U is a set no
         square of the packing can contain a point of (free squares by admissibility, the roles by
         their pose covers), so NO square of the packing has its centre in Z [T] -- exactly the
         verifier's nofams bridge, so the frozen verify_case.py CONSUMES this form as it stands.
         (U as "forbidden area" for the ATOMS adds nothing: an atom in U is inside no non-exempt
         placement; a row meeting U is exactly what this family exempts.)
  poly   the roles' PIECES as exemptions: a placement is dropped when it meets some K'(role)
         polygon by more than EPS_CORE (caselp.ROW_EXEMPT hook) -- a superset of both exemptions
         above (a row meeting U meets some K' or leaves the container [T]); NO certificate under
         the frozen verifier: needs the v4 clause hypotheses.poly_cores = [{vertices}] with the
         exemption "Q meets the closed convex polygon" by exact SAT (A183.4).

    python lp184.py [--max_nodes 8] [--cap 200] [--forms plain,zone,poly]  -> results/lp184.jsonl
"""
import argparse
import json
import os
import time
from fractions import Fraction as Fr

import numpy as np

import common184 as C
from common184 import K, RS
import lp168 as L                                                # noqa: E402  (A168, read-only)
import lp183 as L3                                               # noqa: E402
import polycore                                                  # noqa: E402
import caselp                                                    # noqa: E402  (A57, read-only)
from caselp import NoFam, solve_node                             # noqa: E402
import certwrap170 as CW                                         # noqa: E402  (A170, read-only)

OUT = os.path.join(C.RES, "lp184.jsonl")
WASTE = os.path.join(C.RES, "waste184.jsonl")


def certify184(res, hyp, budget, tag, time_limit=150, jobs=2):
    """lp168.certify's shape, writing under THIS attempt's certs/: A170's exact-core certificate,
    the frozen verifier at depth 56, a FAIL with 0 holes replayed at 64 / 72 before giving up."""
    CW.assert_frozen()
    out = os.path.join(C.CERTS, tag + ".json")
    tau = res["tau"]
    scale = max(1.005, min(1.30, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005
    cert = CW.make_certificate_exact(res, K.S_RAT, scale=scale, hyp=hyp)
    json.dump(cert, open(out, "w"), indent=0)
    tot = float(Fr(cert["total"]))
    log = [dict(tau=tau, total=tot, scale=scale, n_nofams=len((cert.get("hypotheses") or {}).get("nofams") or []))]
    if tot >= budget:
        log[-1]["result"] = "MARGIN"
        return "MARGIN", log
    for dp in (56, 64, 72):
        rc, txt = CW.run_frozen_verifier(out, jobs=jobs, depth=dp, timeout=time_limit * 4)
        tail = CW.verifier_tail(txt)
        log.append(dict(depth=dp, rc=rc, verifier=tail[:4]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=log, result="PASS", verifier=CW.FROZEN, verifier_sha=CW.FROZEN_SHA),
                      open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "PASS", log
        if rc is None or any("hole" in l and "0 hole" not in l for l in tail):
            break
    json.dump(dict(cert=out, rounds=log, result="FAIL", verifier=CW.FROZEN, verifier_sha=CW.FROZEN_SHA),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", log


def poly_exempt(polys, eps=caselp.EPS_CORE):
    """caselp.ROW_EXEMPT: drop a placement when its square meets some K' polygon by depth > eps."""
    P = [np.asarray(p, float) for p in polys]

    def f(th_deg, Cc, keep):
        th = np.radians(th_deg)
        out = np.zeros(len(Cc), bool)
        TH = np.full(len(Cc), th)
        for p in P:
            out |= polycore.poly_square_depth(p, Cc, TH) > eps
        return out
    return f


def solve_form(form, roles, zone, budget, cap, warm, tag, cert_time):
    t0 = time.time()
    H = L3.PiecesHyp(roles)
    rec = dict(form=form, a_pieces=H.a_pieces, a_union_exact=H.a_union_exact, names=H.names)
    if form == "zone":
        H.nofams = [NoFam(x0, x1, y0, y1, [(0.0, 90.0)]) for (x0, x1, y0, y1) in zone]
        rec["n_nofams"] = len(H.nofams)
    caselp.ROW_EXEMPT = poly_exempt([[(float(Fr(v[0])), float(Fr(v[1]))) for v in r.core] for r in roles]) if form == "poly" else None
    try:
        gate = all(L.cores_disjoint_exact(H.cores[i], H.cores[j])[0] for i in range(len(H.cores)) for j in range(i + 1, len(H.cores)))
        if not gate:
            rec.update(verdict="UNDECIDED(core gate)", wall_s=round(time.time() - t0, 1))
            return rec
        s = solve_node(K.S0, H, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900, out=None,
                       log=lambda *x: None, prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                       max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], wall_s=round(time.time() - t0, 1))
        return rec
    finally:
        caselp.ROW_EXEMPT = None
    tau = s.get("tau")
    rec.update(tau=tau, eta=(tau - budget) if tau is not None else None, converged=bool(s.get("converged")),
               minmass=s.get("minmass"), n_rows=s.get("n_rows"), t_lp=round(time.time() - t0, 1),
               kills=bool(tau is not None and tau < budget - 1e-6),
               kills_converged=bool(s.get("converged") and tau is not None and tau < budget - 1e-6))
    if rec["kills_converged"] and form != "poly":
        t1 = time.time()
        v, log = certify184(s, H, budget, tag + "_" + form, time_limit=cert_time)
        rec.update(certified=v, cert_log=log, t_cert=round(time.time() - t1, 1))
    rec["verdict"] = ("DEAD(LP)" if rec.get("certified") == "PASS"
                      else ("DEAD(LP, %s)" % ("no frozen clause: needs v4 poly_cores" if form == "poly" else "certificate pending")
                            if rec["kills_converged"] else ("LP-dead unconverged (kill candidate)" if rec["kills"] else "ALIVE(LP)")))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max_nodes", type=int, default=8)
    ap.add_argument("--cap", type=float, default=200)
    ap.add_argument("--cert_time", type=float, default=150)
    ap.add_argument("--forms", default="plain,zone,poly")
    ap.add_argument("--keys", default="")
    ap.add_argument("--exps", default="f,c")
    a = ap.parse_args()
    C.set_process()
    import run184 as RU
    recs = RU.load_all(2)
    waste = C.load_jsonl(WASTE)
    done = C.load_jsonl(OUT)
    if a.keys:
        keys = a.keys.split(",")
    else:
        keys = []
        for e in a.exps.split(","):
            keys += sorted(k for k, r in recs.items() if r.get("exp") == e and r.get("step") == "S3"
                           and r["verdict"].startswith("ALIVE") and k in waste)
    keys = [k for k in keys if k not in done][:a.max_nodes]
    print("lp184: %d nodes, forms %s, cap %.0fs" % (len(keys), a.forms, a.cap), flush=True)
    warm = L.load_warm(C.CELL)
    for key in keys:
        r = recs[key]
        roles = C.roles_from_json(r["roles"])
        budget = 11 - len(roles)
        rec = dict(key=key, exp=r.get("exp"), setting=r.get("setting"), budget=budget, kept=r.get("kept"),
                   area_U=waste[key]["area_U"], zone_n_rects=waste[key]["zone_n_rects"], forms={})
        tag = "lp184_" + key.replace("|", "_").replace("/", "_")
        for form in a.forms.split(","):
            if RS.memory_gate(tag=tag) is None:
                rec["forms"][form] = dict(verdict="SKIPPED(memory gate)")
                continue
            with C.NodeWall("lp|" + key + "|" + form):
                rec["forms"][form] = solve_form(form, roles, waste[key]["zone_rects"], budget, a.cap, warm, tag, a.cert_time)
            f = rec["forms"][form]
            print("  %-30s %-5s b=%d tau=%s conv=%s %s %.0fs" % (key, form, budget, f.get("tau"), f.get("converged"),
                                                                 f.get("verdict"), f.get("wall_s", 0)), flush=True)
        C.append_jsonl(OUT, rec)


if __name__ == "__main__":
    main()
