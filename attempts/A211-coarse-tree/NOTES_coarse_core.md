# A211e -- COARSE CORES at internal nodes (PI, 2026-09-14 11:00: "cut early, memoize, or go coarser, aka do less work").
Opus. LAUNCH-AND-EXIT.
A211d's profile: 67% of a run is MBox.rebuild in kmode "pieces" (the exact intersection of per-piece cores, 810
rebuilds x ~1.2 s, exact rational arithmetic).  The library also has kmode "union" (A171/A132: one certified polygon on
the union hull of the pieces -- sound, forgets the far-side growth), which the coarse tree never uses (KMODE = "pieces"
in coarse211.py).  At a coarse internal node that precision is wasted; per-piece cores belong only to the exact leaf
cascade.
1. KMODE "union" at coarse internal nodes (set_coarse(True)), "pieces" at the exact leaf cascade (set_coarse(False));
   a smaller certification grid at coarse nodes (n_grid 97 -> 33 or whatever the union build accepts; the core only
   gets SMALLER = still sound) -- state the soundness in notes/coarse_tree.md (union-mode K' is a subset of the true
   core: the library's own guarantee; a coarse node's kills stay valid, its ALIVE means "branch further").
2. The coarse cascade: one pass only at internal nodes (confirm); the exact leaf cascade stops after a pass that
   removed < 0.1% (confirm the existing stop) and never starts once the wall is spent (done).
3. Re-profile on k5_11_interior_Y0202 pad 0 (isolated dirs as A211d did; before = A211d's after-run): per-stage table,
   nodes reached, kills within the 900 s wall, per-node seconds; the certificates MAY differ now (coarser cores at
   internal nodes) -- report what changed (kills lost / gained inside the wall) honestly.  Also time one frontier node.
4. Commit with explicit pathspecs; the workers pick it up per node -- do not restart them; never touch A212 / the k0
   cascade.  Report once and EXIT.
