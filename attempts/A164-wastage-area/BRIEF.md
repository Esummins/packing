# A164 — WASTAGE AREA: the uncoverable set U(node) as an LP-free leaf

**Opus engineer, 2026-09-08.  Working directory `attempts/A164-wastage-area/`.**

## The PI's argument (the seed)

On the k0 cell `l1_104` (H at x 2.4626–2.5674, y 2.1482–2.2530, tilt 30–45°; records A140/A141)
the PI argues by WASTAGE: only one square's centre can sit near the right wall below H's reach,
the upper-right pocket beside the top wall is too short for any centre, so wherever that one
square goes most of the right-wall strip stays uncovered.

A89's **Lemma ID** (`docs/proofs/tilt_floor_k0.md` §7) prices exactly this for corners: at side m
the area no square interior covers is

  E(m) = m² − 11,  E ≤ B₀ = s₀² − 11 = 4.031780343056 on the window,

and a SHALLOW(δ) corner strands (1 − δ)² of it.  Area alone never killed four shallow corners
(4(1−δ)² ≤ 4 < 4.0318).  A164 asks whether the same budget row, charged against a *certified
uncoverable region* rather than a corner box, has teeth.

## The leaf to build and measure — UNCOVERABLE AREA

For a node with pins (fixed squares, A135 exact cores), conditioned squares H (A132 polycore
K′(H)) and `budget` free squares,

  **U(node) = { p ∈ [0,s]² : no admissible square contains p }**

where *admissible* for a FREE square = inside the container and interior-disjoint from every
pin's exact core and from K′(H) of every conditioned square; for a CONDITIONED square its
possible cover is the union of its poses over its box; likewise for a pin over its box.

Every 11-packing consistent with the node covers 11 units of area with its square interiors, and
each square's point set lies in its own coverable set, so

  **|U| ≤ m² − 11.  |U| > m² − 11 ⟹ the node is DEAD, LP-free.**

Threshold used: B₀ = s₀² − 11 = 4.031780343056, the LARGEST wastage budget over the window
slab [3.81794, s₀] (E is increasing in m), so a kill against B₀ is a kill at every m in the slab.
The *window-sound* variant additionally widens the cover square to side λ_max = s₀/3.81794 while
keeping admissibility at side 1 (a λ-square that is admissible contains an admissible unit
square, and its cover is inside the λ_max-square) — stated per node.

## Tasks

1. `l1_104` first: |U| lower bound by region (right-wall strip, pockets, corners) vs 4.0318;
   a figure in A148's panel style with U shaded.
2. The eleven converged-alive k0 cells + every page of `docs/shadows/a57v4/` + the 11 `k0v4`
   pages: |U| vs budget per node, the distribution of |U| / (s₀² − 11), kills if any
   (certificate = raster + margin + the sampled line, independent checker).
3. The leaf's statement and Lean shape (Lemma ID's proof pattern generalised from a corner box
   to a certified-uncoverable region; what obligation the raster carries) and one paragraph each
   for `docs/residue_ledger.md` §6 and `docs/budget.md` §D.

## Soundness

A raster cell is certified ⊆ U only when NO admissible pose meets the closed cell — a
Lipschitz-margin test in the spirit of A148's `geo148.py` (clearance is 1-Lipschitz in the centre
and (√2/2)-Lipschitz in the tilt), so the mask is an INNER approximation of U and |U|_raster is a
LOWER bound.  Cross-check by sampling: 10⁵ random admissible poses, none may contain any
certified-uncoverable cell centre (drawn → tested → hits).

## Rules honoured

Pure geometry; ≤ 2 processes at BelowNormal with affinity 0xFFFF; box ceiling 16 lab processes
(counted before each launch); cap 3 CPU-h; READ-ONLY on every campaign and prior attempt (new
files only under this attempt plus two doc lines); no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`;
git = fetch + plain merge + `git commit -- <pathspecs>` only; registry row and LOG entry.
