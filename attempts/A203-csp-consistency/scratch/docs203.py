"""writes the A203 doc entries (notes s.8-10, registry row, LOG entry, residue ledger, budget item) -- run once."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
A = os.path.join(ROOT, "attempts", "A203-csp-consistency")
table = open(os.path.join(A, "results", "report203.md"), encoding="utf-8").read()

p = os.path.join(A, "notes", "csp_consistency.md")
s = open(p, encoding="utf-8").read()
i = s.index("## 8. Y0839 (both pads)")
s = s[:i] + """## 8. Y0839 (both pads)

The witness option of A202's count -- cell 10 serving BL(1,0) + BR(0,1) + BR(1,0), hull [2.190, 2.226] x
[0.698, 0.770], 11 pieces (all at tilt 62-71 deg: the only poses that reach BR(0,1)'s box) -- survives the
node-level rule S against 11 of H's 512 units (nearest at max centre distance 1.0025: two poses at tilt 64.01 in
opposite corners of the two pieces are separated along the common axis by 1.0005 -- but the option's corner pose
does not meet BR(0,1)); the SETTLE refines its 133 compatible leaf pairs, all die (R / X / S on the children), and
the row is DEAD by **F** (315 ms at g1) -- the coordinator's grid conclusion, reproduced in closed form.  The
singleton (10, BR(0,1)) dies the same way (15 pieces killed), and cell 7's BR(1,0) rows (330 pairs).  The mutual
clip kills 87 of H's 512 units (MC:BR(0,1)).  The count then finds another cover (cell 15 for the triple), and the
bar-H count forces H at BR(0,1) (A202 forced nothing).  Verdict ALIVE at both pads: **25 s / 22 s** (A202's
stage 0 is 16 s of it; the CSP: build 0.65 s, masks 2.6 s = 84,714 node tests + 1.86 M leaf pairs in numpy blocks,
settle 3.5 s at g1 / 1.9 s at pad 0; round 2 cached).  Audit by sampling (`logs/audit_Y0839_g1.log`): 0 refutations.

## 9. Y0191, Y0044, Y0054

* **Y0191** ALIVE both pads (14 s / 14 s): the mutual clip kills 416 of H's 512 units (MC:BL(1,0)) before A202's
  forced clip; 21 rows dead (cell 17's BR / TL rows by F, cells 10 / 12 by H); the count's TL(1,0) pair is now
  (8, 18) -- the PI's pair 14 | 18 is NOT excluded by rule S at piece resolution (656 x 282 pieces, hull max
  distance 1.53: the two rows' pieces are too coarse for the closed form; `logs/pair_y0191.log`), while the
  13 | 14 and 13 | 18 TL(1,0) pairs are.  Settling an option PAIR (the analogue of s.5 on both sides) is the
  closed-form next step; A201's exact test remains the fallback.
* **Y0044** ALIVE both pads (17 s / 17 s): H 512 -> 161 units (MC:BL(1,0)), cell 17's rows dead (H / F), H forced
  at BL(1,0) as in A202.
* **Y0054** ALIVE at g1 (33 s: H 512 -> 1 unit, cell 15's seven rows dead by H, H forced at BL(1,0)); DEAD at pad 0
  by A202's FC at BL(1,0) (H provably misses, CN cap 1: s0-only, WINDOW-PENDING).  The first run's g1 "kill" was
  the artefact of s.7 and is withdrawn.

## 10. The table over the 39 pages A202 left alive at stage 0 (both pads; `results/report203.md`)

Columns: A202's stage-0 / stage-1 verdicts; A203's verdict (seconds); H units built -> alive after the mutual clip;
dead rows by rule H / F; the mutual clip's unit kills per slot; the settle's per-rule kills; the CSP milliseconds
(build / masks / settle) of round 1; H forced.

""" + table + """
**Summary.**  78 (page, pad) runs, median 23 s, max 57 s (13 runs over 30 s: the settle's 6 s budget on pages with
many near pairs -- Y0325, Y0460, Y0865, Y0719 -- on top of A202's 17-28 s).  296 option rows dead (115 by H, 181 by
F), 4,606 H units killed by the mutual clip on every page, H forced on 34 of 78 pads (10 more than A202's stage 0:
Y0839 BR(0,1), Y0308 / Y0985 TR(0,0), Y1022 BR(1,0), Y0660 BL(1,0), Y0842 BR(0,1)).  Kills: **k5_16_interior_Y0842
at the g1 pad** (window-valid; A202 needed stage 1's exact table for it): round 1's F kills (cells 6 and 15) and
round 2's (cell 21, cell 15's BL / BR rows) leave BL(1,0) with a refined union of diameter 0.9495 < 1 (cap 1) and H
provably missing it -- Theorem FC; plus Y0054 at pad 0 (A202's).  Every other page ALIVE: the CSP's value on them is
the H clip (units -> alive), the dead rows and the forcings, all inputs to stage 1 / the trees.
"""
open(p, "w", encoding="utf-8").write(s)

p = os.path.join(ROOT, "attempts", "REGISTRY.md")
s = open(p, encoding="utf-8").read()
i = s.index("| A202-fast30 |")
j = s.index("\n", i) + 1
row = ("| A203-csp-consistency | Fable; <= 2 BelowNormal pythons at affinity 0xFFFF (two page shards), BLAS pinned, lab ceiling 12 excluding \"Claude Extensions\" counted before every launch, "
       "A202's stage-0 code COPIED at d13f7420 and modified only in the copy (A201 / A202 untouched), PYTHONDONTWRITEBYTECODE=1, git = pathspec commits after every page | "
       "the PI's readings (2026-09-10 18:20 on Y0839: clip H on the tight BR / TR meeter options and settle the mutual clip; 17:40 on Y0191: test a slot's meeter pair over MEETING pieces): make the fast count a small CSP on PIECES, closed form, inside 30 s | "
       "`code/csp203.py` rule S (Lemma PC: the separating-axis bound with the tilt bins on a piece pair, corners of the difference rect x 4-deg tilt sub-intervals; numpy blocks `satbatch203.py`), H units (H's pieces at depth 1) and option piece sets (the dyadic intersection over the row's slots, `csp203b.py`), "
       "Lemma HC (a row with no piece compatible with any alive H piece is dead), Lemma MC (an H unit compatible with no row of a slot a free square must meet is dead), the SETTLE refinement (near-dead rows' pairs split 2x2x2 x 3 levels under P/W/C/M/L/R/X + S, `csp203c.py`), Theorem COUNT-CSP (`count203.py`: the count ANDs the H-mask along the branch, pairs on piece trees); "
       "`fig203b.py` page with the CSP panel; `run203.py` / `run203.sh`; lemmas in `notes/csp_consistency.md`; status_gallery (7m) | done-mixed | "
       "**[M] 78 (page, pad) runs over the 39 pages A202 left alive at stage 0: median 23 s, max 57 s; 296 option rows dead (115 H / 181 F), 4,606 H units killed by the mutual clip, H forced on 34 pads (10 more than A202); Y0839's witness row (cell 10, BL+BR01+BR10) DEAD by F in 315 ms -- the coordinator's grid conclusion in closed form -- page ALIVE with H forced at BR(0,1); "
       "ONE new kill at the window pad, k5_16_interior_Y0842 (the F kills leave BL(1,0) a CN cap 1 with H provably missing: Theorem FC), plus Y0054 at pad 0 (A202's). [T] rule S fuzzed (0 refutations of 2,872 dead pairs), the kills audited by pose sampling; "
       "[!] one artefact caught by the audit before the population: a hull-only node walked as an internal node excluded every (free row, H row) pair vacuously -- Y0054 'died' at g1, refuted by a sampled disjoint pair, fixed, everything regenerated. "
       "What the closed form does not settle: an option PAIR at piece resolution (Y0191's 14 \\| 18 stays compatible) -- a pair settle is the next step; verdicts are [C: closed-form trace], no verifier clause | attempts/A203-csp-consistency |\n")
s = s[:j] + row + s[j:]
open(p, "w", encoding="utf-8").write(s)

entry = """
## 2026-09-10 evening -- A203-csp-consistency (Fable) -- done-mixed: **the fast count is a CSP on PIECES: H-consistency, the mutual clip and the settle kill Y0839's witness row in closed form (the coordinator's grid, reproduced), clip H on every page (4,606 units), force H on 10 more pads, and retire k5_16_interior_Y0842 at the window pad on their own; one artefact caught by the audit before shipping**

- **What it is** (`attempts/A203-csp-consistency`, the PI's readings of 18:20 on Y0839 -- "clipping H on both of those (and settling
  the mutual clip) should basically kill all the options there" -- and of 17:40 on Y0191 -- the meeter pair must be tested over
  MEETING pieces; the coordinator's grid check `y0839_csp_gridcheck.py`).  A202's stage 0 (copied at d13f7420, modified only in
  the copy) plus: **rule S** (Lemma PC: an interior-disjoint pair has an axis of one square with projection distance >= 1/2 +
  w(relative tilt)/2; on a piece pair the bound over the difference rect's corners and 4-degree tilt sub-intervals, numpy blocks);
  **Lemma HC** (a row with no piece compatible with any alive H piece is dead -- H exists); **Lemma MC** (an H unit compatible with
  no row of a slot a FREE square must meet is dead -- Corollary FC-count); the **SETTLE** (a near-dead row's compatible pairs split
  2x2x2 three levels under P/W/C/M/L/R/X + S); **Theorem COUNT-CSP** (the count ANDs the H-mask along the branch and needs
  piece-compatible chosen pairs).  Lemmas for any n in `notes/csp_consistency.md`; the page `docs/residue_map/csp203_<nid>.svg`
  = A202's panel + a CSP panel (H's units after the mutual clip, the dead rows lettered H / F, milliseconds per rule).
- **Y0839** (both pads, 25 s / 22 s): the count's witness row (cell 10 serving BL(1,0)+BR(0,1)+BR(1,0), 11 pieces at tilt 62-71
  deg) survives rule S at node level against 11 units (max distance 1.0025) and DIES by F after the settle (133 pairs, all dead,
  315 ms); the mutual clip kills 87 of H's 512 units; the count finds another cover (cell 15) and forces H at BR(0,1).  ALIVE.
- **Y0191** ALIVE (14 s): H 512 -> 96 units by MC:BL(1,0); 21 rows dead; the witness pair for TL(1,0) moves to (8, 18); the PI's
  pair 14 | 18 is NOT excluded at piece resolution (the closed form needs a pair settle; A201's exact test stays the fallback).
  **Y0044** ALIVE (17 s; H -> 161 units, forced at BL(1,0)).  **Y0054** ALIVE at g1 (33 s; H -> 1 unit), DEAD at pad 0 (A202's FC).
- **Population** (39 pages x 2 pads, two shards, 25 min): median 23 s, max 57 s; 296 rows dead (115 H / 181 F); H forced on 34
  pads (10 more than A202's stage 0); **kill: k5_16_interior_Y0842 at g1** (the F kills in cells 6 / 15 / 21 leave BL(1,0) a CN
  cap 1 with H provably missing -- Theorem FC; A202 needed stage 1 for it) and Y0054 at pad 0.  `results/csp203.jsonl`,
  `results/report203.md`, certs, pages; status_gallery block (7m), kills `[C: closed-form trace]` (no verifier clause yet).
- **Soundness**: rule S fuzzed (6,000 pairs, 2,872 dead, 0 refutations); tree compatibility vs brute force (3,000 cases); every
  kill audited by pose sampling (`scratch/audit203.py`).  **The audit caught an artefact**: a fixed role's row (a hull-only node)
  was walked as an internal node with no children, so every (free row, H row) pair surviving the hull test was excluded vacuously
  -- Y0054 "died" at g1; a sampled disjoint admissible pair F (1.504, 0.5, 0 deg) | H (1.949, 1.519, 82.4 deg) refuted it; fixed
  (hull-only nodes are leaf blocks), the population regenerated.  Kept rule: a closed-form kill of a page the exact tests leave
  alive is a bug until audited.
- Files: `code/csp203.py`, `satbatch203.py`, `csp203b.py`, `csp203c.py`, `count203.py`, `cert203.py`, `sweep203.py`, the copies
  `fast30.py` / `fast30b.py` / `rules202.py` / `fig203.py`, `fig203b.py`, `run203.py`, `run203.sh`, `report203.py`;
  `scratch/fuzz203.py`, `fuzz203b.py`, `audit203.py`, `pair_y0191.py`; `logs/`.
"""
open(os.path.join(ROOT, "LOG.md"), "a", encoding="utf-8").write(entry)

p = os.path.join(ROOT, "docs", "residue_ledger.md")
s = open(p, encoding="utf-8").read()
i = s.index("**[T]/[M] A202 (2026-09-10 evening)")
j = s.index("\n", i) + 1
par = ("\n**[T]/[M] A203 (2026-09-10 evening) — the fast count as a CSP on PIECES (`attempts/A203-csp-consistency`, `notes/csp_consistency.md`, pages `residue_map/csp203_<nid>.svg`).** "
       "The PI's readings on Y0839 (clip H on the tight BR / TR meeter options and settle the mutual clip) and Y0191 (a slot's meeter pair over MEETING pieces): rule S = the separating-axis bound with the tilt bins on a piece pair (Lemma PC), H-consistency (a row with no piece compatible with any alive H piece is dead), the mutual clip (an H unit compatible with no row of a slot a free square must meet is dead), the settle refinement of near-dead rows, and the count carrying the H-mask (a cover needs a COMMON H piece) with piece-compatible pairs. "
       "**[M]** On Y0839 the count's witness row (cell 10, BL+BR01+BR10) dies by the settle in 315 ms — the coordinator's grid conclusion (78 meeting poses, none disjoint from any H pose) in closed form — and H is forced at BR(0,1); over the 39 pages A202 left alive: median 23 s a pad, 296 rows dead, 4,606 H units clipped, H forced on 10 more pads, and **k5_16_interior_Y0842 retired at the window pad by stage 0 alone** (the F kills leave BL(1,0) a CN cap 1 with H provably missing). "
       "**[T]** rule S fuzzed (0 refutations), kills audited by pose sampling; the audit caught one artefact before it shipped (a hull-only node excluded every (free row, H row) pair vacuously — Y0054 'died' at g1, refuted, fixed). What the closed form does not settle: an option PAIR at piece resolution (Y0191's 14 | 18) — a pair settle is next; verdicts `[C: closed-form trace]`, no verifier clause.\n")
s = s[:j] + par + s[j:]
open(p, "w", encoding="utf-8").write(s)

p = os.path.join(ROOT, "docs", "budget.md")
s = open(p, encoding="utf-8").read()
i = s.index("14. **A closed-form geometric layer prices at 8")
j = s.index("\n", i) + 1
item = ("15. **The piece-level CSP adds ~5-10 s a pad to the closed-form layer and buys the H clip, ten more forcings and one window-pad kill in 39 pages (A203, 2026-09-10 evening).** "
        "Rule S in numpy blocks (1-3 M leaf pairs a page in 1-3 s), the H-mask and mutual clip in milliseconds, the settle up to 6 s: 78 (page, pad) runs at a median of **23 s** (max 57 s; 13 runs over the 30 s target, all settle-bound) against A202's 8-28 s. "
        "What it buys: Y0839's witness row dead in 315 ms where the coordinator's grid needed 2,975 x 78 pose pairs; H clipped on every page (4,606 units killed, down to 1-96 % of its units), H forced on 34 of 78 pads (A202: 24), 296 option rows dead; **k5_16_interior_Y0842 retired at the g1 pad in 27 s** where A202 needed stage 1's 99 s. "
        "What it does not buy: a verdict on the other 37 pages (their covers survive at piece resolution), the option-pair settle (Y0191's 14 | 18), and the sliver unions / K'-cascade / SEAL of stage 1. Price of the population: 25 min on two BelowNormal processes (~0.9 CPU-h).\n")
s = s[:j] + item + s[j:]
open(p, "w", encoding="utf-8").write(s)
print("docs written")
