#!/usr/bin/env python3
"""
gen_param_lean.py -- convert a parametric-kill-certificate-v1 JSON (format of
attempts/A56-sparametric/code/verify_param.py, loader `load_param`) into Lean source
for the PackingCert.ParamI.checkParamI checker
(lean/PackingCertMathlib/PackingCertMathlib/ParamChecker.lean).

Usage:
    python lean/gen_param_lean.py CERT.json --depth 56 --name k5_06_param \
        -o lean/PackingCertMathlib/PackingCertMathlib/ParamData506.lean \
        [--slo 191/50] [--shi 969271/250000] [--margin 0]

Semantics mirror `PVerifier.__init__` exactly: atoms sorted heavy-first (stable), WD =
lcm of all weight denominators, w = numerator * (WD // denominator),
need = ceil((1 + margin) * WD), sDen = S_DEN = 250000 (both s endpoints must lie on that
grid), and the canary C3 window gate 191/50 <= slo <= shi <= 969271/250000.  Cores and
affine atom coefficients are emitted as exact Rat literals.  `nofams` are unsupported by
verify_param.py and rejected here as well.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

S0 = Fraction(969271, 250000)
S_LO_WINDOW = Fraction(191, 50)
S_DEN = 250000


def to_frac(v) -> Fraction:
    if isinstance(v, bool):
        raise ValueError("boolean is not a number")
    if isinstance(v, int):
        return Fraction(v)
    if isinstance(v, float):
        raise ValueError(f"float {v!r} in certificate: refuse (not exact)")
    if isinstance(v, str):
        return Fraction(v.strip())
    raise ValueError(f"cannot parse rational from {v!r}")


def rat_lean(q: Fraction) -> str:
    if q.denominator == 1:
        return f"({q.numerator} : Rat)"
    return f"(({q.numerator} : Rat) / {q.denominator})"


def int_lean(v: int) -> str:
    return f"({v} : Int)" if v < 0 else str(v)


def load_param(path: str):
    """The gates of verify_param.load_param, verbatim in effect."""
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    if p.get("format") != "parametric-kill-certificate-v1":
        raise ValueError(f"unexpected format {p.get('format')!r}")
    hyp = p.get("hypotheses", {}) or {}
    if hyp.get("nofams"):
        raise ValueError("nofams unsupported")
    aff, weights = [], []
    for a in p["atoms"]:
        aff.append((to_frac(a["ax"]), to_frac(a["bx"]), to_frac(a["ay"]), to_frac(a["by"])))
        w = to_frac(a["w"])
        if w < 0:
            raise ValueError("negative weight")
        weights.append(w)
    cores = []
    for c in hyp["cores"]:
        core = (to_frac(c["akx"]), to_frac(c["bkx"]), to_frac(c["aky"]), to_frac(c["bky"]),
                to_frac(c["tm"]), to_frac(c["a"]))
        if not (0 <= core[4] <= 1) or core[5] <= 0:
            raise ValueError("bad core")
        cores.append(core)
    n = int(p.get("n", 11))
    budget = int(p["budget"])
    if budget != n - len(cores):
        raise ValueError(f"budget {budget} != n - #cores")
    total = sum(weights, Fraction(0))
    if to_frac(p["total"]) != total:
        print(f"WARNING: declared total {p['total']} != computed {total}", file=sys.stderr)
    return p, n, budget, aff, weights, cores, total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--depth", type=int, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--slo", default=str(S_LO_WINDOW))
    ap.add_argument("--shi", default=str(S0))
    ap.add_argument("--margin", default="0")
    a = ap.parse_args()

    p, n, budget, aff, weights, cores, total = load_param(a.cert)
    slo, shi = Fraction(a.slo), Fraction(a.shi)
    margin = Fraction(a.margin)
    if not (S_LO_WINDOW <= slo <= shi <= S0):
        raise ValueError(f"s-window [{slo},{shi}] not inside the census window "
                         f"[{S_LO_WINDOW},{S0}] (canary C3)")
    if total >= budget:
        raise ValueError(f"total {total} >= budget {budget}: certificate proves nothing")

    # ---- atoms heavy-first (PVerifier.__init__ ordering)
    order = sorted(range(len(aff)), key=lambda i: -weights[i])
    aff = [aff[i] for i in order]
    weights = [weights[i] for i in order]

    # ---- weights over the common denominator WD
    wd = 1
    for w in weights:
        wd = wd * w.denominator // math.gcd(wd, w.denominator)
    wi = [w.numerator * (wd // w.denominator) for w in weights]

    # ---- need = ceil((1 + margin) * WD)
    need_q = Fraction(1) + margin
    num = need_q.numerator * wd
    need = num // need_q.denominator + (1 if num % need_q.denominator else 0)

    # ---- s endpoints on the 1/S_DEN grid
    sa = slo * S_DEN
    sb = shi * S_DEN
    if sa.denominator != 1:
        raise ValueError(f"s endpoint {slo} not on the grid")
    if sb.denominator != 1:
        raise ValueError(f"s endpoint {shi} not on the grid")
    sa_num, sb_num = sa.numerator, sb.numerator

    atom_lines = [
        f"    {{ alphaX := {rat_lean(ax)}, betaX := {rat_lean(bx)}, "
        f"alphaY := {rat_lean(ay)}, betaY := {rat_lean(by)}, w := {int_lean(w)} }}"
        for (ax, bx, ay, by), w in zip(aff, wi)]
    core_lines = [
        f"    {{ akx := {rat_lean(akx)}, bkx := {rat_lean(bkx)}, "
        f"aky := {rat_lean(aky)}, bky := {rat_lean(bky)}, "
        f"tm := {rat_lean(tm)}, a := {rat_lean(av)} }}"
        for akx, bkx, aky, bky, tm, av in cores]

    out = []
    out.append("import PackingCertMathlib.ParamChecker\n")
    out.append(f"/-!\nAuto-generated by `lean/gen_param_lean.py` from `{a.cert}`.\n"
               f"Do not edit by hand.\n\n"
               f"name = {p.get('name')}, depth = {a.depth}, "
               f"s in [{slo}, {shi}], margin = {margin}.\n"
               f"wd = {wd}, need = {need} (= ceil((1 + margin) * wd)), "
               f"sDen = {S_DEN}, saNum = {sa_num}, sbNum = {sb_num}.\n"
               f"n = {n}, atoms = {len(aff)}, cores = {len(cores)}, budget = {budget}, "
               f"total = {total} (~{float(total):.9f}).\n-/\n")
    out.append("namespace PackingCert.Data\n")
    out.append("open PackingCert.ParamI\n")
    out.append(f"def {a.name} : PCertI := {{")
    out.append(f"  n := {n}")
    out.append(f"  sDen := {S_DEN}")
    out.append(f"  saNum := {int_lean(sa_num)}")
    out.append(f"  sbNum := {int_lean(sb_num)}")
    out.append(f"  wd := {int_lean(wd)}")
    out.append(f"  need := {int_lean(need)}")
    out.append(f"  depth := {a.depth}")
    out.append("  atoms := [")
    out.append(",\n".join(atom_lines))
    out.append("  ]")
    out.append("  cores := [")
    out.append(",\n".join(core_lines))
    out.append("  ] }")
    out.append("")
    out.append("end PackingCert.Data")
    Path(a.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {len(aff)} atoms, {len(cores)} cores, wd = {wd}, "
          f"need = {need}, saNum = {sa_num}, sbNum = {sb_num}, sDen = {S_DEN}, "
          f"budget = {budget}, total = {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
