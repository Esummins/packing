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


# exact tilt angles read from Ellsworth's SVG sources (kingbird.myphotos.cc/packing/square-<n>.svg), mod 90,
# including the mirror classes (90 - a) where the SVG uses reflections:
A17 = [39.8049589797677950558662536965423, 90 - 36.6237863834465893201859433547298]
A18 = [24.2951889453645703307597489065, 90 - 24.2951889453645703307597489065]
A28 = [30.29140781651076883196499197898633682567489637045665129778]
A29a, A29b, A29c, A29d, A29i = 25.258655308351406, 20.800126762699611, 17.506268475732368, 24.962587989437719, 24.308358401346907
phase1 = []
phase1.append(J(11, [0, TR], 300))
phase1.append(J(17, [0] + A17, 600, tag='svg'))
phase1.append(J(18, [0] + A18, 600, tag='svg'))
phase1.append(J(19, [0, 45], 600))
phase1.append(J(17, [0, 45], 600))
phase1.append(J(18, [0, 45], 600))
phase1.append(J(17, [0, TR], 600))
phase1.append(J(18, [0, TR], 600))
phase1.append(J(12, [0, 45, TR], 600, fix=rec(12) - 1e-4))
phase1.append(J(20, [0, 45], 600, fix=rec(20) - 1e-4))
phase1.append(J(21, [0, 45, TR], 600, fix=rec(21) - 1e-4))
phase1.append(J(28, [0] + A28, 900, tag='svg'))
phase1.append(J(29, [0, A29a, 90 - A29a], 900, tag='svg2'))
phase1.append(J(29, [0, A29a, 90 - A29a, A29d, 90 - A29d], 900, tag='svg4'))
phase1.append(J(26, [0, 45], 900))
phase1.append(J(27, [0, 45], 900))
phase1.append(J(28, [0, 45], 900))
phase1.append(J(29, [0, 45], 900))
phase1.append(J(19, [0, TR], 600))
phase1.append(J(17, [0, 30, 45], 600))
phase1.append(J(18, [0, 20, 45], 600))
phase1.append(J(30, [0, 45], 900, fix=rec(30) - 1e-4))
phase1.append(J(28, [0, 30, 45], 900))
phase1.append(J(29, [0, 20, 45], 900))
json.dump(phase1, open(os.path.join(HERE, 'jobs_phase1.json'), 'w'), indent=1)

A37 = [45, 90 - 47.9133925257940968951470647263, 47.9133925257940968951470647263]
A39a, A39b = 43.715571105495432374596441579910035753318659539168, 37.425248552603373021422459112338754590283042719557
A41a, A41b = 36.419002746410604856962245860953162204062964432209, 31.565779005731469882403502468503934847888675969835
phase2 = []
phase2.append(J(37, [0] + A37, 900, tag='svg'))
phase2.append(J(39, [0, 90 - A39a, 90 - A39b], 900, tag='svg'))
phase2.append(J(41, [0, 90 - A41a, 90 - A41b], 900, tag='svg'))
phase2.append(J(38, [0, 45], 900))
phase2.append(J(40, [0, 45], 900))
phase2.append(J(37, [0, 45], 900))
phase2.append(J(39, [0, A39a, A39b], 900, tag='svgm'))
phase2.append(J(41, [0, A41a, A41b], 900, tag='svgm'))
json.dump(phase2, open(os.path.join(HERE, 'jobs_phase2.json'), 'w'), indent=1)

phase3 = []
phase3.append(J(50, [0, P345, 90 - P345], 600, tag='p345'))
phase3.append(J(53, [0] + A18, 600, tag='svg18'))
for n in (52, 54, 55, 65, 66, 67, 82, 84, 85, 89):
    phase3.append(J(n, [0, 45], 600))
json.dump(phase3, open(os.path.join(HERE, 'jobs_phase3.json'), 'w'), indent=1)
print(len(phase1), len(phase2), len(phase3), 'jobs; phase1 process-seconds =', sum(j['time'] for j in phase1))
