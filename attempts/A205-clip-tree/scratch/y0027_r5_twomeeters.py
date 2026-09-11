"""Is Y0027 / g1 / leaf R.5 really dead?  The kill: BL(1,0) needs two distinct non-pin meeters; H misses; the anonymous
union has diameter < 1 so at most one.  The audit exhibited ONE meeter G (not a refutation of cap 1).  Here: search for
TWO disjoint admissible meeters G1, G2 of BL(1,0) coexisting with some H pose (R.5 box) and F1 (row 23 box)."""
import math, random, itertools
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
BL10=[1.0,2.04,0.0,1.026]
def adm(P): return inside(P) and all(sep(P,Q) for Q in pins)
rng=random.Random(1)
# meeter candidates of BL(1,0): centres in the window [0.5,2.75]x[0.5,1.73], any tilt, admissible, meeting the box
G=[]
while len(G)<6000:
    x=rng.uniform(0.5,2.75); y=rng.uniform(0.5,1.75); t=rng.uniform(0,math.pi/2); P=sq(x,y,t)
    if adm(P) and not sep(P,R(BL10)): G.append((x,y,t,P))
print("admissible meeters of BL(1,0):", len(G))
pairs=[(a,b) for a,b in itertools.combinations(G,2) if math.hypot(a[0]-b[0],a[1]-b[1])>=1.0 and sep(a[3],b[3])]
print("disjoint meeter PAIRS (ignoring H, F1):", len(pairs))
# now with H (R.5 box) and F1 (row 23 box)
Hb=[2.358,2.379,1.799,1.939,87.25,90.0]; Fb=[3.354,3.377,2.226,2.377,0.0,90.0]
Hs=[]; 
for _ in range(400):
    h=(rng.uniform(Hb[0],Hb[1]),rng.uniform(Hb[2],Hb[3]),math.radians(rng.uniform(Hb[4],Hb[5]))); P=sq(*h)
    if adm(P): Hs.append(P)
Fs=[]
for _ in range(400):
    f=(rng.uniform(Fb[0],Fb[1]),rng.uniform(Fb[2],Fb[3]),math.radians(rng.uniform(Fb[4],Fb[5]))); P=sq(*f)
    if adm(P): Fs.append(P)
print("H poses",len(Hs),"F1 poses",len(Fs))
ok=0; ex=None
for a,b in pairs[:20000]:
    if any(sep(a[3],h) and sep(b[3],h) for h in Hs[:50]) and any(sep(a[3],f) and sep(b[3],f) for f in Fs[:20]):
        ok+=1; ex=ex or (a[:3],b[:3]); 
print("pairs coexisting with some H and F1 pose:", ok, "example:", ex)
if pairs: 
    a,b=pairs[0]; print("example pair (no H/F1):", [round(v,3) for v in a[:2]], round(math.degrees(a[2]),1), [round(v,3) for v in b[:2]], round(math.degrees(b[2]),1))
