"""Is the big near-upright value geometry or an artefact?  Point-placement vs
core-box, upright vs mid-tilt, same centre."""
import time
from fractions import Fraction as F
from dead_region import Placed, PlacedBox
from atlas_lib import map_windows, wall_rects, disjointify, snap, _mid_corners
S = F(96, 25)
def run(tag, placed, ctr, box):
    rects = disjointify(snap(wall_rects(box[0],box[1],box[2],box[3], S), F(1,8), S))
    t0=time.time()
    r = map_windows(placed, S, rects, ctr, work_budget=4000)
    print(f"{tag:34s} area={float(r['area']):.4f} pass={r['n_pass']} "
          f"tops={r['n_tops']} trunc={r['truncated']} {time.time()-t0:.0f}s")
c = F(51,40)   # 1.275
box = (F(6,5), F(27,20), F(6,5), F(27,20))
pbox = (c, c, c, c)
for (tag, t) in (('upright th=1.5deg', F(13090,1000000)), ('mid th=31.5deg', F(281998,1000000))):
    P = Placed(c, c, t); run(f'POINT {tag}', [P], (c,c), pbox)
for (tag, t0, t1) in (('th 0-3deg', F(0), F(262,10000)), ('th 30-33deg', F(2679491,10000000), F(2962131,10000000))):
    B = PlacedBox(t0, t1, *box); B.filter_corners=_mid_corners(B)
    run(f'BOX   {tag}', [B], ((box[0]+box[1])/2,(box[2]+box[3])/2), box)
