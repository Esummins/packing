# A90 — Theorem NOCRIT: the side function has no critical point inside K0-BLOCKED (Fable lead, theory)

Context (all 2026-09-03). The proof's k0 residue is K0-BLOCKED: every corner's open unit slot is intersected
by >= 2 squares (else the teleport lemma K0-FREE / CC-2 moves a square into a free slot at the same side and
the point is a k >= 1 point). DF-K0 (A87) reduces k0_00 to H1: no k0 Fritz-John point at side <= s-hat; with
K0-FREE, H1 is H1-B: no FJ point of the enclosing-side function inside K0-BLOCKED at side <= s-hat. The
evidence now says something much stronger and structural:
 * the 167 certified "k0" FJ points (A87) are ALL K0-FREE (0/167 K0-BLOCKED; notes/k0blocked87.md);
 * a directed critical-point search seeded INSIDE K0-BLOCKED (520 seeds, notes/k0dir87.md) found 0 FJ
   points there at ANY side; every flow exits K0-BLOCKED, 520/520 by a blocker sliding away (never by the
   slot squares rearranging); the infimum of sigma over each K0-BLOCKED basin is attained only in the
   closure where a corner becomes K0-FREE (17/18 deep-pass endpoints sit at sigma = 4.000 with the
   second blocker's depth -> 0); lowest K0-BLOCKED packing found 3.985 = s-hat + 0.108;
 * corner occupancy at critical points is thin (633/668 corners one intruder, 21 two, 0 three);
 * BUT Trump's TL corner is a genuine doubly-intruded corner at a critical point (sq4 axis-aligned
   upright at depth 0.155, sq6 at 40.18 deg at depth 0.168, both flush-locked by far-side contacts in
   the Trump grain) — so "a doubly-intruded corner is never critical" is FALSE; the theorem must use all
   four corners blocked (equivalently: no simple square anywhere, K0-BLOCKED).
PI conjecture: the global optimum for every n lies on the k >= 1 manifold. The n = 11 version that the
proof needs is NOCRIT below.

Read first: docs/proofs/drain_flow_k0.md (DF-K0, FJ formalism, drain step and its obligations),
docs/proofs/tilt_floor_k0.md (A89: Lemma LOCK — a square is flush-locked iff its active contacts can
exert a couple away from flush or a self-stress; Lemma MENU — a bottom-wall blocker is locked only by
FAR-SIDE contacts: right edge, support under its bottom-right vertex, down-left-facing contact at its
top-right vertex, contact at its top-left vertex with normal pointing inward; the two walls, left
neighbours and top pressers never lock it; Lemma JAM-0; Theorem TF-U; Lemma ID + the certified 4-shallow
kill), docs/proofs/k0_route.md (K0-FREE, A58 crowding, K0-D4), attempts/A87-drain-flow/notes/
{k0blocked87,k0dir87,fjsecond87}.md (the data; the exit mechanism; flat strata), attempts/A44 (FJ index
identity m = 3k+1+sigma-d), docs/proofs/structure_lemmas.md (L1, L6), docs/known_results.md 16a.

## T1 — Theorem NOCRIT (state at drain-v3 rigor; name every obligation)
Statement to aim for: a packing of 11 unit squares in [0,s]^2 that is K0-BLOCKED is not a Fritz-John
point of the enclosing-side function (at any s; if you need s <= s-hat or s < 4, say so and prove the
restricted form). Equivalent target: sigma has no critical point in the interior of K0-BLOCKED, so the
infimum over K0-BLOCKED is attained on its boundary (a corner becomes K0-FREE), whence by K0-FREE +
the k >= 1 kills every selected k0 minimiser is K0-FREE — k0_00 dies with NO tree.
Route to try first (the data's mechanism): in each blocked corner take the SHALLOWER intruder Q (second
blocker). Show Q cannot be flush-locked at an FJ point when all four corners are blocked: by Lemma MENU
its locking contacts are far-side; count what can supply far-side locks to eight blockers (the three free
squares + other blockers) against the contacts an FJ point can carry (A44 identity; L1 degree >= 2;
per-wall <= 3; Lemma H-LOC) — a counting/pigeonhole argument is the hoped-for shape. Then TF-U (an
unlocked square has tilt exactly 0 at the selected minimiser) + JAM-0 (an axis-aligned offset blocker
pins its partner within arcsin(g) of flush and depth <= g^2/sqrt(1-g^2)) + the slide: an unlocked
axis-aligned intruder slides toward the corner at constant side until it is simple (k >= 1) or its
partner is freed (K0-FREE). Treat explicitly: (a) the case where Q is a rattler; (b) the Trump TL
configuration — your argument must NOT exclude it (it has three slot corners; identify exactly which step
uses "all four corners blocked"); (c) the flat strata (A87: 148/167 FJ points have Hessian identically
zero on the flex space) — criticality is first-order only, do not use second-order sufficiency; (d) the
tolerance law (a tangency is not a block; open-slot intrusion). If NOCRIT fails, produce the obstruction
explicitly: a K0-BLOCKED FJ point (give it as an exact configuration with multipliers, and verify it with
k0blocked87.py + fjpolish87.py) — that is a full success too, and it fixes the residue's true shape.

## T2 — composition and Lean-readiness
If NOCRIT holds: write the composition k0_00 = DF-K0 (drain to a stratum boundary) + NOCRIT (no
stopping point inside K0-BLOCKED) + K0-FREE (teleport) + k >= 1 kills, with the well-foundedness clause
for flat strata (slide along the plateau to its end; A87's plateau-end data: every flex endpoint is k >= 1
or K0-FREE). State which TopLevel axiom it discharges (stratum_kill's k0_00 piece) and what hypothesis it
adds (the selection clause: Phi-minimal per TF-U, or the drain selection). Lean-readiness note only.
If NOCRIT holds only under a restriction (s < 4, or "no rattlers", or "depth >= delta"), state the
residue exactly and price it against A85's tree with A89's shallow-corner certificate and depth prune.

## T3 — empirical checks (Opus chore under your definitions; exact where possible)
On the 520 k0dir87 flows and their 26 polished endpoints: at the exit event, identify the sliding blocker,
confirm it was the shallower intruder, confirm it was NOT flush-locked per Lemma MENU (list its active
contacts and their sides) and that no far-side contact was available; on the 4 endpoints that stayed
K0-BLOCKED and are not FJ, compute the certified Gordan descent direction and show it moves the shallower
intruder. On Trump: list the far-side locks of sq4 and sq6 (the theorem's boundary case). Canary: Trump
must be reported as critical with a locked TL 2-crowd.

Constraints: <= 2 processes, BLAS-pinned, headroom > 6 GB; A57/A60/A61/A86 untouched; frozen verifiers
untouched; writes in attempts/A90-nocrit-blocked/, docs/proofs/nocrit_k0_blocked.md, depgraph C.K4TIER
note (chip -> A90 once A89 releases it; pull/merge), registry row, LOG.md. Report tersely: NOCRIT status
first (proved / restricted form + residue / obstruction), then the composition, then pointers.
