"""Assemble the A33/T1 eta table from t1/results/field_*.json (+ certificate reports if present)."""
import glob, json, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
for p in sorted(glob.glob(os.path.join(HERE, "results", "field_*.json"))):
    if os.path.basename(p).count("_") != 1:      # skip archived variants like field_3.877084_r3.json
        continue
    d = json.load(open(p))
    r = d.get("oracle_residuals") or {}
    rows.append(dict(s=d["s"], tau_LP=d["tau"], eta_float=d["tau"] - 11,
                     nu_dual=d.get("nu_dual"), fracpack_lb=d.get("fracpack_lower_bound"),
                     eta_lb=(d["fracpack_lower_bound"] - 11) if d.get("fracpack_lower_bound") else None,
                     row_violation=r.get("row_violation"), maxcov_shrunk=r.get("maxcov_shrunk"),
                     maxcov_closed=r.get("maxcov_closed"), n_atoms=d.get("n_atoms"),
                     n_rows=d.get("n_rows"), n_orbits=d.get("n_orbits"),
                     lp_verify_ok=(d.get("lp_verify") or {}).get("ok"),
                     wall_time=d.get("wall_time"), field=os.path.basename(p)))
rows.sort(key=lambda r: r["s"])

# re-optimised fractional-packing lower bounds (fracpack_lb.py)
for p in sorted(glob.glob(os.path.join(HERE, "results", "fracpack_lb_*.json"))):
    d = json.load(open(p))
    for r in rows:
        if abs(r["s"] - d["s"]) < 1e-9 and d["maxcov_final"] <= 1 + 1e-6:
            if d["lower_bound"] > (r.get("fracpack_lb_opt") or 0):
                r["fracpack_lb_opt"] = d["lower_bound"]
                r["eta_lb_opt"] = d["lower_bound"] - 11
                r["fracpack_lb_file"] = os.path.basename(p)

# certified totals
for p in sorted(glob.glob(os.path.join(HERE, "certs", "*.report.json"))):
    rep = json.load(open(p))
    if rep.get("result") != "PASS":
        continue
    sv = float(F(rep["s"]))
    tot = float(F(rep["total"]))        # already includes scale_weights (verifier rescales first)
    for r in rows:
        if abs(r["s"] - sv) < 1e-9:
            if r.get("eta_cert") is None or tot - 11 < r["eta_cert"]:
                r["eta_cert"] = tot - 11
                r["cert_total"] = tot
                r["cert_total_exact"] = rep["total"]
                r["cert_scale"] = rep.get("scale_weights")
                r["cert_margin_cost"] = tot - r["tau_LP"]
                r["cert_file"] = rep["cert"]
                r["cert_report"] = os.path.basename(p)

json.dump(rows, open(os.path.join(HERE, "results", "eta_table.json"), "w"), indent=1)
hdr = ("s", "tau_LP", "eta_float", "row_viol", "nu_pack", "eta_lb", "eta_cert", "margin", "LPver")
print(f"{hdr[0]:>10} {hdr[1]:>11} {hdr[2]:>10} {hdr[3]:>10} {hdr[4]:>11} {hdr[5]:>10} {hdr[6]:>10} {hdr[7]:>9} {hdr[8]:>6}")
for r in rows:
    f = lambda v, k=6: ("%.*f" % (k, v)) if isinstance(v, (int, float)) else "-"
    print(f"{r['s']:>10.6f} {f(r['tau_LP']):>11} {f(r['eta_float']):>10} {f(r['row_violation']):>10} "
          f"{f(r.get('fracpack_lb_opt')):>11} {f(r.get('eta_lb_opt')):>10} "
          f"{f(r.get('eta_cert')):>10} {f(r.get('cert_margin_cost')):>9} {str(r['lp_verify_ok']):>6}")
