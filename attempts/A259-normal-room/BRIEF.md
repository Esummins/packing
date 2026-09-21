# A259 -- NORMAL-ROOM: the pocket of the NORMAL ring holds at most two squares (aim: one) -- the room half of the
# k0 exclusion, on the small family that normalisation leaves (PI, 2026-09-21: theory day on k0).
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop.  A258 (NORMAL-RING)
runs in parallel on the STRUCTURE half and will commit attempts/A258-normal-ring/notes/family258.md (the exact
parameter domain D); start from the family below, re-read that file when it appears (git fetch + merge), and say in
your report which version of D you used.
Read first: docs/proofs/common_sense.md s.2 (VALUE-WLOG, NORMAL-CELL, one-step normalisation; s.2.4: the ring is one
exchange per wall from a row of two), attempts/A258-normal-ring/BRIEF.md (the coordinator's reading: the normal ring
is a pinwheel of four common-tilt PAIRS, (delta_w, phi_w) per wall, 8 coordinates + s), mintilt253.md (HOLE-ONE [T]:
in a square of side <= 2 every unit square contains the centre, (w-1)(sigma-w-1) <= 0 with w = cos + sin;
NOTCH-NARROW; room measured constant 1 across 2-26 deg on the common-tilt slice), peel.md (A254: core_fits [Lean T],
BAND-COUNT, POKE: a free square enters a gap of width g by one vertex to depth <= g/2; the non-effective tau0;
QUANT-ROOM [C]), ring_pocket.md (A251: box-valid PIERCE priced 5e14 CPU-h on the 17-coordinate family; INRADIUS,
THREE-DISC, MID-NOTCH), centre_disc.md (A252: disc criteria too weak -- need SQUARE room; ring + ribbon poker =>
residual centre set empty), pocket_waste.md (PIERCE, Lean capacity_le_of_pierce), ring_capacity.md (Lemma TWO).

## The statement
NORMAL-ROOM(11): for every normal ring in D at s in [3.82, s-hat] (stretch: [3.82, 4)), the pocket = container minus
the eight ring squares holds at most TWO interior-disjoint unit squares (then 8 + 2 < 11; aim for ONE, which
leaves margin for a structure with one extra border square).  The free squares include the poker(s).

## Task
1. ANALYTIC FIRST.  The pocket of a pinwheel of four common-tilt pairs: each row has height cos + sin >= 1 above
   its wall, a sawtooth inner boundary (teeth of depth ~ tan phi), and leaves a corner gap before the next wall's
   row.  Generalise HOLE-ONE: find a region R(delta, phi, s) containing every unit square of the pocket (the centre
   square of side s - 2(cos + sin)-ish, enlarged by the POKE depth into teeth and corner gaps) and prove every unit
   square inside the pocket contains the centre O -- or contains one of TWO points (PIERCE(2)) -- by a closed-form
   inequality on D.  Where can a SECOND square hide: the corner gap between a row's end and the next row (this is
   where the ribbon poker lives)?  Bound the corner gaps' capacity (a gap narrower than 1 in one direction holds
   only a poking vertex: POKE) and show poker + centre square exhaust the room, or find the sub-domain where a
   third square fits and draw it.
2. CERTIFIED where the analysis stops: box-valid PIERCE over D (<= 9 coordinates; use D4 and the potentials'
   normal-form equalities to cut dimensions; interval arithmetic outward-rounded; certificate rows + an own
   verifier).  Benchmark 200 boxes before pricing; launch detached if <= 150 CPU-h, else report the price and the
   dimension that costs.  Cross-check every claim against exact region search (A226/A237/A253 room code) on >= 50
   sampled normal rings across D, including the extremes of D.
3. EFFECTIVE tau0 (A254's QUANT-ROOM) falls out if 1-2 cover D; say so, and retire or restate MONOTONE-ROOM.
4. General m (n-general form): with rows of m - 2 the hole is a container of side ~ s - 2(cos + sin) <= s - 2:
   PEEL in normal form, s >= 2 + s(n - 4(m-2)) minus what the corner gaps can hold; state exactly what is [T].
5. Say plainly: NORMAL-ROOM(11) [T] / [T-computed] / [C] and on which side range; with A258's NORMAL-RING the
   chain to FAMILY-STUCK-EXIST(11) and k0_00; the exact remaining obligations.  Deliverables:
   docs/proofs/normal_room.md, Statements/Open/NormalRoom.lean (theorems where the set description suffices --
   HOLE-ONE's pattern --, documented axioms otherwise; consequence chain; build + audit 0 sorry; AUDIT.md rows),
   code/, results/, certs/, pages in docs/residue_map/campaigns/A259-normal-room/ (the normal ring's pocket with
   the region R and the piercing point(s); the corner gap with the poker; the worst case in D; geometry-checked, a
   note per panel saying what it IS, undecided grey stipple never green), registry row, LOG entry, ledger s.4
   note.  Report once (<= 20 lines).  EXIT.
