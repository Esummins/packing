"""
A60 crash-integrity sweep.

The machine hard-crashed (Kernel-Power 41, no dump) with A60 mid-write.  Three artefact classes
can be left torn, and they fail in very different ways:

  * `results/*.jsonl`   -- a torn LAST line.  Benign-ish: `Sink` skips unparseable lines, so the
    child is simply re-run.  But the torn line stays on disk forever and every later `board` run
    re-reports it, so trim it (to `.crashtrim/`).
  * `results/nodes/*.json` -- the cached node LP.  **Dangerous**: `pilot59.run_child` does a bare
    `json.load(open(node_path))` with no try/except, so a torn file makes the shard CRASH on
    resume, repeatedly, at the same child.  Quarantine it and the LP is simply redone.
  * `certs/*.json` with a `.PASS` marker -- **most serious**: a torn certificate carrying a PASS
    marker is a FALSE CLAIM of proof.  Quarantine the certificate AND its marker together; the
    node then re-certifies from scratch.

Quarantine, never delete: everything moves under `crashquarantine/` with its original name.

    python code\integrity60.py            # report only
    python code\integrity60.py --fix      # trim/quarantine and log what was done
"""
import argparse, json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
PROG = os.path.join(BASE, "progress")
QUAR = os.path.join(BASE, "crashquarantine")


def _q(path, why, fix):
    if not fix:
        return
    os.makedirs(QUAR, exist_ok=True)
    dst = os.path.join(QUAR, os.path.basename(path))
    n = 0
    while os.path.exists(dst):
        n += 1
        dst = os.path.join(QUAR, "%s.%d" % (os.path.basename(path), n))
    shutil.move(path, dst)


def check_jsonl(fix):
    out = []
    for f in sorted(os.listdir(RES)):
        if not f.endswith(".jsonl"):
            continue
        p = os.path.join(RES, f)
        lines = open(p, "rb").read().split(b"\n")
        bad = []
        for i, ln in enumerate(lines):
            if not ln.strip():
                continue
            try:
                json.loads(ln.decode("utf-8"))
            except Exception as e:
                bad.append((i + 1, len(ln), str(e)[:60]))
        if bad:
            out.append(dict(file=f, torn_lines=bad, total_lines=len(lines)))
            if fix:
                keep = [ln for ln in lines if ln.strip() and _ok(ln)]
                os.makedirs(QUAR, exist_ok=True)
                shutil.copy2(p, os.path.join(QUAR, f + ".pre-trim"))
                with open(p, "wb") as fh:
                    fh.write(b"\n".join(keep) + b"\n")
    return out


def _ok(ln):
    try:
        json.loads(ln.decode("utf-8"))
        return True
    except Exception:
        return False


def check_json_dir(d, label, fix, also_marker=None):
    out = []
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json"):
            continue
        p = os.path.join(d, f)
        try:
            json.load(open(p))
        except Exception as e:
            rec = dict(file=os.path.join(label, f), size=os.path.getsize(p), error=str(e)[:80])
            marker = p + ".PASS"
            rec["had_PASS_marker"] = os.path.exists(marker)
            out.append(rec)
            _q(p, label, fix)
            if rec["had_PASS_marker"]:
                _q(marker, label + " (PASS marker of a torn certificate)", fix)
    return out


def orphan_markers():
    """a .PASS marker whose certificate is missing entirely."""
    out = []
    if not os.path.isdir(CERTS):
        return out
    for f in sorted(os.listdir(CERTS)):
        if f.endswith(".json.PASS") and not os.path.exists(os.path.join(CERTS, f[:-5])):
            out.append(f)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args()
    rep = dict(ts=time.strftime("%Y-%m-%d %H:%M:%S"), fix=a.fix)
    rep["jsonl"] = check_jsonl(a.fix)
    rep["nodes"] = check_json_dir(os.path.join(RES, "nodes"), "results/nodes", a.fix)
    rep["certs"] = check_json_dir(CERTS, "certs", a.fix)
    rep["progress"] = check_json_dir(PROG, "progress", a.fix)
    rep["results_top"] = check_json_dir(RES, "results", a.fix)
    rep["orphan_PASS_markers"] = orphan_markers()
    tot = sum(len(rep[k]) for k in ("jsonl", "nodes", "certs", "progress", "results_top"))
    rep["total_damaged"] = tot
    print(json.dumps(rep, indent=1))
    with open(os.path.join(BASE, "logs", "integrity_%s.json" %
                           time.strftime("%Y%m%d_%H%M%S")), "w") as f:
        json.dump(rep, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
