# A213b -- the same treatment for the rectangle-obstacle clip (2026-09-14). Opus. LAUNCH-AND-EXIT.
After A213 the profile of the Y0202 pad-0 run is: `_clip_rect_obstacle` (A131 pinclip, Fractions) 747 of 955 s.
Do to it what A213 did to polycore: read attempts/A131-pin-clip (pinclip.py, READ-ONLY) and A171's multibox call
sites (_clip_rect_obstacle, bisect_region, clip_all, no-room's bisect_free); write code/pinclip_int.py (integer sign
tests over the common denominator, homogeneous coordinates, bit bound written down; Fractions only at the boundary;
a float filter with a rigorous error bound + exact fallback as Phase 2, default off), wire it into mbpatch213 behind
`A213_INTCLIP` (default ON only after the differential test passes with 0 mismatches), differential-test by replaying
every clip of the recorded run (fastclip211's clip memo records (obstacle, tilt bin, rect) -> result) plus a fuzz,
re-profile the same run (isolated dirs) and report per-call / per-run before/after.  Ops as A213's brief (never edit
the READ-ONLY libraries; workers untouched, they pick it up per node; explicit-pathspec commits; no monitors, no
waiting turns).  notes/int_clip.md, results/timing213.md appended, LOG entry.  Report once and EXIT.
