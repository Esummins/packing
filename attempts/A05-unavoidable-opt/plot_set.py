"""Plot a point set with the tight (worst) squares.  usage: python plot_set.py result.jsonl [index] out.png"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unavoid import worst_configs, square_corners


def plot(P, s0, out, title=None, nworst=8, worst=None):
    P = np.asarray(P)
    if worst is None:
        worst = worst_configs(P, s0, nth=180, nc=200, K=30, polish=8)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.add_patch(plt.Rectangle((0, 0), s0, s0, fill=False, lw=2, color="k"))
    cmap = plt.get_cmap("tab10")
    for i, w in enumerate(worst[:nworst]):
        cx, cy, th, d = w
        C = square_corners(cx, cy, th)
        ax.plot(C[:, 0], C[:, 1], color=cmap(i % 10), lw=1.2, alpha=0.9,
                label=f"c=({cx:.3f},{cy:.3f}) th={np.degrees(th):.1f}deg d={d:+.4f}")
    ax.plot(P[:, 0], P[:, 1], "o", color="k", ms=6, zorder=5)
    for i, p in enumerate(P):
        ax.annotate(str(i), p, textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax.set_aspect("equal"); ax.set_xlim(-0.1, s0 + 0.1); ax.set_ylim(-0.1, s0 + 0.1)
    ax.set_title(title or f"{len(P)} points, s0={s0:.6f}, max d={worst[0][3]:+.5f}")
    ax.legend(fontsize=6, loc="upper left", bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return worst


if __name__ == "__main__":
    recs = [json.loads(l) for l in open(sys.argv[1])]
    idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    out = sys.argv[3] if len(sys.argv) > 3 else "plot.png"
    recs.sort(key=lambda r: -r.get("s0", 0) if "worst" in r else r["g_fine"])
    r = recs[idx]
    w = plot(r["P"], r["s0"], out, title=f"{r['group']} {''.join(r['spec'])}  s0={r['s0']:.6f}")
    for x in w[:10]:
        print(x)
