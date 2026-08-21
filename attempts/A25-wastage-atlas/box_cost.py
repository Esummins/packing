"""uniformity cost: certified dead area vs core-box size, same centre (1.275,1.275)^2."""
import time
from fractions import Fraction as F
from dead_region import PlacedBox
from atlas_lib import map_windows, wall_rects, disjointify, snap, _mid_corners, tanhalf
S = F(96, 25); c = F(51, 40)
def run(tag, t0, t1, hh):
    box = (c - hh/2, c + hh/2, c - hh/2, c + hh/2)
    B = PlacedBox(t0, t1, *box); B.filter_corners = _mid_corners(B)
    rects = disjointify(snap(wall_rects(*box, S), F(1,8), S))
    st=time.time(); r = map_windows([B], S, rects, (c, c), work_budget=6000)
    print(f"{tag:38s} area={float(r['area']):.4f} pass={r['n_pass']} "
          f"{time.time()-st:.0f}s", flush=True)
for (name, a, b) in (('th30-33', 30, 33), ('th30-31', 30, 31)):
    t0, t1 = tanhalf(a, False), tanhalf(b, True)
    for hh in (F(3,20), F(3,40), F(3,80), F(1,100)):
        run(f'{name} h={float(hh):.4f}', t0, t1, hh)
