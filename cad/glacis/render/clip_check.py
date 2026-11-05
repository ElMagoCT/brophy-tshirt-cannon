"""Every panel's clips drawn flat in the panel's plane: the frame face outline, the acrylic's outline and each clip,
with how much of each clip laps the acrylic. A clip that doesn't lap the acrylic holds nothing. From cad/glacis:
    ../.venv/bin/python render/clip_check.py          # writes out/clip_check.png
"""
import os
import sys

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import params as P  # noqa: E402
import body as B  # noqa: E402
import gun  # noqa: E402

gun.build(lambda *a: None)
B.set_slot_profile(gun.sweep_profile())
solid = B.body_solid()
B.FACES[:] = B.face_info(solid)
panels = [dict(poly=poly, n=fi["n"]) for fi in B.face_info(solid) for poly in B.panels_for(fi)]
reb = P.MEM_W - P.REBATE_W
fig, axs = plt.subplots(2, 4, figsize=(20, 10))
bad = []
for i, (p, ax) in enumerate(zip(panels, axs.flat)):
    clips = B.corner_clips(p)
    pl, pts = B._wp_on(p["poly"], p["n"])
    glass = B.slab(p["poly"], p["n"], reb + P.PANEL_GAP, 0.0, P.CLIP_T, P.ACRYLIC_R)
    loc = lambda v: ((v - pl.origin).dot(pl.xDir), (v - pl.origin).dot(pl.yDir))

    ax.plot([a for a, _ in pts + pts[:1]], [b for _, b in pts + pts[:1]], color="0.3", lw=1)
    top = max(glass.Faces(), key=lambda f: f.Area())
    for e in top.Edges():
        q = [loc(e.positionAt(t / 16)) for t in range(17)]
        ax.plot([a for a, _ in q], [b for _, b in q], color="tab:blue", lw=1)
    for k, c in enumerate(clips):
        lap = c["clip"].intersect(glass).Volume()
        col = "tab:green" if lap >= 120 else "tab:red"
        top_c = max(c["clip"].Faces(), key=lambda f: f.Area())
        for e in top_c.Edges():
            q = [loc(e.positionAt(t / 16)) for t in range(17)]
            ax.plot([a for a, _ in q], [b for _, b in q], color=col, lw=1.4)
        x, y = loc(top_c.Center())
        ax.annotate(f"{k}: {lap:.0f}", (x, y), fontsize=7, color=col)
        if lap < 120:
            bad.append(f"panel {i:02d} clip {k}: lap {lap:.0f} mm3")
    ax.set_aspect("equal")
    ax.set_title(f"Panel {i:02d} ({B._label(p)}): grey frame face, blue acrylic, clips (lap mm3)", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "..", "out", "clip_check.png"), dpi=70)
print("dropped corners:", B.corner_clips.dropped or "none")
print("clips not lapping the acrylic:", bad or "none")
