import json, math, numpy as np, itertools, time
S0=3.877084
def sq(cx,cy,th):
    co,s=math.cos(th),math.sin(th); return [(cx+0.5*(dx*co-dy*s), cy+0.5*(dx*s+dy*co)) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def sep(P,Q):
    for poly in (P,Q):
        for i in range(4):
            x0,y0=poly[i]; x1,y1=poly[(i+1)%4]; nx,ny=y0-y1,x1-x0
            p=[nx*x+ny*y for x,y in P]; q=[nx*x+ny*y for x,y in Q]
            if max(p)<=min(q)+1e-12 or max(q)<=min(p)+1e-12: return True
    return False
def inside(P): return all(-1e-9<=x<=S0+1e-9 and -1e-9<=y<=S0+1e-9 for x,y in P)
def R(B): return [(B[0],B[2]),(B[1],B[2]),(B[1],B[3]),(B[0],B[3])]
pins=[sq(0.5,0.5,0),sq(0.5,1.5,0),sq(0.5,S0-0.5,0),sq(S0-0.5,0.5,0),sq(S0-0.5,S0-0.5,0)]
BOX={'BL(1,0)':[1.0,2.04,0.0,1.026],'BR(1,0)':[1.837,2.877,0.0,1.026],'BR(0,1)':[2.852,3.877,1.0,2.04],'TR(0,1)':[2.852,3.877,1.837,2.877],'TR(1,0)':[1.837,2.877,2.852,3.877],'TL(1,0)':[1.0,2.04,2.852,3.877]}
def adm(P): return inside(P) and all(sep(P,Q) for Q in pins)
def poses(h,t0,t1,serve,n=9,nt=40):
    out=[]
    for x in np.linspace(h[0],h[1],n):
        for y in np.linspace(h[2],h[3],n):
            for t in np.linspace(math.radians(t0),math.radians(t1),nt):
                P=sq(x,y,t)
                if adm(P) and all(not sep(P,R(BOX[s])) for s in serve): out.append((x,y,t,P))
    return out
Hh=[2.49757,2.637327,1.519271,1.659028]
H=poses(Hh,53.13,64.011,[])
A=poses([2.192246,2.22625,0.678839,0.76231],0,90,['BL(1,0)','BR(0,1)','BR(1,0)'])
B=poses([3.353155,3.377084,2.358627,2.377085],0,90,['BR(0,1)','TR(0,1)'])
print("poses H",len(H),"A(cell10)",len(A),"B(cell23)",len(B))
HA=[(h,a) for h in H for a in A if sep(h[3],a[3])]; print("H-A disjoint pairs",len(HA))
HB=[(h,b) for h in H for b in B if sep(h[3],b[3])]; print("H-B disjoint pairs",len(HB))
hA=set(id(h) for h,a in HA); hB=set(id(h) for h,b in HB); print("H poses compatible with A:",len(hA),"with B:",len(hB),"with BOTH:",len(hA&hB))
tri=0
for h,a in HA:
    if id(h) in hB:
        for b in B:
            if sep(h[3],b[3]) and sep(a[3],b[3]): tri+=1; break
print("triples (H,A,B) pairwise disjoint:",tri)
