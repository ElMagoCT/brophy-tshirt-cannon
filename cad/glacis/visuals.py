"""Show-off visuals for the Onshape model (Micah 2026-11-11: "add visuals like the smoke under and coming out and
t-shirts moving and shapes to represent the light behind the windows and a headlight beam that are suppressable via
configuration. make them organic. make a fake floor too").

None of this is hardware: it is exported as its own "Visuals" tab, never goes into PARTS (so no interference, sweep,
print, mass or parts-list checks see it), and every piece is named by kind so the Onshape configuration can hide each
kind. The gun visuals sit at the export pose (gun level, 0 deg), like the gun itself in Onshape.

SHOW below turns kinds on and off for the export too."""
import math
import cadquery as cq
from cadquery import Vector as V

import params as P
from lib import union

SHOW = dict(floor=True, smoke=True, shirts=True, glow=True, beam=True)

COL = {"floor": (0.62, 0.50, 0.36, 1.0),          # gym maple
       "smoke": (0.93, 0.94, 0.96, 0.45),
       "shirt_w": (0.97, 0.97, 0.97, 1.0), "shirt_r": (0.62, 0.08, 0.16, 1.0), "shirt_b": (0.10, 0.20, 0.45, 1.0),
       "band": (0.08, 0.08, 0.09, 1.0),
       "glow_g": (0.15, 0.95, 0.65, 0.55), "glow_v": (0.55, 0.30, 1.00, 0.50),
       "beam": (1.00, 0.96, 0.75, 0.22)}


def _rng(seed):
    """Small deterministic random (the export must not change run to run)."""
    s = [seed * 2654435761 % 2 ** 32 or 1]

    def r(a=0.0, b=1.0):
        s[0] = (1103515245 * s[0] + 12345) % 2 ** 31
        return a + (b - a) * s[0] / 2 ** 31
    return r


def _cloud(path, r0, r1, seed, per=5, spread=0.6, zmin=None):
    """Organic puff: overlapping spheres along a path, growing from r0 to r1, jittered so it billows."""
    rnd = _rng(seed)
    balls = []
    n = len(path)
    for i, p in enumerate(path):
        t = i / max(1, n - 1)
        r = r0 + (r1 - r0) * t
        for k in range(per):
            rr = r * rnd(0.55, 1.0)
            off = V(rnd(-1, 1), rnd(-1, 1), rnd(-0.6, 1)) * (r * spread)
            c = V(*p) + off
            if zmin is not None and c.z - rr < zmin:
                c = V(c.x, c.y, zmin + rr * 0.92)
            balls.append(cq.Solid.makeSphere(rr, c, angleDegrees1=-90, angleDegrees2=90))
    return union(balls).clean()


def _shirt(c, axis, seed):
    """A rolled t-shirt: fat in the middle, tapered ends, a slight bend, two rubber bands."""
    rnd = _rng(seed)
    L = 165.0
    secs = []
    for k, (t, r) in enumerate(((0.0, 26.0), (0.18, 36.0), (0.5, 41.0), (0.82, 35.0), (1.0, 25.0))):
        bend = math.sin(t * math.pi) * 8.0
        z = (t - 0.5) * L
        secs.append(cq.Wire.makeCircle(r * rnd(0.95, 1.05), V(bend, 0, z), V(0, 0, 1)))
    body = cq.Solid.makeLoft(secs, True)
    bands = [cq.Solid.makeTorus(40.5, 2.4, V(math.sin(t * math.pi) * 8.0, 0, (t - 0.5) * L), V(0, 0, 1))
             for t in (0.33, 0.67)]
    a = V(*axis).normalized()
    z = V(0, 0, 1)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, z.dot(a)))))
    ax = z.cross(a)
    out = []
    for s in [body] + bands:
        if ang > 0.01 and ax.Length > 1e-6:
            s = s.rotate(V(0, 0, 0), ax, ang)
        out.append(s.translate(V(*c)))
    return out[0], union(out[1:])


def _panel_glow(panel, seed):
    """An aurora ribbon just behind one acrylic panel, clipped to the panel's outline."""
    f = max(panel.Faces(), key=lambda f: f.Area())
    n = f.normalAt()
    c = f.Center()
    out = V(c.x, c.y, c.z - 400.0)                  # outward = away from the robot's middle
    if n.dot(c - V(0, 0, 400.0)) < 0:
        n = -n
    up = V(0, 0, 1) if abs(n.z) < 0.8 else V(1, 0, 0)
    u = up.cross(n).normalized()
    v = n.cross(u).normalized()
    us = [(p - c).dot(u) for p in [V(*x.toTuple()) for x in f.Vertices()]]
    vs = [(p - c).dot(v) for p in [V(*x.toTuple()) for x in f.Vertices()]]
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    rnd = _rng(seed)
    ribbons = []
    for k, (vm, amp, th) in enumerate(((0.15, 0.18, 0.10), (-0.18, 0.14, 0.07))):
        ph = rnd(0, 6.28)
        top, bot = [], []
        N = 40
        for i in range(N + 1):
            t = i / N
            uu = u0 + (u1 - u0) * (0.08 + 0.84 * t)
            mid = (v0 + v1) / 2 + (v1 - v0) * (vm + amp * math.sin(2.2 * math.pi * t + ph))
            w = (v1 - v0) * th * (0.35 + math.sin(math.pi * t) ** 0.8)
            top.append((uu, mid + w / 2))
            bot.append((uu, mid - w / 2))
        pts = top + bot[::-1]
        base = c - n * 10.0                          # 10 mm behind the acrylic's outer face
        w3 = cq.Wire.makePolygon([base + u * a + v * b for a, b in pts], close=True)
        rib = cq.Solid.extrudeLinear(cq.Face.makeFromWires(w3), -n * 2.0)
        clip = cq.Solid.extrudeLinear(f.translate(-n * 6.0), -n * 10.0)    # the panel's outline, behind it
        rib = rib.intersect(clip)
        if rib.Volume() > 1.0:
            ribbons.append(("glow_g" if k == 0 else "glow_v", rib))
    return ribbons


def build(parts):
    """(name, shape, color) for every visual. `parts` is the built robot (for panels)."""
    out = []
    zf = 0.0                                          # wheels touch z 0
    if SHOW["floor"]:
        fl = cq.Workplane("XY").box(3800, 2600, 12, centered=(True, True, False)).edges("|Z").fillet(300).val()
        out.append(("Visual floor", fl.translate(V(700, 0, zf - 12.0)), COL["floor"]))
    if SHOW["smoke"]:
        zb = P.BELLY_Z - P.PLATE_T
        (fx, fy), (rx, ry) = P.FOG_VENTS
        front = [(fx, fy, zb - 25), (fx + 60, fy + 20, 70), (fx + 160, fy + 60, 55), (fx + 300, fy + 110, 60),
                 (fx + 460, fy + 170, 75)]
        out.append(("Visual smoke front", _cloud(front, 28, 85, 3, zmin=zf), COL["smoke"]))
        rear = [(rx, ry, zb - 25), (rx - 120, ry, 60), (rx - 280, ry - 20, 50), (rx - 430, ry - 50, 55),
                (rx - 600, ry - 90, 70), (rx - 780, ry - 140, 85)]
        out.append(("Visual smoke rear trail", _cloud(rear, 30, 95, 7, zmin=zf), COL["smoke"]))
        for k, (z0, sd) in enumerate(((707.0, 11), (605.0, 13))):
            muz = [(1065 + 45 * i, 0, z0 + 6 * i * i) for i in range(6)]
            out.append((f"Visual smoke muzzle {'top' if k == 0 else 'bottom'}", _cloud(muz, 30, 70, sd, per=4),
                        COL["smoke"]))
    if SHOW["shirts"]:
        for k, (z0, ds, cols) in enumerate(((707.0, (480.0, 1020.0, 1600.0), ("shirt_w", "shirt_r", "shirt_b")),
                                             (605.0, (760.0,), ("shirt_r",)))):
            for i, (col, d) in enumerate(zip(cols, ds)):
                x, z = 1056.0 + d, z0 - 0.00004 * d * d                     # a slight drop along the shown span
                tilt = 15.0 + 55.0 * i + 30.0 * k                       # tumbling
                ax = (math.cos(math.radians(tilt)), 0.25 * (i - 1), math.sin(math.radians(tilt)))
                body, bands = _shirt((x, 0, z), ax, 21 + 5 * i + 17 * k)
                tag = f"{'top' if k == 0 else 'bottom'} {i + 1}"
                out.append((f"Visual t-shirt {tag}", body, COL[col]))
                out.append((f"Visual t-shirt band {tag}", bands, COL["band"]))
    if SHOW["glow"]:
        for p in parts:
            if p["name"].startswith("Panel ") and not p["name"].startswith("Panel clip"):
                for k, (cn, rib) in enumerate(_panel_glow(p["shape"], len(out) + 31)):
                    out.append((f"Visual window glow {p['name'][6:8]} {k + 1}", rib, COL[cn]))
    if SHOW["beam"]:
        x0, zc = 384.0, 246.0
        secs = []
        for k, (dx, w, h, dz) in enumerate(((0, 300, 40, 0), (700, 700, 220, -25), (1700, 1250, 420, -80),
                                              (2600, 1700, 560, -135))):
            pts = []
            for i in range(36):
                a = 2 * math.pi * i / 36
                wob = 1.0 + (0.05 * math.sin(3 * a + k) if k else 0.0)
                pts.append(V(x0 + dx, w / 2 * math.cos(a) * wob, zc + dz + h / 2 * math.sin(a) * wob))
            secs.append(cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)]))
        beam = cq.Solid.makeLoft(secs, False)
        floor_cut = cq.Solid.makeBox(6000, 4000, 2000, V(-1000, -2000, zf - 2000.0))
        out.append(("Visual headlight beam", beam.cut(floor_cut), COL["beam"]))
    return out
