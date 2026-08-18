#!/usr/bin/env python3
"""make_jobs.py -- generate the job lists for run_queue.py (phase 1: n <= 30; phase 2: 31-45; phase 3: > 45)."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'records.json')))
TR = 40.18193729032971646523
P345 = round(math.degrees(math.atan(3 / 4)), 6)   # 36.869898


def rec(n):
    return R[str(n)]['record']


def trivial(n):
    return R[str(n)]['exact_integer']


def J(n, angles, time, fix=None, tag=None):
    d = {'n': n, 'angles': angles, 'time': time}
    if fix is not None:
        d['fix_s'] = fix
    if tag:
        d['tag'] = tag
    return d


phase1 = []
# calibration
phase1.append(J(11, [0, TR], 300))
# n <= 20, T = 600
for n in (17, 18, 19):
    phase1.append(J(n, [0, 45], 600))
for n in (17, 18):
    phase1.append(J(n, [0, TR], 600))
    phase1.append(J(n, [0, 30, 45], 600))
    phase1.append(J(n, [0, 20, 45], 600))
phase1.append(J(19, [0, TR], 600))
phase1.append(J(18, [0, 10, 45], 600))
phase1.append(J(18, [0, 15, 45], 600))
phase1.append(J(17, [0, 35, 45], 600))
# trivial-record cases: feasibility just below the record
phase1.append(J(12, [0, 45, TR], 600, fix=rec(12) - 1e-4))
phase1.append(J(20, [0, 45], 600, fix=rec(20) - 1e-4))
phase1.append(J(21, [0, 45, TR], 600, fix=rec(21) - 1e-4))
# 21-30, T = 900
phase1.append(J(26, [0, 45], 900))
phase1.append(J(27, [0, 45], 900))
for n in (28, 29):
    phase1.append(J(n, [0, 45], 900))
    phase1.append(J(n, [0, TR], 900))
    phase1.append(J(n, [0, 30, 45], 900))
    phase1.append(J(n, [0, 20, 45], 900))
phase1.append(J(26, [0, 45, TR], 900))
phase1.append(J(30, [0, 45], 900, fix=rec(30) - 1e-4))
json.dump(phase1, open(os.path.join(HERE, 'jobs_phase1.json'), 'w'), indent=1)

phase2 = []
for n in (37, 38, 40, 41, 39):
    phase2.append(J(n, [0, 45], 900))
for n in (37, 39, 41):
    phase2.append(J(n, [0, 30, 45], 900))
json.dump(phase2, open(os.path.join(HERE, 'jobs_phase2.json'), 'w'), indent=1)

phase3 = []
phase3.append(J(50, [0, P345, 90 - P345], 600))
for n in (52, 53, 54, 55, 65, 66, 67, 68, 69, 70, 71, 82, 83, 84, 85, 86, 87, 88, 89):
    phase3.append(J(n, [0, 45], 600))
json.dump(phase3, open(os.path.join(HERE, 'jobs_phase3.json'), 'w'), indent=1)
print(len(phase1), len(phase2), len(phase3), 'jobs; phase1 process-seconds =', sum(j['time'] for j in phase1))
