"""Base frame (1x2 / 1x1 x 1/16 aluminum box tube, 1/8 in gussets) and the four drive corners:
Falcon 500 -> 12T WCP pulley -> 140T belt -> 116T printed into a 10 in vector-style printed mecanum
(10 rollers on 608 2RS + fixed M8 rods, three flat aluminum plates).
Each wheel sits on a 1/2 in hex live axle running in flanged hex bearings in the inner and outer rails."""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, tube, hex_prism, union, belt_loop, PARTS

IN = P.IN


# ------------------------------------------------------------------ box tube
def box_tube_solid(axis, a0, a1, c1, c2, size=(1, 1), wall=P.TUBE_WALL):
    """Aluminum box tube along `axis` from a0 to a1. c1, c2: centre on the other two axes (x,y,z order);
    size = (w along the first other axis, h along the second) in inches."""
    w, h = size[0] * IN, size[1] * IN
    o = [k for k in "xyz" if k != axis]
    lo = {axis: min(a0, a1), o[0]: c1 - w / 2, o[1]: c2 - h / 2}
    hi = {axis: max(a0, a1), o[0]: c1 + w / 2, o[1]: c2 + h / 2}
    s = box(lo["x"], hi["x"], lo["y"], hi["y"], lo["z"], hi["z"])
    ilo = {axis: lo[axis] - 1, o[0]: lo[o[0]] + wall, o[1]: lo[o[1]] + wall}
    ihi = {axis: hi[axis] + 1, o[0]: hi[o[0]] - wall, o[1]: hi[o[1]] - wall}
    return s.cut(box(ilo["x"], ihi["x"], ilo["y"], ihi["y"], ilo["z"], ihi["z"]))


def tube_part(name, axis, a0, a1, c1, c2, size=(1, 1), group="frame", cuts=None):
    s = box_tube_solid(axis, a0, a1, c1, c2, size)
    if cuts is not None:
        s = s.cut(cuts)
    prof = "1x2" if max(size) > 1.5 else "1x1"
    return add(name, s, "extr", group, bom=f"Aluminum box tube {prof} x 1/16 wall (owned)", kind="stock",
               note=f"{abs(a1 - a0) / IN:.2f} in")


# kept for misc.py callers
def ext(name, axis, a0, a1, c1, c2, size=(1, 1), bom=None):
    return tube_part(name, axis, a0, a1, c1, c2, size)


def plate_from_circles(circles, y0, holes=(), t=P.PLATE_T):
    """1/8 in plate in an XZ plane: convex hull of (x, z, r) circles, extruded along +y from y0."""
    pts = []
    for (x, z, r) in circles:
        for k in range(24):
            a = 2 * math.pi * k / 24
            pts.append((x + r * math.cos(a), z + r * math.sin(a)))
    hull = _hull(pts)
    s = cq.Workplane("XZ", origin=(0, y0, 0)).polyline(hull).close().extrude(-t).val()
    for (x, z, r) in holes:
        s = s.cut(cyl(r, t + 2, (x, y0 - 1, z), (0, 1, 0)))
    return s


def _hull(pts):
    pts = sorted(set((round(x, 3), round(z, 3)) for x, z in pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


# ------------------------------------------------------------------ pulleys (HTD 5M)
def htd_pulley(teeth, width, y0, x, z, flange=3.0, bore=0.0):
    """Printed / WCP HTD 5M pulley in an XZ plane, teeth as round grooves, flanges both sides, along +y."""
    pd = P.pd(teeth)
    od = pd - 1.14
    body = cyl(od / 2, width, (x, y0 + flange, z), (0, 1, 0))
    if teeth <= 80:
        grooves = []
        for k in range(teeth):
            a = 2 * math.pi * k / teeth
            grooves.append(cyl(1.6, width + 0.2, (x + (od / 2) * math.cos(a), y0 + flange - 0.1,
                                                  z + (od / 2) * math.sin(a)), (0, 1, 0)))
        body = body.cut(union(grooves))
    fl = [cyl(od / 2 + 3.5, flange, (x, y0, z), (0, 1, 0)),
          cyl(od / 2 + 3.5, flange, (x, y0 + flange + width, z), (0, 1, 0))]
    s = union([body] + fl)
    if bore:
        s = s.cut(cyl(bore / 2, width + 2 * flange + 2, (x, y0 - 1, z), (0, 1, 0)))
    return s


# ------------------------------------------------------------------ COTS in the drive
def falcon(x, z, y_face, sgn):
    """Falcon 500: 60 mm body behind the face plane y_face, spline out through the plate."""
    d = -sgn
    L = P.FALCON_L
    body = cyl(P.FALCON_D / 2, L, (x, y_face, z), (0, d, 0))
    fins = []
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        fins.append(cyl(3.2, L * 0.8, (x + (P.FALCON_D / 2 - 1) * math.cos(a), y_face + d * L * 0.1,
                                      z + (P.FALCON_D / 2 - 1) * math.sin(a)), (0, d, 0)))
    face = cyl(P.FALCON_D / 2 + 1.5, 6, (x, y_face, z), (0, d, 0))
    boss = cyl(9.5, 2.5, (x, y_face, z), (0, -d, 0))
    spline = cyl(4.2, 20.0, (x, y_face, z), (0, -d, 0))
    return union([body, face, boss, spline] + fins)


def fr8(x, y0, z, sgn=1, hexbore=False, flange=True):
    """Flanged 1/2 in bearing FR8 (1/2 x 1-1/8 x 5/16), along +y*sgn from y0. hexbore: 1/2 hex bore."""
    t = 0.3125 * IN
    b = cyl(0.5625 * IN, t, (x, y0, z), (0, sgn, 0))
    if flange:
        b = b.fuse(cyl(0.6875 * IN, 1.6, (x, y0, z), (0, sgn, 0)))
    if hexbore:
        return b.cut(hex_prism(12.8, t + 2, (x, y0 - sgn, z), (0, sgn, 0)))
    return b.cut(cyl(0.25 * IN, t + 2, (x, y0 - sgn, z), (0, sgn, 0)))


def rail_bearing(x, y_face, z, into):
    """Flanged 1/2 hex bearing in a tube wall: flange on the wall face at y_face, body going `into` (+1/-1 y)."""
    fl = cyl(0.625 * IN, 1.6, (x, y_face, z), (0, -into, 0))
    body = cyl(0.5625 * IN, 0.3125 * IN - 1.6, (x, y_face, z), (0, into, 0))
    return fl.fuse(body).cut(hex_prism(12.8, 20, (x, y_face - 10 * into, z), (0, into, 0)))


def bearing_seat(x, y_face, z, sgn, depth, r_od=0.5625 * IN + 0.05, r_fl=0.6875 * IN + 0.3):
    """Pocket for bearings pressed in from a face at y_face going sgn*y, flange counterbored flush."""
    return cyl(r_od, depth + 0.8, (x, y_face - sgn * 0.5, z), (0, sgn, 0)).fuse(
        cyl(r_fl, 2.1, (x, y_face - sgn * 0.5, z), (0, sgn, 0)))


def bolt(x, z, y_head, y_end, dia=0.5 * IN, head_af=0.75 * IN, nut=True):
    """Hex bolt along y from head face y_head to y_end (nut at the end)."""
    sgn = 1 if y_end > y_head else -1
    shank = cyl(dia / 2, abs(y_end - y_head) + 6, (x, y_head, z), (0, sgn, 0))
    head = hex_prism(head_af, dia * 0.65, (x, y_head, z), (0, -sgn, 0))
    parts = [shank, head]
    if nut:
        parts.append(hex_prism(head_af, dia * 0.9, (x, y_end, z), (0, sgn, 0)))
    return union(parts)


# ------------------------------------------------------------------ printed mecanum (vector style, after TTB-0010)
def roller_profile(t):
    R, r0 = P.WHEEL_R, P.ROLL_R0
    s = math.sin(math.radians(P.ROLL_ANGLE))
    return math.sqrt(R * R - (t * s) ** 2) - (R - r0)


def _rev(prof):
    """Solid of revolution about +Z from (radius, z) points."""
    pts = [(0, prof[0][1])] + prof + [(0, prof[-1][1])]
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()


def _tread_t(t):
    return P.TREAD_T[0] + (P.TREAD_T[1] - P.TREAD_T[0]) * (2 * t / P.ROLL_L) ** 2


def roller_parts():
    """TPU tread over a PETG core, local frame: axis along +Z, centred at the origin.
    Core: a 608 2RS pressed in from each end, BRG_IN deep, behind the recess the hub's cup stub sits in."""
    L = P.ROLL_L
    ts = [-L / 2 + L * i / 24 for i in range(25)]
    tread = _rev([(roller_profile(t), t) for t in ts]).cut(_rev([(roller_profile(t) - _tread_t(t), t) for t in ts]))
    core = _rev([(roller_profile(t) - _tread_t(t), t) for t in ts])
    bd, bt = P.ROLL_BRG
    z_seat = L / 2 - P.BRG_IN - bt                      # inner face of each bearing
    core = core.cut(cyl(9.0, 2 * z_seat + 0.2, (0, 0, -z_seat - 0.1)))      # light bore; outer-race shoulders
    for s in (-1, 1):
        core = core.cut(cyl(bd / 2, bt, (0, 0, z_seat if s > 0 else -(z_seat + bt))))
        core = core.cut(cyl(P.RECESS_R, P.BRG_IN + 1, (0, 0, L / 2 - P.BRG_IN if s > 0 else -L / 2 - 1)))
    return tread, core


def roller_frames(hand):
    """(centre, axis) for each roller of a wheel whose axle is along Y through the origin; +axis = outboard end."""
    s45 = math.sin(math.radians(P.ROLL_ANGLE))
    out = []
    for i in range(P.N_ROLL):
        th = 2 * math.pi * i / P.N_ROLL
        rad = V(math.cos(th), 0, math.sin(th))
        tan = V(-math.sin(th), 0, math.cos(th))
        axis = (V(0, 1, 0) * P.C45 + tan * (hand * s45)).normalized()
        out.append((rad * P.ROLL_A, axis))
    return out


def place(shape, centre, axis):
    """Move a shape built along +Z at the origin to `centre` with its axis along `axis`."""
    z = V(0, 0, 1)
    ax = axis.normalized()
    k = z.cross(ax)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, z.dot(ax)))))
    s = shape
    if k.Length > 1e-9:
        s = s.rotate(V(0, 0, 0), k, ang)
    return s.translate(centre)


def _roller_clear(hand, extra=1.5):
    L2 = P.ROLL_L / 2
    ts = [-(L2 + 1) + (2 * L2 + 2) * i / 24 for i in range(25)]
    env = _rev([(roller_profile(max(-L2, min(L2, t))) + extra, t) for t in ts])
    return union([place(env, c, ax) for c, ax in roller_frames(hand)])


def _cup(c, ax, outboard):
    """One rod end: (stub + collar, pillar back to the face web, holes).
    Stub sits in the roller recess and bears on the 608 inner race; outboard cups get a hex channel from the
    face to a captured M8 nyloc deep in the stub, inboard cups a blind hole the rod bottoms in."""
    L2 = P.ROLL_L / 2
    d = ax if outboard else ax * -1
    e0 = c + d * (L2 - P.CUP_IN)
    body = cyl(P.CUP_R, P.CUP_IN + P.CUP_OUT, e0.toTuple(), d.toTuple())
    body = body.fuse(cyl(6.0, 1.0, (e0 - d * 1.0).toTuple(), d.toTuple()))
    sg = 1 if outboard else -1
    tip = c + d * (L2 + P.CUP_OUT / 2 + 0.5)
    yf = sg * (P.W_FACE - P.FACE_T / 2)
    pillar = cyl(P.CUP_R, abs(yf - tip.y), tip.toTuple(), (0, sg, 0))
    if outboard:
        rad = V(c.x, 0, c.z).normalized()
        u = (rad - d * rad.dot(d)).normalized()        # a hex flat faces the wheel's radial direction
        h0 = e0 + d * 1.0
        hexs = cq.Workplane(cq.Plane(origin=h0, xDir=d.cross(u), normal=d)).polygon(
            6, 13.3 / math.cos(math.pi / 6)).extrude(60.0).val()
        holes = cyl(P.ROD_D / 2 + 0.2, 4.0, (e0 - d * 1.5).toTuple(), d.toTuple()).fuse(hexs)
    else:
        holes = cyl(P.ROD_D / 2 + 0.15, P.CUP_IN + 4.5, (e0 - d * 1.5).toTuple(), d.toTuple())
    return body, pillar, holes


def _ang(k, n, off=0.0):
    return 2 * math.pi * k / n + off


def _hub_cuts():
    bolts = union([cyl(3.3, 400, (P.HUB_BOLT_R * math.cos(_ang(k, P.N_HUB_BOLT, math.pi / 8)), -200,
                                  P.HUB_BOLT_R * math.sin(_ang(k, P.N_HUB_BOLT, math.pi / 8))), (0, 1, 0))
                   for k in range(P.N_HUB_BOLT)])
    light = union([cyl(13.0, 400, (43 * math.cos(_ang(k, 6)), -200, 43 * math.sin(_ang(k, 6))), (0, 1, 0))
                   for k in range(6)])
    return bolts, light, hex_prism(12.9, 400, (0, -200, 0), (0, 1, 0))


def _lobes(hand, outboard):
    """(x, z) of each cup pillar on one hub face."""
    L2, out = P.ROLL_L / 2, []
    for c, ax in roller_frames(hand):
        tip = c + (ax if outboard else ax * -1) * (L2 + P.CUP_OUT / 2 + 0.5)
        out.append((tip.x, tip.z))
    return out


def _scallop(lobes, y0, t, r_base=96.0, r_lobe=14.0):
    """TTB-style rim: a base disc with a lobe round every cup, along +y from y0, trimmed to HUB_R."""
    shapes = [cyl(r_base, t, (0, y0, 0), (0, 1, 0))]
    for lx, lz in lobes:
        a = math.atan2(lz, lx)
        pts = [(lx + r_lobe * math.cos(2 * math.pi * k / 24), lz + r_lobe * math.sin(2 * math.pi * k / 24))
               for k in range(24)]
        pts += [(r_base * 0.97 * math.cos(a + da), r_base * 0.97 * math.sin(a + da)) for da in (-0.22, 0.22)]
        shapes.append(cq.Workplane("XZ", origin=(0, y0, 0)).polyline(_hull(pts)).close().extrude(-t).val())
    return union(shapes).intersect(cyl(P.HUB_R, t, (0, y0, 0), (0, 1, 0)))


def wheel_parts(hand):
    """One 10 in mecanum, wheel-local (axle along +Y through the roller centre plane, +Y outboard).

    Two PETG hub halves split at the roller centre plane, each a face web + drum ring + boss + spokes + cups;
    the inboard half also carries the 116T teeth (its face web is the belt's outboard flange). Three flat 1/8 in
    aluminum plates (inboard belt flange, centre disc, outboard disc) on 8 x 1/4-20 through-bolts clamp the stack.
    10 rollers, each 2 x 608 2RS on a fixed M8 threaded rod that threads through a captured nyloc in the
    outboard cup and bottoms in the inboard cup's blind hole; the outboard plate covers the channels.
    """
    clear = _roller_clear(hand)
    bolts, light, hexb = _hub_cuts()
    frames = roller_frames(hand)
    yc = P.W_CENTRE_PLATE[1]
    out = []
    for outboard in (True, False):
        sg = 1 if outboard else -1
        y0, y1 = (yc, P.W_FACE) if outboard else (P.W_PULLEY[0], -yc)
        r0, r1 = (yc, P.W_FACE) if outboard else (-P.W_FACE, -yc)
        fy = P.W_FACE - P.FACE_T if outboard else -P.W_FACE
        parts = [_scallop(_lobes(hand, outboard), fy, P.FACE_T).cut(cyl(18.0, P.FACE_T + 2, (0, fy - 1, 0), (0, 1, 0))),
                 tube(83.0, 72.0, r1 - r0, (0, r0, 0), (0, 1, 0)),
                 cyl(22.0, y1 - y0, (0, y0, 0), (0, 1, 0))]
        parts += [cq.Solid.makeBox(8.0, y1 - y0, 56.0, V(-4.0, y0, 18.0)).rotate(V(0, 0, 0), V(0, 1, 0), 60 * k + 30)
                  for k in range(6)]
        parts += [cyl(7.5, y1 - y0, (P.HUB_BOLT_R * math.cos(_ang(k, P.N_HUB_BOLT, math.pi / 8)), y0,
                                     P.HUB_BOLT_R * math.sin(_ang(k, P.N_HUB_BOLT, math.pi / 8))), (0, 1, 0))
                  for k in range(P.N_HUB_BOLT)]
        if not outboard:
            parts.append(tube(P.pd(P.T_WHEEL) / 2 - 0.57, 72.0, P.W_PULLEY[1] - P.W_PULLEY[0], (0, P.W_PULLEY[0], 0),
                              (0, 1, 0)))                 # teeth ring on the spokes
        cups, holes = [], []
        for c, ax in frames:
            b, pil, h = _cup(c, ax, outboard)
            cups.append(b)
            parts.append(pil)
            holes.append(h)
        hub = union(parts).cut(clear).fuse(union(cups))
        hub = hub.intersect(cyl(P.HUB_R, y1 - y0, (0, y0, 0), (0, 1, 0)))
        hub = hub.cut(union(holes)).cut(bolts).cut(light).cut(hexb).clean()
        hub = max(hub.Solids(), key=lambda s: s.Volume())          # drop slivers the nut channels shave off the rim
        if outboard:
            out.append(("Wheel hub outboard", hub, "Mecanum hub, outboard half",
                        "PETG, 5 walls, 40% gyroid, face down; 10 x M8 nyloc captured"))
        else:
            out.append(("Wheel hub inboard + 116T", hub, "Mecanum hub, inboard half + 116T pulley",
                        "PETG, 5 walls, 40% gyroid, teeth down"))
    for tag, (y0, y1), r in (("inner", P.W_INNER_PLATE, P.FLANGE_R), ("centre", P.W_CENTRE_PLATE, 83.0),
                             ("outer", P.W_OUTER_PLATE, None)):
        pl = (cyl(r, y1 - y0, (0, y0, 0), (0, 1, 0)) if r else _scallop(_lobes(hand, True), y0, y1 - y0))
        plate_light = union([cyl(8.0, 400, (68 * math.cos(_ang(k, 8)), -200, 68 * math.sin(_ang(k, 8))), (0, 1, 0))
                             for k in (1, 2, 3, 5, 6, 7)])  # plates only: between the bolts; 0 and 180 deg would
                                                          # meet the hub light holes, so >= 7.7 mm web everywhere
        pl = pl.cut(hexb).cut(bolts).cut(light).cut(plate_light)
        out.append((f"Wheel plate {tag} (1/8 Al)", pl, f"Mecanum {tag} plate (1/8 Al)",
                    "waterjet; 1/2 hex + 8 x 1/4-20 + 12 lightening holes"))
    return out


def rod():
    """Fixed M8 roller rod, local frame like roller_parts: from 0.2 short of the inboard blind-hole bottom to
    flush with the outboard nyloc."""
    L2 = P.ROLL_L / 2
    a0, a1 = -(L2 + 3.0 - 0.2), L2 - P.CUP_IN + 2.0 + 8.0
    return cyl(P.ROD_D / 2, a1 - a0, (0, 0, a0))


# ------------------------------------------------------------------ build
def build(log=print):
    rz = (P.RAIL_Z[0] + P.RAIL_Z[1]) / 2
    brg_holes = union([cyl(0.5625 * IN + 0.1, 1000, (sx * P.AX_X, -500, P.AXLE_Z), (0, 1, 0)) for sx in (-1, 1)])
    for sgn, side in ((1, "L"), (-1, "R")):
        oy = sgn * (P.OUTER_RAIL_Y[0] + P.OUTER_RAIL_Y[1]) / 2
        iy = sgn * (P.INNER_RAIL_Y[0] + P.INNER_RAIL_Y[1]) / 2
        tube_part(f"Outer rail {side} (1x2)", "x", -P.FRAME_X, P.FRAME_X, oy, rz, (1, 2), cuts=brg_holes)
        tube_part(f"Inner rail {side} (1x2)", "x", -(P.FRAME_X - P.RAIL_W), P.FRAME_X - P.RAIL_W, iy, rz, (1, 2),
                  cuts=brg_holes)
    for sx, end in ((1, "front"), (-1, "rear")):
        cx = sx * (P.FRAME_X - P.RAIL_W / 2)
        tube_part(f"End rail {end} (1x2)", "y", -P.OUTER_RAIL_Y[0], P.OUTER_RAIL_Y[0], cx, rz, (1, 2))
        # (corner gussets, bellypan and the Falcon side plates: brackets.py)
    tread, core = roller_parts()
    m8 = rod()
    for front in (True, False):
        for sgn, side in ((1, "L"), (-1, "R")):
            corner = ("F" if front else "R") + side
            ax = (P.AX_X if front else -P.AX_X)
            hand = 1 if (front == (sgn > 0)) else -1          # X pattern seen from above
            fx, fz = P.falcon_xz(front)
            yf = sgn * P.DRIVE_PLATE_Y[0]
            add(f"Falcon 500 {corner}", falcon(fx, fz, yf, sgn), "falcon", "drive", bom="Falcon 500 (owned)")
            band0 = P.YMID + P.W_PULLEY[0] if sgn > 0 else -(P.YMID + P.W_PULLEY[1])
            band0 += 0.5                                       # 15 mm belt centred on 16 mm of teeth
            add(f"Falcon pulley 12T {corner}", htd_pulley(P.T_PIN, 15.0, band0 - 3.0, fx, fz, bore=8.6),
                "alu", "drive", bom="WCP-0319 12T HTD 15 mm Falcon pulley")
            add(f"Belt {P.BELT_T}T {corner}", belt_loop((fx, fz), P.pd(P.T_PIN) / 2, (ax, P.AXLE_Z),
                                                      P.pd(P.T_WHEEL) / 2, 15.0, band0), "belt", "drive",
                bom=f"HTD 5M 15 mm belt, {P.BELT_T}T (WCP)")

            def put(s):
                s2 = s.translate(V(0, P.YMID, 0))
                s2 = s2 if sgn > 0 else s2.mirror("XZ")
                return s2.translate(V(ax, 0, P.AXLE_Z))
            for nm, shp, bom, note in wheel_parts(hand):
                kind = "stock" if "Al" in nm else "print"
                add(f"{nm} {corner}", put(shp), "alu" if kind == "stock" else "print_d", "drive", bom=bom, kind=kind,
                    note=note)
            for i, (c, axv) in enumerate(roller_frames(hand)):
                add(f"Roller tread {corner}{i:02d}", put(place(tread, c, axv)), "tpu", "drive",
                    bom="Mecanum roller tread (TPU 95A)", kind="print")
                add(f"Roller core {corner}{i:02d}", put(place(core, c, axv)), "print_d", "drive",
                    bom="Mecanum roller core (PETG)", kind="print", note="2 x 608 2RS pressed in")
                add(f"Roller rod {corner}{i:02d}", put(place(m8, c, axv)), "steel", "drive",
                    bom="M8 threaded rod, roller axle (cut 109 mm)", kind="stock",
                    note="Loctite 243 in the captured nyloc; slot the outboard end")
            # live axle: 1/2 hex in two flanged hex bearings (outer rail inner wall, inner rail outer wall)
            add(f"Bearing hex wheel {corner} outer", rail_bearing(ax, sgn * P.OUTER_RAIL_Y[0], P.AXLE_Z, sgn), "steel",
                "drive", bom="Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)")
            add(f"Bearing hex wheel {corner} inner", rail_bearing(ax, sgn * P.INNER_RAIL_Y[1], P.AXLE_Z, -sgn), "steel",
                "drive", bom="Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)")
            y_a, y_b = sgn * (P.INNER_RAIL_Y[0] + 0.0), sgn * P.OUTER_RAIL_Y[1]
            shaft = hex_prism(12.7, abs(y_b - y_a), (ax, y_a, P.AXLE_Z), (0, sgn, 0))
            add(f"Wheel axle {corner} (1/2 hex)", shaft, "steel", "drive", bom="1/2 in hex shaft, wheel axle (6 in)",
                kind="stock", note="tapped 10-32 both ends, button head + washer")
            for y0, y1, tag in ((P.INNER_RAIL_Y[1] + 1.6, P.WHEEL_Y[0], "inner"),
                                (P.YMID + P.W_OUTER_PLATE[1], P.OUTER_RAIL_Y[0] - 1.6, "outer")):
                if y1 - y0 > 0.3:
                    sp = cyl(12.0, y1 - y0 - 0.2, (ax, sgn * (y0 + 0.1), P.AXLE_Z), (0, sgn, 0)).cut(
                        hex_prism(12.9, 40, (ax, sgn * (y0 - 10), P.AXLE_Z), (0, sgn, 0)))
                    add(f"Axle spacer {tag} {corner}", sp, "print_d", "drive", bom="1/2 hex spacer (printed or stash)",
                        kind="print", note=f"{y1 - y0:.1f} mm")
    log("drive: built")
