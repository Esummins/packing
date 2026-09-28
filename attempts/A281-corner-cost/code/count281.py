"""A281 the f-table: every assignment of corner classes (T / Ff / Fw) modulo D4, its wall types, and what the
window facts cost it: SIDE (PiPi dead, TWO-POKERS), HOLDERS by the room count (FAMILY-STUCK dominoes + the ninth
square + PROJECTION sharing), the same with [M] SEPARATE-NOTCHES (one poker notch per free square), and the
normal-form lock count (chain link 7: every wall a row or a locked pair).    python count281.py  -> ../results/count281.json"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from wall281 import canonical  # noqa: E402

OUT_ROLE = {'Ff': 'Phi', 'Fw': 'Pi', 'T': 'tau'}      # a corner's role on its OUTGOING wall (wall c)
IN_ROLE = {'Ff': 'Pi', 'Fw': 'Phi', 'T': 'tau'}       # on its INCOMING wall (wall c-1)
NEVER_ROW = {('Phi', 'Pi'), ('Phi', 'tau')}           # a flat beside a tilted toucher is never a common-tilt row


def walls(roles):
    """wall w: (role of corner w on it, role of corner w+1 on it)."""
    return [(OUT_ROLE[roles[w]], IN_ROLE[roles[(w + 1) % 4]]) for w in range(4)]


def slots_needing_free(roles):
    """(wall, corner) slots whose only wall-neighbour supplier is a FLAT while the slot's own meeter is a POKER."""
    need = []
    for w, (r_out, r_in) in enumerate(walls(roles)):
        c_out, c_in = w, (w + 1) % 4
        if r_out == 'Pi' and r_in == 'Phi':
            need.append((w, c_out))
        if r_in == 'Pi' and r_out == 'Phi':
            need.append((w, c_in))
    return need


def corner_walls(c):
    return {c, (c - 1) % 4}


def min_free(roles, separate_notches):
    """least number of free squares (<= 3) covering every needed slot and the ninth-square condition.
    A free square lives in one corner neighbourhood N_c (PROJECTION) and may meet any subset of the 4 slots of c's two
    walls, or be a third BOX meeter.  separate_notches: it meets at most ONE poker notch (SEPARATE-NOTCHES [M])."""
    need = set(slots_needing_free(roles))
    all_slots = [(w, w) for w in range(4)] + [(w, (w + 1) % 4) for w in range(4)]
    options = [('box', None, frozenset())]
    for c in range(4):
        mine = [sl for sl in all_slots if sl[0] in corner_walls(c)]
        for k in range(1, 5):
            for sub in itertools.combinations(mine, k):
                if separate_notches and len(set(sub) & need) > 1:
                    continue
                options.append(('slots', c, frozenset(sub)))
    for h in range(0, 4):
        for combo in itertools.combinations_with_replacement(options, h):
            covered = set().union(*[o[2] for o in combo]) if combo else set()
            if not need <= covered:
                continue
            ninth = any(o[0] == 'box' for o in combo) or any(
                (w, w) in covered and (w, (w + 1) % 4) in covered for w in range(4))
            if ninth:
                return h
    return 4


def main():
    classes = sorted({canonical(list(r)) for r in itertools.product(['T', 'Ff', 'Fw'], repeat=4)})
    rows = []
    for roles in classes:
        wt = walls(roles)
        wt_sorted = [tuple(sorted(p)) for p in wt]
        f = sum(r != 'T' for r in roles)
        never_row = sum(p in NEVER_ROW for p in wt_sorted)
        rows.append({
            'roles': '/'.join(roles), 'f': f, 'walls': ['-'.join(p) for p in wt_sorted],
            'side_dead': ('Pi', 'Pi') in wt_sorted,
            'free_needed_slots': len(slots_needing_free(roles)),
            'h_count': min_free(roles, False),               # PROJECTION only  [T]
            'h_count_sep': min_free(roles, True),            # + SEPARATE-NOTCHES [M]
            'never_row_walls': never_row,
            'h_locks': (never_row + 1) // 2,                  # lock sharing <= the two walls of one corner
        })
    for r in rows:
        r['alive_side'] = not r['side_dead']
        r['alive_count'] = r['h_count'] <= 3
        r['alive_count_sep'] = r['h_count_sep'] <= 3
        r['alive_locks'] = max(r['h_locks'], 1) <= 3
        r['alive_all_T'] = r['alive_side'] and r['alive_count'] and r['alive_locks']
        r['alive_all_TM'] = r['alive_all_T'] and r['alive_count_sep']
    table = {}
    for f in range(5):
        sub = [r for r in rows if r['f'] == f]
        table[f] = {'classes': len(sub),
                    'alive_side': sum(r['alive_side'] for r in sub),
                    'alive_count': sum(r['alive_count'] for r in sub),
                    'alive_count_sep': sum(r['alive_count_sep'] for r in sub),
                    'alive_all_T': sum(r['alive_all_T'] for r in sub),
                    'alive_all_TM': sum(r['alive_all_TM'] for r in sub),
                    'survivors_T': [r['roles'] for r in sub if r['alive_all_T']],
                    'survivors_TM': [r['roles'] for r in sub if r['alive_all_TM']]}
    os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
    json.dump({'rows': rows, 'table': table}, open(os.path.join(HERE, '..', 'results', 'count281.json'), 'w'), indent=1)
    for r in rows:
        print('%-14s f=%d %-34s side%s need=%d h=%d h_sep=%d locks=%d(%d walls) alive[T]=%s alive[T+M]=%s' % (
            r['roles'], r['f'], ' '.join(r['walls']), 'DEAD' if r['side_dead'] else ' ok ', r['free_needed_slots'],
            r['h_count'], r['h_count_sep'], r['h_locks'], r['never_row_walls'], r['alive_all_T'], r['alive_all_TM']))
    for f in range(5):
        t = table[f]
        print('f=%d: %d classes, alive by side %d, by count %d (+sep %d), all [T] %d, all [T+M] %d' % (
            f, t['classes'], t['alive_side'], t['alive_count'], t['alive_count_sep'], t['alive_all_T'], t['alive_all_TM']))


if __name__ == '__main__':
    main()
