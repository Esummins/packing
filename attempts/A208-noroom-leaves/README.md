# A208 -- NO-ROOM at every fully named clip-tree leaf (coordinator-run, 2026-09-11 15:35)
PI: "all of the alive leaves in Y0881 seem to have 10 pinned squares, so they should all die by no_room pretty quickly."
Check (scratch): Y0881's three alive leaves (10 roles each) DEAD by A189's bisection alone in 10 / 11 / 19 s; Y0738's
three: two DEAD (one by the pocket CN bound), one UNDECIDED (pocket at the right wall).  code/noroom208.py runs A189's
no-room leaf + the pocket CN bound over every ALIVE leaf with >= 9 roles in A205's and A206's certificates
(role boxes; sound, weaker than pieces); results/noroom208.jsonl.  Leaf kills are [C: A189 Lemma 1 (+ Lemma CN) on the
leaf's role boxes]; they close LEAVES -- a page closes only when its tree has no undecided branch left.
