"""A209 -- the DEAD leaves not yet audited: '<nid> <run key> <leaf>' per line (inherited and stage-0 kills excluded)."""
import glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
done = set(l.strip() for l in open(os.path.join(HERE, "audit_done.txt"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "audit_done.txt")) else set()
for f in sorted(glob.glob(os.path.join(HERE, "..", "certs", "k5killer209_*.json"))):
    try:
        c = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    for key, d in (c.get("runs") or {}).items():
        if d.get("verdict") not in ("DEAD", "ALIVE"):
            continue
        for n in d.get("nodes") or []:
            if n.get("verdict") == "DEAD" and n.get("kind") != "inherited" and n.get("clip"):
                line = "%s %s %s" % (c["nid"], key, n["label"])
                if line not in done:
                    print(line)
