# A155 — the EXACT-CELL corner band: how much of A150's four-corner product is an artefact of the K0-WIDEN pad?

Restated from the PI's brief of 2026-09-08 (Opus engineer).

## Context

`docs/proofs/k0_route.md` §4.1 (Lemma K0-WIDEN): the k0 tree is built at s0 and covers the window
[3.82, s0] by dilation, so its crowd hypothesis uses corner boxes widened by
`w = (lambda - 1)(1 + sqrt2/2)`, `lambda = s0/m`, `w_max = 0.025509`. At a FIXED side, or on a slab
of declared width T' (`lambda(T') - 1 = T'/(s0 - T')`), the pad is `(lambda(T') - 1)(1 + sqrt2/2)` —
**zero at a fixed side, ~5e-4 for a 1e-3 slab**. The teleport dichotomy (Lemma K0-FREE) holds with
the EXACT unit corner box: a corner met (interior-to-interior) by at most one square teleports the
packing into a k >= 1 class, all of which the pin trees handle (trump5 included), so the corner-root
tree only has to kill packings with two TRUE intruders at every corner.

A150 (`attempts/A150-four-corner-product/`) measured the per-corner band at the FULL pad: 206 of 216
cells survive, the four-corner product is 1.5e9 tuples with only 16 % geometry kills, priced out;
conditioning on four corners at budget 7 buys LP slack (median eta -1.0).

**PI's prediction:** with the exact cell the second-meeter space near the corner is slim, so the band
and the product shrink drastically.

## Tasks

1. **Band vs pad.** Re-run A150's B1 (a first-meeter cell admits an interior-disjoint second meeter
   that meets the corner box interior-to-interior, avoiding K'(first meeter)) at pads
   `w = 0, 5e-4, 2.6e-3, 1.3e-2, 0.0255` (fixed side; slabs of 1e-3, 5e-3, 2.5e-2; the whole window):
   surviving cells of 216 per pad, sampled confirmation (drawn -> tested -> hits) per pad, and a
   figure (A148 panel-G style) of the band at pad 0 vs 0.0255.
2. **Product.** The D4-reduced product cover at pad 0 and at 5e-4 with A150's geometric kills
   (adjacent centre distance, K'-vs-K', diagonals) plus the exact-cell pair kills; survivor counts
   per stage by transfer-matrix trace, as A150 did.
3. **LP (conditional).** If the pad-0 survivors are < 50 000 orbits: the four-conditioned-square LP
   at budget 7 with exact cores on 10 uniformly drawn survivors at s0 (fixed-side semantics; 240 s
   each; 2 BLAS-pinned BelowNormal processes; cap 2 CPU-h; honour every sentinel, no shard) and the
   kill rate.
4. **Slab-wise price.** Number of slabs on [3.82, s0] under the slab-width law (`docs/budget.md` §E;
   check whether the low end is killed outright by A08's root certificate, `k0_route.md` §1) times
   the per-slab product cost from (2)-(3), vs the interior tree's 12 000 CPU-h; and the certificate
   machinery each slab needs (verify_param over the slab with the exact-cell crowd hypothesis: what
   exists and what does not, cf. A56/A114).

## Rules

Read-only on every campaign and prior attempt (new files only under this attempt); frozen verifiers
untouched; no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`; <= 16 python processes on the box
(A149/A151/A152/A153/A154 run 2 each — count first, wait if needed); git = fetch + plain merge +
`git commit -- <pathspecs>` only; registry row + LOG entry. Report ONCE: band-vs-pad table first,
product survivor counts second, LP kills third, slab-wise price fourth, pointers last.
