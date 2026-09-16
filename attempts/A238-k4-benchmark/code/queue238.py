"""A238 -- the benchmark QUEUE for a protected class, in the order that makes the comparison with A100 exact.

    python queue238.py k4_11 [--extra 40] [--out code/queue_k4_11.txt]

  1. "<cls>_root"                    the A84-P1 node (H = the whole interior zone);
  2. every LEVEL-1 cover cell A100 actually attempted by LP (its `a84_<cls>_cover_j0.jsonl` tags, level-1 only):
     the HEAD-TO-HEAD set -- the same boxes, the same hypothesis, priced two ways;
  3. the cells that hold an image square (A100's census `image_boxes`, state "unkillable"): the gate / tube evidence;
  4. `--extra N` further attemptable cells in A100's own stratified order (nearest / median / farthest by `ghost`),
     for the extrapolation.
Each line is "<nid>  # <state> <a100 verdict> <a100 lp_s + cert_s>" so the queue reads as the comparison table."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A100 = os.path.join(ROOT, "attempts", "A100-protected-pilot", "results")
sys.path.insert(0, HERE)
import load238                                                  # noqa: E402


def a100_cells(cls):
    """{i: dict(verdict, lp_s, cert_s, tau, eta)} for the LEVEL-1 cover cells A100 priced (first row per tag wins)."""
    f = os.path.join(A100, "a84_%s_cover_j0.jsonl" % cls)
    out = {}
    if not os.path.exists(f):
        return out
    for ln in open(f, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:                                         # noqa: BLE001
            continue
        t = str(r.get("tag") or "")
        if not t.startswith("c0_Y") or "_D" in t or not t[4:].isdigit():
            continue
        i = int(t[4:])
        if i in out:
            continue
        out[i] = dict(verdict=r.get("verdict"), lp_s=r.get("lp_s"), cert_s=r.get("cert_s"),
                      tau=r.get("tau"), eta=r.get("eta"), budget=r.get("budget"))
    return out


def stratified(rows, n):
    """A84/A100's `_sample_rows`: nearest / median / farthest third by ghost distance."""
    srt = sorted(rows, key=lambda r: (r["ghost"], r["i"]))
    k, m = max(1, n // 3), len(srt)
    pick, seen = [], set()
    for r in srt[:k] + srt[m // 2 - k // 2: m // 2 - k // 2 + k] + srt[-k:]:
        if r["i"] not in seen:
            seen.add(r["i"])
            pick.append(r)
    for r in srt:
        if len(pick) >= n:
            break
        if r["i"] not in seen:
            seen.add(r["i"])
            pick.append(r)
    return pick[:n]


def build(cls, extra=40):
    load238.patch_classes()
    cen = load238.census(cls)
    if cen is None:
        raise SystemExit("A238: no A100 census for %s" % cls)
    by_i = {r["i"]: r for r in cen["rows"]}
    a1 = a100_cells(cls)
    img = sorted({b[0] for v in (cen.get("image_boxes") or {}).values() for b in v})
    lines, seen = [], set()

    def add(nid, why, i=None):
        if nid in seen:
            return
        seen.add(nid)
        r, a = (by_i.get(i) or {}), (a1.get(i) or {})
        cost = "" if not a else " A100 %s %.0fs" % (str(a.get("verdict"))[:28], (a.get("lp_s") or 0) + (a.get("cert_s") or 0))
        lines.append("%-22s # %s %s%s" % (nid, why, r.get("state") or "", cost))

    add("%s_root" % cls, "A84-P1 root (interior zone)")
    for i in sorted(a1):
        add("%s_c0_Y%04d" % (cls, i), "A100 head-to-head", i)
    for i in img:
        add("%s_c0_Y%04d" % (cls, i), "holds an image square (gate/tube)", i)
    rest = [r for r in cen["rows"] if r["state"] == "attemptable" and "%s_c0_Y%04d" % (cls, r["i"]) not in seen]
    for r in stratified(rest, extra):
        add("%s_c0_Y%04d" % (cls, r["i"]), "extrapolation (stratified by ghost)", r["i"])
    return lines


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cls")
    ap.add_argument("--extra", type=int, default=40)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    lines = build(a.cls, a.extra)
    out = a.out or os.path.join(HERE, "queue_%s.txt" % a.cls)
    with open(out, "w", encoding="utf-8") as f:
        f.write("# A238 benchmark queue for %s (%d nodes): root, A100's head-to-head cells, the image cells, then the\n"
                "# stratified extrapolation set.  Run with bench238.sh; resume is by certificate presence.\n" % (a.cls, len(lines)))
        f.write("\n".join(lines) + "\n")
    print("%s: %d nodes -> %s" % (a.cls, len(lines), os.path.relpath(out, ROOT)))
