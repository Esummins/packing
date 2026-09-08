"""A151 -- merge the two workers' per-square growth into one spec (they grow disjoint squares).

    python merge_specs.py results/spec_A.json results/spec_B.json -o results/spec_combined.json

The merged spec is a CONJECTURE, not a certificate: widening two squares at once is not implied by
widening each alone.  The verification run (`a151grow.py combined --verify-only --spec ...`) is the
certificate.
"""
from __future__ import annotations
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a151grow as G  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    base = G.base_spec()
    out = {k: dict(v) for k, v in base.items()}
    for p in a.specs:
        s = json.load(open(p, encoding="utf-8"))
        for name, ax in s.items():
            for k, v in ax.items():
                if v > base[name][k] + 1e-12:      # this worker grew this knob
                    out[name][k] = max(out[name][k], v)
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)
    grown = {n: {k: v for k, v in ax.items() if v > base[n][k] + 1e-12} for n, ax in out.items()}
    print("merged ->", a.out)
    print("grown knobs:", json.dumps({k: v for k, v in grown.items() if v}))


if __name__ == "__main__":
    main()
