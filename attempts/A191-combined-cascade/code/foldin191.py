"""A191 -- the registry row and the LOG entry (run once; idempotent: skips if the A191 row / entry is present)."""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

ROW = ("| A191-combined-cascade | Fable lead (<= 2-3 BelowNormal pythons at affinity 0xFFFF + one verifier child; box ceiling 12 excluding Claude "
       "Extensions counted and WAITED on before every LP and every verifier launch -- the box held 10-12 lab pythons all night, three of them A185's "
       "idle waiters, so two shards ran; READ-ONLY on every other attempt (A168/A181/A183 records read, A185/A190 emitters and verifiers imported, the "
       "frozen verifier re-run unedited); no recursive deletes; PYTHONDONTWRITEBYTECODE=1) | PI (00:45): evidence by 07:00 that the k0 residue is "
       "COMPUTE-BOUND with a price -- the windows + guard-line LP (v5) with the not-yet-placed corners' meeters as anonymous windowed roles and the "
       "no-room leaf on ALL 64 alive S2 nodes of l1_104 (kill rate + per-node cost), then the S3 children of the survivors (coarse), the canary l1_153, "
       "and the CPU-h per cell / for all eleven with the assumption list | node191 leaf: (a) corner NO-ROOM lanes (A189 Lemma 1 on the widened corner "
       "box, m = 2, A141 cover + A118 pair test), (b) the v1-style exact-core LP on the roles' union boxes with A144 guard-line columns at budget n - m "
       "(A190 emitter; converges), (c) A185's windows LP at budget 11 with the same lines as the diagnostic, (d) verify_case_v5 + the frozen "
       "verify_case.py re-run on line-free kills; s3_191 (coarse 4/2 parent-seeded children); fig191 / report191 / price191 | done-success | "
       "**THE FIRST k0 NODE KILLS UNDER THE FROZEN VERIFIER: 17 of the 64 alive S2 nodes of l1_104 (27 %) DEAD** -- every one by the exact-core LP "
       "converged at tau = 7.000 < 8 on a fixed point whose H collapsed (kept <= 0.02 on 14 of 17), v5 PASS and, no guard line ever active, **all 17 "
       "PASS under the frozen verifier** (conditional on K0-O1 as every cascade kill); 26 converged alive at tau = budget exactly, 19 unconverged kill "
       "candidates; [T] the anonymous corner windows cannot change the LP (their rows are implied by the free clause) -- they act in the geometry, "
       "where the corner lanes are None on 64/64; the windows LP never converges (tau 10.0 at every cap) and is a diagnostic; root/D0/S1 is ALIVE "
       "converged (tau = 8.000), not a kill; **305 s per node, 5.4 CPU-h for the layer, 0.32 CPU-h per kill**; canary l1_153 alive converged; S3 "
       "coarse (interior children of S2 survivors): the exact-core LP kills them too (v5 PASS, ~250 s each) while the corner box B0 dies at 4/2 in 60 s; "
       "price table `notes/price191.md` (S2 measured, S3 sampled, S4-S8 assumed: the cell closes at a payable price only if the deep layers kill "
       ">= 0.99) | attempts/A191-combined-cascade |")

ENTRY = """
## 2026-09-10 -- A191-combined-cascade (Fable lead) -- **the combined k0 cascade leaf on l1_104's S2 layer: 17 of 64 alive S2 nodes DEAD under the FROZEN verifier; the layer priced at 305 s per node**
- **The task (PI 00:45).** Evidence by 07:00 that the k0 residue is compute-bound with a price: the windows + guard-line LP (v5) with the
  not-yet-placed corners' two meeters as anonymous windowed roles and the no-room leaf on ALL 64 alive S2 nodes of `l1_104` (A183's
  renorm181/183 fixed points), root/D0/S1 first; then the S3 children of the survivors (coarse), the canary `l1_153`, the CPU-h per cell.
- **[T] The anonymous corner windows cannot change the LP** (`notes/cascade191.md` s.1): a window without a core has the row (V2) on its poses
  not meeting ANOTHER window's attached core; every core is attached, so `E_i = E_0`, and `f = 11 - 9 - 0 = 2 > 0` keeps the free clause (V1),
  a superset of every window row -- (V2) is implied, tau and `b4 = 11` unchanged.  They act in the geometry: the corner NO-ROOM leaf (A189 Lemma 1
  with the pocket = the widened corner box, `m = 2`: K0-BLOCKED's two distinct meeters, R6 and A161's exact miss test make them free; A141 cover +
  A118 pair test give LANE) -- and there LANE = None at BR / TL / BL on 64 of 64 (0 kills, 29 s per node).
- **[M]/[C] The sweep** (`results/run191_l1_104_S2.jsonl`, `figs/steps_l1_104_S2.svg`, two BelowNormal processes, 01:17-04:21, cap 300 s):
  **17 DEAD (27 %)** -- root/D0/S7, S12, S13; D1/S8; D3/S9; D4/S10; D52/S4, S7, S8; D53/S5; D54/S12, S13, S14; D55/S5; D58/S7; D6/S15; D7/S13 -- every
  one by the v1-style LP (A135 exact cores on the roles' UNION boxes, A144 guard-line columns, budget 8, A190's emitter) CONVERGED at **tau = 7.000 < 8**,
  `verify_case_v5` PASS, and -- no guard line ever carrying density (0 of 64 in both LPs) -- **all 17 PASS under the frozen `verify_case.py`
  (A143, sha `521cb01f...`; `certs/*_v1.frozen.certify.json`)**: [C] under the frozen chain, conditional on K0-O1 and the node's case as every
  cascade kill is.  26 (41 %) converged ALIVE at tau = 8.000 = budget exactly; 19 (30 %) LP-dead UNCONVERGED kill candidates (tau 7.19-7.58 at ~240 s);
  tau quantised {7.000 x20, 7.2-7.6 x16, 8.000 x28}.  **[F]** the dead nodes are those whose A183 fixed point COLLAPSED H (kept <= 0.022 on 14 of 17,
  6e-7 on root/D0/S12): the geometry kills, the LP witnesses; the guard lines added nothing at S2; A185's windows LP (budget 11) sits at tau 9.6-10.6
  unconverged at every cap (A185: 10.000 at 300 / 1100 / 1526 s on root/D0/S1) -- a diagnostic, not a verdict.
- **root/D0/S1 (the PI's "first kill if it converges"): NOT a kill** -- v1-style LP tau = 8.000 = budget CONVERGED in 136 s (ALIVE); windows LP 10.03
  unconverged; lanes None.  The first k0 S2 kills are root/D0/S12 and root/D0/S13 (frozen PASS at 01:57).
- **Cost per S2 node [M]:** geometry 29 s, v1 LP 162 s (max 356), windows diagnostic 101 s, certificate 46 s per kill (max 244), wall 305 s mean /
  663 s max; the layer **5.4 CPU-h** (v1 LP 2.9, diagnostic 1.8, geometry 0.5, certificates 0.25); **0.32 CPU-h per kill**.
- **Canary `l1_153`** (1 alive S2 node root/D25/S=H): v1 LP tau = 9.000 = budget converged (ALIVE), lanes None, 263 s -- the construction transfers.
- **S3 (coarse 4/2, parent-seeded; sample):** the first cover box B0 dies at 4/2 by EmptyBox(B) on 4 of 4 parents (60 s each -- a biased sample, the
  sampler then took interior quantiles); the interior children (B95 of root/D0/S0, S1, S11, ...) die by the exact-core LP (v5 PASS, ~250 s each);
  `results/run191_l1_104_S3coarse.jsonl`, `run191_l1_104_S3.jsonl` (the LP on A183's fine S3 records); the counts at report time in `notes/price191.md`.
- **The price** (`notes/price191.md`, `budget.md` s.D item 13 + the k0 row, `residue_ledger.md` s.4): S2 measured (5.4 CPU-h, 27 % kills + 30 % candidates),
  S3 sampled, S4-S8 ASSUMED at the S3 rate with fan-out 112 / 56; the table prints CPU-h per cell and instance-hours (16 vCPU) for the measured, 0.90
  and 0.99 deep kill rates; the lever is the geometry's kill rate at depth (A174 coexistence cut, A178 partner-first), not LP cap.
- **Process.** <= 2 shard pythons + 1 verifier child (<= 5 rule), BelowNormal / 0xFFFF, box ceiling 12 excluding Claude Extensions counted and WAITED on
  before every LP and verifier launch (the box held 10-12 lab pythons all night, three of them A185's idle waiters -- so a third A191 process could never
  pass the gate and was stopped; root/D0/S1's windows leg was left to A185's own running legs); per-node wall 1,500 s with the verifier's process tree
  killed on timeout; frozen verifiers never edited (the frozen one re-RUN, unedited, on the kill certificates); read-only elsewhere; PYTHONDONTWRITEBYTECODE=1.
- Files: `attempts/A191-combined-cascade/{BRIEF.md, notes/{cascade191,price191}.md, code/{prio191,lines191,cert191,node191,run191,s3_191,fig191,report191,
  price191,frozen191,foldin191}.py, code/after_s2.ps1, results/{run191_l1_104_S2.jsonl, run191_l1_104_S3coarse.jsonl, run191_l1_104_S3.jsonl,
  run191_l1_153_S2.jsonl, report191.json, price191.json, lpres_*.json, s3_boxes_*.json}, certs/, figs/steps_l1_104_{S2,S3coarse}.svg, logs/}`,
  `docs/residue_ledger.md` s.4, `docs/budget.md` s.A k0 row + s.D item 13, registry row A191.
"""


def main():
    p = os.path.join(ROOT, "attempts", "REGISTRY.md")
    s = open(p, encoding="utf-8").read()
    if "| A191-combined-cascade |" not in s:
        i = s.find("| A193-highk-probes |")
        j = s.find("\n", i)
        s = s[:j] + "\n" + ROW + s[j:]
        open(p, "w", encoding="utf-8").write(s)
        print("registry row added")
    p = os.path.join(ROOT, "LOG.md")
    s = open(p, encoding="utf-8").read()
    if "A191-combined-cascade (Fable lead)" not in s:
        open(p, "a", encoding="utf-8").write(ENTRY)
        print("LOG entry appended")


if __name__ == "__main__":
    main()
