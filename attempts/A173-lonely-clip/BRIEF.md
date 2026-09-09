# A173 — the LONELY CLIP: Theorem B as a per-piece clip inside A171's multibox library

**Opened** 2026-09-09 (PI).  **Library edited:** `attempts/A171-multibox-invariant/code/multibox.py`
(A172's per-piece K' version, commit 79999887).  Read-only on A168 and every other attempt.

## The gap

A169's **Theorem B** (`docs/proofs/sideband.md` §3, consumption row **R3** in §6) says: a corner
meeter pose that admits **no second meeter** of the widened corner box (a *lonely* pose) is
**impossible** in a K0-BLOCKED packing.  In pose space that is a NO-family, and R3's stated
consumption is "(iii) a conditioned box B_H is clipped to B_H ∖ L_c′" — a **clip**.

A168 applies it only as a whole-role **KILL**
(`attempts/A168-cascade-fable/code/resume168.py`, `lonely_box` / `lonely_role`): a sound
box-level sufficient test, but `lonely_role` requires **every** piece of the role to be lonely,
so a role dies only if every pose is lonely.  Consequences:

* lonely poses **inside a surviving role are never removed**;
* K′ of that role therefore never grows from them;
* and the **cascade** to the other roles (a larger K′(D) clips H harder, which clips D harder …)
  is lost entirely.

The coordinator's measurement with `lonely_box` on the **TR** corner makes the granularity
concrete: an axis-aligned D flush with the right wall slid **down any amount is NOT lonely** (a
partner exists in the top band left of it), but D at **tilt 15° slid 0.1**, or **tilt 30° pressed**,
**IS lonely**.  So the object that Theorem B removes is a set of **tilt sub-bins and centre slabs**,
not whole roles.

## What A173 builds

1. **`lonely_clip(mbox, corner, c)` in `multibox.py`.**  Per piece (tilt sub-bin × centre rect), an
   axis-slab bisection in the style of A131's container clip / A171's `_bisect_boundary`: a slab is
   dropped **iff `lonely_box` holds on the whole slab** (sound — the test is a *sufficient*
   condition for lonely, so keeping the rest is always legal).  A trace step per dropped slab, with
   its area.  Optionally split the tilt sub-bin (`refine`) when a piece is only partly lonely.
   The criterion is **ported** (maths copied with attribution, not imported at runtime) from
   `resume168.lonely_box`, and cross-checked against it on 500 random boxes: identical verdicts.

2. **Wiring into `Node.normalise`** as an optional per-box setting
   `corners={"D": ("TR", c), …}`, applied at **every pass before the mutual clip**, so K′ rebuilds
   from the lonely-clipped pieces and the growth propagates.

3. **Measurement on A168's trees, read-only.**  `results/tree_l1_104.json`,
   `results/tree_l1_153.json`: every **ALIVE S1** node (H + D, corner TR, c = 1 + w,
   w = 0.025509, the K0-WIDEN box) and every **ALIVE S2** node (H, D, S).  Normalise with and
   without the lonely clip; per node report D kept fraction before/after, K′(D) area before/after,
   H kept before/after, passes, invariant, and any `EmptyBox` (a kill).  Table + histogram numbers
   in `results/`.

4. **Figures** (PI's rules; `docs/residue_map/gen_a57_lp.py` is the style reference).  For the S1
   node whose D loses the most: a before/after page — D's pieces as thin rects, the lonely-removed
   slabs hatched red, K′(D) dashed before / solid after, H's K′ before/after, the hypothesis squares
   at box centre and at mid tilt with extremal-tilt outlines, and a note on each panel saying what
   it **is**.  → `docs/residue_map/lonely_clip_S1.svg`, plus a one-page gallery of the ten
   largest-effect nodes in `figs/`.

5. **Test** `attempts/A171-multibox-invariant/tests/test_multibox.py` case **(f)**: the 500-box
   cross-check, soundness sampling (every dropped centre at every sampled tilt of its sub-bin is
   lonely under the pointwise Theorem B criterion), and the invariant after the clip.  Budget 120 s.

## Rules

≤ 2 python processes, BelowNormal, affinity 0xFFFF (logical CPUs 0–15); box ceiling 16 python
processes (A168 shards and A136 are running — count and wait).  Read-only on A168 and every other
attempt.  Editable: A171's `code/`, `tests/`, `notes/`, `usage.md`; this attempt; and the two docs
files (`docs/residue_map/lonely_clip_S1.svg`, `docs/residue_ledger.md`).  No recursive deletes.
`PYTHONDONTWRITEBYTECODE=1`.  Git: fetch + plain merge + `git commit -- <pathspecs>`.  Registry row,
LOG entry, `docs/residue_ledger.md` §6 paragraph.
