#!/usr/bin/env python3
"""
gen_tube_lean.py -- convert the contraction-tube certificates (certs/tube_*.json,
format `contraction-tube-certificate-v1`) into Lean 4 data + replay modules for the
`PackingCert.Rigid.checkTube` kernel
(lean/PackingCertMathlib/PackingCertMathlib/RigidTubeKernel.lean).

Emits
  (a) lean/PackingCertMathlib/PackingCertMathlib/RigidTubeData.lean
        namespace PackingCert.Rigid.Data -- `tube_<ident>_v`, `tube_<ident>_omega`,
        `tube_<ident> : TubeCert` for each certificate, then `tubeAll` (all of them)
        and `tubeLoadBearing` (the three load-bearing ones);
  (b) lean/PackingCertMathlib/PackingCertMathlib/Corpus/Tube/Check_<ident>.lean
        one `native_decide` replay per certificate (lake library `PackingCertCorpus`,
        NOT the default target) + the aggregator Corpus/Tube.lean;
  (c) lean/PackingCertMathlib/PackingCertMathlib/RigidTubeCheck.lean
        the DEFAULT-target isolated `native_decide` module with the three
        load-bearing replays (Measure382Check / RigidityCheck pattern).

All rationals in the inputs are exact strings "num/den"; floats (T_float, ...) are
IGNORED and never emitted.  Rational literal convention matches
lean/gen_rigidity_lean.py's rat_lean.

Usage:
    python lean/gen_tube_lean.py [--certdir DIR] [--outdir DIR] [--manifest PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DEF_CERTDIR = REPO / "certs"
DEF_LEANROOT = REPO / "lean" / "PackingCertMathlib" / "PackingCertMathlib"
DEF_MANIFEST = REPO / "attempts" / "A86-lean-wave7" / "results" / "tube_order.json"

NV = 34
NROWS70 = 70

# The three load-bearing certificates (A86 T1): trump5 slot direction, k4_08 landing,
# and the pure scale ray (k0_00).
LOAD_BEARING = [
    "tube_slot_T4.5e-2_landing.json",
    "tube_k4_08_landing_T28o625_rc1o625_rt21o10000.json",
    "tube_I_none_landing_T1279o10000_rc1o625_rt21o10000.json",
]

# Theorem names in RigidTubeCheck.lean, in the same order.
LOAD_BEARING_THM = ["checkTube_slot_landing", "checkTube_k4_08_landing",
                    "checkTube_scale_landing"]


# ---------------------------------------------------------------- rationals

def to_frac(v) -> Fraction:
    if isinstance(v, bool):
        raise ValueError("boolean is not a number")
    if isinstance(v, float):
        raise ValueError(f"float {v!r} in certificate: refuse (not exact)")
    if isinstance(v, int):
        return Fraction(v)
    if isinstance(v, str):
        return Fraction(v.strip())
    raise ValueError(f"cannot parse rational from {v!r}")


def rat_lean(q: Fraction) -> str:
    if q.denominator == 1:
        return f"({q.numerator} : Rat)"
    return f"(({q.numerator} : Rat) / {q.denominator})"


def nat_lean(v) -> str:
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"expected int, got {v!r}")
    if v < 0:
        raise ValueError(f"expected non-negative int, got {v}")
    return str(v)


def arr(items) -> str:
    return "#[" + ", ".join(items) + "]"


def arr_lines(items, indent: str) -> str:
    """One element per line, for the long arrays."""
    if not items:
        return "#[]"
    inner = (",\n" + indent + "  ").join(items)
    return "#[\n" + indent + "  " + inner + "\n" + indent + "]"


def lean_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------- identifiers

def ident_of(fname: str) -> str:
    """`certs/tube_<X>.json` -> Lean identifier stem `<X>` sanitised.

    Every character outside [A-Za-z0-9_] (the '.' of `T4.5e-2`, the '-' of the
    exponent) becomes '_'; the 'o' of `T28o625` is already a legal letter and is
    kept as it stands.  The mapping is injective over the 54 certificates (checked).
    """
    if not (fname.startswith("tube_") and fname.endswith(".json")):
        raise ValueError(f"not a tube certificate file name: {fname!r}")
    stem = fname[len("tube_"):-len(".json")]
    ident = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ident):
        raise ValueError(f"{fname}: does not yield a Lean identifier ({ident})")
    return ident


# ---------------------------------------------------------------- reading

def read_cert(p: Path) -> dict:
    d = json.loads(p.read_text(encoding="utf-8"))
    if d.get("format") != "contraction-tube-certificate-v1":
        raise ValueError(f"{p.name}: unexpected format {d.get('format')!r}")
    v = [to_frac(x) for x in d["direction_v"]]
    omega = [to_frac(x) for x in d["omega_rational"]]
    P = [nat_lean(x) for x in d["P"]]
    strict = [nat_lean(x) for x in d["strictly_compressed_rows"]]
    if len(v) != NV:
        raise ValueError(f"{p.name}: direction_v has {len(v)} entries, expected {NV}")
    if len(omega) != NROWS70:
        raise ValueError(f"{p.name}: omega has {len(omega)}, expected {NROWS70}")
    if len(P) != NV:
        raise ValueError(f"{p.name}: P has {len(P)}, expected {NV}")
    return {
        "file": p.name,
        "name": d["name"],
        "ident": ident_of(p.name),
        "T": to_frac(d["T"]),
        "rC": to_frac(d["r_c"]),
        "rT": to_frac(d["r_theta"]),
        "rS": to_frac(d["r_s"]),
        "v": v, "omega": omega, "P": P, "strict": strict,
    }


# ---------------------------------------------------------------- (a) data module

def gen_data(certs: list[dict]) -> str:
    L = []
    L.append("import PackingCertMathlib.RigidTubeKernel")
    L.append("")
    L.append(f"/-! GENERATED by lean/gen_tube_lean.py from certs/tube_*.json "
             f"({len(certs)} contraction-tube certificates,")
    L.append("format `contraction-tube-certificate-v1`) — do not edit.")
    L.append("")
    L.append("The float fields of the JSON (`T_float`, ...) are informational and are NOT")
    L.append("emitted: every number below is the exact rational of the certificate. -/")
    L.append("")
    L.append("namespace PackingCert.Rigid.Data")
    L.append("")
    # One top-level def per large array (a single record literal exceeds the
    # elaborator's recursion depth).
    L.append("set_option maxRecDepth 8000")
    L.append("")
    for c in certs:
        i = c["ident"]
        L.append(f"def tube_{i}_v : Array Rat := "
                 + arr_lines([rat_lean(q) for q in c["v"]], ""))
        L.append("")
        L.append(f"def tube_{i}_omega : Array Rat := "
                 + arr_lines([rat_lean(q) for q in c["omega"]], ""))
        L.append("")
        L.append(f"def tube_{i} : TubeCert := {{")
        L.append("  name := " + lean_str(c["name"]) + ",")
        L.append("  T := " + rat_lean(c["T"]) + ",")
        L.append("  rC := " + rat_lean(c["rC"]) + ",")
        L.append("  rT := " + rat_lean(c["rT"]) + ",")
        L.append("  rS := " + rat_lean(c["rS"]) + ",")
        L.append(f"  v := tube_{i}_v,")
        L.append(f"  omega := tube_{i}_omega,")
        L.append("  P := " + arr(c["P"]) + ",")
        L.append("  strictRows := " + arr(c["strict"]))
        L.append("}")
        L.append("")
    L.append("/-- All " + str(len(certs)) + " contraction-tube certificates. -/")
    L.append("def tubeAll : Array TubeCert := "
             + arr_lines([f"tube_{c['ident']}" for c in certs], ""))
    L.append("")
    lb = [c for c in certs if c["file"] in LOAD_BEARING]
    lb.sort(key=lambda c: LOAD_BEARING.index(c["file"]))
    L.append("/-- The three load-bearing tubes: the trump5 slot direction, the `k4_08`")
    L.append("landing tube and the pure scale ray (`k0_00`). -/")
    L.append("def tubeLoadBearing : Array TubeCert := "
             + arr_lines([f"tube_{c['ident']}" for c in lb], ""))
    L.append("")
    L.append("end PackingCert.Rigid.Data")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- (b) corpus

def gen_check(c: dict) -> str:
    i = c["ident"]
    L = []
    L.append("import PackingCertMathlib.RigidTubeData")
    L.append("import PackingCertMathlib.RigidData22")
    L.append("")
    L.append(f"/-!")
    L.append(f"# `{c['name']}` replayed in Lean (A86 T1, corpus Tube)")
    L.append("")
    L.append(f"Certificate `certs/{c['file']}`:")
    L.append(f"`T = {c['T']}`, `r_c = {c['rC']}`, `r_θ = {c['rT']}`, `r_s = {c['rS']}`.")
    L.append("")
    L.append(f"`check_tube_{i}` — `checkTube` accepts it against A22's Krawczyk")
    L.append("certificate (`native_decide` evaluation).")
    L.append("-/")
    L.append("")
    L.append("namespace PackingCert.Rigid")
    L.append("")
    L.append(f"theorem check_tube_{i} : checkTube Data.a22 Data.tube_{i} = true := by")
    L.append("  native_decide")
    L.append("")
    L.append("end PackingCert.Rigid")
    L.append("")
    return "\n".join(L)


def gen_tube_root(certs: list[dict]) -> str:
    L = []
    for c in certs:
        L.append(f"import PackingCertMathlib.Corpus.Tube.Check_{c['ident']}")
    L.append("")
    L.append("/-!")
    L.append(f"# A86 T1 — the {len(certs)} contraction-tube certificates, replayed in Lean")
    L.append("")
    L.append("Part of the `PackingCertCorpus` lake library (a SECOND lean_lib, so the")
    L.append("default target / CI is unchanged).  Build one certificate with")
    L.append("`python attempts/A78-lean-wave6/code/lakeb.py "
             "PackingCertMathlib.Corpus.Tube.Check_regress_a36`.")
    L.append("")
    L.append("The three load-bearing tubes are ALSO replayed in the default target")
    L.append("(`PackingCertMathlib.RigidTubeCheck`).")
    L.append("-/")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- (c) default target

def gen_tubecheck(certs: list[dict]) -> str:
    lb = [c for c in certs if c["file"] in LOAD_BEARING]
    lb.sort(key=lambda c: LOAD_BEARING.index(c["file"]))
    if len(lb) != 3:
        raise ValueError(f"expected 3 load-bearing certificates, found {len(lb)}")
    L = []
    L.append("import PackingCertMathlib.RigidTubeData")
    L.append("import PackingCertMathlib.RigidData22")
    L.append("")
    L.append("/-!")
    L.append("# The contraction-tube replays (A86 T1) — ISOLATED `native_decide` module")
    L.append("")
    L.append("Kept in its own module (the `Measure382Check` / `RigidityCheck` pattern) so")
    L.append("that the evaluation axiom enters exactly here and every other module of the")
    L.append("default target is cache-hit-only.  The three LOAD-BEARING tubes only; the")
    L.append("remaining certificates are replayed one module each in the separate")
    L.append("`PackingCertCorpus` library (`PackingCertMathlib.Corpus.Tube`).")
    L.append("")
    for c, thm in zip(lb, LOAD_BEARING_THM):
        L.append(f"* `{thm}` — `certs/{c['file']}` (`T = {c['T']}`);")
    L.append("-/")
    L.append("")
    L.append("namespace PackingCert.Rigid")
    L.append("")
    L.append("open PackingCert.Rigid.Data")
    L.append("")
    for c, thm in zip(lb, LOAD_BEARING_THM):
        L.append(f"theorem {thm} : checkTube a22 tube_{c['ident']} = true := by native_decide")
        L.append("")
    L.append("end PackingCert.Rigid")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- sanity

def reparse_data(text: str, n: int) -> dict:
    blocks = {}
    for blk in text.split("\ndef ")[1:]:
        name = blk.split(" ", 1)[0]
        blocks[name] = blk
    certdefs = re.findall(r"def (tube_\w+) : TubeCert := \{(.*?)\n\}", text, re.S)
    v_w, o_w, P_w = set(), set(), set()
    names = []
    for nm, body in certdefs:
        names.append(nm)
        v_w.add(len(re.findall(r": Rat\)", blocks[nm + "_v"])))
        o_w.add(len(re.findall(r": Rat\)", blocks[nm + "_omega"])))
        P_w.add(len([x for x in re.search(r"  P := #\[(.*?)\]", body).group(1).split(",")
                     if x.strip()]))
    allseg = re.search(r"def tubeAll : Array TubeCert := #\[\n(.*?)\n\]", text, re.S).group(1)
    # the `name := "slot_T4.5e-2_landing"` string literals legitimately carry dots:
    # strip every string literal before looking for float literals.
    nostr = re.sub(r'"[^"\n]*"', '""', text)
    lbseg = re.search(r"def tubeLoadBearing : Array TubeCert := #\[\n(.*?)\n\]",
                      text, re.S).group(1)
    return {"certs": len(certdefs), "names": names,
            "v_widths": sorted(v_w), "omega_widths": sorted(o_w), "P_widths": sorted(P_w),
            "tubeAll": len([x for x in allseg.split(",") if x.strip()]),
            "tubeLoadBearing": len([x for x in lbseg.split(",") if x.strip()]),
            "floats": len(re.findall(r"\d\.\d", nostr))}


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--certdir", default=str(DEF_CERTDIR))
    ap.add_argument("--leanroot", default=str(DEF_LEANROOT))
    ap.add_argument("--manifest", default=str(DEF_MANIFEST))
    a = ap.parse_args()

    certdir, leanroot = Path(a.certdir), Path(a.leanroot)
    files = sorted(certdir.glob("tube_*.json"))
    if not files:
        raise SystemExit(f"no tube_*.json under {certdir}")
    certs = [read_cert(p) for p in files]

    idents = [c["ident"] for c in certs]
    if len(set(idents)) != len(idents):
        dup = sorted({i for i in idents if idents.count(i) > 1})
        raise SystemExit(f"identifier collision: {dup}")

    out_data = leanroot / "RigidTubeData.lean"
    out_check = leanroot / "RigidTubeCheck.lean"
    corpusdir = leanroot / "Corpus" / "Tube"
    out_root = leanroot / "Corpus" / "Tube.lean"

    corpusdir.mkdir(parents=True, exist_ok=True)
    out_data.write_text(gen_data(certs), encoding="utf-8")
    out_check.write_text(gen_tubecheck(certs), encoding="utf-8")
    out_root.write_text(gen_tube_root(certs), encoding="utf-8")
    for c in certs:
        (corpusdir / f"Check_{c['ident']}.lean").write_text(gen_check(c), encoding="utf-8")

    # build order: increasing T (the regression T = 0 first)
    order = sorted(certs, key=lambda c: (c["T"], c["ident"]))
    man = [{"cert": c["file"], "ident": c["ident"], "name": c["name"],
            "module": f"PackingCertMathlib.Corpus.Tube.Check_{c['ident']}",
            "T": str(c["T"]), "r_c": str(c["rC"]), "r_theta": str(c["rT"]),
            "r_s": str(c["rS"]),
            "load_bearing": c["file"] in LOAD_BEARING} for c in order]
    manp = Path(a.manifest)
    manp.parent.mkdir(parents=True, exist_ok=True)
    manp.write_text(json.dumps(man, indent=1), encoding="utf-8")

    # sanity: re-parse what we just wrote from disk
    r = reparse_data(out_data.read_text(encoding="utf-8"), len(certs))
    ok = True

    def chk(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print(f"  FAIL: {msg}")

    chk(r["certs"] == 54, f"TubeCert defs = {r['certs']} != 54")
    chk(r["tubeAll"] == 54, f"tubeAll = {r['tubeAll']} != 54")
    chk(r["tubeLoadBearing"] == 3, f"tubeLoadBearing = {r['tubeLoadBearing']} != 3")
    chk(r["v_widths"] == [34], f"v widths = {r['v_widths']} != [34]")
    chk(r["omega_widths"] == [70], f"omega widths = {r['omega_widths']} != [70]")
    chk(r["P_widths"] == [34], f"P widths = {r['P_widths']} != [34]")
    chk(r["floats"] == 0, "float literal in RigidTubeData.lean")
    chk(r["names"] == [f"tube_{i}" for i in idents],
        "TubeCert def order does not match the certificate order")
    ctext = out_check.read_text(encoding="utf-8")
    thms = re.findall(r"^theorem (\w+) : checkTube a22 (\w+) = true := by native_decide$",
                      ctext, re.M)
    chk([t[0] for t in thms] == LOAD_BEARING_THM,
        f"RigidTubeCheck.lean replays {[t[0] for t in thms]} != {LOAD_BEARING_THM}")
    # the doc block names the source JSON files (which carry dots); the STATEMENTS
    # must be float-free.
    chk(len(re.findall(r"\d\.\d", "\n".join(t[1] for t in thms))) == 0,
        "float literal in a RigidTubeCheck.lean statement")
    nmods = len(list(corpusdir.glob("Check_*.lean")))
    chk(nmods == 54, f"{nmods} Check modules != 54")
    rt = out_root.read_text(encoding="utf-8")
    chk(len(re.findall(r"^import ", rt, re.M)) == 54,
        "Corpus/Tube.lean does not import 54 modules")

    print(f"{out_data}  ({out_data.stat().st_size} bytes)")
    print(f"  certs={r['certs']} tubeAll={r['tubeAll']} loadBearing={r['tubeLoadBearing']} "
          f"v={r['v_widths']} omega={r['omega_widths']} P={r['P_widths']} "
          f"floats={r['floats']}")
    print(f"{out_check}  ({out_check.stat().st_size} bytes)")
    print(f"{out_root}   ({nmods} Check modules under {corpusdir})")
    print(f"{manp}  (build order, increasing T)")
    for c in certs:
        print(f"    tube_{c['ident']:<42} <- {c['file']:<52} T={str(c['T']):<12} "
              f"strict={len(c['strict'])}")
    print("SANITY: " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
