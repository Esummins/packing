"""A96 deliverables: the per-class window scoreboard, the Lean window-row list, and the
re-projection of A57's remaining wall.

Three outputs, all from measured data (no hand-entered constants except A57's own cover counts,
which come from A57's C-check and are reproduced by A96 code/ladder96.py):

  results/scoreboard96.json + notes/SCOREBOARD.md
      per class: cover size, CI-4 logic kills (per side, NOT parametric), nodes needing level 2,
      candidates, parametric verdicts, and the class window coverage.
      CLASS COVERAGE IS AN INTERSECTION: the class is killed at side s only if EVERY box of its
      cover is discharged at s, so the class's certified set is the intersection of the nodes'
      certified sets.  Reporting a mean over nodes would be meaningless (and flattering).

  results/window_rows_<cls>.json
      A86 T4 WindowRows form: one row per (node, closed sub-window, constructor).  Constructors
      used here: "param" (a parametric-kill-certificate-v1 PASS on [slo, shi]) and "logic"
      (a CI-4 per-side C-check kill).  Each param row carries the exact rational endpoints and
      the gen_param_lean.py command that emits its Lean data module.

  results/projection96.json
      A57's remaining wall under the parametric route vs the four-fixed-side baseline (A95 T3),
      at 3 and 5 workers, with and without the sigma ladder on k5_11.
"""
import json, os, statistics, subprocess, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(BASE, "results")
A95 = os.path.abspath(os.path.join(BASE, "..", "A95-a57-shortcuts", "results"))
SLO, SHI = F(191, 50), F(969271, 250000)
WFLOAT = float(SHI - SLO)
CLASSES = ("k5_11_G1", "k5_16_G1")
# A57's own cover, side 1 (12x12x8 + the NO child); reproduced by code/ladder96.py.
COVER_OK = {"k5_11_G1": 821, "k5_16_G1": 914}
COVER_LOGIC = {"k5_11_G1": 331, "k5_16_G1": 238}


def load(path):
    if not os.path.exists(path):
        return []
    R = []
    for ln in open(path):
        try:
            R.append(json.loads(ln))
        except Exception:
            pass
    return R


def param_records():
    """A96's own pass plus A95's 18-node pilot (same emitter family, same frozen verifier)."""
    R = {}
    for r in load(os.path.join(A95, "t1_param.jsonl")):
        r.setdefault("cls", "k5_11_G1"); r.setdefault("level", 1); r["source"] = "A95"
        R[(r["cls"], r["id"])] = r
    for r in load(os.path.join(OUT, "param96.jsonl")):
        r["source"] = "A96"
        R[(r["cls"], r["id"])] = r
    return R


def resolved():
    return {r["id"]: r for r in load(os.path.join(OUT, "resolve96.jsonl"))}


def witness_file(r):
    for d in (os.path.join(BASE, "certs", "param", r.get("cls", "")),
              os.path.join(A95, "param")):
        p = os.path.join(d, r["id"] + ".witnesses.json")
        if os.path.exists(p):
            return p
    return None


def exact_gaps(witfile):
    """The EXACT s-intervals of the undischarged cells (the float coverage summary is a report,
    the witness boxes are the data)."""
    W = json.load(open(witfile))["witnesses"]
    iv = sorted((F(w["box"]["s"][0]), F(w["box"]["s"][1])) for w in W if "box" in w)
    m = []
    for a, b in iv:
        if m and a <= m[-1][1]:
            m[-1][1] = max(m[-1][1], b)
        else:
            m.append([a, b])
    return [(a, b) for a, b in m]


def node_rows(r, res):
    """The closed sub-windows this node is certified on, as exact rationals, and whether the
    whole window is covered.  A FAIL that ran to completion still certifies W minus its witness
    cells; the resolver (resolve96.py) certifies the cells themselves."""
    if r.get("verdict") == "PASS":
        return [(SLO, SHI)], True
    if not r.get("search_complete"):
        return [], False
    wf = witness_file(r)
    if wf is None:
        return [], False
    rr = res.get(r["id"])
    gaps = [(F(a), F(b)) for a, b in rr["gaps"]] if rr else exact_gaps(wf)
    rows, cur = [], SLO
    for a, b in gaps:
        if a > cur:
            rows.append((cur, a))
        cur = max(cur, b)
    if cur < SHI:
        rows.append((cur, SHI))
    if rr:
        for a, b, _, _, _ in rr["rows"]:
            rows.append((F(a), F(b)))
    return sorted(rows), bool(rr and rr["closed"])


def merge(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def width(iv):
    return sum(float(b - a) for a, b in iv)


def intersect(A, B):
    out, i, j = [], 0, 0
    while i < len(A) and j < len(B):
        lo, hi = max(A[i][0], B[j][0]), min(A[i][1], B[j][1])
        if lo < hi:
            out.append([lo, hi])
        if A[i][1] < B[j][1]:
            i += 1
        else:
            j += 1
    return out


def main():
    sel = json.load(open(os.path.join(OUT, "selection96.json")))
    P, res = param_records(), resolved()
    board, allrows = {}, {}
    for cls in CLASSES:
        cand = [c for c in sel["selection"] if c["cls"] == cls and c["level"] == 1]
        st = sel["stats"][cls]
        done, full, partial, notrun = [], 0, 0, 0
        cover_set, rows = None, []
        for c in cand:
            r = P.get((cls, c["id"]))
            if r is None or r.get("verdict") in (None, "TIMEOUT", "EMIT-ERROR", "MALFORMED"):
                notrun += 1
                continue
            done.append(r)
            nr, closed = node_rows(r, res)
            if closed and nr:
                full += 1
            elif nr:
                partial += 1
            else:
                notrun += 1
                continue
            m = merge([[a, b] for a, b in nr])
            cover_set = m if cover_set is None else intersect(cover_set, m)
            for a, b in nr:
                rows.append(dict(node=c["id"], cls=cls, constructor="param",
                                 slo=str(a), shi=str(b), slo_f=float(a), shi_f=float(b),
                                 cert=os.path.join(BASE, "certs", "param", cls,
                                                   c["id"] + ".param.json")))
        rows += [dict(node=None, cls=cls, constructor="logic",
                      note="CI-4: %d logic-killed boxes, recomputed per side by grid.py --ccheck"
                           % COVER_LOGIC[cls])]
        allrows[cls] = rows
        board[cls] = dict(
            cover_ok_boxes=COVER_OK[cls], cover_logic_kills=COVER_LOGIC[cls],
            a57_rows_seen=st["total"], a57_logic_kill=st["logic_kill"],
            a57_alive_needs_level2=st["alive"], a57_malformed_source=st["malformed"],
            candidates=len(cand), parametric_done=len(done),
            full_window=full, partial_window=partial, not_yet_run=notrun,
            boxes_never_emitted=COVER_OK[cls] - st["total"] + st["logic_kill"],
            class_certified_subwindows=[[str(a), str(b), float(a), float(b)]
                                        for a, b in (cover_set or [])],
            class_certified_frac=(round(width(cover_set) / WFLOAT, 9) if cover_set else 0.0),
            note=("class coverage is the INTERSECTION over the nodes verified so far; boxes not "
                  "yet emitted by the running G1 shards and ALIVE boxes awaiting level 2 are "
                  "not included and keep the class open"))
    # ---- cost model ------------------------------------------------------------------
    ok = [r for r in P.values() if r.get("verdict") in ("PASS", "FAIL") and r.get("param_wall_s")]
    pw = [r["param_wall_s"] for r in ok]
    fw = [r["fixed_wall_s"] for r in ok if r.get("fixed_wall_s")]
    t3 = json.load(open(os.path.join(A95, "t3_time.json")))["projection"]
    lad = json.load(open(os.path.join(OUT, "ladder96.json")))
    mean_param = round(statistics.mean(pw), 1) if pw else None
    med_param = round(statistics.median(pw), 1) if pw else None
    proj = dict(measured=dict(n_param_runs=len(pw), mean_param_wall_s=mean_param,
                              median_param_wall_s=med_param,
                              mean_fixed_wall_s=round(statistics.mean(fw), 1) if fw else None,
                              ratio_param_over_one_fixed_side=(
                                  round(statistics.mean(pw) / statistics.mean(fw), 4)
                                  if pw and fw else None)),
                baseline_four_fixed_sides=dict(
                    level1_days_3w=t3["level1_remaining_wall_days_3workers"],
                    level1_plus_level2_days_3w=t3["level1_plus_level2_wall_days_3workers"],
                    level1_days_5w=t3["level1_remaining_wall_days_5workers"],
                    level1_plus_level2_days_5w=t3["level1_plus_level2_wall_days_5workers"]))
    # parametric route: emit ONCE at side 1, verify the window once per node.  Sides 2/3/4 are
    # frozen, so their level-1 and level-2 fixed-side wall disappears entirely.
    day = 86400.0
    tot_l1_lp_s, tot_l1_par_s, tot_l2_s, tot_l2_par_s = 0.0, 0.0, 0.0, 0.0
    per_class = {}
    for nm in ("k5_11", "k5_16"):
        c = t3[nm]
        s1 = c["level1_by_side"]["1"]
        l2 = c["level2_by_side"]["1"]
        lp_s = s1["wall_s"]                                   # LP+cert still to run at side 1
        par_s = s1["ok_children"] * (mean_param or 0)         # one window verify per ok child
        l2_s = l2["wall_s"]
        l2par_s = l2["children"] * (mean_param or 0)
        per_class[nm] = dict(level1_lp_days=round(lp_s / day, 2),
                             level1_param_days=round(par_s / day, 2),
                             level2_lp_days=round(l2_s / day, 2),
                             level2_param_days=round(l2par_s / day, 2))
        tot_l1_lp_s += lp_s; tot_l1_par_s += par_s; tot_l2_s += l2_s; tot_l2_par_s += l2par_s
    # sigma ladder: k5_11 side 1 pays one LP per ORBIT rep instead of per ok box
    g1 = [g for g in lad["a_min_gate"] if g["side"] == 1][0]
    sigma_factor = g1["sigma_lp_children"] / g1["deployed_lp_children"]
    k11 = t3["k5_11"]["level1_by_side"]["1"]
    sigma_saved_s = k11["wall_s"] * (1 - sigma_factor) + k11["ok_children"] * (1 - sigma_factor) * (mean_param or 0)
    tot = tot_l1_lp_s + tot_l1_par_s + tot_l2_s + tot_l2_par_s
    proj["parametric_route"] = dict(
        per_class=per_class,
        total_days_1proc=round(tot / day, 2),
        wall_days_3workers=round(tot / day / 3, 2),
        wall_days_5workers=round(tot / day / 5, 2),
        with_sigma_ladder_days_1proc=round((tot - sigma_saved_s) / day, 2),
        with_sigma_ladder_wall_days_3workers=round((tot - sigma_saved_s) / day / 3, 2),
        with_sigma_ladder_wall_days_5workers=round((tot - sigma_saved_s) / day / 5, 2),
        sigma_lp_children_side1_k5_11=[g1["deployed_lp_children"], g1["sigma_lp_children"]],
        assumption=("level-1 and level-2 nodes are EMITTED once at side 1 (A57's own measured "
                    "LP+certify wall) and each is verified over the whole window once at the "
                    "measured mean parametric wall; sides 2/3/4 do not run at all"))
    # Level-2 sensitivity at the DEPLOYED pin slack.  A95's level-2 cost (216.4 s/child) comes
    # from the L1_D2 rows, which were produced at delta = 0.  A96 ran one deepen shard at
    # delta = 1e-2 (the deployed value) to see whether that number transfers.  Small sample --
    # reported as a sensitivity, never folded into the headline.
    d2 = os.path.join(BASE, "..", "A57-shadow-trees", "results",
                      "tree_k5_11_interior_G1_D2.jsonl")
    if os.path.exists(d2):
        R = load(d2)
        solved = [r for r in R if (r.get("lp_seconds") or 0) > 0]
        w = [(r.get("lp_seconds") or 0) + (r.get("cert_seconds") or 0) for r in solved]
        lk = sum(1 for r in R if (r.get("cert") or "").startswith("KILL-BY-LOGIC"))
        if R:
            scale = (statistics.mean(w) * len(solved) / len(R)) / 216.4 if w else None
            proj["level2_delta1e2_probe"] = dict(
                rows=len(R), parents=len({r["id"].rsplit("_D", 1)[0] for r in R}),
                logic_kill_frac=round(lk / len(R), 3),
                mean_wall_solved_s=round(statistics.mean(w), 1) if w else None,
                mean_wall_per_child_s=round(statistics.mean(w) * len(solved) / len(R), 1) if w else None,
                a95_delta0_per_child_s=216.4,
                cost_scale_vs_a95=round(scale, 3) if scale else None,
                level2_days_1proc_rescaled=round(
                    (per_class["k5_11"]["level2_lp_days"] + per_class["k5_16"]["level2_lp_days"])
                    * (scale or 1), 2),
                caveat=("supply-limited probe, not the 200-child measurement; the headline "
                        "projection still uses A95's delta=0 number"))
    json.dump(proj, open(os.path.join(OUT, "projection96.json"), "w"), indent=1)
    json.dump(board, open(os.path.join(OUT, "scoreboard96.json"), "w"), indent=1)
    for cls, rows in allrows.items():
        json.dump(dict(cls=cls, window=[str(SLO), str(SHI)], n_rows=len(rows), rows=rows,
                       lean=("per param row: python lean/gen_param_lean.py <cert> --depth 56 "
                             "--slo <slo> --shi <shi> --name <node> -o <ParamData.lean>")),
                  open(os.path.join(OUT, f"window_rows_{cls}.json"), "w"), indent=1)
    print(json.dumps(board, indent=1))
    print(json.dumps(proj["parametric_route"], indent=1))
    print(json.dumps(proj["measured"], indent=1))


if __name__ == "__main__":
    main()
