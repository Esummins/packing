r"""
A82 deliverable assembly: merge the alive gate + the LP scan into results/side_scan.json
and write the plain table into notes/side_scan.md.

Per class it reports
    tau(m), eta(m) = tau - budget, the A39 gate (tau*1.005 < budget), the alive gate
    (m_fam vs budget), the fitted dtau/ds (OLS over the measured sides, plus the local
    slope over the two lowest sides), the crossover m* where eta <= -1 (the A60
    certification law, linear in s from the fit), and the highest side at which the A39
    gate first passes on the descending walk.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glob                                                         # noqa: E402
import json                                                         # noqa: E402
import time                                                         # noqa: E402
from fractions import Fraction as Fr                                # noqa: E402

from sides82 import BASE, CLASSES, S0, S_LO, S_HAT                  # noqa: E402


def ols(xs, ys):
    n = len(xs)
    if n < 2:
        return None, None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None, None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return b, my - b * mx


def main():
    alive = {"classes": {}}
    for fn in ("alive_gate.json", "alive_gate_grid.json"):
        p = os.path.join(BASE, "results", fn)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for cls, c in d.get("classes", {}).items():
            tgt = alive["classes"].setdefault(cls, dict(c, rows=[]))
            have = {r["side"] for r in tgt["rows"]}
            tgt["rows"] += [r for r in c.get("rows", []) if r["side"] not in have]
            if tgt.get("s_fit") in (None, float(S0)) and c.get("s_fit"):
                tgt["s_fit"] = c["s_fit"]
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "s0": str(S0),
           "s_lo": str(S_LO), "s_hat": S_HAT,
           "law": "A60 certification law: a node certifies iff eta = tau - budget reaches -1; "
                  "A39 gate: certify's auto scale needs tau*1.005 < budget",
           "classes": {}}
    for p in sorted(glob.glob(os.path.join(BASE, "results", "scan_*.json"))):
        d = json.load(open(p))
        cls, budget = d["cls"], d["budget"]
        ag = {r["side"]: r for r in alive.get("classes", {}).get(cls, {}).get("rows", [])}
        rows = []
        for r in d["rows"]:
            a = ag.get(r["side"], {})
            rows.append(dict(side=r["side"], side_float=r["side_float"], sym=r["sym"],
                             tau=r["tau"], eta=r["eta"], converged=r["converged"],
                             a39_gate=r["a39_gate"], eta_le_m1=r["kill_law_eta_le_m1"],
                             m_fam=a.get("m_fam"), alive=a.get("alive"),
                             fam_gap=a.get("min_gap_float"),
                             fam_exact=a.get("exact"),
                             eta_lower_bound=a.get("eta_lower_bound"),
                             minmass=r.get("minmass"), maxcov=r.get("maxcov"),
                             delta=r.get("delta", 0.0), shell=r.get("shell"),
                             seconds=r["seconds"],
                             n_orbits=r["n_orbits"], n_rows=r["n_rows"]))
        rows.sort(key=lambda z: -z["side_float"])
        xs = [r["side_float"] for r in rows]
        ys = [r["tau"] for r in rows]
        slope, icpt = ols(xs, ys)
        # local slope over the two LOWEST measured sides
        lo = sorted(rows, key=lambda z: z["side_float"])[:2]
        loc = ((lo[1]["tau"] - lo[0]["tau"]) / (lo[1]["side_float"] - lo[0]["side_float"])
               if len(lo) == 2 and lo[1]["side_float"] != lo[0]["side_float"] else None)
        # measured crossover: highest side (descending) whose eta <= -1 / A39 gate passes
        first_a39 = next((r["side"] for r in rows if r["a39_gate"]), None)
        first_law = next((r["side"] for r in rows if r["eta_le_m1"]), None)
        # extrapolated crossover from the fit: tau = budget - 1
        m_star = None
        if slope not in (None, 0):
            m_star = ((budget - 1) - icpt) / slope
        out["classes"][cls] = dict(
            k=d["k"], budget=budget, sides_measured=len(rows),
            s_fit=alive.get("classes", {}).get(cls, {}).get("s_fit"),
            dtau_ds_ols=slope, dtau_ds_local_low=loc,
            first_side_a39_gate=first_a39, first_side_eta_le_m1=first_law,
            m_star_fit_eta_m1=m_star,
            m_star_in_window=(bool(m_star is not None and float(S_LO) <= m_star <= float(S0))),
            rows=rows)
    json.dump(out, open(os.path.join(BASE, "results", "side_scan.json"), "w"), indent=1)

    # ------------------------------------------------------------------ plain table
    L = []
    L.append("# A82 side scan -- crossover table\n")
    L.append("s0 = %s = %.6f; s-hat = %.15f; window floor = %s = %.2f\n"
             % (S0, float(S0), S_HAT, S_LO, float(S_LO)))
    L.append("alive gate: m_fam = largest STRICTLY separated family found at side m "
             "(A57 disjoint-family bound => tau* >= m_fam).  eta = tau - budget.\n")
    for cls, c in sorted(out["classes"].items()):
        L.append("\n## %s  (k=%d, budget=%d)\n" % (cls, c["k"], c["budget"]))
        L.append("| side m | m (float) | m_fam/budget | alive | eta >= (exact) | tau(m) | "
                 "eta(m) | conv | A39 gate | eta<=-1 | s |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in c["rows"]:
            L.append("| %s | %.6f | %s/%d | %s | %s | %.6f | %+.6f | %s | %s | %s | %.0f |"
                     % (r["side"], r["side_float"],
                        r["m_fam"] if r["m_fam"] is not None else "-", c["budget"],
                        {True: "YES", False: "no", None: "-"}[r["alive"]],
                        ("%+d" % r["eta_lower_bound"]) if r.get("eta_lower_bound")
                        is not None else "-",
                        r["tau"], r["eta"], "y" if r["converged"] else "n",
                        "PASS" if r["a39_gate"] else "-",
                        "PASS" if r["eta_le_m1"] else "-", r["seconds"]))
        L.append("")
        L.append("* s_fit (smallest side with a full budget-size family) = %s"
                 % ("%.9f" % c["s_fit"] if c["s_fit"] else "n/a"))
        L.append("* dtau/ds (OLS over measured sides) = %s ; local slope at the two lowest "
                 "sides = %s"
                 % ("%.4f" % c["dtau_ds_ols"] if c["dtau_ds_ols"] is not None else "n/a",
                    "%.4f" % c["dtau_ds_local_low"] if c["dtau_ds_local_low"] is not None
                    else "n/a"))
        L.append("* first side (descending) passing the A39 gate: %s ; first with eta <= -1: %s"
                 % (c["first_side_a39_gate"] or "NONE", c["first_side_eta_le_m1"] or "NONE"))
        L.append("* extrapolated crossover m* (fit, eta = -1): %s%s"
                 % ("%.6f" % c["m_star_fit_eta_m1"] if c["m_star_fit_eta_m1"] is not None
                    else "n/a",
                    "" if c["m_star_in_window"] else "  [OUTSIDE the window W]"))
    # ------------------------------------------------------- the A57 grid-side table
    gp = os.path.join(BASE, "results", "alive_gate_grid.json")
    if os.path.exists(gp):
        from sides82 import GRID_SIDES, EXT_CLASSES
        g = json.load(open(gp))
        lp = {}
        for p in glob.glob(os.path.join(BASE, "results", "scan_*.json")):
            d = json.load(open(p))
            for r in d["rows"]:
                lp[(d["cls"], r["side"])] = r
        L.append("\n\n# A82 extension -- the three A57 slack-core grid sides\n")
        L.append("exact bound = tau* >= m_fam (rationally verified family), so eta >= "
                 "m_fam - budget.  LP tau is the 600 s conditioned case-LP at that side "
                 "(delta = 0 pins); 'kill' = an emitted certificate PASSing the frozen "
                 "verifier cold.\n")
        for s in GRID_SIDES:
            L.append("\n## side %s = %.6f\n" % (s, float(Fr(s))))
            L.append("| class | k | budget | m_fam | eta >= (exact) | tau | eta | A39 | "
                     "eta<=-1 | certificate |")
            L.append("|---|---|---|---|---|---|---|---|---|---|")
            for cls in EXT_CLASSES:
                gc = g["classes"].get(cls)
                if not gc:
                    continue
                row = next((r for r in gc["rows"] if r["side"] == s), None)
                r = lp.get((cls, s))
                cert = os.path.join(BASE, "certs",
                                    "%s_%s.json" % (cls, s.replace("/", "_")))
                creport = cert.replace(".json", ".report.json")
                cstat = "-"
                if os.path.exists(creport):
                    try:
                        cstat = json.load(open(creport)).get("result", "?")
                    except Exception:
                        cstat = "?"
                L.append("| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s |"
                         % (cls, gc["k"], gc["budget"],
                            ("%d" % row["m_fam"]) if row else "-",
                            ("%+d" % row["eta_lower_bound"])
                            if row and row.get("eta_lower_bound") is not None else "-",
                            ("%.6f" % r["tau"]) if r else "-",
                            ("%+.6f" % r["eta"]) if r else "-",
                            ("PASS" if r["a39_gate"] else "-") if r else "-",
                            ("PASS" if r["kill_law_eta_le_m1"] else "-") if r else "-",
                            cstat))
    open(os.path.join(BASE, "notes", "side_scan.md"), "w", encoding="utf-8").write(
        "\n".join(L) + "\n")
    print("\n".join(L[-60:]))


if __name__ == "__main__":
    main()
