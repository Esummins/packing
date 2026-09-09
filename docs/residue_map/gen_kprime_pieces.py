"""Before/after drawing for the A172 per-piece K' fix on A168's S2 node.  The BEFORE module is the pre-A172
multibox.py extracted from commit 2b7172c3 into a temp file at run time; the AFTER module is the live A171 code.
Run: python docs/residue_map/gen_kprime_pieces.py   (writes kprime_pieces_S2.svg)"""
import os, subprocess, tempfile
ROOT = r"C:\Users\esumm\code\packing"; TMP = tempfile.mkdtemp()
src = subprocess.check_output(["git", "-C", ROOT, "show", "2b7172c3:attempts/A171-multibox-invariant/code/multibox.py"], text=True, encoding="utf-8")
src = "\n".join(('ATT = "C:/Users/esumm/code/packing/attempts"' if l.startswith("ATT = ") else l) for l in src.split("\n"))
open(os.path.join(TMP, "multibox_old.py"), "w", encoding="utf-8").write(src)
# ---- helpers
def clip_poly(poly, a, b):
    out = []
    def side(p): return (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i+1) % n]
        sp, sq = side(p), side(q)
        if sp >= 0: out.append(p)
        if (sp > 0 and sq < 0) or (sp < 0 and sq > 0):
            t = sp / (sp - sq)
            out.append((p[0] + t*(q[0]-p[0]), p[1] + t*(q[1]-p[1])))
    return out
def inter(A, B):
    P = list(A)
    for i in range(len(B)):
        P = clip_poly(P, B[i], B[(i+1) % len(B)])
        if not P: return []
    return P
def area(P):
    return abs(sum(P[i][0]*P[(i+1)%len(P)][1] - P[(i+1)%len(P)][0]*P[i][1] for i in range(len(P)))) / 2
# ---- main
import os, sys, math, importlib.util
from fractions import Fraction as Fr
ROOT = r"C:\Users\esumm\code\packing"; SP = os.path.dirname(os.path.abspath(__file__))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m
OLD = load("multibox_old", os.path.join(TMP, "multibox_old.py"))
NEW = load("multibox_new", os.path.join(ROOT, "attempts", "A171-multibox-invariant", "code", "multibox.py"))
PC = OLD.PC; from caselp import Box
ROLES = {
    "H":  (2.5674485, 2.67226625, 2.357813, 2.46263075, 45.0, 60.0),
    "B1": (3.127084, 3.1733821433529026, 1.5015011950128963, 1.5785397484754269, 45.0, 50.625),
    "D":  (3.223006893074939, 3.377084, 3.211365683498047, 3.377084, 0.0, 11.25),
}
COL = {"H": "#1565c0", "B1": "#c62828", "D": "#2e7d32"}
s0 = float(OLD.S_RAT)
def run(M):
    nd = M.Node(ROLES, name="S2"); nd.normalise(nsub=4, refine=3, verbose=False)
    inv = nd.assert_invariant(raise_on_fail=False)
    out = {}
    for k, mb in nd.boxes.items():
        polys = []
        for (bn, r) in mb.pieces:
            b = Box(float(r[0]), float(r[1]), float(r[2]), float(r[3]), M.deg_of_t(bn.t0), M.deg_of_t(bn.t1))
            polys.append(PC.build(b, n_grid=97, max_v=16).verts)
        P = polys[0]
        for Q in polys[1:]: P = inter(P, Q)
        hull = PC.build(mb.union_box(), n_grid=97, max_v=16)
        out[k] = dict(used=mb.pc.verts, a_used=mb.pc.area(), hull=hull.verts, a_hull=hull.area(),
                      pcs=P, a_pcs=float(area(P)), rects=list(mb.pieces), ubox=mb.ubox, kept=mb.kept_fraction())
    return out, nd.stats.get("passes"), inv["ok"]
old, p_old, ok_old = run(OLD); new, p_new, ok_new = run(NEW)
for k in ROLES:
    print(f"{k}: OLD kept {old[k]['kept']:.4f} K'used {old[k]['a_used']:.4f} (hull {old[k]['a_hull']:.4f}, pieces {old[k]['a_pcs']:.4f}) | "
          f"NEW kept {new[k]['kept']:.4f} K'used {new[k]['a_used']:.4f} (hull {new[k]['a_hull']:.4f}, pieces {new[k]['a_pcs']:.4f})")
print("passes", p_old, p_new, "invariant", ok_old, ok_new)
SC = 440 / s0
def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + dx*c - dy*s, cy + dx*s + dy*c) for dx, dy in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]]
out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="720" font-family="Segoe UI, sans-serif" style="background:#fff">',
       '<text x="30" y="24" font-size="14" font-weight="bold">A168 S2 node BR139/TRH-25: multibox.normalise BEFORE (committed A171: K\' rebuilt from the union hull) and AFTER (A172: exact intersection of per-piece K\'), same settings nsub=4 refine=3</text>']
for pi, (lab, R, passes, ok) in enumerate((("BEFORE (hull rebuild)", old, p_old, ok_old), ("AFTER (per-piece K')", new, p_new, ok_new))):
    OX = 30 + pi * 480; OY = 60
    X = lambda x: OX + x * SC; Y = lambda y: OY + (s0 - y) * SC
    pts = lambda P: " ".join(f"{X(float(x)):.1f},{Y(float(y)):.1f}" for x, y in P)
    out.append(f'<text x="{OX}" y="{OY-8}" font-size="12" font-weight="bold">{lab}: passes {passes}, invariant {"HOLDS" if ok else "FAILS"}</text>')
    out.append(f'<rect x="{X(0)}" y="{Y(s0)}" width="{s0*SC}" height="{s0*SC}" fill="none" stroke="#000" stroke-width="1.2"/>')
    for k, r in R.items():
        c = COL[k]; ub = r["ubox"]; cx, cy = 0.5*(ub.x0+ub.x1), 0.5*(ub.y0+ub.y1)
        for th in (math.radians(ub.th0), math.radians(ub.th1)):
            out.append(f'<polygon points="{pts(sq(cx, cy, th))}" fill="none" stroke="{c}" stroke-width="0.6" stroke-opacity="0.35"/>')
        out.append(f'<polygon points="{pts(sq(cx, cy, math.radians(0.5*(ub.th0+ub.th1))))}" fill="{c}" fill-opacity="0.05" stroke="{c}" stroke-width="0.9" stroke-opacity="0.6"/>')
        for (bn, rr) in r["rects"]:
            out.append(f'<rect x="{X(float(rr[0])):.1f}" y="{Y(float(rr[3])):.1f}" width="{(float(rr[1])-float(rr[0]))*SC:.1f}" height="{(float(rr[3])-float(rr[2]))*SC:.1f}" fill="none" stroke="{c}" stroke-width="0.5" stroke-opacity="0.7"/>')
        out.append(f'<polygon points="{pts(r["pcs"])}" fill="{c}" fill-opacity="0.35" stroke="{c}" stroke-width="1.5"/>')
        out.append(f'<polygon points="{pts(r["used"])}" fill="#fff" fill-opacity="0.5" stroke="{c}" stroke-width="1.1" stroke-dasharray="5,3"/>')
        out.append(f'<text x="{X(cx)-8:.1f}" y="{Y(cy)+4:.1f}" font-size="12" font-weight="bold" fill="{c}">{k}</text>')
ly = 530
out.append(f'<text x="30" y="{ly}" font-size="12" font-weight="bold">box: kept fraction, K\' used by the clip, K\' of the pieces (BEFORE -> AFTER)</text>')
for k in ROLES:
    ly += 17
    out.append(f'<text x="30" y="{ly}" font-size="11" fill="{COL[k]}">{k}: kept {old[k]["kept"]:.4f} -> {new[k]["kept"]:.4f};  K\' used {old[k]["a_used"]:.4f} -> {new[k]["a_used"]:.4f};  per-piece K\' {old[k]["a_pcs"]:.4f} -> {new[k]["a_pcs"]:.4f}  (pieces {len(old[k]["rects"])} -> {len(new[k]["rects"])})</text>')
for t in ["thin rects = surviving centre pieces (one per tilt sub-bin); solid = exact intersection of the per-piece K' at that fixed point; dashed = the K' the clip actually used (hull before, per-piece after)",
          "the band between dashed and solid in the BEFORE panel is the growth the hull rebuild threw away each pass; AFTER it should vanish (dashed on solid)",
          "faint squares = hypothesis square at box centre, mid-tilt, with extremal-tilt outlines; container [0,s]^2, s = %.6f" % s0,
          "kills on the BEFORE fixed point stand (hull K' is a subset of the true K'); only ALIVE verdicts were weakened"]:
    ly += 16; out.append(f'<text x="30" y="{ly}" font-size="10" fill="#333">{t}</text>')
out.append('</svg>')
p = os.path.join(ROOT, "docs", "residue_map", "kprime_pieces_S2.svg")
open(p, "w", encoding="utf-8").write("\n".join(out)); print("wrote", p)
import xml.dom.minidom; xml.dom.minidom.parse(p); print("xml ok")
