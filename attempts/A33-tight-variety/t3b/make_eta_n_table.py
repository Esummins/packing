"""Assemble t3b/results/eta_n_table.json.

Sources
  t3b/results/field_n*.json      this attempt's LP runs (only those AT the record side s_n are
                                 eta(n) measurements; the n=12 runs at s=3.90/3.95/3.99 belong to
                                 tau12_crossing.json and are excluded here)
  t3b/results/fracpack_lb_n*.json rigorous dual (fractional-packing) lower bounds on tau*(s_n)
  t1/results/eta_table.json      T1's n=11 measurement at s = 3.877084
Derived rows: tau* does not depend on n, so one LP run at a side s serves EVERY n whose record side
is s.  s_12 = s_16 = 4, so the n=16 run also measures eta(12).
"""
import glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
A33 = os.path.dirname(HERE)
REC = os.path.join(os.path.dirname(A33), "A11-abinitio-sweep", "records.json")
rec = json.load(open(REC))
EPS_GEO = 1e-4


def entry(n, s, tau, **kw):
    W = s * s - n
    d = dict(n=n, s_n=s, W_n=W, c_n=W / (4 * s), crystal=bool(W < 1e-9),
             record_proven_optimal=rec[str(n)].get("proven"),
             tau_LP=tau, eta=tau - n, rho=(tau - n) / W if W > 1e-9 else None)
    d.update(kw)
    return d


rows, by_s = [], {}
for p in sorted(glob.glob(os.path.join(HERE, "results", "field_n*.json"))):
    d = json.load(open(p))
    by_s[round(d["s"], 8)] = (d, os.path.basename(p))

for n_str, r in rec.items():
    n = int(n_str)
    key = round(r["record"], 8)
    if key not in by_s:
        continue
    d, fn = by_s[key]
    s = d["s"]
    res = d.get("oracle_residuals") or {}
    tau_ub = d.get("tau_ub")
    W = s * s - n
    e = entry(n, s, d["tau"],
              tau_ub=tau_ub, eta_ub=(tau_ub - n) if tau_ub else None,
              rho_ub=((tau_ub - n) / W if (tau_ub and W > 1e-9) else None),
              # tau*(s_n) >= n because n unit squares pack at the record side s_n and the LP's
              # rows are eps-SHRUNK squares, which are then pairwise disjoint closed sets.
              tau_lb_trivial=float(n), eta_lb_trivial=0.0,
              nu_dual=d.get("nu_dual"), tau_lb_raw_dual=d.get("tau_lb"),
              row_violation=res.get("row_violation"), row_witness=res.get("row_witness"),
              maxcov_shrunk=res.get("maxcov_shrunk"), maxcov_exact=res.get("maxcov_exact"),
              converged=d.get("converged"), n_atoms=d.get("n_atoms"), n_rows=d.get("n_rows"),
              n_orbits=d.get("n_orbits"), N0=d.get("N0"), eps_geo=d.get("eps_geo"),
              lp_verify_ok=(d.get("lp_verify") or {}).get("ok"),
              wall_time_s=d.get("wall_time"), field=fn,
              measured_at_n=d["n"],
              note=("tau* is independent of n; this row reuses the LP run made at n=%d, same side"
                    % d["n"]) if d["n"] != n else None)
    rows.append(e)

# T1's n = 11 measurement (s = 3.877084, the Trump side rounded down)
t1 = json.load(open(os.path.join(A33, "t1", "results", "eta_table.json")))
for r in t1:
    if abs(r["s"] - 3.877084) < 1e-9:
        s = r["s"]; W = s * s - 11
        rows.append(entry(11, s, r["tau_LP"],
                          tau_ub=r["tau_LP"] / (1 - (r["row_violation"] or 0.0)),
                          eta_ub=r["tau_LP"] / (1 - (r["row_violation"] or 0.0)) - 11,
                          rho_ub=(r["tau_LP"] / (1 - (r["row_violation"] or 0.0)) - 11) / W,
                          tau_lb_trivial=11.0, eta_lb_trivial=0.0,
                          tau_lb_opt=r.get("fracpack_lb_opt"),
                          eta_lb_opt=r.get("eta_lb_opt"),
                          rho_lb_opt=(r["eta_lb_opt"] / W) if r.get("eta_lb_opt") else None,
                          row_violation=r["row_violation"], converged=True,
                          n_atoms=r["n_atoms"], n_rows=r["n_rows"], n_orbits=r["n_orbits"],
                          lp_verify_ok=r["lp_verify_ok"], wall_time_s=r["wall_time"],
                          field="../t1/results/" + r["field"], measured_at_n=11,
                          eta_cert=r.get("eta_cert"), cert_total=r.get("cert_total"),
                          note="from T1 (attempts/A33-tight-variety/t1/results/eta_table.json); "
                               "s_11 record is 3.87708359, measured at the rounded-down 3.877084"))

# rigorous dual lower bounds
for p in sorted(glob.glob(os.path.join(HERE, "results", "fracpack_lb_n*.json"))):
    d = json.load(open(p))
    m = re.search(r"fracpack_lb_n(\d+)", os.path.basename(p))
    if not m or d.get("maxcov_final", 9) > 1 + 1e-6:
        continue
    for r in rows:
        if abs(r["s_n"] - d["s"]) < 1e-8 and d["lower_bound"] > (r.get("tau_lb_opt") or 0):
            r["tau_lb_opt"] = d["lower_bound"]
            r["eta_lb_opt"] = d["lower_bound"] - r["n"]
            r["rho_lb_opt"] = ((d["lower_bound"] - r["n"]) / r["W_n"]) if r["W_n"] > 1e-9 else None
            r["fracpack_lb_file"] = os.path.basename(p)

# crystal n: tau*(m) = m^2 exactly for the OPEN-square LP (uniform measure of total m^2 is
# feasible, an m^2-packing forces >= m^2); the eps-shrunk LP the pipeline solves has
# tau_eps(m) in [m^2, m^2/(1-2*eps)^2], so eta(m^2) = 0 up to O(4*eps*m^2).
for r in rows:
    if r["crystal"]:
        r["eta_theory_bracket"] = [0.0, r["n"] * ((1 - 2 * EPS_GEO) ** -2 - 1)]
        r["rho"] = None

# universal rigorous upper bound: the uniform measure of density (1-2*eps)^-2 on [0,s]^2 gives every
# eps-shrunk unit square mass exactly 1, so tau_eps(s) <= s^2 / (1-2*eps)^2 for EVERY s.
for r in rows:
    cap = r["s_n"] ** 2 / (1 - 2 * EPS_GEO) ** 2
    r["tau_ub_uniform"] = cap
    if r.get("tau_ub") is None or cap < r["tau_ub"]:
        r["tau_ub"] = cap
        r["tau_ub_source"] = "uniform-measure cap"
    else:
        r["tau_ub_source"] = "LP field / (1 - row_violation)"
    r["eta_ub"] = r["tau_ub"] - r["n"]
    r["rho_ub"] = (r["eta_ub"] / r["W_n"]) if r["W_n"] > 1e-9 else None

rows.sort(key=lambda r: r["n"])
json.dump(rows, open(os.path.join(HERE, "results", "eta_n_table.json"), "w"), indent=1)

print(f"{'n':>4} {'s_n':>12} {'W_n':>7} {'c_n':>6} {'tau_LP':>10} {'eta':>8} {'eta_lb':>8} "
      f"{'eta_ub':>8} {'rho':>7} {'rho_lb':>7} {'rho_ub':>7} {'rowviol':>8} {'conv':>5} {'t(s)':>6}")
for r in rows:
    f = lambda v, k=4: ("%.*f" % (k, v)) if isinstance(v, (int, float)) else "  -"
    print(f"{r['n']:>4} {r['s_n']:>12.8f} {r['W_n']:>7.4f} {r['c_n']:>6.4f} {f(r['tau_LP'],6):>10} "
          f"{f(r['eta']):>8} {f(r.get('eta_lb_opt')):>8} {f(r.get('eta_ub')):>8} "
          f"{f(r.get('rho')):>7} {f(r.get('rho_lb_opt')):>7} {f(r.get('rho_ub')):>7} "
          f"{f(r.get('row_violation'),5):>8} {str(r['converged'])[:5]:>5} {r.get('wall_time_s') or 0:>6.0f}")
