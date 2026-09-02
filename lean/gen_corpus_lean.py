#!/usr/bin/env python3
r"""
gen_corpus_lean.py -- A78 T5 driver: emit the Lean replay modules for a whole
DONE certificate corpus.

For each certificate of a corpus it writes TWO modules (the per-certificate
module pair is the isolation unit -- re-running one certificate must never
re-evaluate any other):

  PackingCertMathlib/Corpus/<CORPUS>/Data_<name>.lean
        `namespace PackingCert.CaseI.Data / def <name> : CCertI := ...`
        (produced verbatim by `lean/gen_case_lean.py` at the depth recorded in
        the certificate's `.report.json`)

  PackingCertMathlib/Corpus/<CORPUS>/Check_<name>.lean
        `theorem check_<name> : checkCaseI Data.<name> = true := by native_decide`
        + `theorem <name>_side : caseSide Data.<name> = <s>`
        + `theorem <name>_kill ...`        (nofams = [], via `checkCaseI_kill`)
          or `theorem <name>_no_family ...` (nofams present, via
          `checkCaseI_no_family`), both in the CaseK506.lean pilot's style.

and per corpus one aggregate

  PackingCertMathlib/Corpus/<CORPUS>.lean
        imports every check module, states ONE corpus theorem
        `corpus_<CORPUS> : checkCaseI Data.a = true /\ ... := <check_a, ...>`

plus the roll-up `PackingCertMathlib/Corpus.lean` (all four aggregates).

D.TRAP shares its six certificates with C.K61: its aggregate imports the K61
check modules and re-uses the same `check_*` facts (NO second evaluation).

Usage:
    python lean/gen_corpus_lean.py all
    python lean/gen_corpus_lean.py K61 --only k5_06 k6_31
    python lean/gen_corpus_lean.py --manifest       # just print the build order
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEANDIR = REPO / "lean" / "PackingCertMathlib" / "PackingCertMathlib"
CORPUSDIR = LEANDIR / "Corpus"
GEN_CASE = REPO / "lean" / "gen_case_lean.py"

# ---------------------------------------------------------------- corpus table

K61_DIRS = {
    "A55/k3_ext": "attempts/A55-k4-sweep/k3_ext/certs",
    "A55": "attempts/A55-k4-sweep/certs",
    "A53": "attempts/A53-simple-strata/certs_wip",
    "A54": "attempts/A54-stragglers/certs",
}

TRAP_NAMES = ["k6_07", "k6_19", "k6_21", "k6_22", "k6_23", "k6_24"]


def k61_members() -> list[tuple[str, Path]]:
    cap = json.loads((REPO / "attempts/A55-k4-sweep/results/cap.json").read_text(encoding="utf-8"))
    out = []
    for e in cap["certified"]:
        out.append((e["name"], REPO / K61_DIRS[e["src"]] / (e["name"] + ".json")))
    assert len(out) == 61, f"cap.json certified has {len(out)} entries, expected 61"
    return out


def p1_members() -> list[tuple[str, Path]]:
    return [("m3_trump5_interior_NO",
             REPO / "attempts/A59-trump-residual/certs/m3_trump5_interior_NO.json")]


def thmu_members() -> list[tuple[str, Path]]:
    return [("u_reinsert_%02d" % i,
             REPO / ("attempts/A65-low-k-closure/certs/u_reinsert_%02d.json" % i))
            for i in range(11)]


CORPORA = {
    "K61": k61_members,
    "P1": p1_members,
    "THMU": thmu_members,
}
# D.TRAP is a *view* of K61 -- same six certificates, no second evaluation.
VIEWS = {"TRAP": ("K61", TRAP_NAMES)}

ORDER = ["K61", "TRAP", "P1", "THMU"]

DOC = {
    "K61": ("C.K61 -- the 61 pin-set kills of the A53/A54/A55 cap "
            "(`attempts/A55-k4-sweep/results/cap.json`, field `certified`), all at "
            "`s = 969271/250000`, all with empty `nofams` (kill form)."),
    "TRAP": ("D.TRAP -- the six k6 trapped classes "
             "{k6_07, k6_19, k6_21, k6_22, k6_23, k6_24}.  These are members of C.K61: "
             "this module re-uses the K61 `check_*` facts, it does NOT re-evaluate them."),
    "P1": ("D.P1 -- `attempts/A59-trump-residual/certs/m3_trump5_interior_NO.json`, "
           "the trump5 interior residual: 5 cores + 1 NO-family, budget 6 (B-NO form)."),
    "THMU": ("A.THMU -- the 11 Theorem-U re-insertion certificates "
             "`attempts/A65-low-k-closure/certs/u_reinsert_{00..10}.json` at "
             "`s = 3877083591023/1000000000000`: 10 cores, 1 NO-family, budget 1, 0 atoms "
             "(B-NO form)."),
}


def lean_name(name: str) -> str:
    return name.replace(".", "_").replace("-", "_")


def cert_info(path: Path) -> dict:
    c = json.loads(path.read_text(encoding="utf-8"))
    rp = path.with_name(path.stem + ".report.json")
    if not rp.exists():
        raise SystemExit(f"no report next to {path}")
    r = json.loads(rp.read_text(encoding="utf-8"))
    if r.get("result") != "PASS":
        raise SystemExit(f"report {rp} is {r.get('result')}, not PASS")
    h = c.get("hypotheses", {}) or {}
    st = r.get("stats", {}) or {}
    return dict(
        cert=path, report=rp, depth=int(r["depth"]),
        s=str(c["s"]), n=int(c.get("n", 11)),
        atoms=len(c.get("atoms", [])), cores=len(h.get("cores", [])),
        nofams=len(h.get("nofams", [])), budget=int(c.get("budget", 11)),
        py_time_s=float(r.get("time_s", 0.0)), boxes=int(st.get("boxes", 0)),
        max_depth=st.get("max_depth"),
    )


def s_lean(s: str) -> tuple[str, str, str]:
    """(numerator, denominator, Lean real literal) for the side."""
    q = Fraction(s)
    assert q.denominator != 1, "integer side unexpected"
    return (str(q.numerator), str(q.denominator),
            f"(({q.numerator} : \u211d) / {q.denominator})")


# ---------------------------------------------------------------- emitters

def emit_data(corpus: str, name: str, info: dict) -> Path:
    out = CORPUSDIR / corpus / ("Data_%s.lean" % lean_name(name))
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(GEN_CASE), str(info["cert"]),
           "--depth", str(info["depth"]), "--name", lean_name(name), "-o", str(out)]
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_case_lean failed for %s:\n%s\n%s" % (name, r.stdout, r.stderr))
    # gen_case_lean writes `import PackingCertMathlib.CaseChecker`; that is what we want.
    return out


def emit_check(corpus: str, name: str, info: dict) -> Path:
    ln = lean_name(name)
    num, den, slit = s_lean(info["s"])
    r = info["cores"]
    n = info["n"]
    mod = "PackingCertMathlib.Corpus.%s.Data_%s" % (corpus, ln)
    L = []
    L.append("import %s" % mod)
    L.append("import PackingCertMathlib.CaseBridge")
    L.append("")
    L.append("/-!")
    L.append("# `%s` replayed in Lean (A78 T5, corpus %s)" % (name, corpus))
    L.append("")
    L.append("Certificate `%s`" % info["cert"].relative_to(REPO).as_posix())
    L.append("(report `%s`: PASS, depth %d, %d boxes, %.3f s in Python)."
             % (info["report"].relative_to(REPO).as_posix(), info["depth"],
                info["boxes"], info["py_time_s"]))
    L.append("%d atoms, %d cores, %d NO-families, budget %d, n = %d, s = %s."
             % (info["atoms"], info["cores"], info["nofams"], info["budget"], n, info["s"]))
    L.append("")
    L.append("* `check_%s` -- the checker PASSes (`native_decide` evaluation);" % ln)
    if info["nofams"] == 0:
        L.append("* `%s_kill` -- no strict family of %d closed unit squares in `[0, %s]\u00b2`"
                 % (ln, n, info["s"]))
        L.append("  has designated owners containing the %d cores (`checkCaseI_kill`)." % r)
    else:
        L.append("* `%s_no_family` -- every strict family of %d closed unit squares in" % (ln, n))
        L.append("  `[0, %s]\u00b2` whose designated owners contain the %d cores has a"
                 % (info["s"], r))
        L.append("  non-owner that is `CaseExempt` (Lemma B-NO occupancy, `checkCaseI_no_family`).")
    L.append("-/")
    L.append("")
    L.append("namespace PackingCert")
    L.append("namespace S11")
    L.append("")
    L.append("open Set CaseI")
    L.append("")
    L.append("/-- The checker PASSes the `%s` certificate (native_decide evaluation). -/" % name)
    L.append("theorem check_%s : checkCaseI Data.%s = true := by" % (ln, ln))
    L.append("  native_decide")
    L.append("")
    L.append("theorem %s_side : caseSide Data.%s = %s / %s := by" % (ln, ln, num, den))
    L.append("  change ((%s : Int) : \u211d) / ((%s : Int) : \u211d) = %s / %s"
             % (num, den, num, den))
    L.append("  norm_num")
    L.append("")
    if info["nofams"] == 0:
        L.append("/-- **The `%s` pin-set kill, strict-family form**: no %d pairwise-disjoint"
                 % (name, n))
        L.append("closed unit squares in `[0, %s]\u00b2` can have designated members" % info["s"])
        L.append("containing the %d certificate cores. -/" % r)
        L.append("theorem %s_kill {Q : Fin %d \u2192 Set RP}" % (ln, n))
        L.append("    (hQ : IsStrictFamily %d %s Q)" % (n, slit))
        L.append("    (own : Fin %d \u2192 Fin %d)" % (r, n))
        L.append("    (hown : \u2200 j : Fin %d, coreSet (Data.%s.cores.get j) \u2286 Q (own j)) :"
                 % (r, ln))
        L.append("    False := by")
        L.append("  rw [\u2190 %s_side] at hQ" % ln)
        L.append("  exact checkCaseI_kill check_%s rfl hQ own hown" % ln)
    else:
        L.append("/-- **The `%s` kill, B-NO form**: every strict family of %d closed unit"
                 % (name, n))
        L.append("squares in `[0, %s]\u00b2` whose designated members contain the %d"
                 % (info["s"], r))
        L.append("certificate cores has a non-owner member inside the certificate's exempt set. -/")
        L.append("theorem %s_no_family {Q : Fin %d \u2192 Set RP}" % (ln, n))
        L.append("    (hQ : IsStrictFamily %d %s Q)" % (n, slit))
        L.append("    (own : Fin %d \u2192 Fin %d)" % (r, n))
        L.append("    (hown : \u2200 j : Fin %d, coreSet (Data.%s.cores.get j) \u2286 Q (own j)) :"
                 % (r, ln))
        L.append("    \u2203 i : Fin %d, (\u2200 j, own j \u2260 i) \u2227 CaseExempt Data.%s (Q i) := by"
                 % (n, ln))
        L.append("  rw [\u2190 %s_side] at hQ" % ln)
        L.append("  exact checkCaseI_no_family check_%s hQ own hown" % ln)
    L.append("")
    L.append("end S11")
    L.append("end PackingCert")
    out = CORPUSDIR / corpus / ("Check_%s.lean" % ln)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


def emit_aggregate(corpus: str, members: list[tuple[str, dict]], home: str) -> Path:
    """`home` is the corpus whose Corpus/<home>/ directory holds the check modules."""
    L = []
    for name, _ in members:
        L.append("import PackingCertMathlib.Corpus.%s.Check_%s" % (home, lean_name(name)))
    L.append("")
    L.append("/-!")
    L.append("# Corpus %s replayed in Lean (A78 T5)" % corpus)
    L.append("")
    L.append(DOC[corpus])
    L.append("")
    L.append("`corpus_%s` is the conjunction of the %d per-certificate `check_*` facts."
             % (corpus, len(members)))
    L.append("Each conjunct was evaluated ONCE, in its own module "
             "(`Corpus/%s/Check_<name>.lean`);" % home)
    L.append("this module only pairs the finished proofs -- it triggers no evaluation.")
    L.append("-/")
    L.append("")
    L.append("namespace PackingCert")
    L.append("namespace S11")
    L.append("")
    L.append("open CaseI")
    L.append("")
    L.append("/-- **Corpus %s**: `checkCaseI` PASSes on all %d certificates. -/"
             % (corpus, len(members)))
    L.append("theorem corpus_%s :" % corpus)
    for i, (name, _) in enumerate(members):
        tail = " \u2227" if i + 1 < len(members) else " :="
        L.append("    checkCaseI Data.%s = true%s" % (lean_name(name), tail))
    L.append("  \u27e8" + ", ".join("check_%s" % lean_name(nm) for nm, _ in members) + "\u27e9")
    L.append("")
    L.append("end S11")
    L.append("end PackingCert")
    out = CORPUSDIR.parent / "Corpus" / ("%s.lean" % corpus)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


def emit_root() -> Path:
    L = []
    for c in ORDER:
        L.append("import PackingCertMathlib.Corpus.%s" % c)
    L.append("")
    L.append("/-!")
    L.append("# A78 T5 -- the four DONE certificate corpora, replayed in Lean")
    L.append("")
    L.append("Root of the `PackingCertCorpus` lake library (a SECOND lean_lib, so the")
    L.append("default target / CI is unchanged).  Build it with")
    L.append("`python attempts/A78-lean-wave6/code/lakeb.py PackingCertCorpus`,")
    L.append("or a single certificate with")
    L.append("`... lakeb.py PackingCertMathlib.Corpus.K61.Check_k5_06`.")
    L.append("")
    L.append("* `corpus_K61` -- the 61 pin-set kills of the A53/A54/A55 cap (C.K61);")
    L.append("* `corpus_TRAP` -- the six trapped k6 classes (D.TRAP, a view of C.K61);")
    L.append("* `corpus_P1` -- the trump5 interior residual (D.P1);")
    L.append("* `corpus_THMU` -- the 11 Theorem-U re-insertion certificates (A.THMU).")
    L.append("-/")
    out = CORPUSDIR.parent / "Corpus.lean"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------- main

def build_manifest() -> dict:
    man = {}
    for c, fn in CORPORA.items():
        man[c] = [(nm, cert_info(p)) for nm, p in fn()]
    return man


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", nargs="?", default="all",
                    help="K61 | TRAP | P1 | THMU | all")
    ap.add_argument("--only", nargs="*", default=None, help="restrict to these certificate names")
    ap.add_argument("--manifest", action="store_true",
                    help="print the build order (cheapest first) as JSON and exit")
    a = ap.parse_args()

    man = build_manifest()

    if a.manifest:
        rows = []
        for c in ORDER:
            if c in VIEWS:
                continue
            for nm, info in man[c]:
                rows.append(dict(corpus=c, name=nm, atoms=info["atoms"], cores=info["cores"],
                                 nofams=info["nofams"], depth=info["depth"], boxes=info["boxes"],
                                 py_time_s=info["py_time_s"],
                                 cert=info["cert"].relative_to(REPO).as_posix(),
                                 module="PackingCertMathlib.Corpus.%s.Check_%s" % (c, lean_name(nm))))
        rows.sort(key=lambda r: (r["boxes"], r["atoms"]))
        print(json.dumps(rows, indent=1))
        return 0

    targets = [c for c in CORPORA] if a.corpus == "all" else [a.corpus]
    if a.corpus == "all":
        targets = [c for c in ORDER if c in CORPORA]
    written = []
    for c in targets:
        if c in VIEWS:
            raise SystemExit("%s is a view of %s; generate %s instead" % (c, VIEWS[c][0], VIEWS[c][0]))
        for nm, info in man[c]:
            if a.only and nm not in a.only:
                continue
            written.append(emit_data(c, nm, info))
            written.append(emit_check(c, nm, info))
        if not a.only:
            written.append(emit_aggregate(c, man[c], c))
    if a.corpus == "all" and not a.only:
        home, names = VIEWS["TRAP"]
        sub = [(nm, info) for nm, info in man[home] if nm in names]
        assert len(sub) == len(names), "TRAP members missing from K61"
        written.append(emit_aggregate("TRAP", sub, home))
        written.append(emit_root())
    for p in written:
        print("wrote", p.relative_to(REPO).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
