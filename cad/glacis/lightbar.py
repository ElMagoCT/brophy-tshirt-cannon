"""Brophy Borealis front light bar hole (2026-11-10, Micah: "for the front hole, it should start from the bottom and
just be a hole, not plastic frame. inside the hole holding the lightbar, should be aluminum extrusions to mount [the
light] to and potentially other stuff", then "the gap should be from the bumper to 4.5in above the bumper").

The hole is a plain opening in the front slant, open at the bottom: from the body's bottom edge (on the bumper) to
4.5 in above the bumper's top. Its edges are ordinary frame members with no panel and no liner. Two 20x20 T-slot rails
run across it behind the shell, one along its bottom and one along its top, each lying flat on the frame's inner face
and held at each end by an M4 x 8 from inside, through a hole CNC'd across the rail into an insert in the frame
member's inner face. The bar stands on
the lower rail on its own end brackets, aimed straight ahead; the upper rail is free for sensors and the like.

Rail cross-sections are placed in the slant's own frame: p = depth inward from the outer face, q = distance up the
slant from the body's bottom edge.
"""
import math

import cadquery as cq
from cadquery import Vector as V

import params as P
from lib import box, cyl

H = P.BAR_HOLE
_A = math.radians(P.FRONT_ANGLE)
N = V(math.sin(_A), 0, math.cos(_A))                  # the slant's outward normal
U = V(-math.cos(_A), 0, math.sin(_A))                 # up the slant
O = V(P.FRAME_X, 0, P.Z_WALL_BOT)                     # the slant's bottom edge (outer face, y = 0)


def at(p, q, y=0.0):
    """World point p deep and q up the slant."""
    return O - N * p + U * q + V(0, y, 0)


def q_inner(z):
    """q on the frame's inner face at height z."""
    return (z - P.Z_WALL_BOT + P.MEM_H * N.z) / U.z


def z1():
    return P.BUMP_Z[1] + H["height"]


def rails():
    """(name, q0) of each rail: the lower one clear of the body's bottom edge, the upper one level with the hole's top."""
    w = P.RAIL20
    q_lo = (P.Z_WALL_BOT + 1.0 - P.Z_WALL_BOT + (P.MEM_H + w) * N.z) / U.z     # its lowest corner 1 mm above the edge
    return [("lower", q_lo), ("upper", q_inner(z1()) - w)]


def cut():
    """The hole in the body polyhedron: runs out past the front and down past the bottom edge, and back to just behind
    the frame's inner face at its top, so it's a clean opening through the shell."""
    x0 = P.front_x(z1(), inner=True) - 15.0
    return box(x0, P.FRAME_X + 50.0, -H["y"], H["y"], P.Z_WALL_BOT - 60.0, z1())


def cuts():
    return [cut()]


def _plane(y0):
    # extrude along +y; local x = depth inward (p), local y = up the slant (q)
    return cq.Plane(origin=O + V(0, y0, 0), xDir=-N, normal=V(0, 1, 0))


def rail(q0):
    """A 20x20 T-slot rail across the hole, its outer face flat on the frame's inner face (simplified profile: a
    6.2 mm slot 6 deep down each face's middle and the centre bore)."""
    w, L = P.RAIL20, H["rail_len"]
    p0, pc, qc = P.MEM_H, P.MEM_H + w / 2, q0 + w / 2
    wp = cq.Workplane(_plane(-L / 2))
    s = wp.center(pc, qc).rect(w, w).extrude(L).val()
    h, d = 3.1, 6.0
    for cx, cy, sx, sy in ((p0 + d / 2, qc, d + 1, 2 * h), (p0 + w - d / 2, qc, d + 1, 2 * h),
                           (pc, q0 + d / 2, 2 * h, d + 1), (pc, q0 + w - d / 2, 2 * h, d + 1)):
        s = s.cut(cq.Workplane(_plane(-L / 2 - 1)).center(cx, cy).rect(sx, sy).extrude(L + 2).val())
    s = s.cut(cq.Workplane(_plane(-L / 2 - 1)).center(pc, qc).circle(2.1).extrude(L + 2).val())
    return s


def screw_hole(q0, y):
    """The M4 x 4 insert in the frame member's inner face beside the hole, at the rail's middle (the member's light
    tunnel runs near its outer face, so an insert from the inside stays clear of it)."""
    a = at(P.MEM_H + 0.1, q0 + P.RAIL20 / 2, y)
    return cyl(P.INSERT[0], P.INSERT[1], a.toTuple(), N.toTuple())


def rail_holes(q0, y):
    """The rail's CNC'd cross hole for that screw: 4.5 mm through its front wall, 8 mm through its back wall and core
    so the M4 x 8's head sits on the inside of the front wall."""
    qc = q0 + P.RAIL20 / 2
    return cyl(2.25, 4.0, at(P.MEM_H - 1.0, qc, y).toTuple(), (-N).toTuple()).fuse(
        cyl(4.0, P.RAIL20 - 1.8 + 1.0, at(P.MEM_H + 1.8, qc, y).toTuple(), (-N).toTuple()))


def bar_box():
    """(x0, x1, z0, z1) of the bar: just behind the slant at its top edge, clear above the lower rail."""
    L, hb, db, _, _ = P.LIGHT_BAR
    zb0 = H["bar_z"]
    zb1 = zb0 + hb
    xb1 = P.front_x(zb1) - H["recess"]
    return xb1 - db, xb1, zb0, zb1


def bar():
    L = P.LIGHT_BAR[0]
    x0, x1, z0, z1_ = bar_box()
    s = box(x0, x1, -L / 2, L / 2, z0, z1_)
    return s.cut(box(x1 - 2.0, x1 + 1.0, -L / 2 + 14.0, L / 2 - 14.0, z0 + 5.0, z1_ - 5.0))   # one lens strip


def brackets():
    """The bar's own end brackets (they come with it): a foot on the lower rail's top face and an ear up each end
    of the bar, through which its side bolt sets the aim."""
    L = P.LIGHT_BAR[0]
    x0, x1, z0, z1_ = bar_box()
    xc, zc = (x0 + x1) / 2, (z0 + z1_) / 2
    q_top = rails()[0][1] + P.RAIL20                    # the lower rail's top face
    out = []
    for sg in (1, -1):
        ya, yb = sorted([sg * (L / 2 + 0.5), sg * (L / 2 + 3.5)])
        foot = cq.Workplane(_plane(ya)).center(P.MEM_H + P.RAIL20 / 2, q_top + 1.5).rect(16.0, 3.0).extrude(yb - ya).val()
        ear = box(xc - 6.0, xc + 16.0, ya, yb, 226.0, zc + 12.0)        # clear of the front wheels' treads
        below = cq.Workplane(_plane(ya - 1)).center(0, q_top - 500.0 + 3.0).rect(2000.0, 1000.0).extrude(yb - ya + 2).val()
        out.append(foot.fuse(ear.cut(below)).clean())
    return out
