"""
A57 post-crash integrity check.

A hard stop (Kernel-Power 41, no dump) can leave a partially written last line in an append-only
jsonl, or a truncated json where a writer was mid-`json.dump`.  The last-record-wins convention
tolerates a *missing* record but a malformed trailing line will crash a reader, so this trims it.

Discipline:
  * only the LAST line of a jsonl may be trimmed -- a malformed line anywhere else is reported
    and NOT touched, because that is corruption of a different kind and wants a human;
  * every file that is modified is copied to `quarantine/<name>.<stamp>.bak` first, and the
    offending text is written to `quarantine/<name>.<stamp>.partial` so nothing is destroyed;
  * whole-json files (progress, node results, certificates) are never repaired, only reported --
    a truncated node json is simply deleted-by-report so the child is recomputed, which is always
    safe (the node is then absent from `done` and gets redone).
"""
import argparse, glob, json, os, shutil, time

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STAMP = time.strftime("%Y%m%d-%H%M%S")
QDIR = os.path.join(BASE, "quarantine")


def q(path, suffix, text=None):
    os.makedirs(QDIR, exist_ok=True)
    dst = os.path.join(QDIR, f"{os.path.basename(path)}.{STAMP}.{suffix}")
    if text is None:
        shutil.copy2(path, dst)
    else:
        with open(dst, "w") as f:
            f.write(text)
    return dst


def check_jsonl(path, fix):
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", errors="replace")
    lines = text.split("\n")
    trailing_nl = text.endswith("\n")
    body = lines[:-1] if trailing_nl else lines
    bad_mid, bad_last = [], None
    for i, ln in enumerate(body):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            if i == len(body) - 1:
                bad_last = (i + 1, ln, repr(e)[:110])
            else:
                bad_mid.append((i + 1, repr(e)[:80]))
    rec = dict(file=os.path.relpath(path, BASE), lines=len([l for l in body if l.strip()]),
               ends_with_newline=trailing_nl, bad_midfile=len(bad_mid))
    if bad_mid:
        rec["midfile_lines"] = [n for n, _ in bad_mid[:5]]
        rec["action"] = "REPORTED ONLY (mid-file corruption -- not auto-repaired)"
    elif bad_last:
        n, ln, err = bad_last
        rec.update(truncated_last_line=n, last_line_bytes=len(ln), error=err)
        if fix:
            q(path, "bak")
            q(path, "partial", ln)
            keep = "\n".join(body[:-1])
            with open(path, "w") as f:
                f.write(keep + ("\n" if keep else ""))
            rec["action"] = "TRIMMED (backup + partial text in quarantine/)"
        else:
            rec["action"] = "would trim (run with --fix)"
    elif not trailing_nl and body and body[-1].strip():
        rec["action"] = "last line parses but has no trailing newline (benign; writer was mid-flush)"
    else:
        rec["action"] = "clean"
    return rec


def check_json(path):
    try:
        with open(path) as f:
            json.load(f)
        return None
    except Exception as e:
        return dict(file=os.path.relpath(path, BASE), size=os.path.getsize(path),
                    error=repr(e)[:120], action="CORRUPT -- quarantine and let it be recomputed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--quarantine-corrupt-json", action="store_true",
                    help="move corrupt whole-json files aside so their child is recomputed")
    a = ap.parse_args()

    out = dict(stamp=STAMP, jsonl=[], json_corrupt=[])
    for p in sorted(glob.glob(os.path.join(BASE, "results", "*.jsonl"))):
        out["jsonl"].append(check_jsonl(p, a.fix))
    pats = ["progress/*.json", "results/nodes/*.json", "results/tree/*/*.json",
            "results/*.json", "certs/*/*.json", "certs/*/*/*.json"]
    for pat in pats:
        for p in sorted(glob.glob(os.path.join(BASE, pat))):
            r = check_json(p)
            if r:
                if a.quarantine_corrupt_json:
                    q(p, "corrupt")
                    os.remove(p)
                    r["action"] = "QUARANTINED and removed (will be recomputed)"
                out["json_corrupt"].append(r)
    out["summary"] = dict(jsonl_files=len(out["jsonl"]),
                          jsonl_trimmed=sum(1 for r in out["jsonl"] if str(r.get("action", "")).startswith("TRIMMED")),
                          jsonl_would_trim=sum(1 for r in out["jsonl"] if str(r.get("action", "")).startswith("would trim")),
                          jsonl_midfile_bad=sum(1 for r in out["jsonl"] if r.get("bad_midfile")),
                          json_corrupt=len(out["json_corrupt"]))
    print(json.dumps(out["summary"], indent=1))
    for r in out["jsonl"]:
        if r.get("action") != "clean":
            print("  jsonl:", json.dumps(r))
    for r in out["json_corrupt"]:
        print("  json :", json.dumps(r))
    json.dump(out, open(os.path.join(BASE, "results", f"fsck_{STAMP}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
