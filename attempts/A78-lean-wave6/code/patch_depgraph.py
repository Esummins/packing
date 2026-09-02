#!/usr/bin/env python3
"""A78: depgraph label/flag/note updates + owner-chip clearing.  Idempotent per node.
Usage: python patch_depgraph.py [--alive] [--corpus K61,TRAP,P1,THMU]"""
import json, os, sys, datetime
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(REPO, 'lean', 'depgraph.json')
d = json.load(open(P, encoding='utf-8'))
N = {n['id']: n for n in d['nodes']}
alive = '--alive' in sys.argv
corpus = []
if '--corpus' in sys.argv:
    corpus = sys.argv[sys.argv.index('--corpus') + 1].split(',')

def upd(nid, **kw):
    n = N[nid]
    note = kw.pop('note_add', None)
    n.update(kw)
    if note and note not in n.get('note', ''):
        n['note'] = (n.get('note', '') + ' || ' + note).strip(' |')
    if kw.get('owner', None) is None and 'owner' in n and n['owner'] == 'A78':
        n['owner'] = None

# T1 — census
upd('B.CENSUS', label='lean-proved', owner=None,
    source=N['B.CENSUS']['source'] + '; LEAN DEFINITION lean/PackingCertMathlib/PackingCertMathlib/Census.lean (+CensusCheck.lean, CensusCorpus.lean)',
    lean='PackingCert.S11.skeleton / censusL / classCodes; skeleton_mem_census (L3 as a theorem at every s in (3,4)); CensusCheck: censusL_length = 1110, classCodes_length = 163, census_eq_corpus (= A72 tuple set), corpus_classes_canon/_distinct (= A72 orbit partition), census_d4_closed, trumpPins_eq_corpus',
    note_add='A78 (2026-09-02): F11 DISCHARGED - the Young-form census is a Lean DEFINITION (Census.lean; all 8 A72 binding choices B1-B8 pinned at their definitions, B1/B3/B6 as theorems), L3 exhaustiveness is the theorem skeleton_mem_census (propext/choice/Quot.sound only), the counts 1110/163 and EXACT agreement with A72\'s tuple set and orbit partition are native_decide theorems (CensusCheck.lean); TopLevel StratumIdx/trumpStratum/InStratum are now definitions (InStratum = skeleton is a D4-image of the class rep). Census window sharpened: one object on (3,4), not just (3.82,3.9).')
upd('B.EXACT', label='lean-proved', owner=None,
    lean='PackingCert.S11.class_kill (Lemma M->E, E.2: a monotone kill of S <= g.T at side s in (3,4) empties the exact class of T); containsPins_skeleton (= hface); skeleton_d4 (D4 equivariance Simp(g.P) = g.Simp(P)); d4_packing; d4Apply_slotCentre (= A67 R8)',
    note_add='A78 (2026-09-02): hface DISCHARGED (containsPins_skeleton) and the E.2 D4 bookkeeping machine-checked (d4Apply/d4Sq/d4Slot/d4Cfg, skeleton_d4); Lemma M->E is the theorem class_kill. docs/proofs/instratum_bridge.md E.5.')
upd('B.SEL', label='lean-proved', owner=None,
    lean='PackingCert.S11.exists_kmax_skeleton (selection with k = |skeleton|, B6 bound skeleton_card_le) + cc2_stuck_census (CensusSelection.lean); hinc discharged by card_lt_teleport',
    note_add='A78 (2026-09-02): hinc DISCHARGED (CensusSelection.lean: skeleton_teleport_mono + teleport_completes => card_lt_teleport); B.SEL = exists_kmax_skeleton + cc2_stuck_census with NO census hypothesis left.')
upd('C.CC2', label='lean-proved', owner=None,
    lean='PackingCert.S11.cc2_stuck_census / cc2_two_meeters_census (CensusSelection.lean)',
    note_add='A78 (2026-09-02): hinc DISCHARGED - CC-2/CC-2\' are unconditional Lean theorems (cc2_stuck_census, cc2_two_meeters_census).')
# T2 — CIDL-LEAN
upd('A.UBshat', label='lean-proved', owner=None,
    lean_axiom='zhat, shatA22, trump_packs_at_shatA22, a22_exact_structure (all = A22 certified content); shatA22_eq_shat is a THEOREM; trump_packs_at_shat composes',
    note_add='A78 T2 (2026-09-02): CIDL-LEAN DISCHARGED - CidlPoly/CidlGen/CidlData/CidlCheck/CidlBridge.lean replay certs/cidl_identity.json by native_decide (generators REBUILT from A22 conventions; identity + octic + sign gates, 27 s); sign gates proved STRONGER (e<0, Delta<0 on [3/10,2/5]); axiom shatA22_eq_shat replaced by a22_exact_structure (A22 certified content only: t-hat in [3/10,2/5], s_A22 in the isolating interval, 13 generators vanish at P-hat built from zhat). The node\'s residual trust = the A22 interface (E.A22, A79), no algebra.')
# T4 — A.UNIQ own tier
upd('A.UNIQ', own_tier='lean-proved', owner=None,
    lean='PackingCert.S11.unique_transfer (THEOREM from census exhaustiveness, TopLevel.lean); unique_via_chain + s_eleven_unique_of_chain (UniqueChain.lean: the chain+collapse with H10-stuck (U-O2) and Theorem U (U-O1) as explicit hypotheses)',
    note_add='A78 T4 (2026-09-02): own tier LEAN-PROVED - unique_transfer AS STATED is a theorem (f = id; every packing at s-hat has a skeleton), and the honest route (unique_transfer.md 2-4) is the theorem unique_via_chain: strong induction on 11-k with CC-2 teleports (card_lt_teleport, teleport_packing) and the Theorem U interface, stuck endpoint = trump_residual + basin; s_eleven_unique_of_chain gives the clause WITHOUT stratum_kill. Node stays blocked-only red until C.K4TIER (U-O2), C.A57/U-O3, D-nodes close.')
# D.D4
upd('D.D4', verifier_lean=True, owner=None,
    lean='PackingCert.S11.d4_wlog / d4_cover_zone (D4Wlog.lean): the WLOG at EVERY side, conditional on root occupancy; R2/R3/R5/R8 = d4Apply_mul/inv, d4Apply_image_container, d4Apply_sqdist, d4Sq_set, d4Apply_slotCentre (Census.lean)',
    verifier_lean_note='the reduction lemma itself is a Lean theorem (d4_wlog, conditional on the s0 root-occupancy hypothesis exactly as D4.4 records); the Python R1-R8 checks are subsumed (R6/R7 are verify_tree2 tree machinery, not ported)',
    note_add='A78 (2026-09-02): D4Wlog.lean - the WLOG is a THEOREM at every side (d4_cover_zone = R4, d4_wlog), built on the Census.lean D4 action; docs/proofs/d4_reduction_s0.md D4.5.')
if alive:
    upd('D.ALIVE', verifier_lean=True, owner=None,
        lean='PackingCert.S11.alive_sound (AliveBridge.lean): checkAlive PASS => no checkCaseI certificate of that budget for these cores at this side (completeness-side arbiter)',
        verifier_lean_note='soundness of the ARBITER: PASS => no case-LP certificate of budget b can pass the (Lean-sound) verifier for this node; never in the trusted composition',
        note_add='A78 T3 (2026-09-02): Lean port AliveChecker.lean + soundness theorem alive_sound (AliveBridge.lean).')
for c in corpus:
    nid = {'K61': 'C.K61', 'TRAP': 'D.TRAP', 'P1': 'D.P1', 'THMU': 'A.THMU'}[c]
    upd(nid, corpus_replayed=True, owner=None,
        note_add='A78 T5 (2026-09-02): corpus REPLAYED in Lean (lean/PackingCertMathlib/PackingCertMathlib/Corpus/%s, one native_decide theorem per certificate, aggregate corpus_%s; lakefile target PackingCertCorpus; timings attempts/A78-lean-wave6/results/t5_timings.jsonl).' % (c, c))
# remaining A78 chips (if any) stay until their task lands
left = [n['id'] for n in d['nodes'] if n.get('owner') == 'A78']
d['meta']['attempt'] += ' || A78 lean-wave6 (2026-09-02): F11 DISCHARGED - Census.lean is the Young-form census definition; B.CENSUS/B.EXACT/B.SEL/C.CC2 -> lean-proved; A.UBshat -> lean-proved (CIDL-LEAN, identity a theorem; A22 interface axioms remain); A.UNIQ own_tier -> lean-proved (unique_transfer + stratify THEOREMS; chain+collapse UniqueChain.lean); D.D4 verifier_lean (d4_wlog); TopLevel roster 12 -> 7 axioms.' + (' D.ALIVE verifier_lean (alive_sound).' if alive else '') + (' Corpora replayed: %s.' % ','.join(corpus) if corpus else '')
d['meta']['date'] = '2026-09-02'
d['meta']['labels']['corpus_replayed_flag'] = 'nodes may carry "corpus_replayed": true - every certificate of the node\'s corpus is replayed in Lean (one native_decide theorem per certificate, isolated PackingCertCorpus target); rendered as a gold corner dot'
json.dump(d, open(P, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
open(P, 'a', encoding='utf-8', newline='\n').write('\n')
print('patched; A78 chips left:', left)
