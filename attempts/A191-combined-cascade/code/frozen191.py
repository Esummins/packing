"""A191 -- re-run the FROZEN v1 verifier (A143 verify_case.py, sha asserted = lp168.VERIFIER_SHA) on a v1-style kill
certificate: the frozen loader reads cores (kx, ky, tm, a), budget = n - #cores and the atoms, and ignores the v5
fields (pbox, guardlines, format), so a certificate with NO active guard line is a v1 certificate verbatim.
A PASS is [C] under the frozen chain, conditional on the cascade node's hypothesis (the roles' squares have poses in
the recorded pieces, hence contain A135's exact cores of their union boxes [T]).  Gated on the box ceiling.

    python frozen191.py CERT.json [CERT.json ...]
"""
import hashlib, os, subprocess, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prio191                                                   # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "..", "A168-cascade-fable", "code"))
import lp168 as L                                                # noqa: E402
assert hashlib.sha256(open(L.VERIFIER, "rb").read()).hexdigest() == L.VERIFIER_SHA, "frozen verifier sha mismatch"
for cert in sys.argv[1:]:
    prio191.wait_box(own=1, max_wait=1500)
    t0 = time.time()
    cmd = [sys.executable, L.VERIFIER, cert, "--jobs", "1", "--depth", "56", "--max-witnesses", "16", "--report", cert.replace(".json", ".frozen.report.json"), "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1500, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    tail = [l for l in p.stdout.splitlines() if l.startswith(("PASS", "FAIL", "MALFORMED"))]
    rec = dict(cert=cert, rc=p.returncode, verifier=L.VERIFIER, verifier_sha=L.VERIFIER_SHA, result=("PASS" if p.returncode == 0 else "FAIL(rc %d)" % p.returncode),
               tail=tail[:4], stderr=p.stderr[-400:], secs=round(time.time() - t0, 1), when=time.strftime("%Y-%m-%d %H:%M"))
    json.dump(rec, open(cert.replace(".json", ".frozen.certify.json"), "w"), indent=1)
    print(json.dumps(rec)[:600], flush=True)
