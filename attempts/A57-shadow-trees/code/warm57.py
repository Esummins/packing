"""
A57 merged warm start (A55/k3_ext E3 lever, generalised).

Union of every atom (column/orbit) and row this lab ever produced for a node, across
A53 (certs_wip + results/nodes), A54 (results/nodes incl. .prev*, _state* checkpoints,
certs/*.resolve*, certs/*.witnesses) and A57's own accumulating artefacts.
Reads only; A53/A54/A55/A56 results are never written.  A29 untouched.

E3: the decisive quantity is the COLUMN set (atoms), not tau.  `atoms_only=True` returns
the column pool without the (large) row set, which is what sibling folding wants.
"""
import glob, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))                      # .../A57-shadow-trees
ATT = os.path.abspath(os.path.join(BASE, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A54 = os.path.join(ATT, "A54-stragglers")
A55 = os.path.join(ATT, "A55-k4-sweep")


def _sources(name):
    S = []
    for root in (A53, A54, A55, BASE):
        S += [os.path.join(root, "results", "nodes", f"{name}.json")]
        S += sorted(glob.glob(os.path.join(root, "results", "nodes", f"{name}.prev*.json")))
        S += sorted(glob.glob(os.path.join(root, "results", "nodes", f"{name}_state*.json")))
        S += sorted(glob.glob(os.path.join(root, "certs_wip", f"{name}.resolve*.json")))
        S += sorted(glob.glob(os.path.join(root, "certs", f"{name}.resolve*.json")))
    return S


def merged_warm(name, extra_sources=(), atoms_only=False, max_atoms=0, max_rows=0):
    atoms, rows, seen_a, seen_r = [], [], set(), set()
    used = []
    for p in list(_sources(name)) + list(extra_sources):
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        used.append(os.path.basename(p))
        for o in d.get("orbits", []):                       # checkpoint columns
            k = (round(o[0], 7), round(o[1], 7))
            if k not in seen_a:
                seen_a.add(k); atoms.append((o[0], o[1]))
        for a in d.get("atoms_all", []):
            k = (round(a[0], 7), round(a[1], 7))
            if k not in seen_a:
                seen_a.add(k); atoms.append((a[0], a[1]))
        if atoms_only:
            continue
        for r in d.get("rows", []):                         # checkpoint rows
            if not (isinstance(r, (list, tuple)) and len(r) == 3):
                continue
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k); rows.append((r[0], r[1], r[2]))
        for r in d.get("rows_all", []):
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k); rows.append((r[0], r[1], r[2]))
    if not atoms_only:
        for wf in glob.glob(os.path.join(A53, "certs_wip", f"{name}*.witnesses.json")) + \
                  glob.glob(os.path.join(A54, "certs", f"{name}*.witnesses.json")) + \
                  glob.glob(os.path.join(BASE, "certs", f"{name}*.witnesses.json")):
            try:
                W = json.load(open(wf))["witnesses"]
            except Exception:
                continue
            used.append(os.path.basename(wf))
            for w in W:
                p = w.get("placement")
                if not p:
                    continue
                th = math.radians(p["theta_deg"])
                for dx, dy in ((0, 0), (0.003, 0), (-0.003, 0), (0, 0.003), (0, -0.003),
                               (0.006, 0.006), (-0.006, -0.006), (0.006, -0.006), (-0.006, 0.006)):
                    for dth in (0.0, 0.004, -0.004):
                        rows.append((p["cx_float"] + dx, p["cy_float"] + dy, th + dth))
    if max_atoms and len(atoms) > max_atoms:
        atoms = atoms[:max_atoms]
    if max_rows and len(rows) > max_rows:
        rows = rows[:max_rows]
    return dict(atoms=atoms, rows=rows), used


if __name__ == "__main__":
    import sys
    for nm in sys.argv[1:]:
        w, u = merged_warm(nm)
        print(nm, len(w["atoms"]), "atoms", len(w["rows"]), "rows from", u)
