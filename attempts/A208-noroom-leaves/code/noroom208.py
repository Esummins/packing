"""A208 (coordinator-run, 2026-09-11): the NO-ROOM leaf (A189 Lemma 1) with the pocket CN bound at every ALIVE leaf of
A205's / A206's clip trees that carries >= 9 roles (5 pins + H + >= 3 instantiated meeters).  PI (15:30): "all of the
alive leaves in Y0881 seem to have 10 pinned squares, so they _should_ all die by no_room pretty quickly."
Roles = the leaf's role BOXES (cores from boxes are smaller than from pieces: sound, weaker).  DEAD iff
sum of pocket bounds < n - k, where a pocket of diameter < 1 contributes at most 1 (Lemma CN) and otherwise A189's lane.
Rows -> results/noroom208.jsonl (one per leaf, verdict, pockets, bound, seconds, certificate dict)."""
import sys, os, json, time, glob, math
ROOT = r"C:\Users\esumm\code\packing"
for d in glob.glob(ROOT + r"\attempts\A189*\code") + glob.glob(ROOT + r"\attempts\A171*\code"):
    sys.path.insert(0, d)
import noroom189 as NR
OUT = os.path.join(ROOT, "attempts", "A208-noroom-leaves", "results", "noroom208.jsonl")
done = set()
if os.path.exists(OUT):
    for l in open(OUT, encoding="utf-8"):
        try: d = json.loads(l); done.add((d["nid"], d["run"], d["leaf"]))
        except Exception: pass

def leaves():
    for f in sorted(glob.glob(ROOT + r"\attempts\A206-named-split\certs\*.json")) + sorted(glob.glob(ROOT + r"\attempts\A205-clip-tree\certs\*.json")) + sorted(glob.glob(ROOT + r"\attempts\A205-clip-tree\certs\extended\*.json")):
        try: c = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        nid = c.get("nid") or os.path.basename(f).split("_", 1)[1].rsplit(".", 1)[0]
        runs = c.get("runs") or {}
        if not runs and "pads" in c:
            runs = {("pad_" + p): r for p, r in c["pads"].items()}
        for rk, r in runs.items():
            for n in r.get("nodes") or []:
                if n.get("verdict") != "ALIVE" or n.get("children"):
                    continue
                R = (n.get("snapshot") or {}).get("roles") or {}
                if len(R) < 9: continue
                roles = {k: (v["box"] if isinstance(v, dict) else v) for k, v in R.items()}
                yield f, nid, rk, n.get("label"), roles

def diam(p):
    return math.hypot(p[1] - p[0], p[3] - p[2])

for f, nid, rk, lab, roles in leaves():
    if (nid, rk, lab) in done: continue
    t0 = time.time()
    try:
        out = NR.noroom(roles, s0=None, budget=None, name=lab, n=11)
    except Exception as e:
        out = dict(verdict="ERROR", reason=repr(e)[:300])
    m = 11 - len(roles)
    cn_bound = None
    if out.get("verdict") == "UNDECIDED" and out.get("pockets"):
        # Lemma CN: a pocket of diameter < 1 holds at most one centre; pockets whose union has diameter < 1 count once
        pk = out["pockets"]; groups = []
        for p in pk:
            for g in groups:
                if all(math.hypot(max(abs(p[1]-q[0]), abs(q[1]-p[0])), max(abs(p[3]-q[2]), abs(q[3]-p[2]))) < 1 for q in g): g.append(p); break
            else: groups.append([p])
        cn_bound = sum(1 if all(diam(q) < 1 for q in g) and len(g) >= 1 and all(math.hypot(max(abs(a[1]-b[0]), abs(b[1]-a[0])), max(abs(a[3]-b[2]), abs(b[3]-a[2]))) < 1 for a in g for b in g) else None for g in groups) if all(all(diam(q) < 1 for q in g) for g in groups) else None
        try:
            cn_bound = sum(1 for g in groups)
            if any(any(diam(q) >= 1 for q in g) for g in groups): cn_bound = None
        except Exception: cn_bound = None
        if cn_bound is not None and cn_bound < m:
            out["verdict"] = "DEAD"; out["reason"] = "pocket CN bound %d < %d free squares (%d pocket group(s) of diameter < 1)" % (cn_bound, m, len(groups)); out["cn_bound"] = cn_bound
    row = dict(nid=nid, run=rk, leaf=lab, cert=os.path.relpath(f, ROOT).replace("\\", "/"), k=len(roles), m=m, verdict=out.get("verdict"), bound=out.get("bound"), cn_bound=cn_bound, reason=str(out.get("reason"))[:300], pockets=out.get("pockets"), seconds=round(time.time() - t0, 1), noroom=out, roles={k: v for k, v in roles.items() if not k.startswith("P")}, when=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(OUT, "a", encoding="utf-8") as fh: fh.write(json.dumps(row, default=str) + "\n")
    print("%s %s %s k=%d m=%d -> %s (%s) %.0fs" % (nid, rk, lab, len(roles), m, row["verdict"], row["reason"][:80], row["seconds"]), flush=True)
print("done", flush=True)
