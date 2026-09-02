#!/usr/bin/env python
"""hintcheck.py -- walk a hinted cert's tree for given roots EXACTLY with the frozen
Python verifier's own primitives (split_box, clip_factor, discharge) and report, per
root: cut misses (cut outside interval), vacuous children, leaves discharged by clause,
leaves NOT discharged (with certain/possible mass), depth profile."""
import sys, json, time, collections
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "A73-pair-v2", "code"))
import verify_pair2 as vp
from fractions import Fraction as Fr
cert_path, roots_sel = sys.argv[1], sys.argv[2].split(";")
cert = vp.Cert(cert_path)
doc = json.load(open(cert_path))
trees = doc["hints"]["trees"]
factors, pairs = vp.roots(cert, 2)
clipped = [vp.clip_factor(F, cert.s) for F in factors]
for key in roots_sel:
    i, j = map(int, key.split(","))
    tree = trees.get(key)
    st = vp.Stats()
    stack = [(clipped[i], clipped[j], 0, tree)]
    miss, vac, undis, leaves = 0, 0, [], 0
    t0 = time.time()
    while stack:
        FA, FB, d, tr = stack.pop()
        st.examined += 1
        if tr is not None and "cut" in tr:
            at = vp.rat(tr["cut"]["at"])
            res = vp.split_box(FA, FB, int(tr["cut"]["f"]), {"t": 0, "x": 1, "y": 2}[tr["cut"]["d"]], at)
            if res is None:
                miss += 1
                continue
            for child, sub in zip(res, (tr.get("lo"), tr.get("hi"))):
                A, B = vp.clip_factor(child[0], cert.s), vp.clip_factor(child[1], cert.s)
                if A is None or B is None:
                    vac += 1
                    if sub is not None: print("  NOTE: vac child has a hint subtree at depth", d + 1)
                    continue
                stack.append((A, B, d + 1, sub))
            continue
        leaves += 1
        cl = vp.discharge(cert, FA, FB, st)
        if cl is None:
            _, mass, _ = vp.covered_try(cert, FA, FB, Fr(1))
            undis.append((d, float(mass), vp.possible_mass_f(cert, FA, FB), tr))
    print("root %s: examined=%d leaves=%d miss=%d vac=%d ex=%d nd=%d cov=%d cf=%d undischarged=%d (%.0fs)"
          % (key, st.examined, leaves, miss, vac, st.exempt, st.nondisjoint, st.covered, st.covered_f, len(undis), time.time() - t0))
    if undis:
        print("  undischarged depth hist", sorted(collections.Counter(u[0] for u in undis).items())[:12])
        print("  first few (depth, certain, possible, hint):", [(u[0], round(u[1], 3), round(u[2], 3), u[3]) for u in undis[:5]])
