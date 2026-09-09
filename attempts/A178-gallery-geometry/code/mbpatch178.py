"""A178 -- a runtime patch (NO edit on disk) of A171's multibox for roles whose K' is EMPTY.

A forced-meeter role is carried as its whole meeter window (about 1.2 x 2.2 x 90 deg): no point
lies in every pose, so A132's `polycore.build` finds no certified polygon and raises.  The sound
semantics of an empty K' is "this box clips nothing" -- (DISJOINT) says a pose of A meeting
int K'(B) is impossible, and int(empty) is empty -- while the box itself is still clipped by the
container and by every other role's K'.  The patch: `MBox.rebuild` catches the failure and installs
an EMPTY core (`EmptyPC`, verts (), area 0, core None); `MBox.obstacle` returns None for it;
`_clip_rect_obstacle` leaves a rect untouched by a None obstacle; `polys_disjoint_exact` treats an
empty polygon as disjoint from everything; `polycore.poly_square_depth` on an empty polygon is
-1 (no meeting).  Everything else in the library is unchanged, and a box whose K' becomes
non-empty once its poses are localised is rebuilt by the ORIGINAL code path.
"""
import numpy as np

import multibox as MB
import polycore as PC


class EmptyPC:
    __slots__ = ("box", "verts", "P", "certified")

    def __init__(self, box):
        self.box = box
        self.verts = ()
        self.P = np.zeros((0, 2))
        self.certified = True

    def area(self):
        return 0.0


_orig_rebuild = MB.MBox.rebuild
_orig_obstacle = MB.MBox.obstacle
_orig_clip = MB._clip_rect_obstacle
_orig_disjoint = MB.polys_disjoint_exact
_orig_depth = PC.poly_square_depth


def rebuild(self, *a, **kw):
    try:
        return _orig_rebuild(self, *a, **kw)
    except RuntimeError as e:
        if "no certified polygon" not in str(e):
            raise
        b = self.union_box()
        if b is None:
            raise MB.EmptyBox(self.name)
        self.ubox = b
        self.pc = EmptyPC(b)
        self.core = None
        self.k_source, self.k_info = "empty", dict(reason="no certified polygon (K' empty)")
        return self.pc


def obstacle(self, mode="poly"):
    if isinstance(self.pc, EmptyPC) or (mode == "core" and self.core is None):
        return None
    return _orig_obstacle(self, mode)


def clip_rect_obstacle(rect, obs, bn, stats, trace=None, tag=""):
    if obs is None:
        return rect
    return _orig_clip(rect, obs, bn, stats, trace=trace, tag=tag)


def polys_disjoint_exact(V1, V2):
    if len(V1) < 3 or len(V2) < 3:
        return True, None, None
    return _orig_disjoint(V1, V2)


def poly_square_depth(P, C, TH):
    P = np.asarray(P, float)
    if P.shape[0] < 3:
        return -np.ones(np.asarray(C, float).reshape(-1, 2).shape[0])
    return _orig_depth(P, C, TH)


def install():
    MB.MBox.rebuild = rebuild
    MB.MBox.obstacle = obstacle
    MB._clip_rect_obstacle = clip_rect_obstacle
    MB.polys_disjoint_exact = polys_disjoint_exact
    PC.poly_square_depth = poly_square_depth
    MB.PC.poly_square_depth = poly_square_depth
    return True


INSTALLED = install()
