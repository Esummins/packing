import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code")
def patch(fn, reps):
    p = os.path.join(D, fn); s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) == 1, (fn, a[:60]); s = s.replace(a, b, 1)
    open(p, "w", encoding="utf-8").write(s)
patch("run203.py", [("import fig203                                                  # noqa: E402", "import fig203b as fig203                                       # noqa: E402")])
patch("csp203b.py", [
("""    dead_keys = {k for k, _, _ in dead_opts}
    killed_pieces = 0
    for (ci, S) in dead_keys:
        if len(S) == 1:
            (p,) = tuple(S)
            before = len(st.alive[p])
            st.alive[p] = [pc for pc in st.alive[p] if pc[0] != ci]
            killed_pieces += before - len(st.alive[p])
            for pc in by_cell_slot.get((ci, p), ()):
                st.letters_csp[(ci, pc[1][1])] = "H\"""",
"""    dead_keys = {k: r for k, r, _ in dead_opts}
    killed_pieces = 0
    for (ci, S), r in dead_keys.items():
        if len(S) == 1:
            (p,) = tuple(S)
            before = len(st.alive[p])
            st.alive[p] = [pc for pc in st.alive[p] if pc[0] != ci]
            killed_pieces += before - len(st.alive[p])
            for pc in by_cell_slot.get((ci, p), ()):
                st.letters_csp[(ci, pc[1][1])] = r"""),
("""def piece_addr(st, pc):
    \"\"\"dyadic address (ci, si, cb, depth, ix, iy, ib) of a free piece from its geometry (midpoints: robust).\"\"\"
    ci, rf, bn = pc[0], pc[1], pc[3]""",
"""def piece_addr(st, pc):
    \"\"\"dyadic address (ci, si, cb, depth, ix, iy, ib) of a free piece from its geometry (midpoints: robust); cached per piece.\"\"\"
    a = st.addr_cache.get(id(pc))
    if a is None:
        a = st.addr_cache[id(pc)] = _piece_addr(st, pc)
    return a


def _piece_addr(st, pc):
    ci, rf, bn = pc[0], pc[1], pc[3]"""),
])
patch("fast30.py", [("        self.settled = {}", "        self.addr_cache = {}\n        self.settled = {}")])
patch("csp203c.py", [("max_pairs=400, depth=3, fanout=64, t_opt=2.0, t_all=8.0", "max_pairs=400, depth=3, fanout=64, t_opt=2.0, t_all=6.0")])
print("ok")
