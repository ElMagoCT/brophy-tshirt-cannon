"""Gun cradle plate outline + lightening (Brophy Borealis, Micah 2026-11-10: "combine chevron and turret wheel. make
the wheel chevrons"). Built flat in XY (x = along the gun, y = gun z) as a thin solid, PLATE_T thick in +Z; gun.py
turns it into the XZ plane at each side and drills the functional holes.

Outline: the Chevron concept's swallowtail back and pointed nose, with the Turret wheel's round boss round the pivot
breaking the top and bottom edges. Pockets: forward-pointing chevrons in the bays between the saddles and ahead of
the wheel, and a wheel of outward-pointing chevrons round the pivot. Every pocket is clipped so solid material stays
at the pivot boss, the 112T ring's standoff pads, the saddles, the breech block, the top rail, the valve-block pads,
the tie bolts and a 10 mm rim, with 6 mm webs and 5 mm corner rounds."""
import math
import cadquery as cq
from cadquery import Vector as V

WEB, RIM, ROUND = 3.0, 10.0, 4.0           # half-web (pockets shrink by this), rim, corner round


def _poly(pts, t):
    q = []
    for p in pts:
        if not q or math.hypot(p[0] - q[-1][0], p[1] - q[-1][1]) > 0.05:
            q.append(p)
    if math.hypot(q[0][0] - q[-1][0], q[0][1] - q[-1][1]) < 0.05:
        q.pop()
    return cq.Workplane("XY").polyline(q).close().extrude(t).val()


def _circle(x, z, r, t):
    return cq.Workplane("XY").center(x, z).circle(r).extrude(t).val()


def _box(x0, x1, z0, z1, t):
    return _poly([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], t)


def _union(shapes):
    s = shapes[0]
    for o in shapes[1:]:
        s = s.fuse(o)
    return s.clean()


def _face_solid(face, t):
    return cq.Workplane("XY").add(face).wires().toPending().extrude(t).val()


def _bottom_wire(s):
    return min(s.Faces(), key=lambda f: f.Center().z).outerWire()


def chevron(x, w, zt, th, t):
    """Chevron pointing +x: apex at x + w (+ th), arms to (x, +-zt), th thick along x."""
    return _poly([(x, zt), (x + w, 0), (x, -zt), (x + th, -zt), (x + w + th, 0), (x + th, zt)], t)


def radial_chevron(ang, r0, r1, half, th, t):
    """Chevron pointing outward along angle ang (deg): apex at r1, arms back to r0 at +-half (mm, tangential)."""
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    loc = [(r0, half), (r1, 0), (r0, -half), (r0 - th, -half), (r1 - th, 0), (r0 - th, half)]
    return _poly([(u * c - v * s, u * s + v * c) for u, v in loc], t)


SIDE_W, SIDE_TH = 22.0, 16.0                  # side chevrons: depth (arm sweep), slot width before the webs
N_REAR, N_FRONT = 3, 3                         # Micah: "go 3 and 3" (they can be broken up by the pads)
WHEEL_REAR, FRONT0 = -72.0, 70.0               # rear row stops short of the wheel; the front row starts here
REAR0 = 44.0                                   # rear row start behind x0 (clear of the V-shaped rear chamber holder)


def _row(xa, xb, n, w):
    """n chevrons spread evenly from xa to xb (each spans w + SIDE_TH)."""
    if n == 1:
        return [xa + (xb - xa - w - SIDE_TH) / 2]
    p = (xb - xa - w - SIDE_TH) / (n - 1)
    return [xa + k * p for k in range(n)]


def layout(x0, zo, saddles, breech_x0):
    rear = _row(x0 + REAR0, WHEEL_REAR, N_REAR, SIDE_W)            # starts ahead of the rear chamber holder
    front = _row(FRONT0, breech_x0 - 6, N_FRONT, 18.0)
    return dict(rear=rear, front=front, w_front=18.0, zt_rear=zo - 28, zt_front=zo - 16,
                pitch=rear[1] - rear[0] if len(rear) > 1 else 0.0)


def saddle_screws(saddles, lay):
    """Two screw points per saddle on the web centre line between rear chevrons (+-z)."""
    zt, g = lay["zt_rear"], lay["pitch"] - SIDE_TH
    out = []
    for xs in saddles:
        best = None
        for xk in lay["rear"]:
            u = xs - xk - SIDE_TH - g / 2                       # how far the web centre must sweep back at this z
            z = zt * (1 - u / SIDE_W)
            if 12 <= z <= zt - 10 and (best is None or abs(z - 0.5 * zt) < abs(best - 0.5 * zt)):
                best = z
        z = best if best is not None else 0.5 * zt
        out += [(xs, z), (xs, -z)]
    return out


def rear_edge_x(x0, zo, z):
    """x of the plate's swallowtail back edge at height z."""
    return x0 + 10 - 50 * abs(z) / (zo - 6)


def plate_2d(t, x0, x1, zo, saddles, breech_x0, rail, keep_pts, standoffs, r_boss_keep=46.0):
    """The plate as a thin solid in XY. keep_pts: [(x, z, r)] extra solid pads; standoffs: [(x, z)] ring pads."""
    zb = zo + 6.0                                                   # turret boss radius
    outline = _union([
        _poly([(x0 - 40, zo - 6), (x0 + 10, 0), (x0 - 40, -zo + 6), (x1 - 40, -zo), (x1 + 10, -zo + 40),
               (x1 + 10, zo - 40), (x1 - 40, zo)], t),
        _circle(0, 0, zb, t)])
    # pockets (Micah: "just 1 set in the ring. increase the ones on the sides")
    lay = layout(x0, zo, saddles, breech_x0)
    pk = [chevron(x, SIDE_W, lay["zt_rear"], SIDE_TH, t) for x in lay["rear"]]
    pk += [chevron(x, lay["w_front"], lay["zt_front"], SIDE_TH, t) for x in lay["front"]]
    for a in (50, 120, 240, 310):                                  # the wheel: an X of chevrons between the ring standoffs
        pk.append(radial_chevron(a, 72, 102, 30, 28, t))
    # webs
    shr = []
    for q in pk:
        w = _bottom_wire(q).offset2D(-WEB, "intersection")
        if w:
            shr.append(_face_solid(cq.Face.makeFromWires(w[0]), t))
    pk = _union(shr)
    # rim
    rim = _face_solid(cq.Face.makeFromWires(_bottom_wire(outline).offset2D(-RIM, "arc")[0]), t)
    keep = [_circle(0, 0, r_boss_keep, t)]
    keep += [_circle(x, z, 9.0, t) for x, z in standoffs]
    keep.append(_box(breech_x0 - 6, x1 + 60, -zo - 60, zo + 60, t))
    keep.append(_box(rail[0] - 6, rail[1] + 6, zo - 26, zo + 60, t))
    keep += [_circle(x, z, r, t) for x, z, r in keep_pts]
    pk = pk.intersect(rim).cut(_union(keep))
    rounded = []
    for s in pk.Solids():
        try:
            e = _bottom_wire(s).offset2D(-ROUND, "arc")
            if not e:
                continue
            f = cq.Face.makeFromWires(e[0].offset2D(ROUND, "arc")[0])
        except Exception:                                           # rounding failed on an odd piece: cut it unrounded
            f = min(s.Faces(), key=lambda f: f.Center().z)
        if f.Area() > 150:
            rounded.append(_face_solid(f, t + 0.02).translate(V(0, 0, -0.01)))
    return outline.cut(_union(rounded)) if rounded else outline


def to_side(s2d, y0):
    """XY thin solid (thickness +Z) -> XZ plane with thickness y0 .. y0 + t."""
    t = s2d.BoundingBox().zlen
    return s2d.rotate(V(0, 0, 0), V(1, 0, 0), 90).translate(V(0, y0 + t, 0))
