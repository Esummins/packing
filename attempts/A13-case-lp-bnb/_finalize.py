# -*- coding: utf-8 -*-
"""final bookkeeping: notes fixes, REGISTRY line, LOG entry, results.md pointer, tree summary appended to notes"""
import io, subprocess, sys, os, json, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
n = io.open('notes.md', encoding='utf-8').read()
n = n.replace(u'column generation for ≤ 15 iterations or until\n  max coverage < 1.05, no row pruning',
              u'column generation (150 columns/iteration) for ≤ 40 iterations or until\n  max coverage < 1.02, no row pruning')
n = n.replace(u'time limit per node LP 180 s.', u'time limit per node LP 300 s (run 3).')
n = n.replace(u'θ inside the θ-intervals by ≥ 0.05°.', u'θ inside the θ-intervals by ≥ 0.3° (margins only at interior ends: θ = 0/90 and the domain boundary cx,cy ∈ {0.5, s−0.5} are closed).')
n = n.replace(u'Status: **running → see §7 for the verdict as it stands** (written incrementally).',
              u'Status: **done-negative (pilot; ~5 h): tree not closed at 3.84 within the budget; machinery + one verified node certificate; verdict §7.**')
# tree summary
try:
    out = subprocess.run([sys.executable, 'summarize.py', 'results/t384c/tree.json', 'x'], capture_output=True, text=True, encoding='utf-8').stdout
except Exception as e:
    out = str(e)
n = n.replace(u'## 5. Rigour: certificates and the LP-convergence problem (Task 4)',
              u'### 4b. Final state of run 3 (`summarize.py results/t384c/tree.json x`, at the end of the pilot; the run may have continued a bit)\n\n```\n' + out + u'```\n\n## 5. Rigour: certificates and the LP-convergence problem (Task 4)')
io.open('notes.md', 'w', encoding='utf-8').write(n)

# REGISTRY
reg_path = '../REGISTRY.md'
reg = io.open(reg_path, encoding='utf-8').read()
line = (u"| A13-case-lp-bnb | LP/B&B postdoc | I-L6 case-LP branch-and-bound over the packing structure: does it close at s = 3.84 (⇒ s(11) ≥ 3.84)? tree growth? rigour plan | "
        u"node = hypotheses (core boxes with rational inner squares K(B) ⊂ every Q of the box, budget 11−m; NO-families zone×θ); node LP = C1 (no symmetry) measure LP with rows disjoint from cores / outside families "
        u"(HiGHS, exact per-θ row oracle, column generation), D4 only at the root/symmetric NO-nodes; zone branch (NO + coarse YES boxes, corners→sides→interior, WLOG corner 0 at the root) + box refinement; "
        u"best-first, 8 workers, 300 s/LP; exact verifier verify_case.py (copy of certs/verify_measure.py) with rational exempt tests (family containment; interval SAT for cores); certify.py separation loop | "
        u"done-negative (pilot) | Sanity: root 3.80 τ 10.45–10.50 (dead), A12 contrast reproduced exactly (corners fixed 7.000; + side zones empty 5.000 converged) — this check caught a NO-filter margin bug at the closed ends θ=0 / cx=0.5 (runs 1–2 void, run 3 = results/t384c). "
        u"3.84 (root τ 11.033, corners 0.972 each, sides 1.0, interior 3.15): NO(all corners) DEAD by 1.59; 9 of 12 corner boxes dead by 0.23–0.69; the 3 boxes containing the corner square (centre [0.5,0.8]², θ thirds) sit at slack ≈ 0 (+0.04…+0.10 at 300 s, ≈ −0.04 after 25 min w/o shell rows, unconverged) ⇒ 3.84 is decided in the 2nd decimal by LP convergence, not tree size; if they die the tree has 13 leaves, else growth ≈ 3 survivors/corner level × 19 children/side level ⇒ 10⁴–10⁵. "
        u"Tree NOT closed in ~40 LPs (300–670 s each; C1 LP convergence ±0.1 at 300 s is the bottleneck: column generation needs ≥ 1000 col/it). Rigour: verify_case selftest PASS; ONE node certificate PASSED end to end (NO interior zone at 3.84, EPS_GEO 3e-3 robust re-solve, 220 atoms, 2.6 s); "
        u"core-node certificate FAILED: LP row oracle blind to the 2e-3 kept shell of squares touching the core (holes 0.80) → shell sampling added (Hyp.shell_points), costs ≈ +0.2 in τ unconverged, not re-certified. "
        u"Verdict: not viable for 3.85–3.87 with the present node LP (≥ 30 min/node for ±0.01 × 10³–10⁵ nodes); first fix column generation (10×) and use support-near small boxes with refinement; cheap decisive next step for 3.84: converge the 3 on-corner boxes with shell rows (≈ 30 min each) → if dead, a 13-leaf tree certifies s(11) ≥ 3.84. | attempts/A13-case-lp-bnb |\n")
if 'A13-case-lp-bnb' not in reg:
    reg = reg.rstrip('\n') + '\n' + line
    io.open(reg_path, 'w', encoding='utf-8').write(reg)

# LOG
log_path = '../../LOG.md'
log = io.open(log_path, encoding='utf-8').read()
entry = (u"\n## 2026-08-18 — A13-case-lp-bnb (case-LP branch-and-bound pilot, I-L6)\n"
         u"Implemented the rigorous case-LP B&B (hypotheses = core boxes with rational inner squares + NO-families; C1 node LP; exact verifier with exempt tests; certify loop). "
         u"Sanity: A12's conditional LP reproduced exactly (7.000 / 5.000). At s = 3.84: NO(all corners) dead by 1.59, 9/12 corner boxes dead by ≥ 0.23, the 3 corner-square boxes at slack ≈ 0 (undecided by 300-s LPs); tree not closed in ~40 LPs; "
         u"one node certificate verified end to end; core-node certification exposed a row-oracle blind spot (touching shell) — fixed, not re-certified. Verdict: LP convergence (column generation) is the bottleneck; 3.84 hinges on three LPs; 3.85+ not viable yet. See attempts/A13-case-lp-bnb/notes.md.\n")
if 'A13-case-lp-bnb' not in log:
    io.open(log_path, 'w', encoding='utf-8').write(log.rstrip('\n') + '\n' + entry)

# results.md pointer
res_path = '../../docs/results.md'
r = io.open(res_path, encoding='utf-8').read()
add = (u"\n\n## Case-LP branch-and-bound pilot (A13, 2026-08-18)\n\n"
       u"I-L6 implemented rigorously (`attempts/A13-case-lp-bnb/`): nodes = hypotheses (some square in a (centre,θ)-box ⇒ a rational core square K ⊂ that square, budget 11−#cores; "
       u"no square in a zone×θ family), node LP without symmetry, exact verifier with exempt tests, one node certificate verified. At s = 3.84 the split \"some square in a corner zone / none\" gives: NO dead by 1.59, "
       u"9 of 12 corner boxes dead by ≥ 0.23, and the 3 boxes containing the corner square at LP slack ≈ 0 (undecided at the pilot's LP accuracy ±0.05–0.1) — **s(11) ≥ 3.84 would follow from a 13-node tree if those three LPs converge below budget 10** (next step). "
       u"The tree did not close in the pilot; the bottleneck is C1 LP convergence (column generation), not tree size. 3.85–3.87 not viable with the present node LP. Details: `attempts/A13-case-lp-bnb/notes.md`.\n")
if 'A13' not in r:
    io.open(res_path, 'w', encoding='utf-8').write(r.rstrip('\n') + add)
print('done')
