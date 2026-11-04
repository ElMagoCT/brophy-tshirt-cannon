"""Section views of the LED bands from the exported STEPs (frame grey, strips red), to check that no strip runs into
another or into a web. Run from cad/glacis after robot.py has exported: ../.venv/bin/python render/led_sections.py"""
import math
import os
import sys

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import params as P  # noqa: E402

STEP = os.path.join(HERE, "..", "out", "step")
frame = [cq.importers.importStep(os.path.join(STEP, f)).val() for f in sorted(os.listdir(STEP))
         if f.startswith("body_frame") and f.endswith(".step")]
frame.append(cq.importers.importStep(os.path.join(STEP, "body_panels_clips.step")).val())
lights = [cq.importers.importStep(os.path.join(STEP, f)).val() for f in os.listdir(STEP)
          if f.startswith("lights_speakers") and f.endswith(".step")]
strips = [s for L in lights for s in L.Solids()
          if s.BoundingBox().xlen < 2000]          # every solid in the lights tabs; the LED loops are the red ones


def cut(shapes, origin, normal):
    """Section edges of the shapes with the plane, as polylines."""
    pl = cq.Face.makePlane(4000, 4000, cq.Vector(*origin), cq.Vector(*normal))
    out = []
    for s in shapes:
        sec = BRepAlgoAPI_Section(s.wrapped, pl.wrapped)
        sec.Build()
        for e in cq.Shape.cast(sec.Shape()).Edges():
            out.append([e.positionAt(t / 12) for t in range(13)])
    return out


def view(name, origin, normal, xdir, box):
    o, n, x = cq.Vector(*origin), cq.Vector(*normal).normalized(), cq.Vector(*xdir).normalized()
    y = n.cross(x)
    fig, ax = plt.subplots(figsize=(6, 6))
    for shapes, col in ((frame, "0.45"), (strips, "red")):
        for poly in cut(shapes, origin, normal):
            ax.plot([(p - o).dot(x) for p in poly], [(p - o).dot(y) for p in poly], color=col, lw=0.8)
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    ax.set_aspect("equal")
    ax.set_title(name, fontsize=9)
    ax.grid(alpha=0.2)
    fig.savefig(os.path.join(HERE, f"sec_{name}.png"), dpi=110, bbox_inches="tight")
    plt.close(fig)


# deck-to-side corner (along x): plane x = -40, looking forward
yS = P.FW / 2 + P.MEM_H
view("deck_side", (-40.0, 0, 0), (1, 0, 0), (0, 1, 0), (yS - 140, yS + 20, P.Z_TOP - 130, P.Z_TOP + 20))
# front-to-deck corner (along y): plane y = 200
view("front_deck", (0, 200.0, 0), (0, 1, 0), (1, 0, 0), (P.X_TOP_FRONT - 120, P.X_TOP_FRONT + 40, P.Z_TOP - 130, P.Z_TOP + 20))
# near the front-deck-side corner: plane x = X_TOP_FRONT - 60
view("deck_side_front", (P.X_TOP_FRONT - 60, 0, 0), (1, 0, 0), (0, 1, 0), (yS - 140, yS + 20, P.Z_TOP - 130, P.Z_TOP + 20))
print("sections written")
