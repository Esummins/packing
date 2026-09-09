# Eleven squares in a square: the result, the method, and who did what

*Living document, edited in place. Status as of 2026-09-09. Tags: [T] proved in the notes, [L] checked in Lean,
[C] backed by a machine-checkable certificate, [P] pending compute, [S] supported but not proved.*

## The question

Take eleven unit squares. What is the smallest square box they all fit in, with no overlaps and any rotation
allowed? The best known arrangement, found in 1979 and never beaten, uses a box of side about 3.8771. Nobody
had proved that nothing smaller works, and the gap between what was known and what was believed had stood
for roughly fifty years. This lab's goal is that proof: the minimal side is exactly the known value, and the
known arrangement is the only way to achieve it, with every step of the argument either a checked proof or a
certificate a computer can verify independently.

## What is established now

- **Bounds.** The side is at least 3.82 and at most 3.877084. The lower bound is certified [C]; the upper bound
  is the exhibited packing. The remaining question is the window between them.
- **The window is closed except for one family.** The problem splits into classes by how many squares sit
  "simply" against the box. Every class but one is closed on the whole window by certificates checked by a
  frozen verifier [C], with the closures around the exact local minima checked in the Lean proof assistant [L]
  for two of the four minima. The last family, called k0, is where no square sits simply and every corner of
  the box is met by two tilted squares. Its residue is eleven cells of hypothesis space.
- **No k0 cell has yet been killed.** This is the honest state of the proof. The machinery to kill one is
  built and is being run on the first cell, l1_104, as the test case. Until a cell dies, the claim that the
  rest is "just compute" is a projection, not a result.

## How the proof works, in plain terms

Every candidate arrangement is described by where each square's centre is and how it is turned. The proof
never searches for arrangements. It does the opposite: it assumes a region of possibilities and shows the
region is empty, by one of two kinds of argument.

1. **Counting arguments turned into linear programs.** If some squares are pinned to a region, the area they
   must cover and the walls they must touch leave less room than the other squares need. A linear program
   finds the contradiction, and a small certificate lets anyone re-check it exactly. This is the workhorse,
   and it is expensive: tens of minutes per case, thousands of cases.
2. **Geometry.** Before any linear program runs, the region is shrunk by facts that need no computation at
   all: a square that must sit here cannot also sit there; two squares that must share a point are the same
   square; a corner met by two squares forces one of them into a narrow band along a wall; a square pulled
   diagonally away from a corner leaves no room for the partner the corner requires. Each such cut also grows
   the "core" every pose of a square must contain, which cuts the neighbouring squares in turn. Done to a fixed
   point, the geometry removes most of the tree before the linear programs see it.

The order of these two, geometry first and to a fixed point, then linear programs only where geometry runs
out, is the central lesson of the lab and the reason a k0 kill is expected to be compute-bound rather than
open-ended.

## What the AI could not do alone

The AI built the pipeline: the certificate format, the frozen verifiers, the Lean kernel, the case trees, the
linear programs, the galleries of thousands of drawings, and the process that ran them across weeks of
compute. It could not, on its own, tell when it was cutting the problem along the wrong lines. Concretely,
from the record:

- The idea that makes the whole proof tractable, stratifying by how many squares sit simply against the box,
  came from the PI, not the AI.
- Twice the AI built multi-square case trees on boxes it had not clipped against each other, producing
  pictures of squares overlapping and leaving the container. The PI saw it in the drawings; the AI had not.
- The AI's clipping code rebuilt cores from a bounding hull, throwing away the growth that makes cuts
  propagate. The PI asked whether the polygon grew on the far side of a clip; it did not; the fix followed.
- The AI's cascade clipped against small inscribed squares rather than the true polygon cores. On the page
  that showed it, one square's outline crossed two neighbours' cores while the printed numbers said nothing
  had been cut. The PI read the picture; the corrected clip kills that node outright.
- Several of the PI's readings were wrong too, and the drawings said so: a hairline grazer the eye cannot
  see, a lane the PI thought open that a certified polygon closed. The loop corrects in both directions.

## The systems that closed the gap

The PI cannot read certificates or linear programs, and does not write proofs in the usual sense. What the
PI can do is look at a drawing of squares and see what is possible. So the lab was built around drawings:
every open case is rendered as a page with the hypothesis square at the centre of its region and at its
middle tilt, the extremes drawn faintly, the cores every pose must contain drawn solid, the pinned squares
drawn only as pins, the undecided region stippled grey and never a hopeful colour, and a note on every panel
saying what it is. A status script moves pages to a `killed/` folder as certificates land so the PI only
reads what is alive. The PI reads pages and writes readings; the AI turns readings into lemmas, tests them
against the certified geometry, and either kills the case or shows the PI why the reading fails. A reading
that survives becomes a reusable leaf that applies to every case, not just the one it came from.

That loop, drawing, reading, refutation or lemma, re-drawing, ran dozens of times a day. It is where the
proof's geometric leaves came from, and it is the part of this work that is not about squares.

## What remains, and what "compute-bound" would mean

- Kill l1_104 [P]: the cascade with the polygon clip, the lonely clip and the partner cuts, then linear
  programs only at the geometric fixed point. A first kill is the evidence the method works on k0.
- Repeat on the other ten k0 cells and on the remaining alive pages of the other classes [P]; the current
  price for the expensive class is a few thousand CPU-hours, and every geometric leaf lowers it.
- Finish the Lean composition [P]: the two remaining local minima, the sideband requirement theorem, and the
  top-level assembly that turns the class certificates into the theorem.

When a k0 cell has died by the same machinery that closed the other classes, the remaining work is running
that machinery, and the claim "the certificates exist for a known amount of compute" becomes a statement
about a pipeline that has already done the hard case once.

*See `02_mathematics.md` for the lemmas and their composition, and `03_lab_timeline.md` for the full record
of the interaction.*
