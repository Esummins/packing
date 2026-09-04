#!/usr/bin/env python3
r"""
gen_crowd_lean.py -- A93 T1: emit the isolated Lean replay modules for ONE crowd-weighted
certificate C(delta, m_lo) (A92 Lemma CW: two runs of the frozen verify_case.py on one
measure, `attempts/A92-blocked-side/certs/runA_<tag>.json` / `runB_<tag>.json`).

Writes (the pair Data_* / Check_* is the isolation unit, as in gen_corpus_lean.py):

  PackingCertMathlib/Corpus/Crowd/Data_<tag>_A.lean     `Data.crowd_<tag>_A : CCertI`
  PackingCertMathlib/Corpus/Crowd/Data_<tag>_B.lean     `Data.crowd_<tag>_B : CCertI`
        (both by `lean/gen_case_lean.py`, at the depth of the run's .report.json)
  PackingCertMathlib/Corpus/Crowd/Check_<tag>.lean
        check_crowd_<tag>_A  : checkCaseI Data.crowd_<tag>_A = true          (native_decide)
        check_crowd_<tag>_B  : checkCaseI Data.crowd_<tag>_B = true          (native_decide)
        same_crowd_<tag>     : sameMeasure A B eNum eDen = true              (native_decide)
        zones_crowd_<tag>    : crowdZones B.sNum B.sDen a_w fuel B.nofams = true (native_decide)
        crowdKill_<tag>      : CrowdKill delta m_lo s0                       (crowdKill_of_files)

Parameters (exact rationals as strings): --e (the crowd weight e, 8e integer), --delta,
--mlo (window floor, default 191/50), --aw (the certificate's a_w; default = the pad formula
lambda(1-delta) + (lambda-1)*7072/10000 rounded UP to 1e-5, lambda = s0/m_lo, as the chore
does), --fuel (bisection depth of the zone checker, default 10).

Build (isolated, one module, cache-hit elsewhere):
    python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Corpus.Crowd.Check_<tag>
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEANDIR = REPO / "lean" / "PackingCertMathlib" / "PackingCertMathlib"
OUTDIR = LEANDIR / "Corpus" / "Crowd"
GEN_CASE = REPO / "lean" / "gen_case_lean.py"


def frac(s: str) -> Fraction:
    return Fraction(str(s).strip())


def rat_lit(q: Fraction) -> str:
    """A `Rat` literal usable both as a Rat and (after cast) as a real."""
    if q.denominator == 1:
        return f"({q.numerator} : Rat)"
    return f"(({q.numerator} : Rat) / {q.denominator})"


def real_lit(q: Fraction) -> str:
    if q.denominator == 1:
        return f"({q.numerator} : ℝ)"
    return f"(({q.numerator} : ℝ) / {q.denominator})"


def report_depth(cert: Path) -> int:
    rep = cert.with_suffix(".report.json")
    if rep.exists():
        d = json.loads(rep.read_text(encoding="utf-8"))
        for k in ("depth", "max_depth", "cert_depth"):
            if k in d:
                return int(d[k])
        if "settings" in d and "depth" in d["settings"]:
            return int(d["settings"]["depth"])
    return 56


def run_gen_case(cert: Path, depth: int, name: str, out: Path) -> str:
    cmd = [sys.executable, str(GEN_CASE), str(cert), "--depth", str(depth),
           "--name", name, "-o", str(out)]
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"gen_case_lean failed on {cert}")
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runA", required=True)
    ap.add_argument("--runB", required=True)
    ap.add_argument("--tag", required=True, help="identifier-safe tag, e.g. d0_10_e1")
    ap.add_argument("--e", required=True, help="crowd weight e (rational, 8e integer)")
    ap.add_argument("--delta", required=True, help="depth delta (rational)")
    ap.add_argument("--mlo", default="191/50")
    ap.add_argument("--aw", default=None, help="a_w (rational); default = chore's pad formula")
    ap.add_argument("--fuel", type=int, default=10)
    ap.add_argument("--depthA", type=int, default=None)
    ap.add_argument("--depthB", type=int, default=None)
    a = ap.parse_args()

    runA, runB = Path(a.runA), Path(a.runB)
    dA = json.loads(runA.read_text(encoding="utf-8"))
    dB = json.loads(runB.read_text(encoding="utf-8"))
    s0 = frac(dA["s"])
    assert frac(dB["s"]) == s0, "runs at different sides"
    e = frac(a.e)
    assert (8 * e).denominator == 1 and e >= 0, "8e must be a nonnegative integer"
    nA = int(dA.get("n", 11))
    assert Fraction(nA) <= 11 + 8 * e, "run A's n exceeds 11 + 8e"
    assert not (dA.get("hypotheses") or {}).get("cores"), "run A must have no cores"
    assert not (dA.get("hypotheses") or {}).get("nofams"), "run A must have no NO-families"
    assert not (dB.get("hypotheses") or {}).get("cores"), "run B must have no cores"
    delta = frac(a.delta)
    mlo = frac(a.mlo)
    assert 0 < mlo < s0 and delta <= 1
    lam = s0 / mlo
    pad = lam * (1 - delta) + (lam - 1) * Fraction(7072, 10000)
    if a.aw is None:
        aw = Fraction(math.ceil(pad * 100000), 100000)
    else:
        aw = frac(a.aw)
    assert pad <= aw, f"a_w = {aw} below the pad {pad}"
    assert 2 * aw <= s0 and (s0 - 2 * aw) ** 2 > 2, "corner boxes not separated"

    OUTDIR.mkdir(parents=True, exist_ok=True)
    tag = a.tag
    nameA, nameB = f"crowd_{tag}_A", f"crowd_{tag}_B"
    depthA = a.depthA if a.depthA is not None else report_depth(runA)
    depthB = a.depthB if a.depthB is not None else report_depth(runB)
    print(run_gen_case(runA, depthA, nameA, OUTDIR / f"Data_{tag}_A.lean"))
    print(run_gen_case(runB, depthB, nameB, OUTDIR / f"Data_{tag}_B.lean"))

    eN, eD = e.numerator, e.denominator
    L = []
    L.append(f"import PackingCertMathlib.CrowdZone")
    L.append(f"import PackingCertMathlib.Corpus.Crowd.Data_{tag}_A")
    L.append(f"import PackingCertMathlib.Corpus.Crowd.Data_{tag}_B")
    L.append("")
    L.append("/-!")
    L.append(f"Auto-generated by `lean/gen_crowd_lean.py`: the crowd certificate `{tag}`")
    L.append(f"(A92 Lemma CW), runs `{runA.name}` / `{runB.name}` at side `{s0}`,")
    L.append(f"e = {e}, delta = {delta}, m_lo = {mlo}, a_w = {aw} (pad {pad}).")
    L.append("Do not edit by hand.")
    L.append("-/")
    L.append("")
    L.append("namespace PackingCert")
    L.append("namespace S11")
    L.append("")
    L.append("open CaseI")
    L.append("")
    L.append(f"/-- Run A PASSes (`native_decide`). -/")
    L.append(f"theorem check_{nameA} : checkCaseI Data.{nameA} = true := by")
    L.append("  native_decide")
    L.append("")
    L.append(f"/-- Run B PASSes (`native_decide`). -/")
    L.append(f"theorem check_{nameB} : checkCaseI Data.{nameB} = true := by")
    L.append("  native_decide")
    L.append("")
    L.append(f"/-- One measure: run B's weights are run A's divided by `1 + e`, e = {e}. -/")
    L.append(f"theorem same_crowd_{tag} : sameMeasure Data.{nameA} Data.{nameB} {eN} {eD} = true := by")
    L.append("  native_decide")
    L.append("")
    L.append(f"/-- Run B's NO-families avoid the crowd family of box size a_w = {aw} at every corner. -/")
    L.append(f"theorem zones_crowd_{tag} : crowdZones Data.{nameB}.sNum Data.{nameB}.sDen "
             f"{rat_lit(aw)} {a.fuel} Data.{nameB}.nofams = true := by")
    L.append("  native_decide")
    L.append("")
    L.append(f"theorem crowd_{tag}_sideA : caseSide Data.{nameA} = {real_lit(s0)} := by")
    L.append(f"  rw [caseSide, show Data.{nameA}.sNum = {s0.numerator} from rfl, "
             f"show Data.{nameA}.sDen = {s0.denominator} from rfl]")
    L.append("  push_cast")
    L.append("  norm_num")
    L.append("")
    L.append(f"theorem crowd_{tag}_sideB : caseSide Data.{nameB} = {real_lit(s0)} := by")
    L.append(f"  rw [caseSide, show Data.{nameB}.sNum = {s0.numerator} from rfl, "
             f"show Data.{nameB}.sDen = {s0.denominator} from rfl]")
    L.append("  push_cast")
    L.append("  norm_num")
    L.append("")
    L.append(f"/-- **C({delta}, {mlo})** (Theorem S(δ) in window form): no packing at any side")
    L.append(f"`m ∈ [{mlo}, {s0})` has two distinct squares at depth `≥ {delta}` at every corner. -/")
    L.append(f"theorem crowdKill_{tag} : CrowdKill {real_lit(delta)} {real_lit(mlo)} {real_lit(s0)} := by")
    L.append(f"  rw [← crowd_{tag}_sideA]")
    L.append(f"  refine crowdKill_of_files (eNum := {eN}) (eDen := {eD}) (by norm_num)")
    L.append(f"    check_{nameA} rfl rfl ?_ check_{nameB} rfl")
    L.append(f"    (by rw [crowd_{tag}_sideA, crowd_{tag}_sideB]) same_crowd_{tag} zones_crowd_{tag}")
    L.append(f"    (by norm_num) (by norm_num) ?_ ?_ ?_")
    L.append(f"  · rw [show Data.{nameA}.n = {nA} from rfl]")
    L.append("    norm_num")
    L.append(f"  · rw [crowd_{tag}_sideA]")
    L.append("    push_cast")
    L.append("    norm_num")
    L.append(f"  · rw [crowd_{tag}_sideA]")
    L.append("    push_cast")
    L.append("    norm_num")
    L.append(f"  · rw [crowd_{tag}_sideA]")
    L.append("    push_cast")
    L.append("    norm_num")
    L.append("")
    L.append("end S11")
    L.append("end PackingCert")
    out = OUTDIR / f"Check_{tag}.lean"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(f"build: python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Corpus.Crowd.Check_{tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
