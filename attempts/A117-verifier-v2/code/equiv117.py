"""A117 T1 -- equivalence of verify_param_v2 with the FROZEN verify_param (v1).

v1 raises `nofams unsupported` on every certificate carrying a NO-family, so no certificate
emitted before A117 contains one and the change CANNOT alter an existing verdict.  This script
proves that claim by running both verifiers, in one process, on the same certificate with the
same flags, and comparing the verdict AND every statistic v1 reports.

Equivalence is checked on v1's OWN key set: v2 adds two breakdown counters
(`exempt_core`, `exempt_nofam`) whose sum must equal v1's `exempt`.

READ-ONLY on every campaign: certificates are opened for reading only; all output goes to
attempts/A117-verifier-v2/results/.

    python equiv117.py --list SELECTION.json --out results/equivalence.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
A96 = os.path.join(ROOT, "attempts", "A96-a57-parametric", "code")
V1_PATH = os.path.join(A96, "verify_param.py")
V2_PATH = os.path.join(A96, "verify_param_v2.py")

# v1's own statistics keys -- the equivalence contract
V1_KEYS = ("boxes", "covered", "vacuous", "exempt", "split", "s_splits", "exact_atom_checks",
           "float_rejects", "max_depth", "max_s_depth", "s_cells", "s_cells_built",
           "depth_hist_covered", "witnesses")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


V1 = _load("a117_v1", V1_PATH)
V2 = _load("a117_v2", V2_PATH)
F = V1.F


class _BoxCap(Exception):
    pass


_CAPPED = {}


def _capped_class(mod):
    """A DETERMINISTIC cap: stop after `box_cap` boxes.  Both verifiers explore boxes in exactly
    the same order, so a capped pair stops at the same box and the comparison is still exact --
    unlike a wall-clock cap, which would not be reproducible."""
    if mod not in _CAPPED:
        class Capped(mod.PVerifier):
            box_cap = 0

            def covered(self, *a, **k):
                if self.box_cap and self.n_boxes > self.box_cap:
                    raise _BoxCap()
                return super().covered(*a, **k)
        _CAPPED[mod] = Capped
    return _CAPPED[mod]


def run_one(mod, cert, slo, shi, depth, split, tscale, sscale, max_w, per_box_cap, use_float,
            box_cap=0):
    """One verifier, one certificate, jobs = 1, in-process.  Returns (verdict, stats, seconds)."""
    t0 = time.time()
    out = mod.load_param(cert)
    p, n, budget, aff, weights, cores, total = out[:7]
    nofams = out[7] if len(out) > 7 else []
    kw = dict(margin=V1.ZERO, depth=depth, tscale=F(tscale), sscale=F(sscale),
              use_float=use_float, max_witnesses=max_w, verbose=False)
    if nofams:
        kw["nofams"] = nofams
    v = _capped_class(mod)(aff, weights, cores, F(slo), F(shi), **kw)
    v.box_cap = box_cap
    boxes = v.root_boxes(split)
    capped = False
    try:
        v.run(boxes, per_box_cap=per_box_cap)
    except _BoxCap:
        capped = True
    st = v.stats()
    st["witnesses"] = len(v.witnesses)
    res = "CAP" if capped else ("PASS" if len(v.witnesses) == 0 else "FAIL")
    return res, st, time.time() - t0


def compare(cert, slo, shi, depth, split, tscale, sscale, max_w, per_box_cap, use_float,
            box_cap=0):
    r1, s1, t1 = run_one(V1, cert, slo, shi, depth, split, tscale, sscale, max_w,
                         per_box_cap, use_float, box_cap)
    r2, s2, t2 = run_one(V2, cert, slo, shi, depth, split, tscale, sscale, max_w,
                         per_box_cap, use_float, box_cap)
    diffs = []
    if r1 != r2:
        diffs.append(f"verdict {r1} != {r2}")
    for k in V1_KEYS:
        if s1.get(k) != s2.get(k):
            diffs.append(f"{k}: {s1.get(k)} != {s2.get(k)}")
    for k in s1:
        if k not in V1_KEYS:
            diffs.append(f"v1 stat key {k!r} not in the equivalence contract")
    extra = set(s2) - set(s1)
    if extra != {"exempt_core", "exempt_nofam"}:
        diffs.append(f"v2 extra stat keys {sorted(extra)} != ['exempt_core','exempt_nofam']")
    if s2.get("exempt_core", 0) + s2.get("exempt_nofam", 0) != s2.get("exempt"):
        diffs.append("v2 exempt_core + exempt_nofam != exempt")
    if s2.get("exempt_nofam", 0) != 0:
        diffs.append("v2 fired the NO-family rule on a certificate with no NO-families")
    return dict(cert=os.path.relpath(cert, ROOT).replace("\\", "/"),
                slo=slo, shi=shi, depth=depth, split=split, tscale=tscale, sscale=sscale,
                v1=dict(result=r1, boxes=s1["boxes"], covered=s1["covered"],
                        vacuous=s1["vacuous"], exempt=s1["exempt"], witnesses=s1["witnesses"],
                        seconds=round(t1, 3)),
                v2=dict(result=r2, boxes=s2["boxes"], covered=s2["covered"],
                        vacuous=s2["vacuous"], exempt=s2["exempt"], witnesses=s2["witnesses"],
                        exempt_core=s2["exempt_core"], exempt_nofam=s2["exempt_nofam"],
                        seconds=round(t2, 3)),
                identical=(not diffs), diffs=diffs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True, help="JSON list of {cert, slo, shi, depth, ...}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--box-cap", type=int, default=0,
                    help="deterministic cap: stop both verifiers after this many boxes (0 = none)")
    a = ap.parse_args()
    sel = json.load(open(a.list))
    rows = []
    for i, e in enumerate(sel):
        cert = e["cert"] if os.path.isabs(e["cert"]) else os.path.join(ROOT, e["cert"])
        try:
            r = compare(cert, e.get("slo", "191/50"), e.get("shi", "969271/250000"),
                        int(e.get("depth", 48)), int(e.get("split", 3)),
                        str(e.get("tscale", "2")), str(e.get("sscale", "8")),
                        int(e.get("max_witnesses", 200)),
                        int(e.get("max_witnesses_per_box", 8)),
                        bool(e.get("use_float", True)), a.box_cap)
        except Exception as exc:                                 # a malformed cert is a data fact
            r = dict(cert=e["cert"], identical=False, diffs=[f"EXCEPTION {exc!r}"])
        r["tag"] = e.get("tag", "")
        rows.append(r)
        print(f"[{i+1}/{len(sel)}] {r['cert']}  "
              f"{'IDENTICAL' if r['identical'] else 'DIFFERS ' + str(r['diffs'])}  "
              f"{r.get('v1', {}).get('result', '?')}  boxes={r.get('v1', {}).get('boxes', '?')}",
              flush=True)
    n_ok = sum(1 for r in rows if r["identical"])
    doc = dict(n=len(rows), identical=n_ok, differing=len(rows) - n_ok,
               v1_sha256=_sha(V1_PATH), v2_sha256=_sha(V2_PATH), rows=rows)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(doc, open(a.out, "w"), indent=1)
    print(f"\n{n_ok}/{len(rows)} byte-identical (verdict + every v1 statistic)")
    return 0 if n_ok == len(rows) else 1


def _sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
