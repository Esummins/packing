"""A206 auditor's list: every DEAD leaf of every run row in results/namedsplit206.jsonl not yet in scratch/audit_done.txt
-> lines "<nid> <run key> <leaf label>" (the leaves come from the certificate's node records)."""
import json, os, sys
sys.stdout.reconfigure(newline=chr(10))                              # no CR on Windows pipes (the labels are read by bash)
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "namedsplit206.jsonl")
DONE = os.path.join(HERE, "audit_done.txt")
done = set(l.strip() for l in open(DONE, encoding="utf-8")) if os.path.exists(DONE) else set()
out, seen = [], set()
for l in open(RES, encoding="utf-8") if os.path.exists(RES) else []:
    try:
        d = json.loads(l)
    except Exception:
        continue
    if not d.get("run") or d.get("killed"):
        continue
    cert = os.path.join(HERE, "..", "certs", "namedsplit206_%s.json" % d["nid"])
    if not os.path.exists(cert):
        continue
    run = (json.load(open(cert, encoding="utf-8")).get("runs") or {}).get(d["run"]) or {}
    for n in run.get("nodes") or []:
        if n.get("verdict") == "DEAD" and n.get("snapshot"):
            key = "%s %s %s" % (d["nid"], d["run"], n["label"])
            if key not in done and key not in seen:
                seen.add(key)
                out.append(key)
print("\n".join(out))
