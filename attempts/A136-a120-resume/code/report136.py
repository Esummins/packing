"""A136 T3 -- the Lean hand-off list: one line per CLOSED node, in the shape
`LocalCompose.y0230_dead` consumes.

    python report136.py

Writes `results/closures136.jsonl` (one row per closed node) and `results/report136.json` (the
run's counts).  Also appends the changed rows to
`attempts/A96-a57-parametric/results/a120_closures.jsonl` (append-only, A120's ledger; the reader
takes the LAST row for each id).

A row is a filled-in instantiation of

```lean
theorem y0230_dead {Ls : List Box} {Ps : List Pin} {s0 : ℝ} {H : ℝ → Cfg → Prop}
    (hD : LocalDead Ls Ps s0)                       -- the local certificate for N
    (hdisj : ...)                                   -- A120's A2 (boxes pairwise pose-disjoint)
    (hsep : ...)                                    -- A120's A3 (boxes vs pins)
    (hpins : ...)                                   -- A120's A1 + A4 (the node's pins ARE N's)
    (hno : ∀ i, ... → ¬ NoneIn (Ls.get i) z) :      -- the |L| NO certificates
    ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → ¬ H s z
```

with, for `hno`, the certificate file of each NO child **and** the `ZONE ⊆ BOX` verdict on its
written rationals — the missing hypothesis of `LocalCompose.noneIn_of_clamped` that finding
F-COVER was about, now discharged at emission (`a136lib.zone_sub_box`).
"""
from __future__ import annotations

import glob, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A6                                               # noqa: E402
sys.path.insert(0, os.path.join(A6.ROOT, "attempts", "A120-no-side-runner", "code"))
import a120lib as A                                                # noqa: E402

LEDGER = os.path.join(A6.ROOT, "attempts", "A96-a57-parametric", "results", "a120_closures.jsonl")
S0_RAT = "969271/250000"
A133_TCERT = dict(id="S02_k5_11_r0.20_rho10", format="local-cert-t-v1",
                  file="attempts/A133-tan-half-emission/certs/S02_k5_11_r0.20_rho10.tcert.json.gz",
                  sha256="a8d95682490e5caeae5512d8db11f5927bb1e53725fa31cf48ce073101a9ab72",
                  dead=True, leaves=16406,
                  note="A133's t-parametrised form of A116/A119's local certificate for N; same "
                       "L, same P, same boxes, sharper than A119's")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def cert_of(ch):
    """the certificate file this attempt accepted for a DEAD-CERT child, and its verdict."""
    # `cert_fcover` -- T1's replay of an A120 certificate, or a `run136 --queue children`
    # re-emission; `cert` -- a `run136 --queue targets` emission through noside120.run_node.
    for f in ("cert_fcover", "cert"):
        c = ch.get(f) or {}
        if c.get("result") != "PASS":
            continue
        if c.get("file"):                       # T1's re-certification of an A120 certificate
            return os.path.join(A6.ROOT, c["file"]), c
        tag = c.get("tag")
        if tag:                                 # T2's own emission
            return os.path.join(A6.CERTS, tag + ".json"), c
    return None, None


def row(rec):
    nid = rec["id"]
    snd = rec.get("soundness") or {}
    ck = snd.get("checks") or {}
    Ls, hno = [], []
    ok = True
    for i, m in enumerate(rec["boxes_used"]):
        ch = rec["children"].get("NO%d" % i) or {}
        p, c = cert_of(ch)
        if ch.get("status") != "DEAD-CERT" or p is None or not os.path.exists(p):
            ok = False
            continue
        cert = A6.jload(p)
        box = (cert["hypotheses"].get("nofam_boxes") or [None])[0]
        zone = cert["hypotheses"]["nofams"][0]
        Ls.append(dict(index=i, name=m["name"], float_box=dict(
            x0=m["x0"], x1=m["x1"], y0=m["y0"], y1=m["y1"], thetas=m["thetas"]),
            written_rational=box))
        hno.append(dict(index=i, box=m["name"],
                        certificate=os.path.relpath(p, A6.ROOT), sha256=sha(p),
                        format=cert.get("format"), result="PASS",
                        seconds=c.get("seconds"), rounds=c.get("rounds"),
                        emitted_by=("A136 recert136 (replay of A120's certificate with the "
                                    "narrowed zone)" if c.get("file") else
                                    "A136 certify136 (re-emission with the F-COVER wrapper)"),
                        verifier=dict(file="attempts/A112-dual-branching/code/verify_case.py",
                                      sha256=A6.VERIFY_CASE_SHA, depth=56, jobs=1),
                        zone_written=zone, box_written=box, zone_sub_box=True,
                        lean_consumer="PackingCert.CaseI.checkCaseI_no_family",
                        lean_bridge="PackingCertMathlib/LocalCompose.lean :: noneIn_of_clamped "
                                    "(B' := BOX, B := ZONE); its hypotheses are the ZONE subset "
                                    "BOX test, decidable on Q",
                        gen_lean=("python lean/gen_case_lean.py %s --depth 56 --name %s -o "
                                  "lean/PackingCertMathlib/PackingCertMathlib/Data/%s.lean"
                                  % (os.path.relpath(p, A6.ROOT).replace(os.sep, "/"),
                                     "%s_no%d" % (nid.split("interior_")[-1].lower(), i),
                                     "%s_no%d" % (nid.split("interior_")[-1].lower(), i)))))
    if not ok:
        return None
    return dict(
        node=nid, cls=rec["cls"], level=rec.get("level"), s0=S0_RAT, s0_float=rec["s"],
        struct_op=rec["struct_op"], inv_op=rec["inv_op"], N=rec["N"],
        status="CLOSED", attempt="A136",
        lean=dict(theorem="PackingCert.S11.LocalCert.y0230_dead",
                  file="lean/PackingCertMathlib/PackingCertMathlib/LocalCompose.lean",
                  step="node_dead_of_yes_no (the only reasoning step)",
                  conclusion="forall s <= s0 and every CfgPacking s z, not H s z, with H the A57 "
                             "node hypothesis of %s" % nid),
        hD=dict(slot="hD : LocalDead Ls Ps s0", N=rec["N"], certificate=A133_TCERT,
                boxes_source="attempts/A119-local-cert-lean/results/N_boxes.json",
                obligations=["CertCover for LocalCertS02.localDead_s02 (A126 T1, pre-existing)",
                             "LocalDead antitonicity in the box list: the written Ls are the "
                             "mapped A119 boxes rounded INWARD, so a subset; Box.mem "
                             "monotonicity, one intro/exact"]),
        Ls=Ls,
        Ps=[dict(name=p["name"], alpha=p["alpha"], beta=p["beta"], halfwidth=p["halfwidth"],
                 theta_deg=0.0) for p in rec["pins_used"]],
        hdisj=dict(slot="hdisj (A120 A2)", ok=(ck.get("A2_boxes_pose_disjoint") or {}).get("ok"),
                   test="octagon.boxes_pose_disjoint, tilt mod 90; decidable on Q in Lean"),
        hsep=dict(slot="hsep (A120 A3)", ok=(ck.get("A3_boxes_vs_pins") or {}).get("ok"),
                  test="pose-disjoint from every pin box and pinguard.classify != 'parent'"),
        hpins=dict(slot="hpins (A120 A1 + A4)",
                   a1=(ck.get("A1_pins_match") or {}).get("ok"),
                   a4=(ck.get("A4_map_invertible") or {}).get("ok"),
                   max_roundtrip_error=(ck.get("A4_map_invertible") or {})
                   .get("max_abs_roundtrip_error"),
                   note="the node's five pin boxes ARE N's pins carried into the node frame by "
                        "the D4 map, which is exactly invertible"),
        hno=hno,
        fcover=dict(fixed=True, check="a136lib.zone_sub_box on the written rationals",
                    note=A6.FCOVER_TAG),
        obligations_remaining=[
            "checkCaseI_no_family speaks of IsStrictFamily (pairwise disjoint CLOSED squares) "
            "while CfgPacking gives interior-disjointness: Dilation.lean Lemma B first "
            "(pre-existing)",
            "each NO certificate still has to be replayed in Lean (gen_case_lean.py + "
            "native_decide, the A78 route)",
            "the closure is s0-only: verify_case.py is a fixed-side verifier and A116's N is "
            "anchored at s0 (window re-verification would need A117's verify_param_v2)"],
        claim=rec.get("claim"), generated=time.strftime("%Y-%m-%d %H:%M:%S"))


def leanfrag(cert_rel, name, log):
    """Run `lean/gen_case_lean.py` on an accepted certificate, into THIS attempt's results/ (the
    `lean/` tree is read-only here).  The fragment is what `native_decide` replays; producing it
    here is what makes the closure 'a Lean replay away'."""
    import subprocess
    out = os.path.join(A6.RES, "leanfrags", name + ".leanfrag")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        return os.path.relpath(out, A6.ROOT)
    cmd = [sys.executable, os.path.join(A6.ROOT, "lean", "gen_case_lean.py"),
           os.path.join(A6.ROOT, cert_rel), "--depth", "56", "--name", name, "-o", out]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        log("  gen_case_lean FAILED for %s: %s" % (name, (p.stdout + p.stderr)[-300:]))
        return None
    return os.path.relpath(out, A6.ROOT)


def main():
    log = A6.mklog("report136.log")
    recs = [A6.jload(p) for p in sorted(glob.glob(os.path.join(A6.NODES, "rec__*.json")))]
    rows, closed, other = [], [], []
    for r in recs:
        if r.get("status") == "CLOSED":
            x = row(r)
            if x:
                for h in x["hno"]:
                    nm = "%s_no%d_fcover" % (x["node"].split("interior_")[-1].lower(), h["index"])
                    h["lean_fragment"] = leanfrag(h["certificate"], nm, log)
                rows.append(x)
                closed.append(r["id"])
            else:
                other.append((r["id"], "CLOSED but a certificate file is missing"))
        else:
            other.append((r["id"], r.get("status")))
    out = os.path.join(A6.RES, "closures136.jsonl")
    with open(out + ".tmp", "w", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(x) + "\n")
    os.replace(out + ".tmp", out)
    log("closures136.jsonl: %d CLOSED nodes -> %s" % (len(rows), out))

    # A120's ledger, APPEND ONLY (the reader takes the last row for each id)
    if rows and "--no_ledger" not in sys.argv:
        with open(LEDGER, "a", encoding="utf-8") as f:
            for x in rows:
                f.write(json.dumps(dict(
                    id=x["node"], cls=x["cls"], level=x["level"], status="CLOSED",
                    attempt="A136", rev=3, s0=x["s0"], N=x["N"],
                    yes="local certificate %s (A133 t-form %s)" % (x["N"],
                                                                   A133_TCERT["sha256"][:12]),
                    no=[h["certificate"] for h in x["hno"]],
                    zone_sub_box=True, fcover="fixed (A136)",
                    note="s0-only; supersedes A120's row for this id",
                    generated=x["generated"])) + "\n")
        log("appended %d rows to %s" % (len(rows), LEDGER))

    summary = dict(generated=time.strftime("%Y-%m-%d %H:%M:%S"), attempt="A136",
                   closed=closed, n_closed=len(closed), other=other, n_records=len(recs))
    A6.jdump(os.path.join(A6.RES, "report136.json"), summary)
    log("records %d, CLOSED %d: %s" % (len(recs), len(closed), closed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
