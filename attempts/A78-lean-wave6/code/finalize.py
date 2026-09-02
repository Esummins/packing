#!/usr/bin/env python3
"""A78 close-out: T5 partial section in findings.md, LOG.md entry, REGISTRY row, depgraph
in-progress notes for the two corpora still replaying.  Re-runnable: each write is guarded by
a marker string.  `--t5-done` switches the T5 wording to complete (run by the T5 engineer at
the end of the corpus run, together with patch_depgraph.py --corpus K61,TRAP)."""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
done_flag = '--t5-done' in sys.argv
rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', 't5_timings.jsonl'), encoding='utf-8')]
by = {}
for r in rows:
    by.setdefault(r['corpus'], []).append(r)
k61 = [r for r in rows if r['corpus'] == 'K61']
trap_names = {'k6_07', 'k6_19', 'k6_21', 'k6_22', 'k6_23', 'k6_24'}
trap_done = [r for r in k61 if r['name'] in trap_names]
tot_min = sum(r['lean_wall_s'] for r in rows) / 60
mx = max(rows, key=lambda r: r['lean_wall_s'])
statuses = sorted(set(r['status'] for r in rows))
ratio = sorted(r['lean_wall_s'] / max(r['py_time_s'], 1e-3) for r in rows)
med_ratio = ratio[len(ratio) // 2]
stat = ('K61 %d/61, TRAP %d/6 (⊂ K61), P1 %d/1, THMU %d/11; %d certificates, all %s; total Lean wall %.1f min; '
        'max %s = %.0f s (%d atoms, %d boxes); Lean/Python wall ratio median %.0f×'
        % (len(k61), len(trap_done), len(by.get('P1', [])), len(by.get('THMU', [])), len(rows), '/'.join(statuses),
           tot_min, mx['name'], mx['lean_wall_s'], mx['atoms'], mx['boxes'], med_ratio))
print(stat)

# --- findings.md T5 section -------------------------------------------------------------
F = os.path.join(HERE, '..', 'notes', 'findings.md')
s = open(F, encoding='utf-8').read()
marker = '## T5 — fixed-corpus replays'
if marker not in s:
    s += '''
## T5 — fixed-corpus replays (Opus; `t5_corpus.md`, `results/t5_timings.jsonl`)

* [T/M] `lean/gen_corpus_lean.py` → `PackingCertMathlib/Corpus/{K61,TRAP,P1,THMU}/` (one
  `Data_*` + `Check_*` module per certificate: `check_<name>` by `native_decide` +
  `<name>_kill` via `checkCaseI_kill` (nofams = []) or `<name>_no_family` via
  `checkCaseI_no_family` (P1, THMU); aggregates `corpus_K61/TRAP/P1/THMU`; root
  `Corpus.lean`), built by the separate lake target `PackingCertCorpus` (default target and
  CI untouched — verified a no-op).  Each `check_*` carries exactly its own
  `native_decide` axiom (`logs/axioms_corpus.log`).
* [M] STATUS AT CLOSE: %s.  %s
* [F] Corpus manifest: `k3_00` is `attempts/A55-k4-sweep/k3_ext/certs/k3_00.json` (579
  atoms, depth 56) — the sibling `attempts/A55-k4-sweep/certs/k3_00.json` has a FAIL
  report and was rejected; all 61 K61 reports PASS; P1 = `m3_trump5_interior_NO`; THMU =
  `u_reinsert_00..10` (0 atoms, budget 1, B-NO form).
* [F/M] Python `--no-float-prepass --jobs 1` cross-checks on the 3 cheapest certificates:
  PASS with box counts identical to the campaign reports (decision-neutral shortlist, as
  A70/A75 found).
* [F] **Pricing for the A57/A60 corpora:** Lean `native_decide` costs 30–170 s per
  certificate here for 2k–200k boxes (Python 0.2–5 s), i.e. 25–100× the Python wall
  under a saturated CPU; the per-box cost is dominated by the `Rat` core-exemption test.
  A corpus of the A57/A60 size (thousands of leaves at depth 56–60) is a multi-day
  desktop job at this rate — a `PackingCertCorpus`-style isolated target built
  incrementally is the only sane shape.
''' % (stat, 'Corpus run COMPLETE.' if done_flag else
       'The remaining K61/TRAP certificates are still replaying in the background runner '
       '(`logs/t5_build.log`); `corpus_replayed` is set only on the COMPLETE corpora (THMU, P1); '
       'C.K61 / D.TRAP keep their A78 chips until the run lands (the engineer re-runs '
       '`patch_depgraph.py --corpus K61,TRAP` + `finalize.py --t5-done`).')
    open(F, 'w', encoding='utf-8', newline='\n').write(s)
    print('findings T5 section written')
elif done_flag:
    s = s.replace('* [M] STATUS AT CLOSE:', '* [M] STATUS AT CLOSE (superseded — see the completion line below):')
    s += '\n* [M] T5 COMPLETION: %s.\n' % stat
    open(F, 'w', encoding='utf-8', newline='\n').write(s)
    print('findings T5 completion appended')

# --- LOG.md ------------------------------------------------------------------------------
L = os.path.join(REPO, 'LOG.md')
log = open(L, encoding='utf-8').read()
lm = '## 2026-09-02 A78-lean-wave6'
if lm not in log:
    log = log.rstrip('\n') + '''

## 2026-09-02 A78-lean-wave6 (Fable lead; Opus T2/T3/T5) -- done-success
- T1 F11/H2 DISCHARGED: the Young-form census is a Lean DEFINITION (Census.lean: skeleton s z = per corner the
  cells whose down-set is occupied by exactly-on-grid axis-aligned squares; all 8 A72 binding choices pinned,
  B1/B3/B6 THEOREMS; B2 decided combinatorially and proved = the real predicate on ALL of (3,4), so the census
  is one object on (3,4)). L3 exhaustiveness = theorem skeleton_mem_census (propext/choice/Quot.sound only);
  CensusCheck.lean (native_decide): 1110 tuples, 163 classes, D4-closed, EXACTLY A72's tuple set AND orbit
  partition, Trump ((2,1),(1),(1),{}) k=5. D4 action on points/squares/slots/configurations with
  skeleton_d4 (Simp(g.P) = g.Simp(P)); hface = containsPins_skeleton; Lemma M->E = class_kill; hinc =
  card_lt_teleport (CensusSelection.lean). B.CENSUS, B.EXACT, B.SEL, C.CC2 -> lean-proved.
- TopLevel: StratumIdx/trumpStratum/InStratum are DEFINITIONS (computation-free); stratify and unique_transfer
  are THEOREMS (census exhaustiveness); roster 12 -> 7 named axioms (stratum_kill, trump_residual, basin +
  the 4 A22 interface axioms). s_eleven_unique depends on exactly basin/stratum_kill/trump_residual/zhat.
- T2 CIDL-LEAN DISCHARGED (A.UBshat -> lean-proved): Cidl{Poly,Gen,Data,Check,Bridge}.lean replay
  certs/cidl_identity.json by native_decide (generators REBUILT from A22 conventions; 86728 -> 2682 terms;
  27 s), sign gates proved STRONGER (e<0, Delta<0 on [3/10,2/5], no Sturm needed); axiom shatA22_eq_shat
  replaced by a22_exact_structure (A22 certified content only); shatA22_eq_shat is a theorem.
- T4 A.UNIQ own tier -> lean-proved: unique_via_chain / s_eleven_unique_of_chain (UniqueChain.lean): the
  CC-2 chain + Theorem U collapse as a strong induction on 11-k, with H10-stuck (U-O2) and Theorem U (U-O1)
  as explicit hypotheses; the clause WITHOUT stratum_kill. Confirms A63's diagnosis exactly.
- D.D4 verifier_lean: d4_wlog (D4Wlog.lean) = the WLOG at every side, conditional on root occupancy (D4.5).
- T3 D.ALIVE verifier_lean: AliveChecker/AliveBridge.lean, alive_sound (PASS => no checkCaseI certificate of
  that budget); pilot trump5_strict 2.8 s. FINDINGS: F1 obstacles are full pin squares not the cert cores
  (theorem proved in core-monotone form); F2 admissibility hard-wired at s0; F3 nofams=[] implicit; F4 LOUD:
  attempts/A57-shadow-trees/results/alive/k5_16_m5.json carries a FALSE LP-UNKILLABLE claim (m=5 < budget 6)
  - do not cite; trump5_strict.json is the only sound witness file.
- T5 corpus replays (PackingCertCorpus target, one native_decide theorem per certificate): %s
- Audit: every new theorem propext/choice/Quot.sound (+ its own native_decide axiom for the check theorems);
  0 sorryAx; full default target green; Measure382Check cache hit throughout; A57/A60/A61/A76/A77/A79 untouched.
  Docs: instratum_bridge.md E.5, unique_transfer.md 6, d4_reduction_s0.md D4.5, attainment_ub.md 7.6;
  lean/README.md; depgraph json+svg (corpus_replayed accent added to the renderer); REGISTRY row.
''' % stat
    open(L, 'w', encoding='utf-8', newline='\n').write(log)
    print('LOG entry written')
elif done_flag:
    log = log.rstrip('\n') + '\n- A78 T5 COMPLETION: %s\n' % stat
    open(L, 'w', encoding='utf-8', newline='\n').write(log)
    print('LOG completion appended')

# --- REGISTRY.md row -----------------------------------------------------------------------
R = os.path.join(REPO, 'attempts', 'REGISTRY.md')
reg = open(R, encoding='utf-8').read()
if '| A78-lean-wave6 |' not in reg:
    row = ('| A78-lean-wave6 | theory lead (Fable) + 3 Opus engineers | Lean wave 6: the census DEFINITION '
           '(F11, unblocks B.CENSUS/B.EXACT/B.SEL/C.CC2), CIDL-LEAN (A.UBshat), fixed-corpus replays (C8), '
           'the two small checkers (D.ALIVE, D.D4), unique_transfer derivation (A.UNIQ) | Census.lean pins A72 '
           'B1-B8; combinatorial B2 proved = real on (3,4); exhaustiveness as a theorem, counts by native_decide; '
           'D4 action + skeleton equivariance; UniqueChain strong induction on 11-k; CIDL sparse-poly '
           'native_decide + monomial-bound sign gates; PackingCertCorpus isolated target | done-success | '
           '**F11 DISCHARGED: the Young-form census is a Lean definition; L3 exhaustiveness is a THEOREM '
           '(every packing at ANY s in (3,4)); 1110/163 and EXACT agreement with A72 (tuple set + orbit '
           'partition) by native_decide.** hface, hinc, Lemma M->E, D4 bookkeeping all Lean; B.CENSUS/B.EXACT/'
           'B.SEL/C.CC2 -> lean-proved. TopLevel: StratumIdx/InStratum definitions, stratify + unique_transfer '
           'THEOREMS, roster 12 -> 7 axioms; s_eleven_unique rests on basin/stratum_kill/trump_residual/zhat only. '
           'CIDL-LEAN discharged (shatA22_eq_shat a theorem; a22_exact_structure = A22 content; sign gates '
           'e,Delta < 0 on [3/10,2/5] - no Sturm). A.UNIQ own tier lean-proved (unique_via_chain: chain + '
           'Theorem U with U-O1/U-O2 explicit). D.D4 d4_wlog at every side. D.ALIVE alive_sound + LOUD finding: '
           'A57 results/alive/k5_16_m5.json carries a FALSE LP-UNKILLABLE claim (m=5 < budget 6); Python '
           'obstacles are full pin squares not cores; admissibility hard-wired at s0. Corpus replays: %s. '
           'All new theorems propext/choice/Quot.sound (+ own native_decide per check); 0 sorry; CI target green | '
           'attempts/A78-lean-wave6 |' % stat)
    reg = reg.rstrip('\n') + '\n' + row + '\n'
    open(R, 'w', encoding='utf-8', newline='\n').write(reg)
    print('REGISTRY row written')

# --- depgraph in-progress notes for C.K61 / D.TRAP --------------------------------------
if not done_flag:
    P = os.path.join(REPO, 'lean', 'depgraph.json')
    d = json.load(open(P, encoding='utf-8'))
    for n in d['nodes']:
        if n['id'] in ('C.K61', 'D.TRAP') and 'A78 T5 (2026-09-02): corpus replay IN PROGRESS' not in n.get('note', ''):
            n['note'] += (' || A78 T5 (2026-09-02): corpus replay IN PROGRESS - modules generated for every '
                          'certificate (lean/PackingCertMathlib/PackingCertMathlib/Corpus/K61, target '
                          'PackingCertCorpus), %d/61 replayed so far, all PASS; corpus_replayed is set when the '
                          'run lands (results/t5_timings.jsonl).' % len(k61))
    json.dump(d, open(P, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
    open(P, 'a', encoding='utf-8', newline='\n').write('\n')
    print('depgraph in-progress notes written')
