"""Base frame (1x2 / 1x1 x 1/16 aluminum box tube, 1/8 in gussets) and the four drive corners:
Falcon 500 -> 12T WCP pulley -> 140T belt -> 120T printed into a 10 in printed mecanum (14 rollers).
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


# ------------------------------------------------------------------ printed mecanum
def roller_profile(t):
    R, r0 = P.WHEEL_R, P.ROLL_R0
    s = math.sin(math.radians(P.ROLL_ANGLE))
    return math.sqrt(R * R - (t * s) ** 2) - (R - r0)


def roller_parts():
    """TPU tread over a PETG core, local frame: axis along +Z, centred at the origin."""
    L = P.ROLL_L
    ts = [-L / 2 + L * i / 20 for i in range(21)]
    outer = [(roller_profile(t), t) for t in ts]
    inner = [(roller_profile(t) - 3.0, t) for t in ts]

    def rev(prof):
        pts = [(0, prof[0][1])] + prof + [(0, prof[-1][1])]
        return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()
    tread = rev(outer).cut(rev(inner))
    core = rev(inner)
    core = core.cut(cyl(2.8, L + 2, (0, 0, -L / 2 - 1)))
    bd, bt = P.ROLL_BRG
    for s in (-1, 1):
        core = core.cut(cyl(bd / 2 + 0.05, bt, (0, 0, s * L / 2 - (bt if s > 0 else 0))))
    return tread, core


def roller_frames(hand):
    """(centre, axis) for each roller of a wheel whose axle is along Y through the origin."""
    a = P.WHEEL_R - P.ROLL_R0
    s45 = math.sin(math.radians(P.ROLL_ANGLE))
    out = []
    for i in range(P.N_ROLL):
        th = 2 * math.pi * i / P.N_ROLL
        rad = V(math.cos(th), 0, math.sin(th))
        tan = V(-math.sin(th), 0, math.cos(th))
        axis = (V(0, 1, 0) * P.C45 + tan * (hand * s45)).normalized()
        out.append((rad * a, axis))
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


def _lug_ends(hand, inner):
    out = []
    for c, ax in roller_frames(hand):
        out.append((c + ax * (P.LUG_OFF if (ax.y > 0) != inner else -P.LUG_OFF), ax))
    return out


def _roller_clear(hand, extra=1.0):
    return union([place(cyl(P.ROLL_R0 + extra, P.ROLL_L + extra, (0, 0, -(P.ROLL_L + extra) / 2)), c, ax)
                  for c, ax in roller_frames(hand)])


def lug_plate(hand, inner, r_in):
    """Annulus r_in..100 on the lug plane plus a boss and web out to every roller axle end."""
    y0, y1 = (-P.W_LUG[1], -P.W_LUG[0]) if inner else P.W_LUG
    parts = [tube(100.0, r_in, y1 - y0, (0, y0, 0), (0, 1, 0)) if r_in else cyl(100.0, y1 - y0, (0, y0, 0), (0, 1, 0))]
    for end, ax in _lug_ends(hand, inner):
        parts.append(place(cyl(P.LUG_R, P.LUG_T, (0, 0, -P.LUG_T / 2)), end, ax))
        r_end = math.hypot(end.x, end.z)
        ang = math.atan2(end.z, end.x)
        parts.append(cq.Workplane("XZ", origin=(0, y1, 0)).polyline([
            (95 * math.cos(ang - 0.07), 95 * math.sin(ang - 0.07)),
            ((r_end + 2) * math.cos(ang - 0.05), (r_end + 2) * math.sin(ang - 0.05)),
            ((r_end + 2) * math.cos(ang + 0.05), (r_end + 2) * math.sin(ang + 0.05)),
            (95 * math.cos(ang + 0.07), 95 * math.sin(ang + 0.07))]).close().extrude(y1 - y0).val())
    return union(parts)


WHEEL_BOLTS = [(70.0 * math.cos(math.radians(30 + 60 * k)), 70.0 * math.sin(math.radians(30 + 60 * k)))
               for k in range(6)]


def wheel_parts(hand):
    """One 10 in mecanum, wheel-local (axle along +Y through the roller centre plane).

    Hub (one PETG print, 245 mm across): 120T pulley + both lug plates + drum + boss, 1/2 hex bore.
    Two 1/8 in aluminum plates sandwich it on 6 x M5 through-bolts; the inner plate is the belt's inboard
    flange. 14 rollers, each 2 x 685ZZ on an M5 x 100 axle through the lug bosses.
    """
    clear = _roller_clear(hand)
    pr = P.pd(P.T_WHEEL) / 2
    pul = cyl(pr - 0.57, P.W_PULLEY[1] - P.W_PULLEY[0], (0, P.W_PULLEY[0], 0), (0, 1, 0))
    flange = cyl(pr + 2.9, P.W_FLANGE[1] - P.W_FLANGE[0], (0, P.W_FLANGE[0], 0), (0, 1, 0))
    drum = tube(94.0, 82.0, P.W_LUG[0] * 2 + 0.2, (0, -P.W_LUG[0] - 0.1, 0), (0, 1, 0))
    boss = cyl(22.0, P.W_LUG[1] - P.W_PULLEY[0], (0, P.W_PULLEY[0], 0), (0, 1, 0))
    hub = union([pul, flange, drum, boss, lug_plate(hand, True, 40.0), lug_plate(hand, False, 0.0)])
    hub = hub.cut(union([place(cyl(2.7, P.ROLL_L + 40, (0, 0, -(P.ROLL_L + 40) / 2)), c, ax)
                         for c, ax in roller_frames(hand)]))
    hub = hub.cut(clear)
    hub = hub.cut(hex_prism(12.9, 400, (0, -200, 0), (0, 1, 0)))
    holes = union([cyl(2.75, 400, (bx, -200, bz), (0, 1, 0)) for bx, bz in WHEEL_BOLTS])
    light = union([cyl(14.0, P.W_PULLEY[1] - P.W_PULLEY[0] + 1, (48 * math.cos(math.radians(60 * k)), P.W_PULLEY[0] - 0.5,
                                                                  48 * math.sin(math.radians(60 * k))), (0, 1, 0))
                   for k in range(6)])
    hub = hub.cut(holes).cut(light)
    out = [("Wheel hub + 120T", hub, "Mecanum hub + 120T pulley (one print)", "PETG, 6 walls, 40% gyroid; 1/2 hex bore")]
    for tag, (y0, y1), r in (("inner", P.W_INNER_PLATE, pr + 2.9), ("outer", P.W_OUTER_PLATE, 98.0)):
        pl = cyl(r, y1 - y0, (0, y0, 0), (0, 1, 0)).cut(hex_prism(12.9, 40, (0, y0 - 10, 0), (0, 1, 0)))
        pl = pl.cut(holes).cut(clear)
        out.append((f"Wheel plate {tag} (1/8 Al)", pl, "Mecanum side plate (1/8 Al)", "router or waterjet; 6 x M5"))
    return out


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
        # U-shaped 1/8 in gussets top and bottom round each wheel end (end rail + outer and inner rails)
        for sgn, side in ((1, "L"), (-1, "R")):
            x_in = sx * (P.AX_X + P.WHEEL_R + 3.0)            # clear of the wheel
            xa, xb = sorted([sx * (P.FRAME_X - 100.0), sx * P.FRAME_X])
            xe0, xe1 = sorted([x_in, sx * P.FRAME_X])
            ys = sorted([sgn * P.INNER_RAIL_Y[0], sgn * P.OUTER_RAIL_Y[1]])
            yo = sorted([sgn * P.OUTER_RAIL_Y[0], sgn * P.OUTER_RAIL_Y[1]])
            yi = sorted([sgn * P.INNER_RAIL_Y[0], sgn * P.INNER_RAIL_Y[1]])
            for zt, tag in ((P.RAIL_Z[1], "top"), (P.RAIL_Z[0] - P.PLATE_T, "bottom")):
                if tag == "bottom":
                    g = box(xe0, xe1, *ys, zt, zt + P.PLATE_T).fuse(box(xa, xb, *yo, zt, zt + P.PLATE_T))
                else:
                    g = union([box(xe0, xe1, *ys, zt, zt + P.PLATE_T), box(xa, xb, *yo, zt, zt + P.PLATE_T),
                               box(xa, xb, *yi, zt, zt + P.PLATE_T)])
                add(f"Corner gusset {end} {side} {tag}", g, "alu", "frame", bom="Corner gusset (1/8 Al)", kind="stock",
                    note="3/16 rivets")
    belly = box(-P.FRAME_X + P.RAIL_W, P.FRAME_X - P.RAIL_W, -P.INNER_RAIL_Y[1], P.INNER_RAIL_Y[1],
                P.BELLY_Z - P.PLATE_T, P.BELLY_Z)
    for x in (-300, -200, 200, 300):
        belly = belly.cut(cyl(35, 10, (x, 0, P.BELLY_Z - 5)))
    for x0, x1, tag in ((-P.FRAME_X + P.RAIL_W, 0.0, "rear"), (0.0, P.FRAME_X - P.RAIL_W, "front")):
        add(f"Bellypan {tag} (1/8 Al)", belly.intersect(box(x0, x1, -500, 500, -10, 500)), "alu", "frame",
            bom="Bellypan half (1/8 Al)", kind="stock", note="rivets to the inner rails")

    tread, core = roller_parts()
    for front in (True, False):
        for sgn, side in ((1, "L"), (-1, "R")):
            corner = ("F" if front else "R") + side
            ax = (P.AX_X if front else -P.AX_X)
            hand = 1 if (front == (sgn > 0)) else -1          # X pattern seen from above
            fx, fz = P.falcon_xz(front)
            y_pl = P.DRIVE_PLATE_Y[0] if sgn > 0 else -P.DRIVE_PLATE_Y[1]
            pl = plate_from_circles(
                [(ax, P.AXLE_Z, 26), (fx, fz, 36), (ax - math.copysign(55, ax), P.RAIL_Z[0] + 4, 4),
                 (fx - math.copysign(40, ax), P.RAIL_Z[0] + 4, 4)], y_pl,
                holes=[(ax, P.AXLE_Z, 18.0), (fx, fz, 10.0)] +
                      [(fx + 25.4 * math.cos(math.radians(60 * k)), fz + 25.4 * math.sin(math.radians(60 * k)), 2.4)
                       for k in range(6)] +
                      [(x, P.RAIL_Z[0] + 12.7, 2.5) for x in (ax - math.copysign(45, ax), fx - math.copysign(30, ax))] +
                      [(x, P.RAIL_Z[1] - 12.7, 2.5) for x in (ax - math.copysign(45, ax), fx - math.copysign(30, ax))])
            add(f"Drive plate {corner} (1/8 Al)", pl, "alu", "drive", bom="Drive plate (1/8 Al)", kind="stock",
                note="rivets to the inner rail; Falcon on 4 x 10-32")
            yf = sgn * P.DRIVE_PLATE_Y[0]
            add(f"Falcon 500 {corner}", falcon(fx, fz, yf, sgn), "falcon", "drive", bom="Falcon 500 (owned)")
            band0 = P.YMID + P.W_PULLEY[0] if sgn > 0 else -(P.YMID + P.W_PULLEY[1])
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
                    bom="Mecanum roller core (PETG)", kind="print", note="2 x 685ZZ, M5 x 100 axle")
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
