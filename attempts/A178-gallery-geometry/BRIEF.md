# A178 — gallery geometry: forced corners, c0_Y1033 cascade, geometry pass over the alive pages

Lead: Fable. Dispatched 2026-09-09 ~14:15 after the PI's reading of docs/shadows/a57v4/.
Agent messaging is broken this session: everything is in this brief and on disk. Responses short;
files written in pieces (<= 250 lines); no proofs or tables inline in chat.

## The PI's reading (2026-09-09 ~14:10)
"A lot of them should die to either core cascades or the forced two-corner solution requirements or
both. E.g. I think c0_Y1033 dies after you include the tl00 corner pair pins, and then cascade from
the br01 two-meeter requirement."  Priority: the PI's named node first, then the rest of the alive pages.

## Toolkit (all read-only for A178)
- attempts/A171-multibox-invariant/code/multibox.py (>= 13f23204): Node(roles).normalise(nsub, refine,
  mode="poly", kmode="pieces", strict_container=False, corners={role: (corner, c)}) = container clip +
  mutual clip against every other role's K' POLYGON to a fixed point, K' rebuilt from the pieces, + the
  LONELY clip (A169 Theorem B) at named corners; assert_invariant(strict=False); EmptyBox = pair-leaf
  kill; chord_rows, lane, misses_cell; notes/usage.md.
- attempts/A173-lonely-clip (measurement pattern).
- attempts/A168-cascade-fable/code/{roles168,resume168,coex174}.py: coexistence / partner-existence
  cut at a corner (A176 is editing that directory — read only).
- docs/proofs/sideband.md (SIDEBAND cell lemma, REQUIREMENT Theorem B, rows R1-R3);
  docs/proofs/k0_route.md, k0_blocked_side.md (K0-WIDEN pad w = 0.025509; K0-BLOCKED corner structure);
  docs/proofs/lockfree.md (teleport / free rotation).
- docs/shadows/a57v4/README.md + review CSVs + status (alive pages and their records: H box, pins,
  conditioned squares, class frame, quadrant census).
- docs/residue_map/gen_a57_lp.py: the drawing rules.

## Tasks
(1) THEORY FIRST [T]: docs/proofs/forced_corners.md — for a page of class k5_11 / k5_16 / trump5 (and
    k0), which corners are FORCED to be doubly met: a container corner whose corner box (side 1 on a
    fixed side, side 1 + w on the window) contains no simple square must be met interior-to-interior
    by two distinct squares — else the singly-meeting square can be made simple (teleport / free
    rotation) and the packing belongs to a class with one more simple square, CLOSED on the window
    (52/52 rows [C]).  Settle: window vs s0, the pad, what "simple" means in the class frame, whether
    the census pins already witness the meeters; state any caveat exactly (e.g. a corner met by a
    simple square of another corner's crowd).
(2) c0_Y1033 (trump5, A60 record): roles = H + every pin + every conditioned square; add the TL00
    corner-pair requirement (both TL meeters as roles with the SIDEBAND cell split, or the coexistence
    cut if the record fixes one); normalise (poly + lonely at every forced corner); then the BR01
    two-meeter requirement as the next cascade step (partner from the allowed cell only, clearing every
    role); re-normalise; rows from the grown cores; pair leaf.  Page docs/residue_map/c0_Y1033_cascade.svg
    (one panel per step: what was added, kept fractions per role, K' before/after, the invariant line).
    Verdict DEAD (which leaf + certificate) or ALIVE (what survives and why).
(3) Same pass over EVERY alive a57v4 page (52) and the eleven k0v4 pages, geometry only (LP only if the
    geometry reaches its fixed point and one multi-box LP is < 0.5 CPU-h): results/geopass178.jsonl
    (roles, forced corners, kept fractions before/after, K' areas, verdict, leaf); a collector block in
    docs/shadows/status_gallery.py in the style of (7b)/(7c); rerun it; regenerate killed pages' figures;
    append docs/residue_ledger.md section 4 and docs/budget.md section D; registry row; LOG entry;
    commit with `git commit -- <pathspecs>` after fetch + plain merge, push, at every milestone.

## Rules
<= 2 python processes, BelowNormal, affinity 0xFFFF (CPUs 0-15); box ceiling 16 python processes (count
and wait); read-only on every other attempt; no recursive deletes; PYTHONDONTWRITEBYTECODE=1; never
delete pidfiles; frozen verifiers byte-identical.  Every claim tagged [T]/[S]/[M]/[F]/[C].
Report ONCE, tersely (< 1,000 words): forced-corner statement; c0_Y1033 verdict + page; pass table
(kills by leaf, pages retired, gallery counts); pointers.
