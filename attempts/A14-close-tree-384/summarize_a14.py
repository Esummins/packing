"""print a table of all A14 node results: python summarize_a14.py [glob ...]"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
pats = sys.argv[1:] or ["results/*.json", "results/br*/child_*.json", "results/l1_*/node_*.json"]
rows = []
for pat in pats:
    for f in sorted(glob.glob(os.path.join(HERE, pat))):
        if f.endswith("_state.json") or os.path.basename(f).startswith(("hyp_", "children", "summary")):
            continue
        try:
            r = json.load(open(f))
        except Exception:
            continue
        if "tau" not in r or "budget" not in r:
            continue
        h = r.get("hyp", {})
        desc = f"{len(h.get('boxes', []))} cores {len(h.get('nofams', []))} nofams"
        rows.append((os.path.relpath(f, HERE), r["s"], r.get("sym"), r["budget"], r["tau"], r["tau"] - r["budget"], r["converged"], r["minmass"], r["maxcov"],
                     r.get("eps_geo"), r["n_rows"], r["n_orbits"], r["time"], desc))
print(f"{'file':44s} {'s':5s} {'sym':3s} {'b':>2s} {'tau':>9s} {'slack':>8s} conv {'mm':>6s} {'mc':>6s} {'eps':>7s} {'rows':>5s} {'orbs':>5s} {'t':>5s}  hyp")
for r in rows:
    print(f"{r[0]:44s} {r[1]:<5} {r[2]:3s} {r[3]:2d} {r[4]:9.4f} {r[5]:+8.4f} {str(r[6])[0]:4s} {r[7]:6.3f} {r[8]:6.3f} {r[9]:7.0e} {r[10]:5d} {r[11]:5d} {r[12]:5.0f}  {r[13]}")
