"""Base frame (1x2 / 1x1 extrusion + 1/8 in plates) and the four drive corners:
Falcon 500 -> 12T WCP pulley -> 80T belt -> printed 72T/18T compound -> 140T belt -> printed 120T on a
12 in printed mecanum wheel (16 rollers) spinning on a dead 1/2 in axle between the inner and outer rails."""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, tube, hex_prism, union, belt_loop, PARTS

IN = P.IN


# ------------------------------------------------------------------ extrusion
def extrusion(axis, a0, a1, c1, c2, size=(1, 1), slots=True):
    """80/20-style 10-series bar along `axis` ('x','y','z') from a0 to a1.
    c1, c2 = centre coordinates of the cross-section on the two other axes (in order x,y,z skipping axis).
    size = (w along first other axis, h along second) in inches."""
    w, h = size[0] * IN, size[1] * IN
    others = [k for k in "xyz" if k != axis]
    lo = {axis: min(a0, a1), others[0]: c1 - w / 2, others[1]: c2 - h / 2}
    hi = {axis: max(a0, a1), others[0]: c1 + w / 2, others[1]: c2 + h / 2}
    s = box(lo["x"], hi["x"], lo["y"], hi["y"], lo["z"], hi["z"])
    if slots:
        cuts = []
        sw, sd = 6.6, 5.0
        for k, n_cells, span, other_len in ((0, round(size[1]), h, w), (1, round(size[0]), w, h)):
            ax_o, ax_slot = others[k], others[1 - k]   # slots on the faces normal to ax_o
            for face in (lo[ax_o], hi[ax_o]):
                for i in range(n_cells):
                    cpos = (lo[ax_slot] + IN / 2 + i * IN)
                    blo = {axis: lo[axis] - 1, ax_slot: cpos - sw / 2,
                           ax_o: face - sd if face == hi[ax_o] else face}
                    bhi = {axis: hi[axis] + 1, ax_slot: cpos + sw / 2,
                           ax_o: face if face == hi[ax_o] else face + sd}
                    cuts.append(box(blo["x"], bhi["x"], blo["y"], bhi["y"], blo["z"], bhi["z"]))
        s = s.cut(union(cuts))
    return s


def ext(name, axis, a0, a1, c1, c2, size=(1, 1), bom=None):
    prof = "1020" if max(size) > 1.5 else "1010"
    length = abs(a1 - a0)
    return add(name, extrusion(axis, a0, a1, c1, c2, size), "extr", "frame",
               bom=f"80/20 {prof} extrusion", kind="stock", note=f"{length / IN:.2f} in")


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
def htd_pulley(teeth, width, y0, x, z, flange=3.0, bore=0.0, hub=None):
    """Printed HTD 5M pulley in an XZ plane, teeth as round grooves, flanges both sides, along +y from y0."""
    pd = P.pd(teeth)
    od = pd - 1.14
    body = cyl(od / 2, width, (x, y0 + flange, z), (0, 1, 0))
    r_groove = 1.6
    grooves = []
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        gx, gz = x + (od / 2) * math.cos(a), z + (od / 2) * math.sin(a)
        grooves.append(cyl(r_groove, width + 0.2, (gx, y0 + flange - 0.1, gz), (0, 1, 0)))
    body = body.cut(union(grooves)) if teeth <= 80 else body
    fl = [cyl(od / 2 + 3.5, flange, (x, y0, z), (0, 1, 0)),
          cyl(od / 2 + 3.5, flange, (x, y0 + flange + width, z), (0, 1, 0))]
    s = union([body] + fl)
    if bore:
        s = s.cut(cyl(bore / 2, width + 2 * flange + 2, (x, y0 - 1, z), (0, 1, 0)))
    return s


# ------------------------------------------------------------------ COTS in the drive
def falcon(x, z, y_face, sgn):
    """Falcon 500: 60 mm body behind the face plane y_face, spline out through the plate."""
    d = -sgn                                  # body goes inboard
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
    inner = [(roller_profile(t) - 4.0, t) for t in ts]

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
    """(centre, axis) for each roller of a wheel whose axle is along Y, centred at the origin."""
    a = P.WHEEL_R - P.ROLL_R0
    s45 = math.sin(math.radians(P.ROLL_ANGLE))
    c45 = math.cos(math.radians(P.ROLL_ANGLE))
    out = []
    for i in range(P.N_ROLL):
        th = 2 * math.pi * i / P.N_ROLL
        rad = V(math.cos(th), 0, math.sin(th))
        tan = V(-math.sin(th), 0, math.cos(th))
        axis = (V(0, 1, 0) * c45 + tan * (hand * s45)).normalized()
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
    """Axle-end points (wheel-local, axle along Y through the origin) on one side of every roller."""
    ymid = (P.WHEEL_Y[0] + P.WHEEL_Y[1]) / 2
    half = P.ROLL_L / 2 + 5.0
    out = []
    for c, ax in roller_frames(hand):
        out.append((c + V(0, ymid, 0) + ax * (half if (ax.y > 0) != inner else -half), ax))
    return out


def _roller_clear(hand, extra=1.0):
    ymid = (P.WHEEL_Y[0] + P.WHEEL_Y[1]) / 2
    return union([place(cyl(P.ROLL_R0 + extra, P.ROLL_L + extra, (0, 0, -(P.ROLL_L + extra) / 2)), c + V(0, ymid, 0), ax)
                  for c, ax in roller_frames(hand)])


def lug_plane(inner):
    """y range of the lug plate: 6 mm, centred on the roller axle ends."""
    ymid = (P.WHEEL_Y[0] + P.WHEEL_Y[1]) / 2
    yl = ymid + (-1 if inner else 1) * (P.ROLL_L / 2 + 5.0) * math.cos(math.radians(P.ROLL_ANGLE))
    return yl - 3.0, yl + 3.0


def wheel_parts(hand):
    """One 12 in mecanum: printed cores (inner one is the 120T pulley) + lug plates printed as arcs.

    Inner core: 120T pulley + disc, inner FR8 pressed in from the pulley's inboard face.
    Outer core: flange disc + boss, outer FR8 pressed in from the outer face.
    Lug arcs (N_ARCS per side): annulus + a web and boss out to each roller axle end; 2 x M4 screws
    per arc into heat-set inserts in the core. The 16 M5 roller axles tie inner and outer arcs together.
    Returns [(name, shape, bom, note)] in wheel-local coordinates (axle along +Y through the origin).
    """
    out = []
    clear = _roller_clear(hand)
    for inner in (True, False):
        y0, y1 = lug_plane(inner)
        r_in = 62.0 if inner else 23.0
        plate = tube(100.0, r_in, y1 - y0, (0, y0, 0), (0, 1, 0))
        lugs, angs = [], []
        for end, ax in _lug_ends(hand, inner):
            lugs.append(place(cyl(P.LUG_R, 9.0, (0, 0, -4.5)), end, ax))
            r_end = math.hypot(end.x, end.z)
            ang = math.atan2(end.z, end.x)
            angs.append(ang)
            web = cq.Workplane("XZ", origin=(0, y1, 0)).polyline([
                (95 * math.cos(ang - 0.06), 95 * math.sin(ang - 0.06)),
                ((r_end + 2) * math.cos(ang - 0.045), (r_end + 2) * math.sin(ang - 0.045)),
                ((r_end + 2) * math.cos(ang + 0.045), (r_end + 2) * math.sin(ang + 0.045)),
                (95 * math.cos(ang + 0.06), 95 * math.sin(ang + 0.06))]).close().extrude(y1 - y0).val()
            lugs.append(web)
        ring = union([plate] + lugs)
        ring = ring.cut(union([place(cyl(2.7, P.ROLL_L + 30, (0, 0, -(P.ROLL_L + 30) / 2)),
                                     c + V(0, (P.WHEEL_Y[0] + P.WHEEL_Y[1]) / 2, 0), ax)
                               for c, ax in roller_frames(hand)]))
        ring = ring.cut(clear)
        # screw holes for the arc-to-core joint (2 per arc), between lugs
        step = 2 * math.pi / P.N_ROLL
        seam0 = angs[0] + step / 2
        r_scr = (r_in + 100.0) / 2 if inner else 52.0
        holes = []
        for k in range(P.N_ARCS):
            a0 = seam0 + k * 2 * math.pi / P.N_ARCS
            for f in (0.25, 0.75):
                a = a0 + f * 2 * math.pi / P.N_ARCS
                holes.append(cyl(2.2, 40, (r_scr * math.cos(a), y0 - 20, r_scr * math.sin(a)), (0, 1, 0)))
        ring = ring.cut(union(holes))
        side = "inner" if inner else "outer"
        for k in range(P.N_ARCS):
            a0 = seam0 + k * 2 * math.pi / P.N_ARCS
            a1 = a0 + 2 * math.pi / P.N_ARCS
            pts = [(0, 0)] + [(400 * math.cos(a0 + (a1 - a0) * i / 8), 400 * math.sin(a0 + (a1 - a0) * i / 8))
                              for i in range(9)]
            wedge = cq.Workplane("XZ", origin=(0, y1 + 10, 0)).polyline(pts).close().extrude(y1 - y0 + 20).val()
            arc = ring.intersect(wedge)
            out.append((f"Wheel lug arc {side} {k + 1}", arc, f"Mecanum lug arc ({side})",
                        "PETG-CF, 2 x M4 into heat-set inserts"))
        if inner:
            pul = htd_pulley(P.T_WHEEL, 15.0, P.P2_Y[0], 0, 0)
            disc = cyl(100.0, y0 - P.P2_Y[1] + 0.2, (0, P.P2_Y[1] - 0.2, 0), (0, 1, 0))
            core = union([pul, disc])
            core = core.cut(bearing_seat(0, P.P2_Y[0], 0, 1, 7.94))
            name, bom = "Wheel core inner + 120T", "Mecanum inner core + 120T pulley"
        else:
            yb1 = P.WHEEL_Y[1]
            core = cyl(70.0, 6.0, (0, y0 - 6.0, 0), (0, 1, 0)).fuse(cyl(21.0, yb1 - (y0 - 6.0), (0, y0 - 6.0, 0), (0, 1, 0)))
            core = core.cut(bearing_seat(0, yb1, 0, -1, 7.94))
            name, bom = "Wheel core outer", "Mecanum outer core"
        core = core.cut(cyl(7.0, 1000, (0, -500, 0), (0, 1, 0)))
        core = core.cut(union([cyl(2.6, 10, (h.Center().x, y0 - 10, h.Center().z), (0, 1, 0)) for h in holes]))
        core = core.cut(clear)
        out.append((name, core, bom, "PETG-CF; heat-set M4 inserts for the arcs"))
    return out


# ------------------------------------------------------------------ build
def build(log=print):
    rz = (P.RAIL_Z[0] + P.RAIL_Z[1]) / 2
    for sgn, side in ((1, "L"), (-1, "R")):
        oy = sgn * (P.OUTER_RAIL_Y[0] + P.OUTER_RAIL_Y[1]) / 2
        iy = sgn * (P.INNER_RAIL_Y[0] + P.INNER_RAIL_Y[1]) / 2
        holes = union([cyl(6.6, 1000, (sx * P.AX_X, -500, P.AXLE_Z), (0, 1, 0)) for sx in (-1, 1)])
        ext(f"Outer rail {side} (1x2)", "x", -P.FRAME_X, P.FRAME_X, oy, rz, (1, 2))
        PARTS[-1]["shape"] = PARTS[-1]["shape"].cut(holes)        # 1/2 in axle holes, drilled
        ext(f"Inner rail {side} (1x2)", "x", -(P.FRAME_X - P.RAIL_W), P.FRAME_X - P.RAIL_W, iy, rz, (1, 2))
        PARTS[-1]["shape"] = PARTS[-1]["shape"].cut(holes)
    for sx, end in ((1, "front"), (-1, "rear")):
        cx = sx * (P.FRAME_X - P.RAIL_W / 2)
        ext(f"End rail {end} (1x2)", "y", -P.OUTER_RAIL_Y[0], P.OUTER_RAIL_Y[0], cx, rz, (1, 2))
        ext(f"Battery cross member {end} (1x1)", "y", -P.INNER_RAIL_Y[0], P.INNER_RAIL_Y[0], sx * 118.0,
            P.RAIL_Z[0] + P.IN / 2, (1, 1))
    belly = box(-P.FRAME_X + P.RAIL_W, P.FRAME_X - P.RAIL_W, -P.INNER_RAIL_Y[1], P.INNER_RAIL_Y[1],
                P.BELLY_Z - P.PLATE_T, P.BELLY_Z)
    for x in (-300, -200, 200, 300):
        belly = belly.cut(cyl(35, 10, (x, 0, P.BELLY_Z - 5)))
    add("Bellypan (1/8 Al)", belly, "alu", "frame", kind="stock", note="waterjet")

    tread, core = roller_parts()
    for front in (True, False):
        for sgn, side in ((1, "L"), (-1, "R")):
            corner = ("F" if front else "R") + side
            ax = (P.AX_X if front else -P.AX_X)
            hand = 1 if (front == (sgn > 0)) else -1          # X pattern seen from above
            cx, cz = P.compound_xz(front)
            fx, fz = P.falcon_xz(front)
            # drive plate
            y_pl = sgn * P.DRIVE_PLATE_Y[0] if sgn > 0 else -P.DRIVE_PLATE_Y[1]
            pl = plate_from_circles(
                [(ax, P.AXLE_Z, 28), (cx, cz, 26), (fx, fz, 36), (ax - math.copysign(60, ax), P.RAIL_Z[0] + 4, 4),
                 (ax + math.copysign(40, ax), P.RAIL_Z[0] + 4, 4)], y_pl,
                holes=[(ax, P.AXLE_Z, 6.6), (cx, cz, 6.6), (fx, fz, 10.0)] +
                      [(fx + 25.4 * math.cos(math.radians(60 * k)), fz + 25.4 * math.sin(math.radians(60 * k)), 2.4)
                       for k in range(6)] +
                      [(ax + dx, P.RAIL_Z[0] + 12.7, 3.3) for dx in (-50, 30)] +
                      [(ax + dx, P.RAIL_Z[1] - 12.7, 3.3) for dx in (-50, 30)])
            add(f"Drive plate {corner} (1/8 Al)", pl, "alu", "drive", bom="Drive plate (1/8 Al, waterjet)",
                kind="stock")
            # Falcon + pinion
            yf = sgn * P.DRIVE_PLATE_Y[0]
            add(f"Falcon 500 {corner}", falcon(fx, fz, yf, sgn), "falcon", "drive", bom="Falcon 500 (owned)")
            p1 = P.P1_Y[0] if sgn > 0 else -P.P1_Y[1]
            p2 = P.P2_Y[0] if sgn > 0 else -P.P2_Y[1]
            add(f"Falcon pulley 12T {corner}", htd_pulley(P.T_PIN, 15.0, p1, fx, fz, flange=3.0, bore=8.6),
                "alu", "drive", bom="WCP-0319 12T HTD 15 mm Falcon pulley")
            # compound pulley 72T + 18T, printed, on two FR8 bearings and a dead 1/2 in bolt
            big = htd_pulley(P.T_C_BIG, 15.0, p1, cx, cz)
            small = htd_pulley(P.T_C_SMALL, 15.0, p2, cx, cz)
            hubc = cyl(16.0, abs(p2 - p1) + 21, (cx, min(p1, p2), cz), (0, 1, 0))
            y_in = sgn * P.P1_Y[0]                         # inboard face of the 72T
            comp = union([big, small, hubc]).cut(cyl(7.0, 400, (cx, -200, cz), (0, 1, 0)))
            comp = comp.cut(bearing_seat(cx, y_in, cz, sgn, 2 * 7.94))
            add(f"Compound pulley 72T/18T {corner}", comp, "print_d", "drive", bom="Compound pulley 72T/18T",
                kind="print", note="PA-CF or PETG-CF, 100% infill hub; FR8 + R8 pressed into the 72T")
            add(f"Bearing FR8 compound {corner}", fr8(cx, y_in, cz, sgn), "steel", "drive",
                bom="Bearing FR8 1/2 x 1-1/8 x 5/16 flanged (WCP-0781)")
            add(f"Bearing R8 compound {corner}", fr8(cx, y_in + sgn * 7.94, cz, sgn, flange=False), "steel", "drive",
                bom="Bearing R8 1/2 x 1-1/8 x 5/16 (no flange)")
            blk_y0 = yf
            blk = box(cx - 22, cx + 22, min(blk_y0, blk_y0 - sgn * 30), max(blk_y0, blk_y0 - sgn * 30), cz - 22, cz + 22)
            blk = blk.cut(cyl(6.6, 80, (cx, -40 + blk_y0, cz), (0, 1, 0)))
            add(f"Compound axle block {corner}", blk, "print_d", "drive", bom="Compound axle block", kind="print")
            y_out = (P.P2_Y[1] + 2) if sgn > 0 else -(P.P2_Y[1] + 2)
            add(f"Compound axle bolt {corner}", bolt(cx, cz, blk_y0 - sgn * 30, y_out, nut=True), "steel", "drive",
                bom="1/2-13 x 3-3/4 in grade 8 bolt + nylock")
            # belts
            add(f"Belt 80T {corner}", belt_loop((fx, fz), P.pd(P.T_PIN) / 2, (cx, cz), P.pd(P.T_C_BIG) / 2,
                                                15.0, p1 + 3.0 if sgn > 0 else p1 + 3.0), "belt", "drive",
                bom="HTD 5M 15 mm belt, 80T (WCP)")
            add(f"Belt {P.BELT2_T}T {corner}", belt_loop((cx, cz), P.pd(P.T_C_SMALL) / 2, (ax, P.AXLE_Z),
                                                       P.pd(P.T_WHEEL) / 2, 15.0, p2 + 3.0), "belt", "drive",
                bom=f"HTD 5M 15 mm belt, {P.BELT2_T}T (WCP)")
            # wheel
            def put(s):
                s2 = s if sgn > 0 else s.mirror("XZ")
                return s2.translate(V(ax, 0, P.AXLE_Z))
            for nm, shp, bom, note in wheel_parts(hand):
                add(f"{nm} {corner}", put(shp), "print_d", "drive", bom=bom, kind="print", note=note)
            ymid = (P.WHEEL_Y[0] + P.WHEEL_Y[1]) / 2
            for i, (c, axv) in enumerate(roller_frames(hand)):
                cc = c + V(0, ymid, 0)
                add(f"Roller tread {corner}{i:02d}", put(place(tread, cc, axv)), "tpu", "drive",
                    bom="Mecanum roller tread (TPU 95A)", kind="print")
                add(f"Roller core {corner}{i:02d}", put(place(core, cc, axv)), "print_d", "drive",
                    bom="Mecanum roller core (PETG)", kind="print", note="2 x 685ZZ, M5 x 100 axle")
            add(f"Bearing FR8 wheel {corner} inner", put(fr8(0, P.P2_Y[0], 0, 1)), "steel", "drive",
                bom="Bearing FR8 1/2 x 1-1/8 x 5/16 flanged (WCP-0781)")
            add(f"Bearing FR8 wheel {corner} outer", put(fr8(0, P.WHEEL_Y[1], 0, -1)), "steel", "drive",
                bom="Bearing FR8 1/2 x 1-1/8 x 5/16 flanged (WCP-0781)")
            y_head = sgn * (P.OUTER_RAIL_Y[1] + 0.1)
            y_end = -sgn * 0 + sgn * (P.INNER_RAIL_Y[0] - 0.1)
            add(f"Wheel axle bolt {corner}", bolt(ax, P.AXLE_Z, y_head, y_end), "steel", "drive",
                bom="1/2-13 x 8 in grade 8 bolt + nylock (dead axle)")
            sp_in = tube(12.0, 6.6, P.P2_Y[0] - P.DRIVE_PLATE_Y[1], (ax, sgn * P.DRIVE_PLATE_Y[1], P.AXLE_Z), (0, sgn, 0))
            add(f"Axle spacer inner {corner}", sp_in, "print_d", "drive", bom="Axle spacer", kind="print")
            sp_out = tube(12.0, 6.6, P.OUTER_RAIL_Y[0] - P.WHEEL_Y[1], (ax, sgn * P.WHEEL_Y[1], P.AXLE_Z), (0, sgn, 0))
            add(f"Axle spacer outer {corner}", sp_out, "print_d", "drive", bom="Axle spacer", kind="print")
    log(f"drive: built")
