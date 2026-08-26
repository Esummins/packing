#!/usr/bin/env python3
"""
A29 drive.py -- finish A27's interior-first case tree at s = 96/25 = 3.84.

Applies A27 section 6's own two speedups:

  (1) REFINE IMMEDIATELY.  A node that does not certify is split 8-way at once; no CPU is spent
      grinding its level-1 LP towards a converged tau that the sound status rule shows can never
      drop below the budget anyway.
  (2) WARM-START EVERY CHILD FROM THE PARENT'S CONVERGED DUAL.  A child is never solved from
      scratch: `synth_node` writes a node json carrying the CHILD's hypothesis (its own, smaller
      box and hence LARGER core) together with the PARENT's atoms and rows, and hands that to
      certify.py, whose EPS_GEO = 3e-3 re-solve then starts from the parent's measure.  This also
      removes the separate EPS_GEO = 1e-4 node solve that A27 ran before every certification:
      certification re-solves at the robustness margin in any case, so the 1e-4 pass was pure
      overhead at the refinement levels.

      SOUNDNESS: a warm start can never make a certificate wrong.  The rows a parent contributes
      that meet the child's larger core are REJECTED by `lpbox.Model.add_row` (which knows the
      node hypothesis), and in the end the arbiter of every death is the exact verifier
      `verify_case.py` run on the finished rational certificate, exactly as in A24/A27.

  (3) SYMMETRY IS USED BEFORE THE CPU IS SPENT, not only afterwards.  sigma(x,y,th) = (y,x,90-th)
      maps the cover's diagonal cells (i,i,k) to (i,i,5-k); when both members of such a pair are
      open only ONE is worked, and `verify_tree2.py` discharges the other exactly.  A node whose
      mirror already carries a certificate is skipped outright.

Resumable: every node's verdict is a file on disk (certs/casetree_3.84/leaf_<path>.json) and the
work queue is checkpointed to results/a29/state.json after every completed node, so the run can be
killed or the machine powered off at any point and restarted with the same command line.

  python drive.py seed                       # level-1 queue from the closure verdict
  python drive.py run --workers 9            # certify-or-refine until closed or --max_depth
  python drive.py status
"""
from __future__ import annotations

import argparse, glob, json, os, re, subprocess, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import multiprocessing as mp
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from caselp import Box, Hyp                                    # noqa: E402
from refine import split8, box_of_path                         # noqa: E402
from certify_a27 import _one as certify_one                    # noqa: E402
import verify_tree2 as V                                       # noqa: E402

CERTS = os.path.join(HERE, 'certs', 'casetree_3.84')
WORK = os.path.join(HERE, 'results', 'a29')
NODES = os.path.join(WORK, 'nodes')
STATE = os.path.join(WORK, 'state.json')
S = 3.84
NTH = 6


# ------------------------------------------------------------------ node bookkeeping
def cert_of(name):
    return os.path.join(CERTS, f'leaf_{name}.json')


def passed(name):
    """certify.py writes leaf_<name>.certify.json with result PASS only after the EXACT verifier
    has accepted the certificate; leaf_<name>.json alone can be an in-flight, not-yet-verified
    file (certify.py dumps it before calling the verifier)."""
    p = os.path.join(CERTS, f'leaf_{name}.certify.json')
    if not os.path.exists(p):
        return False
    try:
        return json.load(open(p)).get('result') == 'PASS'
    except Exception:
        return False


def certified(name):
    return os.path.exists(cert_of(name)) and passed(name)


def sweep_provisional():
    """drop any leaf_*.json left behind by a certification the machine interrupted: it has not been
    accepted by the exact verifier, so it must not be counted (verify_tree2.py would reject it, but
    the driver must not skip refining the node on the strength of it)."""
    n = 0
    for p in glob.glob(os.path.join(CERTS, 'leaf_*.json')):
        if os.path.basename(p).count('.') != 1:
            continue
        name = os.path.basename(p)[len('leaf_'):-len('.json')]
        if not passed(name):
            os.replace(p, p + '.provisional')
            n += 1
    if n:
        print(f'swept {n} unverified provisional certificate(s)', flush=True)
    return n


def have_certs():
    return {os.path.basename(p)[len('leaf_'):-len('.json')]
            for p in glob.glob(os.path.join(CERTS, 'leaf_*.json'))
            if os.path.basename(p).count('.') == 1}


def children_of(name):
    return [f'{name}_{suf}' for suf, _ in split8(box_of_path(name))]


def mirror_path(path):
    """sigma-image path, or None.  Level-1 cell (i,j,k) -> (j,i,5-k) exists in the cover only for
    the diagonal cells i == j; each 8-way suffix (a,b,c) -> (b,a,1-c)."""
    parts = path.split('_')
    mid = V.sigma_cell(int(parts[0]))
    if mid is None:
        return None
    out = [str(mid)]
    for p in parts[1:]:
        a, b, c = p
        out.append(f'{b}{a}{1 - int(c)}')
    return '_'.join(out)


def sigma_free(path, nt=24, nxs=4):
    """True iff `path` is discharged for free by its mirror's certificate (checked exactly, in the
    same way verify_tree2.py will re-check it: the mirror's core must lie in EVERY unit square whose
    parameters lie in the sigma-image of this node's box)."""
    mp_ = mirror_path(path)
    if mp_ is None or not certified(mp_):
        return False
    X0, X1, Y0, Y1, T0, T1 = V.qbox(box_of_path(path))
    cj = json.load(open(cert_of(mp_)))['hypotheses']['cores'][0]
    Ks = (F(cj['kx']), F(cj['ky']), F(cj['tm']), F(cj['a']))
    ok, _ = V.core_in_every_square(Ks, Y0, Y1, X0, X1, V.sigma_t(T1), V.sigma_t(T0), nt, nxs)
    return bool(ok)


def best_result(name):
    """the richest LP result on disk for node `name`: the last witness-feedback re-solve of its own
    certification attempt if there was one, else its EPS_GEO = 3e-3 re-solve, else its node LP."""
    cands = []
    for p in glob.glob(os.path.join(CERTS, f'leaf_{name}.resolve*.json')):
        m = re.search(r'resolve(\d*)\.json$', p)
        if m:
            cands.append((int(m.group(1) or '0'), p))
    if cands:
        return max(cands)[1]
    if '_' not in name:
        p = os.path.join(HERE, 'results', 'l1', f'n{name}.json')
        if os.path.exists(p):
            return p
    for d in (NODES,) + tuple(os.path.join(HERE, 'results', t)
                              for t in ('l2probe', 'l2probe95', 'l3probe', 'l3b', 'l2', 'l3')):
        p = os.path.join(d, f'n_{name}.json')
        if os.path.exists(p):
            return p
    return None


def synth_node(name):
    """node json for `name` = the child's own hypothesis + the parent's atoms/rows (speedup 2)."""
    if '_' not in name:
        p = os.path.join(HERE, 'results', 'l1', f'n{name}.json')
        if os.path.exists(p):
            return p
        raise SystemExit(f'no level-1 node result for {name}')
    out = os.path.join(NODES, f'n_{name}.json')
    if os.path.exists(out):
        return out
    parent = name.rsplit('_', 1)[0]
    src = best_result(parent)
    if src is None:
        raise SystemExit(f'no warm-start result for the parent {parent} of {name}')
    res = json.load(open(src))
    atoms, rows, used = {}, {}, []
    for (x, y, w) in res.get('atoms_all', []):
        atoms[(x, y)] = w
    for r in res.get('rows_all', []):
        rows[tuple(r)] = 1
    used.append(os.path.relpath(src, HERE))
    # the parent's FULL column set (all orbits, including the zero-weight ones) lives in its
    # solver checkpoints; pull every one we can find, they are the expensive part to rediscover.
    for st in [src.replace('.json', '_state.json'), src.replace('.json', '.resolve_state.json')] + \
              sorted(glob.glob(os.path.join(CERTS, f'leaf_{parent}.resolve_state.json'))):
        if os.path.exists(st):
            try:
                d0 = json.load(open(st))
            except Exception:
                continue
            for o in d0.get('orbits', []):
                atoms.setdefault((o[0], o[1]), 0.0)
            for r in d0.get('rows', []):
                rows[tuple(r)] = 1
            used.append(os.path.relpath(st, HERE))
    B = box_of_path(name)
    d = dict(s=S, budget=10, hyp=Hyp([B], ()).to_json(),
             atoms_all=[[x, y, w] for (x, y), w in atoms.items()],
             rows_all=[list(r) for r in rows],
             tau=res.get('tau'), converged=False, minmass=res.get('minmass'),
             maxcov=res.get('maxcov'),
             warm_from=used, synthesized='A29 drive.py speedup (2)')
    os.makedirs(NODES, exist_ok=True)
    tmp = out + '.tmp'
    json.dump(d, open(tmp, 'w'))
    os.replace(tmp, out)
    return out


def stage1_running():
    """True while a separate certify_a27.py wave still owns part of the 9-worker budget."""
    try:
        q = subprocess.run(['wmic', 'process', 'where', "name='python.exe'", 'get', 'commandline'],
                           capture_output=True, text=True, timeout=120)
        return any('certify_a27.py' in l for l in q.stdout.splitlines())
    except Exception:
        return False


# ------------------------------------------------------------------ state
def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return dict(queue=[], depth=1, done={}, history=[])


def save_state(st):
    os.makedirs(WORK, exist_ok=True)
    tmp = STATE + '.tmp'
    json.dump(st, open(tmp, 'w'), indent=1)
    os.replace(tmp, STATE)


# ------------------------------------------------------------------ seed
def closure_missing():
    """the open level-1 cells, from the structural closure verdict (leaf re-verification skipped:
    that is the FINAL arbiter, run once at the end, not a scheduling input)."""
    out = os.path.join(WORK, 'closure.json')
    os.makedirs(WORK, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'verify_tree2.py'),
                    '--skip_leaf_verify', '--out', out],
                   cwd=HERE, capture_output=True, text=True)
    return json.load(open(out))['checks']['closure']['missing']


def cmd_seed(a):
    sweep_provisional()
    miss = closure_missing()
    # symmetry: for a diagonal mirror pair both of whose members are open, work only one of them
    keep, drop = [], []
    seen = set()
    for i in miss:
        if i in seen:
            continue
        m = V.sigma_cell(i)
        if m is not None and m in miss and m != i:
            seen.add(m)
            drop.append(m)
        keep.append(i)
        seen.add(i)
    # nodes a concurrently-running certify_a27.py wave owns: leave them alone this round, the
    # outer loop in finish.py re-seeds and picks up whatever that wave could not certify.
    # Ownership is decided by STATE, not by the process table: a node listed in phaseA_todo.txt
    # that has neither a certificate nor a failure marker has not been dispatched yet and still
    # belongs to the level-1 wave.  As soon as that wave finishes a node it leaves one or the
    # other behind, and the reservation lapses by itself -- no race with process startup, and
    # nothing can be worked by two drivers at once (they share output paths).
    reserved = set()
    p = os.path.join(HERE, 'results', 'phaseA_todo.txt')
    if os.path.exists(p):
        for x in open(p).read().split(','):
            x = x.strip()
            if x and not certified(x) and not os.path.exists(
                    os.path.join(CERTS, f'leaf_{x}.attempt.json')):
                reserved.add(x)
        keep = [i for i in keep if str(i) not in reserved]
    st = load_state()
    st['queue'] = [str(i) for i in keep]
    st['reserved_for_stage1'] = sorted(reserved)
    st['depth'] = 1
    st['sigma_deferred'] = sorted(drop)
    st['seeded_missing'] = miss
    done = st.setdefault('done', {})
    # (a) cells whose level-1 certification has ALREADY been attempted and failed: do not pay for
    #     the same attempt twice, refine them.
    nfail = 0
    for mp_ in glob.glob(os.path.join(CERTS, 'leaf_*.attempt.json')):
        nm = os.path.basename(mp_)[len('leaf_'):-len('.attempt.json')]
        if '_' in nm or certified(nm):
            continue
        try:
            mk = json.load(open(mp_))
        except Exception:
            continue
        done.setdefault(nm, dict(certified=False, depth=1, tail=(mk.get('tail') or '')[:200],
                                 params=mk.get('params'),
                                 why='level-1 certification already failed'))
        nfail += 1
    p = os.path.join(HERE, 'results', 'certs_l1.json')
    if os.path.exists(p):
        for r in json.load(open(p)).get('results', []):
            if not r.get('certified') and not certified(r['name']):
                done.setdefault(r['name'], dict(certified=False, depth=1,
                                                tail=r.get('tail', '')[:200],
                                                why='level-1 certification already failed'))
                nfail += 1
    # (b) A27 section 6 speedup (1): a cell that is alive(LP) -- tau >= budget with the column
    #     oracle exhausted (maxcov <= 1+1e-3), so the coverage LP optimum over the WHOLE atom space
    #     is >= the budget -- can never be certified at this box size.  Refine it at once instead
    #     of spending a certification attempt on it.
    nalive = 0
    for i in keep:
        rp = os.path.join(HERE, 'results', 'l1', f'rec{i}.json')
        if not os.path.exists(rp) or certified(str(i)):
            continue
        r = json.load(open(rp))
        if (r.get('tau') is not None and r['tau'] >= 10 - 1e-9
                and (r.get('maxcov') or 9) <= 1 + 1e-3):
            done.setdefault(str(i), dict(certified=False, depth=1, tau=r['tau'],
                                         maxcov=r.get('maxcov'),
                                         why='alive(LP): refined immediately'))
            nalive += 1
    save_state(st)
    print(f'seed: {len(miss)} open level-1 cells -> queue {len(keep)} '
          f'({len(drop)} deferred to the diagonal symmetry: {drop}); '
          f'{nfail} already-failed + {nalive} alive(LP) go straight to refinement')


# ------------------------------------------------------------------ run
def cmd_run(a):
    st = load_state()
    os.makedirs(NODES, exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs', 'cert'), exist_ok=True)
    sweep_provisional()
    stages = (1.03, 0)
    cur_params = dict(eps_geo=float(a.eps_geo), rounds=int(a.rounds),
                      time_limit=float(a.time_limit), resolve_time=float(a.resolve_time),
                      depth=int(a.depth), max_cols=int(a.max_cols),
                      stages=[float(s) for s in stages])
    while st['queue'] and st['depth'] <= a.max_depth:
        depth = st['depth']
        queue = list(st['queue'])
        todo = []
        skipped = dict(certified=[], sigma=[], tried=[])
        for n in queue:
            if certified(n):
                skipped['certified'].append(n)
                continue
            if sigma_free(n):
                skipped['sigma'].append(n)
                continue
            prev = st['done'].get(n)
            if prev is not None and not prev.get('certified'):
                skipped['tried'].append(n)      # already attempted (or alive(LP)): refine at once
                continue
            todo.append(n)
        print(f'== depth {depth}: {len(queue)} nodes, {len(skipped["certified"])} already certified, '
              f'{len(skipped["sigma"])} free by symmetry, {len(skipped["tried"])} straight to '
              f'refinement, {len(todo)} to certify', flush=True)
        jobs = []
        for n in todo:
            try:
                nj = synth_node(n)
            except SystemExit as e:
                print(f'   !! {e}', flush=True)
                continue
            jobs.append((n, nj, '96/25', a.eps_geo, a.rounds, a.time_limit, a.depth,
                         stages, a.resolve_time, a.max_cols, cur_params))
        res = []
        t0 = time.time()
        # Work the depth in chunks with a fresh pool each time, so the worker count can be
        # re-read between chunks: while a level-1 certification wave is still running elsewhere
        # the driver stays at --workers_low, and takes the full --workers once that wave is gone.
        done_names = 0
        while done_names < len(jobs):
            w = a.workers if stage1_running() is False else a.workers_low
            chunk = jobs[done_names:done_names + max(1, 4 * w)]
            with mp.Pool(min(w, len(chunk))) as pool:
                for r in pool.imap_unordered(certify_one, chunk):
                    res.append(r)
                    nok = sum(1 for x in res if x['certified'])
                    print(f'[d{depth} {len(res)}/{len(jobs)} w{w}] {r["name"]}: '
                          f'{"PASS" if r["certified"] else "FAIL"} total={r["total"]} '
                          f'{r["seconds"]:.0f}s ({nok} ok) {"" if r["certified"] else r["tail"][:90]}',
                          flush=True)
                    st['done'][r['name']] = dict(certified=r['certified'], total=r['total'],
                                                 scale=r['scale'], seconds=r['seconds'],
                                                 tail=r['tail'][:200], depth=depth)
                    save_state(st)
            done_names += len(chunk)
        nok = sum(1 for x in res if x['certified'])
        nxt = []
        for n in queue:
            if certified(n) or sigma_free(n):
                continue
            nxt.extend(children_of(n))
        st['history'].append(dict(depth=depth, n=len(queue), certified_now=nok,
                                  free=len(skipped['certified']) + len(skipped['sigma']),
                                  open_after=len(nxt) // 8, elapsed=time.time() - t0))
        print(f'== depth {depth} done: {nok}/{len(jobs)} certified in {time.time()-t0:.0f}s; '
              f'{len(nxt)//8} nodes refined -> {len(nxt)} children at depth {depth+1}', flush=True)
        st['queue'] = nxt
        st['depth'] = depth + 1
        save_state(st)
    if st['queue']:
        print(f'STOPPED at depth {st["depth"]} (max_depth {a.max_depth}) with {len(st["queue"])} '
              f'nodes still open -- these RESIST refinement:', flush=True)
        resist = sorted({n.rsplit('_', 1)[0] for n in st['queue']})
        print('   ' + ', '.join(resist[:60]), flush=True)
        st['resisting'] = resist
        save_state(st)
    else:
        print('QUEUE EMPTY: every node handed to the driver is certified or free by symmetry.',
              flush=True)


def cmd_status(a):
    st = load_state()
    hc = have_certs()
    print(f'certificates on disk: {len(hc)}  ({len([c for c in hc if "_" not in c])} at level 1)')
    print(f'queue: {len(st["queue"])} at depth {st["depth"]}')
    print(f'attempted by the driver: {len(st["done"])}, '
          f'{sum(1 for v in st["done"].values() if v["certified"])} certified')
    for h in st.get('history', []):
        print('   ', h)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('seed')
    r = sub.add_parser('run')
    r.add_argument('--workers', type=int, default=9)
    r.add_argument('--workers_low', type=int, default=5,
                   help='workers to use while a separate certify_a27.py wave is still running '
                        '(the two together must not exceed the machine budget)')
    r.add_argument('--max_depth', type=int, default=4)
    r.add_argument('--resolve_time', type=float, default=400)
    r.add_argument('--time_limit', type=float, default=400)
    r.add_argument('--rounds', type=int, default=2)
    r.add_argument('--eps_geo', type=float, default=0.003)
    r.add_argument('--max_cols', type=int, default=400,
                   help='columns added per iteration of the EPS_GEO=3e-3 re-solve; the parent '
                        'already supplies a converged column set, so a small value keeps the '
                        'child LP fast')
    r.add_argument('--depth', type=int, default=56, help='verify_case.py subdivision depth')
    sub.add_parser('status')
    a = ap.parse_args()
    dict(seed=cmd_seed, run=cmd_run, status=cmd_status)[a.cmd](a)


if __name__ == '__main__':
    main()
