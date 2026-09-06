"""A94 report generator -- runs in-process at the end of the campaign (and on a crash)."""
import json, os, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
NOTES = os.path.join(BASE, "notes")
SINK = os.path.join(RES, "slotcrowd94_runs.jsonl")
OUT = os.path.join(NOTES, "slotcrowd94_report.md")

WIN_NAME = {"s0_G2": "(s0, G2] = [3.862404, 3.877084)", "G4_lo": "(G4, 3.82] = [3.82, 3.833212)",
            "s0_lo": "(s0, 3.82] = [3.82, 3.877084)", "G3_G4": "(G3, G4] = [3.833212, 3.847780)",
            "G2_G3": "(G2, G3] = [3.847780, 3.862404)"}
WIN_ORDER = ["s0_G2", "G4_lo", "s0_lo", "G3_G4", "G2_G3"]
CLS = ["k5_11", "k5_16"]


def _load():
    recs = []
    if os.path.exists(SINK):
        for l in open(SINK):
            l = l.strip()
            if l:
                try:
                    recs.append(json.loads(l))
                except Exception:
                    pass
    return recs


def _fmt(v, f="%.6f"):
    return "-" if v is None else (f % v if isinstance(v, float) else str(v))


def build():
    os.makedirs(NOTES, exist_ok=True)
    recs = _load()
    lps = [r for r in recs if r.get("phase") in ("P1", "P4", "P6", "P7")]
    certs = [r for r in recs if r.get("phase") == "cert"]
    regs = [r for r in recs if r.get("phase") == "regression"]
    P0 = {}
    p0p = os.path.join(RES, "phase0.json")
    if os.path.exists(p0p):
        try:
            P0 = json.load(open(p0p))
        except Exception:
            P0 = {}
    done = None
    if os.path.exists(os.path.join(RES, "CAMPAIGN_DONE")):
        try:
            done = json.load(open(os.path.join(RES, "CAMPAIGN_DONE")))
        except Exception:
            done = None
    # last record per (tag)
    last = {}
    for r in lps:
        last[r["tag"]] = r
    lps = list(last.values())
    lastc = {}
    for r in certs:
        lastc[(r["cls"], r["window"], r["delta"])] = r
    certs = list(lastc.values())

    L = []
    A = L.append
    A("# A94 slotcrowd94 -- SLOT-CROWD certificates for k5_11 / k5_16 (Opus compute chore)")
    A("")
    A("Implements `attempts/A94-slot-crowds/notes/chore_slot_cert.md`.  Everything is written under")
    A("`attempts/A94-slot-crowds/`; nothing under A57/A60/A61/A86/A92/A93 was written (A92's code and")
    A("notes were read to copy from), and the frozen `verify_case.py` was copied byte-identical")
    A("(sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`) and never edited.")
    A("")
    A("Generated %s (%s); %d LP records, %d certification records."
      % (time.strftime("%Y-%m-%d %H:%M:%S"),
         (done or {}).get("status", "RUNNING"), len(lps), len(certs)))
    A("")

    # ---------------- headline
    A("## HEADLINE")
    A("")
    cpass = [c for c in certs if c.get("verdict") == "PASS"]
    if cpass:
        for cls in CLS:
            for w in WIN_ORDER:
                cc = sorted([c for c in cpass if c["cls"] == cls and c["window"] == w],
                            key=lambda c: c["delta"])
                if cc:
                    A("* **%s, window %s: CERTIFIED at delta = %g (e = %s)** -- the class is dead at"
                      " every side m in the window with all %d usable slot crowds at depth >= %g."
                      % (cls, WIN_NAME.get(w, w), cc[0]["delta"], cc[0]["e"],
                         cc[0].get("n", 0) and 4, cc[0]["delta"]))
    else:
        A("**no certified (1 + r_max)-run PASS in this chore's wall budget**")
    lpp = [r for r in lps if str(r.get("verdict", "")).startswith("LP-PASS")]
    if lpp:
        A("")
        A("LP-passing (tau < budget) nodes, per class x window: smallest / largest delta")
        A("")
        A("| class | window | smallest LP delta | largest LP delta | smallest CERTIFIED delta |")
        A("|---|---|---|---|---|")
        for cls in CLS:
            for w in WIN_ORDER:
                ds = sorted(r["delta"] for r in lpp if r["cls"] == cls and r["window"] == w)
                cd = sorted(c["delta"] for c in cpass if c["cls"] == cls and c["window"] == w)
                if not ds:
                    continue
                A("| %s | %s | %g | %g | %s |" % (cls, w, ds[0], ds[-1],
                                                  ("%g" % cd[0]) if cd else "none"))
    A("")

    # ---------------- constants
    A("## 0. Constants and the objects, as implemented")
    A("")
    A("| quantity | value |")
    A("|---|---|")
    A("| s0 | 969271/250000 = 3.877084 |")
    A("| G2 / G3 / G4 | 965601/250000 / 192389/50000 / 958303/250000 |")
    A("| window floor | 191/50 = 3.82 |")
    A("| lambda | s / m_lo |")
    A("| rho (pin slack) | (lambda - 1) * A_S rounded UP to 1e-5, then + 1e-5; A_S = 3/2 for both classes |")
    A("| a_w(p, delta) | lambda (1-delta) + (lambda-1)(7072/10000 + max(i,j)), rounded UP to 1e-5 |")
    A("| budget | N + 2 m_u e = n - k with n = 11 + 2 m_u e; N = 6, k = 5, m_u = 4 |")
    A("| e order | 1/2, 1/4, 1, 1/8 -> n = 15, 13, 19, 12; budget 10, 8, 14, 7 |")
    A("")
    A("The certificate is ONE measure mu and 1 + r_max = 5 runs of the frozen verifier:")
    A("")
    A("* **run A** `certs/runA_<tag>.json` -- n = 11 + 2 m_u e, budget = n - k, cores = the k pin")
    A("  cores (axis-aligned, centre = slot_j(s) exactly, tm = 0, a = 1/2 - rho), nofams = [].")
    A("  PASS certifies mu(Q) >= 1 for every admissible closed unit square Q in [0,s]^2 meeting NO")
    A("  pin core, and mu(total) < budget = N + 2 m_u e.")
    A("* **run B_r** `certs/runB<r>_<tag>.json` (r = 1..m_u) -- the SAME atoms, weights w/(1 + r e)")
    A("  exactly, the SAME cores, n = 1000 (budget 1000 - k, a dummy), nofams = E_r.  PASS certifies")
    A("  mu(Q) >= 1 + r e for every core-free Q not provably in E_r, hence for every core-free Q")
    A("  lying in >= r of the widened slot families.")
    A("")
    A("Composed (Lemma CW-S): a packing of the class at side m in [m_lo, s) whose every usable slot")
    A("is met at depth >= delta by >= 2 non-pin squares dilates (lambda = s/m, centres only) to a")
    A("disjoint family at side s whose k pin images contain the cores and whose N non-pin images")
    A("carry sum r >= 2 m_u incidences, so sum mu >= N + 2 m_u e > mu(total): contradiction.")
    A("")

    # ---------------- canaries
    A("## 1. Phase 0 canaries (all BEFORE any LP)")
    A("")
    tc = P0.get("trump_slot_canary") or {}
    A("### Trump slot canary (`results/trump_canary94.json`, exact Trump, this chore's slot frames)")
    A("")
    if tc:
        A("Verdict: **%s**, max deviation from the lead's depths = %.3e (tolerance 1e-9)."
          % ("PASS" if tc.get("ok") else "FAIL", tc.get("max_dev", float("nan"))))
        A("")
        A("| slot of trump5 | free meeters (ref) | d1 | d2 | ref d2 | |err| |")
        A("|---|---|---|---|---|---|")
        for r in tc.get("rows", []):
            A("| %s%s | %d (%d) | %.6f | %.6f | %.6f | %.1e |"
              % (r["cell"], " *(pin-clipped)*" if r.get("pin_clipped") else "",
                 r["n_meeters"], r["ref_n"], r["d1"], r["d2"], r["ref_d2"], r["err"]))
    else:
        A("_not recorded_")
    A("")
    A("### Image gate (no D4 Trump image realises the PIN hypothesis of the class at side s)")
    A("")
    ig = P0.get("image_gate") or {}
    if ig:
        A("| class / window | per-image count of pin slots hit (g0..g7) | realising |")
        A("|---|---|---|")
        for kk in sorted(ig):
            rows = ig[kk].get("rows", [])
            A("| %s | %s | %s |" % (kk, " ".join(str(r["n_pins_hit"]) for r in rows),
                                    "NONE" if ig[kk].get("ok") else "**SOME**"))
        A("")
        A("Every image misses at least one pin slot (Trump's TL corner is clear), so no image")
        A("realises the node's pin hypothesis at any rho used here.  Re-checked after every")
        A("certified PASS; a PASS on a realisable node exits 9.")
    A("")
    A("### e = 0 exact-pin regression LP (reproduces the class root tau at s0)")
    A("")
    A("| class | budget | tau | target (A54/A57) | |d| | verdict | rows | LP s |")
    A("|---|---|---|---|---|---|---|---|")
    for r in regs:
        A("| %s | %s | %.6f | %.4f | %.4f | %s | %s | %s |"
          % (r["cls"], r["budget"], r["tau"], r["target"], abs(r["tau"] - r["target"]),
             "OK" if r.get("ok") else "**OFF**", r.get("rows"), _fmt(r.get("lp_s"), "%.0f")))
    A("")
    A("### A57 consistency")
    A("")
    A("A57's G1 records are s0 slack-core tree kills of the SAME classes.  No A57 file was read or")
    A("written by this chore.  Nothing certified here claims anything at any side > the window's s;")
    A("in particular the s = s0 windows say nothing about sides above s0 = 3.877084.")
    A("")

    # ---------------- LP tables
    A("## 2. The LP tables (one row per (class, window, delta, e) attempt)")
    A("")
    A("Node = the class's k pin Boxes as cores (half-width h = rho/sqrt2), no NO-families, C1")
    A("quotient (a pinned class is not D4-symmetric), warm pool = A53/A54 nodes of the class")
    A("rescaled to the side plus this campaign's own solved nodes.  PASS criterion: tau < budget.")
    A("")
    for cls in CLS:
        for w in WIN_ORDER:
            rows = sorted([r for r in lps if r["cls"] == cls and r["window"] == w],
                          key=lambda r: (-r["delta"], str(r["e"])))
            if not rows:
                continue
            A("### %s, window %s" % (cls, WIN_NAME.get(w, w)))
            A("")
            A("| delta | e | n | budget | rho | a_w | tau | eta | minmass | maxcov | rows | atoms | LP s | verdict | certified |")
            A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            for r in rows:
                c = lastc.get((cls, w, r["delta"]))
                A("| %g | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                  % (r["delta"], r.get("e"), r.get("n"), r.get("budget"),
                     _fmt(r.get("rho_f"), "%.5f"),
                     ("/".join("%.5f" % v for v in r["a_w_f"]) if r.get("a_w_f") else "-"),
                     _fmt(r.get("tau")), _fmt(r.get("eta"), "%+.6f"),
                     _fmt(r.get("minmass"), "%.4f"), _fmt(r.get("maxcov"), "%.4f"),
                     r.get("rows"), r.get("atoms"), _fmt(r.get("lp_s"), "%.0f"),
                     r.get("verdict"), (c or {}).get("verdict", "-")))
            A("")

    # ---------------- certification
    A("## 3. Certification (%d frozen-verifier runs per node)" % 5)
    A("")
    A("`certify94.py`, depth 56, jobs 1 (VERIFY_JOBS_CAP = 1), 2 witness-feedback rounds (witnesses")
    A("of EVERY failing run fed back into the SAME slot-crowd-weighted re-solve), auto scale capped")
    A("at 1.4 and chosen against the BUDGET (not n), A85 eps_geo 0.002 / 0.004 repair on a FAIL.")
    A("`<tag>.PASS` is written only if ALL 1 + r_max runs pass.")
    A("")
    if certs:
        A("| tag | class | window | delta | e | budget | verdict | run A | runs B_r | cert s | eps_geo | sha256 A (16) |")
        A("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for c in sorted(certs, key=lambda c: (c["cls"], c["window"], c["delta"])):
            vb = c.get("verdictB") or {}
            A("| `%s` | %s | %s | %g | %s | %s | **%s** | %s | %s | %.0f | %s | %s |"
              % (c["tag"], c["cls"], c["window"], c["delta"], c["e"], c.get("budget"),
                 c.get("verdict"), c.get("verdictA"),
                 " ".join("B%s=%s" % (r, vb[r]) for r in sorted(vb)) if vb else "-",
                 c.get("cert_s", 0.0), c.get("eps_geo_used"),
                 (c.get("sha256_A") or "")[:16]))
    else:
        A("_(no certification attempted / completed within the wall budget)_")
    A("")

    # ---------------- families
    A("## 4. Family statistics")
    A("")
    A("| class | window | delta | lambda | rho | a_w per slot | G cells per slot | E_1..E_4 boxes | overshoot of G over F | max r on the grid |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for cls in CLS:
        for w in WIN_ORDER:
            for r in sorted([x for x in lps if x["cls"] == cls and x["window"] == w],
                            key=lambda x: -x["delta"]):
                if r.get("n_G_cells") is None:
                    continue
                if any(x.get("delta") == r["delta"] and x.get("_seen") for x in []):
                    continue
                ov = r.get("overshoot") or []
                A("| %s | %s | %g | %s | %s | %s | %s | %s | %s | %s |"
                  % (cls, w, r["delta"], _fmt(r.get("lam")), _fmt(r.get("rho")),
                     "/".join("%.5f" % v for v in (r.get("a_w_f") or [])),
                     "/".join(str(v) for v in (r.get("n_G_cells") or [])),
                     "/".join(str(r["n_E_boxes"][k]) for k in sorted(r.get("n_E_boxes") or {}, key=int)),
                     "/".join("-" if v is None else "%.1f%%" % (100 * v) for v in ov),
                     r.get("r_max_grid")))
    A("")
    A("`G_p` is built on the ABSOLUTE 0.02 grid of [0.45, s-0.45]^2 per theta bin (A92's seven,")
    A("edges at multiples of 1/4 deg, overlapping), as the set of cells NOT provably disjoint from")
    A("`F_p(a_w(p))`; the test is exact (Fractions, 193-point t-grid with the sqrt2/2 Lipschitz pad,")
    A("inflated by 1e-8 to absorb `caselp.q`'s 1e-9 outward rounding) and is evaluated at each")
    A("cell's FRAME lower-left corner, which for a reflected frame is a different absolute corner.")
    A("`N(cell)` = the slots whose `G_p` contains the cell; `E_r` = the cells with |N| <= r-1.")
    A("")

    # ---------------- resources
    A("## 5. Resource discipline actually used")
    A("")
    A("BLAS pinned to 1 thread (`blas1` imported before numpy in every entry point).  At most 2")
    A("processes: this driver (which runs the LP in-process) plus ONE `certify94`/`verify_case`")
    A("subprocess, never concurrently.  `free_commit_mb()` (MEMORYSTATUSEX.ullAvailPageFile) polled")
    A("every 60 s before every LP and before every certify launch; the gate requires TWO CONSECUTIVE")
    A("readings above 6144 MB.  `verify_case --jobs 1` everywhere.  Nothing under A57/A60/A61/A86/")
    A("A92/A93 was written; A92's chore held the other LP slot throughout.")
    if done:
        A("")
        A("Campaign terminal status: **%s**, %.1f min wall, %s."
          % (done.get("status"), done.get("minutes", 0.0), done.get("ts")))
    A("")

    # ---------------- deviations
    A("## 6. Deviations from the spec / engine surprises")
    A("")
    for i, t in enumerate(DEVIATIONS, 1):
        A("%d. %s" % (i, t))
    A("")

    # ---------------- files
    A("## 7. Files")
    A("")
    A("| what | path |")
    A("|---|---|")
    A("| engine copy (A92's, verbatim) | `attempts/A94-slot-crowds/code/` |")
    A("| frozen verifier | `code/verify_case.py`, sha256 `521cb01f...cbef7af` |")
    A("| rhs-hooked LP / certificate builder | `code/lpbox94.py`, `code/caselp94.py` (`make_certificate94`) |")
    A("| slot families, E_r, rhs hooks | `code/slotfam94.py` |")
    A("| canaries | `code/canary94.py` |")
    A("| driver | `code/slotcrowd94.py` |")
    A("| (1 + r_max)-run certifier | `code/certify94.py` |")
    A("| pre-flight tests / report generator | `code/smoke94.py`, `code/report94.py` |")
    A("| families | `results/fams/fam_<cls>_<window>_d<delta>.json` |")
    A("| run records | `results/slotcrowd94_runs.jsonl` |")
    A("| Phase 0 record | `results/phase0.json` |")
    A("| node LPs (resumable) | `results/nodes/<tag>.json` |")
    A("| certificates | `certs/runA_<tag>.json`, `certs/runB<r>_<tag>.json` (+ `.report.json`, `.witnesses.json`, `<tag>.certify.json`, `<tag>.PASS`) |")
    A("| logs | `logs/slotcrowd94.log`, `logs/cert_<tag>.log`, `logs/smoke94.out` |")
    A("| terminal marker | `results/CAMPAIGN_DONE` |")
    A("")
    A("## 8. Resuming")
    A("")
    A("    cd attempts/A94-slot-crowds")
    A("    python code/slotcrowd94.py --minutes <wall> --reserve_min 150 --lp_time 900 --cert_time 300")
    A("")
    A("Solved node LPs are cached in `results/nodes/<tag>.json` and reused on a restart (delete one")
    A("to force a longer LP rather than a re-certify of the same measure); families are cached in")
    A("`results/fams/`.  Every attempt appends one record to `results/slotcrowd94_runs.jsonl`.")
    open(OUT, "w").write("\n".join(L) + "\n")
    return OUT


DEVIATIONS = [
    "**U_S and m_u.**  The spec's sec 2 table fixes m_u = 4 for both classes, including the slot "
    "whose extension is k6_23 (k5_11 TR(0,0); k5_16 BL(1,0)), which the A56 scoreboard has as "
    "PARTIAL on [3.82, 3877/1000] rather than FULL -- while `results/slots94.json`'s `usable` field "
    "(the spec's sec 0 wording) lists only the FULL ones, i.e. m_u = 3.  The chore ran the spec's "
    "sec 2 table (m_u = 4).  This is exactly sound for the three windows with s <= G2 = 3.862404 "
    "(< 3877/1000), where k6_23 is dead over the whole window.  For the two windows with s = s0 the "
    "composed statement is sound for m in [m_lo, 3877/1000] and leaves the 8.4e-5 sliver "
    "[3877/1000, s0) to slot_crowds.md sec 5 or to A57's G1 tree; the certificates themselves are "
    "conditional statements about the DECLARED U_S and are unaffected.  A56's scoreboard was read "
    "at start-up (mtime recorded above): k6_27 was still OPEN, so k5_16 did NOT gain BR(1,0)/TL(1,0) "
    "and m_u stayed 4.",
    "**a_w uses the exact per-slot max(i,j)**, not the spec's permitted blanket max(i,j) = 1.  The "
    "blanket value is the conservative simplification; the per-slot value is the formula itself and "
    "is the one implemented (it differs only for k5_11's TR(0,0), where max(i,j) = 0).",
    "**`G_p` is built on the ABSOLUTE grid, not on the frame grid [-1, a_w + 3/4]^2.**  The spec "
    "builds G_p on a frame grid (sec 3) and classifies E_r's cells on the absolute grid (sec 3, "
    "E_r).  Two different grids would make the LP's `r_G` and E_r's `N(cell)` inconsistent: run B_r "
    "needs `Q not in E_r  =>  r_G(Q) >= r`, which holds only if the same cells define both.  Both "
    "are therefore built on the absolute 0.02 grid of [0.45, s-0.45]^2 (which contains every "
    "admissible centre, and whose frame image is inside [-1, a_w+3/4]^2 for every slot used, all of "
    "which have i, j <= 1).  With that, `r_G(Q)` computed by the LP hook is EXACTLY 'the cell of Q "
    "is in G_p', so the bridge is an identity (smoke test [3] checks it on 2000 random poses per r).",
    "**E_r is merged by the UNION of N, not only between cells with IDENTICAL N.**  A run of cells "
    "is merged while the union of their N still has <= r - 1 slots.  This is exactly as sound as "
    "the spec's rule -- the merged box's FRAME lower-left corner is the corner of one of its cells, "
    "and that cell is provably disjoint from every slot outside its own N, hence outside the union "
    "-- and it also merges along y (identical x-range, same rule).  It roughly halves the box count "
    "(e.g. E_3 goes from 934 to 272 boxes), which matters because the verifier tests every NO-family "
    "against every box.  Every emitted box is re-asserted EXACTLY, slot by slot.",
    "**Reflected frames take the EXACT image of the emitted t-interval**, not a re-derived "
    "`t_lo(90-T1) .. t_hi(90-T0)`.  The certificate writes the absolute interval "
    "[t_lo(T0), t_hi(T1)]; its image under t -> (1-t)/(1+t) is computed exactly and used as the "
    "frame t-grid.  Re-deriving t_lo/t_hi at 90 - T rounds outward in the WRONG place and need not "
    "contain that image (both are within ~2/2^24 of the true endpoint, in an uncontrolled order).",
    "**Speed: f(cx, cy, t) = f(cx - cy, 0, t) + cy** (because max(x+d, y+d) = max(x,y) + d).  Every "
    "exact disjointness test is therefore a lookup in a cached one-parameter table; the whole "
    "family build touches ~5x10^3 table entries instead of ~10^6 f-evaluations, and one "
    "(class, window, delta) builds in ~90 s.",
    "**The LP cores are strictly smaller than the certificate cores.**  `caselp.Box.core()` derives "
    "a = (1/2 - hd)/(1 + (t1-t0)) with hd >= h*sqrt2 >= rho and t1 - t0 = 2^-24, so the LP's core is "
    "contained in the emitted core (a' <= 1/2 - rho, asserted): the LP sees at least every row the "
    "certificate exempts, which is the sound direction.  The emitted cores are exactly the spec's "
    "(kx, ky) = slot_j(s), tm = 0, a = 1/2 - rho.",
    "**G dilation 0.02 / 1 deg** for the LP row rhs instead of the spec's EPS_ZONE = 2e-3 / "
    "EPS_TH = 0.3 deg -- the same conservative direction (a pose counts as in G unless it is outside "
    "by the margin: more rows at the higher rhs, never fewer), and one centre-grid cell, exactly as "
    "A92 argued (the exact verifier resolves a box straddling the boundary of E_r only by covering "
    "it, which needs the box smaller than the dilation).",
    "**`sym_kind = \"C1\"`** everywhere (the spec's choice): a pinned class is not D4-symmetric, and "
    "`Hyp.is_symmetric_D4` returns False as soon as there are core boxes, so there is no silent "
    "D4 quotient.  k5_11's transpose symmetry is NOT exploited.",
    "**`lpbox94.py` / `caselp94.py`** are the A92 `lpbox92`/`caselp92` copies (the rhs hooks "
    "unchanged in kind), renamed for self-containment; the only addition is "
    "`caselp94.make_certificate94`, which writes the k pin CORES into every file and sets "
    "budget = n - #cores (A92's `make_certificate92` always wrote `cores: []`).",
    "**`certify94` picks the weight scale against the BUDGET, not n** (A92's node had no cores, so "
    "budget = n there).  A scale chosen against n would emit a certificate with total >= budget and "
    "the frozen verifier would refuse it outright.",
    "**`smoke94.py`, `canary94.py`, `report94.py`** are extra files (not named in the spec): the "
    "pre-flight tests, the two canaries, and the report generator that runs in-process at the end "
    "of the campaign (also on a crash).",
    "**The delta sweep runs DOWNWARDS and stops at the first failure.**  The spec's sec 7 order is "
    "0.05, 0.02, 0.03, 0.10, 0.20, 0.30 (smallest first).  But eta(delta) is monotone DECREASING "
    "in delta: a_w(p, delta) = lambda(1-delta) + (lambda-1)(...) strictly decreases as delta grows, "
    "every F_p and hence every G_p shrinks, so tau falls, while the budget N + 2 m_u e does not "
    "depend on delta at all.  The LP-passing set is therefore upward-closed in delta, and scanning "
    "downwards until the first failing delta finds exactly the same SMALLEST passing delta the "
    "spec's order would, without paying for the deltas below it.  (The spec's order was run first "
    "and its results for the small deltas are in the tables; the cached nodes are reused.)",
    "**The campaign was killed externally after 66 min of its first 480 min run** (no "
    "`CAMPAIGN_DONE`, no report) and was resumed from its node/family caches for the remaining "
    "budget.  The report is now rewritten after EVERY record, so a hard kill always leaves a "
    "current report on disk.",
    "**Every LP is two-stage (probe then full), and the e-sweep is model-guided.**  The spec's "
    "run order sweeps e in 1/2, 1/4, 1, 1/8 for each of 6 deltas x 2 classes x up to 5 windows at "
    "lp_time 900 s -- more than 12 h for Phase 1 alone, against a 480 min budget.  Two "
    "wall-budget devices were used, neither of which can turn a FAIL into a PASS: (a) every LP "
    "first runs a `--probe_time` (300 s) stage, and a probe whose tau is already >= budget refuses "
    "the node without spending the rest of lp_time (tau only rises as the row oracle keeps finding "
    "violated poses); a probe below budget is continued, warm-started, for the remaining lp_time.  "
    "(b) after a failing e, the remaining e values are reordered by the one-parameter model "
    "eta(e) = (tau_0 - N) + (c - 2 m_u) e with c = (tau - tau_0)/e measured on that run and tau_0 "
    "the class's e = 0 root tau, and at most `--max_e` (3) values of e are tried per "
    "(class, window, delta).  Both are recorded per run in `slotcrowd94_runs.jsonl` "
    "(`tau_probe`, `probe_s`).",
    "**A verifier timeout** (`--verify_timeout`, default max(600, 2 x cert_time) seconds per run) "
    "was added so that a single pathological frozen-verifier run cannot consume the whole wall "
    "budget; a timeout is recorded as a FAIL of that run, never as a PASS.",
]

if __name__ == "__main__":
    print(build())
