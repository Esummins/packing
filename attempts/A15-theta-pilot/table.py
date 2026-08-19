"""Print the results table (markdown) from results/*.json."""
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
tags = sys.argv[1:] or ["c380", "c384", "c385", "c387", "m385", "m387", "f385"]
print("| run | s | graph | N | orbits | edges | ν*_G (LP) | ϑ′_G bracket [lb, ub] | SCS pobj/dobj (status) | α_G | LP / SDP / α time |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for t in tags:
    p = os.path.join(HERE, "results", t + ".json")
    if not os.path.exists(p):
        print(f"| {t} | (missing) |"); continue
    R = json.load(open(p))
    g = ("mid-tilt {0}∪[30,36] step %g°" % R.get("mid_step", 2)) if R.get("mid") else f"h={R['h']}, Δθ={R['dtheta']}°"
    g += " + extras" if R.get("extra") else ""
    nu = f"{R['nu']:.4f}" if "nu" in R else "—"
    if "theta_ub_cert" in R:
        lb = max(R.get("theta_lb_feasible", 0.0), float(R.get("alpha", 0) or 0))
        th = f"[{lb:.3f}, **{R['theta_ub_cert']:.3f}**]"
        st = f"{R['theta']:.3f} / {R['theta_dual']:.3f} ({R['sdp_status'].replace('solved (inaccurate - reached time_limit_secs)', 'time limit')}, {R['sdp_iters']} it)"
    else:
        th = "—"; st = "—"
    al = f"{R['alpha']} ({R['alpha_status']})" if "alpha" in R else "—"
    tm = f"{R.get('lp_time', 0):.0f} / {R.get('sdp_time', 0):.0f} / {R.get('alpha_time', 0):.0f} s"
    print(f"| {t} | {R['s']} | {g} | {R['N']} | {R['n_orbits']} | {R['edges']} | {nu} | {th} | {st} | {al} | {tm} |")

print()
print("| run | s | |S| (orbits, edges) | LP ν on G[S] | ϑ′(G[S]) bracket | α(G[S]) | ⇒ ϑ′(G) bracket [ϑ′(G[S]) lb, big-SDP ub] |")
print("|---|---|---|---|---|---|---|")
for t in tags:
    p = os.path.join(HERE, "results", t + ".json")
    if not os.path.exists(p):
        continue
    R = json.load(open(p))
    S = R.get("support_sub")
    if not S:
        print(f"| {t} | {R['s']} | (not run) | | | | |"); continue
    print(f"| {t} | {R['s']} | {S['n']} ({S['orbits']}, {S['edges']}) | {S['nu']:.4f} | [{S['theta_lb']:.4f}, {S['theta_ub']:.4f}] | {S['alpha']} ({S['alpha_status']}) | **[{S['theta_lb']:.3f}, {R.get('theta_ub_cert', float('nan')):.3f}]** |")
