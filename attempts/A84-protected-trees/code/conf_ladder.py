import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from caselp import Hyp, NoFam
from pilot59 import PINS, SLOTS, FREE, core_box, rq, run_child, init_warm
from pinguard import classify
from alive59 import alive_verdict
from drive59 import TSC, boxes_pairwise_disjoint
init_warm()
HW = 0.02
ORDER = ["sq4", "sq6", "sq8", "sq9", "sq10"]
res = []
for j in (4, 3, 2, 1):
    S = ORDER[:j]
    cores = [core_box(n, HW, TSC * HW) for n in S]
    assert not boxes_pairwise_disjoint(cores + PINS)
    assert all(classify(b, PINS, SLOTS)[0] == "ok" for b in cores)
    budget = 6 - j
    for a in (0.3, 0.15, 0.075):
        cx, cy, _ = FREE["sq7"]
        fam = NoFam(rq(cx - a), rq(cx + a), rq(cy - a), rq(cy + a), [(0.0, 90.0)])
        hyp = Hyp(PINS + cores, [fam])
        av = alive_verdict(hyp, budget)
        line = "j=%d budget=%d a=%g  A57-3: k=%d %s" % (j, budget, a, av["k"], av["alive_verdict"][:60])
        print(line, flush=True)
        res.append(dict(j=j, budget=budget, a=a, k=av["k"], unkillable=av["unkillable"]))
        if av["unkillable"]:
            continue
        r = run_child("conf_j%d_hw%g_a%g" % (j, HW, a), hyp, budget, j, a, None,
                      "NO-conf-level", "ok", dict(cores=S, k=av["k"]), fam.to_json(),
                      lp_time=240.0, cert_time=240.0)
        if r:
            res[-1].update(tau=r["tau"], verdict=r["verdict"], lp_s=r["lp_s"], cert_s=r["cert_s"])
        json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                         "results", "conf_ladder.json"), "w"), indent=1)
