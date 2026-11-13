"""Small geometry kit on top of CadQuery plus the part registry every module adds to."""
import math
import cadquery as cq
from cadquery import Vector as V, Location as Loc

# ------------------------------------------------------------------ colours (r, g, b, a)

_clean = cq.Shape.clean


def _safe_clean(self):
    """Shape.clean (merge coplanar faces) that gives the shape back unmerged when OCC's upgrader trips (it does on
    the LED rails' rounded, twisting faces)."""
    try:
        return _clean(self)
    except Exception:
        return self


cq.Shape.clean = _safe_clean

C = {
    "print":   (0.94, 0.94, 0.95, 1.0),     # white PETG/ASA
    "print_d": (0.22, 0.23, 0.26, 1.0),     # dark PETG-CF / PA-CF (drive, pulleys)
    "tpu":     (0.14, 0.14, 0.15, 1.0),
    "acrylic": (0.97, 0.97, 0.98, 0.55),    # frosted white
    "alu":     (0.74, 0.76, 0.79, 1.0),
    "extr":    (0.80, 0.82, 0.85, 1.0),
    "steel":   (0.42, 0.44, 0.47, 1.0),
    "galv":    (0.62, 0.64, 0.66, 1.0),
    "brass":   (0.80, 0.64, 0.28, 1.0),
    "black":   (0.08, 0.08, 0.09, 1.0),
    "falcon":  (0.16, 0.17, 0.19, 1.0),
    "tank":    (0.12, 0.12, 0.13, 1.0),
    "battery": (0.10, 0.10, 0.11, 1.0),
    "red":     (0.86, 0.10, 0.18, 1.0),
    "belt":    (0.10, 0.10, 0.10, 1.0),
    "foam":    (0.96, 0.96, 0.94, 1.0),
    "wood":    (0.78, 0.62, 0.42, 1.0),
    "fabric":  (0.28, 0.40, 0.62, 0.9),     # denim liner
    "led":     (1.00, 0.12, 0.22, 1.0),
    "pcb":     (0.12, 0.42, 0.30, 1.0),
    "tube":    (0.30, 0.55, 0.85, 1.0),
    "spot":    (0.95, 0.75, 0.20, 0.35),    # reserved volume (compressor spot)
    "pc":      (0.88, 0.93, 0.98, 0.40),    # clear polycarbonate barrel
}

PARTS = []
TUBE_HOLES = []          # (what, point, direction, radius, length): cut through the tubes by brackets.drill_tubes
MEMBERS = []             # 40x40 frame members: dict(name, axis, a0, a1, c1, c2) (extrusion-4040)
FASTENERS = []           # every M5 into the extrusion: dict(kind="tnut"|"endtap", spec, at, d, by) where `at` is the
                         # point on the member face (T-nut) or the member's end face (end tap) and `d` the direction
                         # into the member; checked by brackets.check_fasteners, counted for the hardware list


def fastener(kind, spec, at, d, by, **kw):
    FASTENERS.append(dict(kind=kind, spec=spec, at=tuple(float(c) for c in at), d=tuple(float(c) for c in d), by=by,
                          **kw))


def add(name, shape, color, group, bom=None, kind="cots", moving=False, note="", mass=None, frame=False):
    """Register one part. `bom` groups identical parts on the parts list; `mass` (kg) overrides the
    density estimate for hollow or mixed-material parts. `frame` tags a structural frame member."""
    if isinstance(shape, cq.Workplane):
        shape = shape.val() if len(shape.vals()) == 1 else cq.Compound.makeCompound(shape.vals())
    PARTS.append(dict(name=name, shape=shape, color=C[color] if isinstance(color, str) else color,
                      group=group, bom=bom or name, kind=kind, moving=moving, note=note, mass=mass, frame=frame))
    return shape


def profile4040(simple=False, slot=6.2, lip=1.8, cav=(8.6, 5.5), core=2.1, bore=2.5, off=10.0, chamfer=0.5):
    """40x40 20-series T-slot section in a local (u, v) plane centred on the origin, as a cq.Face: the outline with two
    T-slots per face (6.2 mm opening through a 1.8 mm lip into an 8.6 mm wide cavity, 5.5 mm deep) at +/- `off`, and
    unless `simple`, the four 4.2 mm end-tap cores at (+/-off, +/-off) and the centre bore."""
    h = 20.0
    c = chamfer
    pts = []
    s2, cw = slot / 2, cav[0] / 2
    d1, d2 = h - lip, h - cav[1]

    def face_pts():                                       # one face (the +v face) from u = +h to u = -h
        out = [(h - c, h)]
        for uc in (off, -off):
            out += [(uc + s2, h), (uc + s2, d1), (uc + cw, d1), (uc + cw, d2), (uc - cw, d2), (uc - cw, d1),
                    (uc - s2, d1), (uc - s2, h)]
        out.append((-h + c, h))
        return out
    for k in range(4):                                    # rotate the +v face 90 deg at a time
        ang = math.pi / 2 * k
        ca, sa = math.cos(ang), math.sin(ang)
        pts += [(u * ca - v * sa, u * sa + v * ca) for u, v in face_pts()]
    w = cq.Wire.makePolygon([V(u, v, 0) for u, v in pts], close=True)
    inner = []
    if not simple:
        inner = [cq.Wire.makeCircle(core, V(su * off, sv * off, 0), V(0, 0, 1)) for su in (-1, 1) for sv in (-1, 1)]
        inner.append(cq.Wire.makeCircle(bore, V(0, 0, 0), V(0, 0, 1)))
    return cq.Face.makeFromWires(w, inner)


def ext4040(axis, a0, a1, c1, c2, simple=False):
    """40x40 T-slot extrusion along `axis` ("x", "y" or "z") from a0 to a1, centred at (c1, c2) on the other two axes
    (x, y, z order)."""
    a0, a1 = min(a0, a1), max(a0, a1)
    f = profile4040(simple)
    s = cq.Solid.extrudeLinear(f, V(0, 0, a1 - a0))       # along local z
    org, xd, nd = {"x": ((a0, c1, c2), (0, 1, 0), (1, 0, 0)), "y": ((c1, a0, c2), (0, 0, 1), (0, 1, 0)),
                   "z": ((c1, c2, a0), (1, 0, 0), (0, 0, 1))}[axis]
    return s.moved(cq.Location(cq.Plane(origin=org, xDir=xd, normal=nd)))


# ------------------------------------------------------------------ primitives (return cq.Shape)
def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, h, p=(0, 0, 0), d=(0, 0, 1)):
    """Cylinder of radius r and length h starting at p along direction d."""
    return cq.Solid.makeCylinder(r, h, V(*p), V(*d))


def tube(ro, ri, h, p=(0, 0, 0), d=(0, 0, 1)):
    return cyl(ro, h, p, d).cut(cyl(ri, h + 0.2, tuple(V(*p) - V(*d).normalized() * 0.1), d))


def hex_prism(af, h, p=(0, 0, 0), d=(0, 0, 1)):
    """Hex of across-flats af, length h along d starting at p."""
    r = af / math.sqrt(3)
    w = cq.Workplane(cq.Plane(origin=V(*p), xDir=_perp(V(*d)), normal=V(*d))).polygon(6, 2 * r).extrude(h)
    return w.val()


def _perp(d):
    d = d.normalized()
    a = V(1, 0, 0) if abs(d.x) < 0.9 else V(0, 1, 0)
    return a.cross(d).normalized()


def union(shapes):
    shapes = [s for s in shapes if s is not None]
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def moved(shape, x=0, y=0, z=0, rx=0, ry=0, rz=0):
    """Rotate about X, then Y, then Z (degrees, about the origin), then translate."""
    s = shape
    if rx:
        s = s.rotate(V(0, 0, 0), V(1, 0, 0), rx)
    if ry:
        s = s.rotate(V(0, 0, 0), V(0, 1, 0), ry)
    if rz:
        s = s.rotate(V(0, 0, 0), V(0, 0, 1), rz)
    return s.translate(V(x, y, z))


def mirror_y(shape):
    return shape.mirror("XZ")


def poly_prism(pts, h, plane="XY", offset=0.0):
    """Extrude a 2D polygon (list of (u, v)) by h on a named plane at `offset`."""
    w = cq.Workplane(plane, origin=_plane_origin(plane, offset)).polyline(pts).close().extrude(h)
    return w.val()


def htd_teeth(teeth, width, y0=0.0, x=0.0, z=0.0, pitch=5.0, depth=2.06, groove_r=1.53, steps=10):
    """HTD 5M toothed rim (Micah 2026-11-11: "add teeth to the pulley"), axis along +y from y0, centred at (x, z).
    OD = pitch diameter - 1.14 mm; each groove a 1.53 mm radius arc 2.06 mm deep (the HTD 5M pulley groove), so the
    printed pulley takes a real belt."""
    pd = teeth * pitch / math.pi
    ro = pd / 2 - 0.57
    cg = ro - depth + groove_r                     # groove centre radius
    half = math.asin(min(1.0, groove_r / cg)) if cg > groove_r else math.pi / teeth
    pts = []
    for k in range(teeth):
        a0 = 2 * math.pi * k / teeth
        for j in range(steps + 1):                 # groove: polar curve across the groove's angular width
            phi = -half + 2 * half * j / steps
            s = cg * cg * math.sin(phi) ** 2
            r = ro if s > groove_r ** 2 else min(ro, cg * math.cos(phi) - math.sqrt(groove_r ** 2 - s))
            pts.append((x + r * math.cos(a0 + phi), z + r * math.sin(a0 + phi)))
    w = cq.Wire.makePolygon([V(u, y0, v) for u, v in pts], close=True)
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), V(0, width, 0))


def _plane_origin(plane, off):
    return {"XY": (0, 0, off), "XZ": (0, off, 0), "YZ": (off, 0, 0)}[plane]


def belt_loop(c1, r1, c2, r2, width, y0, t=1.6):
    """Belt between two pulleys in the XZ plane (centres (x, z), pitch radii), width along +Y from y0."""
    (x1, z1), (x2, z2) = c1, c2
    dx, dz = x2 - x1, z2 - z1
    L = math.hypot(dx, dz)
    ang = math.atan2(dz, dx)
    b = math.asin((r1 - r2) / L)

    def ring_pts(off):
        pts = []
        a0, a1 = ang + math.pi / 2 + b, ang + 3 * math.pi / 2 - b      # wrap on pulley 1 (far side)
        for i in range(25):
            a = a0 + (a1 - a0) * i / 24
            pts.append((x1 + (r1 + off) * math.cos(a), z1 + (r1 + off) * math.sin(a)))
        a0, a1 = ang - math.pi / 2 - b, ang + math.pi / 2 + b          # wrap on pulley 2
        for i in range(25):
            a = a0 + (a1 - a0) * i / 24
            pts.append((x2 + (r2 + off) * math.cos(a), z2 + (r2 + off) * math.sin(a)))
        return pts

    outer = cq.Workplane("XZ", origin=(0, y0, 0)).polyline([(x, z) for x, z in ring_pts(t / 2)]).close().extrude(-width)
    inner = cq.Workplane("XZ", origin=(0, y0, 0)).polyline([(x, z) for x, z in ring_pts(-t / 2)]).close().extrude(-width)
    return outer.cut(inner).val()


def bbox_centre(s):
    b = s.BoundingBox()
    return ((b.xmin + b.xmax) / 2, (b.ymin + b.ymax) / 2, (b.zmin + b.zmax) / 2)


def t_slot(x0, x1, ys, zs, slot=6.2, depth=6.0, bore=2.1):
    """20x20-style T-slot rail along x (simplified: a 6.2 mm slot down the middle of each face and the centre bore)."""
    (y0, y1), (z0, z1) = ys, zs
    yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
    s = box(x0, x1, y0, y1, z0, z1)
    h = slot / 2
    for cut in (box(x0 - 1, x1 + 1, yc - h, yc + h, z1 - depth, z1 + 1), box(x0 - 1, x1 + 1, yc - h, yc + h, z0 - 1, z0 + depth),
                box(x0 - 1, x1 + 1, y1 - depth, y1 + 1, zc - h, zc + h), box(x0 - 1, x1 + 1, y0 - 1, y0 + depth, zc - h, zc + h),
                cyl(bore, x1 - x0 + 2, (x0 - 1, yc, zc), (1, 0, 0))):
        s = s.cut(cut)
    return s
