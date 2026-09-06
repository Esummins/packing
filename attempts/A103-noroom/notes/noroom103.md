# A103 notes — NOROOM (Fable theory lead, 2026-09-06)

Deliverable: `docs/proofs/noroom.md`. Verdict in one line: (A) closed only locally (Lemma TRUMP-LOCAL:
no K0-BLOCKED packing near a Trump image at side ≤ ŝ + ε₀; with uniqueness, m* > ŝ, ε₀ unquantified);
(B) reduces to RES-LOCK(m) = ∅ on W; (C) delivered: RES-LOCK = K0-BLOCKED + every intruder HELD (Lemma
ROT) + NOCRIT-SEL anchoring; no realisation on disk (12/12 corpus packings have an unheld second meeter,
Trump 5/5 held); the one fact = Conjecture LOCK-FREE(< 4).

## Chores (one process, seconds, pure geometry)

* `code/lock103.py all` — the first-order lock test (Gordan/LP per intruder, branch enumeration for the
  diagonal argmin points, finite-motion confirmation at eps = min(1e-6, g_min/10), room sweep).
  Output `results/lock103.{json,jsonl}`, log `logs/lock103.log`. 13 packings, 3 s.
* `code/trumplocal103.py` — numerical check of Lemma TRUMP-LOCAL (cover claim 29 254 poses, 0 fails;
  pair claim 11 000 valid pairs, 0 doubly-met BR). Output `results/trumplocal103.json`.
* `code/gen_lock103.py` — `results/lockmap103.svg`, the (C) drawing (record 3.98548 and floor-1e-3
  3.99075, intruders labelled HELD/UNHELD, unheld motions drawn, geometry-checked).

## Findings not in the doc's verdict

* The brief's rotation rule ("toward axis decreases Psi") is the vertex-argmin case only; for an
  edge-argmin D-type intruder with c_x ~ c_y the decreasing sense is toward the diamond
  (dmu/dphi = [(c_y - c_x) + (cos phi - sin phi)/2]/(cos phi + sin phi)^2).
* The brief's chain dichotomy (far end = slot square or intruder) has a third case, realised by Trump's
  own column sq4 -> sq7 -> sq8 -> sq1 (far end flush on the floor, tangent to BL, not an intruder).
* The brief's "regions are >= m - 2 - 2 sqrt2 apart" is negative on W: the home regions overlap; one
  free square braces all four corners (Trump's sq7).
* A102's contact-torque anomaly (screw-free second meeters that jam) is the second-order case of Lemma
  ROT: unheld at the 1e-7 bar, but the strictly opening motion ends on an inactive row at gap 1e-7..1e-3.
