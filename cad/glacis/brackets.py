"""Flat waterjet brackets for the box-tube frame (Micah, 2026-11-11: "add all the brackets, everything can be waterjet
from 1/8 in or 1/16 in aluminum. try to avoid bends because they throw off the holes and we plan to cnc the extrusions
... be metal efficient and feel free to style stuff. try to keep brackets under 12x12 which is the size of our
waterjet"; then "tie the motor mounts into the tank posts and stuff. make it interconnected. include the threaded
rivets if/where you use them but no need for screws").

Every bracket is a flat plate on a face of the tubes it joins, held by 3/16 blind rivets in CNC'd holes. Each plate is
kept as 2D data (outline, isogrid pockets, holes), so the solid, the DXF and the nest all come from the same numbers.

- Side plates (one per drive corner, on the inner rail's outboard face): carry the Falcon and the axle as the drive
  plates did, and run on along the rail to rivet into every post on that stretch: rear = both sled posts, the turret
  tower and the rear tank post; front = the front tank post. One plate per side of each end ties the drive, the
  battery sled, the tower and the tank arm together.
- Inboard plates on the rail's inner face round the same posts (clear of the Falcons).
- Arm knees: an L on both faces of every post-to-arm joint (sled rails, tank arms).
- Corner gussets (top C, bottom L) as before, now drilled.
- Tower plates: flat (no bent flanges), under 12 in, plus a spacer strip for the rest of the in-well rail.
- Bellypan in three pieces under 12 in, with a 1/16 in strap under each seam.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, union, PARTS

T8, T16 = P.PLATE_T, 1.5875
WALL = P.TUBE_WALL
RIV = 2.45                                  # 3/16 blind rivet in a #11 hole (4.9 mm)
SHEET = 304.8                               # the waterjet's 12 x 12 in bed
FLAT = []                                   # every flat part: name, key, t, outline, pockets, holes, mirrored copies
RIVETS = []                                 # (plate name, point on the tube face, direction into the tube)
IY = (P.INNER_RAIL_Y[0] + P.INNER_RAIL_Y[1]) / 2
ZR0, ZR1 = P.RAIL_Z
ZARM = ZR1 + 104.0                          # top of the posts = bottom of the arms
TOP = ZARM - 4.4                            # side / inboard plates stop under the arm knees


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


def plate(name, key, t, fr, outline, holes, rivets, pockets=(), group="frame", bom=None, note="", mirrors=(),
          tube="far", flush=False, marks=()):
    """Queue one flat part (built in realise() once the rivets are checked). `rivets` = [(u, v)] into the tube on the
    plate's `tube` side: "far" = beyond the plate along n (the plate is w 0..t), "near" = behind the origin face.
    `mirrors` = [(name, solid -> solid, frame)] for the other copies of the same flat part. `flush` = countersunk
    rivets (no head stands proud)."""
    SPECS.append(dict(name=name, key=key, t=t, fr=fr, outline=ccw(outline), holes=list(holes), rivets=list(rivets),
                      pockets=[ccw(p) for p in pockets], group=group, note=note, mirrors=list(mirrors), tube=tube,
                      flush=flush, bom=bom or f"{key} ({'1/8' if t > 2 else '1/16'} Al, waterjet)", marks=list(marks)))


def _rivet_at(sp, f_, uv):
    """(point on the tube face, direction into the tube, point on the head face, outward direction)."""
    n = f_["n"]
    t = sp["t"]
    if sp["tube"] == "far":
        return world(f_, uv, t), n, world(f_, uv, 0.0), tuple(-c for c in n)
    return world(f_, uv, 0.0), tuple(-c for c in n), world(f_, uv, t), n


def _bb(sh, pad=0.0):
    b = sh.BoundingBox()
    return (b.xmin - pad, b.ymin - pad, b.zmin - pad, b.xmax + pad, b.ymax + pad, b.zmax + pad)


def _ov(a, b):
    return all(a[i] < b[i + 3] and b[i] < a[i + 3] for i in range(3))


def realise(log=print):
    """Drop rivets whose heads would hit another part, then build and register every queued plate."""
    plain = []
    for sp in SPECS:
        s0 = solid(sp["outline"], [], [], sp["t"], sp["fr"])
        plain.append([s0] + [fn(s0) for _, fn, _ in sp["mirrors"]])
    obst = [(p["shape"], _bb(p["shape"])) for p in PARTS if not p["moving"] and not (
        p["name"].endswith("(1x2)") or p["name"].endswith("(1x1)"))]
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
                    hd = cyl(4.8, 1.6, hp, out)
                    hb = _bb(hd)
                    for sh, b in others:
                        if _ov(hb, b) and hd.intersect(sh).Volume() > 0.5:
                            bad = True
                            break
                    if bad:
                        break
            if bad:
                dropped[sp["key"]] = dropped.get(sp["key"], 0) + 1
            else:
                keep.append(uv)
        sp["rivets"] = keep
    if dropped:
        log("rivets dropped (head would hit a part):", dropped)
    for sp in SPECS:
        holes = sp["holes"] + [(u, v, RIV) for u, v in sp["rivets"]]
        s = solid(sp["outline"], sp["pockets"], holes, sp["t"], sp["fr"])
        copies = [(sp["name"], s, sp["fr"])] + [(nm, fn(s), f_) for nm, fn, f_ in sp["mirrors"]]
        for nm, sh, f_ in copies:
            add(nm, sh, "alu", sp["group"], bom=sp["bom"], kind="stock",
                note=sp["note"] + (f"; {len(sp['rivets'])} x 3/16 {'countersunk ' if sp['flush'] else ''}blind rivets"
                                   if sp["rivets"] else ""))
            for uv in sp["rivets"]:
                p_, d_, _, _ = _rivet_at(sp, f_, uv)
                RIVETS.append((nm, p_, d_, sp["flush"]))
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


# ------------------------------------------------------------------ the brackets
POSTS = {"rear": [(-320.0, "sled"), (-215.0, "sled"), (-170.0, "tower"), (-60.0, "tank")],
         "front": [(200.0, "tank")]}


def side_plates():
    """Outboard face of each inner rail, one plate per end (the old drive plate grown along the rail)."""
    yo = P.DRIVE_PLATE_Y[1]                                  # outer face; the plate runs in to the rail at DRIVE_PLATE_Y[0]
    for end, sx in (("front", 1), ("rear", -1)):
        ax = sx * P.AX_X
        fx, fz = P.falcon_xz(end == "front")
        posts = POSTS[end]
        xs = [x for x, _ in posts] + [ax, fx]
        x0 = min(min(x for x, _ in posts) - 15.0, ax - 26.0, fx - 36.0)
        x1 = max(max(x for x, _ in posts) + 15.0, ax + 26.0, fx + 36.0)
        pts = rect(x0, x1, ZR0 + 6.0, ZR1) + circ(ax, P.AXLE_Z, 22.0) + circ(fx, fz, 37.0)
        for x, _ in posts:
            pts += rect(x - 14.0, x + 14.0, ZR1, TOP - 1.0)          # 146 mm tall: two to a 12 x 12 sheet
        out = hull(pts)
        holes = [(ax, P.AXLE_Z, 18.0), (fx, fz, 10.0)] + \
                [(fx + 25.4 * math.cos(math.radians(60 * k)), fz + 25.4 * math.sin(math.radians(60 * k)), 2.4) for k in range(6)]
        riv = []
        x = x0 + 10.0
        while x < x1 - 9.5:                                  # two rows into the rail, every 32 mm, clear of the axle
            if abs(x - ax) > 30.0 and all(abs(x - p) > 9.0 for p, _ in posts):
                riv += [(x, P.AXLE_Z - 12.7), (x, P.AXLE_Z + 12.7)]
            x += 32.0
        for x, kind in posts:
            riv += [(x, ZR1 + 30.0), (x, TOP - 15.0)]        # two up each post
        keep = [(u, v, 9.0) for u, v in riv] + [(ax, P.AXLE_Z, 25.0), (fx, fz, 35.0)]
        pk = isogrid(out, keep)
        fr = frame((0.0, yo, 0.0), (1, 0, 0), (0, 0, 1))      # n = -y: the plate runs from y DRIVE_PLATE_Y[1] in to [0]
        nm = f"Side plate {end} L"
        plate(nm, f"Side plate {end}", T8, fr, out, holes, riv, pk, group="drive",
              note="carries the Falcon (4 x 10-32 into its face) and the axle, and rivets into the inner rail and every "
                   "post on this stretch: " + ", ".join(f"{k} post x {x:.0f}" for x, k in posts),
              mirrors=[(f"Side plate {end} R", mirror_y, mirror_fr_y(fr))], flush=True)   # the wheel runs right beside it


def inboard_plates():
    """Inner face of each inner rail round the same posts, clear of the Falcon bodies (r 30) by 3 mm or more."""
    groups = [("rear", [-320.0, -215.0, -170.0], -335.0, -155.0, ZR1 + 30.0), ("rear tank", [-60.0], -74.0, -20.0, TOP),
              ("front tank", [200.0], 160.0, 240.0, TOP)]
    for tag, xs, x0, x1, top in groups:
        fx, fz = P.falcon_xz(xs[0] > 0)
        pts = rect(x0, x1, ZR0 + 3.0, ZR1)
        for x in xs:
            pts += rect(x - 14.0, x + 14.0, ZR1, top)
        out = hull(pts)
        samples = [(a[0] + (b[0] - a[0]) * k / 40, a[1] + (b[1] - a[1]) * k / 40)
                   for a, b in zip(out, out[1:] + out[:1]) for k in range(41)]
        gap = min(math.hypot(q[0] - fx, q[1] - fz) for q in samples) - P.FALCON_D / 2
        assert gap > 3.0, (tag, gap)
        riv = []
        x = x0 + 10.0
        while x < x1 - 9.5:
            if all(abs(x - p) > 9.0 for p in xs):
                riv += [(x, P.AXLE_Z - 12.7), (x, P.AXLE_Z + 12.7)]
            x += 32.0
        for x in xs:
            riv += [(x, ZR1 + 30.0), (x, top - 14.0)] if top > ZR1 + 60.0 else [(x, ZR1 + 17.0)]
        pk = isogrid(out, [(u, v, 9.0) for u, v in riv]) if top > ZR1 + 60.0 else []
        fr = dict(o=(0.0, P.INNER_RAIL_Y[0], 0.0), u=(1, 0, 0), v=(0, 0, 1), n=(0, -1, 0))   # y0 - T .. y0, rail behind
        plate(f"Inboard plate {tag} L", f"Inboard plate {tag}", T8, fr, out, [], riv, pk, group="frame",
              note="inner face of the inner rail, riveted to it and up each post", tube="near",
              mirrors=[(f"Inboard plate {tag} R", mirror_y, mirror_fr_y(fr))])


def arm_knees():
    """An L on the front and back faces of every post-to-arm joint (sled rails and tank arms). At the -320 sled post
    the rear manifold sits right behind it and the line relief valve in front of its lower half, so that joint gets a
    short knee on its front face only."""
    y0, y1 = P.INNER_RAIL_Y
    zt = ZARM + 25.4
    ya = 190.0

    def knee(zb):
        out = [(y0, zb), (y1, zb), (y1, ZARM - 4.0), (y1 + 4.0, ZARM), (ya, ZARM), (ya, zt), (y0, zt)]
        return fillet_poly(out, 3.0)
    arm = [(IY, ZARM + 12.7), (150.0, ZARM + 12.7), (178.0, ZARM + 12.7)]
    full = (knee(ZARM - 70.0), [(IY, ZARM - 52.0), (IY, ZARM - 22.0)] + arm)
    short = (knee(ZARM - 40.0), [(IY, ZARM - 24.0)] + arm)
    specs = {}
    for x, kind in [(-320.0, "sled"), (-215.0, "sled"), (-60.0, "tank"), (200.0, "tank")]:
        frf = dict(o=(x + 12.7, 0.0, 0.0), u=(0, 1, 0), v=(0, 0, 1), n=(1, 0, 0))      # front face, x + 12.7 .. + T
        frb = mirror_fr_x(frf, x)
        back = lambda s, x=x: s.mirror("YZ", (x, 0, 0))
        backR = lambda s, x=x: s.mirror("YZ", (x, 0, 0)).mirror("XZ")
        if x == -320.0:
            outl, riv = short
            mir = [(f"Arm knee short {kind} {x:.0f} front R", mirror_y, mirror_fr_y(frf))]
            plate(f"Arm knee short {kind} {x:.0f} front L", "Arm knee short", T8, frf, outl, [], riv, (), group="frame",
                  note="front face of the rearmost sled post / rail joint only (the rear manifold is right behind "
                       "it, the line relief valve in front of the post's lower half): 1 rivet in the post, 3 in the rail",
                  mirrors=mir, tube="near")
            continue
        outl, riv = full
        mir = [(f"Arm knee {kind} {x:.0f} back L", back, frb),
               (f"Arm knee {kind} {x:.0f} front R", mirror_y, mirror_fr_y(frf)),
               (f"Arm knee {kind} {x:.0f} back R", backR, mirror_fr_y(frb))]
        plate(f"Arm knee {kind} {x:.0f} front L", "Arm knee", T8, frf, outl, [], riv, (), group="frame",
              note=f"one on each face of the {kind} post / arm joint: 2 rivets up the post, 3 along the arm",
              mirrors=mir, tube="near")


def tower_plates():
    """Flat: the in-well rail strip, a tapered tab down the tower and a tab up the bearing block; the rest of the rail
    gets a flat spacer strip. Both under 12 in."""
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
    riv = [((x0 + x1) / 2, rz0 - 40.0), ((x0 + x1) / 2, rz0 - 16.0)]
    fr = dict(o=(0.0, ry1 + T8, 0.0), u=(1, 0, 0), v=(0, 0, 1), n=(0, -1, 0))     # y ry1 .. ry1 + T
    plate("Tower plate L", "Tower plate", T8, fr, out, holes, riv, (), group="frame",
          note="flat (was bent): 2 rivets into the tower, the in-well rail's M4s through it, 3 x 1/4-20 into the bearing "
               "block; between the rail and the deck's well-edge member",
          mirrors=[("Tower plate R", mirror_y, mirror_fr_y(fr))])
    # the rest of the rail: a plain spacer strip so the rail stays straight
    sx0, sx1 = xe + 1.0, rx1
    sh = [(x_, P.DECK_RAIL["screw_z"], 2.25) for x_ in screws if sx0 < x_ < sx1]
    out2 = fillet_poly(rect(sx0, sx1, rz0, rz1), 2.0)
    plate("Rail spacer strip L", "Rail spacer strip", T8, fr, out2, sh, [], (), group="frame",
          note="fills the gap between the in-well rail and the deck member past the tower plate; the rail's M4s through it",
          mirrors=[("Rail spacer strip R", mirror_y, mirror_fr_y(fr))])


def _mount_screws():
    """(x, y) of each frame-mount post's #10-32 up through the outer / end rail (as misc.frame_mounts places them)."""
    import misc
    out = []
    for name, q in misc.mount_points():
        if name.startswith(("L ", "R ")):
            sgn = 1 if name[0] == "L" else -1
            out.append((q.x, sgn * sum(P.OUTER_RAIL_Y) / 2))
        else:
            sx = 1 if name.startswith("front") else -1
            out.append((sx * (P.FRAME_X - 7.0), q.y))
    return out


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


def corner_gussets():
    """The top C and bottom L round each wheel end (as before), now drilled for rivets."""
    xe0 = P.AX_X + P.WHEEL_R + 3.0
    xa, xb = P.FRAME_X - 100.0, P.FRAME_X
    yi0, yi1 = P.INNER_RAIL_Y
    yo0, yo1 = P.OUTER_RAIL_Y
    top = [(xa, yi0), (xb, yi0), (xb, yo1), (xa, yo1), (xa, yo0), (xe0, yo0), (xe0, yi1), (xa, yi1)]
    bot = [(xe0, yi0), (xb, yi0), (xb, yo1), (xa, yo1), (xa, yo0), (xe0, yo0)]
    xm = (xe0 + xb) / 2
    ym_o = (yo0 + yo1) / 2
    import misc
    mounts = []
    try:
        import misc
        mounts = [(q.x, q.y) for _, q in misc.mount_points()]
    except Exception:
        pass
    mount_xy = [(abs(x), abs(y)) for x, y in _mount_screws()]
    ug_xy = [(abs(x), abs(y)) for x, y in misc.UG_SCREWS]

    def ok(u, v):
        return all(math.hypot(u - a, v - b) > 13.0 for a, b in mount_xy + ug_xy)
    end = [(xm, y) for y in (IY, 150.0, 185.0, 220.0, 245.0)]
    outer = [(x, ym_o) for x in (xa + 12.0, xa + 40.0, xa + 68.0, xb - 10.0)]
    inner = [(x, IY) for x in (xa + 40.0, xa + 64.0)]                 # (xa + 12 is under the sled post's foot)
    for tag, poly, riv in (("top", top, end + outer + inner), ("bottom", bot, end + outer)):
        riv = [(u, v) for u, v in riv if ok(u, v)]
        poly = fillet_poly(poly, 6.0)
        gh = [(u, v, 2.6) for u, v in mount_xy if _inside(poly, u, v, 4.0)]
        if tag == "bottom":
            gh += [(u, v, 3.05) for u, v in ug_xy if _inside(poly, u, v, 4.0)]
        z = ZR1 if tag == "top" else ZR0 - T8
        fr = dict(o=(0.0, 0.0, z), u=(1, 0, 0), v=(0, 1, 0), n=(0, 0, 1))     # z .. z + T
        mir = []
        for nm, f in (("front R", lambda s: s.mirror("XZ")), ("rear L", lambda s: s.mirror("YZ")),
                      ("rear R", lambda s: s.mirror("YZ").mirror("XZ"))):
            frm = fr
            if "R" in nm:
                frm = mirror_fr_y(frm)
            if "rear" in nm:
                frm = mirror_fr_x(frm, 0.0)
            mir.append((f"Corner gusset {nm} {tag}", f, frm))
        plate(f"Corner gusset front L {tag}", f"Corner gusset {tag}", T8, fr, poly, gh, riv, (), group="frame",
              note="rivets into the end rail, the outer rail" + (" and the inner rail" if tag == "top" else "") +
                   ("; countersunk (the underglow bracket runs right under it)" if tag == "bottom" else ""),
              mirrors=mir, tube="near" if tag == "top" else "far", flush=(tag == "bottom"))


SEAMS = ()


def bellypan():
    """One piece on the CNC router (Micah, 2026-11-11: "the bottom plate which can also be cnc'ed"), 768 x 259 mm,
    riveted up into both inner rails (countersunk: a smooth underside), the two fog vents cut through, and every
    electronics part's footprint lightly engraved (layer MARK) so its mounting holes get drilled to the real part."""
    import misc
    xa, xb = -P.FRAME_X + P.RAIL_W, P.FRAME_X - P.RAIL_W
    yb = P.INNER_RAIL_Y[1]
    holes = [(vx, vy, 13.5) for vx, vy in P.FOG_VENTS]
    out = fillet_poly(rect(xa, xb, -yb, yb), 3.0)
    riv = []
    x = xa + 12.0
    while x < xb - 11.0:
        riv += [(x, IY), (x, -IY)]
        x += 64.0
    marks = [(lab, rect(x0, x1, y0, y1)) for lab, x0, x1, y0, y1 in misc.ELEC_MARKS]
    fr = dict(o=(0.0, 0.0, P.BELLY_Z - T8), u=(1, 0, 0), v=(0, 1, 0), n=(0, 0, 1))
    plate("Bellypan", "Bellypan", T8, fr, out, holes, riv, (), group="frame",
          bom="Bellypan (1/8 Al, CNC router, one piece)",
          note="one piece, CNC router: riveted up into both inner rails, the fog vents through it, every electronics "
               "part's footprint engraved (drill its holes to the part)", flush=True, marks=marks)


def build(log=print):
    FLAT.clear()
    RIVETS.clear()
    SPECS.clear()
    side_plates()
    inboard_plates()
    arm_knees()
    tower_plates()
    corner_gussets()
    bellypan()
    realise(log)
    drill_tubes(log)
    span = lambda f: max(max(p[0] for p in f["outline"]) - min(p[0] for p in f["outline"]),
                         max(p[1] for p in f["outline"]) - min(p[1] for p in f["outline"]))
    log(f"brackets: {sum(f['qty'] for f in FLAT)} flat parts ({len(FLAT)} different), {len(RIVETS)} rivets into tubes "
        f"({sum(1 for r in RIVETS if r[3])} countersunk) + {10 * len(SEAMS)} through the bellypan seam straps; "
        f"biggest {max(span(f) for f in FLAT):.0f} mm")


TUBE_TABLE = []                             # (tube, what, face, along, across, dia) for the CNC program


def drill_tubes(log=print):
    """Cut every hole in the box tubes, the CNC'd holes: each bracket rivet through the wall under it, and every
    fastener and bearing hole in lib.TUBE_HOLES (frame mounts, bumper screws, underglow rivnuts, axles). Fills
    TUBE_TABLE with where each hole is on its tube."""
    import lib
    TUBE_TABLE.clear()
    tubes = [p for p in PARTS if p["name"].endswith("(1x2)") or p["name"].endswith("(1x1)")]
    bbs = []
    for p in tubes:
        b = p["shape"].BoundingBox()
        bbs.append((b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax))
    holes = [("rivet 3/16" + (" (countersunk plate)" if fl else ""), pt, d, RIV, WALL + 1.0, -0.5)
             for nm, pt, d, fl in RIVETS] + [(w, pt, d, r, L, 0.0) for w, pt, d, r, L in lib.TUBE_HOLES]
    per, missed = {}, []
    for what, pt, d, r, L, back in holes:
        a = tuple(pt[k] + d[k] * back for k in range(3))
        b_ = tuple(a[k] + d[k] * L for k in range(3))
        lo = [min(a[k], b_[k]) - r for k in range(3)]
        hi = [max(a[k], b_[k]) + r for k in range(3)]
        hit = [i for i, bb in enumerate(bbs) if all(lo[k] < bb[k + 3] and bb[k] < hi[k] for k in range(3))]
        cy = cyl(r, L, a, d)
        hit = [i for i in hit if tubes[i]["shape"].intersect(cy).Volume() > 0.05]
        if not hit:
            missed.append(what)
            continue
        for i in hit:
            per.setdefault(i, []).append(cy)
            bb = bbs[i]
            dims = [bb[k + 3] - bb[k] for k in range(3)]
            ax = dims.index(max(dims))
            n = tuple(-c for c in d)                      # the face the hole is drilled from
            nk = max(range(3), key=lambda k: abs(n[k]))
            face = {(0, 1): "front (+x)", (0, -1): "rear (-x)", (1, 1): "left (+y)", (1, -1): "right (-y)",
                    (2, 1): "top", (2, -1): "bottom"}[(nk, 1 if n[nk] > 0 else -1)]
            through = L > 3 * WALL + 2.0
            ck = [k for k in range(3) if k not in (ax, nk)][0]
            centre = (bb[ck] + bb[ck + 3]) / 2
            TUBE_TABLE.append((tubes[i]["name"], what, face + (" through both walls" if through else ""),
                               round(pt[ax] - bb[ax], 1), round(pt[ck] - centre, 1), round(2 * r, 1)))
    for i, cs in per.items():
        tubes[i]["shape"] = tubes[i]["shape"].cut(union(cs) if len(cs) > 1 else cs[0])
        tubes[i]["note"] = (tubes[i].get("note") or "") + f"; {len(cs)} CNC'd holes (docs/glacis/tube_drilling.csv)"
    if missed:
        from collections import Counter
        log("holes with no tube under them:", dict(Counter(missed)))
    log(f"tube holes: {len(TUBE_TABLE)} in {len(per)} tubes")
    return missed


def export_tube_table(path):
    import csv
    rows = sorted(TUBE_TABLE, key=lambda r: (r[0], r[2], r[3], r[4]))
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Tube", "Hole", "Face (drilled from)", "Along the tube from its -x/-y/-z end (mm)",
                    "Across the face from its centre line (mm)", "Diameter (mm)"])
        w.writerows(rows)


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
    lines = ["# Waterjet parts (frame brackets)", "",
             "Every bracket on the box-tube frame, flat, in millimetres, from `cad/glacis/brackets.py` (the CAD's own "
             "numbers, regenerated by every `robot.py` run). Nothing is bent. Each DXF is one part (layer CUT: outline, "
             "pockets and holes); `nest_*` are the parts laid out on 12 x 12 in sheets (layer SHEET is the sheet edge).", "",
             "- Holes of 4.9 mm are for 3/16 blind rivets (a #11 drill size): the matching holes in the tubes are in the "
             "CAD's tube parts, so the CNC program for each extrusion comes from the same model.",
             "- Parts marked CSK take 3/16 countersunk rivets: countersink those holes 120 deg (the rivets on the parts list are 120 deg heads) on the outer face after "
             "cutting (the side plates sit right beside the wheels; the bottom corner gussets and the bellypan face the "
             "underglow and the floor).",
             "- 1/8 in = 3.175 mm, 1/16 in = 1.59 mm, 6061 or 5052.", "",
             "| Part | Qty | Thickness | Size (mm) | Rivets each | File |", "|---|---|---|---|---|---|"]
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
