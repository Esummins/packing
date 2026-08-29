# A44 — the FJ-Maxwell bound: prove or refute (Fable lead)

Goal: settle the single biggest unproven census multiplier (A43 lever 1): a certified row-count /
flush-count lower bound for the support structures of FJ-critical configurations. If proved, it is
worth ~x1e4 on the grain census (A43-H1's conditional column); if refuted, that column dies
honestly.

Context: docs/proofs/structure_lemmas.md (Soundness ledger: the naive Maxwell |rows| >= 3k+1 is
SOFT — degenerate structures may jam with fewer INDEPENDENT rows; L1 degree >= 2, L2 thin, L3
self-stress branch, L6 chain are the proved local facts); docs/proofs/drain_lemma.md v3 (FJ per
selection, lambda0 branches); A37 atlas_final.json (THE TEST BED: 36 entries with certified
rank/contacts/self-stress — note VALLEYS exist: genuine critical points at rank 28-32 < 34, so
naive isostaticity is FALSE; any candidate bound must survive every atlas entry); A35/M1-M2
(Trump's 42-row v2 basis, wedge structure); A42 notes/structural_facts.md (F-facts).

Program: (1) refutation hunt FIRST — evaluate every candidate bound (total rows >= f(k); flush
count >= g(k); rows-per-loaded-square; chain-local versions) against all 36 atlas entries + Trump's
repaired basis; discard what dies. (2) For survivors, prove at T-quality: the natural route is
FJ + L6 + planarity: lambda0 > 0 forces e_s in the positive row cone; planarity caps point-contact
edges at 3(k+4)-6 single rows; count what positive spanning of the (3k+1)-dim... make the argument
rigorous or find the counterexample. Handle the lambda0 = 0 branch and valleys explicitly (a bound
that holds only for RIGID jams is still useful if stated conditionally — but label it). (3) If a
bound is proved: hand it to the census machinery (A43-H1 code) and measure the actual composed
kill factor at k=3..7 + the k=11 extrapolation. Honest refutation = success; quantify either way.
Constraints: mostly theory; Opus subagents for atlas evaluation + census re-run only; <= 3 heavy
processes (sharing with A45); ONE long-poll waiter; A29 untouched. Registry row, LOG, PI-readable.
