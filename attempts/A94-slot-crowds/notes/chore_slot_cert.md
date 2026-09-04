# A94 chore — SLOT-CROWD certificates for the pinned classes k5_11 / k5_16 (exact definitions + run order)

Lead: Fable (A94). Executor: Opus (one compute chore). This file is a DEFINITION and a RUN ORDER;
the soundness lemma (Lemma CW-S) and the transfer lemma (Lemma B-YES-S) are proved in
`docs/proofs/slot_crowds.md` §3; the chore must implement exactly these objects. A92's crowd code
(`attempts/A92-blocked-side/code/{crowd92,crowdfam92,lpbox92,caselp92,certify92,report92,smoke92}.py`)
is the base: COPY it (and the rest of A92's engine copy, incl. the frozen `verify_case.py`, sha256
521cb01f…, byte-identical, never edited) into `attempts/A94-slot-crowds/code/` and modify the copies.
Nothing under A57/A60/A61/A86/A92/A93 is written; A92's chore is RUNNING and holds one LP slot — do
not read its `results/nodes` or `certs` either (its report is fine). A57's `code/tree57.py` may be
READ for `hyp_from_slots` / `--pin_delta` semantics (copy the function; do not import A57's tree).

## 0. What the certificate says (Lemma CW-S, proved in slot_crowds.md §3.3)

Class S with pins P_S (k pins at slots, s-affine with beta in {0,1}), N = 11 - k free squares.
Certificate CS(S; s, m_lo; delta, e) at fixed side s for the window [m_lo, s): ONE measure mu on
[0,s]^2, verified by 1 + r_max runs of the frozen verifier:

  run A   : mu(Q) >= 1 for every admissible closed unit square Q that meets no PIN CORE K_j
            (cores = the k slot squares at side s, axis-aligned, half-side 1/2 - rho), and
            mu(total) < budget = N + 2 m_u e                                             (A)+(C)
  run B_r : mu(Q) >= 1 + r e for every admissible core-free Q meeting >= r of the widened slot
            families F_p(a_w), p in U_S (r = 1 .. r_max)                                 (B_r)

Composed: a packing of class S at side m in [m_lo, s) (exact pins at slots(m)) in which every
usable slot p in U_S is met, at depth >= delta, by >= 2 non-pin squares, dilates (Delta_lambda,
lambda = s/m, centres only) to a strictly disjoint family at side s whose k pin images contain the
cores (Lemma B, pin slack rho >= (lambda-1) A_S) and whose N non-pin images Q' are core-free with
r(Q') = #{p : Q' in F_p(a_w)} incidences, sum_Q' r(Q') >= 2 m_u; so sum mu(Q') >= N + e * 2 m_u >
mu(total): contradiction. m_u = |U_S| = the USABLE unclipped completable slots (those whose
extension class S u {p} is dead on the whole window, `results/slots94.json` field `usable`).

## 1. Constants (exact rationals; all roundings in the SOUND direction = UP for rho and a_w)

* s0 = 969271/250000; G2 = 965601/250000 = 3.862404; G3 = 192389/50000 = 3.847780;
  G4 = 958303/250000 = 3.833212; m_floor = 191/50 = 3.82; s-hat = 3.877083590022814.
* window (s, m_lo): lambda = s/m_lo. A_S = max over pins of |alpha|_inf (alpha = the s-free part of
  the slot coordinate; k5_11 and k5_16: A_S = 3/2).
* PIN SLACK rho := (lambda - 1) * A_S, rounded UP to 1e-5, then + 1e-5 (strict containment, Lemma B (H)).
  Cores in EVERY emitted certificate file: kx, ky = slot_j(s) exactly, tm = 0, a = 1/2 - rho (rational).
  In the LP node (caselp Hyp) the pins are Boxes of half-width h = rho/sqrt2 rounded UP (caselp
  derives a = 1/2 - h*sqrt2); check the emitted a against 1/2 - rho and assert a <= 1/2 - rho.
* WIDENED family threshold, per slot p = cell (i,j) of corner c:
      a_w(p, delta) := lambda (1 - delta) + (lambda - 1) (7072/10000 + max(i, j)),  rounded UP to 1e-5.
  (You may use the max over U_S, i.e. max(i,j) = 1, for all slots — sound, slightly conservative.)
  Require a_w < 1 for every run (else skip the (window, delta) pair and record "a_w >= 1").
* Check values (max(i,j) = 1):
  | window | lambda - 1 | rho_min | a_w(0.30) | a_w(0.20) | a_w(0.10) | a_w(0.05) | a_w(0.03) | a_w(0.02) |
  | (s0, G2)    | 3670/965601 = 0.0038007 | 0.00571 | 0.70915 | 0.80953 | 0.90991 | 0.96010 | 0.98018 | 0.99022 |
  | (G4, 3.82)  | 3303/955000 = 0.0034586 | 0.00519 | 0.70808 | 0.80843 | 0.90878 | 0.95920 | 0.97927 | 0.98930 |
  | (s0, 3.82)  | 14271/955000 = 0.014943 | 0.02242 | 0.73597 | 0.83746 | 0.93896 | 0.98971 | >= 1    | >= 1    |
  | (G3, G4)    | 3642/958303 = 0.0038005 | 0.00571 | (as (s0,G2) to 5 places) |
  | (G2, G3)    | 3656/961945 = 0.0038006 | 0.00571 | (as (s0,G2) to 5 places) |
  Recompute exactly; these are for cross-checking your code, not to be pasted.
* BUDGET: run A's n field = 11 + 2 m_u e with e chosen so that this is an INTEGER; budget = n - k =
  N + 2 m_u e. With m_u = 4 (both classes): e in {1/8, 1/4, 1/2, 1} -> n = 12, 13, 15, 19, budget
  7, 8, 10, 14.
* SLOT FRAME of p = cell (i,j) of corner c at side s: (x', y') = (u - i, v - j) with (u, v) = corner
  c's frame (u = x or s - x for BR/TR; v = y or s - y for TL/TR), theta' = theta for BL/TR frames
  and 90 - theta for BR/TL frames (exactly `o3run.corner_depth_table`'s t -> (1-t)/(1+t) rule).
  f_p(Q) := corner85.f_min_max(cx', cy', t') — the SAME function as A92 (min over Q of max(x', y')),
  valid for ANY centre (no quadrant assumption; f is nondecreasing in cx', cy' and (sqrt2/2)-
  Lipschitz in theta everywhere).  F_p(a) := {admissible poses at side s : f_p <= a}.

## 2. The classes and their usable slots (`results/slots94.json`, exact; recompute in your code)

| class | pins (s0) | N | unclipped completable slots -> extension (window status) | U_S (usable) | m_u |
|---|---|---|---|---|---|
| k5_11 | (1/2,1/2) (1/2,3/2) (3/2,1/2) (1/2,s-1/2) (s-1/2,1/2) | 6 | BL(1,1)->k6_18 FULL; BR(0,1)->k6_20 FULL; TL(1,0)->k6_20 FULL; TR(0,0)->k6_23 PARTIAL to 3877/1000 | BL(1,1), BR(0,1), TL(1,0), TR(0,0) | 4 |
| k5_16 | (1/2,1/2) (1/2,3/2) (1/2,s-1/2) (s-1/2,1/2) (s-1/2,s-1/2) | 6 | BL(1,0)->k6_23 PARTIAL to 3877/1000; BR(0,1)->k6_29 FULL; TR(0,1)->k6_30 FULL; TR(1,0)->k6_28 FULL; BR(1,0)->k6_27 OPEN; TL(1,0)->k6_27 OPEN | BL(1,0), BR(0,1), TR(0,1), TR(1,0) | 4 |

(k6_23's window ends at 3877/1000 = s-hat - 8.4e-5; the composition absorbs the sliver, see
slot_crowds.md §5. If A61 converts k6_27 during the chore, k5_16 gains BR(1,0), TL(1,0): m_u = 6 —
do NOT assume it; read `attempts/A56-sparametric/results/scoreboard.json` at start-up and use
whatever is FULL then, recording the scoreboard's mtime.)
Slot boxes at side s: centre = slot(s), half-side 1/2. The backed vertex of B_p is its vertex nearest
corner c (= the slot-frame origin).

## 3. Families (adapt `crowdfam92.py` -> `slotfam94.py`)

* G_p ⊇ F_p(a_w): the A92 staircase construction IN THE SLOT FRAME of p, with the centre grid
  extended to frame coordinates [-1, a_w + 3/4]^2 (step 0.02; a non-exempt pose meeting the box can
  have centre coordinates down to about -(sqrt2/2 + 2 rho) because it may graze the backing pins'
  rho-shells; the down-set/staircase logic is unchanged since f is monotone everywhere). Same theta
  bins (o3fam's seven, sigma-closed), same exact disjointness test with the Lipschitz pad, same
  1e-8 inflation. One staircase per (p, bin).
* r-count of a pose: r_F(Q) = #{p in U_S : f_p(Q) <= a_w(p)}. r_max := m_u (or the largest r for
  which G_r is non-empty on the grid).
* E_r (the exempt set of run B_r, r = 1..r_max): on the ABSOLUTE 0.02 grid of [0.45, s-0.45]^2 per
  theta bin, classify every cell by its NON-DISJOINT SLOT SET N(cell) := {p : the cell is NOT provably
  disjoint from F_p(a_w)} (exact test in frame p on the frame-image of the cell — its frame-lower-left
  corner and the mapped bin; the lower-left corner in the frame is a DIFFERENT absolute corner for
  reflected frames — compute it, do not assume). E_r := the cells with |N(cell)| <= r - 1, merged
  along x ONLY between cells with IDENTICAL N(cell) (so every merged box is provably disjoint from all
  F_p except the <= r-1 slots in its N — the property run B_r's soundness needs). Emit as caselp NoFam
  boxes (rect x the bin's t-interval) exactly as A92 did. Assert per box, exactly (Fractions).
* Diagnostics as A92: overshoot of G_p over F_p by exact sampling (aim <= 15 %); count of E_r boxes;
  the multiplicity histogram of r_F over a sample (expect r up to 4 near the container centre for
  k5_11: an axis-aligned square centred near (2.44, 2.44) meets all four widened boxes).

## 4. The LP (adapt `crowd92.py` -> `slotcrowd94.py`; `lpbox92` hooks unchanged in kind)

* Node: side s (a PARAMETER: solve_node(s, ...); S_RAT per run), Hyp(boxes = the k pin Boxes of
  half-width h, nofams = []), budget = N + 2 m_u e, sym_kind = "C1" (k5_11 has the transpose
  symmetry x<->y but do not rely on a Z2 quotient unless lpbox92 already supports it exactly; C1 is safe).
* rhs(Q) = 1 + e * r_G(Q), r_G(Q) = #{p : (centre, theta) in the DILATED G_p in frame p} (A92's GTest
  per frame; dilation 0.02 / 1 deg as A92 — conservative direction: more rows at higher rhs);
  RHS_MAX = 1 + e * r_max; RHS_CELL = cells meeting the dilated union of the G_p.
* Warm pool: A53/A54 node files for the class (`attempts/A53-simple-strata/results/nodes/<name>*.json`,
  `attempts/A54-stragglers/results/nodes/<name>*.json`, `_state` checkpoints), atoms rescaled to side s
  by s/s0 about the origin, capped at ~2500 columns. Do NOT read A57's results (running campaign).
* lp_time 900 s (raise to 1500 s for a re-solve of a node that ended within 0.05 of budget), max_iter
  900, prune_cols 3, col_stop_cov 1.002, as A92. Cache solved nodes in `results/nodes/<tag>.json`.
* PASS criterion: tau < budget. Record tau, eta = tau - budget, minmass, maxcov, rows, lp_s, atoms.
* REGRESSION (run first, once per class, cheap): e = 0, exact pins (rho = 0, A57's eps-fat cores),
  side s0, no crowd hooks -> tau must reproduce the class root value (k5_11 ~ 5.905-5.910, k5_16 ~
  5.973, A54 W3 / A57 T4) within the warm-start tolerance; record it.

## 5. Certification (adapt `certify92.py` -> `certify94.py`)

* run A file: cores = the k pins (kx, ky, tm = 0, a = 1/2 - rho exactly), nofams = [], n = 11 + 2 m_u e,
  budget = n - k, atoms + weights w, s = s (rational string). PASS iff rc = 0.
* run B_r file (r = 1..r_max): same atoms, weights w/(1 + r e) exact, same cores, nofams = E_r,
  n = 1000, budget = 1000 - k (dummy). PASS iff rc = 0.
* ALL files through the frozen `verify_case.py`, --depth 56 --jobs 1 (VERIFY_JOBS_CAP = 1, A57 T19);
  witness feedback: the witnesses of EVERY run fed back into the same weighted re-solve, 2 rounds;
  auto scale cap 1.4; eps_geo repair 0.002 / 0.004 on a FAIL (A85/A92). `<tag>.PASS` written only if
  ALL 1 + r_max runs pass. Record sha256 of every file.
* One measure: assert run-B_r weights are EXACTLY run-A weights / (1 + r e) (smoke test as A92).

## 6. Canaries (before any LP; refuse on failure)

* IMAGE gate (A92's `images_realizing` generalised): none of the 8 Trump images (dilated to side s)
  contains an axis-aligned square within h of EVERY pin slot of S at side s — for k5_11 and k5_16 this
  is trivially true (Trump's TL corner is clear: TL depths 0.168/0.155, nothing within 1e-2 of the TL
  slot); print the per-image pin-hit counts and assert none realises the pin hypothesis. Post-check
  after every PASS as A92 (exit 9 on an engine bug).
* TRUMP SLOT CANARY (lead's `results/trump_canary94.json`, exact): the six unclipped completable slots
  of trump5 each have EXACTLY 2 free meeters on the exact Trump, second depths 0.016049 (BL(0,2)),
  0.280083, 0.252050, 0.264033, 0.305293, 0.155475 (TL(0,0)). Recompute with your f_p in the slot
  frames on `attempts/A03-upper-reconstruct/trump11_exact.json` and assert agreement to 1e-9 — this
  validates the slot-frame maps (reflections, theta mapping) before they drive the rhs.
* REGRESSION of §4 (e = 0 reproduces the class root tau).
* A57 CONSISTENCY (read-only, cheap): A57's G1 records are s0 slack-core tree kills of the SAME classes;
  nothing in a PASS here may claim anything at side > s (state this in the log); no A57 file is read.

## 7. Run order (one LP at a time; free COMMIT > 6144 MB on TWO consecutive 60-s readings before every
## LP and every certify; at most 2 processes incl. this driver; BLAS pinned to 1 thread by blas1)

Phase 0 (exact, minutes, no gate): slots census, Trump canary, families for every (window, delta)
below, image gate, regression LP (this one needs the gate).

Phase 1 — the deciding runs, in THIS order (stop a (class, window, delta) at its first passing e;
e order 1/2, 1/4, 1, 1/8):
  1. k5_11, window (s0, G2), delta = 0.05, then 0.02, then 0.03, 0.10, 0.20, 0.30.
  2. k5_16, window (s0, G2), same deltas.
  3. CERTIFY the smallest passing delta of each of 1 and 2 (and, if time, the largest).
  4. k5_11 then k5_16, window (G4, 3.82): delta = 0.04 (kills the whole slab), then 0.02, 0.10.
  5. CERTIFY the smallest passing delta of 4 per class.
  6. k5_11 then k5_16, window (s0, 3.82): delta = 0.05, 0.10.
  7. chain sides if 1/2 and 4 passed: (G3, G4) at delta = 0.025, 0.02; (G2, G3) at delta = 0.014,
     0.012 (a_w < 1 needs delta > 0.0105 there).
  8. CERTIFY anything passing in 6-7, smallest delta first.
Wall budget 480 min (`--minutes 480 --reserve_min 150 --lp_time 900 --cert_time 300`), resumable
(node cache); write `results/CAMPAIGN_DONE` (status json) LAST, as A92's driver does.

## 8. Outputs

`attempts/A94-slot-crowds/{code,results,certs,logs}`; `results/slotcrowd94_runs.jsonl` (one record
per LP and per certification: class, side, m_lo, lambda, rho, delta, e, a_w per slot, U_S, m_u,
n/budget, G boxes per slot, E_r box counts, overshoot, canary counts, tau, eta, minmass, maxcov,
rows, lp_s, verdicts A/B_r, cert_s, sha256s, eps_geo used); `notes/slotcrowd94_report.md` (generated
by `report94.py`, also on a crash) with: per class x window the table delta -> (e, tau, eta, verdict,
certified?), the SMALLEST certified delta per (class, window) and the smallest LP-passing delta, the
family statistics, the canary tables, the resource discipline used, and every deviation from this
spec. Report to the lead tersely: per class, per window, the largest and the smallest passing delta
(LP) and the smallest CERTIFIED delta first; then tau/eta/minmass rows; then pointers.
