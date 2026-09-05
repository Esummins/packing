"""
A84 `class84.py` -- the PROTECTED-CLASS object (replaces pilot59's hard-wired trump5 constants).

A protected class S is a Young class of k_S pinned upright slot squares (A65 h10_boxspec) that
K1-protects itself: Trump's packing has D4 IMAGES whose upright squares realise every pin of S.
Each such image g contributes N = 11 - k_S "free" squares (the squares of g that are not on a
pin of S).  They play exactly the role Trump's six free squares play in A60:

  * ALIVE WITNESSES (Lemma A57-3 gate) -- alive84.py;
  * (D) TARGETS -- the residue box is discharged when it lies inside the landing radii of the
    image square it hugs;
  * CANARY -- a node realised by any image is never certified.

Pins are SLACK from the start (delta_pin = 2e-2, A57 G1 convention / A83 4.4):
    PINS[i] = Box(x - w, x + w, y - w, y + w, 0, 0),  w = delta / sqrt(2)
so the rational pin core has half-side a = (1/2 - delta) / (1 + 2^-24) -- the containment the
A63 B' transfer needs.  rho = 1/2 - a (cos th_c + sin th_c) and A = max |alpha| over the class's
slot coordinates (v = alpha + beta s) are recorded in every results file.

Witness families are EXACT (Fractions).  They come from A65's crowdfam.json, which searched and
exactly verified one family per class (source `trump-sym<k>`); the second image is obtained by
the class's own exact transpose symmetry (cx, cy, t) -> (cy, cx, (1-t)/(1+t)), an isometry of the
container that fixes the pin set setwise, and is then RE-VERIFIED exactly here.

    python code\class84.py --cls k4_08
writes results/class_<cls>.json and results/witnesses_<cls>.json.  No LP, seconds.
"""
import argparse, json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # A57 T18: pin BLAS to one thread BEFORE numpy loads   # noqa: F401
from caselp import Box, cos_sin_t
from alivewitness import gap_exact, admissible_exact

A65 = os.path.join(ROOT, "attempts", "A65-low-k-closure")
SPEC = os.path.join(A65, "results", "h10_boxspec.json")
CROWD = os.path.join(A65, "results", "crowdfam.json")
TRUMP = os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")

S_RAT = "969271/250000"
S0 = Fr(S_RAT)
S0F = float(S0)
DELTA_PIN = 2e-2                      # A57 G1 / A83 4.4 -- slack pins from the start
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)


# ------------------------------------------------------------------ float image geometry
def trump_scaled():
    """A65 crowdfam.trump_scaled: Trump's packing with centres blown up by lambda = s0/s_T
    (every contact of the rigid packing opens to a ~5.3e-8 gap; the squares stay unit)."""
    T = json.load(open(TRUMP))
    X = [list(r) for r in T["X"]]
    st = float(T["s"])
    lam = S0F / st
    return [[x * lam, y * lam, th] for (x, y, th) in X], st, lam


def symmetry(Y, k):
    """A65 crowdfam.symmetry: the 8 container symmetries.  bit0 x-flip, bit1 y-flip, bit2
    transpose.  theta returned mod pi/2."""
    out = []
    for (x, y, th) in Y:
        if k & 1:
            x, th = S0F - x, -th
        if k & 2:
            y, th = S0F - y, -th
        if k & 4:
            x, y, th = y, x, math.pi / 2 - th
        out.append([x, y, th % (math.pi / 2)])
    return out


# ------------------------------------------------------------------ exact helpers
def t_transpose(t):
    """the exact transpose (x, y, theta) -> (y, x, pi/2 - theta) in t = tan(theta/2)."""
    return (1 - t) / (1 + t)


def t_normalise(t):
    """map t into [0, 1] using theta ~ theta + 90 (same square): t -> (1 + t)/(1 - t)."""
    if t < 0:
        return (1 + t) / (1 - t)
    return t


def slack_pins(slots, delta=DELTA_PIN):
    """A60 slackcore60.slack_pins, on this class's slots."""
    w = delta / math.sqrt(2.0)
    return [Box(x - w, x + w, y - w, y + w, 0.0, 0.0) for (x, y) in slots], w


def rho_of(core):
    """A63 B' containment margin rho = 1/2 - a (cos th_c + sin th_c), exact."""
    a, tm = Fr(str(core.a)), Fr(str(core.tm))
    co, si = cos_sin_t(tm)
    return Fr(1, 2) - a * (co + si)


def alpha_of(v):
    """slot coordinates are v = alpha + beta s (beta in {0,1}, A63 cover-invariance).  Return
    |alpha|."""
    for c in (Fr(1, 2), Fr(3, 2), Fr(5, 2)):
        if abs(v - (S0 - c)) < Fr(1, 10 ** 9):
            return c
    return abs(v)


# ------------------------------------------------------------------ Lemma PD (pin drift)
# The seam width T' per class (theory lead): the contraction-tube radius at which the class's
# (D) leaves transfer.  lambda_max - 1 = (s0 - s_hat + T') / (s_hat - T'); the pin square of the
# DILATED family is Sigma_p + d, d = (lambda - 1) alpha_p per coordinate, always pointing INTO
# the container (alpha = the slot's L-family coordinate, or -(s0 - coordinate) for an R-family
# coordinate).  See pinguard.classify's `pin_full` branch for the kill rule.
T_PRIME = {"k4_08": Fr(457, 10000), "k3_05": Fr(13, 100),
           # A100: the two pilot classes.  Rule read off A84's two entries: T' is the tube radius
           # admissible for the class, just under T_K(delta_pin) from tier84_classes.json.
           # A_S = 3/2  =>  T_K = 0.0510  =>  T' = 457/10000 (A83's certified tube radius), the
           # SAME constant A84 used for k4_08 (also A_S = 3/2).  A_S = 1/2 => T_K = 0.1491 => 13/100.
           "k4_11": Fr(457, 10000), "k3_02": Fr(457, 10000)}
S_HAT_LO = Fr(387708359, 10 ** 8)      # rational LOWER bound on Trump's side 3.8770835900228...
DDEN = 10 ** 12                        # |d_max| is rounded OUTWARD on this grid (sound)


def signed_alpha(v):
    """alpha_p for one slot coordinate, signed so that (lambda - 1) alpha points INTO the
    container: +v for an L-family coordinate, -(s0 - v) for an R-family one."""
    for c in (Fr(1, 2), Fr(3, 2), Fr(5, 2)):
        if abs(v - (S0 - c)) < Fr(1, 10 ** 9):
            return -c
    return v


def pin_drift(name, pins_fr, t_prime=None):
    """-> (t_prime, lambda_max, [(dx, dy) per pin]) with |d| rounded outward."""
    tp = Fr(t_prime) if t_prime is not None else T_PRIME[name]
    lam_max = 1 + (S0 - S_HAT_LO + tp) / (S_HAT_LO - tp)

    def out(x):
        n = (abs(x) * DDEN)
        n = -(-n.numerator // n.denominator)        # ceil
        return Fr(n, DDEN) * (1 if x >= 0 else -1)

    D = [(out((lam_max - 1) * signed_alpha(a)), out((lam_max - 1) * signed_alpha(b)))
         for (a, b) in pins_fr]
    return tp, lam_max, D


# ------------------------------------------------------------------ the class object
def load_class(name, delta=DELTA_PIN, t_prime=None):
    spec = json.load(open(SPEC))
    assert spec["s0"] == S_RAT, "h10_boxspec s0 != %s" % S_RAT
    cl = spec["classes"][name]
    k_s, N = cl["k"], cl["N"]
    assert k_s + N == 11
    pins_fr = [(Fr(p[0]), Fr(p[1])) for p in cl["pins"]]
    slots = [(float(a), float(b)) for (a, b) in pins_fr]
    pins, w = slack_pins(slots, delta)
    rho = min(rho_of(b.core()) for b in pins)
    A = max(max(alpha_of(a), alpha_of(b)) for (a, b) in pins_fr)
    tp, lam_max, DRIFT = pin_drift(name, pins_fr, t_prime)
    from caselp import Core
    PIN_FULL = [(Core(px, py, Fr(0), Fr(1, 2)), Core(px + dx, py + dy, Fr(0), Fr(1, 2)))
                for (px, py), (dx, dy) in zip(pins_fr, DRIFT)]
    lemma_PD = dict(T_prime=str(tp), T_prime_f=float(tp), s_hat_lo=str(S_HAT_LO),
                    lambda_max=str(lam_max), lambda_max_minus_1_f=float(lam_max - 1),
                    d_max=[[str(dx), str(dy)] for (dx, dy) in DRIFT],
                    d_max_f=[[float(dx), float(dy)] for (dx, dy) in DRIFT],
                    rule=("core(B) meets Sigma_p at BOTH lambda = 1 and lambda = lambda_max "
                          "=> contradictory (the meeting set is convex in d)"))

    # ---- images: the container symmetries whose upright squares cover every pin ----------
    Y0, s_trump, lam = trump_scaled()
    images = []
    for k in range(8):
        Z = symmetry(Y0, k)
        up = [i for i in range(11) if min(Z[i][2], math.pi / 2 - Z[i][2]) < 1e-9]
        used, ok = [], True
        for (px, py) in slots:
            m = [i for i in up if abs(Z[i][0] - px) < 1e-5 and abs(Z[i][1] - py) < 1e-5
                 and i not in used]
            if not m:
                ok = False
                break
            used.append(m[0])
        if not ok:
            continue
        free_idx = [i for i in range(11) if i not in used]
        images.append(dict(key="g%d" % k, sym=k, pin_idx=used, free_idx=free_idx,
                           placements=[tuple(p) for p in Z],
                           free={"g%d_sq%d" % (k, i): tuple(Z[i]) for i in free_idx}))
    # A100: |G_S| is 1 or 2 across the protected tier (tier84_classes.json).  A84's two pilot
    # classes both had 2; k4_11 has exactly ONE compatible image (sym0).  Nothing in the engine
    # needs two -- the alive gate, the canary and the (D) targets are all per-image.
    assert 1 <= len(images) <= 2, "%s: expected 1 or 2 images (A71 G_S), got %d" % (name,
                                                                                   len(images))

    # ---- exact witness families ----------------------------------------------------------
    crowd = json.load(open(CROWD))["classes"][name]
    src_sym = int(crowd["source"].replace("trump-sym", ""))
    src = [im for im in images if im["sym"] == src_sym]
    assert src, "%s: crowdfam source sym%d is not an image of this class" % (name, src_sym)
    src = src[0]
    fam = [(Fr(f["cx"]), Fr(f["cy"]), t_normalise(Fr(f["t"]))) for f in crowd["family"]]
    assert len(fam) == N == len(src["free_idx"])
    wit = {src["key"]: {("g%d_sq%d" % (src_sym, i)): fam[j]
                        for j, i in enumerate(src["free_idx"])}}
    # the other image is the exact class transpose of the source (both pilot classes are
    # transpose-symmetric; verified below by the sym index arithmetic)
    others = [im for im in images if im["sym"] != src_sym]
    for oth in others:
        assert oth["sym"] == src_sym ^ 4, \
            "%s: the second image (sym%d) is not the transpose of sym%d" % (name, oth["sym"],
                                                                           src_sym)
        assert oth["free_idx"] == src["free_idx"]
        wit[oth["key"]] = {("g%d_sq%d" % (oth["sym"], i)): (cy, cx, t_transpose(t))
                           for i, (cx, cy, t) in zip(src["free_idx"],
                                                     [fam[j] for j in range(N)])}

    # ---- exact re-verification of EVERY image family -------------------------------------
    report = {}
    for im in images:
        g = im["key"]
        items = sorted(wit[g].items(), key=lambda kv: int(kv[0].split("sq")[-1]))
        sq, bad = [], []
        gmin_pin = None
        for (nm, (cx, cy, t)) in items:
            adm = admissible_exact((cx, cy), t, S0)
            if not adm:
                bad.append("%s not admissible at s0" % nm)
            gp = None
            for pb in pins:
                c = pb.core()
                gg = gap_exact((cx, cy), t, Fr(1, 2), (c.kx, c.ky), c.tm, c.a)
                gp = gg if gp is None else min(gp, gg)
            if gp is not None and gp <= 0:
                bad.append("%s meets a slack pin core (gap %s)" % (nm, gp))
            gmin_pin = gp if gmin_pin is None else min(gmin_pin, gp)
            th = 2 * math.atan(float(t))
            sq.append(dict(name=nm, cx=str(cx), cy=str(cy), t=str(t),
                           cx_f=float(cx), cy_f=float(cy), t_f=float(t),
                           theta_deg=math.degrees(th), theta_rad=th,
                           admissible=bool(adm),
                           min_gap_to_pins=str(gp), min_gap_to_pins_f=float(gp)))
        pg = None
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                (cxi, cyi, ti) = items[i][1]
                (cxj, cyj, tj) = items[j][1]
                gg = gap_exact((cxi, cyi), ti, Fr(1, 2), (cxj, cyj), tj, Fr(1, 2))
                pg = gg if pg is None else min(pg, gg)
        if pg is not None and pg <= 0:
            bad.append("family not strictly pairwise disjoint (min gap %s)" % pg)
        report[g] = dict(key=g, sym=im["sym"], m=len(sq), squares=sq,
                         min_pairwise_gap=str(pg), min_pairwise_gap_f=float(pg),
                         min_gap_to_pins=str(gmin_pin), min_gap_to_pins_f=float(gmin_pin),
                         source=("crowdfam %s" % crowd["source"] if im["sym"] == src_sym
                                 else "exact transpose of crowdfam %s" % crowd["source"]),
                         ok=(not bad), problems=bad)
        # float placement of every free square of the image (the (D) target geometry)
        report[g]["free"] = {nm: list(p) for nm, p in im["free"].items()}

    C = dict(name=name, s_rat=S_RAT, s0=S0F, k_s=k_s, N=N, budget_cover=N - 1, budget_no=N,
             delta_pin=delta, pin_halfwidth=w,
             pins_exact=[[str(a), str(b)] for (a, b) in pins_fr],
             SLOTS=slots, PINS=[b.to_json() for b in pins],
             pin_core_a=float(pins[0].core().a), rho=str(rho), rho_f=float(rho), A=str(A),
             A_f=float(A), lam=lam, s_trump=s_trump, lemma_PD=lemma_PD,
             images=[dict(key=im["key"], sym=im["sym"], pin_idx=im["pin_idx"],
                          free_idx=im["free_idx"], free=im["free"],
                          placements=[list(p) for p in im["placements"]]) for im in images],
             witnesses=report)
    # runtime handles (not serialised)
    C["_PINS"] = pins
    C["_PIN_FULL"] = PIN_FULL
    C["_wit"] = wit
    return C


def witnesses_path(name):
    return os.path.join(RES, "witnesses_%s.json" % name)


def write_class(name, delta=DELTA_PIN):
    C = load_class(name, delta)
    wit = dict(cls=name, s_rat=S_RAT, delta_pin=delta, pin_halfwidth=C["pin_halfwidth"],
               pin_core_a=C["pin_core_a"], rho=C["rho"], A=C["A"],
               images={g: C["witnesses"][g] for g in C["witnesses"]})
    json.dump(wit, open(witnesses_path(name), "w"), indent=1)
    out = {k: v for k, v in C.items() if not k.startswith("_") and k != "witnesses"}
    out["witness_summary"] = {g: dict(m=C["witnesses"][g]["m"],
                                      min_pairwise_gap_f=C["witnesses"][g]["min_pairwise_gap_f"],
                                      min_gap_to_pins_f=C["witnesses"][g]["min_gap_to_pins_f"],
                                      ok=C["witnesses"][g]["ok"],
                                      problems=C["witnesses"][g]["problems"],
                                      source=C["witnesses"][g]["source"])
                              for g in C["witnesses"]}
    json.dump(out, open(os.path.join(RES, "class_%s.json" % name), "w"), indent=1)
    return C, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--delta", type=float, default=DELTA_PIN)
    a = ap.parse_args()
    C, out = write_class(a.cls, a.delta)
    bad = [g for g in C["witnesses"] if not C["witnesses"][g]["ok"]]
    print(json.dumps(dict(cls=a.cls, k_s=C["k_s"], N=C["N"], delta_pin=C["delta_pin"],
                          pin_halfwidth=C["pin_halfwidth"], pin_core_a=C["pin_core_a"],
                          rho=C["rho"], rho_f=C["rho_f"], A=C["A"],
                          images=[im["key"] for im in C["images"]],
                          syms=[im["sym"] for im in C["images"]],
                          free_idx=C["images"][0]["free_idx"],
                          witness_summary=out["witness_summary"]), indent=1))
    if bad:
        print("STOP: exact witness verification FAILED for %s" % bad)
        sys.exit(3)
    print("wrote %s" % witnesses_path(a.cls))


if __name__ == "__main__":
    main()
