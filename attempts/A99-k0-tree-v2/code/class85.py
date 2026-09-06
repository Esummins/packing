"""
A85 `class85.py` -- the UNSTRATIFIED class object k0_00.

k0_00 is the root problem: NO pins (k_S = 0), N = 11 free squares, and ALL EIGHT container
symmetries of Trump are compatible, so G_S = D4 and there are 8 witness families.

Derived from A84's `class84.load_class`, with the pin machinery removed:
  * pins = [], SLOTS = [], K_S = 0, A_S = 0, PIN_FULL = [] (Lemma PD is vacuous: no pin drifts);
  * images = class84.symmetry(trump_scaled, k) for k = 0..7 (float geometry, the (D) targets);
  * exact witnesses: crowdfam.json['classes']['k0_00']['family'] (source trump-sym0, exact
    rationals) mapped to the other 7 images by the EXACT D4 maps on plane points about the
    container centre, in the SAME composition order class84.symmetry uses:
        bit0 x-flip     x -> s0 - x,  t -> -t
        bit1 y-flip     y -> s0 - y,  t -> -t
        bit2 transpose  (x, y) -> (y, x),  t -> (1 - t)/(1 + t)
    then t normalised into [0, 1] by the theta ~ theta + 90 glue (same square).
  * every image family re-verified EXACTLY (alivewitness.admissible_exact + pairwise
    gap_exact > 0); no pin gaps to check.

    python code/class85.py --cls k0_00
writes results/class_k0_00.json and results/witnesses_k0_00.json.  No LP, seconds.
"""
import argparse, json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # A57 T18: pin BLAS to one thread BEFORE numpy loads   # noqa: F401
from alivewitness import gap_exact, admissible_exact
import class84 as K84

S_RAT = K84.S_RAT
S0 = K84.S0
S0F = K84.S0F
DELTA_PIN = 0.0                      # k0_00 has no pins
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)

CROWD = K84.CROWD
CLSNAME = "k0_00"


# ------------------------------------------------------------------ exact t normalisation
def t_norm(t):
    """map t = tan(theta/2) into [0, 1] using the theta ~ theta +- 90 glue (same square)."""
    for _ in range(8):
        if t < 0:
            t = (1 + t) / (1 - t)
        elif t > 1:
            t = (t - 1) / (t + 1)
        else:
            return t
    raise AssertionError("t_norm did not converge for %s" % t)


def exact_sym(cx, cy, t, k):
    """the EXACT container symmetry k, in the same composition order as class84.symmetry."""
    if k & 1:
        cx, t = S0 - cx, -t
    if k & 2:
        cy, t = S0 - cy, -t
    if k & 4:
        cx, cy, t = cy, cx, (1 - t) / (1 + t)
    return cx, cy, t_norm(t)


def theta_deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t))) % 90.0


# ------------------------------------------------------------------ the class object
def load_class(name=CLSNAME, delta=DELTA_PIN, t_prime=None):
    assert name == CLSNAME, "class85 only builds %s (got %s)" % (CLSNAME, name)
    k_s, N = 0, 11

    # ---- images: all 8 container symmetries (no pins to match) ---------------------------
    Y0, s_trump, lam = K84.trump_scaled()
    images = []
    for k in range(8):
        Z = K84.symmetry(Y0, k)
        free_idx = list(range(11))
        images.append(dict(key="g%d" % k, sym=k, pin_idx=[], free_idx=free_idx,
                           placements=[tuple(p) for p in Z],
                           free={"g%d_sq%d" % (k, i): tuple(Z[i]) for i in free_idx}))
    assert len(images) == 8, "k0_00: expected 8 images (G_S = D4), got %d" % len(images)

    # ---- exact witness families ----------------------------------------------------------
    crowd = json.load(open(CROWD))["classes"][name]
    src_sym = int(crowd["source"].replace("trump-sym", ""))
    assert src_sym == 0, "k0_00 crowdfam source is %s, expected trump-sym0" % crowd["source"]
    fam = [(Fr(f["cx"]), Fr(f["cy"]), t_norm(Fr(f["t"]))) for f in crowd["family"]]
    assert len(fam) == N, "crowdfam k0_00 family has %d entries, expected %d" % (len(fam), N)

    wit = {}
    for im in images:
        k = im["sym"]
        wit[im["key"]] = {"g%d_sq%d" % (k, i): exact_sym(cx, cy, t, k)
                          for i, (cx, cy, t) in enumerate(fam)}

    # ---- exact re-verification of EVERY image family -------------------------------------
    report = {}
    for im in images:
        g = im["key"]
        items = sorted(wit[g].items(), key=lambda kv: int(kv[0].split("sq")[-1]))
        sq, bad = [], []
        for (nm, (cx, cy, t)) in items:
            adm = admissible_exact((cx, cy), t, S0)
            if not adm:
                bad.append("%s not admissible at s0" % nm)
            th = 2 * math.atan(float(t))
            # cross-check the exact witness against the FLOAT image placement (the (D) target)
            fx, fy, fth = im["free"][nm]
            dev = max(abs(float(cx) - fx), abs(float(cy) - fy))
            dth = abs(math.degrees(th) % 90.0 - math.degrees(fth) % 90.0)
            dth = min(dth, 90.0 - dth)
            if dev > 1e-5 or dth > 1e-4:
                bad.append("%s exact witness deviates from the image placement "
                           "(dc %.3e, dtheta %.3e deg)" % (nm, dev, dth))
            sq.append(dict(name=nm, cx=str(cx), cy=str(cy), t=str(t),
                           cx_f=float(cx), cy_f=float(cy), t_f=float(t),
                           theta_deg=math.degrees(th), theta_rad=th,
                           admissible=bool(adm),
                           dev_from_image=dev, dtheta_from_image_deg=dth,
                           min_gap_to_pins="n/a (no pins)", min_gap_to_pins_f=None))
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
                         min_gap_to_pins="n/a (no pins)", min_gap_to_pins_f=None,
                         source=("crowdfam %s" % crowd["source"] if im["sym"] == src_sym
                                 else "exact D4 image (sym%d) of crowdfam %s"
                                      % (im["sym"], crowd["source"])),
                         ok=(not bad), problems=bad)
        report[g]["free"] = {nm: list(p) for nm, p in im["free"].items()}

    lemma_PD = dict(note="vacuous for k0_00: no pins, no pin drift", d_max=[], d_max_f=[],
                    T_prime=None, lambda_max=None,
                    rule="no pins => pinguard.classify can never return 'parent' or "
                         "'contradictory(slack-core|PD)'")

    C = dict(name=name, s_rat=S_RAT, s0=S0F, k_s=k_s, N=N, budget_cover=N - 1, budget_no=N,
             delta_pin=0.0, pin_halfwidth=0.0,
             pins_exact=[], SLOTS=[], PINS=[],
             pin_core_a=None, rho="n/a (no pins)", rho_f=None, A="0", A_f=0.0,
             lam=lam, s_trump=s_trump, lemma_PD=lemma_PD,
             images=[dict(key=im["key"], sym=im["sym"], pin_idx=im["pin_idx"],
                          free_idx=im["free_idx"], free=im["free"],
                          placements=[list(p) for p in im["placements"]]) for im in images],
             witnesses=report)
    C["_PINS"] = []
    C["_PIN_FULL"] = []
    C["_wit"] = wit
    return C


def witnesses_path(name=CLSNAME):
    return os.path.join(RES, "witnesses_%s.json" % name)


def write_class(name=CLSNAME, delta=DELTA_PIN):
    C = load_class(name, delta)
    wit = dict(cls=name, s_rat=S_RAT, delta_pin=0.0, pin_halfwidth=0.0,
               pin_core_a=None, rho=C["rho"], A=C["A"],
               images={g: C["witnesses"][g] for g in C["witnesses"]})
    json.dump(wit, open(witnesses_path(name), "w"), indent=1)
    out = {k: v for k, v in C.items() if not k.startswith("_") and k != "witnesses"}
    out["witness_summary"] = {g: dict(m=C["witnesses"][g]["m"],
                                      min_pairwise_gap_f=C["witnesses"][g]["min_pairwise_gap_f"],
                                      ok=C["witnesses"][g]["ok"],
                                      problems=C["witnesses"][g]["problems"],
                                      source=C["witnesses"][g]["source"])
                              for g in C["witnesses"]}
    json.dump(out, open(os.path.join(RES, "class_%s.json" % name), "w"), indent=1)
    return C, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default=CLSNAME)
    ap.add_argument("--delta", type=float, default=DELTA_PIN)
    a = ap.parse_args()
    C, out = write_class(a.cls, a.delta)
    bad = [g for g in C["witnesses"] if not C["witnesses"][g]["ok"]]
    print(json.dumps(dict(cls=a.cls, k_s=C["k_s"], N=C["N"], delta_pin=C["delta_pin"],
                          images=[im["key"] for im in C["images"]],
                          syms=[im["sym"] for im in C["images"]],
                          witness_summary=out["witness_summary"]), indent=1))
    if bad:
        print("STOP: exact witness verification FAILED for %s" % bad)
        sys.exit(3)
    print("wrote %s" % witnesses_path(a.cls))


if __name__ == "__main__":
    main()
