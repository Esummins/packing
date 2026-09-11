"""A207 -- A202's stage 0 (the copies fast30 / fast30b / rules202 / count202 in this directory) with the BASIN CLIP as one more
closed-form layer: every alive piece of every forced slot and every piece of H is cut by the basins B_F(p) of the page's FULL slots
(clip207: exact rect-minus-box per tilt part, Lemma BASIN), before the union caps / Theorem FC / the count / the H forcing.
    python stage0_207.py <nid> [g1|zero|window]     -> certs/s0basin207_<nid>_<pad>.json, results/s0basin207.jsonl, the page"""
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import fast30                                                  # noqa: E402  (the A202 copy)
import fast30b                                                 # noqa: E402
import clip207 as C                                            # noqa: E402
import poly204 as P                                            # noqa: E402

QP = P.QP
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "s0basin207.jsonl"))


class Stage0Basin(fast30.Stage0):
    def __init__(self, nid, pad="g1", **kw):
        fast30.Stage0.__init__(self, nid, pad, **kw)
        self.basins = C.load_basins(self.cls, pad, QP.PADS[pad])
        self.basin_kills = {}

    def _clip_list(self, pieces, tag):
        if not self.basins or not pieces:
            return pieces
        t0 = time.perf_counter()
        out = []
        n_cut = 0
        for pc in pieces:
            ci, rf, _, bn, _, ch = pc
            new, rep = C.clip_pieces([(bn, rf)], self.basins)
            if not rep:
                out.append(pc)
                continue
            n_cut += 1
            for b2, r2 in new:
                q = fast30.mkpiece(ci, r2, fast30.mkbin(b2.t0, b2.t1) if b2 is not bn else bn)
                q[5] = ch                                                  # the parent's min chords: a lower bound for every child pose
                out.append(q)
        if n_cut:
            self.basin_kills[tag] = self.basin_kills.get(tag, 0) + n_cut
            self.tally("B", n_cut, time.perf_counter() - t0)
        return out

    def sweep(self, pieces, p, cnt, tm, depth):
        return self._clip_list(fast30.Stage0.sweep(self, pieces, p, cnt, tm, depth), p)

    def clip_H(self, forced=(), depth=0):
        n = fast30.Stage0.clip_H(self, forced, depth)
        if n and self.basins:
            self.hpieces = self._clip_list(self.hpieces, "H")
            self.refresh_H()
            if not self.hpieces:
                self.verdict_leaf = "BASIN(H): every pose of H lies in the basin of a FULL slot's simple pose (Lemma BASIN)"
        return len(self.hpieces)

    def result(self):
        out = fast30b.certificate(self)
        out["path"] = "fast30+basin207"
        out["basins"] = [C.basin_json(b) for b in self.basins]
        out["basin_pieces_cut"] = dict(self.basin_kills)
        out["verifier"] = "[C: closed-form trace + Lemma BASIN (extension certificates)] -- no verifier clause on the stage-0 layer"
        return out


def run(nid, pad="g1"):
    st = Stage0Basin(nid, pad)
    out = st.run()
    hh = st.h_hull()
    out["H_hull_raw"] = list(hh) if hh else None
    cert = os.path.join(CERTS, "s0basin207_%s_%s.json" % (nid, pad))
    os.makedirs(CERTS, exist_ok=True)
    json.dump(out, open(cert, "w", encoding="utf-8"), indent=1, default=str)
    rd = out["rounds"][-1] if out["rounds"] else {}
    slim = {k: v for k, v in out.items() if k not in ("tests", "steps", "rounds", "subrects", "wbox", "free_opts", "alive0", "alive_rects")}
    slim.update(cert=os.path.relpath(cert, ROOT).replace("\\", "/"), n_rounds=len(out.get("rounds") or []), when=time.strftime("%Y-%m-%d %H:%M:%S"),
                alive_cells={p: len(v) for p, v in (rd.get("single") or {}).items()})
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    print("== stage 0 + basin %s at the %s pad: %s in %.0f ms; basins %s; pieces cut %s; kills %s; alive cells %s; caps %s; forced H %s%s" % (
        nid, pad, out["verdict"], 1000 * out["seconds"], [(b["cell"], b["r_c"]) for b in out["basins"]], out["basin_pieces_cut"],
        {k: v["kills"] for k, v in out["kills"].items()}, slim["alive_cells"], out.get("caps"), out.get("forced_H"), ("; " + str(out["leaf"])) if out["leaf"] else ""), flush=True)
    return out


if __name__ == "__main__":
    import run206
    run206.belownormal()
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "g1")
