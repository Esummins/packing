# A163 — method

Owner A163 (Opus engineer), 2026-09-08.

## 0. What "another frame" means, precisely

A local certificate (Theorem LOCAL, `docs/proofs/local_certificate.md` §3) is a statement about a
**hypothesis on poses**:

> `s ∈ [3.82, s0]`; for each **pin** `p` a square with tilt 0 and centre inside
> `(α_p + β_p s) + [−δ/√2, δ/√2]²`; for each `l ∈ L` a **distinct other** square with centre in `l`'s
> box and tilt (mod 90°) in `l`'s interval ⇒ **no such configuration is a packing at side ≤ s0.**

The *boxes* are absolute geometry. The *pins* are the class's five near-simple slot squares — that is
the **frame**, and it is the only thing that differs between k5_11, k5_16 and trump5. A node of class
`C` has `C`'s five pins fixed by construction, so **only a certificate whose `P` is `C`'s pin set can
kill it**. That is the entire content of this attempt: A160's 53 certified box sets are geometrically
right for k5_16's and trump5's S02 nodes and logically useless to them, because their `P` is k5_11's.

The three frames (`results/frames163.json`, `code/frames163.py`; pin sets are `a116lib.CLASS_PINS`,
which the campaigns already agree on):

| frame | pins (A57 δ = 10⁻² slack cores) | free boxes `L` | dropped |
|---|---|---|---|
| k5_11 | `BL(0,0) BL(0,1) TL(0,0) BL(1,0) BR(0,0)` | `f1 f2 f3 BR(0,1)` | `TR(0,0)`, `f0` |
| **k5_16** | `BL(0,0) BL(0,1) TL(0,0) BR(0,0) TR(0,0)` (= corners4 + BL(0,1)) | `f1 f2 f3 BR(0,1)` | `BL(1,0)`, `f0` |
| **trump5** | `BL(0,0) BL(1,0) BL(0,1) BR(0,0) TR(0,0)` | `f1 f2 f3 BR(0,1)` | `TL(0,0)`, `f0` |

`L` is the **same** in all three: the load path `f1 f2 f3` (`a116lib.LOADBEARING["S02"]`) plus
`BR(0,1)`, the one load-bearing slot square that no class pins. Dropped are `f0` and `BR(0,0)` — the
shadow's two rattlers (A160 T1: slides of length 0.298419 and 0.535705, both Δs\* = 0) — and the
wedged no-load slot square each frame does not pin for free (`TR(0,0)` / `BL(1,0)` / `TL(0,0)`). A
dropped body is one clause FEWER: easier for a node to be in-N, harder for the tree to close, which is
why the frames are not interchangeable even at identical boxes.

**Soundness check that the re-framing is legitimate** (`frames163.json`): at the shadow's own side
s\* = 3.886746 the S02 configuration's seven slot squares sit at their slot cells **exactly** — worst
deviation from `α + β s*` is `0.0e+00` in all three frames, against the core half-width 7.07e−3 — so
the pinwheel does satisfy each frame's pin clauses, and all 53 box sets re-frame with box deviation
exactly 0.0 (identical absolute geometry, `code/frames163.py` asserts it).

## 1. The pipeline

1. `frames163.py` — the frame statement + the re-framing check (above).
2. `run163.py --cls <frame>` — A116's selection tree (`a116lib.Tree`, imported read-only) over each
   re-framed box set, then A116's sampling survivor rule (drawn → tested → hits) and the Trump-in-N
   test on every closed tree. Resumable (`--skip-done`), one jsonl line per box set, keyed by
   `<index>|<A160 id>` because A160's ids are not unique (the r_xy probe reuses one). Refusals are
   labelled `WALL_CAP` (cap reached, 0 witnesses — a compute limit) / `WITNESS` (a LIVE-LOW leaf: a
   real partial packing of `L ∪ P` at side ≤ s0 — a geometry limit) / `SAMPLE_HIT`.
3. `gent163.py --cls <frame> --key <key> --check` — the box set re-emitted through **A133's
   `gen_local_t.py`** (t = tan(θ/2), exact rationals, the tree rebuilt from scratch) and verified by
   **A133's independent `check_local_t.py`**, both imported UNCHANGED with `BASE` re-pointed into this
   attempt (A151's `gen_t151.py` technique). Output: `certs/<id>.tcert.json.gz` + sha256 +
   `results/tcerts163.json`. This is the artefact A136 refuses to proceed without: `A136`'s
   `entry151.py` records any node served only by an A160 union entry as **PENDING-CERTIFICATE**
   because `attempts/A160-s02-f0-slide/certs/` is empty and no entry carries a checker verdict or a
   sha256. A163's files therefore carry the t-certificate reference per entry where one was emitted.
4. `consumer163.py --cls <frame>` — A116's/A151's consumer test unchanged (inject the three tilted
   boxes into distinct support squares of the node's A107 support, canonicalised by A107's
   `struct_op`; `BR(0,1)` not matched, A116's convention) over the frame's own S02 nodes.
5. `nboxes163.py` — `results/N_boxes163_k5_16.json`, `results/N_boxes163_trump5.json` in A119/A125's
   `N_boxes` layout, a LIST whose hypothesis is a DISJUNCTION, each entry cross-referenced to the
   A160 object it is the image of and carrying its own `tree_verdict` (this frame's, never A160's)
   plus the `tcert` block when emitted.
6. `docappend163.py` — the two doc lines, staged in `notes/doc_lines.md`.

## 2. Populations

* **k5_16**: the 68 S02 nodes of `A107/results/shadow_nodes.json`; ALIVE = the 37 that are in A151's
  `alive_s02.json` (the population still alive after the night of 2026-09-08).
* **trump5**: the **12** S02 nodes of the A60 protected-tier run (`residue_ledger` §1b: trump5 ×12).
  A107's S02 list has 15 non-A57 rows; three (`k5_02.stageA`, `k5_03.stageA`, `k6_29.stageA`, src
  A61) are the k5_02 / k5_03 / k6_29 singletons of the family table, **not** trump5, and are excluded.
  A60 is paused with no re-solve ledger since A107's input, so all 12 count as alive (`residue_ledger`
  §0: "325 alive nodes in A107's input (S01 196, S07 18, S02 12 …)").

## 3. Budget discipline

≤ 2 BLAS-pinned (`a116lib` imports `blas1` first) BelowNormal processes at affinity `0xFFFF`, one per
frame; the box ceiling of 16 lab processes was polled before every launch and the launch waited for
slots; `--budget-s` stops a worker cleanly; `PYTHONDONTWRITEBYTECODE=1` everywhere. Exact re-emission
is priced from the record: A119's own `S02_k5_11_r0.20_rho10` t-certificate is 16 406 leaves / 13.5 MB
/ 85 s to check and A151's wide `asym_f1` is 38 590 leaves / 26.8 MB / 191 s, so the emissions are
spent on the box sets that actually carry consumers (greedy cover, the node the PI named first),
not uniformly over all 53.
