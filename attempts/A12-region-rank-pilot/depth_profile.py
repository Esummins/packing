"""depth profile: alpha of the fractional support graph when only edges with overlap depth > d are kept."""
import json, sys, math, numpy as np
from geom import corners, max_independent_set, DEG
from analyze import load_images

def depth_matrix(P):
    n=len(P); D=np.full((n,n),np.inf)
    C=[corners(*p) for p in P]
    for i in range(n):
        for j in range(i+1,n):
            dmin=np.inf
            for th in (P[i,2],P[j,2]):
                for ax in ((math.cos(th),math.sin(th)),(-math.sin(th),math.cos(th))):
                    a=C[i]@ax; b=C[j]@ax
                    dmin=min(dmin, min(a.max(),b.max())-max(a.min(),b.min()))
            D[i,j]=D[j,i]=dmin
    return D

res=json.load(open(sys.argv[1])); s,P=load_images(res,1e-3)
W=P[:,3]; frac=np.nonzero(W<1-1e-6)[0]; Pf=P[frac]; Wf=W[frac]
D=depth_matrix(Pf[:,:3])
ov=D>1e-9
print("fractional support",len(Pf),"sum",Wf.sum())
for d in [1e-9,0.005,0.01,0.02,0.03,0.05,0.08,0.1,0.15,0.2,0.3]:
    adj=D>d; np.fill_diagonal(adj,False)
    a,sel,st=max_independent_set(adj)
    print(f"  edges with depth > {d:<5}: {int(adj.sum()//2):4d} edges  alpha = {a}   ({'cut violated' if a < Wf.sum()-1e-9 else 'no violation'})")
# whole support incl corners
D2=depth_matrix(P[:,:3])
for d in [1e-9,0.01,0.02,0.05,0.1]:
    adj=D2>d; np.fill_diagonal(adj,False)
    a,sel,st=max_independent_set(adj)
    print(f"  ALL support: depth > {d}: alpha = {a} vs {W.sum():.2f}")
# list edges among fractional part sorted by depth
I,J=np.nonzero(np.triu(ov,1))
ed=sorted([(D[i,j],i,j) for i,j in zip(I,J)])
print("smallest depths:",[(round(d,4),tuple(np.round(Pf[i,:2],2)),round(Pf[i,2]/DEG,1),tuple(np.round(Pf[j,:2],2)),round(Pf[j,2]/DEG,1)) for d,i,j in ed[:12]])
