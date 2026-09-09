# A176 -- writeup corrections owed by the A173 library fix (2026-09-09)

Re-derivation of every A171/A172 headline number on node BR139/TRH-25 (cell l1_153, step S2) with the
FIXED multibox.py (>= 13f23204: Obstacle.uid, content-keyed obstacle cache) -- `code/rederive176.py`,
`results/rederive176.json`, figs `figs/A168_BR139_TRH-25_{before,after}.svg` (this attempt only; A171/A172
untouched).  Library test suite post-fix: `results/test_multibox_postfix.json`, ALL PASS (70.7 s, budget 120 s) [M].

Numbers cited in `writeup/02_mathematics.md` (5.9, l. 768) and `writeup/03_lab_timeline.md` (3.7, l. 560-575):

| number | pre-fix (A171 demo171.json / A172 report172.json) | post-fix (A176) | changed? |
|---|---|---|---|
| A171 after normalise, kept H / B1 / D (union hull, the writeup's 0.440792 / 0.942803 / 0.088172) | 0.440792 / 0.942803 / 0.088172 | 0.440792 / 0.942803 / 0.088172 | no |
| A172 fixed point, kept H / D (writeup: 0.44 -> 0.36, 0.088 -> 0.072) | 0.358392 / 0.072175 | 0.358392 / 0.072175 | no |
| K' area, union hull, H / D (writeup: 0.658 / 0.740) | 0.658006 / 0.740065 | 0.658006 / 0.740065 | no |
| K' area, same pieces per-piece, H / D (writeup: 0.709 / 0.774) | 0.709336 / 0.774356 | 0.709336 / 0.774356 | no |
| K' area, A172 fixed point, H / B1 / D | 0.730797 / 0.799343 / 0.793731 | same | no |
| pieces (A172) H / B1 / D; passes | 22 / 32 / 12; 2 | 22 / 32 / 12; 2 | no |
| chord rows top / right beta | 2 / 1 | 2 / 1 | no |
| lane(TR cell) | 0 (33 leaves, 0 open) | 0 | no |
| invariant before / after | FAIL / PASS | FAIL / PASS | no |

Result: NO cited number changed [M].  On this node the id()-keyed cache never served a stale bound
(the obstacle addresses were not recycled across its 2 passes), so the pre-fix and post-fix runs coincide
to every printed digit.  The bug was live in general (A173's reproduction: 2 aliases in test (a), flickering
`a2.invariant_after`), which is why the whole cascade record is re-normalised (renorm176), not just this node.

New number, not yet in the writeup: with the lonely clip on D at TR (`corners={"D": ("TR", 1 + w)}`) the same
node keeps D 0.057384 (was 0.072175), H and B1 unchanged, K' areas unchanged [M].
