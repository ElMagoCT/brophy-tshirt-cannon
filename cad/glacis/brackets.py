"""Flat waterjet brackets for the box-tube frame (Micah, 2026-11-11: "add all the brackets, everything can be waterjet
from 1/8 in or 1/16 in aluminum. try to avoid bends because they throw off the holes and we plan to cnc the extrusions
... be metal efficient and feel free to style stuff. try to keep brackets under 12x12 which is the size of our
waterjet"; then "tie the motor mounts into the tank posts and stuff. make it interconnected. include the threaded
rivets if/where you use them but no need for screws").

extrusion-4040 (Micah, 2026-11-12: "replace all the box tube with 40x40 T-slot ... M5 T-nuts/screws, end taps and new
brackets instead of rivets"): every plate is flat 1/8 in on a face of the extrusion, held by M5 screws into T-nuts in
its slots (button heads, or countersunk where a wheel or the floor is right there); butt joints are 2 x M5 end taps;
cast 40-series corner brackets go wherever one fits. Each plate is kept as 2D data (outline, isogrid pockets, holes),
so the solid, the DXF and the nest all come from the same numbers. check_fasteners() proves every T-nut screw is on a
slot centre line and every end tap on a core.

- Side plates (one per drive corner, on the inner rail's outboard face): carry the Falcon and the inner wheel bearing
  (in a bottom-open slot, held by the inner bearing plate over it) and run on along the rail into every post on that
  stretch: rear = both sled posts, the turret tower and the rear tank post; front = the front tank post.
- Bearing plates: one on each side plate, two stacked on the outer rail's inboard face (the flanged bearing's 5/16 in
  body needs two 1/8 in plates); countersunk M5s on the wheel hub's light-hole circle.
- Corner plates (top C, bottom L) at each corner, on T-nuts (were the riveted gussets).
- Tower plates: flat, under 12 in, plus a spacer strip for the rest of the in-well rail.
- Bellypan: one piece on the CNC router, countersunk M5s into the inner rails.
- Cast corner brackets at the post feet, under the arms and at the inner / end rail corners, where they fit.
(The inboard plates and arm knees went with the rivets: end taps and corner brackets do their job.)
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
import lib
from lib import add, box, cyl, union, PARTS

T8, T16 = P.PLATE_T, 1.5875
SHEET = 304.8                               # the waterjet's 12 x 12 in bed
FLAT = []                                   # every flat part: name, key, t, outline, pockets, holes, mirrored copies
RIVETS = []                                 # (plate name, point on the extrusion face, direction into it, countersunk):
                                            # extrusion-4040: every plate's M5 into a T-nut (the name stayed)
IY = P.IY
ZR0, ZR1 = P.RAIL_Z
ZARM = ZR1 + P.POST_H                       # top of the posts = bottom of the arms
TOP = ZARM - 44.0                           # side plates stop under the arm brackets (cast L under each arm)


# ------------------------------------------------------------------ 2D helpers (convex polygons, CCW)
def hull(pts):
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    if len(pts) < 3:
        return pts
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def circ(u, v, r, n=48):
    return [(u + r * math.cos(2 * math.pi * k / n), v + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def rect(u0, u1, v0, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly))) * -1 \
        if poly else 0.0


def clip(poly, n, c):
    """Keep the part of a convex polygon with n . p >= c."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i - 1], poly[i]
        da, db = n[0] * a[0] + n[1] * a[1] - c, n[0] * b[0] + n[1] * b[1] - c
        if db >= 0:
            if da < 0:
                t = da / (da - db)
                out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            out.append(b)
        elif da >= 0:
            t = da / (da - db)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def inset(poly, d):
    """Shrink a convex CCW polygon by d."""
    out = poly
    for i in range(len(poly)):
        a, b = poly[i - 1], poly[i]
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey)
        if L < 1e-9:
            continue
        n = (-ey / L, ex / L)                             # inward normal of a CCW polygon
        out = clip(out, n, n[0] * a[0] + n[1] * a[1] + d)
        if len(out) < 3:
            return []
    return out


def rounded(poly, r):
    core = inset(poly, r)
    if len(core) < 3:
        return []
    return hull([q for p in core for q in circ(p[0], p[1], r, 16)])


def ccw(poly):
    return poly if area(poly) > 0 else list(reversed(poly))


def isogrid(region, keep, side=44.0, web=5.0, rim=8.0, r=3.5, min_area=140.0):
    """Triangular pockets (isogrid) inside a convex region, clear of keep-out circles (u, v, R)."""
    inner = inset(ccw(region), rim)
    if len(inner) < 3:
        return []
    us, vs = [p[0] for p in inner], [p[1] for p in inner]
    h = side * math.sqrt(3) / 2
    u0, v0 = min(us) - side, min(vs) - 0.5 * h
    nj = int((max(vs) - v0) / h) + 2
    ni = int((max(us) - u0) / side) + nj + 2
    pockets = []
    for j in range(nj):
        for i in range(-nj - 2, ni):
            a, b = (u0 + i * side + j * side / 2, v0 + j * h), (u0 + (i + 1) * side + j * side / 2, v0 + j * h)
            c, d = (u0 + i * side + (j + 1) * side / 2, v0 + (j + 1) * h), (u0 + (i + 1) * side + (j + 1) * side / 2, v0 + (j + 1) * h)
            for tri in ((a, b, c), (b, d, c)):
                p = inset(ccw(list(tri)), web / 2)
                for k in range(len(inner)):
                    if len(p) < 3:
                        break
                    e0, e1 = inner[k - 1], inner[k]
                    ex, ey = e1[0] - e0[0], e1[1] - e0[1]
                    L = math.hypot(ex, ey)
                    n = (-ey / L, ex / L)
                    p = clip(p, n, n[0] * e0[0] + n[1] * e0[1])
                for (ku, kv, kr) in keep:
                    if len(p) < 3:
                        break
                    cx, cy = sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p)
                    dx, dy = cx - ku, cy - kv
                    L = math.hypot(dx, dy)
                    if L < 1e-6:
                        p = []
                        break
                    n = (dx / L, dy / L)
                    if min(n[0] * (q[0] - ku) + n[1] * (q[1] - kv) for q in p) < kr:
                        p = clip(p, n, n[0] * ku + n[1] * kv + kr)
                if len(p) >= 3 and area(ccw(p)) > min_area:
                    q = rounded(ccw(p), r)
                    if len(q) >= 3 and area(q) > min_area * 0.6:
                        pockets.append(q)
    return pockets


def fillet_poly(poly, r, n=6):
    """Round every corner of a simple polygon (concave ones too) by r."""
    out = []
    m = len(poly)
    for i in range(m):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % m]
        v1 = (a[0] - b[0], a[1] - b[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        if l1 < 1e-6 or l2 < 1e-6:
            continue
        u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
        ang = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1])))
        if ang > math.pi - 1e-3:
            out.append(b)
            continue
        d = min(r / math.tan(ang / 2), l1 * 0.45, l2 * 0.45)
        rr = d * math.tan(ang / 2)
        p1 = (b[0] + u1[0] * d, b[1] + u1[1] * d)
        p2 = (b[0] + u2[0] * d, b[1] + u2[1] * d)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        bl = math.hypot(*bis)
        cc = (b[0] + bis[0] / bl * rr / math.sin(ang / 2), b[1] + bis[1] / bl * rr / math.sin(ang / 2))
        a1 = math.atan2(p1[1] - cc[1], p1[0] - cc[0])
        a2 = math.atan2(p2[1] - cc[1], p2[0] - cc[0])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            t = a1 + da * k / n
            out.append((cc[0] + rr * math.cos(t), cc[1] + rr * math.sin(t)))
    return out


# ------------------------------------------------------------------ 2D -> solid
def frame(origin, u, v):
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return dict(o=origin, u=u, v=v, n=n)


def world(fr, p, w=0.0):
    o, u, v, n = fr["o"], fr["u"], fr["v"], fr["n"]
    return tuple(o[i] + p[0] * u[i] + p[1] * v[i] + w * n[i] for i in range(3))


def solid(outline, pockets, holes, t, fr):
    wire = lambda pts: cq.Wire.makePolygon([V(x, y, 0) for x, y in pts], close=True)
    inner = [wire(p) for p in pockets] + [cq.Wire.makeCircle(r, V(u, v, 0), V(0, 0, 1)) for u, v, r in holes]
    face = cq.Face.makeFromWires(wire(outline), inner)
    s = cq.Solid.extrudeLinear(face, V(0, 0, t))
    o, u, v, n = fr["o"], fr["u"], fr["v"], fr["n"]
    loc = cq.Location(cq.Plane(origin=tuple(float(c) for c in o), xDir=tuple(float(c) for c in u),
                               normal=tuple(float(c) for c in n)))
    return s.moved(loc)


SPECS = []
HEAD = dict(button=("M5 x 10 button head + T-nut", False), csk=("M5 x 8 countersunk + T-nut", True),
            csk2=("M5 x 12 countersunk + T-nut", True))


def plate(name, key, t, fr, outline, holes, fasteners, pockets=(), group="frame", bom=None, note="", mirrors=(),
          tube="far", head="button", marks=(), stack=0.0):
    """Queue one flat part (built in realise() once its fasteners are checked). `fasteners` = [(u, v)]: M5 screws into
    T-nuts in the extrusion on the plate's `tube` side: "far" = beyond the plate along n (the plate is w 0..t),
    "near" = behind the origin face. `head` = "button" (M5 x 10, the head stands 2.75 proud and is checked against
    every part) or "csk"/"csk2" (countersunk, flush; csk2 through two stacked plates). `mirrors` = [(name, solid ->
    solid, frame)] for the other copies of the same flat part. `stack` = other plates between this one and the
    extrusion (the screws pass through them)."""
    SPECS.append(dict(name=name, key=key, t=t, fr=fr, outline=ccw(outline), stack=stack,
                      holes=list(holes), rivets=list(fasteners), pockets=[ccw(p) for p in pockets], group=group,
                      note=note, mirrors=list(mirrors), tube=tube, head=head, flush=HEAD[head][1],
                      bom=bom or f"{key} ({'1/8' if t > 2 else '1/16'} Al, waterjet)", marks=list(marks)))


def _rivet_at(sp, f_, uv):
    """(point on the extrusion face, direction into it, point on the head face, outward direction)."""
    n = f_["n"]
    t = sp["t"]
    st = sp.get("stack", 0.0)
    if sp["tube"] == "far":
        return world(f_, uv, t + st), n, world(f_, uv, 0.0), tuple(-c for c in n)
    return world(f_, uv, -st), tuple(-c for c in n), world(f_, uv, t), n


def _bb(sh, pad=0.0):
    b = sh.BoundingBox()
    return (b.xmin - pad, b.ymin - pad, b.zmin - pad, b.xmax + pad, b.ymax + pad, b.zmax + pad)


def _ov(a, b):
    return all(a[i] < b[i + 3] and b[i] < a[i + 3] for i in range(3))


def _obstacles():
    return [(p["shape"], _bb(p["shape"])) for p in PARTS if not p["moving"] and not p.get("frame")]


def _hits(sh, others, tol=0.5):
    b = _bb(sh)
    return any(_ov(b, bo) and sh.intersect(so).Volume() > tol for so, bo in others)


def realise(log=print):
    """Drop button heads that would hit another part, then build and register every queued plate and its fasteners."""
    plain = []
    for sp in SPECS:
        s0 = solid(sp["outline"], [], [], sp["t"], sp["fr"])
        plain.append([s0] + [fn(s0) for _, fn, _ in sp["mirrors"]])
    obst = _obstacles()
    dropped = {}
    for k, sp in enumerate(SPECS):
        others = obst + [(s_, _bb(s_)) for j, ss in enumerate(plain) if j != k for s_ in ss]
        frames = [sp["fr"]] + [f_ for _, _, f_ in sp["mirrors"]]
        keep = []
        for uv in sp["rivets"]:
            bad = False
            if not sp["flush"]:
                for f_ in frames:
                    _, _, hp, out = _rivet_at(sp, f_, uv)
                    if _hits(cyl(P.M5["head_r"], P.M5["head_h"], hp, out), others):
                        bad = True
                        break
            if bad:
                dropped[sp["key"]] = dropped.get(sp["key"], 0) + 1
            else:
                keep.append(uv)
        sp["rivets"] = keep
    if dropped:
        log("M5 button heads dropped (would hit a part):", dropped)
    for sp in SPECS:
        holes = sp["holes"] + [(u, v, P.M5["hole"]) for u, v in sp["rivets"]]
        s = solid(sp["outline"], sp["pockets"], holes, sp["t"], sp["fr"])
        if sp["flush"] and sp["rivets"]:                      # 90 deg countersinks on the head side
            for f_ in [sp["fr"]]:
                for uv in sp["rivets"]:
                    _, _, hp, out = _rivet_at(sp, f_, uv)
                    inward = tuple(-c for c in out)
                    s = s.cut(cq.Solid.makeCone(P.M5["csk_r"] + 0.1, P.M5["hole"], P.M5["csk_h"] + 0.1,
                                                V(*[hp[i] - inward[i] * 0.1 for i in range(3)]), V(*inward)))
        copies = [(sp["name"], s, sp["fr"])] + [(nm, fn(s), f_) for nm, fn, f_ in sp["mirrors"]]
        spec = HEAD[sp["head"]][0]
        for nm, sh, f_ in copies:
            add(nm, sh, "alu", sp["group"], bom=sp["bom"], kind="stock",
                note=sp["note"] + (f"; {len(sp['rivets'])} x {spec}" if sp["rivets"] else ""))
            for uv in sp["rivets"]:
                p_, d_, _, _ = _rivet_at(sp, f_, uv)
                RIVETS.append((nm, p_, d_, sp["flush"]))
                lib.fastener("tnut", spec, p_, d_, nm)
        FLAT.append(dict(name=sp["name"], key=sp["key"], t=sp["t"], outline=sp["outline"], pockets=sp["pockets"],
                         holes=holes, qty=len(copies), rivets=len(sp["rivets"]), flush=sp["flush"], marks=sp["marks"]))


def mirror_y(s):
    return s.mirror("XZ")


def mirror_fr_y(fr):
    o, u, v, n = fr["o"], fr["u"], fr["v"], fr["n"]
    return dict(o=(o[0], -o[1], o[2]), u=(u[0], -u[1], u[2]), v=(v[0], -v[1], v[2]), n=(n[0], -n[1], n[2]))


def mirror_fr_x(fr, x0):
    o, u, v, n = fr["o"], fr["u"], fr["v"], fr["n"]
    return dict(o=(2 * x0 - o[0], o[1], o[2]), u=(-u[0], u[1], u[2]), v=(-v[0], v[1], v[2]), n=(-n[0], n[1], n[2]))


def notch_bottom(poly, x, zc, r, n=16):
    """Splice a bottom-open slot (width 2r, up to a half round at zc) into a CCW polygon whose bottom edge is flat."""
    zb = min(p[1] for p in poly)
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        out.append(a)
        if abs(a[1] - zb) < 1e-6 and abs(b[1] - zb) < 1e-6 and a[0] < x - r < x + r < b[0]:
            out += [(x - r, zb), (x - r, zc)]
            out += [(x + r * math.cos(math.pi - math.pi * k / n), zc + r * math.sin(math.pi - math.pi * k / n))
                    for k in range(1, n)]
            out += [(x + r, zc), (x + r, zb)]
    assert len(out) > len(poly), "no flat bottom edge under the notch"
    return out


def poly_union(polys):
    """Union of simple polygons (CCW list of (u, v)) as one polygon, through OCC faces."""
    from OCP.BRepTools import BRepTools_WireExplorer
    fs = [cq.Face.makeFromWires(cq.Wire.makePolygon([V(u, v, 0) for u, v in p], close=True)) for p in polys]
    u_ = fs[0]
    for f in fs[1:]:
        u_ = u_.fuse(f)
    u_ = u_.clean()
    faces = u_.Faces()
    assert len(faces) == 1, "the polygons don't overlap"
    ex = BRepTools_WireExplorer(faces[0].outerWire().wrapped)
    pts = []
    while ex.More():
        v = cq.Vertex(ex.CurrentVertex())
        pts.append((v.X, v.Y))
        ex.Next()
    return ccw(pts)


def post_top(kind):
    """Top of a post (= the bottom of its arm), and how high the side plate's tab runs up it (44 mm under the arm,
    so a cast corner bracket fits under the arm above the plate)."""
    z = (P.TANK_ARM_TOP if kind == "tank" else P.ARM_TOP) - P.SMALL_W
    return z, z - 44.0


def stadium(u, v, r, du, dv, n=12):
    """A slot of radius r from (u, v) - (du, dv) to (u, v) + (du, dv), as a CCW polygon."""
    L = math.hypot(du, dv)
    a = math.atan2(dv, du)
    pts = []
    for sgn, (cu, cv) in ((1, (u + du, v + dv)), (-1, (u - du, v - dv))):
        base = a - math.pi / 2 if sgn > 0 else a + math.pi / 2
        pts += [(cu + r * math.cos(base + math.pi * k / n), cv + r * math.sin(base + math.pi * k / n)) for k in range(n + 1)]
    return ccw(pts)


# ------------------------------------------------------------------ the brackets
POSTS = {"rear": [(P.SLED_POST_X[0], "sled"), (P.SLED_POST_X[1], "sled"), (-170.0, "tower"), (P.TANK_POST_X[0], "tank")],
         "front": [(P.TANK_POST_X[1], "tank")]}
BRG_R = 0.5625 * P.IN + 0.05                # flanged bearing body (1.125 in) press fit


def _brg_screws(ax):
    """The 4 bearing-plate screws: on the rail's slot lines (AXLE_Z +/- 10) at radius BRG_SCREW_R from the axle, which
    is the wheel hub's light-hole circle, so a hex key reaches each one through a light hole (turn the wheel)."""
    dx = math.sqrt(P.BRG_SCREW_R ** 2 - P.SLOT_OFF ** 2)
    return [(ax + sx * dx, P.AXLE_Z + sz * P.SLOT_OFF) for sx in (-1, 1) for sz in (-1, 1)]


def bearing_plate_outline(ax):
    zb, zt = ZR0 + 1.0, ZR1 - 1.0
    return fillet_poly(rect(ax - 56.0, ax + 56.0, zb, zt), 6.0)


def side_plates():
    """Outboard face of each inner rail, one plate per end (the old drive plate grown along the rail): carries the
    Falcon (its 4 x 10-32 into the Falcon's face) and the inner wheel bearing, and ties in every post on that stretch
    with M5 button heads into T-nuts (the rail's two outboard slots and each post's two). extrusion-4040: the bearing
    sits in a bottom-open slot (the inner bearing plate bolted over it holds it), so with the Falcon unbolted and the
    8 bearing-plate screws out (through the hub's light holes) the wheel, axle and bearings drop straight out."""
    yo = P.DRIVE_PLATE_Y[1]                                  # outer face; the plate runs in to the rail at DRIVE_PLATE_Y[0]
    for end, sx in (("front", 1), ("rear", -1)):
        ax = sx * P.AX_X
        fx, fz = P.falcon_xz(end == "front")
        posts = POSTS[end]
        x0 = min(min(x for x, _ in posts) - 24.0, ax - 70.0, fx - 36.0)
        x1 = max(max(x for x, _ in posts) + 24.0, ax + 70.0, fx + 36.0)
        zb = ZR0 + 2.0
        pts = rect(x0, x1, zb, ZR1)
        for x, kind in posts:
            pts += rect(x - 24.0, x + 24.0, ZR1, post_top(kind)[1])
        hull_ = hull(pts)
        # the Falcon's lobe on its own (a hull with it would cover the posts' faces where the arm brackets go)
        lobe = hull(rect(fx - 37.0, fx + 37.0, zb, ZR1) + circ(fx, fz, 37.0))
        out = notch_bottom(poly_union([hull_, lobe]), ax, P.AXLE_Z, BRG_R)
        holes = [(fx + 25.4 * math.cos(math.radians(60 * k)), fz + 25.4 * math.sin(math.radians(60 * k)), 2.4)
                 for k in range(6)] + [(fx, fz, 10.0)]
        holes += [(u, v, P.M5["hole"]) for u, v in _brg_screws(ax)]          # the inner bearing plate's screws pass
        fas = []
        x = x0 + 12.0
        while x < x1 - 11.5:                                 # two rows into the rail's slots, every 48 mm, clear of the
            if abs(x - ax) > 66.0 and all(abs(x - p) > 24.0 for p, _ in posts):   # bearing plate and the post feet
                fas += [(x, P.AXLE_Z - P.SLOT_OFF), (x, P.AXLE_Z + P.SLOT_OFF)]
            x += 48.0
        for x, kind in posts:                                # two up each post, one in each slot
            fas += [(x - P.SLOT_OFF, ZR1 + 22.0), (x + P.SLOT_OFF, post_top(kind)[1] - 12.0)]
        keep = [(u, v, 9.0) for u, v in fas] + [(ax, P.AXLE_Z, 60.0), (ax, zb, 60.0), (fx, fz, 48.0),
                                                 (fx - 30.0, ZR1, 30.0), (fx + 30.0, ZR1, 30.0)]
        pk = isogrid(hull_, keep)
        fr = frame((0.0, yo, 0.0), (1, 0, 0), (0, 0, 1))      # n = -y: the plate runs from y DRIVE_PLATE_Y[1] in to [0]
        nm = f"Side plate {end} L"
        plate(nm, f"Side plate {end}", T8, fr, out, holes, fas, pk, group="drive",
              note="carries the Falcon (4 x 10-32 into its face) and the inner wheel bearing (bottom-open slot; the inner "
                   "bearing plate over it), M5 into T-nuts in the inner rail and every post on this stretch: " +
                   ", ".join(f"{k} post x {x:.0f}" for x, k in posts),
              mirrors=[(f"Side plate {end} R", mirror_y, mirror_fr_y(fr))], head="button")
        # the inner bearing plate, over the side plate's slot: the bearing's 5/16 in body through both
        bo = bearing_plate_outline(ax)
        bfr = frame((0.0, P.IN_BRG_PLATE_Y[1], 0.0), (1, 0, 0), (0, 0, 1))
        plate(f"Inner bearing plate {end} L", "Bearing plate", T8, bfr, bo, [(ax, P.AXLE_Z, BRG_R)], _brg_screws(ax), (),
              group="drive", note="closed bore: the flanged hex bearing pressed through it and the side plate's slot; "
                                  "4 x M5 x 12 countersunk through both into the inner rail's T-nuts (reach them through "
                                  "the wheel hub's light holes)",
              mirrors=[(f"Inner bearing plate {end} R", mirror_y, mirror_fr_y(bfr))], head="csk2", stack=T8)
        # the two outer bearing plates on the outer rail's inboard face (the same part as the inner one)
        for k in (0, 1):                                     # a: wheel side (the screws' heads), b: rail side
            yb1 = P.OUT_BRG_PLATE_Y[0] + (k + 1) * T8
            ofr = frame((0.0, yb1, 0.0), (1, 0, 0), (0, 0, 1))  # n = -y: yb1 - T .. yb1, the rail behind ("near")
            plate(f"Outer bearing plate {end} {'a' if k == 0 else 'b'} L", "Bearing plate", T8, ofr, bo,
                  [(ax, P.AXLE_Z, BRG_R)] + ([] if k == 0 else [(u, v, P.M5["hole"]) for u, v in _brg_screws(ax)]),
                  _brg_screws(ax) if k == 0 else [], (), group="drive", tube="near", stack=T8 if k == 0 else 0.0,
                  note="two stacked on the outer rail's inboard face, the flanged hex bearing pressed through both; "
                       "4 x M5 x 12 countersunk through both into the rail's T-nuts (reach them through the wheel hub's "
                       "light holes)" if k == 0 else "the rail-side one of the pair (the screws come through it)",
                  mirrors=[(f"Outer bearing plate {end} {'a' if k == 0 else 'b'} R", mirror_y, mirror_fr_y(ofr))],
                  head="csk2")
        # (the outer pair's screws are registered on the wheel-side plate "a"; they pass through "b" and into the rail)


def tower_plates():
    """Flat: the in-well rail strip, a tapered tab down the tower and a tab up the bearing block; the rest of the rail
    gets a flat spacer strip. Both under 12 in. extrusion-4040: the tab takes 2 x M5 into T-nuts in the tower's
    outboard slots (was 2 rivets)."""
    (rx0, rx1), (ry0, ry1), (rz0, rz1) = P.DECK_RAIL["x"], P.DECK_RAIL["y"], P.DECK_RAIL["z"]
    x0, x1 = P.TOWER_X
    px, pz = P.PIVOT
    xs = rx0 + 5.0
    xe = px + 18.0                                           # 293 mm: fits the bed with a margin
    out = [(xs, rz0), (x0 - 24.0, rz0), (x0, rz0 - 52.0), (x1, rz0 - 52.0), (x1 + 24.0, rz0), (xe, rz0),
           (xe, pz + 28.0), (x1 + 20.0, pz + 28.0), (x1, rz1 + 8.0), (x1, rz1), (xs, rz1)]
    out = fillet_poly(out, 4.0)
    holes = [(px, pz, 10.0)]
    holes += [(x_, pz - 14.0 if x_ > px - 30 else rz1 + 26.0, 3.4) for x_ in (x1 + 25.0, (x1 + px) / 2.0, px - 20.0)]
    import misc
    screws = [x_ for x_ in misc.DECK_RAIL_SCREWS]
    holes += [(x_, P.DECK_RAIL["screw_z"], 2.25) for x_ in screws if xs < x_ < xe]
    xc = (x0 + x1) / 2
    fas = [(xc - P.SLOT_OFF, rz0 - 40.0), (xc + P.SLOT_OFF, rz0 - 16.0)]
    fr = dict(o=(0.0, ry1 + T8, 0.0), u=(1, 0, 0), v=(0, 0, 1), n=(0, -1, 0))     # y ry1 .. ry1 + T
    plate("Tower plate L", "Tower plate", T8, fr, out, holes, fas, (), group="frame",
          note="flat: 2 x M5 into T-nuts in the tower's outboard slots, the in-well rail's M4s through it, 3 x 1/4-20 into "
               "the bearing block; between the rail and the deck's well-edge member",
          mirrors=[("Tower plate R", mirror_y, mirror_fr_y(fr))])
    # the rest of the rail: a plain spacer strip so the rail stays straight
    sx0, sx1 = xe + 1.0, rx1
    sh = [(x_, P.DECK_RAIL["screw_z"], 2.25) for x_ in screws if sx0 < x_ < sx1]
    out2 = fillet_poly(rect(sx0, sx1, rz0, rz1), 2.0)
    plate("Rail spacer strip L", "Rail spacer strip", T8, fr, out2, sh, [], (), group="frame",
          note="fills the gap between the in-well rail and the deck member past the tower plate; the rail's M4s through it",
          mirrors=[("Rail spacer strip R", mirror_y, mirror_fr_y(fr))])


def _inside(poly, u, v, margin=0.0):
    """Point in polygon (ray cast), at least `margin` from every edge."""
    n, c = len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i - 1], poly[i]
        if (y1 > v) != (y2 > v) and u < (x2 - x1) * (v - y1) / (y2 - y1) + x1:
            c = not c
        ex, ey = x2 - x1, y2 - y1
        L2 = ex * ex + ey * ey or 1e-9
        t = max(0.0, min(1.0, ((u - x1) * ex + (v - y1) * ey) / L2))
        if math.hypot(u - x1 - t * ex, v - y1 - t * ey) < margin:
            return False
    return c


def _near_endtap(pt, r=9.0):
    """True when a point is within r of any end-tap screw line or its access hole (so a T-nut there would foul it)."""
    for f in lib.FASTENERS:
        if f["kind"] != "endtap":
            continue
        a, d = f["at"], f["d"]
        e = f.get("entry", a[[k for k in range(3) if d[k]][0]])
        k = [k for k in range(3) if abs(d[k]) > 0.5][0]
        lo, hi = sorted([e, a[k] + d[k] * 15.0])
        q = [pt[0], pt[1], pt[2]]
        t = max(lo, min(hi, q[k]))
        c = list(a)
        c[k] = t
        if math.dist(q, c) < r + (P.M5["access_r"] if f.get("access") else P.M5["hole"]):
            return True
    return False


def corner_plates():
    """Flat 1/8 in corner plates top (a C over the end, outer and inner rails) and bottom (an L under the end and outer
    rails) at each corner, on M5 T-nuts in the members' slots (was the riveted corner gussets); the butt joints under
    them also have 2 M5 end taps each."""
    import misc
    xe0 = P.FRAME_X - P.RAIL_W
    xa, xb = P.CORNER_PLATE_X, P.FRAME_X
    yi0, yi1 = P.INNER_RAIL_Y
    yo0, yo1 = P.OUTER_RAIL_Y
    top = [(xa, yi0), (xb, yi0), (xb, yo1), (xa, yo1), (xa, yo0), (xe0, yo0), (xe0, yi1), (xa, yi1)]
    bot = [(xe0, yi0), (xb, yi0), (xb, yo1), (xa, yo1), (xa, yo0), (xe0, yo0)]
    mount_xy = [(abs(x), abs(y)) for x, y, z in misc.MOUNT_SCREWS if z > ZR1 + 0.1]   # posts standing on the plate
    ug_xy = [(abs(x), abs(y)) for x, y in misc.UG_SCREWS]
    xm = xb - P.RAIL_W / 2

    def cands(tag):
        pts = []
        for xs in (xm - P.SLOT_OFF, xm + P.SLOT_OFF):                     # the end rail, along y
            y = yi0 + 10.0
            while y < yo0 - 8.0:
                pts.append((xs, y))
                y += 40.0
        for ys in (P.OY - P.SLOT_OFF, P.OY + P.SLOT_OFF):                  # the outer rail, along x
            x = xa + 10.0
            while x < xb - 8.0:
                pts.append((x, ys))
                x += 40.0
        if tag == "top":
            for ys in (P.IY - P.SLOT_OFF, P.IY + P.SLOT_OFF):              # the inner rail, along x
                x = xa + 10.0
                while x < xe0 - 8.0:
                    pts.append((x, ys))
                    x += 40.0
        return pts
    for tag, poly in (("top", top), ("bottom", bot)):
        z = ZR1 if tag == "top" else ZR0
        fas = []
        for u, v in cands(tag):
            if not _inside(poly, u, v, 7.0):
                continue
            if any(math.hypot(u - a, v - b) < 13.0 for a, b in mount_xy + ug_xy):
                continue
            if _near_endtap((u, v, z)) or _near_endtap((-u, v, z)) or _near_endtap((u, -v, z)) or _near_endtap((-u, -v, z)):
                continue
            fas.append((u, v))
        poly = fillet_poly(poly, 6.0)
        gh = [(u, v, P.M5["hole"]) for u, v in mount_xy if _inside(poly, u, v, 4.0)]
        zp = ZR1 if tag == "top" else ZR0 - T8
        fr = dict(o=(0.0, 0.0, zp), u=(1, 0, 0), v=(0, 1, 0), n=(0, 0, 1))     # zp .. zp + T
        mir = []
        for nm, f in (("front R", lambda s: s.mirror("XZ")), ("rear L", lambda s: s.mirror("YZ")),
                      ("rear R", lambda s: s.mirror("YZ").mirror("XZ"))):
            frm = fr
            if "R" in nm:
                frm = mirror_fr_y(frm)
            if "rear" in nm:
                frm = mirror_fr_x(frm, 0.0)
            mir.append((f"Corner plate {nm} {tag}", f, frm))
        plate(f"Corner plate front L {tag}", f"Corner plate {tag}", T8, fr, poly, gh, fas, (), group="frame",
              note="M5 into T-nuts in the end rail, the outer rail" + (" and the inner rail" if tag == "top" else "") +
                   ("; countersunk (the underglow bracket runs right under it)" if tag == "bottom" else
                    "; the frame-mount posts' M5s through it where they stand on it"),
              mirrors=mir, tube="near" if tag == "top" else "far", head="button" if tag == "top" else "csk")


def bellypan():
    """One piece on the CNC router (Micah, 2026-11-11: "the bottom plate which can also be cnc'ed"), 768 x 259 mm,
    screwed up into both inner rails with M5 countersunk into T-nuts in their inner bottom slots (a smooth underside),
    the two fog vents cut through, a 12 mm hole under each post's end taps, and every electronics part's footprint
    lightly engraved (layer MARK) so its mounting holes get drilled to the real part."""
    import misc
    xa, xb = -P.FRAME_X + P.RAIL_W, P.FRAME_X - P.RAIL_W
    yb = P.INNER_RAIL_Y[1]
    holes = [(vx, vy, 13.5) for vx, vy in P.FOG_VENTS]
    taps = [f["at"] for f in lib.FASTENERS if f["kind"] == "endtap" and abs(f["at"][2] - ZR1) < 0.5 and f["d"][2] > 0.5]
    holes += [(a[0], a[1], 6.0) for a in taps]               # wrench access to the post feet
    out = fillet_poly(rect(xa, xb, -yb, yb), 3.0)
    fas = []
    x = xa + 12.0
    while x < xb - 11.0:
        for sg in (1, -1):
            pt = (x, sg * (P.IY - P.SLOT_OFF))
            if all(math.hypot(pt[0] - a[0], pt[1] - a[1]) > 14.0 for a in taps):
                fas.append(pt)
        x += 48.0
    marks = [(lab, rect(x0, x1, y0, y1)) for lab, x0, x1, y0, y1 in misc.ELEC_MARKS]
    fr = dict(o=(0.0, 0.0, P.BELLY_Z - T8), u=(1, 0, 0), v=(0, 1, 0), n=(0, 0, 1))
    plate("Bellypan", "Bellypan", T8, fr, out, holes, fas, (), group="frame",
          bom="Bellypan (1/8 Al, CNC router, one piece)",
          note="one piece, CNC router: M5 countersunk up into T-nuts in both inner rails, the fog vents through it, a 12 mm "
               "hole under each post foot's end taps, every electronics part's footprint engraved (drill its holes to the "
               "part)", head="csk", marks=marks)


# ------------------------------------------------------------------ cast 40-series corner brackets
CNR = dict(L=40.0, W=40.0, t=4.0, hole_at=22.0, mass=0.035)


def cnr_bracket(c, e1, e2):
    """A cast 40-series L corner bracket in the inside corner along the line through c (its width along e3 = e1 x e2):
    one leg on the face whose outward normal is e2 (running along e1), the other on the face whose normal is e1
    (running along e2), a centre rib, 2 x M5 per leg on the slot lines (+/- 10 across). Returns (solid, fasteners)."""
    L, W, t = CNR["L"], CNR["W"], CNR["t"]
    e1, e2 = V(*e1), V(*e2)
    e3 = e1.cross(e2)
    pl = cq.Plane(origin=V(*c), xDir=e1, normal=e3)               # local x = e1, y = e2, z = e3
    legA = cq.Solid.makeBox(L, t, W, V(0, 0, -W / 2))
    legB = cq.Solid.makeBox(t, L, W, V(0, 0, -W / 2))
    rib = cq.Solid.extrudeLinear(cq.Face.makeFromWires(cq.Wire.makePolygon(
        [V(t, t, -2.0), V(L - 3.0, t, -2.0), V(t, L - 3.0, -2.0)], close=True)), V(0, 0, 4.0))
    s = legA.fuse(legB).fuse(rib)
    fas = []
    for w in (-P.SLOT_OFF, P.SLOT_OFF):
        s = s.cut(cyl(P.M5["hole"], t + 2, (CNR["hole_at"], -1.0, w), (0, 1, 0)))
        s = s.cut(cyl(P.M5["hole"], t + 2, (-1.0, CNR["hole_at"], w), (1, 0, 0)))
        fas.append(((CNR["hole_at"], 0.0, w), (0, -1, 0), (CNR["hole_at"], t, w), (0, 1, 0)))
        fas.append(((0.0, CNR["hole_at"], w), (-1, 0, 0), (t, CNR["hole_at"], w), (1, 0, 0)))
    loc = cq.Location(pl)
    s = s.moved(loc)

    def g(p):
        return tuple(pl.toWorldCoords(p).toTuple())

    def gd(d):
        return tuple((pl.toWorldCoords(d) - pl.toWorldCoords((0, 0, 0))).toTuple())
    return s, [(g(a), gd(d), g(h), gd(o)) for a, d, h, o in fas]


def corner_brackets(log=print):
    """Cast 40-series corner brackets wherever one fits (each candidate is dropped if it, or a button head on it, would
    hit any part): both sides of each post foot on the inner rail, under each arm outboard of its post (above the side
    plate), and the inside corners where the inner rails meet the end rails."""
    cands = []
    zr1 = ZR1
    for sgn, side in ((1, "L"), (-1, "R")):
        y_c = sgn * P.IY
        for x, kind in POSTS["rear"] + POSTS["front"]:
            for sx, face in ((1, "front"), (-1, "back")):
                cands.append((f"Corner bracket {kind} {x:.0f} {side} foot {face}",
                              (x + sx * P.SMALL_W / 2, y_c, zr1), (sx, 0, 0), (0, 0, 1)))
            if kind in ("sled", "tank"):
                cands.append((f"Corner bracket {kind} {x:.0f} {side} arm",
                              (x, sgn * P.GUN_RAIL_Y, post_top(kind)[0]), (0, 0, -1), (0, sgn, 0)))
        for sx, end in ((1, "front"), (-1, "rear")):
            cands.append((f"Corner bracket {end} {side} inner rail",
                          (sx * (P.FRAME_X - P.RAIL_W), sgn * P.INNER_RAIL_Y[0], (ZR0 + ZR1) / 2), (0, -sgn, 0), (-sx, 0, 0)))
    named = [(p["shape"], _bb(p["shape"]), p["name"]) for p in PARTS if not p["moving"]]
    for sx in (-1, 1):                                       # each wheel's swept envelope (+3 mm), not its rollers as
        for sg in (-1, 1):                                   # they happen to stand
            y0, y1 = sorted([sg * P.WHEEL_Y[0], sg * P.WHEEL_Y[1]])
            env = cyl(P.WHEEL_R + 3.0, y1 - y0, (sx * P.AX_X, y0, P.AXLE_Z), (0, 1, 0))
            named.append((env, _bb(env), "a wheel's swept circle"))

    def first_hit(sh, tol=0.5):
        b = _bb(sh)
        for so, bo, nm in named:
            if _ov(b, bo) and sh.intersect(so).Volume() > tol:
                return nm
        return None
    placed, dropped = [], []
    for name, c, e1, e2 in cands:
        s, fas = cnr_bracket(c, e1, e2)
        why = first_hit(s)
        if why is None:
            for a, d, h, o in fas:
                why = first_hit(cyl(P.M5["head_r"], P.M5["head_h"], h, o)) or ("an end tap" if _near_endtap(a, 6.0) else None)
                if why:
                    why = "head: " + why
                    break
        if why:
            dropped.append(f"{name} [{why}]")
            continue
        named.append((s, _bb(s), name))
        placed.append((s, name))
        add(name, s, "alu", "frame", bom="40-series cast corner bracket (M5, 2 holes per leg)", kind="cots",
            mass=CNR["mass"], note="4 x M5 x 10 button head + T-nut")
        for a, d, h, o in fas:
            lib.fastener("tnut", "M5 x 10 button head + T-nut", a, d, name)
    log(f"corner brackets: {len(placed)} placed, {len(dropped)} candidates didn't fit" +
        (f" ({', '.join(dropped)})" if dropped else ""))


def build(log=print):
    FLAT.clear()
    RIVETS.clear()
    SPECS.clear()
    side_plates()
    tower_plates()
    corner_plates()
    bellypan()
    realise(log)
    corner_brackets(log)
    finish_members(log)
    span = lambda f: max(max(p[0] for p in f["outline"]) - min(p[0] for p in f["outline"]),
                         max(p[1] for p in f["outline"]) - min(p[1] for p in f["outline"]))
    log(f"brackets: {sum(f['qty'] for f in FLAT)} flat parts ({len(FLAT)} different), {len(RIVETS)} plate M5s into T-nuts "
        f"({sum(1 for r in RIVETS if r[3])} countersunk); biggest {max(span(f) for f in FLAT):.0f} mm")


CUT_LIST = []                               # (member, length, end taps a0, end taps a1, access holes) for the shop


def finish_members(log=print):
    """Cut the 10 mm end-tap access holes into the members they pass through (each from its far face up to the joint
    face's 1.8 mm lip, which the socket head bears on), and fill CUT_LIST. Replaces the box tube's drill_tubes."""
    CUT_LIST.clear()
    byname = {p["name"]: p for p in PARTS if p.get("frame")}
    cuts = {}
    for f in lib.FASTENERS:
        if f["kind"] != "endtap" or not f.get("access") or f["cross"] not in byname:
            continue
        a, d = f["at"], f["d"]
        k = [i for i in range(3) if abs(d[i]) > 0.5][0]
        e = f["entry"]
        L = abs(a[k] - e) - 1.8
        start = list(a)
        start[k] = e + (1.0 if e > a[k] else -1.0)
        dirn = [0.0, 0.0, 0.0]
        dirn[k] = 1.0 if a[k] > e else -1.0
        cuts.setdefault(f["cross"], []).append(cyl(P.M5["access_r"], L + 1.0, tuple(start), tuple(dirn)))
    for nm, cs in cuts.items():
        p = byname[nm]
        p["shape"] = p["shape"].cut(union(cs) if len(cs) > 1 else cs[0])
        p["note"] = (p.get("note") or "") + f"; {len(cs)} x 10 mm end-tap access holes"
    for m in lib.MEMBERS:
        taps = [f for f in lib.FASTENERS if f["kind"] == "endtap" and _member_of_tap(f) is m]
        n0 = sum(1 for f in taps if f["d"]["xyz".index(m["axis"])] > 0)
        n1 = len(taps) - n0
        acc = [f for f in lib.FASTENERS if f["kind"] == "endtap" and f.get("access") and f["cross"] == m["name"]]
        ax = "xyz".index(m["axis"])
        CUT_LIST.append((m["name"], round(m["a1"] - m["a0"], 1), n0, n1, len(acc),
                         "; ".join(f"{_along(m, f):.1f}" for f in sorted(acc, key=lambda f: _along(m, f)))))
    log(f"frame: {len(lib.MEMBERS)} 40x40 members, {sum(r[1] for r in CUT_LIST) / 1000:.2f} m; "
        f"{sum(r[2] + r[3] for r in CUT_LIST)} M5 end taps, {sum(r[4] for r in CUT_LIST)} access holes")


def _along(m, f):
    """Where an access hole is along member m, from its a0 end."""
    ax = "xyz".index(m["axis"])
    return f["at"][ax] - m["a0"]


def _member_of_tap(f):
    a, d = f["at"], f["d"]
    for m in lib.MEMBERS:
        ax = "xyz".index(m["axis"])
        if abs(d[ax]) < 0.5:
            continue
        end = m["a0"] if d[ax] > 0 else m["a1"]
        o = [k for k in range(3) if k != ax]
        if abs(a[ax] - end) < 0.3 and abs(abs(a[o[0]] - m["c1"]) - P.CORE_OFF) < 0.3 and \
                abs(abs(a[o[1]] - m["c2"]) - P.CORE_OFF) < 0.3:
            return m
    return None


def _member_of_tnut(f):
    """(member, face key, across offset, along coordinate) for a T-nut, or None: the face plane must hold the point
    (0.3 mm), face normal = -d, the point within the member's length."""
    a, d = f["at"], f["d"]
    k = [i for i in range(3) if abs(d[i]) > 0.5]
    if len(k) != 1:
        return None
    k = k[0]
    for m in lib.MEMBERS:
        ax = "xyz".index(m["axis"])
        if ax == k:
            continue
        o = [i for i in range(3) if i != ax]
        cen = {o[0]: m["c1"], o[1]: m["c2"]}
        face = cen[k] - d[k] * 20.0                          # the face the screw enters from
        if abs(a[k] - face) > 0.3:
            continue
        acr = [i for i in o if i != k][0]
        if abs(a[acr] - cen[acr]) > 20.0 or not (m["a0"] - 0.1 <= a[ax] <= m["a1"] + 0.1):
            continue
        return m, (m["name"], k, d[k]), a[acr] - cen[acr], a[ax]
    return None


def check_fasteners(log=print):
    """Every T-nut screw on a slot centre line (0.3 mm) of the face it enters, T-nuts in one slot 12 mm or more apart and
    8 mm or more from a member end; every end tap on a core of the member's end; nothing in an end tap's access hole;
    any fastener that meets no member is listed."""
    res = dict(tnut=0, endtap=0, off_slot=[], missed=[], close=[], near_end=[], tap_off_core=[], in_access=[])
    slots = {}
    for f in lib.FASTENERS:
        if f["kind"] == "endtap":
            res["endtap"] += 1
            if _member_of_tap(f) is None:
                res["tap_off_core"].append((f["by"], tuple(round(c, 1) for c in f["at"])))
            continue
        res["tnut"] += 1
        hit = _member_of_tnut(f)
        if hit is None:
            res["missed"].append((f["by"], tuple(round(c, 1) for c in f["at"])))
            continue
        m, fk, acr, along = hit
        if abs(abs(acr) - P.SLOT_OFF) > 0.3:
            res["off_slot"].append((f["by"], m["name"], round(acr, 2)))
            continue
        if min(along - m["a0"], m["a1"] - along) < 8.0:
            res["near_end"].append((f["by"], m["name"], round(min(along - m["a0"], m["a1"] - along), 1)))
        slots.setdefault(fk + (round(acr, 1),), []).append((along, f["by"]))
        if _near_endtap(f["at"], 2.0):
            res["in_access"].append((f["by"], tuple(round(c, 1) for c in f["at"])))
    for key, v in slots.items():
        v.sort()
        for (a1, b1), (a2, b2) in zip(v, v[1:]):
            if a2 - a1 < 12.0:
                res["close"].append((key[0], b1, b2, round(a2 - a1, 1)))
    log(f"fasteners: {res['tnut']} T-nut screws, {res['endtap']} end taps; off a slot line {len(res['off_slot'])}, "
        f"no member {len(res['missed'])}, end tap off a core {len(res['tap_off_core'])}, T-nuts under 12 mm apart "
        f"{len(res['close'])}, within 8 mm of a member end {len(res['near_end'])}, in an access hole "
        f"{len(res['in_access'])}")
    for k in ("off_slot", "missed", "tap_off_core", "close", "near_end", "in_access"):
        for r in res[k][:12]:
            log("   ", k, r)
    return res


def hardware_counts():
    """M5 hardware by spec, T-nuts, corner brackets, end taps and access holes (for the log and the docs)."""
    from collections import Counter
    c = Counter(f["spec"] for f in lib.FASTENERS)
    tn = sum(1 for f in lib.FASTENERS if f["kind"] == "tnut")
    # the 4 outer bearing-plate screws go through plate "b" too: registered once (on plate "a")
    return c, tn


def export_cut_list(path):
    import csv
    rows = sorted(CUT_LIST, key=lambda r: r[0])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Member (40x40 20-series)", "Length (mm), square cut +0/-0.3", "M5 end taps at the -x/-y/-z end",
                    "M5 end taps at the +x/+y/+z end", "10 mm access holes", "Access holes along it from its -x/-y/-z end (mm)"])
        w.writerows(rows)


def export_tube_table(path):                # (kept for robot.py's old call; the box tube is gone)
    export_cut_list(path.replace("tube_drilling.csv", "cut_list_4040.csv"))


# ------------------------------------------------------------------ DXFs and the 12 x 12 nest
def _xf(pts, rot, dx, dy, u0, v0):
    out = []
    for u, v in pts:
        u, v = u - u0, v - v0
        if rot:
            u, v = -v, u
        out.append((u + dx, v + dy))
    return out


def _draw(msp, f, rot=False, dx=0.0, dy=0.0, layer="CUT"):
    us = [p[0] for p in f["outline"]]
    vs = [p[1] for p in f["outline"]]
    u0, v0 = min(us), min(vs)
    if rot:                                                  # keep the rotated part in +x, +y
        dx += max(vs) - v0
    msp.add_lwpolyline(_xf(f["outline"], rot, dx, dy, u0, v0), close=True, dxfattribs={"layer": layer})
    for pk in f["pockets"]:
        msp.add_lwpolyline(_xf(pk, rot, dx, dy, u0, v0), close=True, dxfattribs={"layer": layer})
    for u, v, r in f["holes"]:
        (x, y), = _xf([(u, v)], rot, dx, dy, u0, v0)
        msp.add_circle((x, y), r, dxfattribs={"layer": layer})
    for lab, poly in f.get("marks", []):                     # engraved footprints (layer MARK, 0.3 mm deep)
        pts = _xf(poly, rot, dx, dy, u0, v0)
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "MARK"})
        cx, cy = sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)
        msp.add_text(lab, height=5.0, dxfattribs={"layer": "MARK", "insert": (cx - 2.5 * len(lab) / 2, cy)})


def export_flat(out_dir, log=print, gap=3.0, margin=4.0):
    """One DXF per different flat part, the parts nested on 12 x 12 in sheets per thickness (one DXF per sheet), and
    a README with the table."""
    import os
    import ezdxf
    os.makedirs(out_dir, exist_ok=True)
    for fn in os.listdir(out_dir):
        if fn.endswith(".dxf"):
            os.remove(os.path.join(out_dir, fn))
    groups = {}
    for f in FLAT:                                           # identical parts share a file
        sig = (f["key"], f["t"], len(f["holes"]), len(f["pockets"]), round(abs(area(f["outline"]))))
        groups.setdefault(sig, dict(f, qty=0, names=[]))
        groups[sig]["qty"] += f["qty"]
        groups[sig]["names"].append(f["name"])
    parts = list(groups.values())
    for f in parts:
        f["file"] = f["key"].lower().replace(" ", "_").replace("/", "") + ".dxf"
        us = [p[0] for p in f["outline"]]
        vs = [p[1] for p in f["outline"]]
        f["w"], f["h"] = max(us) - min(us), max(vs) - min(vs)
        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 4
        _draw(doc.modelspace(), f)
        doc.saveas(os.path.join(out_dir, f["file"]))
    # nest: MaxRects (best short side fit), each part either way round, biggest first
    usable = SHEET - 2 * margin
    sheets = {}

    def fits(fr_, w, h):
        return w <= fr_[2] + 1e-6 and h <= fr_[3] + 1e-6

    def split(free, r):
        out = []
        for f in free:
            if r[0] >= f[0] + f[2] or r[0] + r[2] <= f[0] or r[1] >= f[1] + f[3] or r[1] + r[3] <= f[1]:
                out.append(f)
                continue
            if r[0] > f[0]:
                out.append((f[0], f[1], r[0] - f[0], f[3]))
            if r[0] + r[2] < f[0] + f[2]:
                out.append((r[0] + r[2], f[1], f[0] + f[2] - r[0] - r[2], f[3]))
            if r[1] > f[1]:
                out.append((f[0], f[1], f[2], r[1] - f[1]))
            if r[1] + r[3] < f[1] + f[3]:
                out.append((f[0], r[1] + r[3], f[2], f[1] + f[3] - r[1] - r[3]))
        out = [f for f in out if f[2] > 1 and f[3] > 1]
        return [f for i, f in enumerate(out) if not any(
            j != i and g[0] <= f[0] and g[1] <= f[1] and g[0] + g[2] >= f[0] + f[2] and g[1] + g[3] >= f[1] + f[3]
            and (g != f or j < i) for j, g in enumerate(out))]

    def pack(items, mode=0):
        sh = []
        for f in items:
            best = None
            for k, S in enumerate(sh):
                for fr_ in S["free"]:
                    for rot in (False, True):
                        w, h = ((f["h"], f["w"]) if rot else (f["w"], f["h"]))
                        if fits(fr_, w + gap, h + gap) or fits(fr_, w, h) and (fr_[0] + w >= usable - 1 or fr_[1] + h >= usable - 1):
                            sc = (min(fr_[2] - w, fr_[3] - h), fr_[2] * fr_[3] - w * h, fr_[1] * 1000 + fr_[0])[mode]
                            if best is None or sc < best[0]:
                                best = (sc, k, fr_[0], fr_[1], rot, w, h)
            if best is None:
                rot = f["w"] < f["h"]
                w, h = ((f["h"], f["w"]) if rot else (f["w"], f["h"]))
                if w > usable or h > usable:
                    log("does not fit a 12 x 12 sheet:", f["key"])
                    continue
                sh.append(dict(free=[(0.0, 0.0, usable, usable)], place=[]))
                best = (0, len(sh) - 1, 0.0, 0.0, rot, w, h)
            _, k, x, y, rot, w, h = best
            S = sh[k]
            S["place"].append((f, rot, margin + x, margin + y))
            S["free"] = split(S["free"], (x, y, w + gap, h + gap))

        return sh

    orders = [lambda f: -(f["w"] * f["h"]), lambda f: -max(f["w"], f["h"]), lambda f: -(f["w"] + f["h"]),
              lambda f: -min(f["w"], f["h"]), lambda f: -f["h"], lambda f: -f["w"]]
    for f in parts:
        f["cnc"] = max(f["w"], f["h"]) > usable or min(f["w"], f["h"]) > usable
    for t in sorted({f["t"] for f in parts}, reverse=True):
        base = [f for f in parts if f["t"] == t and not f["cnc"] for _ in range(f["qty"])]
        best = None
        for key in orders:
          for mode in (0, 1, 2):
            sh = pack(sorted(base, key=key), mode)
            fill = sum(r[2] * r[3] for r in sh[-1]["free"]) if sh else 0
            if best is None or (len(sh), fill) < (len(best), best_fill) and len(sh) <= len(best):
                best, best_fill = sh, fill
        sh = best
        sheets[t] = sh
        for i, S in enumerate(sh):
            doc = ezdxf.new("R2010")
            doc.header["$INSUNITS"] = 4
            msp = doc.modelspace()
            msp.add_lwpolyline([(0, 0), (SHEET, 0), (SHEET, SHEET), (0, SHEET)], close=True, dxfattribs={"layer": "SHEET"})
            for f, rot, x, y in S["place"]:
                _draw(msp, f, rot, x, y)
            doc.saveas(os.path.join(out_dir, f"nest_{'1-8' if t > 2 else '1-16'}_sheet{i + 1}.dxf"))
    used = {t: sum(abs(area(f["outline"])) - sum(abs(area(p)) for p in f["pockets"]) for f in parts
                   if f["t"] == t and not f["cnc"] for _ in range(f["qty"])) for t in sheets}
    lines = ["# Waterjet parts (frame plates, 40x40 T-slot frame)", "",
             "Every flat plate on the 40x40 T-slot frame (branch extrusion-4040), in millimetres, from "
             "`cad/glacis/brackets.py` (the CAD's own numbers, regenerated by every `robot.py` run). Nothing is bent. Each "
             "DXF is one part (layer CUT: outline, pockets and holes); `nest_*` are the parts laid out on 12 x 12 in sheets "
             "(layer SHEET is the sheet edge).", "",
             "- Holes of 5.5 mm are for M5 screws into drop-in / roll-in T-nuts in the extrusion's 6 mm slots: no holes "
             "in the extrusion for them, so the plates go on anywhere along a slot. The shop list for the extrusion "
             "itself (lengths, end taps, 10 mm access holes) is `docs/glacis/cut_list_4040.csv`.",
             "- Parts marked CSK take M5 countersunk screws: countersink those holes 90 deg to 10.4 mm on the outer face "
             "after cutting (the bearing plates sit right beside the wheels; the bottom corner plates and the bellypan "
             "face the underglow and the floor). The rest take M5 x 10 button heads.",
             "- The bearing plates (3 per wheel: the inner one on the side plate, two stacked on the outer rail) "
             "take the flanged 1/2 hex bearing as a press fit (28.68 mm): ream to fit the bearing in hand.",
             "- 1/8 in = 3.175 mm, 6061 or 5052.", "",
             "| Part | Qty | Thickness | Size (mm) | M5 screws each | File |", "|---|---|---|---|---|---|"]
    for f in sorted(parts, key=lambda f: (-f["t"], f["key"])):
        lines.append(f"| {f['key']}{' (CNC router)' if f['cnc'] else ''} | {f['qty']} | {'1/8' if f['t'] > 2 else '1/16'} in | "
                     f"{f['w']:.0f} x {f['h']:.0f} | {f['rivets']}{' CSK' if f['flush'] else ''} | `{f['file']}` |")
    lines += ["", "## Nest", ""]
    for t, sh in sheets.items():
        lines.append(f"- {'1/8' if t > 2 else '1/16'} in: {len(sh)} sheet(s) of 12 x 12 in, "
                     f"{100 * used[t] / (len(sh) * SHEET * SHEET):.0f}% of the metal used "
                     f"({', '.join(f'`nest_{chr(49) if False else ('1-8' if t > 2 else '1-16')}_sheet{i + 1}.dxf`' for i in range(len(sh)))})")
    lines += ["", "Not in this nest (CNC router, bigger than the 12 x 12 bed): the bellypan, one piece with every "
              "electronics part's footprint engraved on layer MARK (0.3 mm deep: drill each part's holes to the part), and "
              "the two gun cradle plates (`docs/glacis/gun_plates/`). Also not here: the fog heater bracket.", ""]
    open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    log(f"waterjet: {len(parts)} different parts, " + ", ".join(
        f"{'1/8' if t > 2 else '1/16'} in {len(sh)} sheet(s) {100 * used[t] / (len(sh) * SHEET * SHEET):.0f}% used"
        for t, sh in sheets.items()))
    return parts, sheets
