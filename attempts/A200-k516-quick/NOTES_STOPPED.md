# A200 STOPPED by the coordinator on the PI's instruction (2026-09-10 16:50)

The fast-phase certificates for the k5_16 pages are the deliverable and stay (certs/, results/quick200.jsonl,
docs/residue_map/quick200_fast_*.svg via live200).  The slow phase (SEAL at 300-600 s per corner, deep pair tests at
900 s per survivor) is DEFERRED: the PI wants every closed-form constraint inside a 30 s stage 0 with the page drawn
before anything slower (A202 fast30), and the exact cell-pair exclusion (A201) before any branched leaf.
Its worker processes were stopped at 16:50 (Y1022, Y0991, Y0491, Y1110 chains in flight; their rows are absent or
partial).  Do not relaunch.  Successors: A202 (stage 0 + stage 1), A201 (exact pair table), then the leaves.
