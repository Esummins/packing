"""Assemble t3b/results/tau12_crossing.json: tau*(s) for s >= 3.877084 and the s where it crosses 12.

tau*(s) < n  ==>  s(n) >= s  (Theorem 1, docs/results.md).  The crossing tau*(s) = 12 is therefore
the exact CEILING of every lower bound on s(12) obtainable by the measure/LP method.
"""
import glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
A33 = os.path.dirname(HERE)

pts = []
# T1's anchor at s = 3.877084
t1 = json.load(open(os.path.join(A33, "t1", "results", "eta_table.json")))
for r in t1:
    v = r["row_violation"] or 0.0
    pts.append(dict(s=r["s"], tau_LP=r["tau_LP"], row_violation=v,
                    tau_ub=r["tau_LP"] / (1 - v), tau_lb_opt=r.get("fracpack_lb_opt"),
                    source="t1/results/" + r["field"], converged=True))

for p in sorted(glob.glob(os.path.join(HERE, "results", "field_n12_s*.json"))):
    d = json.load(open(p))
    res = d.get("oracle_residuals") or {}
    pts.append(dict(s=d["s"], tau_LP=d["tau"], row_violation=res.get("row_violation"),
                    tau_ub=d.get("tau_ub"), tau_lb_opt=None, converged=d.get("converged"),
                    n_rows=d.get("n_rows"), n_orbits=d.get("n_orbits"),
                    wall_time_s=d.get("wall_time"), lp_verify_ok=(d.get("lp_verify") or {}).get("ok"),
                    source=os.path.basename(p)))
pts = {round(p["s"], 8): p for p in pts}
pts = [pts[k] for k in sorted(pts)]


def cross(key, target=12.0):
    """linear interpolation of the crossing tau = target on the recorded points"""
    xs = [(p["s"], p[key]) for p in pts if p.get(key) is not None]
    for (s0, v0), (s1, v1) in zip(xs, xs[1:]):
        if v0 < target <= v1:
            return s0 + (s1 - s0) * (target - v0) / (v1 - v0)
    if xs and xs[-1][1] < target:                # extrapolate off the last segment
        (s0, v0), (s1, v1) = xs[-2], xs[-1]
        return s1 + (s1 - s0) * (target - v1) / (v1 - v0)
    return None


certs = []
for p in sorted(glob.glob(os.path.join(HERE, "certs", "*.report.json"))):
    r = json.load(open(p))
    certs.append(dict(cert=r["cert"], report=os.path.basename(p), s=r["s"], s_float=float(r["s_float"])
                      if "s_float" in r else None, n=r["n"], total=r["total"],
                      total_float=r["total_float"], result=r["result"],
                      slack_to_12=12 - r["total_float"], time_s=r.get("time_s"),
                      scale_weights=r.get("scale_weights"), atoms=r.get("atoms")))

out = dict(
    quantity="tau*(s) = min total mass of an atomic guard field on [0,s]^2 giving every "
             "eps-shrunk closed unit square (eps = 1e-4) mass >= 1",
    theorem="tau*(s) < n  ==>  s(n) >= s   (docs/results.md Theorem 1, certs/verify_measure.py)",
    points=pts,
    crossing_tau_eq_12=dict(
        from_tau_LP=cross("tau_LP"),
        from_tau_ub=cross("tau_ub"),
        comment="tau_ub = tau_LP/(1-row_violation) is a rigorous upper bound on tau* given the "
                "field (scaling a field whose worst placement carries 1-v by 1/(1-v) makes it "
                "feasible); tau_LP is the raw LP value, an under-estimate while rows are missing. "
                "The true crossing lies between the two interpolations."),
    prior_state=dict(best_published_lower_bound_s12=3.7889,
                     t1_sealed=dict(s="969271/250000", s_float=3.877084, total_float=11.425399552,
                                    file="t1/certs/A33_measure_feasible_3.877084.json",
                                    note="T1's sealed feasibility certificate already implies "
                                         "s(12) >= 3.877084 by Theorem 1 (total < 12)")),
    certificates=certs)
json.dump(out, open(os.path.join(HERE, "results", "tau12_crossing.json"), "w"), indent=1)

print(f"{'s':>10} {'tau_LP':>10} {'tau_ub':>10} {'rowviol':>9} {'conv':>6}  source")
for p in pts:
    f = lambda v, k=6: ("%.*f" % (k, v)) if isinstance(v, (int, float)) else "  -"
    print(f"{p['s']:>10.6f} {f(p['tau_LP']):>10} {f(p.get('tau_ub')):>10} "
          f"{f(p.get('row_violation')):>9} {str(p.get('converged'))[:5]:>6}  {p['source']}")
print(f"\ncrossing tau*=12 :  from tau_LP  s ~ {out['crossing_tau_eq_12']['from_tau_LP']}")
print(f"                    from tau_ub  s ~ {out['crossing_tau_eq_12']['from_tau_ub']}")
for c in certs:
    print(f"cert {c['report']}: s={c['s']} total={c['total_float']:.6f} {c['result']} "
          f"slack_to_12={c['slack_to_12']:.4f}")
