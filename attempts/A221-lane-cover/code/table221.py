"""A221 -- render results/bench221.md from results/bench221.jsonl (last row per (tag, page, run, node))."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")


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
    out = ["# A221 benchmark -- A189's no-room leaf vs A221's pocket cover",
           "",
           "Every row replays a RECORDED no-room node out of an A211 certificate (`code/nodeload221.py`: the node's",
           "own role boxes, pins included) through `noroom221`.  `A189` is what the certificate recorded; `A221` is",
           "this module.  A REGRESSION is a recorded DEAD that A221 does not kill -- the only unsound direction.",
           "Tags: `four` = the four target k=10 nodes (full leaf), `inherit` = the same through Lemma POCKET-INHERIT",
           "(the nearest recorded ancestor's pockets, no container bisection), `deep` = the budget probe of",
           "`results/experiment221.md` s.3b, `closed` = every recorded no-room node of a CLOSED page (verdict",
           "agreement).", "",
           "| tag | page | run | node | A189 | s | A221 | s | clip | pockets dead | step |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    out += [fmt(r) for r in rows]
    reg = [r for r in rows if r.get("regression")]
    kills = [r for r in rows if r.get("recorded") == "UNDECIDED" and r.get("a221") == "DEAD"]
    both = [r for r in rows if r.get("recorded_seconds") and r.get("a221_seconds")]
    sp = sorted(float(r["recorded_seconds"]) / max(float(r["a221_seconds"]), 1e-6) for r in both)
    out += ["",
            "## Summary", "",
            "* rows: %d; **REGRESSIONS: %d**" % (len(rows), len(reg)),
            "* nodes A221 kills that A189 left UNDECIDED: **%d**%s"
            % (len(kills), (" (" + ", ".join("%s %s" % (r["page"][-18:], r["node"]) for r in kills) + ")") if kills else ""),
            "* speed-up A189 s / A221 s: median **%.1fx**, range %.1fx - %.1fx (%d rows)"
            % (sp[len(sp) // 2], sp[0], sp[-1], len(sp)) if sp else "* speed-up: n/a"]
    with open(os.path.join(RES, "bench221.md"), "w", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out[-6:]))


if __name__ == "__main__":
    main()
