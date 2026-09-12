"""A210 driver: per page, STAGE 0 (A202's closed-form layer) + A203's piece CSP + RULE CC (Lemma CORNER-COVER),
PAD 0 FIRST (a pad-0 kill is s0-only, WINDOW-PENDING; A209's note) then the G1 window pad; the page drawn after each
pad.  Certificates certs/cornercover210_<nid>_<pad>_s0.json; rows results/cornercover210.jsonl (one per (nid, pad):
page, pad, verdict, rows killed by Q, seconds).  Resumable: a (nid, pad) already in the jsonl is skipped unless
--force.
    python run210.py <nid> [--pads zero,g1] [--force]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "cornercover210.jsonl"))
sys.path.insert(0, HERE)
import fast30                                                  # noqa: E402
import fig210                                                  # noqa: E402


def emit(out, cert):
    os.makedirs(os.path.dirname(cert), exist_ok=True)
    json.dump(out, open(cert, "w", encoding="utf-8"), indent=1, default=str)
    slim = {k: v for k, v in out.items() if k not in ("tests", "steps", "rounds", "subrects", "wbox", "alive_rects", "csp")}
    slim["csp"] = [{k: v for k, v in r.items() if k not in ("unit_rects", "unit_alive", "mask_bits", "dead_units")} for r in out.get("csp") or []]
    slim["cc"] = out.get("cc")
    slim["Q_kills"] = (out.get("kills") or {}).get("Q", {}).get("kills", 0)
    slim["cert"] = os.path.relpath(cert, ROOT).replace("\\", "/")
    slim["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")


def done(nid, pad):
    if not os.path.exists(RES):
        return None
    last = None
    for line in open(RES, encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("nid") == nid and d.get("pad") == pad:
            last = d
    return last


def draw(nid):
    try:
        print("   page: %s" % fig210.render(nid), flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("   fig210 failed: %r" % (e,), flush=True)


def stage0(nid, pad, force):
    cert = os.path.join(CERTS, "cornercover210_%s_%s_s0.json" % (nid, pad))
    prev = done(nid, pad)
    if prev and not force and os.path.exists(cert):
        print("   %s pad: cached %s" % (pad, prev.get("verdict")), flush=True)
        return prev
    st = fast30.Stage0(nid, pad)
    out = st.run()
    hh = st.h_hull()
    out["H_hull_raw"] = list(hh) if hh else None
    emit(out, cert)
    cc = (out.get("cc") or [{}])[-1]
    print("== %s pad %s: %s in %.0f ms; kills %s; CC: %d Q + %d H piece(s) in %s ms, slots %s; caps %s%s" % (
        nid, pad, out["verdict"], 1000 * out["seconds"], {k: v["kills"] for k, v in out["kills"].items()},
        cc.get("killed", 0), cc.get("h_killed", 0), cc.get("ms"),
        [(s["slot"], s["near_corner"], s.get("dead_classes")) for s in cc.get("slots") or []], out.get("caps"),
        ("; " + str(out["leaf"])) if out["leaf"] else ""), flush=True)
    draw(nid)
    return out


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:
        pass


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--pads", default="zero,g1")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for pad in a.pads.split(","):
        stage0(a.nid, pad, a.force)
