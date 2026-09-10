"""A191 -- the price table from the measured numbers (results/report191.json + the S3 sample), written into
notes/price191.md between the %%S2_TABLE%% / %%PRICE_TABLE%% markers (re-runnable).

Model (per k0 cell, l1_104-sized): layers S2..S8; N_k alive nodes entering layer k; c_k CPU-s per node; kappa_k the
fraction of layer-k nodes DECIDED DEAD (certified); the rest fan out with phi_k children each.  Cost = SUM N_k c_k.
S2: everything measured tonight.  S3: c_3 measured on the coarse sample, kappa_3 sampled (geometry + LP).
S4..S8: kappa = kappa_3 (ASSUMED), phi = phi_first (112, A168's S3 fan-out) for a corner's first meeter and
phi_partner for its second (ASSUMED half: Lemma A2 halves the partner window).  Three scenarios on the deep
kill rate.  CPU-h at one process per vCPU; instance-hours at 16 vCPU-h per instance-hour.
"""
import glob
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
NOTE = os.path.join(BASE, "notes", "price191.md")


def s2_numbers():
    R = [json.loads(l) for l in open(os.path.join(RES, "run191_l1_104_S2.jsonl"), encoding="utf-8")]
    R = {r["record_node"]: r for r in R if not str(r.get("verdict", "")).startswith(("[P]", "ERROR"))}.values()
    R = list(R)
    dead = [r for r in R if r["verdict"].startswith("DEAD")]
    v1 = [r["v1"] for r in R]
    cand = [r for r in R if not r["verdict"].startswith("DEAD") and r["v1"].get("kills")]
    conv_alive = [r for r in R if r["v1"].get("converged") and not r["v1"].get("kills")]
    return dict(n=len(R), dead=len(dead), cand=len(cand), conv_alive=len(conv_alive),
                geo=st.mean(r["geo_s"] for r in R), v1=st.mean(v["lp_s"] for v in v1), win=st.mean(r["lp_s"] for r in R),
                cert=st.mean((r.get("cert_s") or 0) + (r["v1"].get("cert_s") or 0) for r in R),
                wall=st.mean(r["wall_s"] for r in R), wall_max=max(r["wall_s"] for r in R),
                total_h=sum(r["wall_s"] for r in R) / 3600.0)


def s3_numbers():
    f = os.path.join(RES, "run191_l1_104_S3coarse.jsonl")
    if not os.path.exists(f):
        return None
    R = [json.loads(l) for l in open(f, encoding="utf-8")]
    R = list({r["record_node"]: r for r in R if not str(r.get("verdict", "")).startswith(("[P]", "ERROR"))}.values())
    if not R:
        return None
    dead_geo = [r for r in R if r["verdict"].startswith("DEAD(C") ]
    dead_lp = [r for r in R if r["verdict"].startswith("DEAD(LP")]
    cand = [r for r in R if not r["verdict"].startswith("DEAD") and (r.get("v1") or {}).get("kills")]
    lp = [r for r in R if r.get("v1")]
    return dict(n=len(R), dead_geo=len(dead_geo), dead_lp=len(dead_lp), cand=len(cand), n_lp=len(lp),
                clip=st.mean(r.get("clip_s") or 0 for r in R), geo=st.mean(r.get("geo_s") or 0 for r in lp) if lp else 0,
                v1=st.mean(r["v1"]["lp_s"] for r in lp) if lp else 0, win=st.mean(r.get("lp_s") or 0 for r in lp) if lp else 0,
                cert=st.mean((r.get("cert_s") or 0) + (r["v1"].get("cert_s") or 0) for r in lp) if lp else 0,
                wall=st.mean(r["wall_s"] for r in R), wall_max=max(r["wall_s"] for r in R))


def price(s2, s3, kappa_deep, phi_first=112.0, phi_partner=56.0, n_s2=64, layers=("S2", "S3", "S4", "S5", "S6", "S7", "S8")):
    """returns rows [(layer, N_k, c_k, kappa_k, cost_h)] and the total."""
    c2 = s2["wall"]
    k2 = s2["dead"] / s2["n"]
    c3 = (s3["wall"] if s3 else 250.0)
    k3 = ((s3["dead_geo"] + s3["dead_lp"]) / s3["n"]) if s3 else kappa_deep
    rows, N, tot = [], float(n_s2), 0.0
    for L in layers:
        if L == "S2":
            c, k = c2, k2
        elif L == "S3":
            c, k = c3, k3
        else:
            c, k = c3, kappa_deep
        cost = N * c / 3600.0
        rows.append((L, N, c, k, cost))
        tot += cost
        phi = phi_first if L in ("S2", "S4", "S6") else phi_partner       # S3 = B (first BR), S4 = B' (partner), S5 = T1 ...
        # the children of layer L's survivors form layer L+1; S2's survivors fan out to S3 with phi_first
        N = N * (1.0 - k) * (phi_first if L in ("S2", "S4", "S6") else phi_partner)
    return rows, tot


def fmt_rows(rows, tot):
    out = ["| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |", "|---|---|---|---|---|"]
    for (L, N, c, k, cost) in rows:
        out.append("| %s | %s | %.0f | %.2f | %s |" % (L, ("%.0f" % N if N < 1e6 else "%.3g" % N), c, k, ("%.1f" % cost if cost < 1e5 else "%.3g" % cost)))
    out.append("| **total per cell** | | | | **%s** (%s instance-h at 16 vCPU) |" % (("%.0f" % tot if tot < 1e6 else "%.3g" % tot), ("%.0f" % (tot / 16) if tot < 1e6 else "%.3g" % (tot / 16))))
    return "\n".join(out)


def main():
    s2 = s2_numbers()
    s3 = s3_numbers()
    t2 = ("| l1_104 S2 (64 alive after A183) | DEAD certified | kill candidates (v1 LP below budget, unconverged at cap) | converged ALIVE | "
          "geometry s | v1 LP s | windows LP s (diagnostic) | certificate s | wall s mean / max | total CPU-h |\n|---|---|---|---|---|---|---|---|---|---|\n"
          "| %d | %d (%.0f %%) | %d (%.0f %%) | %d (%.0f %%) | %.0f | %.0f | %.0f | %.0f | %.0f / %.0f | %.1f |" % (
              s2["n"], s2["dead"], 100.0 * s2["dead"] / s2["n"], s2["cand"], 100.0 * s2["cand"] / s2["n"], s2["conv_alive"],
              100.0 * s2["conv_alive"] / s2["n"], s2["geo"], s2["v1"], s2["win"], s2["cert"], s2["wall"], s2["wall_max"], s2["total_h"]))
    if s3:
        t2 += ("\n\n| l1_104 S3 coarse sample (children of S2 survivors, nsub 4 / refine 2, parent-seeded) | DEAD by geometry | DEAD by LP | "
               "kill candidates | clip s | corner leaf s | v1 LP s | windows LP s | cert s | wall s mean / max |\n|---|---|---|---|---|---|---|---|---|---|\n"
               "| %d | %d | %d | %d | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f / %.0f |" % (
                   s3["n"], s3["dead_geo"], s3["dead_lp"], s3["cand"], s3["clip"], s3["geo"], s3["v1"], s3["win"], s3["cert"], s3["wall"], s3["wall_max"]))
    blocks = []
    k3 = ((s3["dead_geo"] + s3["dead_lp"]) / s3["n"]) if s3 else None
    scen = [("deep kill rate = the S3 sample's (%s)" % ("%.2f" % k3 if k3 is not None else "not yet measured; 0.27 = S2's"), k3 if k3 is not None else 0.27),
            ("deep kill rate 0.90 (what closure at S8 needs)", 0.90), ("deep kill rate 0.99", 0.99)]
    for name, kd in scen:
        rows, tot = price(s2, s3, kd)
        blocks.append("**Scenario: %s; fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**\n\n%s" % (name, fmt_rows(rows, tot)))
    blocks.append("**Eleven cells:** multiply the per-cell total by <= 11 (l1_104 is the largest S1 layer of the eleven; the canary "
                  "l1_153 has 1 alive S2 node against 64, so the true multiplier is well below 11).  The S2 layer alone, all eleven "
                  "cells at l1_104's size: %.0f CPU-h = %.0f instance-hours." % (11 * s2["total_h"], 11 * s2["total_h"] / 16))
    txt = open(NOTE, encoding="utf-8").read()
    import re
    txt = re.sub(r"%%S2_TABLE%%.*?(?=\n## 3\.)", "%%S2_TABLE%%\n" + t2 + "\n", txt, flags=re.S) if "%%S2_TABLE%%" in txt else txt
    txt = re.sub(r"%%PRICE_TABLE%%.*?(?=\n## 4\.)", "%%PRICE_TABLE%%\n" + "\n\n".join(blocks) + "\n", txt, flags=re.S) if "%%PRICE_TABLE%%" in txt else txt
    open(NOTE, "w", encoding="utf-8").write(txt)
    json.dump(dict(s2=s2, s3=s3, scenarios=[(n, price(s2, s3, k)[1]) for n, k in scen]), open(os.path.join(RES, "price191.json"), "w"), indent=1)
    print(t2)
    print("\n\n".join(blocks))


if __name__ == "__main__":
    main()
