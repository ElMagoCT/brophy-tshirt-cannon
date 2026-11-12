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


def add(name, shape, color, group, bom=None, kind="cots", moving=False, note="", mass=None):
    """Register one part. `bom` groups identical parts on the parts list; `mass` (kg) overrides the
    density estimate for hollow or mixed-material parts."""
    if isinstance(shape, cq.Workplane):
        shape = shape.val() if len(shape.vals()) == 1 else cq.Compound.makeCompound(shape.vals())
    PARTS.append(dict(name=name, shape=shape, color=C[color] if isinstance(color, str) else color,
                      group=group, bom=bom or name, kind=kind, moving=moving, note=note, mass=mass))
    return shape


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
