# A172 — MULTIBOX K' PER PIECE: the exact intersection of the per-piece cores (Opus)

**A small, exact fix to A171's library** `attempts/A171-multibox-invariant/code/multibox.py`.
No new library, no LP, no tree: one function inside `MBox.rebuild()` is wrong-by-weakness and the
cascade it feeds is therefore weaker than it should be.

## PROBLEM (PI finding; the coordinator's scratch script is not in the repo, so it is re-derived here)

`MBox.rebuild()` recomputes `K'(B)` from `union_box()` — the smallest axis box × tilt hull
containing every SURVIVING piece. That hull FORGETS the shape of the survivors: a clip that removes
different slabs in different tilt sub-bins leaves the hull almost unchanged, so `K'` barely grows on
the side opposite the clip. Since the whole point of the fixed-point loop is the cascade (dropping
poses from `B` enlarges `K'(B)`, which clips the OTHER boxes harder), a `K'` that does not grow is a
cascade that does not bite.

Measured on A168's S2 node BR139/TRH-25 (the `ROLES` of `attempts/A171-multibox-invariant/code/demo171.py`)
after `normalise(nsub=4, refine=3)`:

| | `K'` area, union hull | `K'` area, exact intersection of the per-piece `K'` |
|---|---|---|
| H | 0.658 | 0.710 |
| B1 | 0.798 | 0.799 |
| D | 0.740 | 0.774 |

and one more clip pass with the per-piece obstacles takes the kept fractions H 0.4408 → 0.3816 and
D 0.0882 → 0.0725.

## FIX

In `rebuild()`, build `K'` PER PIECE (`polycore.build` on the piece's own `Box`, per tilt sub-bin)
and take the **exact rational intersection** of the per-piece polygons (convex, ccw;
Sutherland–Hodgman in `Fractions`, then hull/simplify to `<= max_v` vertices by dropping vertices
**INWARD only, never outward**), then **re-certify every vertex of the result with
`polycore.vertex_ok` against EVERY piece** (belt and braces: a vertex that lies in every per-piece
`K'` is inside every pose of every piece, so this must pass — and it, not the construction, is the
proof). The exact axis core likewise: the largest axis square about the centroid of the
intersection, its four corners certified per piece (A135's pattern — the search is a heuristic, the
corner test is the proof).

Keep the union-hull `K'` available as a fallback/diagnostic (mode flag). Keep the public API
(`Node`, `normalise`, `assert_invariant`, `figure`, `chord_rows`, `lane`, `misses_cell`,
`EmptyBox`, `InvariantError`) unchanged, and make the fixed-point loop use the new `K'`. Update the
figure legend (`solid = K'(B) = intersection of per-piece K', certified`).

## TESTS (extend `attempts/A171-multibox-invariant/tests/test_multibox.py`, budget 120 s)

  (i)   on the S2 node the per-piece `K'` areas are `>=` the union-hull areas and within 1e-6 of the
        numbers above at the same settings, and the new fixed point keeps strictly fewer poses for
        H and D than the old one (report the new kept fractions and pass count);
  (ii)  every vertex of every `K'` passes `vertex_ok` against every piece;
  (iii) all the existing tests still pass.

## DELIVERABLES

The before/after table (`K'` areas, kept fractions, passes, invariant status);
`figs/A168_BR139_TRH-25_after.svg` regenerated via `demo171.py`; one paragraph appended to A171's
`notes/usage.md` and to `docs/residue_ledger.md` §6; registry row and LOG entry.

## RULES

≤ 2 python processes, BelowNormal, affinity `0xFFFF` (logical CPUs 0–15); box ceiling 16 python
processes (A168, A169, A136 are running — count and wait). Read-only on every other
attempt/campaign: A171's `code/`, `tests/`, `figs/`, `notes/` and `results/` are the only files
edited outside this attempt (plus the two documentation appends). No recursive deletes.
`PYTHONDONTWRITEBYTECODE=1`. Git = fetch + plain merge + `git commit -- <pathspecs>` only.
