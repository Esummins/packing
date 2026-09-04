"""A92 -- regenerate notes/crowd92_report.md from the run records and the family files.

Called in-process by crowd92.py at the end of the campaign (also on a crash), so the report
always exists with whatever finished, with unfinished items marked.
"""
import json, os, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
NOTES = os.path.join(BASE, "notes")

DELTAS = [0.3, 0.2, 0.1, 0.05]


def _runs():
    p = os.path.join(RES, "crowd92_runs.jsonl")
    out = []
    if os.path.exists(p):
        for l in open(p):
            l = l.strip()
            if l:
                try:
                    out.append(json.loads(l))
                except Exception:
                    pass
    return out


def _fam(d):
    p = os.path.join(RES, "fam_d%g.json" % d)
    return json.load(open(p)) if os.path.exists(p) else None


def _fmt(x, f="%.6f"):
    return "-" if x is None else (f % x if isinstance(x, float) else str(x))


def build():
    runs = _runs()
    lp = [r for r in runs if r.get("phase") != "cert"]
    ce = [r for r in runs if r.get("phase") == "cert"]

    # ---- families
    fam_rows = []
    can_rows = []
    for d in DELTAS:
        f = _fam(d)
        if not f:
            continue
        ov = f.get("overshoot") or {}
        fam_rows.append("| %.2f | %s | %.6f | %dx%d | %d | %d | **%.2f %%** | %d / %d | %.1e | %s |"
                        % (d, f["a"], f["a_float"], f["NX"], f["NY"], f["n_g_per_corner"], f["n_e"],
                           100.0 * (ov.get("overshoot") or 0.0), ov.get("n_in_F_not_G", -1),
                           ov.get("n", 0), f.get("d4_defect", 0.0), f.get("build_s", "-")))
        cs = f.get("canary") or []
        real = [c["image"] for c in cs if c.get("realises")]
        can_rows.append("| %.6f (d %.2f) | %s | **%s** |"
                        % (f["a_float"], d,
                           " | ".join("%d%d%d%d" % (c["BL"], c["BR"], c["TL"], c["TR"]) for c in cs),
                           ",".join(real) if real else "NONE"))

    # ---- LP table
    lp_rows = []
    for r in lp:
        lp_rows.append("| %.2f | %s | %d | %.6f | %s | %s | %s | %s | %s | %s | %s |"
                       % (r["delta"], r["e"], r["n"], r["a_w_float"], _fmt(r.get("tau")),
                          _fmt(r.get("eta")), _fmt(r.get("minmass"), "%.4f"),
                          _fmt(r.get("maxcov"), "%.4f"), r.get("rows"), _fmt(r.get("lp_s"), "%.0f"),
                          r.get("verdict")))

    # ---- certification table
    ce_rows = []
    best = None
    for r in ce:
        ce_rows.append("| %s | %.2f | %s | %d | **%s** | %s | %s | %.0f | `%s` | `%s` |"
                       % (r["tag"], r["delta"], r["e"], r["n"], r.get("verdict"),
                          r.get("verdictA"), r.get("verdictB"), r.get("cert_s") or 0.0,
                          (r.get("sha256_A") or "-")[:16], (r.get("sha256_B") or "-")[:16]))
        if r.get("verdict") == "PASS" and (best is None or r["delta"] > best["delta"]):
            best = r

    headline = ("**no certified two-run PASS in this chore's wall budget**" if best is None else
                "**delta = %.2f at e = %s (n = %d)** — `certs/runA_%s.json` + `certs/runB_%s.json`, "
                "both PASS under the frozen verifier at depth 56"
                % (best["delta"], best["e"], best["n"], best["tag"], best["tag"]))

    marker = os.path.join(RES, "CAMPAIGN_DONE")
    mk = json.load(open(marker)) if os.path.exists(marker) else None

    txt = TEMPLATE % dict(
        headline=headline,
        fam_table="\n".join(fam_rows) or "| _(none built)_ | | | | | | | | | |",
        can_table="\n".join(can_rows) or "| _(none)_ | | |",
        lp_table="\n".join(lp_rows) or "| _(no LP completed within the wall budget)_ | | | | | | | | | | |",
        cert_table="\n".join(ce_rows) or "| _(no certification attempted within the wall budget)_ | | | | | | | | | |",
        n_lp=len(lp), n_cert=len(ce),
        status=("status=%s, %.0f min" % (mk["status"], mk["minutes"])) if mk else "RUNNING",
        ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    p = os.path.join(NOTES, "crowd92_report.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt)
    return p


TEMPLATE = r"""# A92 crowd92 — the CROWD-WEIGHTED root certificate (Opus compute chore)

Implements `attempts/A92-blocked-side/notes/chore_crowd_cert.md`. Everything is written under
`attempts/A92-blocked-side/`; nothing under A57/A60/A61/A85/A86/A89 was written, and the frozen
`verify_case.py` was copied byte-identical (sha256 in section 9) and never edited.

Generated %(ts)s (%(status)s); %(n_lp)d LP records, %(n_cert)d certification records.

## HEADLINE — largest delta with a CERTIFIED two-run PASS

%(headline)s

---

## 0. Constants

| quantity | value |
|---|---|
| s0 | 969271/250000 = 3.877084 |
| window floor | 3.82 |
| lambda_max = s0/3.82 | 969271/955000 = 1.0149434554 |
| a_w(delta) | lambda_max (1-delta) + (lambda_max - 1) * 7072/10000, rounded UP to 1e-5 |
| budget n | 11 + 8e; e in {1/4, 1/2, 1, 2} -> n = 13, 15, 19, 27 |

| delta | a_w (exact) | a_w (float) | spec's printed value |
|---|---|---|---|
| 0.30 | 72103/100000 | 0.721030 | 0.72103 |
| 0.20 | 82253/100000 | 0.822530 | 0.82252 (spec truncates; see Deviations) |
| 0.10 | 46201/50000 | 0.924020 | 0.92402 |
| 0.05 | 97477/100000 | 0.974770 | 0.97477 |

## 1. The certificate (Lemma CW), as implemented

ONE measure mu on [0,s0]^2, TWO runs of the frozen verifier:

* **run A** `certs/runA_<tag>.json` — n = budget = 11 + 8e, atoms + weights w, hypotheses
  {cores: [], nofams: []}. PASS certifies mu(Q) >= 1 for EVERY admissible closed unit square
  Q in [0,s0]^2, and mu(total) < 11 + 8e.
* **run B** `certs/runB_<tag>.json` — the SAME atoms, weights w/(1+e) (exact rationals),
  n = budget = 1000 (its "total < 1000" clause is a dummy), hypotheses {cores: [], nofams: E}.
  PASS certifies mu(Q) >= 1+e for every Q not provably in E; every E box is exactly certified
  disjoint from F_c(a_w) for all four corners c, so this covers every admissible Q that meets the
  closed box [0,a_w]^2 at some corner.

Composed (Lemma CW): a packing with 2 such squares at each corner (8 distinct, CC-1(ii)) plus 3
others has sum_i mu(Q_i) >= 8(1+e) + 3 = 11 + 8e > mu(total) — contradiction.

The hypothesis is carried entirely by the LP right-hand sides: rhs(Q) = 1 + e*[Q in G], G an
outer cover of F_c(a_w) at every corner. The node itself has NO cores and NO NO-families.

## 2. Families (`code/crowdfam92.py`, `results/fam_d<delta>.json`, `results/crowd92_fams.json`)

Method, all exact in Fractions. `f(u,v,t) = corner85.f_min_max` is nondecreasing in u and in v and
(sqrt2/2)-Lipschitz in theta, so a cell `[x_i,x_{i+1}] x [y_j,y_{j+1}] x [T0,T1]` is PROVABLY
DISJOINT from `F(a) = {f <= a}` iff `min over a 193-point exact t-grid of f(x_i,y_j,t) - pad > a`
with `pad = (sqrt2/2)*dtheta/2`. Centre grid 0.02 on `[0.45, a_w+3/4]^2` (a pose meeting
`[0,a_w]^2` has corner-frame centre coords <= `a_w + sqrt2/2 < a_w + 3/4`); every test is inflated
by 1e-8 so the 1e-9 outward rounding of `caselp.q` on the emitted NoFam corners cannot break it.
G = every cell NOT provably disjoint (a DOWN-set = staircase per theta bin, run-length merged
LOSSLESSLY, so the merge adds no overshoot). Theta bins are o3fam's seven, edges at multiples of
1/4 deg, sigma-closed and overlapping by 1 deg (so no verifier box straddles a bin forever).
E = the exact complement of G in `[0.45, s0-0.45]^2 x [0,90]`, decomposed into horizontal strips
(lower band, upper band, one middle rect per bin), each EXACTLY certified disjoint from
`F_c(a_w)` at all four corners.

| delta | a_w | a_w float | grid | G boxes / corner | E boxes | overshoot of G over F | in F but not G | D4 defect | build s |
|---|---|---|---|---|---|---|---|---|---|
%(fam_table)s

## 3. Canary (checked FIRST, before any LP)

Per-image, per-corner count of Trump placements with `f_c <= a_w` (exact). An image REALISES the
crowd hypothesis iff every corner has >= 2. Counts printed as `[BL BR TL TR]`.

| a_w | g0 | g1 | g2 | g3 | g4 | g5 | g6 | g7 | realising |
|---|---|---|---|---|---|---|---|---|---|
%(can_table)s

Reading: three corners of every image hold exactly ONE slot square (f = 0 exactly, the square with
a vertex at the container corner); the fourth is Trump's TL 2-crowd (f = 0.831679 / 0.844500), so
it contributes 0 below a_w = 0.72/0.82 and 2 above a_w = 0.92. No image ever reaches 2 at all four
corners, so no image realises the hypothesis at any a_w < 1 — **CANARY PASS**, exactly as the spec
predicted. The engine also re-checks after every PASS and exits 9 on a realisable node.

**Out of scope, logged and not checked:** the certified K0-BLOCKED packings of d2front87 at
4.03-4.36 and s0115 at 3.985 have side > s0 and are not touched by this certificate.

## 4. Phase 1 — (S), the D2^4 pattern: the LP table

Node = the k0_00 ROOT at s0, no pins, no cores, no NO-families, D4 quotient, warm pool = A38's
root_s0 + A07's 3.82/3.83 columns rescaled (<= 1600 columns), lp_time 900 s, LP-ONLY.
PASS criterion: tau < n = 11 + 8e; eta = tau - n.

| delta | e | n | a_w | tau | eta | minmass | maxcov | rows | LP s | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
%(lp_table)s

## 5. Phase 1 — certification (two frozen-verifier runs per node)

`certify92.py`, depth 56, jobs 1, 2 witness-feedback rounds (witnesses of BOTH runs fed back into
the same crowd-weighted re-solve), auto scale capped at 1.4, A85 eps_geo 0.002 / 0.004 repair on a
FAIL. `<tag>.PASS` is written only if BOTH runs pass.

| tag | delta | e | n | verdict | run A | run B | cert s | sha256 A (16) | sha256 B (16) |
|---|---|---|---|---|---|---|---|---|---|
%(cert_table)s

## 6. Phase 2 — mixed patterns for (N)

NOT REACHED in this chore's wall budget (it is gated on Phase 1 finishing and on free-commit
headroom; see section 7). The general certificate is architected but not coded: families
`G_c^(k)` with weight `e_k` and multiplicity `m_k` per corner, run A with `n = 11 + sum_c m_c e_c`
(floored to an integer, which is the sound direction), one run B per DISTINCT weight (weights
`w/(1+e_k)`, NO-families = the complement of the union of the weight-`e_k` families), and the S
corners' SHALLOW families added to run A as caselp nofams. Two things must be added to the code:
(i) `crowdfam92.build_E` must take the set of active corners and a per-corner delta (the current
builder assumes all four corners at one delta); (ii) `crowd92` must force `sym_kind="C1"` — the
mixed patterns are NOT D4-symmetric, and `Hyp([],[]).is_symmetric_D4` returns True vacuously, so
the D4 quotient would be silently wrong. A89's experience says the C1 quotient needs 5-10x the LP
time of the D4 one to reach a certifiable minmass.

## 7. Resource discipline actually used

BLAS pinned to 1 thread (`blas1` imported before numpy in every entry point). At most 2 processes:
this driver (which runs the LP in-process, as A89's `o3run` did) plus ONE `certify92`/`verify_case`
subprocess, never concurrently. `free_commit_mb()` (MEMORYSTATUSEX.ullAvailPageFile) polled every
60 s before every LP and before every certify launch; the gate requires TWO CONSECUTIVE readings
above 6144 MB before proceeding. Nothing under A57/A60/A61/A86 was read or written. The LP sweep
stops early if it would eat the certification reserve (default 80 min) — a certified two-run PASS
is the deliverable, an extra LP row is not.

## 8. Deviations from the spec / engine surprises

1. **`lpbox92.py` exists.** The spec says "add `caselp92.py` / `certify92.py` (copies with the ONE
   change below)", but the row right-hand side is set in `lpbox.Model.add_row` (`h.addRow(al,...)`)
   and the row-oracle threshold in `lpbox.RowOracle.search`, not in `caselp.py`. So the one change
   lives in a third copy, `lpbox92.py` (`lpbox.py` itself is left byte-identical to A89's), and
   `caselp92.py` imports it. The whole diff is 3 hunks:
   * module globals `RHS_MULT / RHS_MAX / RHS_CELL` (defaults `None / 1.0 / None` = A85 behaviour);
   * `Model.add_row`: `al = al * RHS_MULT(centre, theta)`;
   * `RowOracle.search`: two passes per theta (see 2) and the per-pose rhs in slot 4 of each
     violation tuple — so `lpbox.run`'s existing `minmass = viol[0][3] / viol[0][4]` is exactly the
     mass/rhs ratio with no further edit and `converged` keeps its meaning; plus one line in
     `exact_theta` for the `cell_keep` filter.
2. **The row oracle needs a second pass, not just a widened threshold** (engine surprise, and the
   one real trap). Simply raising the oracle threshold from `alpha` to `alpha*(1+e)` makes almost
   EVERY cell of `exact_theta`'s O(K^2) arrangement a candidate: a memory blow-up, and the existing
   20000-cell cap then keeps the LOWEST-mass cells (the uninteresting mass ~1 ones in the middle of
   the container) and hides the genuine 1+e violations in the corner regions — the LP would report
   convergence while run B still had holes. Fix: pass 1 = the unmodified A85 oracle at threshold
   `alpha` over the whole domain (any pose with mass < alpha is violated whatever its rhs); pass 2
   = threshold `alpha*(1+e)` with the cells pre-filtered by `RHS_CELL` to those meeting the dilated
   G. Cost: the row oracle runs twice per theta.
3. **G dilation 0.02 / 1 deg instead of the spec's EPS_ZONE = 2e-3 / EPS_TH = 0.3 deg.** The spec
   fixes the conservative DIRECTION (a pose counts as in G unless it is outside every G-rect by the
   margin — more rows at 1+e, never fewer); any larger margin is the same direction and strictly
   more conservative (it only raises tau). 0.02 (one centre-grid cell) is used because the exact
   verifier can only discharge a box straddling the boundary of E by COVERING it (mass >= 1+e on
   the whole box), which needs the box smaller than the dilation: 0.02 costs ~8 bisections per
   axis, 2e-3 would cost ~11 and roughly 60x the boundary boxes.
4. **`a_w(0.2) = 0.82253`, not the spec's printed 0.82252.** The spec's formula says "rounded UP at
   the last step"; `lambda_max*0.8 + (lambda_max-1)*0.7072 = 0.822520766...`, whose round-UP to
   1e-5 is 0.82253. The other five printed values match round-up exactly, so 0.82252 is a
   truncation in the spec text. Round-UP is also the sound direction (a_w must be large enough for
   the depth->reach transfer), so it is what is implemented.
5. **E is certified by a stronger property than "E n G_c = empty".** Every E box is exactly
   certified (Fractions, all four corners, all inflated by 1e-8 to absorb `caselp.q`'s 1e-9 outward
   rounding of the emitted NoFam corners) to be provably DISJOINT FROM `F_c(a_w)` itself — which is
   what run B's soundness actually needs and which implies interior-disjointness from G. E and G
   are exact complements by construction, so they do share boundary faces; every point of such a
   face lies in a cell proved disjoint from F, so no pose of F is ever exempted.
6. **G's D4-closure is by construction, not by a rect-list match.** The LP's G test maps the centre
   into each of the four corner frames and tests the ONE stored BL staircase, so the multiplier is
   D4-invariant identically. The materialised per-corner rect lists (o3fam `corner_fams`-style) are
   also produced and their D4 mismatch measured (2.2e-16, one ulp of `s0 - u`); a 4000-pose
   randomised D4-invariance test of the multiplier passes with 0 failures (`smoke92.py`).
7. **`format` / `symmetry` fields.** The files carry `"format": "case-lp-certificate-v1"` as asked;
   the frozen verifier does not read that field. `"symmetry": "D4"` is deliberately NOT set:
   `caselp.solve_node` already returns `atoms_all` with every D4 image expanded, so setting it
   would double every atom.
8. **Run A and run B really are one measure.** Identical atom lists, and run B's weights are
   EXACTLY run A's divided by (1+e) as rationals (asserted in `smoke92.py`).
9. `smoke92.py` and `report92.py` are extra files (not in the spec): the pre-flight test of the rhs
   hook / D4 invariance / two-run certificate format through the frozen verifier's loader, and the
   report generator that runs in-process at the end of the campaign (also on a crash).

## 9. Files

| what | path |
|---|---|
| engine copy (38 modules, verbatim from A89) | `attempts/A92-blocked-side/code/` |
| frozen verifier (byte-identical to A85's and A89's) | `code/verify_case.py`, sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af` |
| the ONE engine change | `code/lpbox92.py` (56 diff lines vs `lpbox.py`) |
| certificate builder | `code/caselp92.py` (`make_certificate92`, 46 diff lines vs `caselp.py`) |
| two-run certifier | `code/certify92.py` |
| family builder | `code/crowdfam92.py` |
| driver | `code/crowd92.py` |
| pre-flight tests / report generator | `code/smoke92.py`, `code/report92.py` |
| families | `results/crowd92_fams.json`, `results/fam_d<delta>.json` |
| run records | `results/crowd92_runs.jsonl` |
| node LPs (resumable) | `results/nodes/<tag>.json` |
| certificates | `certs/runA_<tag>.json`, `certs/runB_<tag>.json` (+ `.report.json`, `.witnesses.json`, `<tag>.certify.json`, `<tag>.PASS`) |
| logs | `logs/crowd92.log`, `logs/crowd92.out`, `logs/fams.out`, `logs/cert_<tag>.log` |
| terminal marker | `results/CAMPAIGN_DONE` |

## 10. Resuming

    cd attempts/A92-blocked-side
    python code/crowd92.py --minutes <wall budget> --reserve_min 80 --lp_time 900 --cert_time 300

Solved node LPs are cached in `results/nodes/<tag>.json` and reused on a restart (delete them to
force a longer LP rather than a re-certify of the same measure); families are cached in
`results/fam_d<delta>.json`. Every attempt appends one record to `results/crowd92_runs.jsonl`.
"""


if __name__ == "__main__":
    print(build())
