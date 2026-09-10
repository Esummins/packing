"""A190 smoke test of the emitter's certificate on A144's stored guard-arm node record of Y0147 (no LP here):
the certificate is built with the record's atoms and A144's z, loaded by verify_case_v5 (rhs* re-derived, pboxes
bound, exact cores), and verified in-process at a small depth.  python smoke190.py [--depth 40]"""
import argparse, json, os, sys, io, contextlib
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.abspath(os.path.join(HERE, "..")); ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, HERE)
import emit190 as E, guardline as G, guardlp, verify_case_v5 as v5           # noqa: E402
ap = argparse.ArgumentParser(); ap.add_argument("--depth", type=int, default=40); a = ap.parse_args()
A144 = os.path.join(ATT, "A144-guard-lines", "results")
rec = json.load(open(os.path.join(A144, "nodes", "k5_11_interior_Y0147_guard.json")))
row = [json.loads(l) for l in open(os.path.join(A144, "invitro144_s0.jsonl")) if l.strip() and '"k5_11_interior_Y0147"' in l][0]
zs = row["arms"]["guard"]["z"]
pins, hbox = G.node_boxes(rec)
H = E.ExactHyp(pins + [hbox], [])
lines, z = [], []
for e in zs:
    L = G.Line(e["line"]["orient"], Fr(e["line"]["off"]), e["line"]["tag"])
    gr = G.guard_row(pins, hbox, L)
    guardlp.attach_costs([L], [gr]); lines.append(L); z.append(float(e["z"]))
print("lines", [(L.orient, float(L.off), round(zz, 4), round(float(L.rhs_exact), 4)) for L, zz in zip(lines, z)])
print("exact cores ok", H.exact_ok, "a_exact", [round(x, 5) for x in H.a_exact])
cert = E.make_certificate_v5(rec, H, lines, z, 1.02, "smoke_Y0147")
p = os.path.join(BASE, "results", "tmp", "smoke_Y0147.json"); json.dump(cert, open(p, "w"), indent=0)
print("atoms", len(cert["atoms"]), "total", float(Fr(cert["total"])), "total_v5", float(Fr(cert["total_v5"])), "budget", cert["budget"])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = v5.main([p, "--jobs", "1", "--depth", str(a.depth), "--max-witnesses", "16", "--quiet", "--report", p[:-5] + ".report.json", "--witness-file", p[:-5] + ".w.json"])
print(buf.getvalue()[-1800:]); print("rc", rc)
