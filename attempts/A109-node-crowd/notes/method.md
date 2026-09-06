# A109 — method, and the one piece of new bookkeeping

## Discipline

* READ-ONLY on `attempts/A57-shadow-trees/`, `attempts/A60-trump5-campaign/`,
  `attempts/A61-window-stragglers/`, `attempts/A94-slot-crowds/`, `attempts/A96-a57-parametric/`,
  `attempts/A107-shadow-gallery/`: every node json used here was **copied** into
  `attempts/A109-node-crowd/results/nodes/<nid>.src.json` before anything touched it, and the
  A94 engine was **copied** into `attempts/A109-node-crowd/code/` (so that even `__pycache__`
  lands here).  No campaign process was started, stopped or re-niced.
* `verify_case.py` byte-identical to the frozen one:
  `sha256 = 521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`
  (same file as A53/A57/A94).
* At most 2 A109 python processes, BLAS pinned to 1 thread (`blas1` imported before numpy in
  every entry point); every LP is preceded by two consecutive readings of free COMMIT > 6144 MB
  **and** free physical > 3072 MB.
* Writes confined to `attempts/A109-node-crowd/**`, the registry row, `LOG.md` and one note
  field on the A57 depgraph node.

## What is added to the A94 engine (`code/slotfam94.py`, three edits, all flagged `A109`)

1. window `G1slab` = `(s0, m_lo)` with `m_lo = s0 / (1 + rho_A57 * 2/5) = 3.8616374951330865`,
   `rho_A57 = 1125896618508387/112589990684262500` — **A57's own G1 slab** (`lemmas.md` T23),
   the only window an A57 G1 node certificate speaks about;
2. `trump5` added to `CLASSES` (pins and usable slots from `A94/results/slots94.json`);
3. `build(..., aw_override, slots_override)` and the flag `ALLOW_AW_GE1`, so that a family can be
   built with an explicit pad and an explicit slot set.

Nothing else in the A94 engine is touched; `caselp94`, `lpbox94` (the `RHS_MULT` hook),
`certify94`'s certificate writer and `verify_case.py` are used verbatim.

## The two configurations, and why `a_w = 1` is the sound one on A57's slab

Lemma SLOT-CROWD gives, at a usable slot `p` of a packing of class `S` at side
`m ∈ W_T = [3.82, ŝ'_p]`, **two non-pin squares meeting the open slot box**.  Lemma SLOT-SLIDE
upgrades "meeting" to depth `d_p ≥ ŝ'_p − m`.  Lemma B-YES-S then places the dilated squares in
`F_p(a_w)` with

    a_w(m) = λ(m) (1 − d) + (λ(m) − 1)(1/√2 + max(i,j)),   λ(m) = s/m,  d = max(0, ŝ'_p − m).

A single family covering the **whole** slab needs `a_w ≥ sup_m a_w(m)`.  For a slot whose
extension is dead on the FULL window (`ŝ'_p = s0`) the SLOT-SLIDE margin and the dilation pad
cancel exactly:

    a_w(m) = (s0/m)(1 + c − s0 + m) − c   is increasing in m, and   a_w(s0) = 1   exactly,

independently of `c = 1/√2 + max(i,j)` (`code/aw_check.py`, exact Fractions, 20001 grid points +
endpoints: `sup a_w = 1`, `a_w(m_lo) = 0.995320478`).  **So the sound node-level crowd family on
A57's G1 slab is `F_p(1)` — "Q meets the closed slot box" — and no positive δ is licensed there.**
A109 uses `a_w = 1 + 10⁻⁵` (a strict outer pad) and calls this configuration `sound`.

The brief's ladder δ ∈ {0.3, 0.1, 0.05} corresponds to `a_w = 0.70963 / 0.91043 / 0.96063` and is
run as a **mechanism measurement**: by Theorem N-S such a certificate kills only sides
`m ≤ ŝ' − δ ≤ 3.827`, i.e. **none of A57's G1 slab** (3.861637, s0].  Reported for the reach of
the mechanism, never as a kill of these nodes.

**`m_u = 3`, not 4.**  A94 ran `m_u = 4`, using the slot whose extension is `k6_23`
(k5_11 TR(0,0), k5_16 BL(1,0), trump5 TL(0,0)), certified only on `[3.82, 3877/1000]` plus the
fixed-`s0` A54 certificate.  On A57's G1 slab that leaves `(3877/1000, s0)` — a real sub-interval
of the slab — with **no** crowd hypothesis at that slot, so the fourth slot cannot enter a
slab-wide node certificate.  It can enter a **fixed-side-s0** one (A60's exact-pin nodes), where
`m = s0` and the A54 certificate applies; the δ-ladder runs here keep A94's `m_u = 4` for
comparability, the `sound` runs use `m_u = 3`.

**A109-O1 (stated dependency).** SLOT-CROWD at the slab's top endpoint `m = s0` needs the
extension classes dead *at* `s0`, not merely on `[3.82, s0)`.  The FULL rows (k6_18, k6_20,
k6_28, k6_29, k6_30 and, for trump5, k6_19, k6_22, k6_24) carry A54/A56/A61 fixed-`s0` base
certificates, which `A96/notes/pocket96.md` §2 relies on in the same way.  If that reading is
wrong the `sound` configuration covers `(m_lo, s0)` and leaves the single side `s0` to A57's own
leaf.

## The node-level incidence budget (the one new piece of bookkeeping)

Lemma CW-S at a **class root** reads: `N` non-pin squares, `Σ r(Q') ≥ 2 m_u`, budget `N + 2 m_u e`.
At a **node** the hypothesis has `k` pin cores *and* `b` branched free-square cores, and the LP
only pays for the `budget₀ = 11 − k − b` remaining squares.  The branched square is a non-pin
square, so it may carry some of the guaranteed incidences and they are then not collectible:

    budget = budget₀ + floor(e · B),      B = 2 m_u − Σ_{branched cores} r_max(B⁺),

`floor` because `verify_case.py` needs `n = 11 + eB` integral.  `B⁺` is the set of poses of a
*unit square that contains the core* `K(B)` — the node certificate's actual claim — bounded in
`a109lib.core_plus`: if `Q ⊇ K` then `a(cos Δ + sin Δ) ≤ 1/2` and `|k − q| ≤ √2(1/2 − a)`, so

    B⁺ ⊆ {|c − k|_∞ ≤ √2(1/2 − a)} × {|θ − θ_K| ≤ arcsin(min(1, 1/(2a√2))) − 45°}.

`r_max(B⁺)` is the max of the **dilated** G-test over a ≤ 0.01 / 0.5° grid of `B⁺` with the
sample half-cell added to the zone tolerance (`a109lib.box_rmax`), so it can only over-count,
which is the sound direction.  Measured on the 46 planned nodes: `r_max ∈ {0,1,2,3}`, so
`B ∈ {3,4,5,6}` at `m_u = 3` and `B ∈ {5,6,7,8}` at `m_u = 4`.

## The e ladder, and the one-LP decision rule

`η(e) = τ(e) − budget(e) = η₀ + c(e)·e − floor(eB)` with `c(e) = (τ(e) − τ₀)/e` the incidence
count the LP's own fractional packing realises.  `τ(e)` is the optimum of an LP whose right-hand
side is affine in `e`, hence **convex and increasing in e**, so `c(e)` is non-decreasing.
Therefore

* a kill at `e` needs `c(e) < B`;
* if the smallest `e` that buys any bonus at all (`floor(eB) ≥ 1`) already returns `c ≥ B`, then
  no larger `e` can kill either — one LP settles the node.

`t2.py --e auto` runs that smallest `e` and only adds `e = 1` when `c < B`.

## Known looseness (all in the conservative direction)

* the row oracle's dilated `G` (EPS_ZONE_G = 0.02, EPS_TH_G = 1°) charges the bonus to more poses
  than `F_p(a_w)` contains — more rows at the higher rhs, never fewer;
* `r_max(B⁺)` over-counts what the branched square can carry, so `B` is a lower bound;
* the 90 s probe refuses a node when `τ_probe ≥ budget`; `τ` rises with the row oracle, so this
  can in principle discard a would-be kill (A94's own rule, `slotcrowd94.run_lp`).
