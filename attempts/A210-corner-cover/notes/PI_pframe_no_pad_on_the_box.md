# PI reading (2026-09-12 01:50): state CORNER-COVER in the PACKING's frame; pad the CONTACT REGION, not the box
"this lemma is about forcing a square to be simple ... I'm not convinced that the simple unit square needs the pad.
Simple is simple at side length 1 regardless of s; the real question is whether the pad allows a square to reach the
valid second meeter positions near the walls."

Corollary CC' (replace the brief's corollary; prove before use):
 In P (side m in the window), a unit square Q1 within delta of both walls of the unpinned corner c, tilt t, covers the
 corner cell except the two wall wedges W(t, delta) (width <= h(t) - 1/2 + delta each).  The second meeter Q2 of the
 corner slot has a point in W(t, delta).  In F = the dilate (every square translated by (lam - 1) c_Q, lam - 1 <= 0.004
 on the G1 pages), Q2' has a point in W(t, delta) + (lam - 1) c_{Q2}: the wedges translated by <= (lam-1) S0 = 0.016
 along the direction of c_{Q2}, i.e. TOWARD the corner.  Hence Q2' centre lies within 1/sqrt2 of the wedges widened by
 0.016 along the walls -- the band along the two walls -- and NOWHERE ELSE.  There is no inner-corner margin disc: the
 inner corner is covered in P exactly, and the box pad never enters.  delta is read off Q1's pieces in F
 (max distance to either wall) plus (lam - 1) h(t).
So rule CC kills on the WINDOW pad exactly as at pad 0, with the wall band 0.016 wider.  If the pass reported window
survivors through the "margin disc", re-run with CC'.

General principle (memory): pad the contact region a lemma actually uses, never the whole box.
