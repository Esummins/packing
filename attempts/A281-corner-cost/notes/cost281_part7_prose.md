# cost281 part 7 -- computations (code `attempts/A281-corner-cost/code/`, results `results/`)

**Method.**  `geom281.py`: A249's parametrisation of every meeter (floor toucher A(th, d), wall toucher B(th, d); th = 0
is the flat) in each corner's frame, mapped to the container by the D4 frames; SAT gaps; the three border cells per
corner.  `wall281.py`: Nelder-Mead sup-margin (least of: pair gaps, containment on the untouched walls, own-box
incidence, tilt / offset windows, TILT-MIN sin th <= d for a poker beside its flat) with structured restarts and an
SLSQP polish of the slack form; then the witness is RATIONALISED (tan(th/2), d to 10^-7) and every constraint is
re-checked in Fractions (`exact_verify`): a witness is [T-computed] only if that passes.  An optimiser's negative sup is
[M] evidence (never a proof) except where a theorem already says so (Pi-Pi: TWO-POKERS [T]).  Independent cross-check:
A248's numpy `poly_gap` on the F^4 pinwheel at s-hat agrees (0.051943 = the reported margin).  `count281.py`: the
f-table (part 6).  `fslots281.py`: the F-SLOTS-ONE probe.  `pages281.py`: the page with a geometry note per panel.

**Readings.**
* Every wall pair type except Pi-Pi has an exact 4-square witness at BOTH ends of W (margins 0.06-0.10); Pi-Pi's best
  attempt is negative at both (TWO-POKERS): part 2's summary is confirmed.
* The poker's slot IS supplied by a T neighbour's wall meeter, with either global sense (`Pi-tau+ADJ<45`, `>45`), and
  by the row continuation (`Pi-tau+ROW`: the T-meeter also meets its own slot); the flat NEVER supplies it
  (`PhiPi+ADJ?` sup -0.00000: the sup is 0, attained only in the flat-above-flat limit y_0 = y_T, FLAT-ABOVE [T]).
  Phi-tau and tau-tau walls admit mutual ADJ supply (both slots served by the eight meeters).
* The all-F pinwheel (four Phi-Pi walls) EXISTS as an 8-square outer structure on all of W (C4-symmetric witness: flat
  offset d = 0.662, poker tilt 14.2 deg, y_V = 0.948 at s-hat; margins 0.045 / 0.052 at 3.82 / s-hat): A248's kill of
  f = 4 is a HOLDER kill (four notches, three free squares, SEPARATE-NOTCHES [M]), not a side kill -- part 6.
* The f = 3 orbit Ff/Ff/Ff/T exists on all of W (0.047 / 0.054).  The orbits with a Pi-Pi wall fail at both ends
  (sup -0.0003 .. -0.0004, the TWO-POKERS deficit at these sides being small: s* - s-hat = 0.057 is spent on the pokers'
  own tilt windows).  The remaining orbits: table 7.2 (rows still landing at exit are PENDING -- `finish281.sh` commits them; a class with sup <= 0 and no exact witness is UNDECIDED by side
  and drawn grey; the count of part 6 does not need side-realisability, it only needs the wall types).
