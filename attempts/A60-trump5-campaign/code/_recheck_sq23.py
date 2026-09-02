import sys,json,math; sys.path.insert(0,'code')
import tree60 as T
from tree60 import ladder_scan, gate, RBASIN
from caselp import Box
loc=[Box.from_json(d) for d in json.load(open('results/a60_located_sq1.json'))]
def hugof(b,cond=(),names=(),budget=5):
    g=gate(b,list(cond),[],budget,list(names)); h=g['hugs']
    return h if isinstance(h,str) else (h[0] if h else None)
byh={}
for b in loc: byh.setdefault(hugof(b),[]).append(b)
B1=byh['sq7'][0]; out={}
print('RE-CHECK squares 2,3 under corrected test (t-world, rBasin=%g)'%RBASIN, flush=True)
r1,_=ladder_scan(['sq7'],30,cond_boxes=[B1]); L=r1['levels'][-1]
print('square 2: L%d boxes=%d contain_t=%.4e contain_theta=%.4e all_inside=%s'%(L['level'],L['boxes'],L['max_containment_t'] or 0,L['max_containment_theta'] or 0,L['all_inside']), flush=True)
out['sq2']=dict(level=L['level'],boxes=L['boxes'],contain_t=L['max_containment_t'],contain_theta=L['max_containment_theta'],all_inside=L['all_inside'])
L1=[Box.from_json(d) for d in r1['final_residue']]
h1={}
for b in L1: h1.setdefault(hugof(b,[B1],['sq7'],4),[]).append(b)
nm2=sorted(h1)[0]; B2=h1[nm2][0]
r2,_=ladder_scan(['sq7',nm2],30,cond_boxes=[B1,B2]); L=r2['levels'][-1]
print('square 3 (cond +%s): L%d boxes=%d contain_t=%.4e contain_theta=%.4e all_inside=%s'%(nm2,L['level'],L['boxes'],L['max_containment_t'] or 0,L['max_containment_theta'] or 0,L['all_inside']), flush=True)
out['sq3']=dict(cond2=nm2,level=L['level'],boxes=L['boxes'],contain_t=L['max_containment_t'],contain_theta=L['max_containment_theta'],all_inside=L['all_inside'])
for k,v in out.items():
    if v['contain_t']: print('  %s margin vs rBasin = %.2fx'%(k, RBASIN/v['contain_t']), flush=True)
json.dump(out,open('results/a60_recheck_sq23_rbasin.json','w'),indent=1)
print('DONE', flush=True)
