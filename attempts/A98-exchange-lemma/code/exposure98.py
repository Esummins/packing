r"""exposure98.py -- A98: exposure of A87's 21 verified depth-1 exchange placements.

For each EXCHANGE_SUCCESS row of exchange87.refine.json (verified placement Q0),
compute area(Q0 \ (A u B)) (the EXPOSURE, Lemma EXPOSE) and area(Q0 \ (A u B u S)),
using shapely polygons in the container frame.  Seconds, one process.
Writes results/exposure98.json.
"""
import os, sys, json, math
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ[_v]="1"
from shapely.geometry import Polygon
HERE=os.path.dirname(os.path.abspath(__file__)); A98=os.path.join(HERE,'..'); ATT=os.path.join(A98,'..')
sys.path.insert(0, os.path.join(ATT,'A87-drain-flow','code'))
import exchange87 as X
def poly(sq):
    return Polygon(X.verts_f(*sq))
packs={p['name']:p for p in X.load_packings()+X.load_anchored()+[X.load_trump()]}
ref=json.load(open(os.path.join(X.RESULTS,'exchange87.refine.json')))
ex=[json.loads(l) for l in open(os.path.join(X.RESULTS,'exchange87.jsonl'))]+[json.loads(l) for l in open(os.path.join(X.RESULTS,'exchange87.anchored.jsonl'))]
removed={(r['packing'],r['corner']):r.get('removed') for r in ex}
out=[]
for r in ref['rows']:
    if not r.get('EXCHANGE_SUCCESS'): continue
    pk=packs[r['packing']]; sqsQ,m=X.z_to_sqs(pk['z']); mf=float(m)
    sqs=[(float(a),float(b),float(c)) for a,b,c in sqsQ]
    A,B=removed[(r['packing'],r['corner'])]
    pl=r['placement']; Q0=poly((pl['cx_f'],pl['cy_f'],pl['theta_f']))
    slot=X.slot_square(r['corner'],m); S=poly((float(slot[0]),float(slot[1]),0.0))
    AB=poly(sqs[A]).union(poly(sqs[B]))
    expo=Q0.difference(AB).area; expoS=Q0.difference(AB.union(S)).area
    inA=Q0.intersection(poly(sqs[A])).area; inB=Q0.intersection(poly(sqs[B])).area
    # which untouched squares does Q0 come within 1e-3 of
    near=[i for i in range(11) if i not in (A,B) and Q0.distance(poly(sqs[i]))<1e-3]
    out.append({'packing':r['packing'],'corner':r['corner'],'removed':[A,B],'lambda':r['lambda_refined_pre_relax'],
                'theta_deg':r['theta_deg'],'exposure':expo,'exposure_excl_slot':expoS,'in_A':inA,'in_B':inB,
                'near_untouched_1e-3':near,'is_cell':abs(math.sin(2*math.radians(r['theta_deg'])))<1e-6})
    print('%-15s %s lam=%.8f expo=%.4f (exclS %.4f) inA=%.3f inB=%.3f near=%s cell=%s'%(r['packing'],r['corner'],r['lambda_refined_pre_relax'],expo,expoS,inA,inB,near,out[-1]['is_cell']))
json.dump(out,open(os.path.join(A98,'results','exposure98.json'),'w'),indent=1)
print('n',len(out),'min expo',min(o['exposure'] for o in out),'median',sorted(o['exposure'] for o in out)[len(out)//2])
