"""A85 Lemma K0-ROT numerics (theory lead).  Rotation stationarity of sigma at Trump's packing
and the rotational-ghost radius (rigid rotations of z-hat are k0_00 packings; how far do they
stay at side <= s0?).  Float, diagnostic only -- the lemma's exact form is docs/proofs/k0_route.md.

sigma(phi) = max(X(phi), Y(phi)) with X = max_i (x_i + h_i) - min_i (x_i - h_i) after a rigid
rotation by phi of the whole packing about the container centre.  h_i(theta) = (|cos| + |sin|)/2.
One-sided derivatives are computed both by the exact contact bookkeeping (K0-ROT formula) and by
finite differences of sigma(R_phi z-hat) (re-normalised, no container needed).
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T = json.load(open(os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")))
S = T["s"]
S0 = 969271 / 250000
X = [tuple(r) for r in T["X"]]


def h(th):
    return (abs(math.cos(th)) + abs(math.sin(th))) / 2.0


def rot(pl, phi, about=(S / 2, S / 2)):
    out = []
    for (x, y, th) in pl:
        dx, dy = x - about[0], y - about[1]
        c, s = math.cos(phi), math.sin(phi)
        out.append((about[0] + c * dx - s * dy, about[1] + s * dx + c * dy, th + phi))
    return out


def extents(pl):
    xs = [(x - h(th), x + h(th)) for (x, y, th) in pl]
    ys = [(y - h(th), y + h(th)) for (x, y, th) in pl]
    Xe = max(b for a, b in xs) - min(a for a, b in xs)
    Ye = max(b for a, b in ys) - min(a for a, b in ys)
    return Xe, Ye, max(Xe, Ye)


def dh_plus(th, eps=1e-12):
    """one-sided derivative of h in the +theta direction"""
    return (h(th + eps) - h(th)) / eps


def dh_minus(th, eps=1e-12):
    """one-sided derivative in the -theta direction: lim (h(th - e) - h(th))/e"""
    return (h(th - eps) - h(th)) / eps


def contacts(pl, tol=1e-6):
    """extremal wall contacts: which squares attain the four extents"""
    xs = [(x - h(th), x + h(th)) for (x, y, th) in pl]
    ys = [(y - h(th), y + h(th)) for (x, y, th) in pl]
    xl, xr = min(a for a, b in xs), max(b for a, b in xs)
    yb, yt = min(a for a, b in ys), max(b for a, b in ys)
    L = [i for i, (a, b) in enumerate(xs) if abs(a - xl) < tol]
    R = [i for i, (a, b) in enumerate(xs) if abs(b - xr) < tol]
    B = [i for i, (a, b) in enumerate(ys) if abs(a - yb) < tol]
    Tt = [i for i, (a, b) in enumerate(ys) if abs(b - yt) < tol]
    return L, R, B, Tt


def k0rot_derivatives(pl):
    """Lemma K0-ROT bookkeeping.  Rotation by +phi about ANY point: x_i' = -(y_i - cy), y_i' = x_i - cx.
    D+X = max_R(-(y_i-cy) + D+h_i) + max_L((y_i-cy) + D+h_i)   (the centre cancels)
    D-X = max_R(+(y_i-cy) + D-h_i) + max_L(-(y_i-cy) + D-h_i)
    D+Y = max_T((x_i-cx) + D+h_i) + max_B(-(x_i-cx) + D+h_i)
    D-Y = max_T(-(x_i-cx) + D-h_i) + max_B((x_i-cx) + D-h_i)"""
    L, R, B, Tt = contacts(pl)
    y = [p[1] for p in pl]
    x = [p[0] for p in pl]
    th = [p[2] for p in pl]
    DpX = max(-y[i] + dh_plus(th[i]) for i in R) + max(y[i] + dh_plus(th[i]) for i in L)
    DmX = max(y[i] + dh_minus(th[i]) for i in R) + max(-y[i] + dh_minus(th[i]) for i in L)
    DpY = max(x[i] + dh_plus(th[i]) for i in Tt) + max(-x[i] + dh_plus(th[i]) for i in B)
    DmY = max(-x[i] + dh_minus(th[i]) for i in Tt) + max(x[i] + dh_minus(th[i]) for i in B)
    return dict(L=L, R=R, B=B, T=Tt, DpX=DpX, DmX=DmX, DpY=DpY, DmY=DmY)


def main():
    Xe, Ye, sig = extents(X)
    d = k0rot_derivatives(X)
    out = dict(s_hat=S, s0=S0, X_extent=Xe, Y_extent=Ye, sigma=sig, tight_axes=[a for a, v in (("X", Xe), ("Y", Ye)) if abs(v - sig) < 1e-9],
               contacts=dict(L=d["L"], R=d["R"], B=d["B"], T=d["T"]),
               K0ROT=dict(DpX=d["DpX"], DmX=d["DmX"], DpY=d["DpY"], DmY=d["DmY"],
                          Dp_sigma=max(v for a, v in (("X", d["DpX"]), ("Y", d["DpY"])) if abs((Xe if a == "X" else Ye) - sig) < 1e-9),
                          Dm_sigma=max(v for a, v in (("X", d["DmX"]), ("Y", d["DmY"])) if abs((Xe if a == "X" else Ye) - sig) < 1e-9)))
    # finite differences of sigma(R_phi z)
    fd = {}
    for phi in (1e-7, 1e-6, 1e-5, 1e-4, 1e-3):
        sp = extents(rot(X, phi))[2]
        sm = extents(rot(X, -phi))[2]
        fd["%g" % phi] = dict(Dp=(sp - sig) / phi, Dm=(sm - sig) / phi, sigma_plus=sp, sigma_minus=sm)
    out["finite_differences"] = fd
    # ghost radius: largest |phi| with sigma(R_phi z) <= s0, by bisection on each side
    def ghost(sign):
        lo, hi = 0.0, 1e-3
        for _ in range(200):
            mid = (lo + hi) / 2
            if extents(rot(X, sign * mid))[2] <= S0:
                lo = mid
            else:
                hi = mid
        return lo
    gp, gm = ghost(+1), ghost(-1)
    rmax = max(math.hypot(x - S / 2, y - S / 2) for (x, y, th) in X)
    out["ghost"] = dict(phi_plus=gp, phi_minus=gm, max_centre_radius=rmax,
                        centre_move_bound=rmax * max(gp, gm), tilt_move=max(gp, gm),
                        landing_rc=1.6e-3, landing_rtheta=2.1e-3,
                        inside_landing=(rmax * max(gp, gm) < 1.6e-3 and max(gp, gm) < 2.1e-3))
    json.dump(out, open(os.path.join(ROOT, "attempts", "A85-k0-route", "results", "rot85.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
