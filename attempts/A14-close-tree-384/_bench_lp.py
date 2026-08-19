import json, sys, time, os
sys.path.insert(0,'.')
import numpy as np, highspy
import lpbox, caselp
from lpbox import *
from caselp import Hyp
st = json.load(open('results/n2_long_state.json'))
tree = json.load(open('../A13-case-lp-bnb/results/t384c/tree.json'))
rec = [n for n in tree['nodes'] if n['id']==2][0]
hyp = Hyp.from_json(rec['hyp']); s=3.84
caselp.NoFam.s_hi = s-0.5
sym = Sym('C1', s); tbox = ThetaBox(ThetaBox.parse('0-90'), 'C4')
orbits, rows = [tuple(o) for o in st['orbits']], [tuple(r) for r in st['rows']]
print(len(orbits), len(rows))
def build(norb, strat=None, presolve=None):
    M = Model(s, 10, sym, tbox, hyp=hyp)
    if strat is not None: M.h.setOptionValue('simplex_strategy', strat)
    if presolve is not None: M.h.setOptionValue('presolve', presolve)
    for (x,y) in orbits[:norb]: M.add_orbit(x,y)
    for r in rows: M.add_row(*r)
    return M
mode = sys.argv[1]
if mode == 'cold':
    for strat in (1, 4):
        M = build(len(orbits), strat)
        t=time.time(); obj=M.solve(); print('cold strat',strat,'rows',len(M.rows),'cols',len(M.orbits),'obj',obj,'t',time.time()-t, flush=True)
elif mode == 'inc':
    # warm: solve with first 3800 orbits, then add 1500 columns, then solve with dual (1) / primal (4)
    strat = int(sys.argv[2])
    M = build(3800, 1)
    t=time.time(); obj=M.solve(); print('base obj',obj,'t',time.time()-t, flush=True)
    for (x,y) in orbits[3800:5300]: M.add_orbit(x,y)
    M.h.setOptionValue('simplex_strategy', strat)
    t=time.time(); obj=M.solve(); print('after +1500 cols strat',strat,'obj',obj,'t',time.time()-t, flush=True)
elif mode == 'both':
    strat = int(sys.argv[2])
    M = Model(s, 10, sym, tbox, hyp=hyp)
    M.h.setOptionValue('simplex_strategy', 1)
    for (x,y) in orbits[:3800]: M.add_orbit(x,y)
    for r in rows[:6200]: M.add_row(*r)
    t=time.time(); obj=M.solve(); print('base obj',obj,'t',time.time()-t, flush=True)
    for (x,y) in orbits[3800:5300]: M.add_orbit(x,y)
    for r in rows[6200:]: M.add_row(*r)
    M.h.setOptionValue('simplex_strategy', strat)
    t=time.time(); obj=M.solve(); print('after +1500 cols +748 rows strat',strat,'obj',obj,'t',time.time()-t, flush=True)
elif mode == 'rows':
    strat = int(sys.argv[2])
    M = Model(s, 10, sym, tbox, hyp=hyp)
    M.h.setOptionValue('simplex_strategy', 1)
    for (x,y) in orbits: M.add_orbit(x,y)
    for r in rows[:6200]: M.add_row(*r)
    t=time.time(); obj=M.solve(); print('base obj',obj,'t',time.time()-t, flush=True)
    for r in rows[6200:]: M.add_row(*r)
    M.h.setOptionValue('simplex_strategy', strat)
    t=time.time(); obj=M.solve(); print('after +748 rows strat',strat,'obj',obj,'t',time.time()-t, flush=True)
