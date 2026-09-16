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
        return dict(n=n, dead=dead, tube=tube, alive=alive, s238=round(s238, 1),
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
    return dict(cls=cls, cover=cov, head=H, extra=E, all=allp, root=(dict(verdict=root.get("verdict"), seconds=root.get("priced_seconds") or root.get("seconds"),
                n_nodes=root.get("n_nodes"), gate=(root.get("gate_root") or {}).get("contains")) if root else None),
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


def md(sums):
    L = ["# A238 -- the k5 toolkit on the Trump-parent protected classes: geometry against A100's LP", "",
         "Every row is ONE node of a protected class's tree at s0 with the SAME hypothesis A100 priced: M_S & YES(H),",
         "delta_pin = 2e-2, H the A100/A84 level-1 cover cell (`attempts/A238-k4-benchmark/code/load238.py`).",
         "A238's verdict is the k5 toolkit's (A211 coarse tree, A212 gate + Lemma TUBE-LEAF/S in the class direction,",
         "A224 Rule SNAP with the k+1 hand-off, A230 Rule EPS, A220/A221); A100's is the case-LP's.", ""]
    for S in sums:
        A, H = S["all"], S["head"]
        L += ["## %s" % S["cls"], "",
              "| set | n | A238 DEAD | TUBE | ALIVE | A238 mean s | A100 PASS | A100 mean s | speed-up |",
              "|---|---|---|---|---|---|---|---|---|",
              "| A100 head-to-head | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                  H["n"], H["dead"], H["tube"], H["alive"], H["mean238"], H["a100_pass"], H["mean100"],
                  ("%.1fx" % (H["mean100"] / H["mean238"])) if (H["mean238"] and H["mean100"]) else "-"),
              "| + extrapolation set | %s | %s | %s | %s | %s | - | - | - |" % (
                  S["extra"]["n"], S["extra"]["dead"], S["extra"]["tube"], S["extra"]["alive"], S["extra"]["mean238"]),
              "| all cover nodes | %s | %s | %s | %s | %s | %s | %s | - |" % (
                  A["n"], A["dead"], A["tube"], A["alive"], A["mean238"], A["a100_pass"], A["mean100"]), "",
              "root (A84-P1 node, H = the whole interior zone): %s" % (S["root"] or "not run"), "",
              "kills by rule: `%s`; gate hits %d; TRUMP-TUBE leaves %d; SNAP kills %d, hand-offs %d; max depth %s" % (
                  json.dumps(S["rules"]), S["gate_hits"], S["tube_leaves"], S["snap_kills"], S["snap_handoffs"], json.dumps(S["depth"])), ""]
        p = price(S)
        if p:
            L += ["price: %d cover cells x %.1f s = **%.1f CPU-h** of geometry; the %.0f %% geometry leaves over (at "
                  "A100's %.0f s/node LP) %.1f CPU-h; total **%.1f CPU-h** against A100's measured %s CPU-h "
                  "(per node %s x cheaper)." % (p["cells"], p["mean_node_s"], p["geometry_cpu_h"],
                                                100 * (1 - p["kill_rate"]), p["a100_node_s"], p["lp_residue_cpu_h"],
                                                p["total_cpu_h"], p["a100_total_cpu_h"], p["speedup_per_node"]), ""]
    tot = [price(S) for S in sums if price(S)]
    if tot:
        per = sum(t["total_cpu_h"] for t in tot) / len(tot)
        a100per = sum((t["a100_total_cpu_h"] or 0) for t in tot) / len(tot)
        L += ["## Tier extrapolation", "",
              "| tier block | classes | per class CPU-h (A238) | per class CPU-h (A100) | block CPU-h (A238) | block CPU-h (A100) |",
              "|---|---|---|---|---|---|",
              "| Trump-parent (image-bearing) | %d | %.0f | %.0f | %.0f | %.0f |" % (
                  TRUMP_PARENTS, per, a100per, TRUMP_PARENTS * per, TRUMP_PARENTS * a100per),
              "| shadow (%s): no image, kill-only | 2 | %.0f | - | %.0f | - |" % (
                  ", ".join(SHADOW), per, 2 * per), "",
              "The shadow classes carry no Trump image, so the gate never holds: every node is submitted to the kill",
              "rules and there is no tube-pending residue -- the same geometry price with a smaller alive fraction.", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(A238, "results", "bench238.md"))
    a = ap.parse_args()
    R = rows()
    sums = [summarise(c, it) for c, it in per_class(R).items()]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(md(sums))
    json.dump(dict(rows=len(R), classes=sums, price={S["cls"]: price(S) for S in sums}),
              open(os.path.join(A238, "results", "bench238_summary.json"), "w", encoding="utf-8"), indent=1, default=str)
    print("A238 report: %d rows, %d classes -> %s" % (len(R), len(sums), os.path.relpath(a.out, ROOT)))
