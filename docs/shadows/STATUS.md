# Shadow-gallery STATUS -- the checklist (generated, do not hand-edit)

Generated `2026-09-11 15:45` by `docs/shadows/status_gallery.py` (A162).  Rerun it at every pause:

```
python docs/shadows/status_gallery.py            # move DEAD pages, rewrite this file
python docs/shadows/status_gallery.py --dry-run  # print the plan, write nothing
```

**DEAD pages live in `docs/shadows/<gallery>/killed/`** -- they are `git mv`d there, never deleted.  ALIVE pages stay in place.  A page is DEAD only where a record gives a converged bound or a certificate `PASS`, at the page's **own tree tag** (A137 §C.3, "an id is not a node"), or where an ancestor is dead (monotonicity).

## Residue left

Of the 71 gallery pages the PI reviews, **47 are still ALIVE and 24 are now DEAD**. `k0v4` is 11 alive / 0 dead; `a57v4` is 36 alive / 24 dead; , out of 1,693 alive A57/A60 records -- 1,590 distinct nodes, k5_11 713, k5_16 552, trump5 (A60) 325 -- and the k0 lane holds its 11 converged-alive `k0_00` cells.  So the galleries are a **3.8 % sample of the live A57/A60 board** and the whole of the k0 residue: the pages are where the residue is *looked at*, not where it is *counted* -- the count is the work-owing number above.  Nothing in either gallery is dead by an unconverged LP: every DEAD page below carries a certificate.

## Counts

### Per gallery

| gallery | pages | ALIVE | DEAD |
|---|---|---|---|
| `k0v4` | 11 | 11 | 0 |
| `a57v4` | 60 | 36 | 24 |
| **total** | **71** | **47** | **24** |

### By family (A107/A128 shadow family of the page's panel N)

| family | ALIVE | DEAD |
|---|---|---|
| `K01` | 3 | 0 |
| `K03` | 1 | 0 |
| `K04` | 1 | 0 |
| `K05` | 1 | 0 |
| `K06` | 1 | 0 |
| `K20` | 1 | 0 |
| `S01` | 12 | 14 |
| `S02` | 4 | 5 |
| `S03` | 10 | 1 |
| `S05` | 1 | 0 |
| `S07` | 1 | 0 |
| `S08` | 2 | 0 |
| `S10` | 0 | 1 |
| `S11` | 1 | 1 |
| `S36` | 0 | 1 |
| `S38` | 1 | 0 |
| `S53` | 1 | 0 |
| `none` | 6 | 1 |

### By killing leaf

| attempt -- leaf | pages killed |
|---|---|
| A149 -- case-measure-certificate-v1 (exact cores, FROZEN verify_case) | 3 |
| A149 -- case-measure-certificate-v1 (ordinary leaf; only the core half-side changed) | 2 |
| A190 -- guard-line clause v5 [h=2.9078; tau 4.8896 < 5] | 2 |
| A136 -- A120 composition (YES local cert + all NO children) | 1 |
| A161 -- chord-limited lane [BL(1,0)] | 1 |
| A182 -- forced-first assignment: no admissible meeter assignment at BL(1,0) (notes/assignment.md Theorem ASSIGN; 188 multibox nodes) | 1 |
| A190 -- guard-line clause v5 [-; tau 4.0000 < 5] | 1 |
| A190 -- guard-line clause v5 [-; tau 4.7500 < 5] | 1 |
| A190 -- guard-line clause v5 [h=2.9078, h=2.8852; tau 4.8775 < 5] | 1 |
| A190 -- guard-line clause v5 [v=0.9929, v=0.9693; tau 4.8773 < 5] | 1 |
| A198 -- fastprop: A1/FC at BL(0,2): no free cell can hold a meeter (Theorem FC + Lemma A1 cells + exact reach + chord rows) | 1 |
| A198 -- fastprop: EmptyBox(H) at round1 (Theorem FC + Lemma A1 cells + exact reach + chord rows) | 1 |
| A200 -- quick killer [propagation; zero pad]: FC at BL(1,0): at most 1 distinct non-pin meeter(s) (H provably misses; roles []; anonymous cap 1 by CN: union diameter 0.8952 < 1) [pad 0: s0-only, WINDOW-PEND (s0-only; WINDOW-PENDING) | 1 |
| A202 -- fast30 stage 1 [stage1-propagation; g1 pad]: FC at TR(0,0): at most 1 distinct non-pin meeter(s) (H provably misses; roles []; anonymous cap 1 by A1: 1 alive cell(s)) | 1 |
| A205 -- cliptree205 clip tree [g1 pad; 2 nodes, depth 0]: every branch of the clip tree DEAD: Rr1 root<-None by EmptyBox r1 | 1 |
| A205 -- cliptree205 clip tree [g1 pad; 3 nodes, depth 1]: every branch of the clip tree DEAD: R.1 TR(0,0)<-[23] by FC r1; R.2 TR(0,0)<-[24] by EmptyBox r3 | 1 |
| A205 -- cliptree205 clip tree [g1 pad; 5 nodes, depth 1]: every branch of the clip tree DEAD: R.1 BR(0,1)<-[10] by FC r1; R.2 BR(0,1)<-[15] by FC r2; R.3 BR(0,1)<-[22] by EmptyBox r1; R.4 BR(0,1)<-[23] by COUNT r1 | 1 |
| A206 -- namedsplit206 clip tree with Rule NS [g1 pad; 8 nodes, depth 2, 0 NS splits]: every branch DEAD under Rule NS: R.1 BR(0,1)<-[16] by EmptyBox r2; R.2.1 TL(1,0)<-[7, 9] by FC r1; R.2.2 TL(1,0)<-[7, 14] by FC r1; R.2.3 TL(1,0)<-[8, 9] by FC  | 1 |
| A206 -- namedsplit206 clip tree with Rule NS [g1 pad; 8 nodes, depth 2, 0 NS splits]: every branch DEAD under Rule NS: R.1 BR(0,1)<-[16] by FC r1; R.2.1 TL(1,0)<-[7, 9] by FC r1; R.2.2 TL(1,0)<-[7, 14] by FC r1; R.2.3 TL(1,0)<-[8, 9] by FC r1; R. | 1 |
| A57 tree -- PASS -- case-measure-certificate-v1 in A57's own tree certs (k5_16_interior_L1) | 1 |

## Checklist -- `k0v4`: the k0 residue gallery v4 (converged-alive k0_00 cells)

| page | node | class | level | family | status | leaf | attempt | date | subtree cost (CPU-h, A142 rank) |
|---|---|---|---|---|---|---|---|---|---|
| [ ] [`l1_071.svg`](l1_071.svg) | `l1_071` | `k0_00` | 1 | `K01` | **ALIVE** | -- | -- | -- | 2.88 |
| [ ] [`l1_104.svg`](l1_104.svg) | `l1_104` | `k0_00` | 1 | `K04` | **ALIVE** | -- | -- | -- | 2.88 |
| [ ] [`l1_124.svg`](l1_124.svg) | `l1_124` | `k0_00` | 1 | `none` | **ALIVE** | -- | -- | -- | 2.88 |
| [ ] [`l1_148.svg`](l1_148.svg) | `l1_148` | `k0_00` | 1 | `K01` | **ALIVE** | -- | -- | -- | 2.88 |
| [ ] [`l1_153.svg`](l1_153.svg) | `l1_153` | `k0_00` | 1 | `none` | **ALIVE** | -- | -- | -- | 2.88 |
| [ ] [`l1_158.svg`](l1_158.svg) | `l1_158` | `k0_00` | 1 | `none` | **ALIVE** | -- | -- | -- | 2.88 |
| [ ] [`l1_159.svg`](l1_159.svg) | `l1_159` | `k0_00` | 1 | `K06` | **ALIVE** | -- | -- | -- | 2.88 |
| [ ] [`l2_p114_001.svg`](l2_p114_001.svg) | `l2_p114_001` | `k0_00` | 2 | `K20` | **ALIVE** | -- | -- | -- | 2.27 |
| [ ] [`l2_p65_101.svg`](l2_p65_101.svg) | `l2_p65_101` | `k0_00` | 2 | `K01` | **ALIVE** | -- | -- | -- | 2.27 |
| [ ] [`l2_p65_111.svg`](l2_p65_111.svg) | `l2_p65_111` | `k0_00` | 2 | `K03` | **ALIVE** | -- | -- | -- | 2.27 |
| [ ] [`l2_p74_001.svg`](l2_p74_001.svg) | `l2_p74_001` | `k0_00` | 2 | `K05` | **ALIVE** | -- | -- | -- | 2.27 |

## Checklist -- `a57v4`: the A57 / A60 review gallery v4

| page | node | class | level | family | status | leaf | attempt | date | subtree cost (CPU-h, A142 rank) |
|---|---|---|---|---|---|---|---|---|---|
| [x] [`c0_Y0076.svg`](killed/c0_Y0076.svg) | `c0_Y0076` | `trump5_j0` | 1 | `S02` | **DEAD** | fastprop: A1/FC at BL(0,2): no free cell can hold a meeter (Theorem FC + Lemma A1 cells + exact reach + chord rows) | A198 | 2026-09-10 | 2.88 (rank 17) |
| [x] [`c0_Y0175.svg`](killed/c0_Y0175.svg) | `c0_Y0175` | `trump5_j0` | 1 | `S01` | **DEAD** | guard-line clause v5 [v=0.9929, v=0.9693; tau 4.8773 < 5] | A190 | 2026-09-10 | 2.88 (rank 21) |
| [x] [`c0_Y0939.svg`](killed/c0_Y0939.svg) | `c0_Y0939` | `trump5_j0` | 1 | `S01` | **DEAD** | case-measure-certificate-v1 (exact cores, FROZEN verify_case) | A149 | 2026-09-08 | 2.88 (rank 5) |
| [x] [`c0_Y0942.svg`](killed/c0_Y0942.svg) | `c0_Y0942` | `trump5_j0` | 1 | `S01` | **DEAD** | case-measure-certificate-v1 (exact cores, FROZEN verify_case) | A149 | 2026-09-08 | 2.88 (rank 6) |
| [x] [`c0_Y0952.svg`](killed/c0_Y0952.svg) | `c0_Y0952` | `trump5_j0` | 1 | `S01` | **DEAD** | guard-line clause v5 [h=2.9078; tau 4.8896 < 5] | A190 | 2026-09-10 | 2.88 (rank 11) |
| [x] [`c0_Y0959.svg`](killed/c0_Y0959.svg) | `c0_Y0959` | `trump5_j0` | 1 | `S01` | **DEAD** | guard-line clause v5 [h=2.9078; tau 4.8896 < 5] | A190 | 2026-09-10 | 2.88 (rank 7) |
| [x] [`c0_Y1038.svg`](killed/c0_Y1038.svg) | `c0_Y1038` | `trump5_j0` | 1 | `S01` | **DEAD** | case-measure-certificate-v1 (exact cores, FROZEN verify_case) | A149 | 2026-09-08 | 2.88 (rank 9) |
| [x] [`k5_11_interior_Y0147.svg`](killed/k5_11_interior_Y0147.svg) | `k5_11_interior_Y0147` | `k5_11` | 1 | `S01` | **DEAD** | guard-line clause v5 [h=2.9078, h=2.8852; tau 4.8775 < 5] | A190 | 2026-09-10 | 2.88 (rank 39) |
| [x] [`k5_11_interior_Y0275.svg`](killed/k5_11_interior_Y0275.svg) | `k5_11_interior_Y0275` | `k5_11` | 1 | `none` | **DEAD** | case-measure-certificate-v1 (ordinary leaf; only the core half-side changed) | A149 | 2026-09-08 | 2.88 (rank 16) |
| [x] [`k5_11_interior_Y0308.svg`](killed/k5_11_interior_Y0308.svg) | `k5_11_interior_Y0308` | `k5_11` | 1 | `S01` | **DEAD** | cliptree205 clip tree [g1 pad; 3 nodes, depth 1]: every branch of the clip tree DEAD: R.1 TR(0,0)<-[23] by FC r1; R.2 TR(0,0)<-[24] by EmptyBox r3 | A205 | 2026-09-11 | 2.88 (rank 17) |
| [x] [`k5_11_interior_Y0985.svg`](killed/k5_11_interior_Y0985.svg) | `k5_11_interior_Y0985` | `k5_11` | 1 | `S01` | **DEAD** | namedsplit206 clip tree with Rule NS [g1 pad; 8 nodes, depth 2, 0 NS splits]: every branch DEAD under Rule NS: R.1 BR(0,1)<-[16] by EmptyBox r2; R.2.1 TL(1,0)<-[7, 9] by FC r1; R.2.2 TL(1,0)<-[7, 14] by FC r1; R.2.3 TL(1,0)<-[8, 9] by FC  | A206 | 2026-09-11 | 2.88 (rank 19) |
| [x] [`k5_11_interior_Y1104.svg`](killed/k5_11_interior_Y1104.svg) | `k5_11_interior_Y1104` | `k5_11` | 1 | `S10` | **DEAD** | namedsplit206 clip tree with Rule NS [g1 pad; 8 nodes, depth 2, 0 NS splits]: every branch DEAD under Rule NS: R.1 BR(0,1)<-[16] by FC r1; R.2.1 TL(1,0)<-[7, 9] by FC r1; R.2.2 TL(1,0)<-[7, 14] by FC r1; R.2.3 TL(1,0)<-[8, 9] by FC r1; R. | A206 | 2026-09-11 | 11.59 (rank 1) |
| [x] [`k5_11_interior_Y1110.svg`](killed/k5_11_interior_Y1110.svg) | `k5_11_interior_Y1110` | `k5_11` | 1 | `S36` | **DEAD** | fast30 stage 1 [stage1-propagation; g1 pad]: FC at TR(0,0): at most 1 distinct non-pin meeter(s) (H provably misses; roles []; anonymous cap 1 by A1: 1 alive cell(s)) | A202 | 2026-09-10 | 2.88 (rank 5) |
| [x] [`k5_16_interior_Y0027.svg`](killed/k5_16_interior_Y0027.svg) | `k5_16_interior_Y0027` | `k5_16` | 1 | `S01` | **DEAD** | guard-line clause v5 [-; tau 4.0000 < 5] | A190 | 2026-09-10 | 2.88 (rank 21) |
| [x] [`k5_16_interior_Y0054.svg`](killed/k5_16_interior_Y0054.svg) | `k5_16_interior_Y0054` | `k5_16` | 1 | `S02` | **DEAD** | quick killer [propagation; zero pad]: FC at BL(1,0): at most 1 distinct non-pin meeter(s) (H provably misses; roles []; anonymous cap 1 by CN: union diameter 0.8952 < 1) [pad 0: s0-only, WINDOW-PEND (s0-only; WINDOW-PENDING) | A200 | 2026-09-10 | 2.88 (rank 42) |
| [x] [`k5_16_interior_Y0083.svg`](killed/k5_16_interior_Y0083.svg) | `k5_16_interior_Y0083` | `k5_16` | 1 | `S02` | **DEAD** | PASS -- case-measure-certificate-v1 in A57's own tree certs (k5_16_interior_L1) | A57 tree | 2026-09-01 | 4.53 (rank 3) |
| [x] [`k5_16_interior_Y0191.svg`](killed/k5_16_interior_Y0191.svg) | `k5_16_interior_Y0191` | `k5_16` | 1 | `S03` | **DEAD** | fastprop: EmptyBox(H) at round1 (Theorem FC + Lemma A1 cells + exact reach + chord rows) | A198 | 2026-09-10 | 2.88 (rank 22) |
| [x] [`k5_16_interior_Y0230.svg`](killed/k5_16_interior_Y0230.svg) | `k5_16_interior_Y0230` | `k5_16` | 1 | `S01` | **DEAD** | guard-line clause v5 [-; tau 4.7500 < 5] | A190 | 2026-09-10 | 2.88 (rank 45) |
| [x] [`k5_16_interior_Y0275.svg`](killed/k5_16_interior_Y0275.svg) | `k5_16_interior_Y0275` | `k5_16` | 1 | `S11` | **DEAD** | case-measure-certificate-v1 (ordinary leaf; only the core half-side changed) | A149 | 2026-09-08 | 2.88 (rank 24) |
| [x] [`k5_16_interior_Y0491.svg`](killed/k5_16_interior_Y0491.svg) | `k5_16_interior_Y0491` | `k5_16` | 1 | `S01` | **DEAD** | cliptree205 clip tree [g1 pad; 2 nodes, depth 0]: every branch of the clip tree DEAD: Rr1 root<-None by EmptyBox r1 | A205 | 2026-09-11 | 2.88 (rank 49) |
| [x] [`k5_16_interior_Y0565.svg`](killed/k5_16_interior_Y0565.svg) | `k5_16_interior_Y0565` | `k5_16` | 1 | `S01` | **DEAD** | cliptree205 clip tree [g1 pad; 5 nodes, depth 1]: every branch of the clip tree DEAD: R.1 BR(0,1)<-[10] by FC r1; R.2 BR(0,1)<-[15] by FC r2; R.3 BR(0,1)<-[22] by EmptyBox r1; R.4 BR(0,1)<-[23] by COUNT r1 | A205 | 2026-09-11 | 2.88 (rank 50) |
| [x] [`k5_16_interior_Y0839.svg`](killed/k5_16_interior_Y0839.svg) | `k5_16_interior_Y0839` | `k5_16` | 1 | `S01` | **DEAD** | forced-first assignment: no admissible meeter assignment at BL(1,0) (notes/assignment.md Theorem ASSIGN; 188 multibox nodes) | A182 | 2026-09-10 | 2.88 (rank 26) |
| [x] [`k5_16_interior_Y0842.svg`](killed/k5_16_interior_Y0842.svg) | `k5_16_interior_Y0842` | `k5_16` | 1 | `S02` | **DEAD** | chord-limited lane [BL(1,0)] | A161 | 2026-09-08 | 2.88 (rank 27) |
| [x] [`k5_16_interior_Y0941.svg`](killed/k5_16_interior_Y0941.svg) | `k5_16_interior_Y0941` | `k5_16` | 1 | `S02` | **DEAD** | A120 composition (YES local cert + all NO children) | A136 | 2026-09-09 | 2.88 (rank 29) |
| [ ] [`c0_Y0169.svg`](c0_Y0169.svg) | `c0_Y0169` | `trump5_j0` | 1 | `S38` | **ALIVE** | -- | -- | -- | 2.88 (rank 19) |
| [ ] [`c0_Y0171.svg`](c0_Y0171.svg) | `c0_Y0171` | `trump5_j0` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 20) |
| [ ] [`c0_Y0215.svg`](c0_Y0215.svg) | `c0_Y0215` | `trump5_j0` | 1 | `S11` | **ALIVE** | -- | -- | -- | 2.88 (rank 23) |
| [ ] [`c0_Y0223.svg`](c0_Y0223.svg) | `c0_Y0223` | `trump5_j0` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 24) |
| [ ] [`c0_Y0255.svg`](c0_Y0255.svg) | `c0_Y0255` | `trump5_j0` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 16) |
| [ ] [`c0_Y0257.svg`](c0_Y0257.svg) | `c0_Y0257` | `trump5_j0` | 1 | `S08` | **ALIVE** | -- | -- | -- | 2.88 (rank 13) |
| [ ] [`c0_Y0258.svg`](c0_Y0258.svg) | `c0_Y0258` | `trump5_j0` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 3) |
| [ ] [`c0_Y0695.svg`](c0_Y0695.svg) | `c0_Y0695` | `trump5_j0` | 1 | `S02` | **ALIVE** | -- | -- | -- | 2.88 (rank 15) |
| [ ] [`c0_Y0787.svg`](c0_Y0787.svg) | `c0_Y0787` | `trump5_j0` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 4) |
| [ ] [`c0_Y0788.svg`](c0_Y0788.svg) | `c0_Y0788` | `trump5_j0` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 12) |
| [ ] [`c0_Y1033.svg`](c0_Y1033.svg) | `c0_Y1033` | `trump5_j0` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 8) |
| [ ] [`f1_L10_0003.svg`](f1_L10_0003.svg) | `f1_L10_0003` | `trump5_j0` | 1 | `S07` | **ALIVE** | -- | -- | -- | 2.88 (rank 10) |
| [ ] [`k5_11_interior_Y0130.svg`](k5_11_interior_Y0130.svg) | `k5_11_interior_Y0130` | `k5_11` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 12) |
| [ ] [`k5_11_interior_Y0202.svg`](k5_11_interior_Y0202.svg) | `k5_11_interior_Y0202` | `k5_11` | 1 | `S05` | **ALIVE** | -- | -- | -- | 2.88 (rank 40) |
| [ ] [`k5_11_interior_Y0662.svg`](k5_11_interior_Y0662.svg) | `k5_11_interior_Y0662` | `k5_11` | 1 | `none` | **ALIVE** | -- | -- | -- | 2.88 (rank 9) |
| [ ] [`k5_11_interior_Y0672.svg`](k5_11_interior_Y0672.svg) | `k5_11_interior_Y0672` | `k5_11` | 1 | `S53` | **ALIVE** | -- | -- | -- | 4.53 (rank 2) |
| [ ] [`k5_11_interior_Y0738.svg`](k5_11_interior_Y0738.svg) | `k5_11_interior_Y0738` | `k5_11` | 1 | `S02` | **ALIVE** | -- | -- | -- | 3.76 (rank 4) |
| [ ] [`k5_16_interior_Y0044.svg`](k5_16_interior_Y0044.svg) | `k5_16_interior_Y0044` | `k5_16` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 38) |
| [ ] [`k5_16_interior_Y0099.svg`](k5_16_interior_Y0099.svg) | `k5_16_interior_Y0099` | `k5_16` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 43) |
| [ ] [`k5_16_interior_Y0249.svg`](k5_16_interior_Y0249.svg) | `k5_16_interior_Y0249` | `k5_16` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 33) |
| [ ] [`k5_16_interior_Y0325.svg`](k5_16_interior_Y0325.svg) | `k5_16_interior_Y0325` | `k5_16` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 46) |
| [ ] [`k5_16_interior_Y0380.svg`](k5_16_interior_Y0380.svg) | `k5_16_interior_Y0380` | `k5_16` | 1 | `S02` | **ALIVE** | -- | -- | -- | 2.88 (rank 47) |
| [ ] [`k5_16_interior_Y0402.svg`](k5_16_interior_Y0402.svg) | `k5_16_interior_Y0402` | `k5_16` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 35) |
| [ ] [`k5_16_interior_Y0436.svg`](k5_16_interior_Y0436.svg) | `k5_16_interior_Y0436` | `k5_16` | 1 | `none` | **ALIVE** | -- | -- | -- | 2.88 (rank 48) |
| [ ] [`k5_16_interior_Y0460.svg`](k5_16_interior_Y0460.svg) | `k5_16_interior_Y0460` | `k5_16` | 1 | `none` | **ALIVE** | -- | -- | -- | 2.88 (rank 32) |
| [ ] [`k5_16_interior_Y0500.svg`](k5_16_interior_Y0500.svg) | `k5_16_interior_Y0500` | `k5_16` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 37) |
| [ ] [`k5_16_interior_Y0660.svg`](k5_16_interior_Y0660.svg) | `k5_16_interior_Y0660` | `k5_16` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 52) |
| [ ] [`k5_16_interior_Y0719.svg`](k5_16_interior_Y0719.svg) | `k5_16_interior_Y0719` | `k5_16` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 54) |
| [ ] [`k5_16_interior_Y0865.svg`](k5_16_interior_Y0865.svg) | `k5_16_interior_Y0865` | `k5_16` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 56) |
| [ ] [`k5_16_interior_Y0881.svg`](k5_16_interior_Y0881.svg) | `k5_16_interior_Y0881` | `k5_16` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 28) |
| [ ] [`k5_16_interior_Y0991.svg`](k5_16_interior_Y0991.svg) | `k5_16_interior_Y0991` | `k5_16` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 57) |
| [ ] [`k5_16_interior_Y1022.svg`](k5_16_interior_Y1022.svg) | `k5_16_interior_Y1022` | `k5_16` | 1 | `S03` | **ALIVE** | -- | -- | -- | 2.88 (rank 59) |
| [ ] [`k5_16_interior_Y1056.svg`](k5_16_interior_Y1056.svg) | `k5_16_interior_Y1056` | `k5_16` | 1 | `S08` | **ALIVE** | -- | -- | -- | 2.88 (rank 31) |
| [ ] [`k5_16_interior_Y1110.svg`](k5_16_interior_Y1110.svg) | `k5_16_interior_Y1110` | `k5_16` | 1 | `S02` | **ALIVE** | -- | -- | -- | 2.88 (rank 61) |
| [ ] [`k5_16_interior_Y1117.svg`](k5_16_interior_Y1117.svg) | `k5_16_interior_Y1117` | `k5_16` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 36) |
| [ ] [`slack0.02_c0_Y0272.svg`](slack0.02_c0_Y0272.svg) | `slack0.02_c0_Y0272` | `trump5_j0` | 1 | `S01` | **ALIVE** | -- | -- | -- | 2.88 (rank 1) |

**The kills, with their certificates.**

* `k5_11_interior_Y1104` (tree tag `k5_11_interior_G1`) -- direct kill record, **A206** by `namedsplit206 clip tree with Rule NS [g1 pad; 8 nodes, depth 2, 0 NS splits]: every branch DEAD under Rule NS: R.1 BR(0,1)<-[16] by FC r1; R.2.1 TL(1,0)<-[7, 9] by FC r1; R.2.2 TL(1,0)<-[7, 14] by FC r1; R.2.3 TL(1,0)<-[8, 9] by FC r1; R.`; certificate `attempts/A206-named-split/certs/namedsplit206_k5_11_interior_Y1104.json`; attributed by *id occurs in exactly one tree*; 1 record(s) agree.
* `k5_16_interior_Y0083` (tree tag `k5_16_interior_L1`) -- direct kill record, **A57 tree** by `PASS -- case-measure-certificate-v1 in A57's own tree certs (k5_16_interior_L1)`; certificate `attempts/A57-shadow-trees/certs/tree/k5_16_interior_L1/k5_16_interior_Y0083.json`; attributed by *the record's own tree jsonl (tag is the file)*; 2 record(s) agree.  **An id is not a node (A137 §C.3): the `k5_16_interior_G1` node of this id is still ALIVE** -- only the `k5_16_interior_L1` node is dead, and this page was drawn from the `k5_16_interior_L1` record.
* `k5_11_interior_Y1110` (tree tag `k5_11_interior_G1`) -- direct kill record, **A202** by `fast30 stage 1 [stage1-propagation; g1 pad]: FC at TR(0,0): at most 1 distinct non-pin meeter(s) (H provably misses; roles []; anonymous cap 1 by A1: 1 alive cell(s))`; certificate `attempts/A202-fast30/certs/f30_k5_11_interior_Y1110_g1_s1.json`; attributed by *prior tau matched the tree record*; 3 record(s) agree.
* `k5_11_interior_Y0275` (tree tag `k5_11_interior_G1`) -- direct kill record, **A149** by `case-measure-certificate-v1 (ordinary leaf; only the core half-side changed)`; certificate `attempts/A149-a57-reprice/certs/k5_11_interior_Y0275__exall.json`; attributed by *prior tau matched the tree record*; 3 record(s) agree.
* `k5_11_interior_Y0308` (tree tag `k5_11_interior_G1`) -- direct kill record, **A205** by `cliptree205 clip tree [g1 pad; 3 nodes, depth 1]: every branch of the clip tree DEAD: R.1 TR(0,0)<-[23] by FC r1; R.2 TR(0,0)<-[24] by EmptyBox r3`; certificate `attempts/A205-clip-tree/certs/cliptree205_k5_11_interior_Y0308.json`; attributed by *prior tau matched the tree record*; 1 record(s) agree.
* `k5_11_interior_Y0985` (tree tag `k5_11_interior_G1`) -- direct kill record, **A206** by `namedsplit206 clip tree with Rule NS [g1 pad; 8 nodes, depth 2, 0 NS splits]: every branch DEAD under Rule NS: R.1 BR(0,1)<-[16] by EmptyBox r2; R.2.1 TL(1,0)<-[7, 9] by FC r1; R.2.2 TL(1,0)<-[7, 14] by FC r1; R.2.3 TL(1,0)<-[8, 9] by FC `; certificate `attempts/A206-named-split/certs/namedsplit206_k5_11_interior_Y0985.json`; attributed by *id occurs in exactly one tree*; 1 record(s) agree.
* `k5_16_interior_Y0027` (tree tag `k5_16_interior_G1`) -- direct kill record, **A190** by `guard-line clause v5 [-; tau 4.0000 < 5]`; certificate `attempts/A190-guardline-clause/certs/k5_16_interior_Y0027.json`; attributed by *prior tau matched the tree record*; 3 record(s) agree.
* `k5_16_interior_Y0191` (tree tag `k5_16_interior_G1`) -- direct kill record, **A198** by `fastprop: EmptyBox(H) at round1 (Theorem FC + Lemma A1 cells + exact reach + chord rows)`; certificate `attempts/A198-fastprop/certs/fp198_k5_16_interior_Y0191.json`; attributed by *prior tau matched 2 trees (all)*; 2 record(s) agree.
* `k5_16_interior_Y0275` (tree tag `k5_16_interior_G1`) -- direct kill record, **A149** by `case-measure-certificate-v1 (ordinary leaf; only the core half-side changed)`; certificate `attempts/A149-a57-reprice/certs/k5_16_interior_Y0275__exall.json`; attributed by *prior tau matched the tree record*; 3 record(s) agree.
* `k5_16_interior_Y0839` (tree tag `k5_16_interior_G1`) -- direct kill record, **A182** by `forced-first assignment: no admissible meeter assignment at BL(1,0) (notes/assignment.md Theorem ASSIGN; 188 multibox nodes)`; certificate `attempts/A180-forced-first-assignment/results/trees/k5_16_interior_Y0839.json`; attributed by *id occurs in exactly one tree*; 2 record(s) agree.
* `k5_16_interior_Y0842` (tree tag `k5_16_interior_G1`) -- direct kill record, **A161** by `chord-limited lane [BL(1,0)]`; certificate `attempts/A161-chord-lane/certs/cl_k5_16_interior_Y0842__BL1_0.json`; attributed by *id occurs in exactly one tree*; 4 record(s) agree.
* `k5_16_interior_Y0941` (tree tag `k5_16_interior_G1`) -- direct kill record, **A136** by `A120 composition (YES local cert + all NO children)`; certificate `attempts/A163-s02-other-frames/certs/S02_k5_16_A163chain_BOTH_base_r0.20_h10.00_nof0_+00.00.tcert.json.gz`; attributed by *applies_to_tags (A137 fold137)*; 4 record(s) agree.
* `k5_11_interior_Y0147` (tree tag `k5_11_interior_G1`) -- direct kill record, **A190** by `guard-line clause v5 [h=2.9078, h=2.8852; tau 4.8775 < 5]`; certificate `attempts/A190-guardline-clause/certs/k5_11_interior_Y0147.json`; attributed by *prior tau matched the tree record*; 1 record(s) agree.
* `k5_16_interior_Y0054` (tree tag `k5_16_interior_G1`) -- direct kill record, **A200** by `quick killer [propagation; zero pad]: FC at BL(1,0): at most 1 distinct non-pin meeter(s) (H provably misses; roles []; anonymous cap 1 by CN: union diameter 0.8952 < 1) [pad 0: s0-only, WINDOW-PEND (s0-only; WINDOW-PENDING)`; certificate `attempts/A200-k516-quick/certs/q200_k5_16_interior_Y0054_pad0.json`; attributed by *id occurs in exactly one tree*; 4 record(s) agree.
* `k5_16_interior_Y0230` (tree tag `k5_16_interior_G1`) -- direct kill record, **A190** by `guard-line clause v5 [-; tau 4.7500 < 5]`; certificate `attempts/A190-guardline-clause/certs/k5_16_interior_Y0230.json`; attributed by *prior tau matched the tree record*; 1 record(s) agree.
* `k5_16_interior_Y0491` (tree tag `k5_16_interior_G1`) -- direct kill record, **A205** by `cliptree205 clip tree [g1 pad; 2 nodes, depth 0]: every branch of the clip tree DEAD: Rr1 root<-None by EmptyBox r1`; certificate `attempts/A205-clip-tree/certs/cliptree205_k5_16_interior_Y0491.json`; attributed by *prior tau matched 2 trees (all)*; 1 record(s) agree.
* `k5_16_interior_Y0565` (tree tag `k5_16_interior_G1`) -- direct kill record, **A205** by `cliptree205 clip tree [g1 pad; 5 nodes, depth 1]: every branch of the clip tree DEAD: R.1 BR(0,1)<-[10] by FC r1; R.2 BR(0,1)<-[15] by FC r2; R.3 BR(0,1)<-[22] by EmptyBox r1; R.4 BR(0,1)<-[23] by COUNT r1`; certificate `attempts/A205-clip-tree/certs/cliptree205_k5_16_interior_Y0565.json`; attributed by *prior tau matched the tree record*; 1 record(s) agree.
* `c0_Y0939` (tree tag `trump5_j0`) -- direct kill record, **A149** by `case-measure-certificate-v1 (exact cores, FROZEN verify_case)`; certificate `attempts/A149-a57-reprice/certs/a60/c0_Y0939__exH.json`; attributed by *single-tree camp*; 2 record(s) agree.
* `c0_Y0942` (tree tag `trump5_j0`) -- direct kill record, **A149** by `case-measure-certificate-v1 (exact cores, FROZEN verify_case)`; certificate `attempts/A149-a57-reprice/certs/a60/c0_Y0942__exH.json`; attributed by *single-tree camp*; 2 record(s) agree.
* `c0_Y0959` (tree tag `trump5_j0`) -- direct kill record, **A190** by `guard-line clause v5 [h=2.9078; tau 4.8896 < 5]`; certificate `attempts/A190-guardline-clause/certs/c0_Y0959.json`; attributed by *single-tree camp*; 1 record(s) agree.
* `c0_Y1038` (tree tag `trump5_j0`) -- direct kill record, **A149** by `case-measure-certificate-v1 (exact cores, FROZEN verify_case)`; certificate `attempts/A149-a57-reprice/certs/a60/c0_Y1038__exH.json`; attributed by *single-tree camp*; 2 record(s) agree.
* `c0_Y0952` (tree tag `trump5_j0`) -- direct kill record, **A190** by `guard-line clause v5 [h=2.9078; tau 4.8896 < 5]`; certificate `attempts/A190-guardline-clause/certs/c0_Y0952.json`; attributed by *single-tree camp*; 1 record(s) agree.
* `c0_Y0076` (tree tag `trump5_j0`) -- direct kill record, **A198** by `fastprop: A1/FC at BL(0,2): no free cell can hold a meeter (Theorem FC + Lemma A1 cells + exact reach + chord rows)`; certificate `attempts/A198-fastprop/certs/fp198_c0_Y0076.json`; attributed by *single-tree camp*; 2 record(s) agree.
* `c0_Y0175` (tree tag `trump5_j0`) -- direct kill record, **A190** by `guard-line clause v5 [v=0.9929, v=0.9693; tau 4.8773 < 5]`; certificate `attempts/A190-guardline-clause/certs/c0_Y0175.json`; attributed by *single-tree camp*; 1 record(s) agree.

**Review-sheet flag.** 1 page(s) in `review_a57v4.csv` carry `eta < 0` (that is `tau < budget`, a kill) while the review sheet's `verdict` column says `ALIVE-at-LP`: `k5_16_interior_Y0083` (tau 4.500000000, budget 5, eta -5.000e-01, now **DEAD**).  The `verdict` column is stale for these; the status above is taken from the campaign records, not from that column.

## Where the verdicts came from

| source | records read | of which kills |
|---|---|---|
| `A136 closures136.jsonl` | 30 | 30 |
| `A137 clipkills137.jsonl` | 159 | 159 |
| `A140 exactcore140.jsonl` | 12 | 1 |
| `A141 polycore_lane_kills.jsonl` | 293 | 293 |
| `A149 a60_reemit_g0.jsonl` | 42 | 10 |
| `A149 a60_reemit_g1.jsonl` | 48 | 12 |
| `A149 a60_reemit_g2.jsonl` | 45 | 13 |
| `A149 a60_reemit_g3.jsonl` | 38 | 11 |
| `A149 a60_reemit_g4.jsonl` | 25 | 24 |
| `A149 a60_reemit_g5.jsonl` | 19 | 17 |
| `A149 a60_reemit_smoke.jsonl` | 1 | 0 |
| `A149 exact_reemit_m0.jsonl` | 9 | 7 |
| `A149 exact_reemit_m1.jsonl` | 9 | 6 |
| `A149 exact_reemit_prio.jsonl` | 1 | 1 |
| `A149 exact_reemit_w0.jsonl` | 1 | 0 |
| `A149 exact_reemit_w1.jsonl` | 1 | 0 |
| `A149 exact_reemit_w2.jsonl` | 47 | 8 |
| `A149 exact_reemit_w3.jsonl` | 44 | 7 |
| `A149 exact_reemit_w4.jsonl` | 41 | 20 |
| `A149 exact_reemit_w5.jsonl` | 37 | 14 |
| `A149 exact_reemit_w6.jsonl` | 27 | 15 |
| `A149 exact_reemit_w7.jsonl` | 23 | 15 |
| `A149 poly149.jsonl` | 1 | 0 |
| `A156 lp156_d1118.jsonl` | 132 | 96 |
| `A156 lp156_d1119.jsonl` | 127 | 90 |
| `A156 lp156_d1606L2.jsonl` | 93 | 83 |
| `A158 no158.jsonl` | 66 | 0 |
| `A158 yescert158.jsonl` | 6 | 0 |
| `A161 t3_dedup.jsonl` | 98 | 98 |
| `A167 pass_s0.jsonl` | 7 | 7 |
| `A167 pass_s1.jsonl` | 10 | 10 |
| `A182 assign182.jsonl` | 2 | 2 |
| `A189 noroom189.jsonl` | 6 | 0 |
| `A190 run190.jsonl` | 18 | 18 |
| `A197 slotpair197.jsonl` | 1 | 1 |
| `A198 fastprop198.jsonl` | 2 | 2 |
| `A199 seal199.jsonl` | 1 | 1 |
| `A200 quick200.jsonl` | 2 | 2 |
| `A202 fast30.jsonl` | 8 | 8 |
| `A203 csp203.jsonl` | 3 | 3 |
| `A205 cliptree205.jsonl` | 7 | 7 |
| `A206 namedsplit206.jsonl` | 2 | 2 |
| `A57 tree jsonl (k5_11_interior_G1) -- dead rows only` | 780 | 780 |
| `A57 tree jsonl (k5_11_interior_G1_D2) -- dead rows only` | 729 | 729 |
| `A57 tree jsonl (k5_11_interior_G1_D2_D2) -- dead rows only` | 101 | 101 |
| `A57 tree jsonl (k5_11_interior_G1_D2_D2_D2) -- dead rows only` | 26 | 26 |
| `A57 tree jsonl (k5_11_interior_L1) -- dead rows only` | 175 | 175 |
| `A57 tree jsonl (k5_11_interior_L1_D2) -- dead rows only` | 22 | 22 |
| `A57 tree jsonl (k5_16_interior_G1) -- dead rows only` | 746 | 746 |
| `A57 tree jsonl (k5_16_interior_G1_D2) -- dead rows only` | 389 | 389 |
| `A57 tree jsonl (k5_16_interior_L1) -- dead rows only` | 98 | 98 |
| `A57 tree jsonl (k5_16_interior_L1_D2) -- dead rows only` | 8 | 8 |
| `A96 a120_closures.jsonl` | 174 | 132 |
| `clipkill certs (attempts/*/certs/**)` | 342 | 342 |
| `ledger superseded_by_backlog_A137.jsonl` | 581 | 581 |
| `ledger superseded_by_exactcore_A137.jsonl` | 46 | 46 |
| `ledger superseded_by_exactcore_A149.jsonl` | 93 | 93 |
| `ledger superseded_by_exactcore_a60_A149.jsonl` | 87 | 87 |
| `ledger superseded_by_tight_core.jsonl` | 70 | 70 |

`*__exall.json` is **not** a kill record (A148's rule: it exists on LOST-KILL / TOO-TIGHT / FAIL too) and is not scanned.  A158's `yescert158.jsonl` rows say `verdict = "KILL"` with `kill = false` and are counted as **not** kills; in particular **`c0_Y0076`'s NO child is NOT a kill** (A158b: the YES child converges at `tau = budget`, `eta = 0`).  A140's `exactcore140.jsonl` kills only where `kills_converged` and the certificate `PASS` -- `l1_148`, `l2_p65_101` and `l2_p65_111` have `kills = true` with `converged = false` and are **not** kills (A124: a non-converged `tau` was never a bound).

### Records REFUSED -- tree tag unresolved (A137 §C.3)

118 record(s) name an id that exists in more than one tree and carry neither an `applies_to_tags` field nor a prior `tau` to match, so the tree they belong to cannot be read off them.  **115 of them are redundant** -- the same id is killed with an explicit tag by another record -- and **3 leave a node unattributed**.  A refusal never kills a page: the certificate is correct for the node it names, but this script will not guess which tree that is.

| source | id | leaf | why refused | redundant? |
|---|---|---|---|---|
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0186_D00_D05` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0978_D07_D03` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y1140_D07_D04` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0978_D06_D00` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0978_D06_D04` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0978_D06_D05` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0636_D06_D00` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0636_D06_D02` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0978_D04_D05` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0636_D04_D00` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0636_D04_D02` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0186_D01_D03` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0414_D07_D04` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0414_D07_D05` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0954_D00_D00` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A137 clipkills137.jsonl` | `k5_11_interior_Y0954_D00_D01` | KILL-BY-LOGIC (pin-clip T5''' at the exact pin core) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0300` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `ledger superseded_by_tight_core.jsonl` | `k5_16_interior_Y0299` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0036_D02_D05` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0036_D03_D00` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0036_D03_D01` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0036_D03_D04` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0036_D07_D00` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0036_D07_D04` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0186_D00_D01` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `ledger superseded_by_tight_core.jsonl` | `k5_11_interior_Y0186_D00_D00_D03` | T5-prime tight common-inscribed core (A96) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D00` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D04` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D05` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D00` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D04` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D05` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D00` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D04` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D05` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D00` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D04` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D05` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D00` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D04` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A96 a120_closures.jsonl` | `k5_11_interior_Y0036_D07_D05` | A120 composition | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0029` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0030` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0053` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BR(0,1)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0138` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TR(0,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0192` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BR(0,1)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0209` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BR(0,1)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0222` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0269` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TR(0,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0299` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TR(0,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0366` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BR(0,1)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0029` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0137` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0179` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0221` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0293` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0335` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0365` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0425` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0539` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0605` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_16_interior_Y0617` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0137` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0210` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BR(0,1)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0221` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0329` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BR(0,1)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A141 polycore_lane_kills.jsonl` | `k5_11_interior_Y0444` | LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; teleport into the certified-dead extension class) [BR(0,1)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0011` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0023` | chord-limited lane [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0197` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0245` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0371` | chord-limited lane [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0383` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0431` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0533` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0587` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0641` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0653` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0065` | chord-limited lane [TL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A161 t3_dedup.jsonl` | `k5_16_interior_Y0305` | chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A167 pass_s0.jsonl` | `k5_16_interior_Y0635` | conditional chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | **no -- unattributed** |
| `A167 pass_s0.jsonl` | `k5_16_interior_Y0281` | conditional chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | **no -- unattributed** |
| `A167 pass_s1.jsonl` | `k5_16_interior_Y0635` | conditional chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | **no -- unattributed** |
| `A167 pass_s1.jsonl` | `k5_16_interior_Y0191` | conditional chord-limited lane [BL(1,0)] | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A199 seal199.jsonl` | `k5_16_interior_Y0491` | corner seal [BR: F meets BR(0,1), BR(1,0) unmet] (s0-only; WINDOW-PENDING) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `A200 quick200.jsonl` | `k5_16_interior_Y0191` | quick killer [propagation; g1 pad]: EmptyBox(H) at round1 | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0036_D03_D05` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0036_D07_D00` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0036_D07_D01` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0036_D07_D04` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0036_D07_D05` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0150` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0186_D00_D01` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0276` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0300` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0360` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1, k5_11_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_16_interior_Y0155` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_16_interior_Y0251` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_16_interior_Y0527` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_16_interior_Y0623` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_G1, k5_16_interior_L1` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0186_D00_D05` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0186_D01_D03` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0414_D07_D04` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0414_D07_D05` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0636_D04_D00` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0636_D04_D02` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0636_D06_D00` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0636_D06_D02` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0954_D00_D00` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0954_D00_D01` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0978_D04_D05` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0978_D06_D00` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0978_D06_D04` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0978_D06_D05` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0978_D07_D03` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y1140_D07_D04` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_G1_D2_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_11_interior_Y0041_D02` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_11_interior_G1_D2, k5_11_interior_L1_D2` |
| `clipkill certs (attempts/*/certs/**)` | `k5_16_interior_Y0449` | T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1) | AMBIGUOUS id over 2 trees, no tag and no prior tau | yes -- also killed at `k5_16_interior_L1` |

