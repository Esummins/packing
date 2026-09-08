"""A151 T1 -- join the night's kill records to A107's shadow families and report kill rates.

READ-ONLY on every campaign.  Writes only under attempts/A151-pinwheel-basin/results/.

Three lanes are kept apart (the `lane` field in A137's rows says "exact-core re-emission" for BOTH
the re-solve of the pre-existing ALIVE population and the first LP of the night's fresh children;
the file each row sits in is what distinguishes them):

  L1  exact-core RE-SOLVE of the pre-existing ALIVE population
      A137 results/exact_reemit_w{0,1}.jsonl   +  A149 results/exact_reemit_w{0..3}.jsonl
  L2  fresh-emission LP with exact cores (first LP of a child emitted that night)
      A137 results/emit_lp_combined.jsonl, emit_lp_k5_11_interior_G1_s0.jsonl
  L3  geometric leaves at emission (T5' at the exact pin core, T5''' clip, T5'''' polygon)
      A137 results/emit_geo_*.jsonl (kills) against the screened population
      (kills + the LP queue results/queue_bc.json + the rows of L2)
"""
from __future__ import annotations
import json, os, re, sys, glob, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A107 = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
A137 = os.path.join(ROOT, "attempts", "A137-night-shift-2", "results")
A149 = os.path.join(ROOT, "attempts", "A149-a57-reprice", "results")
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)


def jl(path):
    out = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


# ------------------------------------------------------------------ families
sn = json.load(open(os.path.join(A107, "shadow_nodes.json"), encoding="utf-8"))
ex = json.load(open(os.path.join(A107, "extract.json"), encoding="utf-8"))
nodes = ex["nodes"]
fam_of = {}
for tag, rows in sn.items():
    for r in rows:
        fam_of.setdefault(r["nid"], tag)
integral_of = {n["nid"]: bool(n["integral"]) for n in nodes}
unexpl_nids = {nodes[i]["nid"] for i in ex["unexplained"]}


def ancestors(nid):
    out, cur = [nid], nid
    while True:
        m = re.match(r"^(.*)_D\d\d$", cur)
        if not m:
            break
        cur = m.group(1)
        out.append(cur)
    m = re.match(r"^(.*Y\d{4})[ab]$", out[-1])
    if m:
        out.append(m.group(1))
    return out


def family(nid):
    anc = ancestors(nid)
    for a in anc:
        if a in fam_of:
            return fam_of[a]
    for a in anc:
        if a in unexpl_nids:
            return "fractional" if not integral_of.get(a, True) else "unexplained-integral"
    for a in anc:
        if a in integral_of:
            return "fractional" if not integral_of[a] else "unexplained-integral"
    return "post-A107 (no gallery entry)"


ORDER = ["S02", "S01", "S07", "other-shadow", "fractional", "unexplained-integral",
         "post-A107 (no gallery entry)"]


def bucket(f):
    if f in ("S02", "S01", "S07", "fractional", "unexplained-integral",
             "post-A107 (no gallery entry)"):
        return f
    return "other-shadow"


# ------------------------------------------------------------------ L1 / L2
def load_lane(paths):
    by_id = {}
    for p in paths:
        for r in jl(p):
            by_id[r["id"]] = r          # a node re-solved twice: the later file wins
    return by_id


L1 = load_lane([os.path.join(A137, "exact_reemit_w0.jsonl"),
                os.path.join(A137, "exact_reemit_w1.jsonl")]
               + sorted(glob.glob(os.path.join(A149, "exact_reemit_w*.jsonl"))))
L2 = load_lane([os.path.join(A137, "emit_lp_combined.jsonl"),
                os.path.join(A137, "emit_lp_k5_11_interior_G1_s0.jsonl")])

RESULTS = ["PASS", "NO-KILL", "LOST-KILL-ON-RESOLVE", "TOO-TIGHT", "FAIL", "WALL-CAP"]


def lp_table(lane, title):
    tab = collections.defaultdict(collections.Counter)
    walls = collections.defaultdict(list)
    for nid, r in lane.items():
        b = bucket(family(nid))
        tab[b][r.get("result", "?")] += 1
        tab[b]["_n"] += 1
        walls[b].append(r.get("wall_total_s") or r.get("wall_s") or 0.0)
    lines = ["", "### " + title, "",
             "| family | n | " + " | ".join(RESULTS) + " | decided | **kill rate** | median wall |",
             "|---|---|" + "---|" * (len(RESULTS) + 3)]
    tot, allw = collections.Counter(), []
    for b in ORDER:
        c = tab.get(b)
        if not c:
            continue
        dec = c["_n"] - c["WALL-CAP"]
        tot.update(c); allw += walls[b]
        lines.append("| %s | %d | %s | %d | **%.1f %%** | %.0f s |"
                     % (b, c["_n"], " | ".join(str(c.get(k, 0)) for k in RESULTS), dec,
                        (100.0 * c["PASS"] / dec) if dec else 0.0,
                        statistics.median(walls[b])))
    dec = tot["_n"] - tot["WALL-CAP"]
    lines.append("| **all** | %d | %s | %d | **%.1f %%** | %.0f s |"
                 % (tot["_n"], " | ".join(str(tot.get(k, 0)) for k in RESULTS), dec,
                    (100.0 * tot["PASS"] / dec) if dec else 0.0, statistics.median(allw)))
    return "\n".join(lines), tab


# ------------------------------------------------------------------ L3 geometry
geo = {}
for fn in sorted(os.listdir(A137)):
    if fn.startswith("emit_geo_") and fn.endswith(".jsonl"):
        for r in jl(os.path.join(A137, fn)):
            geo[r["id"]] = r
queue = {q["id"] for q in json.load(open(os.path.join(A137, "queue_bc.json"), encoding="utf-8"))}
screened = set(geo) | queue | set(L2)

LEAVES = ["T5' exact core", "T5''' clip", "T5'''' polygon", "other"]


def leaf_of(r):
    lf = (r.get("leaf") or "")
    if "T5'" in lf and "tight core" in lf:
        return "T5' exact core"
    if "clip" in lf.lower():
        return "T5''' clip"
    if "poly" in lf.lower():
        return "T5'''' polygon"
    return "other"


tab_geo = collections.defaultdict(collections.Counter)
for nid in screened:
    b = bucket(family(nid))
    tab_geo[b]["_screened"] += 1
    lvl = min(nid.count("_D") + 1, 4)
    tab_geo[b]["L%d_screened" % lvl] += 1
    if nid in geo and (geo[nid].get("cert") or "").startswith("KILL"):
        tab_geo[b]["_kill"] += 1
        tab_geo[b][leaf_of(geo[nid])] += 1
        tab_geo[b]["L%d_kill" % lvl] += 1

lines = ["", "### L3 -- geometric leaves at emission (kill rate = dead by geometry / screened)", "",
         "| family | screened | dead | " + " | ".join(LEAVES) + " | **kill rate** | L1 | L2 | L3 |",
         "|---|---|---|" + "---|" * (len(LEAVES) + 4)]
tot = collections.Counter()
for b in ORDER:
    c = tab_geo.get(b)
    if not c:
        continue
    tot.update(c)
    lines.append("| %s | %d | %d | %s | **%.1f %%** | %d/%d | %d/%d | %d/%d |"
                 % (b, c["_screened"], c["_kill"], " | ".join(str(c.get(k, 0)) for k in LEAVES),
                    100.0 * c["_kill"] / c["_screened"],
                    c["L1_kill"], c["L1_screened"], c["L2_kill"], c["L2_screened"],
                    c["L3_kill"], c["L3_screened"]))
lines.append("| **all** | %d | %d | %s | **%.1f %%** | %d/%d | %d/%d | %d/%d |"
             % (tot["_screened"], tot["_kill"], " | ".join(str(tot.get(k, 0)) for k in LEAVES),
                100.0 * tot["_kill"] / tot["_screened"],
                tot["L1_kill"], tot["L1_screened"], tot["L2_kill"], tot["L2_screened"],
                tot["L3_kill"], tot["L3_screened"]))
geo_md = "\n".join(lines)

t1, tabA = lp_table(L1, "L1 -- exact-pin-core RE-SOLVE of the pre-existing ALIVE population "
                        "(A137 163 + A149 57 = %d nodes)" % len(L1))
t2, tabB = lp_table(L2, "L2 -- fresh-emission LP with exact cores (first LP of a child emitted "
                        "that night, %d nodes)" % len(L2))

out = ["# A151 T1 -- kill rates by A107 shadow family (A137 night 2026-09-07/08 + A149 day)", "",
       "Family = A107's shadow attribution of the node itself, or of its nearest ancestor that "
       "the gallery classifies. `post-A107` = a child emitted after A107's gallery was built "
       "(A107 covers 1,566 of the 3,160 corpus rows), so it has no ancestor in the gallery at all.",
       t1, t2, geo_md]
txt = "\n".join(out)
print(txt)
with open(os.path.join(RES, "family_rates.md"), "w", encoding="utf-8") as f:
    f.write(txt + "\n")
json.dump(dict(L1={k: dict(v) for k, v in tabA.items()},
               L2={k: dict(v) for k, v in tabB.items()},
               L3={k: dict(v) for k, v in tab_geo.items()},
               L1_rows={nid: dict(result=r.get("result"), family=family(nid), level=r.get("level"),
                                  cls=r.get("cls"), tau=r.get("tau"),
                                  wall=r.get("wall_total_s") or r.get("wall_s"))
                        for nid, r in L1.items()}),
          open(os.path.join(RES, "family_rates.json"), "w", encoding="utf-8"), indent=1)
