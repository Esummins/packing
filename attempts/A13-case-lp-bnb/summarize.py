"""summarize a B&B tree: python summarize.py results/<tag>/tree.json"""
import json, sys, math, collections
T = json.load(open(sys.argv[1]))
nodes = T["nodes"]
print(f"s={T['s']} tag={T['tag']} LPs={T['n_lp']} elapsed={T['elapsed']:.0f}s nodes={len(nodes)}")
st = collections.Counter(n["status"] for n in nodes)
print("status:", dict(st))
bd = collections.defaultdict(collections.Counter)
for n in nodes:
    bd[n["depth"]][n["status"]] += 1
for d in sorted(bd):
    solved = sum(v for k, v in bd[d].items() if k not in ("pending", "running"))
    dead = sum(v for k, v in bd[d].items() if k.startswith("dead"))
    print(f"  depth {d}: {dict(bd[d])}  solved={solved} dead-frac={dead/max(1,solved):.2f}")
lt = [n["lp_time"] for n in nodes if n.get("lp_time")]
if lt:
    print(f"LP time: mean {sum(lt)/len(lt):.0f}s, max {max(lt):.0f}s, n={len(lt)}")
print("branch types:", collections.Counter((n.get("branch_on") or "-").split(" ")[0] for n in nodes if n.get("branch_on")))
kinds = collections.Counter()
for n in nodes:
    b = n["branch"]
    k = "root" if b == "root" else ("NO" if b.startswith("NO") else ("YES" if b.startswith("YES") else "REFINE"))
    kinds[(k, n["status"])] += 1
print("by branch kind x status:", dict(kinds))
alive = [n for n in nodes if n["status"] == "alive"]
print("alive (solved) nodes: slack list:", sorted([round(n["tau"] - n["budget"], 3) for n in alive], reverse=True)[:40])
byb = collections.defaultdict(list)
for n in nodes:
    if n.get("tau") is not None:
        byb[n["budget"]].append((n["tau"] - n["budget"], n["status"]))
for b in sorted(byb, reverse=True):
    xs = byb[b]
    print(f"  budget {b}: n={len(xs)} dead={sum(1 for x in xs if x[1].startswith('dead'))} alive={sum(1 for x in xs if x[1]=='alive')} "
          f"slack min/max {min(x[0] for x in xs):+.3f}/{max(x[0] for x in xs):+.3f}")
if len(sys.argv) > 2:
    for n in nodes:
        if n.get("tau") is not None:
            print(f"{n['id']:4d} d{n['depth']} p{n['parent']} {n['sym']} b{n['budget']} tau={n['tau']:.4f} slack={n['tau']-n['budget']:+.4f} "
                  f"{n['status']:7s} conv={n.get('converged')} mm={n.get('minmass',0):.2f} mc={n.get('maxcov',0):.2f} t={n.get('lp_time',0):.0f} | {n['branch'][:90]}")
