"""Dense LOCAL row grids around verify_measure.py witness placements.

Injecting the witness placements themselves is not enough: the LP satisfies them exactly and the
deficit pocket simply moves ~1 degree / ~0.005 away (the heuristic row oracle's (0.125 deg, 0.005)
grid cannot see a pocket that narrow, so it never comes back).  Covering a whole neighbourhood of
each witness with rows removes the pocket instead of displacing it.

  python local_rows.py out.json cert1.witnesses.json [cert2.witnesses.json ...]
"""
import json, math, sys

DTH = math.radians(0.15)      # theta step
NTH = 5                       # +/- NTH steps  (+/- 1.2 deg)
DC = 0.008                    # centre step
NC = 2                        # +/- NC steps   (+/- 0.024)
CLUSTER = (1.0, 0.05)         # merge witnesses within 0.5 deg and 0.02 in centre


def main():
    out_path, files = sys.argv[1], sys.argv[2:]
    seeds = []
    for f in files:
        for w in json.load(open(f))["witnesses"]:
            p = w.get("placement")
            if not p:
                continue
            th = 2.0 * math.atan(p["t_float"])
            cx, cy = p["cx_float"], p["cy_float"]
            if any(abs(math.degrees(th - t0)) < CLUSTER[0] and abs(cx - x0) < CLUSTER[1]
                   and abs(cy - y0) < CLUSTER[1] for (t0, x0, y0) in seeds):
                continue
            seeds.append((th, cx, cy))
    rows = []
    for (th, cx, cy) in seeds:
        for i in range(-NTH, NTH + 1):
            t = th + i * DTH
            if t < 0 or t > math.pi / 2:
                continue
            for j in range(-NC, NC + 1):
                for k in range(-NC, NC + 1):
                    rows.append([cx + j * DC, cy + k * DC, t])
    json.dump(rows, open(out_path, "w"))
    print(f"{len(seeds)} witness clusters -> {len(rows)} local rows -> {out_path}")


if __name__ == "__main__":
    main()
