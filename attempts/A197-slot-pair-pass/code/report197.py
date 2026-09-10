"""A197 report: the kill table of results/slotpair197.jsonl."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JL = os.path.abspath(os.path.join(HERE, "..", "results", "slotpair197.jsonl"))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else JL
    last = {}
    for l in open(path, encoding="utf-8"):
        if l.strip():
            d = json.loads(l)
            last[d["nid"]] = d
    dead = [d for d in last.values() if d.get("verdict") == "DEAD"]
    alive = [d for d in last.values() if d.get("verdict") == "ALIVE"]
    err = [d for d in last.values() if d.get("verdict") not in ("DEAD", "ALIVE")]
    print("rows %d  DEAD %d  ALIVE %d  ERROR %d" % (len(last), len(dead), len(alive), len(err)))
    by = {}
    for d in last.values():
        by.setdefault(d.get("cls"), [0, 0])
        by[d["cls"]][0 if d.get("verdict") == "DEAD" else 1] += 1
    print("by class:", {k: "dead %d / alive %d" % tuple(v) for k, v in sorted(by.items())})
    if dead:
        print("\nKILLS")
        for d in sorted(dead, key=lambda z: z["nid"]):
            print("  %-28s %-7s %-9s %s  (%.0f s)" % (d["nid"], d.get("cls"), d.get("kill_cell"),
                                                      d.get("leaf"), d.get("seconds") or 0))
    print("\nALIVE detail (cell, H-meets alive/tested, two-free alive/pairs, caps)")
    for d in sorted(alive, key=lambda z: z["nid"]):
        bits = []
        for t in (d.get("subcases") or []):
            hm = next((x for x in t["subcases"] if x.get("case") == "H-meets"), {})
            tf = next((x for x in t["subcases"] if x.get("case") == "two-free"), {})
            bits.append("%s hm %s/%s tf %s/%s%s"
                        % (t["cell"], hm.get("n_alive", "-"), hm.get("tested", hm.get("n_pairs", "-")),
                           tf.get("n_alive", "-"), tf.get("n_pairs", "-"),
                           ("*" + ",".join(t.get("caps") or []) if t.get("caps") else "")))
        print("  %-28s %-7s %s  [%s/%s cells, %.0f s]%s"
              % (d["nid"], d.get("cls"), " | ".join(bits) or "-",
                 d.get("n_cells_tested", "?"), d.get("n_cells_forced", "?"),
                 d.get("seconds") or 0, "  WALL" if d.get("timed_out") else ""))
    nw = sum(1 for d in alive for t in (d.get("subcases") or []) if t.get("witness"))
    print("\nwitnesses sampled: %d cell(s); pages hitting the wall: %d"
          % (nw, sum(1 for d in alive if d.get("timed_out"))))
    print("total CPU-s: %.0f" % sum(float(d.get("seconds") or 0) for d in last.values()))


if __name__ == "__main__":
    main()
