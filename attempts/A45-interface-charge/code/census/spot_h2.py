"""A45-B spot measurement: RULER + CHARGE on the 10 A43-H2 k=3 spine survivors
(attempts/A43-spine-census/results/h2/survivors_k3.txt) with their certified tilt windows.

A spine type is (k; end types F/C; link types FL/CEab/CEba/CC).  F end = wall-flush (WF, class 0
pin); C end = wall-corner (WC, a charged corner type).  FL link = flush contact; CE/CC = corner
type.  The k=3 survivors are all C-C, so the flush components carry NO wall pin.
"""
import os, re, sys, json
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A45 = os.path.abspath(os.path.join(HERE, '..', '..'))
H2 = os.path.abspath(os.path.join(A45, '..', 'A43-spine-census', 'results', 'h2'))
sys.path.insert(0, HERE)
import ruler
import charge as CH

TAB = CH.load_table()
SQRT2 = ruler.SQRT2_UP


def parse(line):
    name = line.split('\t')[0].strip()
    ends, links = name.split('-')[0] + name.split('-')[-1], name.split('-')[1].split('.')
    win = re.findall(r'\[(\d+),\s*(\d+)\]', line)
    return dict(name=name, e_left=name.split('-')[0], e_right=name.split('-')[-1],
                links=links, windows=[(int(a), int(b)) for a, b in win])


def run():
    rows = []
    for line in open(os.path.join(H2, 'survivors_k3.txt')):
        if not line.strip():
            continue
        t = parse(line)
        k = len(t['links']) + 1
        fl = [(i, i + 1) for i, lk in enumerate(t['links']) if lk == 'FL']
        ce = [(i, i + 1) for i, lk in enumerate(t['links']) if lk != 'FL']
        wf, wc = [], []
        (wf if t['e_left'] == 'F' else wc).append((0, 0))          # left wall
        (wf if t['e_right'] == 'F' else wc).append((k - 1, 2))     # right wall
        # cos+sin over the class window: the extent cap must use the LARGEST value (weakest)
        lo, hi = t['windows'][0]
        cs = SQRT2 if (lo <= 45 <= hi) else max(
            CH.F(1), CH.F(1))                                       # windows here all contain 45
        r = ruler.analyse(k, fl, wf, cs_max=cs)
        wm = [0] * k
        wm[0] |= 1
        wm[k - 1] |= 4
        # min-over-window bins for the two wall-corner ends
        bins = CH.bins_of_window(min(lo, 45), min(hi, 45))
        c_min_sound = CH.min_wc(TAB, bins)
        tot, det = CH.decoration_charge(TAB, k, wm, wc, ce, class_windows={
            0: (lo, hi), k - 1: (lo, hi)}, force_ce=False)
        tot_ce, _ = CH.decoration_charge(TAB, k, wm, wc, ce, class_windows={
            0: (lo, hi), k - 1: (lo, hi)}, force_ce=True)
        n_charged = len(wc) + len(ce)
        rows.append(dict(
            type=t['name'], window=[lo, hi], fl_links=len(fl), ce_links=len(ce),
            n_wc=len(wc), n_ce=len(ce),
            ruler_kill=r['kill'], ruler_gauge_full=r['gauge_full'],
            ruler_gauge_ok=r['gauge_ok'],
            ruler_keep=(r['gauge_ok'] / r['gauge_full']) if r['gauge_full'] else 1.0,
            charge_min_semantics=float(tot), charge_ce_forced=float(tot_ce),
            charge_kill=bool(tot > CH.B0), reachable_bins=bins,
            min_table_wc_over_window=float(c_min_sound),
            required_per_contact_charge_to_kill=float(CH.B0 / n_charged) if n_charged else None,
            ownership_ceiling_per_contact=float(TAB['cap_per_contact']
                                                if TAB.get('cap_per_contact') else F(1, 16)),
            table_max_entry=float(TAB.get('max_entry', 0)),
            can_ever_kill=bool(n_charged * (TAB['cap_per_contact'] or F(1, 16)) > CH.B0)))
    return rows


if __name__ == '__main__':
    rows = run()
    for r in rows:
        print('%-16s win%s  RULER kill=%-5s keep=%d/%d  CHARGE sum=%.6f kill=%-5s  '
              'need %.3f/contact (ownership ceiling %.6f)'
              % (r['type'], r['window'], r['ruler_kill'], r['ruler_gauge_ok'],
                 r['ruler_gauge_full'], r['charge_min_semantics'], r['charge_kill'],
                 r['required_per_contact_charge_to_kill'],
                 r['ownership_ceiling_per_contact']))
    json.dump(rows, open(os.path.join(A45, 'results', 'spot_h2_k3.json'), 'w'), indent=1)
    print('kills: RULER %d/%d, CHARGE %d/%d'
          % (sum(r['ruler_kill'] for r in rows), len(rows),
             sum(r['charge_kill'] for r in rows), len(rows)))
