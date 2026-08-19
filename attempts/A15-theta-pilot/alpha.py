"""alpha(G) by CP-SAT (reference only)."""
import numpy as np


def max_independent_set(ov, time_limit=120.0, workers=8, hint=None):
    from ortools.sat.python import cp_model
    n = len(ov)
    m = cp_model.CpModel()
    z = [m.NewBoolVar(f"z{i}") for i in range(n)]
    I, J = np.nonzero(np.triu(ov, 1))
    for i, j in zip(I.tolist(), J.tolist()):
        m.AddBoolOr([z[i].Not(), z[j].Not()])
    m.Maximize(sum(z))
    if hint is not None:
        hs = set(hint)
        for i in range(n):
            m.AddHint(z[i], 1 if i in hs else 0)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = time_limit
    sol.parameters.num_workers = workers
    st = sol.Solve(m)
    sel = [i for i in range(n) if sol.Value(z[i])]
    return len(sel), sel, sol.StatusName(st), sol.BestObjectiveBound()
