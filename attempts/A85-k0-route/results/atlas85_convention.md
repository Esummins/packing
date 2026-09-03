# A37 atlas `z_center` coordinate convention (A85 JOB 2)

Sources: `attempts/A37-cp-atlas/results/atlas_final.json`, the 37 cert files it points at,
`attempts/A37-cp-atlas/code/a37_check.py` (the standalone re-checker, which is the operative
definition of what the certificates mean), `attempts/A37-cp-atlas/notes/cookbook.md` (step 5 +
amendment A8).

## The vector

`z_center` is a list of **34 exact rationals** (decimal strings `p/q`), laid out as

```
z = [ cx_0, cy_0, th_0,  cx_1, cy_1, th_1,  ...,  cx_10, cy_10, th_10,  s ]
      ^-- 11 triples, one per square, in the entry's own square ordering --^   ^ index 33
```

This is "A22 order": **squares in interleaved triples**. It is *not* the `pack11.py` layout used by
the A04 catalogue (`best_x`: centres interleaved `x[2i], x[2i+1]`, thetas blocked `x[22+i]`,
`s = x[33]`). Cookbook amendment A8 records the conversion; A37 applies it at load.

Verified directly in `a37_check.py`: `row_vars` returns `[3*i, 3*i+1, 3*i+2]` for square `i`
(plus `S_IDX = 33` for `x=s` / `y=s` wall rows), `row_jet` reads `cx, cy, th = V[0], V[1], V[2]`
and `sep_td` reads `box[3*i], box[3*i+1], box[3*i+2]`.

## The tilt coordinate

**`th` is the tilt angle in radians, plain `theta` — NOT `t = tan(theta/2)`.** `a37_check.py`
feeds it straight into `iv.cos(box[3*i+2])` / `iv.sin(box[3*i+2])` and builds corners as
`q = c + R(th) h`. So the E.COORD X.1 conversion (`|dt| <= |dtheta| <= 2|dt|` on `[0, 45 deg]`) is
**not needed** for A37 boxes; the box radius `h_certified` is a bound on `|dtheta|` in radians
directly.

`th` is **not** reduced mod `pi/2`: both `0` and `pi/2 = 1.5707963...` occur as literal
coordinates of axis-aligned squares (e.g. entry 0 has `th_3 = 0`, `th_5 = pi/2`). A comparison must
therefore allow `theta -> theta + k*pi/2` (the unit square is invariant under it, so the
re-labelled configuration is the same packing with the same `s`).

## The frame

Absolute coordinates in the critical point's **own container frame `[0, s]^2`**, unnormalised and
unrescaled, with **`s` itself the 34th box coordinate**. The box is the L-infinity ball
`||z - z_center||_inf <= h_certified` in exactly these coordinates, so `|s - s_center| <= h` is one
of the 34 constraints. Entry `s_center` may differ from the atlas field `s_min_float` by up to
2.3e-4 (fam14) because `z_center` is the Gauss-Newton refined / Krawczyk-rationalised point.

## D4 normalisation

**There is none, and there is no canonical square ordering.** Each entry sits at whichever D4 image
and square labelling its producer happened to hand over (the A04 catalogue `best_x` for families
0..31, the A37 drain probe for `A37-NEW-*`, A51 for `A51-NEW-0`). Concrete evidence: entry 0's
`z_center` is the **transpose** (reflection in `y = x`, `theta -> pi/2 - theta`) of
`attempts/A03-upper-reconstruct/trump11_float.json`, with the squares in a different order. The
self-test confirms it: Trump's own placements match entry 0 under D4 element `diag` at L-infinity
distance 3.6e-15.

Consequence for any containment test: it must quotient by the 8 D4 images, by the 11! square
relabellings, and by `theta + k*pi/2`. `atlas85.in_atlas` does all three (D4 enumerated, relabelling
by exact bottleneck/minimax bipartite assignment on the per-square L-infinity cost, `k` folded into
the cost via `theta_delta`).

## Soundness of the normalisations

(i) A D4 image of a feasible packing in `[0,s]^2` is a feasible packing in `[0,s]^2` with the same
`s`. (ii) Relabelling squares and shifting a tilt by `k*pi/2` change the coordinate vector but not
the set of squares, hence not feasibility and not `s`. So if any normalised image of a packing lies
in an entry's box, the entry's claim `sigma >= V` applies to that packing.

Not applied: global translation. The container walls fix the frame, and a translation that keeps the
packing inside the container would also be sound, but it is not used here — reported distances are
therefore upper bounds on the achievable distance, i.e. margins are conservative.

## Claim recap

Per entry: *every interior-disjoint 11-square packing `z` with `||z - z_center||_inf <= h_certified`
has `s(z) >= V`*, with `V >= s0 = 969271/250000 = 3.877084` an exact rational. Range of
`h_certified` over the 37 entries: 3.759e-3 (entry 0, the tightest) to 5.99e-2 (entry 31).
