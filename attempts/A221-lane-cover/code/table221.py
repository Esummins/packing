"""A221 -- render results/bench221.md from results/bench221.jsonl (last row per (tag, page, run, node))."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
HEAD = """# A221 benchmark -- A189's no-room leaf vs A221's pocket cover

Every row replays a RECORDED no-room node out of an A211 certificate (`code/nodeload221.py`: the node's own role
boxes, the five pins included) through `noroom221`.  `A189` is the verdict and seconds the CERTIFICATE recorded;
`A221` is this module on the replayed boxes.  A REGRESSION is a recorded DEAD that A221 does not kill -- the only
unsound direction, and there are none.

**The replayed boxes are not always the boxes A189 saw.**  A node record's `roles` is the page's live dict, so a
certificate can carry boxes TIGHTER than the ones `tree209.noroom_at` was handed at the leaf.  That is why the
`a189ctl` rows exist: they run A189's OWN leaf (`noroom189.noroom`) on exactly the replayed boxes, so a kill A221
reaches and the certificate did not is attributed to the COVER only when the control also fails to kill it.

Tags: `four` = the four target k=10 nodes (full leaf, 45 s pocket cap) | `inherit` / `inherit5` = the same through
Lemma POCKET-INHERIT (the nearest recorded ancestor's pockets, no container bisection) | `alive_page` = every
recorded no-room node of the ALIVE page Y0402 at the 45 s cap | `cap5` = the same with the MEASURED 5 s pocket cap
(the deployed setting) | `closed` = every recorded no-room node of the CLOSED pages Y0500 g1 / Y0460 g1 (verdict
agreement) | `a189ctl` = the control | `deep` = the budget probe of `results/experiment221.md` s.3b.
"""


def load(path):
    rows = {}
    for ln in open(path):
        try:
            r = json.loads(ln)
        except Exception:                                                    # noqa: BLE001
            continue
        rows[(r.get("tag"), r.get("page"), r.get("run"), r.get("node"))] = r
    return list(rows.values())


def fmt(r):
    pd = r.get("pocket_dead") or []
    return "| %s | %s | %s | %s | %s | %ss | %s | %ss | %s | %d/%d | %s |" % (
        r.get("tag"), (r.get("page") or "")[-22:], (r.get("run") or "")[:4], (r.get("node") or "")[-24:],
        r.get("recorded"), r.get("recorded_seconds"), r.get("a221"), r.get("a221_seconds"),
        r.get("a221_clip") or "-", sum(1 for x in pd if x), len(pd), r.get("step"))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, "bench221.jsonl")
    rows = load(path)
    rows.sort(key=lambda r: (str(r.get("tag")), str(r.get("page")), str(r.get("run")), str(r.get("node"))))
    out = [HEAD, "| tag | page | run | node | A189 | s | A221 | s | clip | pockets dead | step |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    out += [fmt(r) for r in rows]

    ctl = {r["node"]: r for r in rows if r.get("step") == "a189-control"}
    live = [r for r in rows if r.get("tag") not in ("deep",) and r.get("step") != "a189-control"]
    reg = [r for r in live if r.get("regression")]
    kills = sorted(set((r["node"], (ctl.get(r["node"]) or {}).get("a221", "control not run"))
                       for r in live if r.get("recorded") == "UNDECIDED" and r.get("a221") == "DEAD"))
    out += ["", "## Summary", "",
            "* rows: %d (%d A189 control, %d budget probe); **REGRESSIONS: %d**"
            % (len(rows), len(ctl), sum(1 for r in rows if r.get("tag") == "deep"), len(reg)), "",
            "Nodes A221 kills that the certificate left UNDECIDED, with the control's verdict on the SAME boxes:", ""]
    out += ["  * `%s` -- A189 on the same replayed boxes: **%s**%s"
            % (nd, v, "  (so this kill is A221's cover)" if v == "UNDECIDED"
               else "  (so this one is the tighter replayed boxes, NOT A221)") for nd, v in kills] or ["  * none"]
    out += ["", "Wall, per lane (non-vacuous nodes only):", ""]
    for tag in sorted(set(r.get("tag") for r in live)):
        sel = [r for r in live if r.get("tag") == tag and r.get("recorded") != "VACUOUS"
               and r.get("recorded_seconds") is not None and r.get("a221_seconds") is not None]
        if not sel:
            continue
        a = sum(float(r["recorded_seconds"]) for r in sel)
        b = sum(float(r["a221_seconds"]) for r in sel)
        out.append("* `%s`: %d nodes, A189 %.0f s -> A221 %.0f s (**%.2fx**); slowest A221 node %.1f s"
                   % (tag, len(sel), a, b, a / max(b, 1e-9), max(float(r["a221_seconds"]) for r in sel)))
    with open(os.path.join(RES, "bench221.md"), "w", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out[out.index("## Summary"):]))


if __name__ == "__main__":
    main()
