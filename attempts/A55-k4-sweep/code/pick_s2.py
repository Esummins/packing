"""A55: pick the nodes that earned an s2 escalation pass -- s1 certification reached the
verifier and failed on holes (rc=1), i.e. the scale headroom exists and only the field is
short.  rc=3 (auto-scale total >= budget) and the never-certified canaries are excluded."""
import json, os, sys, glob
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 and sys.argv[1] else None
out = []
for p in sorted(glob.glob(os.path.join(BASE, "results", "k4_*_s1.json"))):
    d = json.load(open(p))
    n = d["name"]
    if only and n not in only:
        continue
    if os.path.exists(os.path.join(BASE, "results", f"{n}_s2.json")):
        continue
    if str(d.get("cert", "")).startswith("FAIL(rc=1)"):
        out.append(n)
print(",".join(out))
