"""A201 experiment: price the exact pair test (rule (c)) in two forms on the pairs the count actually reaches on a page
(after (a) A1 and (b) CN): V1 = the CELL-level seeded clip (the union of the two cells' anonymous survivors; the full multibox node was V1 in the first run);
V2 = the SEEDED two-box mutual clip (pairclip201.pair_clip: the two rows' own surviving pieces, per-tilt-quarter K',
A171's exact clip, iterated).  Prints seconds and verdict per pair per variant, and the PI's column pairs (cells 21/22/23).
    python exp201.py <nid> [pad] [n_sample]
"""
import os
import random
import sys
import time

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import quick201 as Q1                                          # noqa: E402
import pairtab201 as PT                                        # noqa: E402
import pairclip201 as PCL                                      # noqa: E402
import fastprop as FP                                          # noqa: E402  READ-ONLY (A198)
import count201                                                # noqa: E402

nid = sys.argv[1] if len(sys.argv) > 1 else "k5_16_interior_Y0044"
pad = sys.argv[2] if len(sys.argv) > 2 else "g1"
nsample = int(sys.argv[3]) if len(sys.argv) > 3 else 24
T = FP.Trace(wall=3000)
rec, cls, row = FP.load_page(nid)
pg = Q1.QPage201(rec, cls, nid, T, pad=pad, pair_exact=False)
t0 = time.time()
pg.normalise("base")
free_opts, fixed_opts, single = pg.build_options()
print("page built in %.0f s: %d free options, fixed %s" % (time.time() - t0, len(free_opts), {r: len(v) for r, v in fixed_opts.items()}), flush=True)
table = PT.PairTable(pg, budget=0, exact=False)
table.register(free_opts, fixed_opts)
caps = {p: Q1.INF for p in pg.slots}
r = count201.count_search(pg.slots, free_opts, fixed_opts, pg.n_free - len(pg.role_cell), pg.lines, pg.pin_chords, pg.s, caps, table, use_chords=False)
print("count (A1+CN only): feasible %s, nodes %d; table %s" % (r.feasible, r.nodes, table.summary()), flush=True)
survivors = [tuple(pk) for pk, (ok, _) in table.cache.items() if ok]
rng = random.Random(201)
sample = rng.sample(survivors, min(nsample, len(survivors)))
# the PI's column: anonymous options in cells 21 / 22 / 23 (k5_16 grid) for the right-wall slots
col = [k for k in table.hull if k[0] == "free" and k[1] in (21, 22, 23)]
colpairs = [(a, b) for i, a in enumerate(col) for b in col[i + 1:] if a[1] != b[1] and table.compatible(a, b)]
print("column options %d; column pairs surviving (a)(b): %d" % (len(col), len(colpairs)), flush=True)
todo = [("sample", pk) for pk in sample] + [("column", pk) for pk in colpairs[:16]]
tab_full = PT.PairTable(pg, budget=10 ** 9, exact=True)
tab_full.register(free_opts, fixed_opts)
tot = {"V1": [0.0, 0], "V2": [0.0, 0], "V2r": [0.0, 0]}
for tag, (k1, k2) in todo:
    p1, p2 = table.pieces(k1), table.pieces(k2)
    t1 = time.time()
    r2 = PCL.pair_clip(p1, p2, pg.s, max_iter=4, refine=0)
    d2 = time.time() - t1
    t1 = time.time()
    r2r = PCL.pair_clip(p1, p2, pg.s, max_iter=4, refine=1)
    d2r = time.time() - t1
    t1 = time.time()                                           # V1 (full multibox node) was measured first: see logs/exp201_y0044.log
    ok1 = True                                                 # (0 exclusions in 118 s over 40 pairs); now V1 = the CELL-level clip
    if k1[0] == "free" and k2[0] == "free":
        rc = PCL.pair_clip(tab_full.cell_union(k1[1]), tab_full.cell_union(k2[1]), pg.s, max_iter=3, refine=0)
        ok1 = not rc["excluded"]
    d1 = time.time() - t1
    for nm, d, ex in (("V1", d1, not ok1), ("V2", d2, r2["excluded"]), ("V2r", d2r, r2r["excluded"])):
        tot[nm][0] += d
        tot[nm][1] += int(ex)
    print("%-7s %s | %s  (%d, %d pieces): V1 %s %.2fs | V2 %s %.2fs (%s) | V2r %s %.2fs (%s)" % (
        tag, PT.key_json(k1), PT.key_json(k2), len(p1), len(p2), "EXCL" if not ok1 else "comp", d1,
        "EXCL" if r2["excluded"] else "comp", d2, r2.get("why", "")[:50], "EXCL" if r2r["excluded"] else "comp", d2r, r2r.get("why", "")[:50]), flush=True)
print("TOTALS (seconds, exclusions) over %d pairs: %s" % (len(todo), tot), flush=True)
