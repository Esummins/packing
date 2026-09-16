"""A238 -- the report: A100's LP price against A238's geometry price, cell by cell, plus the rule counts, the gate /
tube / hand-off census and the tier extrapolation.

    python report238.py [--out results/bench238.md]

Reads results/bench238.jsonl (one row per node, written by run238 through rows212.row_of) and A100's
a84_<cls>_cover_j0.jsonl + a84_<cls>_census_j0.json + a100_projection.json.  Writes the markdown table and
results/bench238_summary.json.  No run, no wall: safe to call at any time."""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A238 = os.path.abspath(os.path.join(HERE, ".."))
A100 = os.path.join(ROOT, "attempts", "A100-protected-pilot", "results")
ROWS = os.path.join(A238, "results", "bench238.jsonl")
sys.path.insert(0, HERE)
import queue238 as Q                                            # noqa: E402  (a100_cells)

TRUMP_PARENTS = 14      # A84 s.0: the 16 protected classes minus the two shadow classes k4_05 / corners4
SHADOW = ("k4_05", "corners4")


def rows():
    """the LAST row per nid (a re-run supersedes)."""
    out = {}
    if not os.path.exists(ROWS):
        return out
    for ln in open(ROWS, encoding="utf-8", errors="replace"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:                                         # noqa: BLE001
            continue
        if r.get("nid"):
            out[r["nid"]] = r
    return out


def cls_of(nid):
    return nid.rsplit("_c0_Y", 1)[0] if "_c0_Y" in nid else nid.rsplit("_root", 1)[0]


def idx_of(nid):
    return int(nid.rsplit("_c0_Y", 1)[1]) if "_c0_Y" in nid else None


def census(cls):
    f = os.path.join(A100, "a84_%s_census_j0.json" % cls)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None


def a100_proj(cls):
    f = os.path.join(A100, "a100_projection.json")
    return (json.load(open(f, encoding="utf-8"))["per_class"].get(cls) or {}) if os.path.exists(f) else {}


def decided(r):
    return r.get("verdict") in ("DEAD", "TRUMP-TUBE")


def per_class(R):
    out = collections.OrderedDict()
    for nid, r in sorted(R.items()):
        out.setdefault(cls_of(nid), []).append((nid, r))
    return out


def summarise(cls, items):
    a1 = Q.a100_cells(cls)
    cen = census(cls) or {}
    cov = (cen.get("counts") or {})
    head, extra, root = [], [], None
    for nid, r in items:
        i = idx_of(nid)
        if i is None:
            root = r
        elif i in a1:
            head.append((i, r))
        else:
            extra.append((i, r))
    def agg(pairs, a100=False):
        n = len(pairs)
        s238 = sum((r.get("priced_seconds") or r.get("seconds_total") or r.get("seconds") or 0.0) for _i, r in pairs)  # tree + stage 0
        dead = sum(1 for _i, r in pairs if r.get("verdict") == "DEAD")
        tube = sum(1 for _i, r in pairs if r.get("verdict") == "TRUMP-TUBE")
        alive = n - dead - tube
        s100 = sum(((a1.get(i) or {}).get("lp_s") or 0.0) + ((a1.get(i) or {}).get("cert_s") or 0.0) for i, _r in pairs) if a100 else None
        k100 = sum(1 for i, _r in pairs if str((a1.get(i) or {}).get("verdict") or "").startswith("PASS")) if a100 else None
        def med(v):
            v = sorted(v)
            return round((v[len(v) // 2] if len(v) % 2 else 0.5 * (v[len(v) // 2 - 1] + v[len(v) // 2])), 1) if v else None
        m238 = med([(r.get("priced_seconds") or r.get("seconds") or 0.0) for _i, r in pairs])
        m100 = med([((a1.get(i) or {}).get("lp_s") or 0.0) + ((a1.get(i) or {}).get("cert_s") or 0.0) for i, _r in pairs]) if a100 else None
        return dict(n=n, dead=dead, tube=tube, alive=alive, s238=round(s238, 1), med238=m238, med100=m100,
                    mean238=round(s238 / n, 1) if n else None, kill_rate=round(dead / n, 4) if n else None,
                    s100=(round(s100, 1) if s100 is not None else None),
                    mean100=(round(s100 / n, 1) if (s100 is not None and n) else None),
                    a100_pass=k100, a100_kill_rate=(round(k100 / n, 4) if (k100 is not None and n) else None))
    H, E = agg(head, a100=True), agg(extra)
    allp = agg(head + extra, a100=True)
    rules = collections.Counter()
    gate_hits = tube_leaves = snap_k = snap_h = eps_k = 0
    depth_hist = collections.Counter()
    for _nid, r in items:
        for k, v in (r.get("kills_by_rule") or {}).items():
            rules[k] += v
        gate_hits += r.get("gate_hits") or 0
        tube_leaves += r.get("tube_leaves") or 0
        snap_k += (r.get("snap") or {}).get("kills") or 0
        snap_h += (r.get("snap") or {}).get("handoffs") or 0
        depth_hist[r.get("max_depth")] += 1
    return dict(cls=cls, cover=cov, head=H, extra=E, all=allp, rows_head=head, root=(dict(verdict=root.get("verdict"), seconds=root.get("priced_seconds") or root.get("seconds"),
                n_nodes=root.get("n_nodes"), gate=root.get("gate_root")) if root else None),
                rules=dict(rules), gate_hits=gate_hits, tube_leaves=tube_leaves, snap_kills=snap_k, snap_handoffs=snap_h,
                depth=dict(depth_hist), a100=a100_proj(cls))


def price(S):
    """the class's geometry price and the residue it leaves, from the measured mean node cost."""
    cov = S["cover"] or {}
    cells = (cov.get("attemptable") or 0) + (cov.get("unkillable") or 0)
    A = S["all"]
    if not A["n"]:
        return None
    mean = A["mean238"] or 0.0
    kill = A["kill_rate"] or 0.0
    a1 = S["a100"]
    lp = a1.get("w_node_asrun_s") or 0.0
    geo_h = cells * mean / 3600.0
    resid_h = cells * (1 - kill) * lp / 3600.0
    return dict(cells=cells, mean_node_s=round(mean, 1), kill_rate=round(kill, 4), a100_node_s=round(lp, 1),
                geometry_cpu_h=round(geo_h, 1), lp_residue_cpu_h=round(resid_h, 1),
                total_cpu_h=round(geo_h + resid_h, 1), a100_total_cpu_h=a1.get("total_measured_cpu_h"),
                speedup_per_node=(round(lp / mean, 2) if mean else None))


def forced():
    """the forced-cell census (code/fc238.py): traction = the one-slot extensions closed on the window."""
    f = os.path.join(A238, "results", "forced238.json")
    return {r["cls"]: r for r in json.load(open(f, encoding="utf-8"))} if os.path.exists(f) else {}


def tier(sums):
    """the extrapolation, split by the ONE number that predicts it: the class's usable forced cells."""
    FC = forced()
    K4 = ["k4_03", "k4_05", "k4_06", "k4_08", "k4_11"]
    K3 = ["k3_01", "k3_02", "k3_03", "k3_04", "k3_05"]
    P = {S["cls"]: price(S) for S in sums if price(S)}
    k4 = P.get("k4_11")
    k3 = P.get("k3_02")
    L = ["## Tier extrapolation", "",
         "The measured per-class numbers are the two pilots; the extrapolation carries them by the ONE number that",
         "predicts traction -- the class's USABLE forced cells (`results/forced238.md`), i.e. how many of its one-slot",
         "extensions are closed on the window.", "",
         "| block | classes | usable forced cells | geometry CPU-h | LP residue CPU-h | total (A238) | A100's price |",
         "|---|---|---|---|---|---|---|"]
    if k4:
        n4 = ", ".join("%s %s/%s" % (c, (FC.get(c) or {}).get("n_usable"), (FC.get(c) or {}).get("n_cells")) for c in K4)
        L.append("| k4 with traction (%s) | 5 | %s | %.0f | %.0f | **%.0f** | %s each |" % (
            ", ".join(K4), n4, 5 * k4["geometry_cpu_h"], 5 * k4["lp_residue_cpu_h"], 5 * k4["total_cpu_h"],
            k4["a100_total_cpu_h"]))
    if k3:
        L.append("| k <= 3 (%s, k2_*, k1_00) | 9 | 0 for every one | %.0f | %.0f | **%.0f** | %s each |" % (
            ", ".join(K3), 9 * k3["geometry_cpu_h"], 9 * k3["lp_residue_cpu_h"], 9 * k3["total_cpu_h"],
            k3["a100_total_cpu_h"]))
    L += ["| corners4 (shadow, no image) | 1 | 0/8 -- every extension is the OPEN k5_16 | 0 | not priced | - | not priced |", ""]
    L += ["`corners4` is not run: with no usable forced cell the toolkit's rules have nothing to act on (A193 and",
          "A84 s.7.1 independently), so a run would cost the stage-0 seconds and decide nothing -- exactly what the",
          "k3_02 rows above measure.  For the same reason the k <= 3 row is NOT a saving: the geometry is cheap there",
          "because it is blind, and the LP residue is A100's whole price.", "",
          "**The lever the numbers point at**: five of the nine blocked k <= 3 extensions are k4 classes A55 already",
          "killed exactly (k4_00 / 01 / 02 / 04 / 07 / 09 / 10 / 12) that simply have no full-window scoreboard row.",
          "Emitting those rows would give each k3 class 2-5 usable forced cells and move it into the k4 row of this",
          "table.", ""]
    return L


def md(sums):
    L = ["# A238 -- the k5 toolkit on the Trump-parent protected classes: geometry against A100's LP", "",
         "Every row is ONE node of a protected class's tree at s0 with the SAME hypothesis A100 priced: M_S & YES(H),",
         "delta_pin = 2e-2, H the A100/A84 level-1 cover cell (`attempts/A238-k4-benchmark/code/load238.py`).",
         "A238's verdict is the k5 toolkit's (A211 coarse tree, A212 gate + Lemma TUBE-LEAF/S in the class direction,",
         "A224 Rule SNAP with the k+1 hand-off, A230 Rule EPS, A220/A221); A100's is the case-LP's.", ""]
    for S in sums:
        A, H = S["all"], S["head"]
        L += ["## %s" % S["cls"], "",
              "| set | n | A238 DEAD | TUBE | ALIVE | A238 mean / median s | A100 PASS | A100 mean / median s | speed-up (median) |",
              "|---|---|---|---|---|---|---|---|---|",
              "| A100 head-to-head | %s | %s | %s | %s | %s / %s | %s | %s / %s | %s |" % (
                  H["n"], H["dead"], H["tube"], H["alive"], H["mean238"], H["med238"], H["a100_pass"], H["mean100"], H["med100"],
                  ("%.1fx" % (H["med100"] / H["med238"])) if (H["med238"] and H["med100"]) else "-"),
              "| + extrapolation set | %s | %s | %s | %s | %s / %s | - | - | - |" % (
                  S["extra"]["n"], S["extra"]["dead"], S["extra"]["tube"], S["extra"]["alive"], S["extra"]["mean238"], S["extra"]["med238"]),
              "| all cover nodes | %s | %s | %s | %s | %s / %s | %s | %s / %s | - |" % (
                  A["n"], A["dead"], A["tube"], A["alive"], A["mean238"], A["med238"], A["a100_pass"], A["mean100"], A["med100"]), "",
              "root (A84-P1 node, H = the whole interior zone): %s" % (S["root"] or "not run"), "",
              "kills by rule: `%s`; gate hits %d; TRUMP-TUBE leaves %d; SNAP kills %d, hand-offs %d; max depth %s" % (
                  json.dumps(S["rules"]), S["gate_hits"], S["tube_leaves"], S["snap_kills"], S["snap_handoffs"], json.dumps(S["depth"])), ""]
        cells = sorted(((i, r) for i, r in S["rows_head"]), key=lambda t: t[0])
        if cells:
            L += ["### %s — cell by cell (A100's own LP row against A238's geometry)" % S["cls"], "",
                  "| cell | A100 verdict | A100 s | A238 verdict | A238 s | killed by | nodes | depth |",
                  "|---|---|---|---|---|---|---|---|"]
            for i, r in cells:
                a = r.get("a100") or {}
                L.append("| `c0_Y%04d` | %s | %.0f | **%s** | %.1f | %s | %s | %s |" % (
                    i, str(a.get("verdict") or "-")[:34], (a.get("lp_s") or 0) + (a.get("cert_s") or 0),
                    r.get("verdict"), r.get("priced_seconds") or 0.0,
                    ", ".join("%s x%d" % (k, v) for k, v in sorted((r.get("kills_by_rule") or {}).items())) or "—",
                    r.get("n_nodes"), r.get("max_depth")))
            L.append("")
        p = price(S)
        if p:
            L += ["price: %d cover cells x %.1f s = **%.1f CPU-h** of geometry; the %.0f %% geometry leaves over (at "
                  "A100's %.0f s/node LP) %.1f CPU-h; total **%.1f CPU-h** against A100's measured %s CPU-h "
                  "(per node %s x cheaper)." % (p["cells"], p["mean_node_s"], p["geometry_cpu_h"],
                                                100 * (1 - p["kill_rate"]), p["a100_node_s"], p["lp_residue_cpu_h"],
                                                p["total_cpu_h"], p["a100_total_cpu_h"], p["speedup_per_node"]), ""]
    L += tier(sums)
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(A238, "results", "bench238.md"))
    a = ap.parse_args()
    R = rows()
    sums = [summarise(c, it) for c, it in per_class(R).items()]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(md(sums))
    for S in sums:
        S.pop("rows_head", None)
    json.dump(dict(rows=len(R), classes=sums, price={S["cls"]: price(S) for S in sums}),
              open(os.path.join(A238, "results", "bench238_summary.json"), "w", encoding="utf-8"), indent=1, default=str)
    print("A238 report: %d rows, %d classes -> %s" % (len(R), len(sums), os.path.relpath(a.out, ROOT)))
