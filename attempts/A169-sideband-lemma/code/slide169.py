"""A169 slide169: exact slide thresholds delta_min(theta) from Theorem B's clauses (1-D scan + golden refinement),
the winning clause and its zeta*, the crossing angle theta* where the mode-(a) law tan(theta/2) stops being the
minimiser, the pressed-square widened threshold angle, and numeric checks of the three support inequalities used in
the proof (wedge, triangle, pressed).  Light: < 1 CPU-min.  Output results/slide169.json."""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geo169 import W0
R2 = math.sqrt(2)
def w(phi): return abs(math.cos(phi)) + abs(math.sin(phi))
def supp(x1, y1, th, n):
    e = (math.cos(th), math.sin(th)); ep = (-e[1], e[0])
    return n[0]*x1 + n[1]*y1 + 0.5*(abs(n[0]*e[0]+n[1]*e[1]) + abs(n[0]*ep[0]+n[1]*ep[1]))
def q1_slide(theta, d):
    g = 0.5*(math.cos(theta)+math.sin(theta)); return (g+d, g, theta)
def clause_margins(x1, y1, th, c, steps=3600):
    """max margin per clause over its angle; (P) as the pressed-square separation."""
    best = {'NE': (-9, None), 'W': (-9, None), 'S': (-9, None), 'P': (-9, None)}
    for k in range(steps+1):
        a = (k/steps)*(math.pi/2); ca, sa = math.cos(a), math.sin(a)
        m = c*(ca+sa) - supp(x1, y1, th, (ca, sa))
        if m > best['NE'][0]: best['NE'] = (m, a)
        mp = -supp(x1, y1, th, (-ca, -sa)) - (ca+sa)   # min_Q1 (ca x + sa y) - (ca+sa) >= 0 is (P)
        if mp > best['P'][0]: best['P'] = (mp, a)
        if 0 < k < steps:
            for cond, n in (('W', (-sa, ca)), ('S', (ca, -sa))):
                m = c*ca - sa*sa - supp(x1, y1, th, n)
                if m > best[cond][0]: best[cond] = (m, a)
    return best
def nonlonely_margin(x1, y1, th, c):
    b = clause_margins(x1, y1, th, c)
    m = max(b['NE'][0], b['W'][0], b['S'][0], b['P'][0] if c > 1 else -9)
    which = max(b, key=lambda k: b[k][0] if (k != 'P' or c > 1) else -9)
    return m, which, b[which][1]
def delta_min(theta, c):
    lo, hi = 0.0, 1.5
    if nonlonely_margin(*q1_slide(theta, lo), c)[0] > 0: return 0.0, nonlonely_margin(*q1_slide(theta, lo), c)[1:]
    for _ in range(40):
        mid = 0.5*(lo+hi)
        if nonlonely_margin(*q1_slide(theta, mid), c)[0] > 0: hi = mid
        else: lo = mid
    return hi, nonlonely_margin(*q1_slide(theta, hi+1e-6), c)[1:]
out = {'slide': {}}
for deg in range(0, 90, 5):
    th = math.radians(deg); t = math.tan(th/2); row = {'tan_half': t}
    for name, c in (('unit', 1.0), ('widened', 1+W0)):
        d, (cl, ang) = delta_min(th, c)
        row[name] = dict(delta_min=d, clause=cl, angle_deg=math.degrees(ang) if ang is not None else None)
    out['slide'][str(deg)] = row
    print(deg, round(t, 4), row['unit'], row['widened'], flush=True)
# crossing angle theta*: largest theta with delta_min(unit) == tan(theta/2) (to 1e-6)
lo, hi = math.radians(45), math.radians(75)
for _ in range(30):
    mid = 0.5*(lo+hi); d, _x = delta_min(mid, 1.0)
    if d < math.tan(mid/2) - 1e-7: hi = mid
    else: lo = mid
out['theta_star_deg'] = math.degrees(lo)
# pressed-square widened threshold angle: largest theta with delta_min(widened) == 0
lo, hi = 0.0, math.radians(45)
for _ in range(30):
    mid = 0.5*(lo+hi); d, _x = delta_min(mid, 1+W0)
    if d > 1e-9: hi = mid
    else: lo = mid
out['pressed_widened_theta_deg'] = math.degrees(lo)
out['arccos_1_over_c_deg'] = math.degrees(math.acos(1/(1+W0)))
# inequality checks on a fine grid
worst = {'wedge': 9, 'triangle': 9, 'pressed_NE': 9, 'pressed_W': 9}
N = 720
for i in range(N+1):
    z = (i/N)*(math.pi/2)
    for j in range(4*N+1):
        phi = (j/(4*N))*2*math.pi
        worst['wedge'] = min(worst['wedge'], w(phi) - w(z+phi)*(math.cos(z)-math.sin(z)) - 2*math.sin(z)**2)
        worst['triangle'] = min(worst['triangle'], w(phi)*(math.cos(z)+math.sin(z)) + w(phi-z) - 2*(math.cos(z)+math.sin(z)))
    th = z
    for j in range(N+1):
        a = (j/N)*(math.pi/2)
        worst['pressed_NE'] = min(worst['pressed_NE'], w(a-th) - (2-w(th))*w(a))
        worst['pressed_W'] = min(worst['pressed_W'], w(th)*(math.cos(a)-math.sin(a)) + w(a-th) - 2*math.cos(a) + 2*math.sin(a)**2)
out['inequality_min_over_grid'] = worst
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'results', 'slide169.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'slide'}, indent=1))
