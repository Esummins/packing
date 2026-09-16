"""A238 -- the residue-map pages: one SVG per benchmark node + a gallery, in
docs/residue_map/campaigns/A238-k4-benchmark/.

    python pages238.py [nid ...]          # default: the class roots, the first kills and every gated / tube node

A238 reuses A212's page layout (`fig212`: A211's `fig211` panel plus a gate / tube note on every node) with the
output directory and the certificate directory rebound to this attempt.  Read-only: fig204 / fig211 / fig212 are
imported, never edited."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import path238                                                  # noqa: E402
path238.fix()
import fig211 as F11                                            # noqa: E402  READ-ONLY (A211)
import fig212 as F12                                            # noqa: E402  READ-ONLY (A212: the gate / tube notes)

ROOT = path238.ROOT
A238 = os.path.abspath(os.path.join(path238.HERE, ".."))
CERTS = os.path.join(A238, "certs")
OUTD = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A238-k4-benchmark")
F12.OUTD, F12.CERTS = OUTD, CERTS


def cert_of(nid):
    return os.path.join(CERTS, "k4bench238_%s.json" % nid)


def render(nid):
    f = cert_of(nid)
    if not os.path.exists(f):
        return None
    doc = json.load(open(f, encoding="utf-8"))
    os.makedirs(OUTD, exist_ok=True)
    F11.node_note, F11.stage_lines = F12.node_note, F12.stage_lines
    svg = F11.page_svg(doc)
    svg = svg.replace("A211 coarsetree211: the COARSE tree",
                      "A238 k4bench238: the k5 toolkit on the PROTECTED CLASS %s (A211's live coarse tree + A212's "
                      "Trump-containment GATE + Lemma TUBE-LEAF/S in the class direction; pad 0, s0-only)" % doc.get("cls"), 1)
    svg = svg.replace("certs/coarsetree211_%s.json" % doc["nid"], "attempts/A238-k4-benchmark/certs/k4bench238_%s.json" % doc["nid"])
    p = os.path.join(OUTD, "k4bench238_%s.svg" % nid)
    open(p, "w", encoding="utf-8").write(svg)
    return p


def interesting(limit_per_class=6):
    """the class roots, the first geometry kills of each class, and every node whose gate held."""
    out, first = [], {}
    for f in sorted(glob.glob(os.path.join(CERTS, "k4bench238_*.json"))):
        try:
            doc = json.load(open(f, encoding="utf-8"))
        except Exception:                                         # noqa: BLE001
            continue
        nid, cls = doc.get("nid"), doc.get("cls")
        d = (doc.get("runs") or {}).get("zero_page") or {}
        gated = any((n.get("trump_gate") or {}).get("contains") for n in (d.get("nodes") or []))
        if nid.endswith("_root") or gated:
            out.append(nid)
            continue
        if d.get("verdict") == "DEAD" and len(first.setdefault(cls, [])) < limit_per_class:
            first[cls].append(nid)
    for v in first.values():
        out += v
    return sorted(set(out))


def gallery():
    S, docs = 52, []
    for f in sorted(glob.glob(os.path.join(CERTS, "k4bench238_*.json"))):
        try:
            docs.append(json.load(open(f, encoding="utf-8")))
        except Exception:                                         # noqa: BLE001
            continue
    F12.CERTS = CERTS
    try:
        return F12.gallery()
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)
        return None


if __name__ == "__main__":
    nids = sys.argv[1:] or interesting()
    done = []
    for nid in nids:
        p = render(nid)
        if p:
            done.append(os.path.relpath(p, ROOT).replace("\\", "/"))
    print("A238 pages: %d written -> %s" % (len(done), os.path.relpath(OUTD, ROOT)))
    for p in done:
        print("   " + p)
