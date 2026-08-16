#!/usr/bin/env python3
"""
gen_cert_lean.py -- convert a packing certificate JSON into Lean source
(lean/PackingCert/PackingCert/Data.lean) for the PackingCert checker.

Usage
-----
    python lean/gen_cert_lean.py certs/trump11_certificate_int.json \
        [-o lean/PackingCert/PackingCert/Data.lean] [--name trump11] [--no-lean-check]

Accepted JSON shapes (the script is deliberately forgiving because the
certificate is produced by another agent; see certs/ for the real files):

  * common denominator:  "denominator" | "denom" | "D"                (int)
    (optional if every square carries explicit rational corners; then the
     script computes the lcm itself)
  * container side:      "container_side" | "side" | "s" | "s_c" | "container"
        given as  "3877084/1000000"  |  3877084  (int, then den = 1)
               |  {"num": .., "den": ..}  |  [num, den]  |  {"int": S}  (S/D)
        A float is REJECTED (not exact).
  * squares:             "squares"  -- a list; each entry is one of
        - a list of 4 points  [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]         (ints over D,
              or "p/q" strings / {"num","den"} rationals)
        - {"corners": [...4 points...]}                                (same)
        - {"center"|"centre": [cx, cy], "t"|"tan_half": t}             (rationals; corners
              are computed exactly: cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2))
          an optional per-square "theta_tan_half" or a top-level shared "t" is
          also honoured.

The output is a Lean file defining `PackingCert.Data.<name> : Cert` with all
coordinates as integers over one common denominator, corners in
counter-clockwise order (the Lean checker also accepts clockwise).

The script performs the same checks as the Lean checker in exact Fraction
arithmetic first (unit-square shape, strict containment, pairwise SAT) and
refuses to write a Lean file for an invalid certificate unless --force is given,
so that a failing `lake build` always means "Lean disagrees", never "bad input".
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path


# ----------------------------------------------------------------------------- parsing helpers

def to_frac(v) -> Fraction:
    if isinstance(v, bool):
        raise ValueError("boolean is not a number")
    if isinstance(v, int):
        return Fraction(v)
    if isinstance(v, float):
        raise ValueError(f"float {v!r} in certificate: refuse (not exact). Use ints or 'p/q' strings.")
    if isinstance(v, str):
        return Fraction(v.strip())
    if isinstance(v, dict) and "num" in v and "den" in v:
        return Fraction(int(v["num"]), int(v["den"]))
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, int) for x in v):
        return Fraction(v[0], v[1])
    raise ValueError(f"cannot parse rational from {v!r}")


def first_key(d: dict, keys, default=None):
    for k in keys:
        if k in d:
            return d[k]
    return default


def parse_side(cert: dict, D: int | None) -> Fraction:
    v = first_key(cert, ["container_side", "side", "s", "s_c", "container", "container_side_int"])
    if v is None:
        raise ValueError("no container side found (keys tried: container_side, side, s, s_c, container)")
    if isinstance(v, dict) and "int" in v:
        if D is None:
            raise ValueError("container {'int': S} needs a denominator")
        return Fraction(int(v["int"]), D)
    if isinstance(v, dict) and ("num" not in v) and "value" in v:
        v = v["value"]
    return to_frac(v)


def parse_point(p, D: int | None) -> tuple[Fraction, Fraction]:
    if isinstance(p, dict):
        p = [first_key(p, ["x"]), first_key(p, ["y"])]
    if not (isinstance(p, (list, tuple)) and len(p) == 2):
        raise ValueError(f"point must be [x, y], got {p!r}")
    x, y = p
    # ints with a certificate-wide denominator mean x/D
    if D is not None and isinstance(x, int) and isinstance(y, int):
        return Fraction(x, D), Fraction(y, D)
    return to_frac(x), to_frac(y)


def corners_from_center(cx: Fraction, cy: Fraction, t: Fraction):
    """Exact corners of the unit square centred at (cx,cy) rotated by theta, tan(theta/2) = t.
    Counter-clockwise order starting from the corner at (-1/2,-1/2) in body frame."""
    den = 1 + t * t
    c = (1 - t * t) / den
    s = (2 * t) / den
    h = Fraction(1, 2)
    body = [(-h, -h), (h, -h), (h, h), (-h, h)]
    return [(cx + c * bx - s * by, cy + s * bx + c * by) for bx, by in body]


def parse_square(sq, D: int | None, shared_t):
    if isinstance(sq, dict):
        if "corners" in sq:
            pts = [parse_point(p, D) for p in sq["corners"]]
        else:
            ctr = first_key(sq, ["center", "centre", "c"])
            t = first_key(sq, ["t", "tan_half", "theta_tan_half", "tan_half_theta"], shared_t)
            if ctr is None or t is None:
                raise ValueError(f"square {sq!r}: need 'corners' or 'center'+'t'")
            cx, cy = parse_point(ctr, None) if not (D is not None and all(isinstance(v, int) for v in ctr)) \
                else parse_point(ctr, D)
            pts = corners_from_center(cx, cy, to_frac(t))
    elif isinstance(sq, (list, tuple)) and len(sq) == 4:
        pts = [parse_point(p, D) for p in sq]
    else:
        raise ValueError(f"cannot parse square {sq!r}")
    if len(pts) != 4:
        raise ValueError("square needs exactly 4 corners")
    return pts


def load_certificate(path: Path):
    cert = json.loads(path.read_text(encoding="utf-8"))
    D_raw = first_key(cert, ["denominator", "denom", "D", "common_denominator"])
    D = int(D_raw) if D_raw is not None else None
    if D is not None and D <= 0:
        raise ValueError("denominator must be positive")
    shared_t = first_key(cert, ["t", "tan_half", "theta_tan_half"])
    side = parse_side(cert, D)
    sq_raw = first_key(cert, ["squares", "packing", "placements"])
    if sq_raw is None:
        raise ValueError("no 'squares' list")
    squares = [parse_square(sq, D, shared_t) for sq in sq_raw]
    return side, squares, cert


# ----------------------------------------------------------------------------- exact checks (mirror of Checker.lean)

def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def perp(a): return (-a[1], a[0])


def orient_ccw(pts):
    """Return corners in CCW order (reverse if clockwise). Does not validate shape."""
    e = sub(pts[1], pts[0])
    n = perp(e)
    if pts[2] == add(pts[1], n) and pts[3] == add(pts[0], n):
        return pts
    if pts[2] == sub(pts[1], n) and pts[3] == sub(pts[0], n):
        return [pts[0], pts[3], pts[2], pts[1]]
    return pts  # invalid shape; caught by is_unit_square


def is_unit_square(pts):
    e = sub(pts[1], pts[0]); n = perp(e)
    return dot(e, e) == 1 and pts[2] == add(pts[1], n) and pts[3] == add(pts[0], n)


def inside(pts, side):
    return all(0 < x < side and 0 < y < side for x, y in pts)


def edges(pts):
    return [sub(pts[(i + 1) % 4], pts[i]) for i in range(4)]


def sep_margin(A, B):
    """Return (axis, margin) of the best strictly separating edge axis, or None. Margin is a true
    Euclidean distance (axis normalised by its length) -- for reporting only."""
    best = None
    for n in edges(A) + edges(B):
        pa = [dot(a, n) for a in A]; pb = [dot(b, n) for b in B]
        gap = max(min(pb) - max(pa), min(pa) - max(pb))
        if gap > 0:
            L = math.sqrt(float(dot(n, n)))
            m = float(gap) / L
            if best is None or m > best[1]:
                best = (n, m)
    return best


def check_python(side, squares):
    problems = []
    for i, sq in enumerate(squares):
        if not is_unit_square(sq):
            problems.append(f"square {i}: not a unit square (CCW corners expected)")
        if not inside(sq, side):
            problems.append(f"square {i}: corner not strictly inside (0,{side})^2")
    min_gap = None
    for i, j in combinations(range(len(squares)), 2):
        r = sep_margin(squares[i], squares[j])
        if r is None:
            problems.append(f"pair ({i},{j}): no strictly separating edge axis")
        else:
            min_gap = r[1] if min_gap is None else min(min_gap, r[1])
    wall = min(min(min(x, y, side - x, side - y) for x, y in sq) for sq in squares) if squares else None
    return problems, min_gap, wall


# ----------------------------------------------------------------------------- Lean emission

def lcm(a, b): return a * b // math.gcd(a, b)


def emit_lean(name, side: Fraction, squares, src: str, extra_comment: str = ""):
    D = 1
    for sq in squares:
        for x, y in sq:
            D = lcm(D, x.denominator); D = lcm(D, y.denominator)
    lines = []
    lines.append("import PackingCert.Checker")
    lines.append("")
    lines.append("/-!")
    lines.append(f"# Certificate data: `{name}`")
    lines.append("")
    lines.append("AUTO-GENERATED by lean/gen_cert_lean.py -- do not edit by hand.")
    lines.append(f"Source: {src}")
    lines.append(f"Common denominator D = {D}")
    lines.append(f"Container side = {side.numerator}/{side.denominator}")
    lines.append(f"Number of squares = {len(squares)}")
    if extra_comment:
        lines.append(extra_comment)
    lines.append("-/")
    lines.append("")
    lines.append("namespace PackingCert.Data")
    lines.append("")
    lines.append(f"def {name} : Cert :=")
    lines.append(f"  {{ denom := {D}")
    lines.append(f"    sideNum := {side.numerator}")
    lines.append(f"    sideDen := {side.denominator}")
    lines.append("    squares :=")
    body = []
    for sq in squares:
        pts = ", ".join(f"⟨{int(x * D)}, {int(y * D)}⟩" for x, y in sq)
        body.append(f"        ⟨{pts}⟩")
    lines.append("      [ " + (",\n".join(body)).lstrip() + " ] }")
    lines.append("")
    lines.append("end PackingCert.Data")
    lines.append("")
    return "\n".join(lines), D


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json", type=Path)
    ap.add_argument("-o", "--out", type=Path,
                    default=Path(__file__).resolve().parent / "PackingCert" / "PackingCert" / "Data.lean")
    ap.add_argument("--name", default="trump11", help="Lean identifier for the certificate")
    ap.add_argument("--force", action="store_true", help="write Lean even if the Python pre-check fails")
    args = ap.parse_args(argv)

    side, squares, raw = load_certificate(args.json)
    squares = [orient_ccw(sq) for sq in squares]
    problems, min_gap, wall = check_python(side, squares)
    print(f"[gen_cert_lean] {args.json}: {len(squares)} squares, container side {side} "
          f"(= {float(side):.9f})")
    if min_gap is not None:
        print(f"[gen_cert_lean] min pairwise SAT margin ~ {min_gap:.3e}, min wall margin ~ {float(wall):.3e}")
    if problems:
        print("[gen_cert_lean] Python pre-check FAILED:")
        for p in problems:
            print("   ", p)
        if not args.force:
            print("[gen_cert_lean] not writing Lean file (use --force to override)")
            return 1
    else:
        print("[gen_cert_lean] Python pre-check passed (exact Fraction arithmetic)")
    src = str(args.json).replace("\\", "/")
    text, D = emit_lean(args.name, side, squares, src)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"[gen_cert_lean] wrote {args.out}  (D = {D}, {D.bit_length()} bits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
