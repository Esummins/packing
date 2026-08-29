"""Acyclic-orientation counter (A31 level1.py, verbatim)."""
_ao_cache = {}


def acyclic_orientations(n, edges):
    if n == 0:
        return 1
    key = (n, tuple(sorted(edges)))
    v = _ao_cache.get(key)
    if v is not None:
        return v
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    full = (1 << n) - 1
    memo = {0: 1}

    def a(S):
        if S in memo:
            return memo[S]
        tot = 0
        sub = S
        while True:
            if sub:
                ok = True
                t = sub
                while t:
                    b = t & -t
                    i = b.bit_length() - 1
                    t ^= b
                    if adj[i] & sub:
                        ok = False
                        break
                if ok:
                    sgn = -1 if (bin(sub).count('1') % 2 == 0) else 1
                    tot += sgn * a(S & ~sub)
            if sub == 0:
                break
            sub = (sub - 1) & S
        memo[S] = tot
        return tot

    v = a(full)
    _ao_cache[key] = v
    return v
