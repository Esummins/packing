# A85 — k0_00: cut the price by an order of magnitude before spending it (Fable lead)

You are the THEORY lead (Fable). A84 priced k0_00 (the exact zero-simple-square class = the
unstratified root problem: no pins, no cores, no logic kills, 11 free squares, 8 Trump images) at
~25-30 desktop-days with A58's corner seed, >= 100 plain. The PI does not accept that as final and
neither does the advisor. Your job: DESIGN the cheapest sound route, prove its lemmas, pilot the
cover, re-price. Three cuts A84 did not take — verify each, quantify each:

## C1 — quotient by D4
k0_00's pin set is empty => the class's symmetry group is all of D4 (A67 machine-checked the D4
reduction at s0; A78's Census.lean has the action). The 8 Trump images are ONE residue seen 8 times:
run the tree on a fundamental domain with the mod-G bookkeeping stated (Lemma K0-D4: a selected
k0 minimiser has a D4 representative in the fundamental domain; (D) leaves land on ONE image;
the tube composes per D.S6's mod-G clause). Expected: ~/8 on the residue term.

## C2 — teleport reduction to k1_00
CC-2 (Lean): a non-simple square teleports onto any completable slot FREE of other squares. At
k=0 the only completable slots are the four corner slots. Lemma K0-FREE: a k0_00 packing at side m
with a free corner slot is excluded whenever k1_00 is excluded at side m (teleport, same side,
lands in k1_00 by definition — check: exactly one simple square results; is the result
necessarily in k1_00 and not a higher class? state the case). So k0_00's OWN tree owes only the
residual K0-BLOCKED: all four corner slots non-free. Then A58's theorem applies with force: each
corner box met by >= 2 non-simple squares (prove the "slot non-free => corner box doubly
crowded" step or cite A58's exact form) => 8 squares localised to 4 corner regions, 3 free.
State the k1_00 dependency explicitly (k1_00 is image-bearing, priced by A84 as a k3-scale tree).

## C3 — the doubly-blocked seed as a COVER
Turn "two non-simple squares meet each corner box" into box-level localisation for 8 of 11
squares (which two positions/tilt classes are possible for a corner-blocker pair: one flush on
each wall? both tilted? enumerate exactly — this is the corners4 straddler analysis applied to a
corner with NO simple square in it). If the corner-blocker geometry is as rigid as corners4's
straddlers (likely: two unit squares both meeting [0,1]^2, neither simple, no overlap, and the
corner slot must be non-free), K0-BLOCKED may reduce to a finite case list — then discharge by
per-case exact certificates instead of a tree. Either way pilot the cover on the fundamental
domain with A84's engine copy (<= 3 LP slots, BLAS-pinned, headroom > 6 GB): census, kill rate,
residue, contraction ratio; canary: the Trump image in the fundamental domain must land in a (D)
leaf, never be killed.

## T4 — the stratum_kill_selected re-split
A84 notes the corner seed forces the kill axiom to be stated for SELECTED minimisers. Write the
exact statement change for TopLevel (which axiom, what hypothesis is added, why B.SEL/Census
supply it) — a Lean-readiness note, no lean/ edits.

Deliverables: docs/proofs/k0_route.md (K0-D4, K0-FREE, the blocker-pair enumeration, composition,
re-price with the three cuts separately and stacked); pilot results; depgraph C.K4TIER note
(chip -> A85); registry; LOG; findings (in the proof doc §last if notes/ is blocked). A85 is a
design+pilot attempt: the deliverable is a PRICE with proofs behind it, and a finite case list if
one exists. Constraints as A84: copy engines, never touch A57/A60/A61 or frozen verifiers.
