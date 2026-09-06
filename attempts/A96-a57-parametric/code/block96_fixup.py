"""Re-certify block96 nodelp rows that failed only because A57 certify.py's auto scale
(--scale 0) divides by tau, and a block-first node can have tau = 0 exactly.  Rewrites the row."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import block96 as B  # noqa: E402

P = os.path.join(B.RES, "block96_nodelp.jsonl")
rows = [json.loads(l) for l in open(P)]
n = 0
for r in rows:
    if str(r.get("cert", "")).startswith("FAIL") and (r.get("tau") == 0.0) and not r.get("cert_tail"):
        np_ = os.path.join(B.NODES, r["tag"] + ".json")
        if not os.path.exists(np_):
            continue
        co = os.path.join(B.CERTS, r["tag"] + ".json")
        rc, secs, out = B.certify(np_, co, tau=0.0)
        r["cert"] = "PASS" if rc == 0 else "FAIL(rc=%d)" % rc
        r["cert_seconds"] = secs
        r["cert_path"] = co if rc == 0 else None
        r["refixed"] = True
        n += 1
with open(P, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(json.dumps(dict(refixed=n)))
