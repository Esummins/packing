# cost281 part 6 -- THE COUNT: the f-table (code `count281.py`, results `count281.json`)

**Classes.**  A corner is T, Ff (flat on its outgoing wall, poker on its incoming) or Fw (the mirror); 3^4 = 81
assignments, 15 orbits under D4 (rotation; reflection reverses the cycle and swaps Ff <-> Fw).  Each orbit has its four
wall types (part 2).  Facts applied, with tags:
  SIDE   [T]  a wall of type PiPi is dead on W (TWO-POKERS).  No other wall type is dead by side (part 2 + part 7 witnesses).
  COUNT  [T]  FAMILY-STUCK: every slot needs a non-own meeter; on a PhiPi wall the poker's slot cannot be met by the
              flat (FLAT-ABOVE) nor by any other meeter (PROJECTION, SAME-WALL), so it needs a FREE square; every other
              slot is granted its ADJ supply (optimistic); the ring family needs a NINTH square: some wall with both
              slots met by free squares, or a free third box meeter (A258); a free square meets cells of ONE corner
              neighbourhood (PROJECTION), i.e. slots of the two walls at one corner only.
  +SEP   [M]  SEPARATE-NOTCHES (A248): no free square serves two poker notches.
  LOCKS  [T-prose, normal form] every wall is a common-tilt row or a locked open pair (chain link 7); PhiPi and Phi-tau
              walls are never rows; a lock serves at most the two walls of one corner (so #free >= ceil(#never-row / 2)).
  Free squares available: n - 8 = 3.

**The table** (h = least free squares by COUNT; h_sep with SEP; locks = ceil(never-row walls / 2)):
  f  orbit (BL/BR/TR/TL)   walls                              SIDE   h  h_sep  locks   survives [T]   survives [T]+[M]
  4  Ff/Ff/Ff/Ff (pinwheel) PhiPi PhiPi PhiPi PhiPi            ok     2   4      2       YES            NO (h_sep = 4 > 3)
  4  Ff/Ff/Ff/Fw            PhiPi PhiPi PhiPhi PiPi            DEAD   -   -      -       no             no
  4  Ff/Ff/Fw/Fw            PhiPi PhiPhi PhiPi PiPi            DEAD                       no             no
  4  Ff/Fw/Ff/Fw            PhiPhi PiPi PhiPhi PiPi            DEAD                       no             no
  3  Ff/Ff/Ff/T             PhiPi PhiPi Phi-tau Pi-tau         ok     1   2      2       YES            YES
  3  Ff/Ff/Fw/T             PhiPi PhiPhi Pi-tau Pi-tau         ok     1   1      1       YES            YES
  3  Ff/Ff/T/Fw             PhiPi Phi-tau Phi-tau PiPi         DEAD                       no             no
  3  Ff/Fw/Ff/T             PhiPhi PiPi Phi-tau Pi-tau         DEAD                       no             no
  2  Ff/Ff/T/T (adjacent)   PhiPi Phi-tau tau-tau Pi-tau       ok     1   1      1       YES            YES
  2  Ff/Fw/T/T (adjacent)   PhiPhi Pi-tau tau-tau Pi-tau       ok     1   1      0       YES            YES
  2  Ff/T/Ff/T (opposite)   Phi-tau Pi-tau Phi-tau Pi-tau      ok     1   1      1       YES            YES
  2  Ff/T/Fw/T (opposite)   Phi-tau Phi-tau Pi-tau Pi-tau      ok     1   1      1       YES            YES
  2  Ff/T/T/Fw (adjacent)   Phi-tau tau-tau Phi-tau PiPi       DEAD                       no             no
  1  Ff/T/T/T               Phi-tau tau-tau tau-tau Pi-tau     ok     1   1      1       YES            YES
  0  T/T/T/T                tau-tau x 4                        ok     1   1      0       YES            YES
Per f: side kills 3 of 4 orbits at f = 4, 2 of 4 at f = 3, 1 of 5 at f = 2, none at f <= 1.  COUNT alone kills NOTHING
(h <= 2 everywhere: A250's "the count does not close below 4" in role form); with SEP [M] it kills exactly the f = 4
pinwheel (A248's result, now placed in the table); LOCKS kill nothing (<= 2 everywhere).

**Reading.**  [T] Every surviving orbit contains a T corner except the f = 4 pinwheel, and the pinwheel survives only the
[T] layer: its four PhiPi walls need four free squares in four poker notches unless one free square serves two adjacent
notches, which SEPARATE-NOTCHES [M] forbids by 0.003.  So on W, **modulo one [M] margin, every k0 skeleton has a T
corner**, and the f = 0 case (the one-sense ring) survives every count with h = 1: the ribbon poker -- exactly the
structure ROOM excludes (the free square contains O: 8 + 1 < 11, A259/A260).  The f = 1..3 survivors are the HYBRID
pictures: F corners whose flat walls are locked pairs and whose poker walls are Pi-tau rows or locked pairs, with 1-2 free
squares as locks / notch squares and the ninth square; what closes them is ROOM on the hybrid family (A260 [T-computed]
at common tilt; the independent-tilt residue is the open 20 P2 cells) -- not any count.
**What the count DOES buy** [T]: a free square in a poker's notch (needed by every PhiPi wall) is a ribbon square of that
wall only if it also meets the flat's slot; part 7 checks on the witnesses whether the notch square can be the ninth
square (if never, every f >= 1 skeleton with a PhiPi wall needs h >= 2).
