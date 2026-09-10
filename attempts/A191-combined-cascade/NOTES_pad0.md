# Coordinator note for A191's successor (2026-09-10 02:45) — the K0-WIDEN pad is what keeps l1_104 alive

A194 (docs/proofs/descent_examples.md, l1_104): the tau = 10 windows-LP support of root/D0/S1 is a k3-SKELETON —
exact slot squares at BR / TL / TR (weight 1) plus grazers of depth <= 0.026 at TL, three lonely — i.e. three k1
pockets that exist ONLY because of the K0-WIDEN pad w = 0.025509 (the dilation transfer of the s0 certificate over
the window). At pad 0 the slot square is lonely (Theorem B, Cor. B1) and the support loses weight >= 3.

Therefore: (1) certify the k0 nodes AT s0 with pad 0 (unit corner boxes, lonely clip at c = 1, corner windows of
the unit box) — the support dies there; (2) cover the window [3.82, s0] by SLABS in s, each transported with its
own pad (lambda_slab - 1)(1 + sqrt2/2), small enough that no k1 pocket survives — "the exact row is slab-wise";
the slab count is the price. Emit per slab; the composition is the same as the window rows' (Lemma B'/M->E).
Also: CC-5's column row = Lemma CH-L (a band meeter carries a unit chord on every wall-parallel line within
gamma = 0.2071 of its centre line) — emit it as a fixed v5 guard line per centre slab of height <= 2 gamma.
