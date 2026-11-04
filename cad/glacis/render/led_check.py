"""Fast LED check without the full robot build: panels, window insets, webs and strips, then every strip against the
other strips and webs and the frame shell, plus section views of three corners. From cad/glacis:
    ../.venv/bin/python render/led_check.py"""
import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import params as P  # noqa: E402
import body as B  # noqa: E402
from lib import union  # noqa: E402

t0 = time.time()
import gun  # noqa: E402
gun.build(lambda *a: None)
B.set_slot_profile(gun.sweep_profile())
solid = B.body_solid()
B.FACES[:] = B.face_info(solid)
shell = solid.cut(B.inner_solid()).clean()
panels = [dict(poly=poly, n=fi["n"]) for fi in B.face_info(solid) for poly in B.panels_for(fi)]
B.edge_kinds(panels, print)
B._settle_insets(panels, shell, print)
rest = shell.cut(union([B._window_prism(p) for p in panels]))
webs = [B.led_web(p) for p in panels]
strips = [B.led_loop(p)[0] for p in panels]
print(f"built in {time.time() - t0:.0f} s")

bad = 0
for i, s in enumerate(strips):
    if s is None:
        continue
    for j, o in enumerate(strips[:i]):
        if o is not None and s.intersect(o).Volume() > 1.0:
            v = s.intersect(o)
            c = v.BoundingBox().center
            print(f"strip/strip {B._label(panels[j])} x {B._label(panels[i])}: {v.Volume():.0f} mm3 at ({c.x:.0f}, {c.y:.0f}, {c.z:.0f})")
            bad += 1
    for j, w in enumerate(webs):
        if j != i and w is not None:
            v = s.intersect(w)
            if v.Volume() > 1.0:
                c = v.BoundingBox().center
                print(f"strip {B._label(panels[i])} into web {B._label(panels[j])}: {v.Volume():.0f} mm3 at ({c.x:.0f}, {c.y:.0f}, {c.z:.0f})")
                bad += 1
    v = B._robust(s.intersect, rest)
    for x in v.Solids():
        if x.Volume() > 1.0:
            c = x.BoundingBox().center
            print(f"strip {B._label(panels[i])} into frame: {x.Volume():.0f} mm3 at ({c.x:.0f}, {c.y:.0f}, {c.z:.0f})")
            bad += 1
print(f"{bad} contacts; checked in {time.time() - t0:.0f} s")

frame = [rest] + [w for w in webs if w is not None]
reds = [x for x in strips if x is not None]


def cut(shape, o, n):
    pl = cq.Face.makePlane(5000, 5000, o, n)
    sec = BRepAlgoAPI_Section(shape.wrapped, pl.wrapped)
    sec.Build()
    return [[e.positionAt(t / 16) for t in range(17)] for e in cq.Shape.cast(sec.Shape()).Edges()]


def view(name, origin, normal, xdir, box):
    o, n, x = cq.Vector(*origin), cq.Vector(*normal).normalized(), cq.Vector(*xdir).normalized()
    y = n.cross(x)
    fig, ax = plt.subplots(figsize=(5, 5))
    for shapes, col, lw in ((frame, "0.35", 0.7), (reds, "red", 1.2)):
        for poly in [q for sh in shapes for q in cut(sh, o, n)]:
            ax.plot([(p - o).dot(x) for p in poly], [(p - o).dot(y) for p in poly], color=col, lw=lw)
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    ax.set_aspect("equal")
    ax.set_title(name, fontsize=9)
    ax.grid(alpha=0.25)
    fig.savefig(os.path.join(HERE, f"sec_{name}.png"), dpi=100, bbox_inches="tight")
    plt.close(fig)


yd = max(v.Y for v in solid.Vertices() if abs(v.Z - P.Z_TOP) < 1.0)      # deck edge at the side
xr = min(v.X for v in solid.Vertices() if abs(v.Z - P.Z_TOP) < 1.0)      # deck edge at the rear
xf = P.front_x(300.0)
ys = max(q.y for poly in cut(rest, cq.Vector(0, 0, 300.0), cq.Vector(0, 0, 1)) for q in poly)
view("deck_side_x-40", (-40.0, 0, 0), (1, 0, 0), (0, 1, 0), (yd - 70, yd + 10, P.Z_TOP - 70, P.Z_TOP + 10))
view("deck_side_x-105_seam", (-105.0, 0, 0), (1, 0, 0), (0, 1, 0), (yd - 70, yd + 10, P.Z_TOP - 70, P.Z_TOP + 10))
view("deck_rear_y190", (0, 190.0, 0), (0, 1, 0), (-1, 0, 0), (-xr - 70, -xr + 10, P.Z_TOP - 70, P.Z_TOP + 10))
view("front_side_z300", (0, 0, 300.0), (0, 0, 1), (1, 0, 0), (xf - 80, xf + 15, ys - 80, ys + 15))
print("sections written", f"{time.time() - t0:.0f} s")
