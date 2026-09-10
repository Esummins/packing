"""A196 step 4, the two legs.   python lp196b.py <nid> --leg a|b [--case LABEL] [--cap 300] [--wall 1500] [--zone 1]"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lp196 as L                                                # noqa: E402
import prio196                                                   # noqa: E402
import cert191 as C                                              # noqa: E402
import lines191 as LN                                            # noqa: E402
import emit190 as E                                              # noqa: E402
import winlp185 as W                                             # noqa: E402
import rows196 as RW                                             # noqa: E402
from caselp import Box                                           # noqa: E402
from lp168 import cores_disjoint_exact                           # noqa: E402  READ-ONLY (A168)

RES = L.RES


def load_inputs(nid, case_label=None):
    nodes = json.load(open(os.path.join(RES, "node_%s.json" % nid), encoding="utf-8"))
    cases = [c for c in nodes.get("cases", []) if c.get("verdict") != "DEAD"]
    if case_label:
        cases = [c for c in cases if c["label"] == case_label]
    case = cases[0]
    wp = os.path.join(RES, "waste_%s__%s.json" % (nid, case["label"].replace(":", "_").replace("+", "-")))
    waste = json.load(open(wp, encoding="utf-8")) if os.path.exists(wp) else None
    rp = os.path.join(RES, "rows_%s__%s.json" % (nid, case["label"].replace(":", "_").replace("+", "-")))
    rws = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else None
    return nodes, case, waste, rws


def leg_a(nid, nodes, case, waste, rws, a, log=print):
    t0 = time.time(); deadline = t0 + a.wall
    node = case["node"]
    tag = "%s__%s_a" % (nid, case["label"].replace(":", "_").replace("+", "-"))
    rec = dict(nid=nid, case=case["label"], leg="a", cap=a.cap, when=time.strftime("%Y-%m-%d %H:%M"))
    cored, uncored = {}, []
    for k, h in node["hull"].items():
        b = Box(*h)
        if b.core() is not None:
            cored[k] = b
        else:
            uncored.append(k)
    nfs = L.nofams_of((waste or {}).get("zone_rects_nofam", [])) if (a.zone and waste) else []
    H = E.ExactHyp(list(cored.values()), nfs)
    bud = L.N - H.m()
    gate = [cores_disjoint_exact(H.cores[i], H.cores[j])[0] for i in range(H.m()) for j in range(i + 1, H.m())]
    rec.update(cored=list(cored), uncored=uncored, budget=bud, n_nofams=len(nfs), exact_ok=H.exact_ok, exact_gap=H.exact_gap,
               a_exact=H.a_exact, cores_disjoint=all(gate))
    if not all(gate):
        rec.update(verdict="UNDECIDED(core gate: exact cores not certifiably disjoint)", wall_s=round(time.time() - t0, 1))
        return rec
    warm, d = L.warm_of(nodes["record"], nodes["cls"])
    fam = L.line_family(node, RW.pin_lines(sweep=8))
    lines, lrep = LN.select(d.get("packing") or [], fam, k=a.lines, boxes=list(cored.values()))
    rec.update(n_family=len(fam), lines=lrep)
    ok, mem = prio196.wait_box(own=0, max_wait=3600, log=log)
    rec["gate"] = mem
    if not ok:
        rec.update(verdict="[P] box gate (LP not run)", wall_s=round(time.time() - t0, 1))
        return rec
    t1 = time.time()
    try:
        res, z = C.solve_guarded(H, bud, lines, warm, a.cap)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return rec
    tau = res.get("tau")
    json.dump(dict(tau=tau, converged=res.get("converged"), atoms_all=res.get("atoms_all"), rows_all=(res.get("rows_all") or [])[:20000],
                   packing=res.get("packing"), n_rows=res.get("n_rows"), minmass=res.get("minmass"), hyp=res.get("hyp"), z=z,
                   lines=[Ln.to_json() for Ln in lines]), open(os.path.join(RES, "lpres_%s.json" % tag), "w"))
    n_active = sum(1 for zz in z if zz > 1e-6)
    rec.update(tau=tau, eta=(tau - bud) if tau is not None else None, converged=bool(res.get("converged")), minmass=res.get("minmass"),
               n_rows=res.get("n_rows"), support=L.support_kind(res.get("packing")), n_active=n_active,
               z=[dict(line=Ln.to_json(), z=zz, rhs=float(Ln.rhs_exact)) for Ln, zz in zip(lines, z)], lp_s=round(time.time() - t1, 1),
               kills=bool(tau is not None and tau < bud - 1e-6), kills_converged=bool(res.get("converged") and tau is not None and tau < bud - 1e-6))
    if rec["kills_converged"]:
        if n_active == 0:
            v, lg, path = L.frozen_certify(res, H, tag, deadline, log)
            rec.update(certified=v, cert_log=lg, cert=os.path.relpath(path, L.ROOT).replace("\\", "/"), verifier="frozen verify_case.py (A143 copy, sha 521cb01f...)")
        else:
            def mk(r, zz, sc):
                cert = E.make_certificate_v5(r, H, lines, zz, sc, tag)
                cert["hypotheses"]["nofams"] = L.nofams_json(nfs)
                return cert
            v, lg, path = C.certify(res, z, H, lines, tag, deadline, rounds=2, log=log, make=mk, budget=bud)
            rec.update(certified=v, cert_log=lg, cert=os.path.relpath(path, L.ROOT).replace("\\", "/"), verifier="verify_case_v5 (A190) [C under v5 ONLY]")
    rec["verdict"] = ("DEAD(LP exact-core, %s)" % ("frozen-certified" if n_active == 0 else "v5-certified") if rec.get("certified") == "PASS"
                      else ("LP-dead, certificate %s (kill candidate)" % rec.get("certified") if rec["kills_converged"]
                            else ("LP-dead unconverged at cap (kill candidate)" if rec["kills"]
                                  else ("ALIVE(LP exact-core; converged)" if rec["converged"] else "ALIVE(LP exact-core; unconverged at cap)"))))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def leg_b(nid, nodes, case, waste, rws, a, log=print):
    t0 = time.time(); deadline = t0 + a.wall
    node = case["node"]
    tag = "%s__%s_b" % (nid, case["label"].replace(":", "_").replace("+", "-"))
    rec = dict(nid=nid, case=case["label"], leg="b", cap=a.cap, when=time.strftime("%Y-%m-%d %H:%M"))
    wroles = [W.WRole(k, node["pieces"][k]) for k in node["pieces"]]
    H = W.WindowsHyp(wroles)
    nfs = L.nofams_of((waste or {}).get("zone_rects_nofam", [])) if (a.zone and waste) else []
    H.nofams = nfs
    rec.update(n_cores=H.m, budget=H.budget4, free=H.free, n_nofams=len(nfs), core_kind={w.name: w.core_kind for w in wroles},
               a_core={w.name: (float(w.core.a) if w.core else None) for w in wroles})
    gate = [cores_disjoint_exact(H.cores[i], H.cores[j])[0] for i in range(H.m) for j in range(i + 1, H.m)]
    rec["cores_disjoint"] = all(gate)
    if not all(gate):
        rec.update(verdict="UNDECIDED(core gate)", wall_s=round(time.time() - t0, 1))
        return rec
    warm, d = L.warm_of(nodes["record"], nodes["cls"])
    fam = L.line_family(node, RW.pin_lines(sweep=8))
    lines, lrep = LN.select(d.get("packing") or [], fam, k=a.lines)
    rec.update(n_family=len(fam), lines=lrep)
    ok, mem = prio196.wait_box(own=0, max_wait=3600, log=log)
    rec["gate"] = mem
    if not ok:
        rec.update(verdict="[P] box gate (LP not run)", wall_s=round(time.time() - t0, 1))
        return rec
    t1 = time.time()
    try:
        res, z = C.solve_guarded(H, H.budget4, lines, warm, a.cap)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return rec
    tau = res.get("tau")
    json.dump(dict(tau=tau, converged=res.get("converged"), atoms_all=res.get("atoms_all"), rows_all=(res.get("rows_all") or [])[:20000],
                   packing=res.get("packing"), n_rows=res.get("n_rows"), minmass=res.get("minmass"), hyp=res.get("hyp"), z=z,
                   lines=[Ln.to_json() for Ln in lines]), open(os.path.join(RES, "lpres_%s.json" % tag), "w"))
    n_active = sum(1 for zz in z if zz > 1e-6)
    rec.update(tau=tau, eta=(tau - H.budget4) if tau is not None else None, converged=bool(res.get("converged")), minmass=res.get("minmass"),
               n_rows=res.get("n_rows"), support=L.support_kind(res.get("packing")), n_active=n_active,
               z=[dict(line=Ln.to_json(), z=zz) for Ln, zz in zip(lines, z)], lp_s=round(time.time() - t1, 1),
               kills=bool(tau is not None and tau < H.budget4 - 1e-6),
               kills_converged=bool(res.get("converged") and tau is not None and tau < H.budget4 - 1e-6))
    if rec["kills_converged"]:
        def mk(r, zz, sc):
            cert = C.make_certificate(r, H, lines, zz, sc, tag)
            cert["hypotheses"]["nofams"] = L.nofams_json(nfs)
            return cert
        v, lg, path = C.certify(res, z, H, lines, tag, deadline, rounds=2, log=log, make=mk)
        rec.update(certified=v, cert_log=lg, cert=os.path.relpath(path, L.ROOT).replace("\\", "/"), verifier="verify_case_v5 (A190) [C under v5 ONLY]")
    rec["verdict"] = ("DEAD(LP windows+lines, v5-certified) [C under v5 ONLY]" if rec.get("certified") == "PASS"
                      else ("LP-dead, certificate %s (kill candidate)" % rec.get("certified") if rec["kills_converged"]
                            else ("LP-dead unconverged at cap (kill candidate)" if rec["kills"]
                                  else ("ALIVE(LP windows+lines; converged)" if rec["converged"] else "ALIVE(LP windows+lines; unconverged at cap)"))))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--leg", default="a")
    ap.add_argument("--case", default="")
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--lines", type=int, default=8)
    ap.add_argument("--zone", type=int, default=1)
    a = ap.parse_args()
    nodes, case, waste, rws = load_inputs(a.nid, a.case or None)
    if waste and "zone_rects_nofam" not in waste:
        import waste196 as WS
        waste["zone_rects_nofam"] = WS.nofam_rects(waste.get("zone_rects") or [])
    rec = (leg_a if a.leg == "a" else leg_b)(a.nid, nodes, case, waste, rws, a)
    p = os.path.join(RES, "lp_%s__%s_%s.json" % (a.nid, case["label"].replace(":", "_").replace("+", "-"), a.leg))
    json.dump(rec, open(p, "w", encoding="utf-8"), indent=0, default=str)
    print("== %s leg %s: %s tau=%s budget=%s conv=%s active=%s (%.0f s)" % (a.nid, a.leg, rec.get("verdict"), rec.get("tau"), rec.get("budget"),
                                                                            rec.get("converged"), rec.get("n_active"), rec.get("wall_s") or 0), flush=True)


if __name__ == "__main__":
    main()
