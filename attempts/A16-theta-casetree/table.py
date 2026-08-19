"""A16 — summary table from results/*.json (markdown to stdout and results/table.md)."""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))

ORDER = ["N0", "N1", "N2", "N3a", "N3b", "N3c", "N3d", "N3e", "N4", "N4b", "N5", "N5s"]


def fmt(v, nd=3):
    return "–" if v is None else f"{v:.{nd}f}"


def row(R):
    b = R.get("budget")
    nu = R.get("nu"); nu_lb = R.get("nu_lb")
    th_lb = R.get("theta_lb_feasible"); th_ub = R.get("theta_ub_cert")
    sub = R.get("support_sub") or {}
    if sub.get("theta_lb") is not None:
        th_lb = max(th_lb or 0, sub["theta_lb"])
    al = R.get("alpha")
    if al is not None:
        th_lb = max(th_lb or 0, al)
    lp_v = "–" if nu is None else ("dead %+.2f" % (nu - b) if nu < b - 1e-6 else "alive %+.2f" % (nu - b))
    th_v = "–" if th_ub is None else ("DEAD (ub %+.2f)" % (th_ub - b) if th_ub < b - 1e-6 else ("alive (lb %+.2f)" % (th_lb - b) if (th_lb or 0) >= b - 1e-6 else "undecided [%+.2f, %+.2f]" % ((th_lb or 0) - b, th_ub - b)))
    seeded = "seeded" if R.get("seeded") else "UN-seeded"
    if R.get("seeded") and not R.get("a15_extras"):
        seeded = "seeded (own only)"
    return (f"| {R.get('node')} | {R.get('s')} | {seeded} | {R.get('tag')} | {R.get('N')} | {R.get('group')} | {R.get('edges')} | "
            f"{fmt(nu, 4)} (≥{fmt(nu_lb, 3)}) | [{fmt(th_lb, 3)}, {fmt(th_ub, 3)}] | {'–' if al is None else al} | {b} | LP: {lp_v}; ϑ′: {th_v} | "
            f"{R.get('sdp_iters', '–')} it / {fmt(R.get('sdp_time'), 0)} s; sub |S|={sub.get('n', '–')} [{fmt(sub.get('theta_lb'), 3)}, {fmt(sub.get('theta_ub'), 3)}] |")


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "results", "*.json"))):
        R = json.load(open(f, encoding="utf-8"))
        if "node" not in R or R["tag"].startswith("smoke"):
            continue
        rows.append(R)
    rows.sort(key=lambda R: (ORDER.index(R["node"]) if R["node"] in ORDER else 99, R["s"], not R.get("seeded", False), R["tag"]))
    hdr = ("| node | s | grid | tag | N | sym | edges | ν*_G (LP) [lb] | ϑ′_G bracket | α_G | budget | verdict (slack vs budget) | SDP iters/time; support sub-SDP |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    out = hdr + "\n" + "\n".join(row(R) for R in rows)
    print(out)
    open(os.path.join(HERE, "results", "table.md"), "w", encoding="utf-8").write(out + "\n")


if __name__ == "__main__":
    main()
