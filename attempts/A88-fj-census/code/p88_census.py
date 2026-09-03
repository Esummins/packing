"""p88_census.py -- A88 T3 pilot: reader for the census chore's sample.

Reads results/census88_sample.jsonl in the schema of notes/sample_format.md:

  rows              A30 t3lib vocabulary, EQUALITY rows only
                    {'kind':'wall','i','corner','wall'} and
                    {'kind':'sep','o','e','p','kstar'}
                    The t3lib DOMINANCE rows are deliberately NOT emitted --
                    they are determined by (o, e, p, kstar) and the pilot
                    rebuilds them.  They are side conditions g >= 0, not
                    equalities, so they go into Structure.ineq.
  tilt_class        class id per square, class 0 = the pinned class if it exists
  class_order_strict  STRICT PARTIAL order [[lower, upper], ...]
  zero_class_pinned true iff class 0 exists and is phi = 0
  E / F / m / chi   bookkeeping, re-derived and cross-checked here

tag "F0+K0-1+K0-3" is the main block; "F0+K0-3 (K0-1 dropped)" the 100 extra
records with the slot-exclusion filter K0-1 not imposed.
"""
from __future__ import annotations

import glob
import json
import math
import os

import t3lib as T
import p88_struct as S

HALFPI = math.pi / 2.0

ROWKEYS = ('rows', 'H', 'structure', 'active_rows', 'support')
CLSKEYS = ('tilt_class', 'tilt_classes', 'classes', 'cls')
ORDKEYS = ('class_order_strict', 'order', 'tilt_order', 'class_order')
PINKEYS = ('zero_class_pinned', 'class0_pinned', 'pinned', 'pin0')


def _first(d, keys):
    for k in keys:
        if k in d:
            return d[k]
    return None


def census_sources(resdir):
    """[(path, label)] for every census-side input that has landed."""
    out = []
    p = os.path.join(resdir, 'census88_sample.jsonl')
    if os.path.exists(p) and os.path.getsize(p) > 0:
        out.append((p, 'census'))
    for pat in ('*k0drop*.jsonl', '*k0_drop*.jsonl', '*dropped*.jsonl'):
        for q in sorted(glob.glob(os.path.join(resdir, pat))):
            if q not in [x for x, _ in out] and os.path.getsize(q) > 0:
                out.append((q, 'k0drop'))
    return out


def dominance_of(rows):
    """Rebuild the t3lib dominance side conditions for every sep row."""
    out = []
    seen = set()
    for r in rows:
        if r['kind'] != 'sep':
            continue
        o, e, p, k = r['o'], r['e'], r['p'], r['k']
        for m in range(4):
            if m == k:
                continue
            key = (o, e, p, k, m)
            if key in seen:
                continue
            seen.add(key)
            out.append(T.dom_row(o, e, p, k, m))
    return out


def parse(rec, tag, label):
    rj = _first(rec, ROWKEYS)
    if not rj:
        return None
    rows = S.rows_from_json(rj)
    loaded = S.loaded_squares(rows)

    cj = _first(rec, CLSKEYS)
    cls = {}
    if isinstance(cj, dict):
        cls = {int(k): int(v) for k, v in cj.items()}
    elif isinstance(cj, list):
        if cj and isinstance(cj[0], (list, tuple)):
            for c, grp in enumerate(cj):
                for i in grp:
                    cls[int(i)] = c
        else:
            for i, v in enumerate(cj):
                if v is not None:
                    cls[int(i)] = int(v)
    for i in loaded:
        if i not in cls:
            cls[i] = max(cls.values(), default=-1) + 1
    cls = {i: cls[i] for i in loaded}
    ncls = int(rec.get('n_classes') or (max(cls.values()) + 1 if cls else 0))
    ncls = max(ncls, (max(cls.values()) + 1) if cls else 0)

    oj = _first(rec, ORDKEYS) or []
    order = [(int(a), int(b)) for a, b in oj
             if 0 <= int(a) < ncls and 0 <= int(b) < ncls]

    pj = _first(rec, PINKEYS)
    pinned = {}
    if pj is True:
        pinned[0] = 0.0
    elif isinstance(pj, dict):
        for k, v in pj.items():
            pinned[int(k)] = 0.0 if isinstance(v, bool) else float(v)
    elif isinstance(pj, (list, tuple)):
        for c in pj:
            pinned[int(c)] = 0.0

    # representative tilts: bookkeeping only -- free classes get the whole
    # [0, pi/2] bin at the root regardless
    reps = [pinned.get(c, HALFPI * (c + 1) / (ncls + 1.0)) for c in range(ncls)]

    extra = {'set': label, 'label': rec.get('tag') or label,
             'census_m': rec.get('m'), 'census_chi': rec.get('chi'),
             'census_E': rec.get('E'), 'census_F': rec.get('F'),
             'census_Ess': rec.get('Ess'), 'census_Esw': rec.get('Esw'),
             'census_rigid_possible': rec.get('rigid_possible'),
             'K0_1': rec.get('K0_1'), 'K0_2': rec.get('K0_2'),
             'K0_3': rec.get('K0_3'),
             'n_slot_squares': len(rec.get('slot_squares') or []),
             'wall_mask': rec.get('wall_mask')}
    st = S.Structure(tag, rows, cls, reps, pinned, order, extra,
                     ineq=dominance_of(rows))
    # cross-check the census bookkeeping against what we rebuilt
    extra['m_agrees'] = (rec.get('m') is None or rec['m'] == st.m)
    extra['chi_agrees'] = (rec.get('chi') is None or rec['chi'] == st.chi)
    return st


def load_census(path, label, limit=None):
    out = []
    with open(path) as f:
        for n, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            lab = label
            if 'K0-1 dropped' in str(rec.get('tag', '')):
                lab = 'k0drop'
            st = parse(rec, '%s_%05d' % (lab, n), lab)
            if st is not None:
                out.append(st)
            if limit and len(out) >= limit:
                break
    return out
