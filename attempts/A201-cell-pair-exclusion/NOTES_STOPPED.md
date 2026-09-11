# A201 STOPPED by the coordinator on the PI's instruction (2026-09-10 19:05)
"once a new agent has started actively checking [pages], kill the old checkers, since they're just slower and take
cpu space."  A203 (closed-form CSP: piece-level pair compatibility + H-consistency / mutual clip, stage 0) supersedes
A201's exact-bisection pair table as the running checker.  A201's results (results/pairexcl201.jsonl, certs/,
docs/residue_map/pairexcl201_*.svg) stay; its exact pair test remains the fallback for pairs the closed-form bounds
leave undecided, to be invoked from A203's chain when needed.  Do not relaunch.
