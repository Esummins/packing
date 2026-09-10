"""A191 -- soundness audit of every kill certificate: (1) the cores are pairwise interior-disjoint EXACTLY (lp168's
SAT test on the rational squares; the bridge budget = n - #cores needs the cores' squares to be distinct, which the
node's hypothesis gives: each core lies inside its role's square and the roles are distinct squares); (2) the bridge
"some square contains the core": the v5 verifier itself binds every core to its `pbox` (= the role's union box, a
superset of the pieces) by A135's exact `point_in_all_poses` on the four corners (HARD REJECT otherwise), so a v5
PASS certifies core inside Q(pi) for every pose of the role [T]; the test against the node record's K' polygon is
INFORMATIONAL only (A172's K' is simplified INWARD, so a core certified against the box may poke outside the
recorded polygon); (3) the frozen-verifier verdict file if present.  Writes results/audit191.json.
"""
import glob
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
RES = os.path.join(BASE, "results")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ATT, "A168-cascade-fable", "code"))
import lp168 as L                                                # noqa: E402  (A168, read-only)
import renorm181 as R8                                           # noqa: E402  (A181, read-only)
from caselp import Core                                          # noqa: E402  (A57, read-only)


def core_of(c):
    return Core(Fr(c["kx"]), Fr(c["ky"]), Fr(c["tm"]), Fr(c["a"]))


def corners(k):
    return [(k.kx + k.a * (i * k.cm - j * k.sm), k.ky + k.a * (i * k.sm + j * k.cm)) for i, j in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def inside_poly(P, x, y):
    n = len(P)
    sgn = 0
    for i in range(n):
        (x0, y0), (x1, y1) = (Fr(P[i][0]), Fr(P[i][1])), (Fr(P[(i + 1) % n][0]), Fr(P[(i + 1) % n][1]))
        cr = (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)
        if cr == 0:
            continue
        s = 1 if cr > 0 else -1
        if sgn == 0:
            sgn = s
        elif s != sgn:
            return False
    return True


def main():
    out = []
    recs = {}
    for f in glob.glob(os.path.join(RES, "run191_*.jsonl")):
        for ln in open(f, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            recs[r["node"]] = r
    side = {c: R8.load_side(c) for c in ("l1_104", "l1_153")}
    for cf in sorted(glob.glob(os.path.join(BASE, "certs", "*_v1.json"))):
        cert = json.load(open(cf, encoding="utf-8"))
        cores = [core_of(c) for c in cert["hypotheses"]["cores"]]
        pair = [dict(i=i, j=j, **dict(zip(("disjoint", "gap"), L.cores_disjoint_exact(cores[i], cores[j]))))
                for i in range(len(cores)) for j in range(i + 1, len(cores))]
        tag = os.path.basename(cf)[:-len("_v1.json")]
        rec = recs.get(tag) or {}
        node = rec.get("record_node")
        roles_json = rec.get("roles_fixed") or ((side.get(rec.get("cell"), {}).get(node) or {}).get("roles"))
        in_k = None
        if roles_json:
            in_k = {}
            for c, name in zip(cores, rec.get("roles") or list(roles_json.keys())):
                P = roles_json[name]["core"]
                in_k[name] = all(inside_poly(P, x, y) for (x, y) in corners(c))
        fz = cf.replace(".json", ".frozen.certify.json")
        frozen = json.load(open(fz))["result"] if os.path.exists(fz) else None
        v5f = cf.replace(".json", ".certify.json")
        v5 = json.load(open(v5f))["result"] if os.path.exists(v5f) else None
        row = dict(cert=os.path.relpath(cf, BASE).replace("\\", "/"), node=node, n_cores=len(cores), budget=cert["budget"],
                   total=float(Fr(cert["total"])), cores_pairwise_disjoint=all(p["disjoint"] for p in pair),
                   min_gap=min((float(p["gap"]) for p in pair), default=None),
                   inside_recorded_Kprime_informational=in_k, core_in_pbox_certified=(v5 == "PASS"), v5=v5, frozen=frozen)
        out.append(row)
        print("%-32s cores %d budget %d total %.4f disjoint %s v5 %s frozen %s" % (
            str(node)[-32:], len(cores), cert["budget"], row["total"], row["cores_pairwise_disjoint"], v5, frozen))
    json.dump(out, open(os.path.join(RES, "audit191.json"), "w"), indent=1, default=str)
    print("audited %d certificates; cores pairwise disjoint on all: %s; core-in-pbox certified by v5 on all: %s; frozen PASS: %d" % (
        len(out), all(r["cores_pairwise_disjoint"] for r in out), all(r["core_in_pbox_certified"] for r in out),
        sum(1 for r in out if r["frozen"] == "PASS")))


if __name__ == "__main__":
    main()
