"""the PI's Y0191 TL(1,0) pair (cells 14 | 18) on PIECES: rule S hierarchically over the two rows' meeting pieces."""
import sys, itertools
sys.path.insert(0, 'attempts/A203-csp-consistency/code')
import fast30, fast30b as B, csp203b as CB, csp203 as C, rules202 as R, fastprop as FP
st = fast30.Stage0('k5_16_interior_Y0191', 'g1')
out = st.run()
fo, _ = B.free_options(st)
by = {}
for p in st.slots:
    for pc in st.alive[p]:
        by.setdefault((pc[0], p), []).append((CB.piece_addr(st, pc), pc))
rows = {(o[0], o[1]): o for o in fo if 'TL(1,0)' in o[1] and o[0] in (14, 18, 8, 13, 19)}
trees = {k: CB.opt_node(st, CB.opt_pieces(st, k[0], k[1], by), k) for k in rows}
cp = C.Compat(4.0)
for (k1, n1), (k2, n2) in itertools.combinations(sorted(trees.items(), key=lambda kv: (kv[0][0], sorted(kv[0][1]))), 2):
    if k1[0] == k2[0]:
        continue
    a1 = FP.a1_compatible(rows[k1][3], rows[k2][3])
    ok = cp.ok(n1, n2)
    print('%2d %-28s | %2d %-28s  A1 %s  rule S on pieces: %s  hull maxdist %.4f  pieces %d x %d' % (
        k1[0], '+'.join(sorted(k1[1])), k2[0], '+'.join(sorted(k2[1])), 'ok' if a1 else 'EXCL', 'compatible' if ok else 'EXCLUDED',
        C.maxdist(n1, n2), len(n1.leaves) if n1.leaves is not None else sum(len(k.leaves) for k in n1.kids), len(n2.leaves) if n2.leaves is not None else sum(len(k.leaves) for k in n2.kids)))
