"""A152 T5 -- normalise the emitted certificates and write the SHA-256 manifest.

One normalisation: `n_pins` is recomputed as `#cond_boxes - #M_index` (the sweep's first pass
recorded it from a key that `lane_corner_generic` does not set, so it was one too large on every
certificate written before the fix; nothing else in the object, and nothing the checker consumes,
depended on it).  The certificate is then rewritten byte-for-byte the way `emit141.write_cert`
writes it and its SHA-256 recorded.

    python t5_manifest.py
"""
import glob
import hashlib
import json
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))


def main():
    rows, fixed = [], 0
    for p in sorted(glob.glob(os.path.join(BASE, "certs", "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        want = len(d["cond_boxes"]) - len(d.get("M_index") or [])
        if d.get("n_pins") != want:
            d["n_pins"] = want
            fixed += 1
        blob = json.dumps(d, indent=1, sort_keys=True)
        open(p, "w", encoding="utf-8").write(blob)
        rows.append(dict(cert=os.path.relpath(p, ROOT).replace("\\", "/"),
                         sha256=hashlib.sha256(blob.encode()).hexdigest(),
                         nid=d.get("cell"), slot=d.get("corner"), cls=d.get("cls"),
                         src=d.get("src"), level=d.get("level"),
                         translate=d.get("translate"), extension=d.get("extension"),
                         lane_ub=d.get("lane_ub"), M=d.get("M"),
                         conditional=bool(d.get("conditional")),
                         bytes=len(blob)))
    out = dict(n_certs=len(rows), n_pins_normalised=fixed,
               kind="polycore_slot_lane_shrunk_v1",
               note="every certificate is CONDITIONAL on the slack-form kill of its extension "
                    "class (notes/prereq.md); none of them is a kill today",
               certs=rows)
    p = os.path.join(BASE, "results", "cert_manifest.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("certs %d, n_pins normalised on %d, manifest %s" % (len(rows), fixed, p))


if __name__ == "__main__":
    main()
