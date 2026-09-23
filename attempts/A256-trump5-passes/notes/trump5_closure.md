# A256 -- the TRUMP5 CLOSURE ACCOUNT: what it would take to make trump5 a full-window row (2026-09-21)

Labels: **[T]** proved, **[T-computed]** proved modulo an exact certificate on disk, **[M]** measured here,
**[C]** open.  Every link names its file.  The account answers the brief's question -- *is the seam closed?* --
with: **no, and the blocking link is not the seam but the pin slack of A60's records** (s.4, O1).

## 1. [M] The rebase decision (why A256 has no chain of its own)

A212 froze a COPY of A211's chain at `b06a8203`; A211's chain has since gained A220 (exact-first, NOROOM_INHERIT),
A221 (lane), A224 Rule SNAP, A228's guards, A229's `--start` / `--cert-suffix` shards, A230 Rule EPS.  Diffing
A212's copy against A211 at `b06a8203` (ignoring line endings) shows the trump5 work touched exactly **three**
files, two of them by **one line**:

| file | the trump5 change |
|---|---|
| `load211.py` | +48 lines: A60's frontier records answered by `FP.load_page` (`a60_record` / `a60_rows` / `a60_page`) |
| `stage209.py` | `c["roles"]["H"]` -> the first `H*` key (f1_L10_0003's 2-H record) |
| `poly204.py` | the same one line in `load_start` |

So A256 **rebases**: `code/run256.py` pre-imports those three files (plus `inherit211`, which only adds A212's
certificates as a merge source) under their real names and then runs **A211's own `run211.py` verbatim**
(`runpy`).  The chain is not forked a second time and every lever the k5 loop gained applies to trump5 for free.
Verified end to end (`logs/trump5passes256_c0_Y1033__zero_R.4.log`): stage 0 reused from A212's certificate,
Lemma INHERIT merged A212's tree (4 dead paths, 7 start nodes), the A229 shard filter fired, A220/A224 flags on.

## 2. [T-computed] The chain as it stands

| # | link | status | file |
|---|---|---|---|
| L1 | Trump's packing z-hat at s-hat = 3.877083590022814, 60 digits, rational centre, \|z-hat - z0\| <= 1e-50 | **[T]** | `attempts/A03-upper-reconstruct/trump11_exact.json` |
| L2 | z-hat is strictly locally optimal; A22's handover box r_N = 1/2000 | **[T]** (Lean, A79) | A22 / A70 / A79 |
| L3 | the trump5 stratum at s0 = 969271/250000: 5 corner pins {0,1,2,3,5} + H, A60's residual tree | **[T-computed]** | `attempts/A60-trump5-campaign/` |
| L4 | A60's 49 PASS (K) leaves | **[T-computed] but s0-ONLY** | `attempts/A60-trump5-campaign/notes/ledger.md` s.1 |
| L5 | A60's alive frontier (136 records) + 13 alive gallery pages = **149 trump5 nodes** | **[M]** | `attempts/A212-trump5-tree/results/trump5tree212.jsonl` |
| L6 | A212's pass 1, pad 0 only, one 1,800 s wall each: **65 DEAD, 84 ALIVE**, gate_root False and gate_hits 0 on all 149 | **[M]** | same file; `attempts/A212-trump5-tree/notes/trump5_tree.md` |
| L7 | the contraction tube: Theorem T1, 12 exact certificates, 289 checks, 0 failures, 10/10 gates | **[T]** | `docs/proofs/contraction_tube.md` s.1, `certs/verify_tube.py` |
| L8 | Lemma SEAM: T' = min(T_tube, T_K(delta_pin)), T_K(d) = ((2/3) d s-hat - (s0 - s-hat))/(1 + (2/3) d), A = 3/2 | **[T]** | `contraction_tube.md` s.4.1 |
| L9 | **Lemma TUBE-KILL** (s.3 below), implemented + verifier | **[T]**, domain empty here | `code/tree256.py`, `certs/verify_tubekill256.py` |
| L10 | A256 pass 2+: the 84 alive nodes re-run at pad 0 with A220/A221/A224/A228/A229/A230 | **running** | `results/trump5passes256.jsonl`, `results/progress.md` |

## 3. [T] Lemma TUBE-KILL -- the tube theorem used as a KILL (the (D) leaf near t = 0)

*Setting.* N is a node of the trump5 residual tree at a **window pad** with dilation bound lam_pad, i.e. the slab
(s_bot, s0], s_bot = s0/lam_pad; T' := s-hat - s_bot.  N's hypothesis: there is a packing P of eleven unit squares
at some side m in (s_bot, s0] whose class pins are trump5's five corner pins -- so each pinned centre coordinate is
**exactly** slots(m) = alpha + beta m, |alpha| <= 3/2 -- and whose dilate F = Delta_{s0/m} P satisfies N's pieces.

**Lemma TUBE-KILL.**  Suppose
 (i) all eleven squares of N are named (5 pins + H(s) + instantiated roles; no anonymous square);
 (ii) there are g in D4 and an injective assignment of N's named free roles to the free squares of g.z-hat such that
   every piece of every named free role lies inside the box of half-widths (r_c - 2(s0 - s-hat), r_theta) about its
   assigned square, the pins being matched to g.z-hat's pins corner by corner;
 (iii) a **slot-ray** tube certificate with trump5's pin set {0,1,2,3,5} and r_s = 0 passes `certs/verify_tube.py`
   at (T, r_c, r_theta) with **T >= T'** -- `certs/tube_slot_T4.5e-2_landing.json`: T = 9/200, r_c = 1/625,
   r_theta = 21/10000;
 (iv) Lemma SEAM's (K) condition **T_K(delta_pin) >= T'**, delta_pin the pin-core slack of N's own record.
Then **no packing satisfying N exists at any side m < s-hat, and at m = s-hat the only one is g.z-hat.**

*Proof.*  Fix such a P at side m <= s-hat and put t := s-hat - m in [0, T'].  Pull back per coordinate exactly as
`contraction_tube.md` s.4.1: a **pinned** coordinate is alpha + beta m = z-hat_i - t v_i with **w_i = 0** (v =
slot(pins), s.1.1); a **free** centre coordinate is F_i/lam with |F_i - z-hat_i| <= r_c - 2(s0 - s-hat) by (ii), and
z-hat_i m/s0 = z-hat_i - t z-hat_i/s-hat - z-hat_i(1 - t/s-hat)(s0 - s-hat)/s0, so |w_i| <= r_c; **tilts** are
unchanged by a dilation, |w_theta| <= r_theta by (ii); the **side** is m = s-hat - t, so **w_s = 0**.  Hence
g^{-1}P in Tube_slot(T', (r_c, r_theta, 0)) at depth t.  (iii) gives T >= T', so Theorem T1 (s.1.1-1.2) applies:
z_s >= s-hat with equality only at z-hat.  Therefore m >= s-hat, i.e. m = s-hat and g^{-1}P = z-hat.  (iv) is what
makes N's own hypothesis available to F at s0: by Corollary B' (s.4.1) F's pin squares contain the delta_pin-slack
cores at slots(s0) iff (lam - 1)A < delta_pin with A = 3/2, which is T_K(delta_pin) >= T'.  []

*What the lemma does NOT say.*  Nothing about m in (s-hat, s0]: that sliver lies **above** the target side and is
irrelevant to s(11) >= s-hat.  A TUBE-KILL leaf is therefore recorded as its own verdict, not as DEAD.
At **pad 0** the same containment is only Lemma TUBE-LEAF (A212 s.2): an s0-only localisation, never a kill.
If (iii) or (iv) fails, `tree256.tube_try` leaves the node **ALIVE** with the failing number printed -- the lemma is
never stretched.  Verifier clause: `certs/verify_tubekill256.py` re-checks (i)-(iv) from the node's snapshot and
re-runs `certs/verify_tube.py` on the cited certificate; gates `--corrupt {radii, seam, ray, T, names}`.
**NOT ported from A212:** the aligned split (`tree212.py` s.3 / `expand212.py`), which would need a fork of A211's
current `_expand`; a gated node is cut by A211's own Lemma ROLE-SPLIT instead (open link O4).

## 4. [M] Where the Trump residue actually is -- the (a)/(b) triage, and the blocker

`code/ray256.py` extends A212's containment gate **to the whole ray**: the configuration a window node would have
to hold if its packing were a contracted Trump configuration at depth t is Delta_{s0/m}(z-hat - t v), m = s-hat - t.
On the **scale** ray that is c-hat(s0/s-hat) for every square, independent of t; on the **slot** ray the free
squares are the same point and only the pinned coordinates sweep an interval of length (lam_pad - 1)|alpha|.  So the
ray gate costs no more than the pad-0 gate.  Applied to the ROOT boxes of all 149 nodes (a superset of every
descendant's pieces, so an (a) verdict is inherited by the whole subtree), margins outward:

| pad | slab | pin drift allowed | (a) no ray image | (b) might hold one |
|---|---|---|---|---|
| zero | {s0} | 0 | **149** (84 alive, 65 dead) | **0** |
| g1 | (3.861637, s0] | 6.0e-3 | **149** | **0** |
| window | (3.82, s0] | 2.24e-2 | **149** | **0** |

`results/triage256.json`.  Mechanism, node by node: the five pins force **g = id** (the pin set is not
D4-symmetric), and then no image square lies in the node's H box -- e.g. `f1_L10_0003` has H0 = Trump's square 7
but **H1** (A60's ladder box) holds none, and every c0_* page's H box holds none at all.  So **[M] the entire
Trump residue of the class was already discharged by A60/A83 before A212 ran**: A212's 149 are ordinary survivors,
Lemma TUBE-KILL's domain on this population is **empty**, and the remaining work is plain kills -- exactly what the
k5 pages looked like before passes 4-13 closed 286 of 303.

**[M] The blocker, found here and NOT in the brief.**  A window (pad g1) run on these records is **not a window
statement**.  A60's records carry pin cores of half-side 1/2 - delta_pin with **delta_pin = 3.08e-8** on 146 of the
149 (only `slack0.02_c0_Y0272 / _Y0411 / _Y0419` carry 2e-2), while the k5 pages that the pass loop closes at g1
carry delta_pin = **1e-2**.  The A211 pad enters "only through Theorem FC's slot pads and CC's lam"
(`attempts/A211-coarse-tree/notes/coarse_tree.md` S6), never through the pins, so the dilated family F of a packing
at m < s0 -- whose pins sit up to (lam - 1)*3/2 = 6.0e-3 (g1) / 2.24e-2 (window) off slots(s0) -- does not satisfy
the node's pin hypothesis at all.  In Lemma SEAM's arithmetic: **T_K(3.08e-8) = -3.3e-7 < 0**, i.e. those records
reach no side below s0 whatsoever.  This is A60's own ledger finding (`notes/ledger.md` s.1: all 49 PASS
certificates s0-fixed, transfer shell 4.0e-10 relative -- "no side of [3.82, s-hat] at all") and
`contraction_tube.md` s.4.4 item 1 ("**every A60 (K) leaf must be re-emitted at delta_pin = 1e-2**"), now confirmed
to bind on the frontier records too, not only on the PASS leaves.

## 5. Open links, in the order they block the row

| id | link | status | what closes it |
|---|---|---|---|
| **O1** | **A60 re-emission at delta_pin >= 1e-2** for all 149 trump5 records (146 are at 3.08e-8) | **[C]** blocking | A60's owner re-emits `results/nodes/<tag>.json` with slack cores; T_K(1e-2) = 0.0257 >= 0.0154 (g1) but < 0.0571 (whole window). **A257 revision (`attempts/A257-trump5-window/notes/window257.md` s.1): "two slabs (g1 + one below)" is wrong -- T' is the depth below s-hat, so slabs do NOT stack and the tube's reach is one number, s-hat - min(T_tube, T_K).** The cover is one TUBE slab plus plain Regime-1 certificates: **three** slabs at delta_pin = 1e-2 (tube to 3.851408, two grid certificates below), **two** only at delta_pin >= 1.8e-2 (T_tube = 0.045 binds, tube to 3.832084, one grid certificate) -- and that needs a new pad lam = s0/3.832084, since `g1` stops 0.0295 short of the certified reach. A257 also prices the re-emission: 49 (K) leaves at 974 s each = 13.3 CPU-h [M, `a60_slackcore_delta1e-2.json`], plus the A60 ladder's own kills, which were proved at delta_pin = 3.08e-8 and do **not** inherit to a widened pin hypothesis (~20-25 CPU-h, [C], not previously priced) |
| **O2** | the **s0 row** itself: 84 of the 149 still ALIVE at pad 0 | **running** | A256's pass loop (s.6); at pass 1 A212 had no A220/A221/A224/A230 lever |
| **O3** | **trump5's own delta_LP** (A82-style crossover scan) -- the seam's second number | **[C]**, but the operational question is now being measured | `contraction_tube.md` s.4.2 / s.4.4 item 3: delta_basin(trump5) = 0.0257 is measured, delta_LP(trump5) is **not**. **A257's SEAM PILOT measures the operational content directly** rather than the number: on a synthetic Trump-containing trump5 page at delta_pin = 1e-2, pad g1, the aligned descent reaches the tube in **14 cuts / 108 s** and TUBE-KILL fires (the first time it ever has), and each of the **14 near-Trump siblings** is then run on its own with A211's ordinary rules -- `attempts/A257-trump5-window/results/seam_table257.md`, page `docs/residue_map/campaigns/A257-trump5-window/seam257.svg`. First row measured: the shallowest sibling **DEAD by EmptyBox in 142 s**, against A212 s.6's sibling that did not die in 700 s under the old rules |
| **O4** | the **aligned split** of A212 s.3 on A211's current `_expand` | **[T] CLOSED (A257)** | **no fork of `_expand` is needed**: A211 turns a leaf rule's `"RSPLIT"` hand-back into children through `RS.branches` / `RS.apply_rsplit`, both pure functions of a spec dict, so handing back an RS-shaped spec whose `m` is the tube WALL installs A212 s.3 with zero lines of `_expand` changed (`attempts/A257-trump5-window/code/tree257.py`, `aligned_spec`). Soundness is Lemma ROLE-SPLIT's own. A257 also reports three defects in this file's own tube code that stop a window row today: `trump256.tube` boxes the PINS (Lemma TUBE-KILL (ii) asks the box on the free roles only, and with the delta_pin = 1e-2 the window needs, the pin box is +-1e-2 > r_c so the test can never pass); `tree256.tube_try` takes **max** over the pins' delta_pin where Corollary B' needs the **min**; and `tube_kill` / `tube_leaf` have one more `%` conversion than arguments, so the first tube leaf ever taken raises TypeError. Nothing on disk is affected ((b) = 0), but all three must be fixed before A256 can run a window pad |
| **O5** | the **audit** of A256's DEAD leaves (A211 S7 runs `audit211` per shard) | **[C]** | `audit211.py` reads A211's own certs/results; A256's worker skips it deliberately rather than write into A211's tree |
| **O6** | Lean: the tube obligation | **[C]** | `lean/tube_obligation_A83.md` (~400 lines, no new analysis) |

**A269 update (2026-09-23, `attempts/A269-trump5-reemit/notes/trump5_row.md`).**

| id | status after A269 |
|---|---|
| O1 | **149 records re-emitted** (`attempts/A269-trump5-reemit/records/`, A60's files untouched): `*_r269a` at delta_pin 9/500 for pad A `tube` (lam 969271/958021, slab (3.832084, s0], the tube slab) and `*_r269b` at **9/400** for pad B `window` (lam 969271/955000, (3.82, s0]) -- 1.8e-2 is NOT enough at pad B (drift 0.0224152).  Class (b) = 0 at both pads, so pad B alone is the full-window statement per root; benchmark 10 roots x 2 pads **20/20 DEAD in one wall**, ~12 CPU-h per pad; pad B launched over all 149.  Still open under O1: A60's ladder kills and 49 PASS leaves at slack pins, and the Trump-containing (D) branch (TUBE-KILL on pad A + a re-centred sub-slab record) |
| O2 | superseded for the window: the s0 row (pad 0) is closed (A256 pass 12); the window row runs on the re-emitted records |
| O3 | unchanged [C] |
| O4 | closed (A257); A269 also found that this file's `--tube` (run256.install_tube) recurses -- run269 installs Tree257 through a proxy |
| O5 | unchanged [C]: A269's DEAD leaves are not audited by audit211 either |
| O6 | unchanged [C] |

**Verdict on the seam (the brief's question).**  delta_basin(trump5) = 0.0257 at delta_pin = 1e-2 is **[T]**
(Lemma SEAM + the certified tube).  delta_LP(trump5) is **[C]** -- never scanned.  So the seam is an **obligation,
not a closed link**, and it is not even the first one: O1 (the pin slack of A60's records) blocks every window
statement about trump5 before the seam is reached.

## 6. What A256 launched

`code/loop256.sh 3 1800 zero` over A212's 84 ALIVE nodes -- start-node shards (Lemma PAR / Lemma INHERIT), 3
workers, 1,800 s wall each, pad 0, flags `A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1`, A228 rc rows, per-shard
commits, A256's own claims dir / STOP files / certs / results.  Pad **g1 is deliberately not launched** on the 146
delta_pin = 3.08e-8 records (s.4); the window pilot, when O1 or a decision to use the three slack records lands, is

    bash attempts/A256-trump5-passes/code/loop256.sh 3 1800 g1 slack0.02_c0_Y0272 slack0.02_c0_Y0419

(T_K(2e-2) = 0.0510 >= T'(g1) = 0.0154: those two records ARE window-capable at g1).
Stop: `touch attempts/A256-trump5-passes/logs/STOP_LOOP` (loop) / `.../logs/STOP` (workers).
Resume: `rm -f attempts/A256-trump5-passes/logs/STOP*` and relaunch the same line -- the queue is rebuilt from the
certificates, so every start node already closed is simply absent.
