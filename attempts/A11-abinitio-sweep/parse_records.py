#!/usr/bin/env python3
"""
parse_records.py -- best-known s(n) for n <= 100 from the local copy of David Ellsworth's
"Squares in Squares" triangular-table view (Feb 2026), docs/papers/ellsworth_squares_in_squares__triangular_table.txt.

For n listed: s = the \\Nn{...} number or the integer.  For n not listed: "the closest packing shown to
the right of it is the best known packing" => record(n) = record(next listed n).  Proven-optimal n from
docs/known_results.md (1-10, 13-16, 22-25, 33-36, 46-49, 62-64, 79-81, 98-100).
Where the closed form is a polynomial root or has sqrt terms we keep the 15-digit decimal (page value) as
`record`, plus `polynomial` where the page prints one, and a guess of the tilt angles from the closed form:
 sqrt2 -> 45 deg, sqrt7 -> unknown (heuristics), Pythagorean 3-4-5 -> atan(3/4).
Writes records.json.
"""
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(HERE, '..', '..', 'docs', 'papers', 'ellsworth_squares_in_squares__triangular_table.txt')
PROVEN = set(list(range(1, 11)) + list(range(13, 17)) + list(range(22, 26)) + list(range(33, 37)) +
             list(range(46, 50)) + list(range(62, 65)) + list(range(79, 82)) + list(range(98, 101)))
THETA_TRUMP = 40.18193729032971646523


def main():
    lines = open(TXT, encoding='utf-8').read().split('\n')
    entries = {}
    i = 0
    while i < len(lines):
        m = re.match(r'^\s*(\d+)\. \[A (square-[^\]]+)\]', lines[i])
        if m:
            n = int(m.group(1))
            svg = m.group(2)
            body = []
            j = i + 1
            while j < len(lines) and not re.match(r'^\s*(\d+)\. \[A square', lines[j]):
                body.append(lines[j].strip())
                j += 1
            text = ' '.join(body)
            mm = re.search(r'\\Nn\{([0-9.]+)\}', text)
            if mm:
                s = float(mm.group(1))
                exact = False
            else:
                mm = re.search(r'\$s = (\d+)\$', text)
                s = float(mm.group(1))
                exact = True
            poly = None
            mp = re.search(r'\$([^$]*s\^[^$]*=0)\$', text)
            if mp:
                poly = mp.group(1)
            closed = re.search(r'\$s = ([^$]*)\$', text)
            closed = closed.group(1) if closed else None
            entries[n] = {'n': n, 'svg': svg, 'record': s, 'exact_integer': exact, 'closed_form': closed,
                          'polynomial': poly, 'text': text[:400]}
            i = j
        else:
            i += 1
    listed = sorted(entries)
    out = {}
    for n in range(1, 101):
        if n in entries:
            e = dict(entries[n])
            e['listed'] = True
        else:
            nxt = min(m for m in listed if m > n)
            e = dict(entries[nxt])
            e['n'] = n
            e['listed'] = False
            e['from_n'] = nxt
        e['proven'] = n in PROVEN
        # tilt-angle guesses from the closed form
        cf = e.get('closed_form') or ''
        angles = []
        if 'sqrt 2' in cf or 'sqrt{2}' in cf or (e.get('polynomial') and 'sqrt{2}' in e['polynomial']):
            angles.append(45.0)
        if 'sqrt 7' in cf:
            angles.append('sqrt7-unknown')
        if '4\\over 7' in cf:
            angles.append(round(math.degrees(math.atan(3 / 4)), 6))
        if n == 11:
            angles = [THETA_TRUMP]
        e['angle_hints'] = angles
        out[n] = e
    json.dump(out, open(os.path.join(HERE, 'records.json'), 'w'), indent=1)
    print('n  record  proven listed hints closed_form')
    for n in range(1, 101):
        e = out[n]
        print(f"{n:3d} {e['record']:.14f} {'P' if e['proven'] else '-'} {'L' if e['listed'] else '-'} "
              f"{e['angle_hints']} {e['closed_form']}")


if __name__ == '__main__':
    main()
