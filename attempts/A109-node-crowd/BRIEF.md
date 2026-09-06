# A109 — teleport kills in phase space: SLOT-CROWD rows at the NODE level of A57 (Opus chore, measurement; read-only)

Context (2026-09-06). A107's gallery (docs/shadows.md) explains 1,260 of A57/A60/A61's 1,566 alive-at-LP nodes by 53
shadows. The PI read the top entries and found that most are not near-packings at all but configurations the
TELEPORT lemma already kills: **S01 (620 nodes, side exactly 4.000) has a free corner** — any packing there moves a
square into the empty corner cell and lands in a higher-k class that is certified dead on the window; **S03's free
squares f0/f1/f2 are essentially simple** (a hair off lattice cells: SNAP); **S04's f0 teleports into BR(0,1)**. The LP
does not know this: nothing in the node LP forbids a dual support that leaves a usable slot empty or singly met. The
PI's diagnosis: "the issue is turning teleport-lemma kills into kills in phase space." The lab already has the sound
mechanism, unused in the tree: **Lemma SLOT-CROWD and the crowd certificate CS (docs/proofs/slot_crowds.md, A94)** —
in every packing at side m ∈ [3.82, s0) containing the pins of class S, every USABLE completable slot p of S (one whose
extension S ∪ {p} is certified dead on a window containing m) is met, open-interior, by ≥ 2 non-pin squares; the
certificate adds incidence rows (budget N + 2 m_u e, Lemma CW-S) and is verified by 1 + r_max runs of the frozen
verifier. A94 tried it as a ROOT certificate for the whole class and it failed at the s0 side (needs δ ≥ 0.2 to pass
the LP; certified runs fail on holes). The question here is different: at the NODE level, where the box is small,
do crowd rows kill the S01/S03/S04-type alive nodes, and at what price?

Read first: docs/proofs/slot_crowds.md (SLOT-CROWD, the usable slots of k5_11 = BL(1,1), BR(0,1), TL(1,0), TR(0,0)
[TR only on [3.82, 3.877)] and of k5_16 = BR(0,1), TR(0,1), TR(1,0); Lemma CW-S; the 1 + r_max verification; §4.4's
failure modes), docs/proofs/k0_blocked_side.md (Lemma CW, Theorem N), attempts/A94-slot-crowds/{code,notes} (the crowd
LP implementation — reuse it), docs/shadows.md S01/S03/S04 + attempts/A107-shadow-gallery/results/shadow_nodes.json
(which alive nodes each shadow explains), attempts/A57-shadow-trees/results/tree/**/<node>.json (node LP results:
'hyp' cores, 'packing', 'rows_all', tau/budget), attempts/A53-simple-strata/code/caselp.py (solve_node) and the frozen
verify_case.py (byte-identical, run only), attempts/A96-a57-parametric/notes/ (parametric emission — crowd rows must be
compatible with the 4-D window certificate or be run at s0 with the slab bookkeeping; say which).

## T1 — the mechanism check on the shadows
For S01, S03, S04 (and S05 if quick): for each explained alive node, which usable slot of its class does the dual
support leave empty or singly met (count incidences of the support's placements with each usable slot box at δ =
0.3, 0.1, 0.05)? Report the fraction of explained nodes whose support violates SLOT-CROWD at each δ — that is the
upper bound on what crowd rows can kill.

## T2 — crowd rows at the node level (offline, own copies)
Take ≥ 40 alive nodes (stratified: S01-explained, S03/S04-explained, and 10 fractional/unexplained as controls;
levels 1–2), copy their LP hypotheses, add the SLOT-CROWD incidence rows for the class's usable slots at δ ∈ {0.3,
0.1, 0.05} (Lemma CW-S form: budget N + 2 m_u e), re-solve with solve_node (same warm pool, 300 s cap), report τ, η,
minmass per node and per δ, and the count that go DEAD at the LP. For the DEAD ones certify a sample (≥ 8) with the
frozen verifier in the 1 + r_max form of A94 §4 and report PASS/FAIL with hole counts — the s0-side failure mode A94
hit (holes in runs B_r, r ≥ 2) is the thing to look for; state whether node-level boxes escape it.

## T3 — price and composition
Per node: LP time and verifier time with crowd rows vs without; kills per level; what it removes from A57's remaining
schedule (13.3 wall-days at 5, tail concentrated at levels 3–4 — A96's tables in attempts/A96-a57-parametric/notes/)
if deployed as (a) a re-solve on alive nodes only, (b) rows in every node LP. Compatibility with the parametric
window certificate: can the crowd rows ride in the 4-D verifier (A96's verify_param.py) or only at fixed s0? Trump
canary: trump5's usable slots — Trump must NOT be killed (its slots are doubly met or unusable); run one trump5 node
through T2 and confirm. One-line verdict: "node-level crowd rows kill X of Y S01/S03/S04 nodes at δ = …, certify Z of
Z, cost C per node, worth D wall-days" or the failure mode.

Constraints: READ-ONLY on A57/A96/A94/A107 state (copy node jsons; never write under their dirs; never touch their
processes); ≤ 2 processes, BLAS-pinned, 6144 MB commit gate and > 3 GB free physical before every LP (the box runs
six A57 shards + deepens + resolvers); frozen verifiers byte-identical; git = fetch + plain merge + push own paths (no
rebase/autostash/reset). Writes: attempts/A109-node-crowd/{code,results,notes,logs}, registry row, LOG.md, one-line
note on the A57 depgraph node (owner field untouched). Report ONCE: T3 verdict first, T2 table second, T1 third,
pointers last. No interim messages.
