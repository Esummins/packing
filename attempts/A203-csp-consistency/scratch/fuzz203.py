"""fuzz: every piece pair rule S (scalar and batch) declares dead admits NO interior-disjoint pose pair (exact float SAT)."""
import sys, math, random, time
import numpy as np
sys.path.insert(0, 'attempts/A203-csp-consistency/code')
import csp203 as C, satbatch203 as SB
def sq(cx,cy,th):
    co,s=math.cos(th),math.sin(th); return [(cx+0.5*(dx*co-dy*s), cy+0.5*(dx*s+dy*co)) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def sep(P,Q):
    for poly in (P,Q):
        for i in range(4):
            x0,y0=poly[i]; x1,y1=poly[(i+1)%4]; nx,ny=y0-y1,x1-x0
            p=[nx*x+ny*y for x,y in P]; q=[nx*x+ny*y for x,y in Q]
            if max(p)<=min(q)+1e-12 or max(q)<=min(p)+1e-12: return True
    return False
rng=random.Random(1)
N=6000; R1=[];B1=[];R2=[];B2=[]
for _ in range(N):
    w1=rng.uniform(0.005,0.15); w2=rng.uniform(0.005,0.15)
    x1=rng.uniform(0,1); y1=rng.uniform(0,1)
    ang=rng.uniform(0,2*math.pi); d=rng.uniform(0.85,1.25)
    x2=x1+d*math.cos(ang); y2=y1+d*math.sin(ang)
    R1.append((x1,x1+w1,y1,y1+w1)); R2.append((x2,x2+w2,y2,y2+w2))
    a=rng.uniform(0,90); b=rng.uniform(0,90)
    B1.append((a,min(90,a+rng.uniform(0.2,20)))); B2.append((b,min(90,b+rng.uniform(0.2,20))))
t=time.time(); dead_s=[C.sat_dead(R1[i],B1[i],R2[i],B2[i]) for i in range(N)]; ts=time.time()-t
t=time.time(); dead_b=SB.sat_dead_batch(np.array(R1),np.array(B1),np.array(R2),np.array(B2)); tb=time.time()-t
print('scalar dead',sum(dead_s),'%.1f us/pair'%(1e6*ts/N),'batch dead',int(dead_b.sum()),'%.2f us/pair'%(1e6*tb/N),'agree',sum(int(a)==int(b) for a,b in zip(dead_s,dead_b)))
bad=0; checked=0
for i in range(N):
    if not (dead_s[i] or dead_b[i]): continue
    checked+=1
    r1,b1,r2,b2=R1[i],B1[i],R2[i],B2[i]
    for _ in range(300):
        P=sq(rng.uniform(r1[0],r1[1]),rng.uniform(r1[2],r1[3]),math.radians(rng.uniform(*b1)))
        Q=sq(rng.uniform(r2[0],r2[1]),rng.uniform(r2[2],r2[3]),math.radians(rng.uniform(*b2)))
        if sep(P,Q): bad+=1; print('REFUTED',i,r1,b1,r2,b2,dead_s[i],dead_b[i]); break
    # corners x endpoint tilts too
    for cx in (r1[0],r1[1]):
        for cy in (r1[2],r1[3]):
            for t1 in b1:
                for dx in (r2[0],r2[1]):
                    for dy in (r2[2],r2[3]):
                        for t2 in b2:
                            if sep(sq(cx,cy,math.radians(t1)),sq(dx,dy,math.radians(t2))): bad+=1; print('REFUTED-corner',i); break
print('dead pairs checked',checked,'refutations',bad)
