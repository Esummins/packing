"""A151 T1(b) -- the S02-family population still ALIVE after the night, and its distance to A116's N.

READ-ONLY on every campaign.  Modelled on A137's state137.py (verdict / ancestor-dead rules), with
A149's day ledger and A137's fresh-emission LP rows folded in on top.
"""
from __future__ import annotations
import collections, glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "results")
A107 = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
A116 = os.path.join(ROOT, "attempts", "A116-local-selection-tree", "results")
A137 = os.path.join(ROOT, "attempts", "A137-night-shift-2", "results")
A149 = os.path.join(ROOT, "attempts", "A149-a57-reprice", "results")
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def verdict(rec):
    c = rec.get("cert") or ""
    for pre, name in (("PASS", "PASS"), ("KILL-BY-LOGIC", "logic kill"), ("ALIVE", "ALIVE"),
                      ("FAIL", "FAIL"), ("UNSOUND", "parent box"), ("CANARY", "CANARY"),
                      ("SKIPPED", "skipped")):
        if c.startswith(pre):
            return name
    return "other"


# ------------------------------------------------------------------ corpus
rows = {}
for p in sorted(glob.glob(os.path.join(A57, "tree_*.jsonl"))):
    tree = os.path.basename(p)[5:].rsplit("_s", 1)[0].replace(".jsonl", "")
    for r in jl(p):
        if "id" in r:
            rows[r["id"]] = dict(r, _tree=tree)

dead = {}


def mark(nid, why):
    dead.setdefault(nid, why)


for f, why in (("superseded_by_backlog_A137.jsonl", "A137 fold-in (geometry backlog)"),
               ("superseded_by_exactcore_A137.jsonl", "A137 exact-core re-solve"),
               ("superseded_by_tight_core.jsonl", "tight-core supersession")):
    for r in jl(os.path.join(A57, f)):
        mark(r["id"], why)
for r in jl(os.path.join(A149, "superseded_by_exactcore_A149.jsonl")):
    mark(r["id"], "A149 exact-core re-solve")
for r in jl(os.path.join(A149, "superseded_by_exactcore_v3_A149.jsonl")):
    mark(r["id"], "A149 exact-core re-solve (v3)")
# the night's fresh emission: geometry kills and LP PASSes
geo_rows, lp_rows = [], []
for fn in sorted(os.listdir(A137)):
    if fn.startswith("emit_geo_") and fn.endswith(".jsonl"):
        geo_rows += jl(os.path.join(A137, fn))
    if fn.startswith("emit_lp_") and fn.endswith(".jsonl"):
        lp_rows += jl(os.path.join(A137, fn))
for r in geo_rows:
    if (r.get("cert") or "").startswith("KILL"):
        mark(r["id"], "A137 emission geometry leaf")
for r in lp_rows:
    if r.get("result") == "PASS":
        mark(r["id"], "A137 fresh-emission LP (exact cores)")


def anc_dead(nid):
    parts = nid.split("_D")
    return nid in dead or any("_D".join(parts[:i]) in dead for i in range(1, len(parts)))


alive = {nid: r for nid, r in rows.items()
         if verdict(r) in ("ALIVE", "FAIL") and not anc_dead(nid)}

# ------------------------------------------------------------------ families
sn = json.load(open(os.path.join(A107, "shadow_nodes.json"), encoding="utf-8"))
fam_of = {}
for tag, rr in sn.items():
    for r in rr:
        fam_of.setdefault(r["nid"], tag)


def ancestors(nid):
    out = [nid]
    cur = nid
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
    for k, a in enumerate(ancestors(nid)):
        if a in fam_of:
            return fam_of[a], ("direct" if k == 0 else "ancestor")
    return None, None


# ------------------------------------------------------------------ distance to N (A116)
cons = json.load(open(os.path.join(A116, "t3_consumer.json"), encoding="utf-8"))
census = {}
for key, lst in cons["distance_census"].items():
    for e in lst:
        census[e["nid"]] = dict(dmax=e["dmax"], tmax=e["tmax"], key=key)
inN = {}
for pn in cons["per_N"]:
    N = pn["N"]
    if N["tag"] != "S02":
        continue
    lab = "%s r=%.3f rho=%.1f %s" % (N["cls"], N["r"], N["rho"], N["label"])
    for e in pn["nodes"]:
        inN.setdefault(e["nid"], []).append(lab)

fam_counts = collections.Counter()
s02_alive = []
for nid, r in alive.items():
    fam, how = family(nid)
    fam_counts[fam or "not-in-A107-gallery"] += 1
    if fam == "S02":
        c = census.get(nid) or census.get(ancestors(nid)[-1]) or {}
        s02_alive.append(dict(nid=nid, tree=r["_tree"], level=r.get("level"),
                              verdict=verdict(r), how=how,
                              dmax=c.get("dmax"), tmax=c.get("tmax"),
                              in_symmetric_N=inN.get(nid) or inN.get(ancestors(nid)[-1]) or []))

s02_alive.sort(key=lambda e: (e["dmax"] is None, e["dmax"] or 0))

# distance histogram against A116's certified N boxes
BANDS = [(0.02, 2.0), (0.05, 5.0), (0.10, 10.0), (0.20, 10.0), (0.20, 20.0), (0.30, 20.0)]
hist = collections.Counter()
for e in s02_alive:
    d, t = e["dmax"], e["tmax"]
    if d is None:
        hist["no-census-entry"] += 1
        continue
    placed = False
    for (r_, rho_) in BANDS:
        if d <= r_ and t <= rho_:
            hist["<= r %.2f, rho %.0f" % (r_, rho_)] += 1
            placed = True
            break
    if not placed:
        hist["beyond r 0.30 / rho 20"] += 1

out = dict(n_rows=len(rows), n_dead_marks=len(dead), n_alive=len(alive),
           alive_by_family=dict(fam_counts.most_common()),
           s02_alive_n=len(s02_alive), s02_alive=s02_alive, distance_hist=dict(hist),
           dead_marks_by_source=dict(collections.Counter(dead.values())))
json.dump(out, open(os.path.join(RES, "alive_s02.json"), "w", encoding="utf-8"), indent=1)

print("corpus rows %d  dead marks %d  ALIVE/FAIL open %d" % (len(rows), len(dead), len(alive)))
print("dead marks by source:", json.dumps(out["dead_marks_by_source"], indent=1))
print("alive by A107 family:", json.dumps(out["alive_by_family"], indent=1))
print("S02-family still alive: %d" % len(s02_alive))
print("distance to A116's N (dmax = max centre offset, tmax = max tilt offset, deg):")
for k, v in sorted(hist.items(), key=lambda kv: -kv[1]):
    print("   %-28s %d" % (k, v))
print()
print("| nid | tree | level | verdict | dmax | tmax deg | inside A116 N |")
print("|---|---|---|---|---|---|---|")
for e in s02_alive:
    print("| %s | %s | %s | %s | %s | %s | %s |"
          % (e["nid"], e["tree"], e["level"], e["verdict"],
             "-" if e["dmax"] is None else "%.4f" % e["dmax"],
             "-" if e["tmax"] is None else "%.3f" % e["tmax"],
             "; ".join(e["in_symmetric_N"]) or "-"))
