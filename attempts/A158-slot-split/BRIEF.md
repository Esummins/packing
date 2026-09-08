# A158 — the SLOT SPLIT: a tautologous YES/NO branch on the near-simple slot box

## The brief (restated)

`c0_Y0076` (A60 trump5, level 1, alive; page `docs/shadows/a57v4/c0_Y0076.svg`; A141/A157 records
in `attempts/A141-polycore-lane/results/t2_a5760_s{0,1}.jsonl` and
`attempts/A157-undecided-slots/`) has `TL(0,0)` as a **usable slot** — trump5's non-simple corner,
extension class `k6_23`, which must be certified dead on the node's window (A118's table; verify).
A157 found that a second free meeter of that slot **exists in isolation**: a square tilted
29.4420 deg clearing `K'(H)` and every pin core by **1.1026e-2**.

**The PI's diagnosis.** The node LP stays alive only because it simultaneously

* puts a square in the *near-simple* `TL` slot position, and
* counts `H` (and the tilted square above-right of `H`) as meeters of that slot,

which no single packing does. Concretely:

* if the slot region holds a square, **that square is the sole meeter** of the slot cell
  (teleport ⇒ the certified-dead `k6` extension class);
* if it does not, the only two-meeter configuration is `H` + the tilted square, and that strands
  all the area to `H`'s left.

**The leaf is therefore a YES/NO split on the slot box**

    S = { poses of the slot : centre within 0.10 of the exact slot centre,
                              tilt within 10 deg of 0 or 90 }          (then 0.15 / 15 deg)

which is a tautology (`some square's pose is in S` OR `no square's pose is in S`).

* **YES child**: some square has its pose in `S`. Run A141's conditional lane test with that
  square's `K'(S)` as an ADDITIONAL obstacle. `LANE_K'(cell | S occupied) = 0` *and* `M = 0`
  ⇒ the slot cell is met by the `S`-square alone ⇒ singly met ⇒ snap ⇒ the dead `k6` class.
  Certificate in A141's `polycore_slot_lane_v1` format, exact-pin form, caveat **A118-O1 stands**.
* **NO child**: no square has its pose in `S` — a `NoFam(S)` exclusion (A112's `caselp` `nofams`
  clause through A136's `a136lib` wrapper: inward rounding + `ZONE ⊆ BOX` on the written
  rationals), the node LP re-solved with exact cores and the `K'`-pruned pool (240 s, 900 s at a
  knife edge), certified by the frozen `verify_case` at `s0` (and `verify_param_v2` at the
  degenerate window) exactly as A120/A136 did.

## Tasks

1. **`c0_Y0076` first**: both children, `tau`/`eta`, certificates.
2. **Then the population**: every alive A57/A60 node (A137's `PAUSED.md` v3 state and A60's alive
   list) whose dual support puts weight ≥ 0.5 into some usable slot's `S` box. Count them, run the
   split on the top 20 by that weight, report kills (both children dead) vs YES-only / NO-only.
3. **The leaf statement and the Lean shape** — the tautologous split over `S`, the conditional lane
   leaf, `NoFam` — all existing pieces, named; plus the fold-in lines (`PAUSED.md` v3 addendum,
   A60 ledger) and one sentence in `docs/residue_ledger.md` §1.

## Rules

≤ 2 BLAS-pinned processes, affinity `0xFFFF`, Normal priority, cap **4 CPU-h**. ≤ 16 lab python
processes on the box (counted first, see `notes/method.md` §0). Honour every sentinel; never launch
a shard. READ-ONLY on every campaign and every prior attempt — new files only under this attempt
plus the named appends (`attempts/A57-shadow-trees/PAUSED.md`,
`attempts/A60-trump5-campaign/notes/ledger.md`, `docs/residue_ledger.md` §1). Frozen verifiers
byte-identical (sha checked). 6144 MB commit gate and > 3 GB free physical before every LP; per-LP
wall 1,500 s. No recursive deletes. `PYTHONDONTWRITEBYTECODE=1`. Git = fetch + plain merge +
`git commit -- <pathspecs>` only. Registry row and LOG entry.
