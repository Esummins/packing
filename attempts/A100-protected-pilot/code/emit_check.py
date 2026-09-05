"""A100 pre-flight: does A96's UNMODIFIED emitter accept a PROTECTED-class certificate?

A96's `to_param96.core_affine` anchors every hypothesis core either on a Trump slot
(1/2, 3/2, 5/2 and their s0-reflections) or on the (P-aff) cover family e_q(s) = c0 + q(s - 2c0),
c0 = 11/10, 12q dyadic (docs/proofs/cover_invariance.md).  A84's protected-class cover is
tree57.cover over zones(s0, 0.6)["interior"] = [11/10, s0 - 11/10]^2 at w = 0.15, i.e. nx = 12 --
the SAME grid A57 uses -- and the class pins are exactly slot coordinates.  So the emitter should
accept these certificates verbatim.  This script proves it on A84's k4_08 corpus before any of
A100's own LP wall is spent.  Read-only on A84; writes only to --outdir.
"""
import glob, json, os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import to_param96


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("globs", nargs="+")
    ap.add_argument("--outdir", default=os.path.join(os.environ.get("TEMP", "."), "a100emit"))
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    ok, bad, errs, cores = 0, 0, [], []
    for g in a.globs:
        for p in sorted(glob.glob(g)):
            b = os.path.basename(p)
            if any(x in b for x in (".report.", ".witnesses.", ".resolve", ".certify.",
                                    ".param.")):
                continue
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if d.get("format") != "case-measure-certificate-v1":
                continue
            try:
                r = to_param96.convert(p, os.path.join(a.outdir, b[:-5] + ".param.json"))
                ok += 1
                cores.append(len(r["hypotheses"]["cores"]))
            except Exception as e:
                bad += 1
                errs.append([b, repr(e)[:140]])
    print(json.dumps(dict(emit_ok=ok, emit_error=bad, cores_per_cert=sorted(set(cores)),
                          errors=errs[:8]), indent=1))


if __name__ == "__main__":
    main()
