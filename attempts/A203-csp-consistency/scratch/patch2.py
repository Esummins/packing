import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code")


def patch(fn, reps):
    p = os.path.join(D, fn)
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) == 1, (fn, a[:60])
        s = s.replace(a, b, 1)
    open(p, "w", encoding="utf-8").write(s)


patch("csp203.py", [
("""    __slots__ = ("rect", "bins", "kids", "uid", "tag", "leaves", "lr", "lb")

    def __init__(self, rect, bins, kids=(), tag=None, leaves=None):
        self.rect, self.bins, self.kids, self.tag = rect, list(bins), list(kids), tag
        self.uid = next(_UID)
        self.leaves = leaves
        if leaves is not None:
            self.lr = np.array([p[2] for p in leaves], dtype=float)
            self.lb = np.array([p[4] for p in leaves], dtype=float)
        else:
            self.lr = self.lb = None""",
"""    __slots__ = ("rect", "bins", "kids", "uid", "tag", "leaves", "lr", "lb", "lkey")

    def __init__(self, rect, bins, kids=(), tag=None, leaves=None):
        self.rect, self.bins, self.kids, self.tag = rect, list(bins), list(kids), tag
        self.uid = next(_UID)
        self.leaves = leaves
        if leaves is not None:
            self.lr = np.array([p[2] for p in leaves], dtype=float)
            self.lb = np.array([p[4] for p in leaves], dtype=float)
            self.lkey = tuple(id(p) for p in leaves)                     # the block cache survives the round (same pieces)
        else:
            self.lr = self.lb = self.lkey = None"""),
("""    def __init__(self, step=4.0):
        self.cache = {}
        self.pairs = {}
        self.step = step
        self.n_sat = 0
        self.n_dead = 0
        self.n_leaf = 0
        self.ms = 0.0""",
"""    def __init__(self, step=4.0):
        self.cache = {}
        self.pairs = {}
        self.blocks = {}                                               # (lkey, lkey) -> alive leaf index pairs (persistent)
        self.step = step
        self.n_sat = 0
        self.n_dead = 0
        self.n_leaf = 0
        self.n_hit = 0
        self.ms = 0.0

    def reset(self):
        \"\"\"a new round: the node caches go (new nodes), the leaf-block cache stays.\"\"\"
        self.cache, self.pairs = {}, {}"""),
("""    def block(self, A, B):
        k = (A.uid, B.uid) if A.uid <= B.uid else (B.uid, A.uid)
        v = self.cache.get(k)
        if v is not None:
            return v
        d = SB.block(A.lr, A.lb, B.lr, B.lb, self.step)
        self.n_leaf += d.size
        alive = np.argwhere(~d)
        v = len(alive) > 0
        if v:
            self.pairs[k] = [(int(i), int(j)) if A.uid <= B.uid else (int(j), int(i)) for i, j in alive]
        self.cache[k] = v
        return v""",
"""    def block(self, A, B):
        k = (A.uid, B.uid) if A.uid <= B.uid else (B.uid, A.uid)
        v = self.cache.get(k)
        if v is not None:
            return v
        bk = (A.lkey, B.lkey)
        prs = self.blocks.get(bk)
        if prs is None:
            d = SB.block(A.lr, A.lb, B.lr, B.lb, self.step)
            self.n_leaf += d.size
            prs = self.blocks[bk] = [(int(i), int(j)) for i, j in np.argwhere(~d)]
            self.blocks[(B.lkey, A.lkey)] = [(j, i) for i, j in prs]
        else:
            self.n_hit += 1
        v = len(prs) > 0
        if v:
            self.pairs[k] = prs if A.uid <= B.uid else [(j, i) for i, j in prs]
        self.cache[k] = v
        return v"""),
])

patch("csp203c.py", [
("""    import fast30
    cur = [pc]
    for d in range(depth):
        nxt = []
        for q in cur:
            for ch in fast30.split(q):
                if st.kill_base(ch, cnt, tm) is not None:
                    continue
                if any(st.kill_slot(ch, p, cnt, tm, exact=True) is not None for p in S):
                    continue
                if C.sat_dead(ch[2], ch[4], hp[2], hp[4], st.sat_step):
                    cnt["S"] += 1
                    continue
                nxt.append(ch)
        cur = nxt
        if not cur:
            return True
        if len(cur) > fanout:
            return False
    return False""",
"""    import fast30
    key = (id(pc), id(hp), S)
    v = st.settled.get(key)
    if v is not None:
        return v
    cur = [pc]
    out = False
    for d in range(depth):
        nxt = []
        for q in cur:
            for ch in fast30.split(q):
                if st.kill_base(ch, cnt, tm) is not None:
                    continue
                if any(st.kill_slot(ch, p, cnt, tm, exact=False) is not None for p in S):
                    continue                                           # R (cheap) for every slot first
                if C.sat_dead(ch[2], ch[4], hp[2], hp[4], st.sat_step):
                    cnt["S"] += 1
                    continue
                if any(st.kill_slot(ch, p, cnt, tm, exact=True) is not None for p in S):
                    continue                                           # then A161's exact miss X
                nxt.append(ch)
        cur = nxt
        if not cur:
            out = True
            break
        if len(cur) > fanout:
            break
    st.settled[key] = out
    return out"""),
])

patch("csp203b.py", [
("    compat = st.compat = C.Compat(step)\n", "    if st.compat is None:\n        st.compat = C.Compat(step)\n    compat = st.compat\n    compat.reset()\n"),
("sat_tests=compat.n_sat, sat_dead=compat.n_dead, leaf_pairs=compat.n_leaf,", "sat_tests=compat.n_sat, sat_dead=compat.n_dead, leaf_pairs=compat.n_leaf, block_hits=compat.n_hit,"),
])
patch("fast30.py", [
("        self.compat = None\n", "        self.compat = None\n        self.settled = {}                                                      # (id piece, id H piece, S) -> settled dead?\n"),
])
print("ok")
