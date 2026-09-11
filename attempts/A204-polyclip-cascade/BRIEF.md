# A204 -- the POLYGON-CLIP CASCADE to a fixed point on the k>=1 survivors of the geometric layers (READY; launch when
A203 reports; PI 2026-09-10 19:50: "a bunch of them are going to die once we move from the geo kills to the
clipping/polygon kills. I doubt any of these (maybe one) will survive through to LP.")

Model: Fable. Short responses, files in pieces <= 250 lines, no interim messages, commit after every page batch
(`git add -- <paths>; git commit -- <paths>`; fetch + plain merge only; never pull --rebase / autostash / reset; no
recursive deletes; PYTHONDONTWRITEBYTECODE=1; <= 2 processes, BLAS pinned to 1 thread, affinity 0xFFFF, BelowNormal;
lab ceiling 12 python processes EXCLUDING command lines containing "Claude Extensions"; 6144 MB commit gate; never
touch other campaigns' state or the frozen verifiers). Agent messaging is broken; report ONCE at the end.
Pages: docs/residue_map/campaigns/A204-polyclip/polyclip204_<nid>.svg (+ polyclip204_gallery.svg) -- the binding
layout in docs/residue_map/README.md; set docs/residue_map/CURRENT.json to A204 (A203's pattern kept as fallback)
and run docs/residue_map/refresh_current.py after every batch.

## Order of stages (PI directive; never run a slower stage before the faster one's page exists)
stage 0  A202/A203 closed-form layer (<= 30 s per pad) -- DONE for every page; take its survivors and its clipped
         H box / forced slots / instantiated roles as the starting node (certs in attempts/A203-csp-consistency/certs,
         results/csp203.jsonl; fall back to attempts/A202-fast30/certs).
stage 2  THIS campaign: the exact polygon-clip cascade (A171 multibox library at/after 13f23204, A172 per-piece K',
         A173 lonely clip, A175/A181 polygon-obstacle clip with parent seeding, A182/A180 assignment with unit
         propagation, A189 no-room leaf), coarse only (nsub 4 / refine 2), order D->S->B where roles exist, forced
         meeters instantiated as roles (Theorem FC), every clip re-run on the PIECES so K' grows on the far side and
         clips neighbours harder (memory: geometry-before-lp), iterated to a FIXED POINT.  A page after EVERY round
         (drawing rules: hypothesis squares only at admissible poses, pins as pins, undecided grey stipple never
         green, a note saying what the panel IS, seconds per round).  Wall 900 s per pad per page; both pads
         (g1 = the page's window, then pad 0 = s0-only, WINDOW-PENDING).  NO LP, NO branched tree in this campaign.
stage 3  (not yours) the branched tree / LP on whatever survives, with A201's exact pair test and A203's CSP.

## Deliverables
results/polyclip204.jsonl (one row per nid x pad: verdict, killing leaf, rounds, seconds per round, kept fractions
per role, verifier label [C-v4]/[C-v5] where a verifier applies, else [C: library clip trace]); certs/; pages;
notes/polyclip_cascade.md (what died at which round by which clip, the survivors' state with the next lever, the PI
credited for the prediction and for geometry-before-LP); registry row, LOG entry, docs/residue_ledger.md section 4,
docs/budget.md item, status gallery collector block for kills; PAUSED.md fold-in for survivors.
