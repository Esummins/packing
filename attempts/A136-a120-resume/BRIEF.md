# A136 — resume the NO-side runner with the F-COVER fix: NO zones rounded inward, ZONE ⊆ BOX checked at emission on the written rationals, the 22 PASSing certificates re-certified, the 24 remaining targets processed (Opus)

Context (2026-09-07 evening). A120 (`5d0069a5`; attempts/A120-no-side-runner/notes/runner.md, results/) ran the local
certificate as the YES leaf of the region tree: 11 of 35 in-N nodes processed, 4 closed outright, 22 NO certificates
PASS under the frozen verify_param_v2, 24 targets and 17 open NO children left when A123's PAUSE sentinel stopped
it. Two things have changed since: (1) **F-COVER** (A126, A133 notes/fcover.md): the NO zone is rounded OUTWARD when
the certificate is written — in `attempts/A112-dual-branching/code/caselp.py::make_certificate`, `nofams=` clause:
`t_lo`/`t_hi` at TDEN = 2²⁴ with floor/ceil ± 1 extra unit, `q` at XDEN = 10⁹ nearest — so ZONE ⊄ BOX by 9·10⁻⁸ …
1.1·10⁻⁷ on ALL 22 certificates and the YES ∪ NO = H tautology (`LocalCompose.yes_or_no`) fails at that level; the
narrowest t-interval is 8.75·10⁻², so nothing collapses under an inward rounding; A120's own A6 guard checked the
exact zone, not the written one. (2) The scoped pause: `pausegate.paused(base=OWN_BASE)` at the consumer's call site
(A124, attempts/A57-shadow-trees/PAUSED.md v2 §7a) — do not delete A123's sentinel; run under your own base.

Also available now: A133's t-parametrised local certificates (attempts/A133-tan-half-emission/certs, sharper than
A119's; same N boxes) and A125's S33/S38 N_boxes (results/N_boxes.json, one consumer node c0_Y0335). Certifier
default: rounds 6, wall 2,600 s (A120's finding at the 0.3 % margin). Emission is nondeterministic: replay
certificates, never re-emit to reproduce a kill.

Read first: A120's runner.md + code (a120lib, run120), A112's caselp.py make_certificate (READ ONLY), A126's
LocalCompose.lean (the exact hypothesis of `yes_or_no`), A133's notes/fcover.md, verify_param_v2 (frozen — its
exemption clause reads the written zone), PAUSED.md v2 §7a, docs/budget.md §B.

## T1 — the fix, without editing A112 or A120
`a136lib.py`: a wrapper that post-processes the certificate dict returned by `make_certificate` BEFORE it is written:
every NO-zone bound rounded INWARD to the same denominators (t: ceil for lower / floor for upper at TDEN; q: same at
XDEN), the YES box bounds outward, and then the decidable check ZONE ⊆ BOX on the WRITTEN rationals (fail loudly). A
positive control: re-write A120's 22 certificates through the wrapper, confirm ZONE ⊆ BOX on all 22 and that the
change is ≤ 1.2·10⁻⁷ per bound; then re-certify all 22 under the frozen verify_param_v2 (240 s each; the LP part is a
re-solve — A120's protocol; 900 s only at a knife edge). Report PASS/FAIL per certificate.

## T2 — resume
The 24 remaining targets and the 17 open NO children, A120's queue order, two processes BelowNormal, under your own
sentinel base; every new NO certificate through the wrapper; the two-stage protocol (240 s → certify on η ≤ −1e-3;
900 s only at the knife edge); CAP is never a verdict. Cap 20 CPU-h. Kills reported as certified passes only; the
survivor-count line per node (drawn → tested → hits) for the sampled checks. Use A133's t-certificates for the YES
leaf where the N matches (say which); A125's N for c0_Y0335 if that node is in scope.

## T3 — the Lean hand-off
For each closed node: the list (YES N id, NO certificate ids, all with ZONE ⊆ BOX verified) in the format A126's
`LocalCompose.y0230_dead` consumed, so the closure is a Lean replay away; one line each in results/closures136.jsonl.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal (A134/A135 running; the PI is using the machine; count the box
first, stay ≤ 16 python processes total); READ-ONLY on every campaign and on A112/A120/A126/A133 files (new files
only under attempts/A136-a120-resume/); frozen verifiers byte-identical; never delete a sentinel or a pidfile; NO
recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths with explicit pathspecs.
Writes: attempts/A136-a120-resume/{code,notes,results,certs,logs}, attempts/A96-a57-parametric/results/
a120_closures.jsonl (append only), registry row, LOG.md, docs/budget.md A57 row's A120 clause (the closure count).
Report ONCE at the cap or when the queue is empty: T1's 22 re-certifications first, T2's closures second, pointers
last. No interim messages.
