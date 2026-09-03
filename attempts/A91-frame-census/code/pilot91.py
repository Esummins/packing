import json,math,os,random,time
import numpy as np, census91 as C, frame91 as F, real91 as R, geom91 as G
import canary91 as CA
rng=random.Random(777); ws,tot=R.shape_weights()
out=[]; t0=time.time()
c1,f1=CA.C1()
r=R.bnb(f1,box_cap=20000,time_cap=120.0)
r['tag']='C1_archetype'; r['margin_root']=R.realisable(f1)[1]; out.append(r)
print('C1 archetype:',r,flush=True)
done=0
while done<20 and time.time()-t0<420:
    f,shape=R.random_frame_L0(rng,ws,tot)
    if f is None: continue
    if R.sample_terminals(f,rng) is None: continue
    ok=True
    for s in f.slots():
        ch,_=R.chains(f,s,cap=500)
        if not ch: ok=False;break
        f.column[s]=rng.choice(ch)
    if not ok: continue
    good,marg=R.realisable(f)
    r=R.bnb(f,box_cap=20000,time_cap=30.0)
    r['tag']='sample%d'%done; r['margin_root']=marg; r['R6_realisable']=bool(good)
    r['shape']=[list(shape[0]),list(shape[1]),shape[2]]
    out.append(r); done+=1
    print(done,r['verdict'],'R6ok',good,'boxes',r['boxes'],'%.3fs'%r['seconds'],flush=True)
json.dump(out,open(os.path.join(G.RESULTS,'t3pilot91.json'),'w'),indent=1)
sec=[x['seconds'] for x in out[1:]]
nc=sum(1 for x in out[1:] if x['verdict']=='CLOSED')
print('PILOT: %d frames, %d CLOSED (%.1f%%), mean %.4f s/frame, max %.3f'%(len(sec),nc,100.0*nc/max(len(sec),1),float(np.mean(sec)),max(sec)))
