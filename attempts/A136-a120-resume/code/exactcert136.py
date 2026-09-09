"""A136 -- A170's EXACT cores applied to this attempt's own cert-FAIL / cert-CAP NO children.

WHY THIS EXISTS.  A170 audited every certificate on disk and classified this attempt's lane:
`attempts/A170-certfix/results/scan170.json` has **122 A136 certificates, all `kind: "stock"`,
`exact_lane: false`**, with the exact core up to **1.0787x** the carried one -- and A170 then
re-certified **none of them** (no A136 row appears in any `recert170_*.jsonl`).  A136's certifier
goes through `caselp.make_certificate` directly, which is exactly the path A170 found reverts the
cores, so every A136 certificate exempts a strictly smaller core than A135's exact vertex test
licenses.

That matters here because of WHERE this attempt's remaining survivors are.  Of 72 ALIVE NO children,
**56 are LP-alive** -- the LP itself found no kill, and no certifier budget touches those -- but
**16 are alive only because the CERTIFICATE did not land** (14 CAP, 2 FAIL) while the LP had already
converged to a real margin (`eta` from -0.116 to -0.444).  **Six of those sixteen are the ONLY alive
child of their node**, i.e. six nodes are one certificate away from CLOSED, and one of the six is
`k5_16_interior_Y0941`, which carries an ALIVE `docs/shadows` page.

WHAT IS DONE, AND WHY IT IS SOUND.  A170's `certwrap170.carry_exact_cores` is IMPORTED UNCHANGED and
applied to the certificate ALREADY ON DISK; no LP is re-solved and no certificate is re-emitted.
Its two guards are what make this safe over a stock-core certificate (A170's own docstring):

  * a core is only ever **ENLARGED** (`a_new` is installed only when `a_exact > a_carried`);
  * the substitution is refused unless A135's `exact_a` reports `cert_ok` and `(kx, ky, tm)` are
    unchanged, so the core stays the same square, only wider.

Enlarging a *certified* core can only REMOVE verification obligations, so it can turn FAIL into PASS
and never the reverse, and the FROZEN `verify_case.py` (sha `521cb01f...`, asserted byte-identical
before every run) validates whatever cores the certificate carries.  The patched copy is written to
a NEW file under `certs_exact/`; **the original certificate is never overwritten**.

The NO zone and `nofam_boxes` are untouched, so A136's F-COVER property survives verbatim; this
script re-checks `ZONE subset BOX` on the written rationals of the patched file anyway and refuses
to verify a file that fails it.

    python exactcert136.py                 # verify the candidates, write results/exactcert136.jsonl
    python exactcert136.py --adopt         # + promote every PASS to DEAD-CERT and re-status its node

READ-ONLY on every other attempt (A170's wrapper, A135's exactcore, A132's vertex test and the
frozen verifier are all imported).  PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import argparse, glob, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A6                                               # noqa: E402

sys.path.insert(0, os.path.join(A6.ROOT, "attempts", "A170-certfix", "code"))
import certwrap170 as W                                            # noqa: E402  READ-ONLY (A170)

OUT = os.path.join(A6.RES, "exactcert136.jsonl")
CERTX = os.path.join(A6.BASE, "certs_exact")
CERTDIR = {"": "certs", "_asym": "certs_asym", "_a160": "certs_a160", "_a163": "certs_a163"}


def candidates():
    """Every ALIVE NO child whose LP found a margin but whose certificate did not land.

    Sorted so that a node with ONE alive child -- one certificate from CLOSED -- comes first.
    """
    out = []
    for nd in [A6.NODES] + sorted(glob.glob(os.path.join(A6.RES, "nodes_*"))):
        if not os.path.isdir(nd):
            continue
        suf = os.path.basename(nd)[len("nodes"):]
        cd = os.path.join(A6.BASE, CERTDIR.get(suf, "certs" + suf))
        for rp in sorted(glob.glob(os.path.join(nd, "rec__*.json"))):
            rec = A6.jload(rp)
            if rec.get("status") == "CLOSED":
                continue
            st = rec.get("child_status") or []
            n_alive = sum(1 for s in st if s == "ALIVE")
            for ck, ch in sorted((rec.get("children") or {}).items()):
                if ch.get("status") != "ALIVE":
                    continue
                c = ch.get("cert")
                res = c.get("result") if isinstance(c, dict) else c
                if res not in ("FAIL", "CAP"):
                    continue                                        # LP-alive: no certifier helps
                tag = ch.get("cert_tag") or "%s_a136%s__a116N__%s" % (
                    rec["id"], suf.replace("_", ""), ck)
                p = os.path.join(cd, tag + ".json")
                if not os.path.exists(p):
                    cand = glob.glob(os.path.join(cd, "%s_*__%s.json" % (rec["id"], ck)))
                    cand = [q for q in cand if not q.endswith((".report.json", ".certify.json"))]
                    p = cand[0] if cand else None
                lp = ch.get("lp") or {}
                out.append(dict(node=rec["id"], rec=rp, suf=suf or "(base)", child=ck,
                                was=res, n_alive_in_node=n_alive, cert=p,
                                eta=lp.get("eta"), tau=lp.get("tau"),
                                converged=lp.get("converged")))
    out.sort(key=lambda d: (d["n_alive_in_node"], d["node"], d["child"]))
    return out


def zone_sub_box(cert):
    """Re-check A136's F-COVER property on the WRITTEN rationals of the patched file, with
    a136lib's OWN decidable predicate -- the same one `narrow` raised on at emission."""
    h = cert.get("hypotheses") or {}
    zs, bs = h.get("nofams") or [], h.get("nofam_boxes") or []
    if not zs or not bs:
        return dict(ok=None, why="certificate carries no nofams/nofam_boxes")
    from fractions import Fraction as Fr

    def rat(d):
        # the file stores every bound as a decimal string; a136lib's predicate compares NUMBERS
        return dict(x0=Fr(d["x0"]), x1=Fr(d["x1"]), y0=Fr(d["y0"]), y1=Fr(d["y1"]),
                    t_intervals=[[Fr(a), Fr(b)] for a, b in (d.get("t_intervals") or [])])

    bad = []
    for i, (z, b) in enumerate(zip(zs, bs)):
        err = A6.zone_sub_box(rat(z), rat(b))
        if err:
            bad.append("%d: %s" % (i, err))
    return dict(ok=not bad, errors=bad[:6], n=len(zs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adopt", action="store_true")
    ap.add_argument("--only_one_away", action="store_true",
                    help="only children that are the sole survivor of their node")
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--timeout", type=float, default=1800.0)
    ap.add_argument("--wall", type=float, default=9000.0)
    ap.add_argument("--out_tag", default="",
                    help="suffix on results/exactcert136<tag>.jsonl -- a SECOND pass over the same "
                         "certificates at a different --depth is a different experiment and gets "
                         "its own ledger and its own dedupe set")
    ap.add_argument("--only", default="",
                    help="comma-separated node ids to restrict to")
    a = ap.parse_args()
    global OUT
    OUT = os.path.join(A6.RES, "exactcert136%s.jsonl" % a.out_tag)

    log = A6.mklog("exactcert136%s.log" % a.out_tag)
    log("frozen verify_case.py asserted: %s" % W.assert_frozen()[:16])
    os.makedirs(CERTX, exist_ok=True)
    cands = candidates()
    if a.only_one_away:
        cands = [c for c in cands if c["n_alive_in_node"] == 1]
    if a.only:
        want = {x.strip() for x in a.only.split(",") if x.strip()}
        cands = [c for c in cands if c["node"] in want]
    log("candidates %d (%d of them the SOLE survivor of their node)"
        % (len(cands), sum(1 for c in cands if c["n_alive_in_node"] == 1)))

    done = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["id"])
                except Exception:
                    pass
    rows, t_start = [], time.time()
    for c in cands:
        key = "%s%s/%s" % (c["node"], c["suf"], c["child"])
        if key in done:
            continue
        if time.time() - t_start > a.wall:
            log("wall reached -- stopping between certificates")
            break
        if not c["cert"] or not os.path.exists(c["cert"]):
            rec = dict(c, id=key, result="NO-CERT-FILE")
            rows.append(rec)
            log("%-44s NO CERTIFICATE FILE ON DISK" % key)
            continue
        t0 = time.time()
        cert = A6.jload(c["cert"])
        if cert.get("format") != "case-measure-certificate-v1":
            rows.append(dict(c, id=key, result="WRONG-FORMAT", format=cert.get("format")))
            continue
        rep = W.carry_exact_cores(cert)                              # ENLARGE ONLY (A170 guards)
        n_app = sum(1 for r in rep if r.get("applied"))
        mx = max([r.get("ratio") or 1.0 for r in rep] or [1.0])
        base = dict(c, id=key, n_applied=n_app, max_ratio=mx, cores=rep,
                    cert_src=os.path.relpath(c["cert"], A6.ROOT).replace("\\", "/"))
        if n_app == 0:
            rows.append(dict(base, result="NO-CHANGE",
                             why="every carried core is already at least the exact core"))
            log("%-44s NO-CHANGE (cores already exact)" % key)
            continue
        zb = zone_sub_box(cert)
        if zb.get("ok") is False:
            rows.append(dict(base, result="REFUSED-ZONE", zone_sub_box=zb))
            log("%-44s REFUSED: ZONE not inside BOX after patch: %s" % (key, zb["errors"]))
            continue
        p = os.path.join(CERTX, os.path.basename(c["cert"])[:-5] + "__exact.json")
        base["depth"] = a.depth
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=0)
        rc, txt = W.run_frozen_verifier(p, jobs=a.jobs, depth=a.depth, timeout=a.timeout)
        tail = W.verifier_tail(txt)
        result = "PASS" if rc == 0 else ("TIMEOUT" if rc is None else "FAIL")
        rows.append(dict(base, result=result, rc=rc, zone_sub_box=zb,
                         seconds=round(time.time() - t0, 1),
                         cert=os.path.relpath(p, A6.ROOT).replace("\\", "/"),
                         verifier=dict(file="A143-corner-first-k0/code/verify_case.py",
                                       sha256=W.FROZEN_SHA, depth=a.depth, jobs=a.jobs),
                         verifier_tail=tail[:3]))
        log("%-44s %-4s -> %-7s  cores x%d (max %.4f)  %.0f s  | %s"
            % (key, c["was"], result, n_app, mx, time.time() - t0,
               (tail[-1][:70] if tail else "")))
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(rows[-1]) + "\n")

    npass = sum(1 for r in rows if r["result"] == "PASS")
    log("done: %d verified, %d PASS" % (len(rows), npass))

    if a.adopt:
        # adopt from the LEDGER, not from this run's rows: a resumed run skips what is already
        # verified, and a PASS must still be promoted (A136, 2026-09-09)
        led = []
        if os.path.exists(OUT):
            with open(OUT, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        led.append(json.loads(line))
        n = 0
        for r in led:
            if r["result"] != "PASS":
                continue
            rec = A6.jload(r["rec"])
            ch = rec["children"][r["child"]]
            ch["status"] = "DEAD-CERT"
            ch["cert"] = dict(result="PASS", file=r["cert"], seconds=r.get("seconds"),
                              rounds=None, source="A136 exactcert136.py",
                              note="the ALREADY-EMITTED certificate with A135's EXACT cores carried "
                                   "through by A170's certwrap170.carry_exact_cores (cores ENLARGED "
                                   "only, %d of %d, max ratio %.4f), re-run under the FROZEN "
                                   "verify_case.py.  No LP was re-solved and the original "
                                   "certificate %s is unchanged on disk.  Previous verdict: %s."
                                   % (r["n_applied"], len(r["cores"]), r["max_ratio"],
                                      r["cert_src"], r["was"]))
            ch["cert_exactcore"] = dict(applied=r["n_applied"], max_ratio=r["max_ratio"],
                                        was=r["was"], report=r["cores"])
            st = [rec["children"].get("NO%d" % i, {}).get("status")
                  for i in range(len(rec.get("boxes_used") or []))]
            rec["child_status"] = st
            rec["open_children"] = [i for i, s in enumerate(st) if s != "DEAD-CERT"]
            if st and all(s == "DEAD-CERT" for s in st):
                rec["status"] = "CLOSED"
            A6.jdump(r["rec"], rec)
            n += 1
            log("adopted %s -> node %s now %s" % (r["id"], rec["id"], rec["status"]))
        log("adopted %d PASSes" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
