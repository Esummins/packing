# A228 -- the pass-5 segfault on Y0402 pad 0 (2026-09-15 00:45).
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, at most ONE python of your own (BelowNormal, affinity 0xFFFF), never touch the
running workers (p5a on Y1056, p5b on Y0738, run212 w1-w3) -- they run the SAME flags, so fix fast and cleanly.

## The fact
attempts/A211-coarse-tree/logs/worker_p5a.log: the pad-0 run of k5_16_interior_Y0402 (flags A220_NOROOM_INHERIT=1
A221_LANE=1, wall 1800) died with "Segmentation fault" (rc=139) at t ~ 977 s, right after
   node R.3.4.p1   d1 pocket<-[0]: INTERNAL (24.3 s, 1 rounds; t=977.1)
(logs/coarsetree211_k5_16_interior_Y0402.log, the pad-zero segment starting at line 384); the certificate kept the
nodes up to R.3.4.p1.p1 (VACUOUS), so the progress is not lost.  The g1 run of the same page then ran to rc=0.
No other run has crashed (p5b clean; A220's bench ran without A221_LANE).  Suspects: (a) noroom221 / pocket221
(A221, new in pass 5: pocket-rooted depth-first clip -- deep Python recursion overflowing the C stack on Windows;
or the A214 C kernel (ctypes DLL) fed a value past its 192-bit bound); (b) the A220 short no-room cap path; (c) the
pocket instantiation at k=9, m=2 with 2 surviving pockets.

## Task
1. Reproduce: run the pad-0 page with the same flags from the same inherited state in an isolated cert dir
   (--cert-dir, --results, --no-fig, wall 1200) with `python -X faulthandler` so the crash prints a traceback; if
   it needs the exact start, load R.3.4.p1's snapshot (startload211 / inherit211) and run the leaf rules on it
   directly.  Identify the crashing call (faulthandler output, or bisect by disabling A221_LANE / A220 flags).
2. Fix: if recursion -- make it iterative or bound the depth with a sound fallback (UNDECIDED, never a verdict);
   if the C kernel -- the input guard (fall back to the exact Python path beyond the bit bound); if the pocket path
   -- the guard.  Keep the fix flag-neutral and sound (a crash-avoidance fallback may only return UNDECIDED).
3. Worker hygiene: worker211.sh records a row only for rc=137; add the rc=139 (and any rc != 0) row so a crash is
   visible in results/coarsetree211.jsonl and progress.md, and make the worker re-queue the pad (the page is re-run
   next pass anyway; at least log it).  Do not restart the running workers; new pages pick the fix up.
4. Verify the fixed code on the reproduction (runs past t = 977 s to the wall or a verdict) and on one closed page
   (verdict agreement).  Deliverables: the patch (pocket221.py / noroom221.py / worker211.sh as needed),
   notes/segfault228.md (cause, fix, evidence), registry row, LOG entry.  Report once (<= 10 lines) and EXIT.
