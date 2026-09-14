"""A213 -- the runtime patch (NO edit on disk of the read-only libraries, the mbpatch178 pattern) that routes the K'
build through integer space:  polycore.build -> polycore_fast.build (the float pipeline, bit-identical, vectorised),
polycore.vertex_ok -> polycore_int.vertex_ok (also what A135 exactcore.a_ok calls), multibox.pieces_poly /
axis_core_pieces / certify_verts -> the polycore_int drop-ins.  `MBox.rebuild` itself is untouched: it looks these
names up in its module at call time, so the memo (fastclip211), the empty-K' handling (mbpatch178) and the coarse grid
(coarse211) stack on top exactly as before.

Flags:  A213_INTCORE=0 turns the patch off (the library runs as before);  A213_VERIFY=1 runs BOTH builds on every
call and asserts the results equal (the differential test, live);  A213_VEC=1 routes the vertex certification through
polycore_vec (Phase 2, itself falling back to the exact integer path wherever the float filter cannot decide).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import polycore_int as PI                                      # noqa: E402
import pinclip_int as PIC                                      # noqa: E402  (A213b: the rectangle-obstacle clip)
import polycore_fast as PF                                     # noqa: E402
import multibox as MB                                          # noqa: E402  READ-ONLY (A171)
import polycore as PC                                          # noqa: E402  READ-ONLY (A132)

FLAG = os.environ.get("A213_INTCORE", "1") != "0"      # default ON: the replay of 441 rebuilds + the fuzz passed with 0 mismatches
VERIFY = os.environ.get("A213_VERIFY") == "1"
VEC = os.environ.get("A213_VEC", "0") == "1"
FLAGC = os.environ.get("A213_INTCLIP", "0") == "1"     # A213b: OFF until the replay + fuzz pass (flipped ON below)
ORIG = dict(build=PC.build, vertex_ok=PC.vertex_ok, pieces_poly=MB.pieces_poly,
            axis_core_pieces=MB.axis_core_pieces, certify_verts=MB.certify_verts,
            clip=MB._clip_rect_obstacle)
INSTALLED = [False]
CLIP_AT = [None]
STATS = dict(build=0, vertex_ok=0, pieces_poly=0, axis_core=0, certify=0, clip=0, verified=0)


def _same_pc(a, b):
    return (list(getattr(a, "verts", ())) == list(getattr(b, "verts", ())) and getattr(a, "shrink", None) == getattr(b, "shrink", None)
            and getattr(a, "n_grid", None) == getattr(b, "n_grid", None))


def _err(f, *a, **kw):
    try:
        return ("ok", f(*a, **kw))
    except Exception as e:                                     # noqa: BLE001
        return ("err", type(e).__name__, str(e))


def _verified(name, new, old, same):
    def g(*a, **kw):
        r = _err(new, *a, **kw)
        s = _err(old, *a, **kw)
        STATS["verified"] += 1
        ok = (r[0] == s[0]) and (same(r[1], s[1]) if r[0] == "ok" else r[1:] == s[1:])
        assert ok, "A213 VERIFY %s: int %r != lib %r" % (name, r[:3], s[:3])
        if r[0] == "err":
            new(*a, **kw)                                      # re-raise the same exception
        return r[1]
    g.__name__ = name
    return g


def _counted(name, f):
    def g(*a, **kw):
        STATS[name] += 1
        return f(*a, **kw)
    g.__name__ = f.__name__
    return g


def _verified_clip(new, old):
    """the clip's differential wrapper: `stats` and `trace` are MUTATED, so the library gets copies."""
    def g(rect, obs, bn, stats, trace=None, tag=""):
        s2 = dict(stats)
        n0 = 0 if trace is None else len(trace)
        out = new(rect, obs, bn, stats, trace=trace, tag=tag)
        t2 = None if trace is None else []
        ref = old(rect, obs, bn, s2, trace=t2, tag=tag)
        STATS["verified"] += 1
        assert ref == out and s2 == stats and (t2 is None or t2 == trace[n0:]), (
            "A213 VERIFY clip: int %r %r != lib %r %r" % (out, stats, ref, s2))
        return out
    g.__name__ = "clip_rect_obstacle"
    return g


def install_clip(verify=None):
    """A213b: route `_clip_rect_obstacle` to the integer-space clip.  A211's clip MEMO (fastclip211) captured the
    library function at ITS import, so when the memo is installed the patch goes into `fastclip211._ORIG_CLIP` (the
    memo's miss path) and the memo stays on top; otherwise straight into the multibox global."""
    if not FLAGC:
        return False
    verify = VERIFY if verify is None else verify
    clip = PIC.clip_rect_obstacle
    if verify:
        clip = _verified_clip(clip, ORIG["clip"])
    clip = _counted("clip", clip)
    where = []
    FC = sys.modules.get("fastclip211")
    if FC is not None and getattr(FC, "_ORIG_CLIP", None) is ORIG["clip"]:
        FC._ORIG_CLIP = clip
        where.append("fastclip211._ORIG_CLIP")
    if MB._clip_rect_obstacle is ORIG["clip"]:
        MB._clip_rect_obstacle = clip
        where.append("multibox._clip_rect_obstacle")
    CLIP_AT[0] = " + ".join(where) or None
    return bool(where)


def _pp_same(a, b):
    return a[0] == b[0] and a[1] == b[1] and [(x.x0, x.x1, x.y0, x.y1, y, z) for x, y, z in a[2]] == \
        [(x.x0, x.x1, x.y0, x.y1, y, z) for x, y, z in b[2]]


def install(verify=None, vec=None):
    """route the library's names to the integer-space build (idempotent).  Returns True when installed."""
    verify = VERIFY if verify is None else verify
    vec = VEC if vec is None else vec
    if not FLAG:                                               # A213 off, A213b still available on its own flag
        return install_clip(verify)
    build, vok, pp, ac, cv = PF.build, PI.vertex_ok, PI.pieces_poly, PI.axis_core_pieces, PI.certify_verts
    if vec:
        import polycore_vec as PV
        cv = PV.certify_verts
    if verify:
        build = _verified("build", build, ORIG["build"], _same_pc)
        vok = _verified("vertex_ok", vok, ORIG["vertex_ok"], lambda a, b: a == b)
        pp = _verified("pieces_poly", pp, ORIG["pieces_poly"], _pp_same)
        ac = _verified("axis_core_pieces", ac, ORIG["axis_core_pieces"], lambda a, b: a == b)
        cv = _verified("certify_verts", cv, ORIG["certify_verts"], lambda a, b: a == b)
    PC.build = _counted("build", build)
    PC.vertex_ok = _counted("vertex_ok", vok)
    MB.pieces_poly = _counted("pieces_poly", pp)
    MB.axis_core_pieces = _counted("axis_core", ac)
    MB.certify_verts = _counted("certify", cv)
    install_clip(verify)
    INSTALLED[0] = True
    return True


def uninstall():
    FC = sys.modules.get("fastclip211")
    if FC is not None and getattr(FC, "_ORIG_CLIP", None) is not ORIG["clip"]:
        FC._ORIG_CLIP = ORIG["clip"]
    MB._clip_rect_obstacle = ORIG["clip"]
    CLIP_AT[0] = None
    PC.build, PC.vertex_ok = ORIG["build"], ORIG["vertex_ok"]
    MB.pieces_poly, MB.axis_core_pieces, MB.certify_verts = ORIG["pieces_poly"], ORIG["axis_core_pieces"], ORIG["certify_verts"]
    INSTALLED[0] = False


def rep():
    return dict(installed=INSTALLED[0], flag=FLAG, flag_clip=FLAGC, clip_at=CLIP_AT[0],
                verify=VERIFY, vec=VEC, **STATS)
