"""A107 T1 step 1: load every ALIVE-at-LP node's LP dual support (A57 both classes/shards/levels,
A60 trump5, A61 window stragglers), build its shadow = hypothesis cores + integral support, snap to
named slot cells, and group by combinatorial structure (slot set + free count) modulo the class
symmetry.  READ-ONLY on every campaign: reads only, writes under attempts/A107-shadow-gallery."""
import os, sys, json, math, glob, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadowlib as L

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OUT = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results')
S = L.S0

SOURCES = [
    ('A57', 'attempts/A57-shadow-trees/results/tree/*/*.json'),
    ('A60', 'attempts/A60-trump5-campaign/results/nodes/*.json'),
    ('A61', 'attempts/A61-window-stragglers/results/nodes/*.json'),
    ('A85', 'attempts/A85-k0-route/results/nodes/*.json'),
    ('A99', 'attempts/A99-k0-tree-v2/results/nodes/*.json'),
]

def level_of(nid):
    tail = nid.split('_interior_', 1)[-1]
    n = len([t for t in tail.split('_') if t and t[0] in 'YD' and t[1:].isdigit()])
    return max(n, 1)

def core_squares(d):
    out = []
    for c in (d.get('hyp') or {}).get('cores', []):
        b = c.get('box') or {}
        fl = c.get('float', {})
        cx = 0.5 * (b['x0'] + b['x1']) if 'x0' in b else float(fl.get('kx', 0))
        cy = 0.5 * (b['y0'] + b['y1']) if 'y0' in b else float(fl.get('ky', 0))
        th = math.radians(0.5 * (b.get('th0', 0.0) + b.get('th1', 0.0))) if 'th0' in b \
            else math.radians(float(fl.get('theta_deg', 0.0)))
        out.append((cx, cy, th))
    return out

def collect():
    nodes = []
    for tag, pat in SOURCES:
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            nid = os.path.basename(p)[:-5]
            shard = os.path.basename(os.path.dirname(p))
            try:
                d = L.load_node(p)
            except Exception:
                continue
            if 'packing' not in d or 'hyp' not in d:
                continue
            if d.get('dead', True):
                continue
            cs = core_squares(d)
            if not cs:
                continue
            ys = [float(q.get('y', 0.0)) for q in d.get('packing', [])]
            sup = [(float(q['cx']), float(q['cy']), float(q['theta']))
                   for q in d.get('packing', []) if float(q.get('y', 0.0)) > 0.5]
            frac = [(float(q['cx']), float(q['cy']), float(q['theta']), float(q['y']))
                    for q in d.get('packing', []) if float(q.get('y', 0.0)) > 0.02]
            integral = all(y < 1e-6 or y > 1 - 1e-6 for y in ys)
            nodes.append(dict(src=tag, path=os.path.relpath(p, ROOT).replace('\\', '/'), shard=shard,
                              nid=nid, level=level_of(nid), budget=d.get('budget'), tau=d.get('tau'),
                              converged=d.get('converged'), cores=cs, sup=sup, frac=frac,
                              integral=integral, npl=len(ys), nsig=len(frac),
                              skeleton=d.get('skeleton_name')))
    return nodes

def slot_key(cx, cy, th):
    return L.snap(cx, cy, th, S)

def structure(cfg):
    """(sorted tuple of slot names, list of free squares)."""
    slots, free = [], []
    for q in cfg:
        nm = slot_key(*q)
        if nm is not None:
            slots.append(nm)
        else:
            free.append(q)
    return tuple(sorted(set(slots))), free

def apply_op(f, cfg):
    return [tuple(f(x, y, t)) for x, y, t in cfg]

def canon_structure(cfg, ops):
    """Canonical (slot-set, nfree) over the class stabiliser -- but for grouping we use the FULL D4
    orbit restricted to ops that preserve the class skeleton, so equivalent nodes collapse."""
    best = None
    for nm, f in ops:
        sl, fr = structure(apply_op(f, cfg))
        key = (sl, len(fr))
        if best is None or key < best[0]:
            best = (key, nm)
    return best

# LP rows are grid CELLS (pitch ~0.192 in x,y and 5 deg in tilt): two placements in distinct cells
# can be realised disjointly iff their representatives' SAT gap exceeds -pitch.  Verified integral LP
# solutions in this corpus have min pairwise gap -0.2045, so PITCH_TOL = -0.21 is the honest test.
PITCH_TOL = -0.21

def disjoint(a, b, tol=PITCH_TOL):
    return L.sat_gap(a[:2], a[2], b[:2], b[2]) >= tol

def integral_component(cores, frac, budget, tlim=1.0):
    """Split a fractional dual support into an integral component: a set of `budget` placements that
    are pairwise disjoint and disjoint from the hypothesis cores (a candidate near-packing).
    Weight-greedy DFS with a per-node time cap; returns the first full-size set found, else the
    largest found."""
    cand = [q[:3] for q in sorted(frac, key=lambda q: -q[3])]
    cand = [q for q in cand if all(disjoint(q, c) for c in cores)]
    n = len(cand)
    if n == 0:
        return []
    adj = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            adj[i][j] = adj[j][i] = disjoint(cand[i], cand[j])
    best = []
    t0 = time.time()
    def dfs(cur, allowed):
        nonlocal best
        if len(cur) > len(best):
            best = list(cur)
        if len(best) >= budget or time.time() - t0 > tlim:
            return
        if len(cur) + len(allowed) <= len(best):
            return
        for k, i in enumerate(allowed):
            if len(cur) + len(allowed) - k <= len(best):
                return
            cur.append(i)
            dfs(cur, [j for j in allowed[k + 1:] if adj[i][j]])
            cur.pop()
            if len(best) >= budget or time.time() - t0 > tlim:
                return
    dfs([], list(range(n)))
    return [cand[i] for i in best]

def main():
    t0 = time.time()
    nodes = collect()
    print('alive-at-LP nodes with LP support:', len(nodes))
    print('by source:', dict(collections.Counter(n['src'] for n in nodes)))

    # class = the axis-aligned slot squares among the cores of the SHALLOWEST node of each family
    for n in nodes:
        sl, fr = structure(n['cores'])
        n['skel_slots'] = sl
        n['cond'] = fr                       # tilted / non-slot cores = conditioned squares
    skels = collections.Counter((n['src'], n['skel_slots']) for n in nodes)
    print('skeletons:')
    for k, v in skels.most_common(30):
        print('  ', v, k[0], k[1])

    # stabiliser per skeleton slot-set
    cells = L.slot_cells(S)
    stab = {}
    for (src, sl), _ in skels.items():
        pins = [cells[nm] for nm in sl]
        stab[(src, sl)] = L.stabiliser(pins, S)

    groups = collections.defaultdict(list)
    unexp = []
    nfrac_full = 0
    for k, n in enumerate(nodes):
        if n['integral'] and n['sup']:
            cfg = list(n['cores']) + list(n['sup'])
            n['via'] = 'integral'
        else:
            comp = integral_component(n['cores'], n['frac'], n['budget'] or 5)
            if len(comp) < (n['budget'] or 5):
                n['via'] = 'none'; n['comp'] = len(comp)
                unexp.append(k); continue
            cfg = list(n['cores']) + list(comp)
            n['via'] = 'component'
            nfrac_full += 1
        n['cfg'] = cfg
        n['minsat'] = min([L.sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2])
                           for i in range(len(cfg)) for j in range(i + 1, len(cfg))] or [0.0])
        ops = stab[(n['src'], n['skel_slots'])]
        (key, opname) = canon_structure(cfg, ops)
        n['struct'] = key
        n['struct_op'] = opname
        groups[(n['src'], n['skel_slots'], key)].append(k)
    print('fractional nodes with a full integral component:', nfrac_full)

    print('\nstructures (integral shadows), by node count:')
    for g, mem in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        src, sl, (slots, nfree) = g
        print(f'  {len(mem):4d}  {src}  skel={"+".join(sl)}  slots={"+".join(slots)}  free={nfree}')
    print('distinct structures:', len(groups), ' nodes covered:', sum(len(v) for v in groups.values()))
    print('nodes with no integral support:', len(unexp))
    print('elapsed', round(time.time() - t0, 1), 's')

    os.makedirs(OUT, exist_ok=True)
    ser = []
    for n in nodes:
        m = {k: v for k, v in n.items() if k not in ('frac',)}
        m['skel_slots'] = list(n['skel_slots'])
        if 'struct' in n:
            m['struct'] = [list(n['struct'][0]), n['struct'][1]]
        ser.append(m)
    json.dump(dict(nodes=ser,
                   groups={json.dumps([g[0], list(g[1]), [list(g[2][0]), g[2][1]]]): v for g, v in groups.items()},
                   unexplained=unexp),
              open(os.path.join(OUT, 'extract.json'), 'w'), indent=1)
    print('wrote results/extract.json')

if __name__ == '__main__':
    main()
