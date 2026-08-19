"""A17 — export the float kernel certificate: results/kernel_<tag>.json (spec, atoms, weights,
lambda, attack numbers) + results/kernel_<tag>_M.npy (dense (m+1)x(m+1) PSD matrix, feature order =
(const, atoms in listed order)).   usage: python export_cert.py <tag> [<s>] [--atoms a07_384]
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main(tag, s=3.84, atoms="a07_384"):
    from features import FeatureMap, load_atoms_a07_384, load_atoms_cert, build_symmetry, stretch_1d
    from sdp import KernelSDP
    if atoms == "a07_384":
        A, w, s_at = load_atoms_a07_384()
        if abs(s_at - s) > 1e-12:
            A = np.stack([stretch_1d(A[:, 0], s_at, s), stretch_1d(A[:, 1], s_at, s)], 1)
    else:
        ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
        A, w, _ = load_atoms_cert(os.path.join(ROOT, "certs", "measure_certificate_3.82.json"), s_to=s)
    fm = FeatureMap(A, w, s)
    sym = build_symmetry(fm)
    prob = KernelSDP(sym)
    st = np.load(os.path.join(HERE, "results", tag + "_state.npz"), allow_pickle=True)
    Y = {n: st["Y_" + n] for n in prob.names}
    M = prob.get_M(Y)
    run = json.load(open(os.path.join(HERE, "results", tag + ".json")))
    fin = run.get("final", {})
    out = dict(
        format="kernel-certificate-float-v1",
        claim=f"K(x,y) = phi(x)^T M phi(y) with phi(x) = (1, 1[p_k in Q(x)]/m(x)) satisfies "
              f"K(x,x) <= lambda-1 for all x in P_s and K(x,y) <= -1 for all pairs of disjoint "
              f"CLOSED unit squares in [0,{s}]^2, with lambda = lam_cert < 11 => s(11) >= {s} "
              f"(FLOAT phase: constraints verified only by the cutting-plane oracles; see notes.md §7)",
        s=s, n=11,
        feature_map="normalised coverage indicators: phi_0 = 1, phi_k = 1[p_k in Q(x)]/m(x), "
                    "m(x) = sum_k w_k 1[p_k in Q(x)] (closed squares)",
        atoms=[[float(x), float(y)] for x, y in A],
        weights=[float(v) for v in w],
        n_features=fm.nf,
        M_file=f"kernel_{tag}_M.npy",
        M_psd="exact by construction (M = sum_n,r T Y^T Y T^T)",
        lam_sdp=run["history"][-1]["lam_sdp"] if run.get("history") else None,
        attack=fin,
        provenance=dict(attempt="A17-kernel-root", solver="block Burer-Monteiro + L-BFGS",
                        rank=run.get("rank"), delta_pair=run.get("delta_pair"),
                        rows_final=run["history"][-1]["nrows"] if run.get("history") else None,
                        atom_source=atoms),
    )
    np.save(os.path.join(HERE, "results", f"kernel_{tag}_M.npy"), M)
    json.dump(out, open(os.path.join(HERE, "results", f"kernel_{tag}.json"), "w"), indent=1)
    ev = np.linalg.eigvalsh(M)
    print(f"exported kernel_{tag}.json + M ({fm.nf}x{fm.nf}, rank@1e-8 {int((ev > 1e-8*ev.max()).sum())}, "
          f"min eig {ev.min():.2e}); lam_cert = {fin.get('lam_cert')}")


if __name__ == "__main__":
    tag = sys.argv[1]
    s = float(sys.argv[2]) if len(sys.argv) > 2 else 3.84
    atoms = sys.argv[3] if len(sys.argv) > 3 else "a07_384"
    main(tag, s, atoms)
