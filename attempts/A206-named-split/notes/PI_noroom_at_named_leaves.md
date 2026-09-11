# PI reading (2026-09-11 13:10), Y0738's surviving sharp leaves: "they only have 10 squares placed. I think if we mark
# all geo dead space, there's no space left for an 11th."

Coordinator's check with A189's NO-ROOM leaf on the leaf's role BOXES (scratch noroom_y0738.py):
- leaf R.1.1.2s.2.1.1.1s (9 roles: pins + H + F1..F3, m = 2 free squares needed): bisection leaves ONE pocket of free
  centres, [3.037, 3.440] x [2.920, 3.440] (the TR corner, where leaf ...2s puts F4); the lane cover returned None
  (UNDECIDED, 312 s).  But the pocket's diameter is 0.66 < 1, so by Lemma CN it holds at most ONE free centre:
  bound <= 1 < m = 2  =>  the leaf is DEAD.  (The pocket bound must be added to noroom's lane step: a pocket of
  diameter < 1 contributes lane <= 1 without any lane search; in general the lane of a pocket <= the max number of
  centres pairwise >= 1 apart inside it.)
- leaf ...2.1.1.2s (10 roles incl. F4 in that corner, m = 1): running -- if the bisection leaves no pocket, DEAD.

RULE for A206 (and every tree after it): at every fully hard-named leaf run the NO-ROOM leaf (A189) with the pocket
CN bound (diameter < 1 -> at most one free centre) BEFORE declaring "next lever: LP"; it is the PI's "mark all geo
dead space" step and costs ~300 s.  Kills are [C: library clip trace + A189 Lemma 1 + Lemma CN].

## Results on all three alive leaves of Y0738's R.1.1.2s tree (role BOXES, A189 defaults)
- ...2.1.1.1s (9 roles, m=2): one pocket [3.037,3.440]x[2.920,3.440], diameter 0.66 -> lane <= 1 < 2 -> DEAD by CN.
- ...2.1.1.2s (10 roles, m=1): DEAD by bisection alone, 17 s (every pose of a free square meets some core).
- ...2.1.2s   (10 roles, m=1): UNDECIDED: two adjacent pockets at the right wall, [3.205,3.440]x[1.574,1.893] and
  [3.273,3.440]x[1.437,1.609] (union diameter ~0.5 -> at most ONE centre = m, so CN does not decide); the lane returned
  None on boxes.  Re-run with the leaf's PIECES (bigger cores, esp. F3 / F1) and the lane; this is the only leaf that
  keeps Y0738 alive after the no-room step.
