"""A170 -- REGRESSION TEST for the `make_certificate` stock-core reversion.

The test the lab was missing: emit a certificate through the WRAPPER and assert that every core it
carries equals `exactcore.exact_a` of the box that core carries, on 50 random boxes.  It also
demonstrates the failure it guards against, by asserting that the UNWRAPPED
`caselp.make_certificate` writes the STOCK core on the same input whenever the exact core is
strictly larger.

Boxes: 50 pseudo-random parameter boxes (fixed seed) spanning the shapes the campaigns use --
pins (`th0 == th1 == 0`), tilted windows, and wide-tilt k0 cells -- plus, when they are on disk,
boxes lifted verbatim from real certificates so the test tracks the deployed corpus.

No LP is solved: `make_certificate` only reads `res["atoms_all"]`, `res["hyp"]`, `res["budget"]`,
`res["tau"]` and `res["s"]`, so a synthetic single-atom measure exercises the whole emission path.

    python code/test_cores170.py            # -> "50/50 OK" and exit 0
"""
import glob
import json
import os
import random
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, HERE)

import certwrap170 as W                                        # noqa: E402
import caselp                                                  # noqa: E402  READ-ONLY (A57)
from caselp import Box, Hyp                                    # noqa: E402  READ-ONLY (A57)
import exactcore as EC                                         # noqa: E402  READ-ONLY (A135)

S0_RAT = "969271/250000"
S0 = float(Fr(S0_RAT))
N = 50


def random_boxes(n, seed=1701):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        kind = rng.choice(("pin", "tilt", "wide"))
        cx = rng.uniform(0.6, S0 - 0.6)
        cy = rng.uniform(0.6, S0 - 0.6)
        if kind == "pin":
            d = rng.choice((0.005, 0.01, 0.02)) / (2 ** 0.5)
            b = Box(cx - d, cx + d, cy - d, cy + d, 0.0, 0.0)
        elif kind == "tilt":
            h = rng.uniform(0.002, 0.03)
            t0 = rng.uniform(0.0, 80.0)
            b = Box(cx - h, cx + h, cy - h, cy + h, t0, t0 + rng.uniform(0.05, 3.0))
        else:
            h = rng.uniform(0.02, 0.09)
            t0 = rng.uniform(0.0, 45.0)
            b = Box(cx - h, cx + h, cy - h, cy + h, t0, t0 + rng.uniform(5.0, 20.0))
        if b.core() is None:
            continue
        try:
            a, _a0, ok = EC.exact_a(b)
        except Exception:                                      # noqa: BLE001
            continue
        if a is None or not ok:
            continue
        out.append(b)
    return out


def corpus_boxes(limit):
    """boxes lifted verbatim from certificates on disk, so the test tracks the real corpus."""
    out = []
    for f in sorted(glob.glob(os.path.join(ATT, "*", "certs", "*.json")))[::37]:
        if f.endswith((".report.json", ".witnesses.json", ".certify.json")):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            continue
        if d.get("format") != "case-measure-certificate-v1":
            continue
        for c in (d.get("hypotheses", {}) or {}).get("cores") or []:
            b = W.box_from_core_json(c)
            if b is None or b.core() is None:
                continue
            try:
                a, _a0, ok = EC.exact_a(b)
            except Exception:                                  # noqa: BLE001
                continue
            if a is not None and ok:
                out.append(b)
            if len(out) >= limit:
                return out
    return out


def fake_res(boxes, budget=None, s=S0):
    hyp = Hyp(list(boxes), [])
    return dict(s=s, budget=(budget if budget is not None else max(1, 11 - len(boxes))),
                tau=1.0, atoms_all=[[0.5, 0.5, 0.001]], rows_all=[],
                hyp=hyp.to_json()), hyp


def main():
    boxes = corpus_boxes(N // 2)
    boxes += random_boxes(N - len(boxes))
    assert len(boxes) == N, len(boxes)
    ok = bad = witnessed = 0
    fails = []
    for i, b in enumerate(boxes):
        res, hyp = fake_res([b])
        a_exact, a_stock, cert_ok = EC.exact_a(b)
        assert cert_ok, "exact_a vertex test failed on box %d" % i

        # 1) the WRAPPER carries the exact core
        cert = W.make_certificate_exact(res, S0_RAT, scale=1.005, hyp=hyp)
        got = Fr(cert["hypotheses"]["cores"][0]["a"])
        if got != a_exact:
            bad += 1
            fails.append(dict(i=i, box=b.to_json(), got=str(got), want=str(a_exact),
                              which="wrapper"))
            continue

        # 2) the recompute-from-the-certificate's-own-box path agrees
        cert2 = W.make_certificate_exact(res, S0_RAT, scale=1.005)
        if Fr(cert2["hypotheses"]["cores"][0]["a"]) != a_exact:
            bad += 1
            fails.append(dict(i=i, box=b.to_json(), which="recompute-from-box",
                              got=cert2["hypotheses"]["cores"][0]["a"], want=str(a_exact)))
            continue

        # 3) the guarded regression: the UNWRAPPED emitter writes the stock core
        raw = caselp.make_certificate(res, S0_RAT, scale=1.005)
        raw_a = Fr(raw["hypotheses"]["cores"][0]["a"])
        if raw_a != a_stock:
            bad += 1
            fails.append(dict(i=i, box=b.to_json(), which="raw!=stock",
                              got=str(raw_a), want=str(a_stock)))
            continue
        if a_exact > a_stock:
            witnessed += 1
        ok += 1
    print("%d/%d OK  (%d of them witness the bug the wrapper repairs: exact core strictly larger "
          "than the stock core `make_certificate` would have written)" % (ok, N, witnessed))
    if fails:
        print("FAILURES:")
        for f in fails[:10]:
            print("  ", json.dumps(f))
    json.dump(dict(n=N, ok=ok, bad=bad, witnessed=witnessed, failures=fails),
              open(os.path.join(BASE, "results", "test_cores170.json"), "w"), indent=1)
    return 0 if bad == 0 and ok == N else 1


if __name__ == "__main__":
    sys.exit(main())
