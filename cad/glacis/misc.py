"""Everything else: towers and pivot bearings, the elevation motor, belt and angle pot, both reservoir tanks,
the rear manifold, main valve and in valves, the battery sleds, the back-bottom electronics bay, the smoke machine and its
ducts, FRC-style bumpers, wall standoffs, the recessed acrylic panels with their corner clips, and the
printed body-frame pieces."""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
import body as B
import speakers as SPK
import lightbar as LB
from lib import add, box, cyl, tube, hex_prism, union, t_slot
from drive import frame_member, end_tap, fr8, _hull, bearing_seat
import lib
import pneu_parts as PP

IN = P.IN
IY, OY = P.IY, P.OY                                    # inner / outer rail centre |y|


def qd_inline(tag, points, group="pneu", avoid=()):
    """One of the four interior quick disconnects (M-style coupler + female-thread plug) in the middle of a tube's
    longest straight run. Returns the cylinder to cut out of the tube there (Micah 2026-11-11: make the CAD BOM and the
    parts list match)."""
    from lib import PARTS
    segs = sorted([(V(*a), V(*b)) for a, b in zip(points, points[1:])], key=lambda s: -(s[1] - s[0]).Length)
    pick = None
    for a, b in segs:                                # longest straight run first, the first spot clear of every part
        if (b - a).Length < 90.0:
            continue
        for fr in (0.5, 0.35, 0.65, 0.25, 0.75):
            d = (b - a).normalized()
            q = a + (b - a) * fr
            if min((q - a).Length, (b - q).Length) < 42.0:
                continue
            dt = d.toTuple()
            body = union([hex_prism(22.0, 10.0, (q - d * 38.0).toTuple(), dt),
                          tube(11.5, 7.0, 32.0, (q - d * 28.0).toTuple(), dt)])
            plug = PP.m_plug_f(q + d * 22.0, -d)
            env = body.fuse(plug)
            e = env.BoundingBox()
            clash = False
            for s_ in avoid:                         # e.g. the gun at every swing angle
                s = s_.BoundingBox()
                if s.xmin < e.xmax and e.xmin < s.xmax and s.ymin < e.ymax and e.ymin < s.ymax and s.zmin < e.zmax and e.zmin < s.zmax:
                    if env.intersect(s_).Volume() > 1.0:
                        clash = True
                        break
            for p in ([] if clash else PARTS):
                s = p["shape"].BoundingBox()
                if s.xmin < e.xmax and e.xmin < s.xmax and s.ymin < e.ymax and e.ymin < s.ymax and s.zmin < e.zmax and e.zmin < s.zmax:
                    if not p["name"].startswith(("Tube", "Service loop")) and env.intersect(p["shape"]).Volume() > 1.0:
                        clash = True
                        break
            if not clash:
                pick = (q, d, dt, body, plug)
                break
        if pick:
            break
    if pick is None:                                 # no clear spot: the middle of the longest run, flagged in the log
        a, b = segs[0]
        d = (b - a).normalized()
        q = a + (b - a) * 0.5
        dt = d.toTuple()
        body = union([hex_prism(22.0, 10.0, (q - d * 38.0).toTuple(), dt),
                      tube(11.5, 7.0, 32.0, (q - d * 28.0).toTuple(), dt)])
        plug = PP.m_plug_f(q + d * 22.0, -d)
        print(f"QD {tag}: no clear spot, placed mid-run", flush=True)
        pick = (q, d, dt, body, plug)
    q, d, dt, body, plug = pick
    add(f"QD coupler {tag}", body, "brass", group,
        bom="Quick disconnect coupler: 1/4 NPT female M-style, brass, 300 psi (RUBY.Q)",
        note="supply side (the coupler has the shut-off); a push-to-connect in its back")
    add(f"QD plug {tag}", plug, "steel", group,
        bom="QD plugs + fill plug: 1/4 NPT female-thread M-style plugs, brass, 10 pcs (ZKZX B081F9J3VF)",
        note="on the downstream tube, a push-to-connect in its back")
    return cyl(9.0, 76.0, (q - d * 40.0).toTuple(), dt)


def add_split(name, shape, *a, start=None, **k):
    """A tube cut in two by its quick disconnect: one part per piece (supply side = the piece nearest `start`)."""
    sols = shape.Solids()
    if start is not None:
        sols = sorted(sols, key=lambda s: s.distance(cq.Vertex.makeVertex(*start)))
    if len(sols) == 1:
        return add(name, shape, *a, **k)
    for s, tag in zip(sols, ("supply", "downstream", "3", "4")):
        add(f"{name} ({tag})", s, *a, **k)


def tube_path(points, r=3.175):
    """DOT nylon tube along a polyline (cylinders + joint spheres)."""
    segs = []
    for a, b in zip(points, points[1:]):
        a, b = V(*a), V(*b)
        d = b - a
        if d.Length < 0.5:
            continue
        segs.append(cyl(r, d.Length, a.toTuple(), d.normalized().toTuple()))
    for p in points[1:-1]:
        segs.append(cq.Solid.makeSphere(r, V(*p), angleDegrees1=-90, angleDegrees2=90))
    return union(segs)


def post(name, x, y, z0, z1):
    """A 40x40 post standing on the inner rail (extrusion-4040): 2 x M5 end taps up into its foot from below, through
    10 mm access holes in the rail's bottom face (fitted before the bellypan; the bellypan has a hole under each), plus
    the cast corner brackets brackets.py fits where they clear."""
    side = "L" if y > 0 else "R"
    frame_member(name, "z", z0, z1, x, y, note="M5 end taps both ends")
    end_tap(f"{name} (4040)", 0, ((1, 1), (-1, -1)), f"Inner rail {side} (4040)", P.RAIL_Z[0],
            f"{name}: foot into the inner rail")
    return f"{name} (4040)"


def arm(name, x, sgn, post_name, top=P.ARM_TOP):
    """A 40x40 arm along y on top of its post, tapped down into the post's top: 2 x M5 from the arm's top face."""
    frame_member(name, "y", sgn * P.INNER_RAIL_Y[0], sgn * P.ARM_REACH, x, top - P.SMALL_W / 2,
                 note="10 mm access holes in its top face for the post's end taps")
    end_tap(post_name, 1, ((1, -1), (-1, 1)), f"{name} (4040)", top, f"{post_name}: top into {name}")
    return f"{name} (4040)"


# ------------------------------------------------------------------ pivot, elevation, angle sensor
def towers_and_pivot():
    px, pz = P.PIVOT
    x0, x1 = P.TOWER_X
    y0, y1 = P.BEARING_BLOCK_Y
    for sgn, side in ((1, "L"), (-1, "R")):
        yc = sgn * IY
        # Brophy Borealis (Micah, 2026-11-10): the tower stops under the in-well rail, the rail runs over it and the
        # bearing block sits on the rail; one 1/8 in plate on the outboard side wraps the tower and ties the three
        tw = post(f"Turret tower {side}", (x0 + x1) / 2, yc, P.RAIL_Z[1], P.DECK_RAIL["z"][0])
        # its top: 2 x M5 x 35 down through the in-well 20x20 rail (its centre line y IY + 10 is the tower's core line)
        end_tap(tw, 1, ((1, sgn), (-1, sgn)), f"Rail 20x20 well {'left' if sgn > 0 else 'right'}", P.DECK_RAIL["z"][1],
                f"{tw}: top, down through the in-well rail", spec="M5 x 35 socket head (down through the 20x20 rail)",
                access=False)
        # (the tower's base: end taps + the side plate's T-nuts; the tower plate up top: brackets.py)
        # bearing block from the tower's front face forward to the axle: two flanged 1/2 hex bearings
        blk = box(x1, px + 25.0, min(sgn * y0, sgn * y1), max(sgn * y0, sgn * y1), pz - 28, pz + 28)
        blk = blk.cut(cyl(9.0, 800, (px, -400, pz), (0, 1, 0)))
        blk = blk.cut(bearing_seat(px, sgn * y0, pz, sgn, 7.94)).cut(bearing_seat(px, sgn * y1, pz, -sgn, 7.94))
        add(f"Pivot bearing block {side}", blk, "print_d", "frame", bom="Pivot bearing block", kind="print",
            note="PETG, 5 walls, 40% gyroid; sits on the in-well rail (2 x M4 x 12 down into T-nuts in its top slot), "
                 "3 x 1/4-20 through the tower plate into heat-set inserts")
        for yb, d in ((y0, sgn), (y1, -sgn)):
            add(f"Pivot bearing {side} {yb:.0f}", fr8(px, sgn * yb, pz, d, hexbore=True), "steel", "frame",
                bom="Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)")
    # elevation: goBILDA 5203 (19.2:1, 312 rpm: backdrives easily when off) on a Spark MAX, 16T -> 112T HTD 5M 9 mm
    # belt on the right axle end (7:1, about 45 rpm free at the gun). Gearbox drawn at the 3-stage length (conservative)
    mx_, mz_ = P.ELEV_MOTOR_X, P.ELEV_MOTOR_Z
    ya, yb_ = P.ELEV_PULLEY_Y
    y_face = -P.ELEV_MOTOR_FACE_Y
    # the 8 mm REX output shaft (FTC) ends flush with the pinion, now further out toward the gun (belt centred between
    # the cradle plate and the bearing block)
    mot = cyl(18.0, 50.3, (mx_, y_face, mz_), (0, -1, 0)).fuse(cyl(18.75, 74.8, (mx_, y_face - 50.3, mz_), (0, -1, 0))).fuse(
        cyl(4.0, P.ELEV_MOTOR_FACE_Y - ya, (mx_, y_face, mz_), (0, 1, 0)))
    add("Elevation motor goBILDA 5203 19.2:1", mot, "black", "frame",
        bom="goBILDA 5203-2402-0019 Yellow Jacket 19.2:1, 312 rpm (FTC motor)", note="Spark MAX, brushed mode")
    # HTD 5M teeth under the 9 mm belt (y -(ya+11)..-(ya+2)), a 2 mm flange each side (Micah 2026-11-11: "add teeth
    # to the pulley")
    from lib import htd_teeth
    rf = P.pd(P.ELEV_T[0]) / 2 + 2.5
    pin = union([htd_teeth(P.ELEV_T[0], 9.0, -(ya + 11.0), mx_, mz_),
                 cyl(rf, 2.0, (mx_, -(ya + 2.0), mz_), (0, 1, 0)),
                 cyl(rf, (yb_ - ya) - 11.0, (mx_, -yb_, mz_), (0, 1, 0))]).cut(
        cyl(4.1, 40, (mx_, -yb_ - 5, mz_), (0, 1, 0)))
    add("Elevation pinion 16T", pin, "print_d", "frame", bom="Elevation pinion 16T HTD 9 mm (8 mm REX bore)", kind="print",
        note="printed from Micah's own pulley design; sits out on the shaft so the belt is centred between the cradle plate "
             "and the bearing block")
    yi, yo = y_face - 2.0, -P.Y_SLOT + 2.0                  # the bracket stays inside the gun well
    brk = union([box(px - 10.0, px + 25.0, yo, yi, mz_ - 20.0, P.DECK_RAIL["z"][0]),   # web up to the right rail
                 box(px - 10.0, mx_ + 26.0, yo, yi, mz_ - 24.0, mz_ + 24.0)])        # arm out to the motor
    brk = brk.cut(cyl(18.3, 60, (mx_, yi + 5, mz_), (0, -1, 0)))
    add("Elevation motor bracket", brk, "print", "frame", bom="Elevation motor bracket", kind="print",
        note="PETG, 5 walls, 40% gyroid; hangs from the right in-well rail (2 x M4 x 12 up into T-nuts in its bottom "
             "slot); slotted for belt tension")
    circles = [(px, pz, P.pd(P.ELEV_T[1]) / 2), (mx_, mz_, P.pd(P.ELEV_T[0]) / 2)]
    pts = []
    for (x, z, r) in circles:
        for k in range(72):
            a = 2 * math.pi * k / 72
            pts.append((x + r * math.cos(a), z + r * math.sin(a)))
    hull = _hull(pts)
    per = sum(math.hypot(hull[i][0] - hull[i - 1][0], hull[i][1] - hull[i - 1][1]) for i in range(len(hull)))
    w = cq.Workplane("XZ", origin=(0, -(ya + 2.0), 0)).polyline(hull).close().wires().val()
    face = cq.Face.makeFromWires(w.offset2D(0.9, "arc")[0], [w.offset2D(-0.9, "arc")[0]])
    add("Elevation belt", cq.Solid.extrudeLinear(face, V(0, -9.0, 0)), "belt", "frame",
        bom=f"HTD 5M 9 mm belt, {P.ELEV_BELT_T}T", note=f"{per:.0f} mm pitch length")
    # arm-angle pot on the end of the axle, outboard of the left bearing block (read by the main controller's ADC)
    yb = P.BEARING_BLOCK_Y[1]
    add("Pot coupler", cyl(9.0, 16.0, (px, yb + 1.0, pz), (0, 1, 0)).cut(cyl(7.45, 14.0, (px, yb + 0.5, pz), (0, 1, 0))),
        "print_d", "frame", bom="Pot coupler (1/2 hex to 1/4 in D)", kind="print")
    add("Arm-angle pot", cyl(12.0, 12.0, (px, yb + 25.0, pz), (0, 1, 0)).fuse(cyl(4.8, 8.0, (px, yb + 17.0, pz), (0, 1, 0))),
        "black", "frame", bom="10k linear pot, 1/4 in shaft (arm angle)")
    zb0 = max(pz - 30.0, P.Z_TOP + 1.0)                    # above the deck when the pivot is that high
    bri = box(px - 30, px + 30, yb + 37.0, yb + 40.2, zb0, pz + 10).cut(cyl(5.0, 10, (px, yb + 35, pz), (0, 1, 0)))
    for sx in (-1, 1):
        bri = bri.fuse(box(px + sx * 24 - 3, px + sx * 24 + 3, yb + P.PLATE_T + 0.2, yb + 37.0, zb0, pz + 10))
    add("Pot bracket", bri, "print", "frame", bom="Pot bracket", kind="print",
        note="screws through the left tower plate into the bearing block")
    return per


# ------------------------------------------------------------------ air
def _tank_shell(axis, c):
    L, R = P.TANK_L, P.TANK_D / 2
    x, y, z = c
    if axis == "x":
        wp = cq.Workplane("YZ", origin=(x - L / 2, 0, 0)).center(y, z)
    else:
        wp = cq.Workplane("XY", origin=(0, 0, z - L / 2)).center(x, y)
    return wp.circle(R).extrude(L).edges().fillet(30.0).val()


REAR_MAN = (-347.0, 93.5, 250.0)             # rear manifold centre, back bottom, behind the rear panel
REAR_DY = -120.0                             # the flat rear cross's y from REAR_MAN (2026-11-12)
MAIN_OUT = []
FILL = (-300.0, 55.0, 200.0)                 # valve cross centre (the tanks' side of the in valves), back bottom bay;
                                             # Borealis: 51 mm further back so the longer GOGO runs clear the rear Falcon
# the two in-valve runs off the valve cross: (flow direction, cannon, the chamber cross's branch axis, DIN plug side)
VALVE_RUNS = ((V(1, 0, 0), "A (top cannon)", V(0, 0, 1), -1), (V(0, -1, 0), "B (bottom cannon)", V(-1, 0, 0), -1))
LINE_RELIEF = V(0, 1, 0)                     # the valve cross's own 200 psi relief
CHECKS = []                                  # outlets of the two in valves (service loops start here)
RELIEF_AT = []                               # the chamber crosses' relief ports (the electronics shelf is notched round A's)
FOG_OUT = []                                 # fog splitter barb for the gun's smoke line


def air():
    L, R = P.TANK_L, P.TANK_D / 2
    tx, ty, tz = P.TANK_SIDE
    zp = tz - R - 8
    tank_out = {}
    for sgn, side in ((1, "left"), (-1, "right")):
        c = (tx, sgn * ty, tz)
        shell = _tank_shell("x", c)
        for dx in (-80.0, 0.0, 80.0):                       # weld bungs: a 1/4 NPT port opening down
            shell = shell.fuse(cyl(9.0, 12.0, (tx + dx, sgn * ty, tz - R + 4), (0, 0, -1))).cut(
                cyl(7.0, 11.0, (tx + dx, sgn * ty, zp - 0.5), (0, 0, 1)))
        add(f"Air tank {side} (6 L 200 psi)", shell, "tank", "pneu",
            bom="Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT (owner's AliExpress pick)")
        xb0 = tx                                          # middle port, outlet forward: clear of the arms and straps
        add(f"Tank push-to-connect {side}", PP.ptc_straight(V(xb0, sgn * ty, zp), (0, 0, -1)), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)", note="straight down (Micah 2026-11-12: no elbows)")
        tank_out[side] = (xb0, sgn * ty, zp - 18.0)
        for dx in (-80.0, 80.0):
            if side == "right" and dx > 0:            # Micah 2026-11-12: the rear manifold is one cross, so the tank
                                                     # transducer goes in a tank bung: the front one (the rear one is on the arm knee)
                add("Tank transducer 0-300 psi", PP.transducer(V(tx + dx, sgn * ty, zp), (0, 0, -1)), "steel", "pneu",
                    bom="Pressure transducer 0-300 psi, 0.5-4.5 V, 5 V, 1/8 NPT, stainless, with plug cable",
                    note="in the right tank's front bung (1/4 x 1/8 bushing)")
                continue
            add(f"Tank plug {side} {dx:.0f}", PP.npt_plug(V(tx + dx, sgn * ty, zp), (0, 0, -1)), "brass", "pneu",
                bom="1/4 NPT brass plug")
        for xb in P.TANK_POST_X:
            pn = post(f"Tank post {side} {xb:.0f}", xb, sgn * IY, P.RAIL_Z[1], P.RAIL_Z[1] + P.TANK_POST_H)
            arm(f"Tank arm {side} {xb:.0f}", xb, sgn, pn, top=P.TANK_ARM_TOP)
            # (the cast corner brackets at the joints: brackets.py)
            zt_ = P.TANK_ARM_TOP                           # the arm's top
            sad = box(xb - 20, xb + 20, sgn * ty - 68, sgn * ty + 68, zt_ + P.PLATE_T, tz).cut(
                cyl(R + 1.0, 60, (xb - 30, sgn * ty, tz), (1, 0, 0)))
            # a foot down onto the arm, clear of the tank line
            fy = sorted([sgn * max(ty - 68.0, P.INNER_RAIL_Y[0]), sgn * min(ty + 68.0, 210.0)])
            sad = sad.fuse(box(xb - 20, xb + 20, fy[0], fy[1], zt_, zt_ + P.PLATE_T + 0.5))
            # extrusion-4040: 2 x M5 x 12 button heads down into T-nuts in the arm's top slots (fitted before the tank),
            # heads in counterbores that open into the cradle
            for dx_, yy in ((-P.SLOT_OFF, ty - 30.0), (P.SLOT_OFF, ty + 40.0)):
                sad = sad.cut(cyl(P.M5["hole"], 30.0, (xb + dx_, sgn * yy, zt_ - 1.0), (0, 0, 1))).cut(
                    cyl(P.M5["access_r"], 80.0, (xb + dx_, sgn * yy, zt_ + P.PLATE_T + 4.5), (0, 0, 1)))
                lib.fastener("tnut", "M5 x 12 button head + T-nut", (xb + dx_, sgn * yy, zt_), (0, 0, -1),
                             f"Tank saddle {side} {xb:.0f}")
            add(f"Tank saddle {side} {xb:.0f}", sad, "print", "pneu", bom="Tank saddle", kind="print",
                note="2 x M5 x 12 into T-nuts in the arm's top slots (before the tank goes in), plus the cam strap")
        for xs in (tx - 40.0, tx + 40.0):
            add(f"Tank strap {side} {xs:.0f}", tube(R + 2.5, R + 0.5, 25.0, (xs - 12.5, sgn * ty, tz), (1, 0, 0)), "black",
                "pneu", bom="1 in cam-buckle strap")
    # rear manifold (200 psi zone), back bottom (Micah 2026-11-12): one ChillWaves cross lying flat. Fill check valve
    # straight out its back face through the rear panel with the fill plug on its end, the main ball valve straight
    # off its front face inside the robot (lever inside), the two tank lines into its sides. No tank relief here
    # (Micah's call): the valve cross's relief covers the tanks while the main valve is open. The tank transducer
    # is in the right tank's front bung (the rear one sits on the arm knee)
    mx, my, mz = REAR_MAN
    xo = P.rear_x(mz)
    cc, e14 = 16.5, 10.2                                   # cross centre to port face; NPT engagement
    xp = xo - e14 - 4.2                                    # the check valve's outer tip: the plug's hex sits outside the panel
    xc = xp + 49.4 - e14 + cc                              # the check valve's inner end threads into the cross's back face
    yc = my + REAR_DY                                      # clear of in valve A's coil
    cA = V(xc, yc, mz)
    yv, zv, xv = V(0, 1, 0), V(0, 0, 1), V(1, 0, 0)
    add("Rear manifold cross", PP.npt_cross(cA, (1, 0, 0), (0, 1, 0), c2e=cc), "brass", "pneu",
        bom="1/4 NPT brass cross (ChillWaves)", note="lying flat: fill out the back, main valve in front, tanks either side")
    tops = {}
    for tag, sg in (("right", -1), ("left", 1)):
        add(f"Rear manifold push-to-connect {tag} tank", PP.ptc_straight(cA + yv * (sg * cc), (0, sg, 0)), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
        tops[tag] = cA + yv * (sg * (cc + 18.0))
    # main valve (manual tank shut-off): a 1/4 ball valve on a close nipple straight off the cross's front face,
    # inside the robot, lever up (open all session, closed for transport and gun work)
    fa = cA + xv * cc
    add("Main valve nipple", PP.close_nipple(fa + xv * 0.9, (1, 0, 0)), "brass", "pneu",
        bom="1/4 NPT brass close nipple")
    vc = fa + xv * (1.8 + 22.5)
    add("Main valve (1/4 ball valve)", PP.ball_valve(vc, (1, 0, 0), (0, 0, 1)), "brass", "pneu",
        bom="Main valve: 1/4 NPT brass ball valve, FNPT x FNPT, 600 WOG (the old cannon's if it fits)",
        note="inside the robot behind the rear panel; lever along the line = open")
    add("Main valve push-to-connect", PP.ptc_straight(vc + xv * 22.5, (1, 0, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    MAIN_OUT[:] = [vc + xv * (22.5 + 18.0)]
    # fill: the male x male check valve straight out the cross's back face, through the rear panel, with the FEMALE
    # M-style plug threaded on its outer end (your universal coupler snaps on)
    add("Fill plug (M-style, female)", PP.m_plug_f(V(xp, yc, mz), (-1, 0, 0)), "steel", "pneu",
        bom="Fill plug: 1/4 NPT female-thread M-style plug, brass (ZKZX B081F9J3VF)", note="your universal coupler snaps on")
    x0, x1 = xp, xc - cc + e14
    add("Fill check valve", PP.check_valve_mm(V(x0, yc, mz), (1, 0, 0), length=x1 - x0), "brass", "pneu",
        bom="Fill check valve, 304 stainless, 1/4 NPT male x male (AliExpress)",
        note="through the rear panel; holds the tanks behind the open plug; flow arrow toward the manifold")
    # main valve (the tanks' shut-off, opens only while a chamber fills) into a brass cross; one in valve per chamber
    # off the cross meters its chamber against that chamber's transducer, and its closed seat is what keeps the
    # other cannon's shot from reaching it (no check valves). Main valve to in-valve seats is all brass at tank
    # pressure, so the cross carries its own 200 psi relief.
    fx, fy, fz = FILL
    vc = 16.5                                              # ChillWaves cross: ~33 mm across its ports
    sx1 = fx - vc - 1.8

    add("Valve cross push-to-connect", PP.ptc_straight(V(fx - vc, fy, fz), (-1, 0, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    add("Valve cross", PP.npt_cross(V(fx, fy, fz), (1, 0, 0), (0, 1, 0), c2e=vc), "brass", "pneu",
        bom="1/4 NPT brass cross (ChillWaves)", note="G1/4 adapters straight into the in valves")
    add("Line relief valve 200 psi", PP.relief_valve(V(fx, fy, fz) + LINE_RELIEF * vc, LINE_RELIEF), "brass", "pneu",
        bom="Relief valve 200 psi, 1/4 NPT male, ASME, ring pull, brass (Loner ST25-1A200, B0F4QP9CG2)")
    CHECKS.clear()
    RELIEF_AT.clear()
    for d, tag, up, plug in VALVE_RUNS:
        # Brophy Borealis (Micah via the Mac chat): GOGO GPG-M03 in valves, G1/4 ports, a G1/4 x 1/4 NPT hex nipple in
        # each, straight into the valve cross; coil up, flow toward the chamber. The chamber's transducer and
        # 200 psi relief sit on a brass cross right after it; one hose (with a QD) runs on to the chamber's bung
        a0 = V(fx, fy, fz) + d * (vc + 11.8)              # the valve's inlet face
        add(f"In valve {tag} inlet nipple", PP.hex_nipple_g(a0, -d), "steel", "pneu",
            bom="G1/4 BSPP male x 1/4 NPT male hex nipple, 304")
        add(f"In valve {tag}", PP.solenoid_gogo(a0 + d * 20.0, d, (0, 0, 1), plug=plug), "brass", "pneu",
            bom="In valve: GOGO GPG-M03 2/2 NC direct-acting 12 V DC, G1/4, 2.5 mm", note="coil up; flow arrow toward the chamber")
        o = a0 + d * 40.0                                  # the outlet face
        add(f"In valve {tag} outlet nipple", PP.hex_nipple_g(o, d), "steel", "pneu",
            bom="G1/4 BSPP male x 1/4 NPT male hex nipple, 304")
        ce = 16.5                                          # the ChillWaves cross is ~33 mm across its ports
        c = o + d * (11.8 + ce)                             # A's cross sits beside the left tower: its branches stand
                                                           # up and down (the shelf is notched for the relief); B's lie
                                                           # flat (down, its relief would hit the main breaker)
        if up.z > 0.5:
            RELIEF_AT.append(c - up * ce)
        add(f"Chamber cross {tag}", PP.npt_cross(c, d, up, c2e=ce), "brass", "pneu", bom="1/4 NPT brass cross (ChillWaves)",
            note="the chamber's transducer and relief on its branches, the hose on")
        add(f"Chamber transducer {tag}", PP.transducer(c + up * ce, up), "steel", "pneu",
            bom="Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT (+ 1/4 x 1/8 bushing)")
        add(f"Chamber relief valve 200 psi {tag}", PP.relief_valve(c - up * ce, -up), "brass", "pneu",
            bom="Relief valve 200 psi, 1/4 NPT male, ASME, ring pull, brass (Loner ST25-1A200, B0F4QP9CG2)",
            note="the chamber's own relief and hand bleed (the in valve's closed seat seals it off from the tanks)")
        add(f"Chamber cross {tag} push-to-connect", PP.ptc_straight(c + d * ce, d), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
        CHECKS.append(c + d * (ce + 18.0))
    # tubes: tanks -> rear manifold, rear manifold -> main valve
    for side, dy in (("left", 35.0), ("right", -45.0)):
        t = tank_out[side]
        sg = 1 if side == "left" else -1
        # inboard of the rail posts (|y| 104+) and outside the gun, over the Falcons, then up between the sled
        # posts and across to the manifold above the sled rails
        xr = -295.0 if sg > 0 else -330.0                 # the right one rises behind service loop B
        e = tops[side]
        zr = 282.0 if sg > 0 else 245.0                   # the left one passes over in valve A's DIN plug
        # down out of the tank's straight push-to-connect, across, up and over, then down beside the flat cross and
        # in along y (no quick disconnects, Micah 2026-11-12)
        yt_ = 84.5                                         # inboard of the 40x40 posts (|y| 89.35+)
        pts = [t, (t[0], t[1], t[2] - 15.0), (t[0], sg * yt_, max(262.0, zr)), (xr, sg * yt_, zr), (xr, sg * yt_, 330.0),
               (e.x, sg * yt_, 330.0), (e.x, sg * yt_, e.z), e.toTuple()]
        add_split(f"Tube tank {side}", tube_path(pts), "tube", "pneu", start=tuple(pts[0]), bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")
    m0 = MAIN_OUT[0]                                       # forward out of the main valve, down, back under the valve cross
    tf = [m0.toTuple(), (m0.x + 15.0, m0.y, mz), (m0.x + 15.0, m0.y, 170.0), (fx - vc - 40.0, fy, 170.0),
          (fx - vc - 40.0, fy, fz), (fx - vc - 18.0, fy, fz)]
    add_split("Tube main valve to cross", tube_path(tf), "tube", "pneu", start=tf[0], bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")


# ------------------------------------------------------------------ fog
def fog():
    """Custom 12 V fogger in the front bay, printed 1 -> 3 splitter: a silicone line up into the gun's core (to the
    smoke collar round the barrels), one flexible line to a vent under the front bumper and one along the centreline
    to a vent down through the bellypan near the back (smoke trails front and back)."""
    (x0, x1), (y0, y1), (z0, z1) = P.FOG_BOX
    # custom 12 V fogger: two 200 W cast heater cores on an aluminum bracket (never on a print), a peristaltic pump
    # each from a printed fluid tank, and a 5015 blower that pushes the fog into the splitter
    add("Smoke machine tray", box(x0 - 6, x1 + 6, y0 - 6, y1 + 6, P.BELLY_Z, z0 + 20).cut(box(x0, x1, y0, y1, z0, z0 + 21)).cut(
        box(x0 + 20, x1 - 20, y0 + 15, y1 - 15, P.BELLY_Z - 1, z0 + 1)),
        "print", "power", bom="Smoke machine tray", kind="print")
    add("Fog fluid tank", box(x0 + 4, x0 + 88, y0 + 6, y1 - 6, z0, z0 + 58).cut(box(x0 + 7, x0 + 85, y0 + 9, y1 - 9, z0 + 3, z0 + 59)),
        "print", "power", bom="Fog fluid tank (printed, about 400 mL)", kind="print", note="water-based glycol fog fluid only")
    zb = z0 + 72.0
    for k, sy in enumerate((1,)):                          # one core for now: the right half of the tray and the
        yp0, yp1 = sorted([sy * 14.0, sy * 50.0])            # bracket stay free for a second core and pump
        add(f"Fog pump {'L' if sy > 0 else 'R'}", box(x0 + 94, x0 + 150, yp0, yp1, z0, z0 + 34), "black", "power",
            bom="Fog fluid pump: Kamoer NKP 12 V peristaltic")
        yc0, yc1 = sorted([sy * 6.0, sy * 38.0])
        add(f"Fog heater core {'L' if sy > 0 else 'R'}", box(x1 - 104, x1 - 7, yc0, yc1, zb + 3, zb + 39), "steel", "power",
            bom="Fog heater core 12 V 200 W (cast, 97 x 32 x 36 mm)", note="ceramic-fiber wrap; K probe clamped on (firmware cut at 245 C)")
    add("Fog heater bracket (1/8 Al)", box(x1 - 110, x1 - 2, y0 + 4, y1 - 4, zb, zb + 3), "alu", "power",
        bom="Fog heater bracket (1/8 Al)", kind="stock")
    for (xp, yp) in ((x0 + 92, y0 + 6), (x0 + 92, y1 - 6), (x1 - 8, y0 + 6), (x1 - 8, y1 - 6)):   # clear of tank and pumps
        add(f"Fog bracket standoff {xp:.0f} {yp:.0f}", cyl(3.0, zb - z0, (xp, yp, z0), (0, 0, 1)), "alu", "power",
            bom="M5 aluminum standoff (stash)")
    cx = (x0 + x1) / 2
    add("Fog blower 5015", box(cx - 25, cx + 25, -25, 25, z1, z1 + 14), "black", "power", bom="12 V 5015 blower",
        note="pushes the fog from the cores into the splitter")
    hub = box(cx - 22, cx + 22, -28, 28, z1 + 14, z1 + 44).cut(box(cx - 19, cx + 19, -25, 25, z1 + 13, z1 + 41))
    barbs = []
    for sy in (1, -1):                                     # trail lines out the sides, the gun line out the top
        hub = hub.fuse(tube(11.0, 8.5, 16.0, (cx, sy * 28.0, z1 + 29), (0, sy, 0)))
        barbs.append((cx, sy * 44.0, z1 + 29))
    hub = hub.fuse(tube(9.8, 7.5, 18.0, (cx - 8, 0, z1 + 44), (0, 0, 1)))         # 3/4 in barb (was 1/2) for the 3/4 x 1 line
    add("Fog splitter 1-3", hub, "print", "power", bom="Fog splitter 1 -> 3 (printed)", kind="print",
        note="22 mm barbs for the two trail tubes, a 3/4 in barb (15 mm bore) for the gun's 3/4 in silicone line")
    FOG_OUT[:] = [V(cx - 8, 0, z1 + 62)]
    # front: down through the bellypan just ahead of the machine
    side_b = barbs[0]
    vx, vy = P.FOG_VENTS[0]
    add("Fog vent front", tube(13.0, 10.0, 14.0, (vx, vy, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1)).fuse(
        tube(16.0, 10.0, 3.0, (vx, vy, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1))), "print", "power",
        bom="Fog vent nozzle (under bumper)", kind="print", note="through a hole in the bellypan")
    add("Fog tube front", tube_path([side_b, (side_b[0] + 15, vy, side_b[2] - 10.0), (vx, vy, P.BELLY_Z + 10.0),
                                     (vx, vy, P.BELLY_Z - P.PLATE_T)], r=11.0),
        "tube", "power", bom="Fog tube (owner's flexible tube)", kind="stock")
    # back: along the bellypan centreline, under the gun's swing, down through the bellypan just ahead of the
    # electronics bay (the trail comes out underneath, not straight out the back)
    side_b = barbs[1]
    rx, ry = P.FOG_VENTS[1]
    add("Fog vent rear", tube(13.0, 10.0, 14.0, (rx, ry, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1)).fuse(
        tube(16.0, 10.0, 3.0, (rx, ry, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1))), "print", "power",
        bom="Fog vent nozzle (under the belly)", kind="print", note="through a hole in the bellypan")
    # 2026-11-11 (Micah: "the fog tube can move to run above stuff"): it runs high along the centreline at z 235,
    # under the gun-well floor and over every board, then drops straight to the vent (searched clear of every solid)
    zt_ = 235.0
    add("Fog tube rear", tube_path([side_b, (side_b[0], -64.0, side_b[2]), (side_b[0], -64.0, zt_), (150.0, -64.0, zt_),
                                    (150.0, ry, zt_), (rx, ry, zt_), (rx, ry, P.BELLY_Z + 10.0),
                                    (rx, ry, P.BELLY_Z - P.PLATE_T)], r=11.0),
        "tube", "power", bom="Fog tube (owner's flexible tube)", kind="stock")


# ------------------------------------------------------------------ power + controls
def batteries_and_electronics():
    L, W, H = P.BATT
    zs = P.ARM_TOP                                         # sled rail top
    for sgn, side in ((1, "left"), (-1, "right")):
        for xr in P.SLED_POST_X:
            pn = post(f"Sled post {side} {xr:.0f}", xr, sgn * IY, P.RAIL_Z[1], P.RAIL_Z[1] + P.POST_H)
            arm(f"Sled rail {side} {xr:.0f}", xr, sgn, pn)
        ya, yb = sorted([sgn * (P.BATT_Y[0] - 3.0), sgn * (P.BATT_Y[1] + 4.0)])
        sled = box(P.BATT_X[0] - 4.0, P.BATT_X[1] + 4.0, ya, yb, zs, P.BATT_Z)
        for (x0, x1) in ((P.BATT_X[0] - 4.0, P.BATT_X[0] - 2.0), (P.BATT_X[1] + 2.0, P.BATT_X[1] + 4.0)):
            sled = sled.fuse(box(x0, x1, ya, yb, P.BATT_Z, P.BATT_Z + 25.0))
        yin = sgn * (P.BATT_Y[0] - 1.0)
        sled = sled.fuse(box(P.BATT_X[0] - 4.0, P.BATT_X[1] + 4.0, min(yin, yin - sgn * 2.0), max(yin, yin - sgn * 2.0),
                             P.BATT_Z, P.BATT_Z + 25.0))
        yh = sgn * (P.BATT_Y[1] + 4.0)
        sled = sled.fuse(box(-280.0, -210.0, min(yh, yh + sgn * 8.0), max(yh, yh + sgn * 8.0), zs, zs + 14.0))
        add(f"Battery sled {side}", sled, "print", "power", bom="Battery sled (pulls out its side's battery door)", kind="print")
        y0, y1 = sorted([sgn * P.BATT_Y[0], sgn * P.BATT_Y[1]])
        b = box(P.BATT_X[0], P.BATT_X[1], y0, y1, P.BATT_Z, P.BATT_Z + H - 12)
        for dx in (25.0, L - 25.0):
            b = b.fuse(box(P.BATT_X[0] + dx - 8, P.BATT_X[0] + dx + 8, y0 + 25, y0 + 45, P.BATT_Z + H - 12, P.BATT_Z + H))
        add(f"FRC battery {side}", b, "battery", "power", bom="FRC 12 V 18 Ah battery (owned, MK ES17-12)")
        add(f"Anderson SB50 {side}", box(-252.0, -232.0, min(sgn * 113.0, sgn * 137.0), max(sgn * 113.0, sgn * 137.0),
                                          P.BATT_Z + 12.2, P.BATT_Z + 37.2), "red", "power",
            bom="Anderson SB50 pair + 6 AWG contacts (stash)")
    # Everything on the bellypan (Micah, 2026-11-11: "try to put all the electronics on the bottom plate which can also
    # be cnc'ed"): the printed shelf is gone. Each part's spot was found clear of every other part (the pneumatics over
    # the rear bay, the fog tube, the vents, the inner plates); boards stand on 6 mm M3 nylon standoffs. The CNC'd
    # bellypan carries each footprint as a light engraving (brackets.bellypan), so the holes are drilled to the real part
    zb = P.BELLY_Z
    ELEC_MARKS.clear()
    add("Power distribution (REV PDH)", box(-370.0, -267.0, -86.5, 86.5, zb, zb + 36), "black", "power",
        bom="REV PDH (owned) + ATO breakers / fuses (stash)")
    ELEC_MARKS.append(("PDH", -370.0, -267.0, -86.5, 86.5))
    # the main breaker is the robot's on / off switch and its kill switch (Micah 2026-11-12: no rear E-stop, the
    # breaker's red trip button already kills everything, logic rail included): its face through a hole in the panel
    by, bz = BREAKER
    xi = P.rear_x(bz) + P.CLIP_T + 4.0                     # behind the acrylic, its face parallel to the slanted panel
    lean = math.degrees(math.atan((P.rear_x(bz + 18.0) - P.rear_x(bz - 18.0)) / 36.0))
    brk_ = box(0.0, 41.0, -26.0, 26.0, -18.0, 18.0).rotate(V(0, 0, 0), V(0, 1, 0), lean).translate(V(xi, by, bz))
    add("Main breaker 120 A", brk_, "black", "power",
        bom="120 A main breaker (stash)", note="rear panel, bottom strip: the on / off switch and the kill button (red trip); its face "
        "through a 42 mm hole, 2 x #10-32 through its ears and the panel")
    boards = [
              ('Main controller ESP32-P4 + C6 (Waveshare)', -259, -203, -47, 41, 6, 18, 'pcb',
               'Main controller: Waveshare ESP32-P4-Module-DEV-KIT, ESP32-P4 + ESP32-C6 (B0FDWZ6KWT)'),
              ('ESP32-S3 safety node', -263, -194, 42, 70, 6, 15, 'pcb',
               'ESP32-S3-DevKitC-1 N8R8 (owned)'),
              ('PWM expander PCA9685', -203, -177, -31, 31, 6, 12, 'pcb',
               'PWM expander: PCA9685 16-channel, I2C (Dorhea B07RMTN4NZ)'),
              ('ADS1115 ADC 1 (pressures)', -111, -83, -25, -7, 6, 6, 'pcb',
               'ADS1115 16-bit 4-channel ADC module, I2C, 2-pack (B0DZSP4CG8)'),
              ('ADS1115 ADC 2 (battery and bus volts)', -79, -51, -25, -7, 6, 6, 'pcb',
               'ADS1115 16-bit 4-channel ADC module, I2C, 2-pack (B0DZSP4CG8)'),
              ('Spark MAX (elevation)', -263, -193, -83, -48, 0, 25, 'black',
               'REV Spark MAX (owned)'),
              ('Valve arm relay 40 A', -15, 13, -29, -11, 0, 36, 'black',
               '12 V 40 A SPDT relay + socket'),
              # 2026-11-11 (Micah: make the CAD BOM and the parts list match): the old combined
              # driver block split into the real modules, each spot searched clear of everything
              ('Relay driver board (ULN2803A)', 43, 83, 36, 66, 6, 12, 'pcb',
               'ULN2803A Darlington driver on a perfboard: the relay coils'),
              ('Fog relay 40 A core 1', 49, 77, 15, 33, 0, 36, 'black',
               '12 V 40 A SPDT relay + socket (fog core)'),
              ('Fog relay 40 A core 2', 66, 94, 69, 87, 0, 36, 'black',
               '12 V 40 A SPDT relay + socket (fog core, spare)'),
              ('Valve MOSFET module 1 (firing valve A)', 97, 131, 78, 95, 6, 10, 'pcb',
               'MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger (valve / contactor driver)'),
              ('Valve MOSFET module 2 (firing valve B)', 46, 80, -30, -13, 6, 10, 'pcb',
               'MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger (valve / contactor driver)'),
              ('Valve MOSFET module 3 (in valve A)', 85, 119, -30, -13, 6, 10, 'pcb',
               'MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger (valve / contactor driver)'),
              ('Valve MOSFET module 4 (in valve B)', 136, 170, 78, 95, 6, 10, 'pcb',
               'MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger (valve / contactor driver)'),
              ('Valve MOSFET module 5 (contactor (controller))', 151, 168, 36, 70, 6, 10, 'pcb',
               'MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger (valve / contactor driver)'),
              ('Valve MOSFET module 6 (contactor (safety node))', 154, 171, -46, -12, 6, 10, 'pcb',
               'MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger (valve / contactor driver)'),
              ('Fog and light MOSFET module 1 (light bar)', 175, 215, 69, 89, 6, 20, 'pcb',
               'MOSFET switch module 5-36 V 15 A with heat sink (light bar / fog)'),
              ('Fog and light MOSFET module 2 (fog heater)', 124, 144, -87, -47, 6, 20, 'pcb',
               'MOSFET switch module 5-36 V 15 A with heat sink (light bar / fog)'),
              ('Fog and light MOSFET module 3 (fog heater 2)', 148, 168, -93, -53, 6, 20, 'pcb',
               'MOSFET switch module 5-36 V 15 A with heat sink (light bar / fog)'),
              ('Fog and light MOSFET module 4 (fog pump)', 220, 260, 69, 89, 6, 20, 'pcb',
               'MOSFET switch module 5-36 V 15 A with heat sink (light bar / fog)'),
              ('Fog and light MOSFET module 5 (fog blower)', 172, 212, -90, -70, 6, 20, 'pcb',
               'MOSFET switch module 5-36 V 15 A with heat sink (light bar / fog)'),
              ('Thermocouple amp MAX6675', 283, 298, -15, 10, 6, 8, 'pcb',
               'Thermocouple amp MAX6675 module (+ K probe on the core)'),
              ('Inline ATO fuse holder (logic tap)', -263, -218, 72, 87, 0, 15, 'red',
               'Inline ATO fuse holder + 5 A fuse'),
              ('DS18B20 probe electronics', -170, -130, 14, 22, 0, 6, 'steel',
               'DS18B20 waterproof temperature probe'),
              ('DS18B20 probe battery bay', -191, -183, 57, 97, 0, 6, 'steel',
               'DS18B20 waterproof temperature probe'),
              ('DS18B20 probe fogger', 301, 309, -30, 10, 0, 6, 'steel',
               'DS18B20 waterproof temperature probe'),
              ('Buck 12-5 V 20 A', 97, 147, 13, 69, 0, 25, 'black',
               '12->5 V 20 A buck (B089M5R3NJ)'),
              ('Logic supply 5 V (buck-boost)', 125, 150, -43, -17, 6, 10, 'pcb',
               'Logic supply: 5 V 5 A buck-boost module, 3.6-32 V in'),
    ]
    for name, x0, x1, y0, y1, so, h, col, bom in boards:
        y0, y1 = _in_bay(y0, y1)
        add(name, box(x0, x1, y0, y1, zb + so, zb + so + h), col, "power", bom=bom,
            note="heat-staked onto its printed board tray" if so else "screwed to the bellypan (M4)")
        ELEC_MARKS.append((name.split(" (")[0], x0, x1, y0, y1))
        if so:      # a printed tray (Micah: "things like standoffs we can 3d print"): 2 mm base, four 6 mm posts with
            # pegs a soldering iron mushrooms over the board's holes; 2 x M4 x 12 up through the bellypan into inserts
            tr = box(x0, x1, y0, y1, zb, zb + 2.0)
            for cx, cy in ((x0 + 4.0, y0 + 4.0), (x1 - 4.0, y0 + 4.0), (x0 + 4.0, y1 - 4.0), (x1 - 4.0, y1 - 4.0)):
                tr = tr.fuse(cyl(3.5, so - 2.0, (cx, cy, zb + 2.0)))
            long_x = (x1 - x0) >= (y1 - y0)
            for k in (-1, 1):
                hx = (x0 + x1) / 2 + (k * (x1 - x0) / 4 if long_x else 0.0)
                hy = (y0 + y1) / 2 + (0.0 if long_x else k * (y1 - y0) / 4)
                tr = tr.fuse(cyl(4.5, so - 2.0, (hx, hy, zb + 2.0))).cut(cyl(P.INSERT[0], P.INSERT[1], (hx, hy, zb - 0.1)))
            add(f"Board tray {name.split(' (')[0]}", tr.clean(), "print", "power", bom="Printed board tray", kind="print",
                note="PETG; the board heat-staked onto its four pegs; 2 x M4 x 12 up through the bellypan into inserts")
    relay = "Contactor + battery relays: 12 V 200 A continuous duty, isolated coil, 4-pin (B0D97PSZBB)"
    add("PDH contactor 200 A", box(-175.0, -100.0, -87.0, -27.0, zb, zb + 70.0), "black", "power", bom=relay,
        note="main breaker -> contactor -> PDH; coil through the safety node and the main controller in series")
    # rev D.2.1: one 200 A relay in each battery's + lead (same part as the contactor), a 4.7 ohm 5 W resistor across each
    add("Battery relay A 200 A", box(-175.0, -100.0, 27.0, 87.0, zb, zb + 70.0), "black", "power", bom=relay,
        note="in battery A's + lead, between its SB50 and the bus; the controller keeps only the fuller pack connected "
             "until the two are within 0.3 V")
    add("Battery relay B 200 A", box(-97.0, -22.0, -87.0, -27.0, zb, zb + 70.0), "black", "power", bom=relay,
        note="in battery B's + lead, between its SB50 and the bus")
    ELEC_MARKS.extend([("Contactor", -175.0, -100.0, -87.0, -27.0), ("Battery relay A", -175.0, -100.0, 27.0, 87.0),
                       ("Battery relay B", -97.0, -22.0, -87.0, -27.0)])
    # bottom of the rear panel, one tight row (Micah 2026-11-12): breaker, charge port, the fill plug, USB-C
    cy, cz = CHARGE
    xc = P.rear_x(cz)
    add("Charge port (SB50 panel mount)", box(xc - 4.0, xc + 26.0, cy - 18.0, cy + 18.0, cz - 14.0, cz + 14.0), "red", "power",
        bom="Anderson SB50 panel-mount charge port", note="rear panel, bottom: charge or run on standby power with the batteries in")
    xu = P.rear_x(USB[1])
    add("USB-C panel pass-through", cyl(8.5, 28.0, (xu - 2.0, USB[0], USB[1]), (1, 0, 0)), "black", "power",
        bom="Panel-mount USB-C extension (to the main controller)")


def _in_bay(y0, y1, lim=87.0):
    """extrusion-4040: the 40x40 inner rails' inner faces are at |y| 89.35 (was 103.95), so every bellypan part moves
    in to |y| <= 87."""
    if y1 > lim:
        return y0 - (y1 - lim), lim
    if y0 < -lim:
        return -lim, y1 + (-lim - y0)
    return y0, y1


BREAKER = (-135.0, 255.0)   # (y, z) on the rear panel, bottom strip: one tight row, breaker / charge / fill / USB-C;
                            # the breaker (41 mm deep) stays outside the tank lines that drop beside the rear cross
ELEC_MARKS = []             # (label, x0, x1, y0, y1) of every part on the bellypan: engraved on the CNC'd bellypan
CHARGE = (-75.0, 255.0)
USB = (10.0, 255.0)


# ------------------------------------------------------------------ speakers + audio
def speakers():
    """Slim siren speakers in printed cups in the front-side corner notches, a printed grille on each, and the
    audio amp and boost on the middle of the bellypan."""
    plain = B.body_solid(notched=False)
    w, h, d = P.SPEAKER
    for pod in SPK.pods():
        a, q = pod["a"], pod["q"]
        cup = pod["cut"].intersect(plain).cut(pod["pocket"]).cut(pod["wire"])
        for nm, at, dir_ in CUP_SCREWS:                   # M4 x 8 button heads through the side walls into the frame
            if nm == pod["name"]:
                cup = cup.cut(cyl(2.25, P.SPK_WALL + 2.0, (at - dir_ * (P.SPK_WALL + 1.0)).toTuple(), dir_.toTuple()))
        add(f"Speaker cup {pod['name']}", cup, "print", "body", bom="Speaker cup", kind="print",
            note=f"lines the corner notch; {sum(nm == pod['name'] for nm, _, _ in CUP_SCREWS)} x M4 x 8 through its "
                 "side walls into inserts in the frame; the speaker's L foot bolts through the cup's lower wall (M4)")
        add(f"Speaker {pod['name']}", pod["speaker"], "black", "power", mass=2.27,
            bom="Siren speaker 200 W, 8 ohm, aluminium (Xprite B01DMSR4L4)", note="5.7 x 5.5 x 2.3 in with its foot, 121-130 dB")
        add(f"Speaker grille {pod['name']}", pod["grille"], "print", "body", bom="Speaker grille", kind="print",
            note="3 walls, no top or bottom layers, 12% gyroid: an open mesh; glue or screw to the cup")
    # front light bar (Brophy Borealis): Micah's Zmoon 12 in single-row bar in the plain hole at the bottom of the
    # front slant, standing on the lower of the two 20x20 rails that cross the hole (front_rails), on its own end
    # brackets. The main controller switches (and can PWM-dim) it through a MOSFET channel
    add("LED light bar front", LB.bar(), "black", "power", mass=0.37,
        bom="Front light bar: Zmoon 12 in single-row LED bar, 72 W spot/flood combo, 12/24 V",
        note="in the front hole, on the lower rail; aimed straight ahead")
    for br, side in zip(LB.brackets(), ("left", "right")):
        add(f"Light bar bracket {side}", br, "steel", "power", bom="Light bar end bracket (comes with the bar)",
            kind="cots", note="its foot on the lower front rail (M4 x 8 into a drop-in T-nut), the bar's side bolt through its ear")
    audio_power()


def audio_power():
    """The siren amp and its boost converter on the middle of the bellypan (their own function so the electronics
    can be rebuilt without the body)."""
    zb = P.BELLY_Z                             # middle of the bellypan, beside the smoke tube and under the gun's swing
    add("Audio amp (TPA3255)", box(-95.0, 27.0, 14.0, 87.0, zb, zb + 30.0), "pcb", "power",       # moved 40 mm forward: battery relay A sits behind it
        bom="TPA3255 2 x 300 W class-D amp board, 19-50 V DC, 122 x 73 x 30 mm", note="one channel per speaker, about 70 W each on 33 V")
    ELEC_MARKS.extend([("Amp", -95.0, 27.0, 14.0, 87.0), ("Boost", -10.0, 120.0, -87.0, -32.0)])
    add("Audio boost 12-33 V 1200 W", box(-10.0, 120.0, -87.0, -32.0, zb, zb + 55.0), "black", "power",
        bom="1200 W 20 A boost converter, 8-60 V in, 12-80 V out (set to 33 V)", note="feeds the amp from a 40 A PDH channel; "
             "size not on the listing [UNVERIFIED], drawn 130 x 55 x 55 like the same module on Amazon")


# ------------------------------------------------------------------ deck rails (Brophy Borealis)
DECK_RAIL_SCREWS = []                     # x of each in-well rail's M4 screws (mirrored), set by body_parts


def deck_rails():
    """A 20x20 T-slot rail inside the gun well along each side (Micah, 2026-11-10: "inside the cannon section, not on
    top of the panel"), one piece over the cut-down tower, the pivot's bearing block on top of it, the tower plate
    between it and the deck's well-edge member. M4 x 30s through holes CNC'd across the rail's core (8 mm head access from the well side) and the plate into heat-set inserts in the member's inner face."""
    (x0, x1), (y0, y1), (z0, z1) = P.DECK_RAIL["x"], P.DECK_RAIL["y"], P.DECK_RAIL["z"]
    n_ = len(DECK_RAIL_SCREWS)
    for sg, side in ((1, "left"), (-1, "right")):
        ys = (y0, y1) if sg > 0 else (-y1, -y0)
        r = t_slot(x0, x1, ys, (z0, z1))
        for f in lib.FASTENERS:                           # extrusion-4040: the tower's M5 x 35s down through it
            if f["kind"] == "endtap" and f.get("cross") == f"Rail 20x20 well {side}":
                r = r.cut(cyl(P.M5["hole"], 40.0, (f["at"][0], f["at"][1], z0 - 10.0), (0, 0, 1)))
        for x_ in DECK_RAIL_SCREWS:                       # the CNC'd cross holes: 4.5 through, 8 mm head access
            zs = P.DECK_RAIL["screw_z"]
            r = r.cut(cyl(2.25, 30.0, (x_, sg * (y0 - 5.0), zs), (0, sg, 0)))
            r = r.cut(cyl(4.0, 7.0, (x_, sg * (y0 - 1.0), zs), (0, sg, 0)))          # to the core: the head sits on it
        add(f"Rail 20x20 well {side}", r, "alu", "body", bom="20x20 T-slot extrusion (owned spare, cut)", kind="stock",
            mass=0.47 * (x1 - x0) / 1000.0,
            note=f"{x1 - x0:.0f} mm inside the gun well, over the cut-down tower; {n_} x M4 x 30 through CNC'd cross holes "
                 "(8 mm head access from the well side, the head on the core) and the tower plate into inserts in the deck's well-edge member; the bearing "
                 "block on top, the elevation motor bracket under the right one; 2 x 5.5 mm holes down its centre line for "
                 "the tower's M5 x 35 end taps (heads on its top face)")
        # (the tower plate, flat now, and the rail's spacer strip: brackets.py)


def front_rails():
    """Two 20x20 T-slot rails across the front light bar hole, flat on the frame's inner face behind it: the bar
    stands on the lower one, the upper one is free for sensors and the like."""
    for name, q0 in LB.rails():
        n_ = sum(1 for nm, _ in FRONT_RAIL_SCREWS if nm == name)
        r = LB.rail(q0)
        for nm, y_ in FRONT_RAIL_SCREWS:
            if nm == name:
                r = r.cut(LB.rail_holes(q0, y_))
        add(f"Rail 20x20 front {name}", r, "alu", "body", bom="20x20 T-slot extrusion (owned spare, cut)",
            kind="stock", mass=0.47 * P.BAR_HOLE["rail_len"] / 1000.0,
            note=f"{P.BAR_HOLE['rail_len']:.0f} mm across the front hole; {n_} x M4 x 8 from inside, through holes CNC'd "
                 "across the rail into M4 x 4 inserts in the frame member beside the hole")


# ------------------------------------------------------------------ bumpers
def bumpers():
    zb0, zb1 = P.BUMP_Z
    fd = P.FOAM_D
    t = P.BUMP_BACK_T
    xf, yo = P.FRAME_X + P.BUMP_GAP, P.OUTER_RAIL_Y[1] + P.BUMP_GAP      # 3/16 in clear of the chassis all round
    reach = t + fd
    segs = {
        "front": dict(axis="y", pos=xf, out=(1, 0), span=(-(yo + reach), yo + reach)),
        "rear": dict(axis="y", pos=-xf, out=(-1, 0), span=(-(yo + reach), yo + reach)),
        "left": dict(axis="x", pos=yo, out=(0, 1), span=(-(xf + reach), xf + reach)),
        "right": dict(axis="x", pos=-yo, out=(0, -1), span=(-(xf + reach), xf + reach)),
    }
    # the four backings are one ring: the end strips run the full width and the side strips butt into them, joined
    # by a printed bracket outside each corner (2 x #10-32 x 1/2 in per leg from the rail side, heads counterbored
    # flush in the ply, into heat-set inserts). Only the sides are screwed to the robot, between the wheels, where a
    # driver reaches from the open bay underneath; with those 6 out the ring slides straight down
    T_, L_ = P.BUMP_CORNER[1], P.BUMP_CORNER[0]
    xo_, yo_ = xf + t, yo + t
    zc0, zc1 = zb0 + 6.0, zb1 - 14.0
    corners, ring_holes = [], []
    for sx in (-1, 1):
        for sy in (-1, 1):
            end_leg = box(*sorted([sx * xo_, sx * (xo_ + T_)]), *sorted([sy * (yo_ - L_), sy * (yo_ + T_)]), zc0, zc1)
            side_leg = box(*sorted([sx * (xf - L_), sx * (xo_ + T_)]), *sorted([sy * yo_, sy * (yo_ + T_)]), zc0, zc1)
            brk = end_leg.fuse(side_leg)
            for zs in (zb0 + 30.0, zb1 - 45.0):
                ye = sy * (yo_ - 25.0)                    # through the end strip, along x
                ring_holes.append(("end", sx, cyl(5.5, 2.6, (sx * (xf - 0.1), ye, zs), (sx, 0, 0)).fuse(
                    cyl(2.6, t + 1.0, (sx * (xf - 0.5), ye, zs), (sx, 0, 0)))))
                brk = brk.cut(cyl(P.INSERT_1032[0], P.INSERT_1032[1], (sx * (xo_ - 0.1), ye, zs), (sx, 0, 0)))
                xe = sx * (xf - 25.0)                     # through the side strip, along y
                ring_holes.append(("side", sy, cyl(5.5, 2.6, (xe, sy * (yo - 0.1), zs), (0, sy, 0)).fuse(
                    cyl(2.6, t + 1.0, (xe, sy * (yo - 0.5), zs), (0, sy, 0)))))
                brk = brk.cut(cyl(P.INSERT_1032[0], P.INSERT_1032[1], (xe, sy * (yo_ - 0.1), zs), (0, sy, 0)))
            corners.append(brk)
            add(f"Bumper corner bracket {'front' if sx > 0 else 'rear'} {'L' if sy > 0 else 'R'}", brk, "print", "bumper",
                bom="Bumper corner bracket (printed)", kind="print",
                note="joins the ring outside the corner, inside the foam; 4 x #10-32 x 1/2 in from the rail side "
                     "into heat-set inserts. 4 walls, 25%")
    corner_cut = union([c_.translate(V(0, 0, 0)) for c_ in corners])
    for name, sgm in segs.items():
        a0, a1 = sgm["span"]
        ox, oy = sgm["out"]
        if sgm["axis"] == "y":
            bx0, bx1 = sorted([sgm["pos"], sgm["pos"] + ox * t])
            backing = box(bx0, bx1, -yo_, yo_, zb0, zb1)
        else:
            by0, by1 = sorted([sgm["pos"], sgm["pos"] + oy * t])
            backing = box(-xf, xf, by0, by1, zb0, zb1)
        piece = backing
        zr = HANGER_Z
        if sgm["axis"] == "x":                        # side strips: an M5 tee nut at each hanger block
            for x in P.BUMP_SIDE_X:
                piece = piece.cut(cyl(P.TNUT, t + 2, (x, sgm["pos"] - oy, zr), (0, oy, 0)))
            for kind, sg_, h_ in ring_holes:
                if kind == "side" and sg_ == oy:
                    piece = piece.cut(h_)
        else:
            for kind, sg_, h_ in ring_holes:
                if kind == "end" and sg_ == ox:
                    piece = piece.cut(h_)
        add(f"Bumper backing {name}", piece, "wood", "bumper", bom="Bumper backing, 1x6 ripped to 5 in (3/4 x 5 in)", kind="stock",
            note=("M5 x 30 from each printed hanger block (x -80, 0, 80) into an M5 pronged tee nut" if sgm["axis"] == "x"
                  else "no screws to the robot: held by the side strips through the corner brackets"))
        # one foam strip per side (cut from 24 in lengths of the GoTo block, butt-joined under the cover), mitred at the corners
        if sgm["axis"] == "y":
            f0, f1 = sorted([sgm["pos"] + ox * t, sgm["pos"] + ox * (t + fd)])
            fm = box(f0, f1, a0, a1, zb0, zb1)
        else:
            f0, f1 = sorted([sgm["pos"] + oy * t, sgm["pos"] + oy * (t + fd)])
            fm = box(a0, a1, f0, f1, zb0, zb1)
        fm = _mitre(fm, sgm, yo, xf, reach).cut(corner_cut)           # notched round the corner brackets
        fm = max(fm.Solids(), key=lambda x: x.Volume()) if len(fm.Solids()) > 1 else fm
        add(f"Bumper foam {name}", fm, "foam", "bumper", bom="Bumper foam strip 2 x 5 in (GoTo Foam 43 ILD)", kind="stock")
        if sgm["axis"] == "y":
            c0, c1 = sorted([sgm["pos"] + ox * t, sgm["pos"] + ox * (t + fd + 1.5)])
            outer = box(c0, c1, -(yo + reach) + 1, yo + reach - 1, zb0 - 1, zb1 + 1)
            inner = box(c0 + (0 if ox > 0 else 1.5), c1 - (1.5 if ox > 0 else 0), -(yo + reach), yo + reach, zb0, zb1)
        else:
            c0, c1 = sorted([sgm["pos"] + oy * t, sgm["pos"] + oy * (t + fd + 1.5)])
            outer = box(-(xf + reach) + 1, xf + reach - 1, c0, c1, zb0 - 1, zb1 + 1)
            inner = box(-(xf + reach), xf + reach, c0 + (0 if oy > 0 else 1.5), c1 - (1.5 if oy > 0 else 0), zb0, zb1)
        add(f"Bumper cover {name}", _mitre(outer.cut(inner), sgm, yo, xf, reach), "foam", "bumper",
            bom="Bumper fabric cover (white canvas, owner's pick)", kind="stock")


HANGER_Z = P.RAIL_Z[0] - P.BUMP_HANGER[1] / 2      # the bumper screw's height (was the rail centre)


def hanger_box(x, sgn, pad=0.0):
    L, drop = P.BUMP_HANGER
    y0, y1 = P.OUTER_RAIL_Y[0], P.OUTER_RAIL_Y[1] + P.BUMP_GAP
    return box(x - L / 2 - pad, x + L / 2 + pad, *sorted([sgn * (y0 - pad), sgn * (y1 + pad)]), P.RAIL_Z[0] - drop - pad,
               P.RAIL_Z[0] + pad)


def bumper_spacers():
    """extrusion-4040: a printed hanger block under the outer rail at each of the 6 bumper stations (between the wheels,
    reached from the open bay underneath), in place of the old spacer on a #10-32 through the tube. 2 x M5 x 12 up into
    T-nuts in the rail's two bottom slots; one M5 x 30 from its inboard face (counterbored 34 mm) out through the
    3/16 in it fills behind the board and the 1x6 into an M5 pronged tee nut on the foam side."""
    L, drop = P.BUMP_HANGER
    z0 = P.RAIL_Z[0] - drop
    for sgn, side in ((1, "left"), (-1, "right")):
        for x in P.BUMP_SIDE_X:
            hb = hanger_box(x, sgn)
            for dx_, dy_ in ((-12.0, -P.SLOT_OFF), (12.0, P.SLOT_OFF)):
                yy = sgn * (OY + dy_)
                hb = hb.cut(cyl(P.M5["hole"], drop + 2, (x + dx_, yy, z0 - 1), (0, 0, 1))).cut(
                    cyl(P.M5["access_r"], drop - 8.0 + 1, (x + dx_, yy, z0 - 1), (0, 0, 1)))
                lib.fastener("tnut", "M5 x 12 socket head + T-nut", (x + dx_, yy, P.RAIL_Z[0]), (0, 0, 1),
                             f"Bumper hanger {side} {x:.0f}")
            ys = sgn * P.OUTER_RAIL_Y[0]
            hb = hb.cut(cyl(P.M5["hole"], 80.0, (x, ys - sgn, HANGER_Z), (0, sgn, 0))).cut(
                cyl(P.M5["access_r"], P.RAIL_W - 6.0 + 1.0, (x, ys - sgn, HANGER_Z), (0, sgn, 0)))
            add(f"Bumper hanger {side} {x:.0f}", hb, "print", "bumper", bom="Bumper hanger block (printed)", kind="print",
                note="PETG-CF, 5 walls, 40%: 2 x M5 x 12 up into the outer rail's bottom T-nuts; the bumper's M5 x 30 from "
                     "its inboard face (34 mm counterbore) into an M5 tee nut in the 1x6")


UG_SCREWS = []                                # (x, y) of every underglow bracket screw (corner gussets get holes)


def underglow():
    """Underglow: a printed 45 deg strip bracket under the outer and end rails, just inside the bumper backing, each
    carrying a 60/m strip aimed down and out. The light passes under the bumper (its bottom is 3 in up) and pools on
    the floor round the robot; a strip inside the bumper would mostly light the foam."""
    dz = 0.0                                              # flat on the rail; relieved under the corner plates
    UG_SCREWS.clear()
    zr0 = P.RAIL_Z[0]                                     # the rail's bottom face (107 on 40x40; the strip stays put)
    # 2026-11-11 (Micah: "the underglow LEDs need to go lower down and be at least level with the bottom of the bumper"):
    # the 45 deg face drops 16 mm on a web from the rail, so the strip's centre is 2.6 mm under the bumper's bottom edge
    sec = [(u, z + dz) for u, z in ((-19.0, 68.6), (-5.0, 82.6), (-5.0, zr0), (-25.0, zr0), (-25.0, zr0 - 3.0),
                                    (-8.0, zr0 - 3.0), (-8.0, 86.0), (-21.1, 72.9))]
    c, d, nn = (-14.0, 73.6 + dz), (0.7071, 0.7071), (0.7071, -0.7071)
    strip = [(c[0] - 5 * d[0], c[1] - 5 * d[1]), (c[0] + 5 * d[0], c[1] + 5 * d[1]),
             (c[0] + 5 * d[0] + 1.6 * nn[0], c[1] + 5 * d[1] + 1.6 * nn[1]),
             (c[0] - 5 * d[0] + 1.6 * nn[0], c[1] - 5 * d[1] + 1.6 * nn[1])]
    xo, yo = P.FRAME_X, P.OUTER_RAIL_Y[1]
    total = 0.0
    for tag, out, half, pos in (("left", (0, 1), xo - P.RAIL_W - 5.0, yo), ("right", (0, -1), xo - P.RAIL_W - 5.0, yo),
                                ("front", (1, 0), yo - P.RAIL_W - 5.0, xo), ("rear", (-1, 0), yo - P.RAIL_W - 5.0, xo)):
        ox, oy = out

        def prism(pts, a0, a1):
            if ox == 0:                                   # runs along x; section in the (y, z) plane
                q = [(oy * (pos + u), z) for u, z in pts]
                return cq.Workplane("YZ", origin=(a0, 0, 0)).polyline(q).close().extrude(a1 - a0).val()
            q = [(ox * (pos + u), z) for u, z in pts]
            return cq.Workplane("XZ", origin=(0, a1, 0)).polyline(q).close().extrude(a1 - a0).val()
        n = math.ceil(2 * half / 230.0)
        # where the rail is covered: the bottom corner plates (relief in the flange's top); on the sides, the bumper
        # hanger blocks (the bracket stops 1 mm short of each)
        if ox == 0:
            ug = [box(*sorted([sg_ * P.CORNER_PLATE_X, sg_ * (P.FRAME_X + 1.0)]), -400, 400, -1000, 1000) for sg_ in (-1, 1)]
            clear_ = union([hanger_box(x_, oy, pad=1.0) for x_ in P.BUMP_SIDE_X])
        else:
            ug = [box(-500, 500, *sorted([sg_ * P.INNER_RAIL_Y[0], sg_ * 400.0]), -1000, 1000) for sg_ in (-1, 1)]
            clear_ = None
        under = union(ug)                                 # under a corner plate the flange steps down by the plate
        top = box(-1000, 1000, -1000, 1000, zr0 - 3.4, zr0 + 0.4)
        for k in range(n):
            a0 = -half + 2 * half * k / n
            b_lo, b_hi = a0 + 0.5, a0 + 2 * half / n - 0.5
            low = prism([(-25.0, zr0 - 6.6), (-5.0, zr0 - 6.6), (-5.0, zr0 - 3.4), (-25.0, zr0 - 3.4)], b_lo,
                        b_hi).intersect(under)
            seg_ = prism(sec, b_lo, b_hi).cut(top.intersect(under)).fuse(low)
            if clear_ is not None:
                seg_ = seg_.cut(clear_)
            seg_ = seg_.clean()
            # extrusion-4040: countersunk M5 x 8 up through the 3 mm flange into T-nuts in the rail's outer bottom slot
            # (u -10 = the slot line), two per bracket, clear of the corner plates and the hanger blocks
            nsc = 0
            for fr_ in (0.22, 0.78, 0.5, 0.35, 0.65):
                if nsc == 2:
                    break
                a_ = b_lo + (b_hi - b_lo) * fr_
                pt = (a_, oy * (pos - P.SLOT_OFF), zr0) if ox == 0 else (ox * (pos - P.SLOT_OFF), a_, zr0)
                hole = cyl(P.M5["hole"], 12.0, (pt[0], pt[1], zr0 - 8.0), (0, 0, 1))
                if hole.intersect(under).Volume() > 0.01 or (clear_ is not None and hole.intersect(clear_).Volume() > 0.01):
                    continue
                if any(math.hypot(pt[0] - q[0], pt[1] - q[1]) < 20.0 for q in UG_SCREWS):
                    continue
                seg_ = seg_.cut(hole).cut(cq.Solid.makeCone(P.M5["csk_r"], P.M5["hole"], P.M5["csk_h"],
                                                            V(pt[0], pt[1], zr0 - 3.0 - 0.01), V(0, 0, 1)))
                UG_SCREWS.append((pt[0], pt[1]))
                lib.fastener("tnut", "M5 x 8 countersunk + T-nut", pt, (0, 0, 1), f"Underglow bracket {tag} {k + 1}")
                nsc += 1
            add(f"Underglow bracket {tag} {k + 1}", seg_, "print", "bumper",
                bom="Underglow bracket (printed, 45 deg)", kind="print",
                note=f"{nsc} x M5 x 8 countersunk up into T-nuts in the rail's outer bottom slot; the strip on its 45 deg "
                     "face with 3M tape")
        add(f"LED strip underglow {tag}", prism(strip, -half + 5.0, half - 5.0), "led", "bumper",
            bom="WS2812B strip 10 mm, 60/m (m)", kind="stock", note="aimed 45 deg down and out, its centre just under the bumper's bottom edge; 3M tape")
        total += 2 * half - 10.0
    return total


def _mitre(s, sgm, yo, xf, reach):
    """Cut a bumper run at 45 deg along each corner diagonal (outer corner -> rail corner)."""
    big = 3000.0
    out = s
    for sx in (-1, 1):
        for sy in (-1, 1):
            if sgm["axis"] == "y" and sgm["out"][0] != sx:
                continue
            if sgm["axis"] == "x" and sgm["out"][1] != sy:
                continue
            c = V(sx * (xf + reach), sy * (yo + reach), 0)
            d = V(sx, sy, 0).normalized()
            n = V(sy, -sx, 0).normalized()
            ox, oy = sgm["out"]
            mid = V(sgm["pos"] + ox * reach / 2, 0, 0) if sgm["axis"] == "y" else V(0, sgm["pos"] + oy * reach / 2, 0)
            m = n * -1 if n.dot(mid - c) > 0 else n
            pts = [c + d * big, c - d * big, c - d * big + m * big, c + d * big + m * big]
            half = cq.Workplane("XY", origin=(0, 0, -100)).polyline([(p.x, p.y) for p in pts]).close().extrude(800).val()
            out = out.cut(half)
    return out


def mount_points():
    """Where the body frame screws down to the chassis: a #10-32 up from below into a heat-set insert in the frame.
    (name, point on the frame's underside); the insert axis is +z. The side wall's bottom member sits right on the
    bumper (1.5 mm over it), so each side station gets a tab on the frame's inner face, out over the outer rail, and
    the insert goes in that. End inserts sit far enough in from the slanted face to keep a wall to the light tunnel."""
    zb, out = P.Z_WALL_BOT, []
    for sgn, side in ((1, "L"), (-1, "R")):
        for x in P.SIDE_MOUNT_X:
            out.append((f"{side} {x:.0f}", V(x, sgn * (P.wall_y(zb, inner=True) - P.MOUNT_TAB[0] / 2 - 1.5), zb)))
        # (Brophy Borealis: no tower station any more: the in-well rail's M4s into the deck's well-edge member, right
        # over the cut-down tower and its plate, hold the deck to the tower)
    for sx, end, dh in ((1, "front", 22.0), (-1, "rear", 17.5)):
        xe = P.front_x(zb) if sx > 0 else P.rear_x(zb)
        for y in (P.FRONT_MOUNT_Y if sx > 0 else P.END_MOUNT_Y):
            out.append((f"{end} {y:.0f}", V(xe - sx * dh, y, zb)))
    return out


def mount_tab(name, q):
    """The side-station tab on the frame's inner face: MOUNT_TAB reach in from the face (plus 2 mm into the member),
    height up from the frame's underside, length along the wall."""
    sgn = 1 if name[0] == "L" else -1
    reach, h, ln = P.MOUNT_TAB
    yi = P.wall_y(P.Z_WALL_BOT, inner=True)
    return box(q.x - ln / 2, q.x + ln / 2, min(sgn * (yi - reach), sgn * (yi + 2.0)), max(sgn * (yi - reach), sgn * (yi + 2.0)),
               P.Z_WALL_BOT, P.Z_WALL_BOT + h)


MOUNT_SCREWS = []                         # (x, y, z) of every frame-mount post's M5 into the rail (corner plates
                                          # get clearance holes where a post stands on one)


def frame_mounts():
    """The chassis side of mount_points(). extrusion-4040: each printed post stands on the outer or end rail's top face
    (or on the top corner plate there) and is held by 2 x M5 x 12 socket heads down into T-nuts in the rail's top slots,
    driven from above through 10 mm counterbores before the body goes on (no more 2-1/2 in #10-32 up through a tube).
    The frame's own 1/2 in #10-32 still goes up through the post's 4 mm top into the frame's heat-set insert; its head
    sits in a pocket that opens outward, behind the bumper (take the bumper ring off and every frame screw is in
    reach)."""
    MOUNT_SCREWS.clear()
    zb, zr0, zr1 = P.Z_WALL_BOT, P.RAIL_Z[0], P.RAIL_Z[1]
    top_t = 4.0                                           # post top under the frame: 4 + 0.5 gap + 8.2 in the insert
    clear = lambda q, t=top_t: cyl(2.6, t + 2.0, (q.x, q.y, q.z - 0.5 - t - 1.0), (0, 0, 1))

    def screws(post, pts, z0, name):
        for (x, y) in pts:
            post = post.cut(cyl(P.M5["hole"], 30.0, (x, y, z0 - 1.0), (0, 0, 1))).cut(
                cyl(P.M5["access_r"], zb, (x, y, z0 + 8.0), (0, 0, 1)))
            MOUNT_SCREWS.append((x, y, z0))
            lib.fastener("tnut", "M5 x 12 socket head + T-nut" if z0 < zr1 + 0.1 else "M5 x 16 socket head + T-nut",
                         (x, y, zr1), (0, 0, -1), f"Frame mount {name}")
        return post
    for name, q in mount_points():
        if name.startswith(("L ", "R ")):
            sgn = 1 if name[0] == "L" else -1
            y_in, y_out = P.OUTER_RAIL_Y
            post = box(q.x - 20, q.x + 20, min(sgn * y_in, sgn * y_out), max(sgn * y_in, sgn * y_out), zr1, zb - 0.5)
            ya, yb_ = sorted([q.y - sgn * 6.0, sgn * (y_out + 3.0)])
            pocket = box(q.x - 7, q.x + 7, ya, yb_, zr1 + 16.0, zb - 0.5 - top_t)
            post = post.cut(pocket).cut(clear(q))
            post = screws(post, [(q.x - 13.0, sgn * (OY - P.SLOT_OFF)), (q.x + 13.0, sgn * (OY - P.SLOT_OFF))], zr1, name)
            add(f"Frame mount {name}", post, "print", "body", bom="Frame mount post (printed)", kind="print",
                note="2 x M5 x 12 down into T-nuts in the outer rail's inner top slot (before the body); the frame's "
                     "1/2 in #10-32 up from the outer pocket into the frame tab (bumper ring off first)")
        else:
            sx = 1 if name.startswith("front") else -1
            xi, xo = sx * (P.FRAME_X - P.RAIL_W), sx * P.FRAME_X
            on_plate = abs(q.y) + 20 > P.INNER_RAIL_Y[0]          # on the top corner plate
            z0 = zr1 + (P.PLATE_T if on_plate else 0.0)
            post = box(min(xi, xo), max(xi, xo), q.y - 20, q.y + 20, z0, zb - 0.5)
            inner = q.x - sx * 6.0                        # the pocket's inner end, round the screw head
            if (inner - xi) * sx < 3.0:                   # too close to the rail's inner edge: a cap over it,
                cap_x = xi - sx * 7.0                     # high above the wheel, keeps 3 mm of skin
                post = post.fuse(box(min(cap_x, xi), max(cap_x, xi), q.y - 20, q.y + 20, zb - 20.0, zb - 0.5))
                inner = xi - sx * 4.0
            pocket = box(min(inner, xo + sx * 3.0), max(inner, xo + sx * 3.0), q.y - 7, q.y + 7, z0 + 16.0,
                         zb - 0.5 - top_t)
            post = post.cut(pocket).cut(clear(q))
            xs_ = sx * (P.FRAME_X - P.RAIL_W / 2 - P.SLOT_OFF)            # the end rail's inner top slot
            post = screws(post, [(xs_, q.y - 14.0), (xs_, q.y + 14.0)], z0, name)
            add(f"Frame mount {name}", post, "print", "body", bom="Frame mount post (printed)", kind="print",
                note="2 x M5 down into T-nuts in the end rail's inner top slot" + (" through the corner plate" if on_plate
                                                                                    else "") +
                     " (before the body); the frame's 1/2 in #10-32 from the outer pocket (bumper ring off first)")


REAR_HOLES = ((REAR_MAN[1] + REAR_DY, REAR_MAN[2], 12.0),   # fill check valve (2026-11-12: flat cross)
              (CHARGE[0], CHARGE[1], 26.0), (USB[0], USB[1], 10.0),
              (BREAKER[0], BREAKER[1], 21.0))


CUP_SCREWS = []                          # (point on the part's face, direction into the frame): set by body_parts
FRONT_RAIL_SCREWS = []                   # (rail, y) of each front-hole rail's M4 screw: set by body_parts


def _overlaps(a, b, pad=0.0):
    ba, bb = a.BoundingBox(), b.BoundingBox()
    return ba.xmin - pad < bb.xmax and bb.xmin - pad < ba.xmax and ba.ymin - pad < bb.ymax and bb.ymin - pad < ba.ymax \
        and ba.zmin - pad < bb.zmax and bb.zmin - pad < ba.zmax


def _hits(shape, others):
    return any(_overlaps(shape, o) and shape.intersect(o).Volume() > 0.5 for o in others)


def _frame_insert(pieces, hole, avoid, share=0.95):
    """Cut an insert hole into the frame piece that holds it if it lies `share` inside one piece and clear of every
    solid in `avoid` (light tunnels, joint screws); True when cut."""
    if _hits(hole, avoid):
        return False
    for p in pieces:
        if _overlaps(p["shape"], hole) and p["shape"].intersect(hole).Volume() >= share * hole.Volume():
            p["shape"] = p["shape"].cut(hole)
            return True
    return False


def body_parts(log=print):
    body, frame, panels = B.build(log=log)
    pieces, edges = B.section(frame, panels, log=log)
    B.add_joints(pieces, panels, log=log)
    tun_list = list(B.build.tunnels or [])
    screws = list(getattr(B.add_joints, "screws", []))
    # #10-32 heat-set inserts where the frame screws down to the chassis and the turret towers
    tun = union(B.build.tunnels) if B.build.tunnels else None
    hit, miss, clash = 0, [], []
    for name, q in mount_points():
        if name.startswith(("L ", "R ")):           # side stations: a tab on the inner face first
            tab = mount_tab(name, q)
            tb = tab.BoundingBox()
            near = [p for p in pieces if p["shape"].BoundingBox().xmin < tb.xmax and p["shape"].BoundingBox().xmax > tb.xmin
                    and p["shape"].BoundingBox().ymin < tb.ymax and p["shape"].BoundingBox().ymax > tb.ymin
                    and p["shape"].BoundingBox().zmin < tb.zmax and p["shape"].BoundingBox().zmax > tb.zmin]
            own = max(near, key=lambda p: p["shape"].intersect(tab).Volume(), default=None)
            if own is not None:
                s = own["shape"].fuse(tab)
                for o in near:
                    if o is not own and o["shape"].intersect(tab).Volume() > 0.5:
                        s = s.cut(o["shape"])
                own["shape"] = s.clean()
                if len(own["shape"].Solids()) != 1:
                    clash.append(f"{name} tab left {own['name']} in {len(own['shape'].Solids())} solids")
            if _hits(tab, screws):
                clash.append(f"{name} tab blocks a frame joint's cross screw")
            if _hits(tab, tun_list):
                clash.append(f"{name} tab fills a light tunnel or feed slot")
        hole = cyl(P.INSERT_1032[0], P.INSERT_1032[1] + 0.5, (q.x, q.y, q.z - 0.5), (0, 0, 1))
        if _hits(hole, screws):
            clash.append(f"{name} insert crosses a frame joint's cross screw")
        got = False
        for p in pieces:
            bb = p["shape"].BoundingBox()
            if bb.xmin - 1 < q.x < bb.xmax + 1 and bb.ymin - 1 < q.y < bb.ymax + 1 and bb.zmin - 1 < q.z < bb.zmax + 1:
                v = p["shape"].intersect(hole).Volume()
                if v > 1.0:
                    if v < 0.6 * hole.Volume():
                        clash.append(f"{name} only {v / hole.Volume() * 100:.0f}% in frame")
                    p["shape"] = p["shape"].cut(hole)
                    got = True
        if tun is not None and tun.intersect(hole).Volume() > 0.5:
            clash.append(f"{name} cuts a light tunnel")
        hit += got
        if not got:
            miss.append(name)
    log(f"frame mounts: {hit} #10-32 inserts in the frame" + (f"; no frame at {miss}" if miss else "")
        + (f"; check {clash}" if clash else ""))
    # speaker cups: 4 x M4 through each cup's side walls (the button heads sit in the clearance gap round the
    # speaker) into inserts in the frame round the notch, where an insert is clear of tunnels and joint screws
    CUP_SCREWS.clear()
    w_, h_, _ = P.SPEAKER
    for pod in SPK.pods():
        a_, b1, b2, q0 = pod["a"], pod["b1"], pod["b2"], pod["q"]
        chosen = []                                   # up to 2 per wall, 35 mm apart, where frame backs it
        for axis, half_out, half_across, other in ((b1, h_ / 2, w_ / 2, b2), (b2, w_ / 2, h_ / 2, b1)):
            for sg_ in (1, -1):
                dir_, here = axis * sg_, 0
                for dd in range(8, 92, 8):
                    for acr in range(-int(half_across) + 10, int(half_across) - 9, 12):
                        if here == 2 or len(chosen) == 4:
                            break
                        at = q0 + a_ * dd + dir_ * (half_out + P.SPK_CLEAR + P.SPK_WALL) + other * acr
                        if any((at - c_).Length < 35.0 for c_, _ in chosen):
                            continue
                        hole = cyl(P.INSERT[0], P.INSERT[1], (at - dir_ * 0.1).toTuple(), dir_.toTuple())
                        if _frame_insert(pieces, hole, tun_list + screws):
                            chosen.append((at, dir_))
                            here += 1
        CUP_SCREWS.extend((pod["name"], at, dir_) for at, dir_ in chosen)
        if len(chosen) < 4:
            clash.append(f"speaker cup {pod['name']}: only {len(chosen)} of 4 screws found frame")
    # front hole rails: one M4 x 8 each end from inside, through the rail into an insert in the inner face of the
    # frame member beside the hole (clear of the member's light tunnel, which runs near its outer face)
    FRONT_RAIL_SCREWS.clear()
    for name, q0 in LB.rails():
        for sg in (1, -1):
            for yy in (183.0, 181.0, 185.0, 179.0, 187.0, 180.0, 186.0):
                if _frame_insert(pieces, LB.screw_hole(q0, sg * yy), tun_list + screws, share=0.9):
                    FRONT_RAIL_SCREWS.append((name, sg * yy))
                    break
            else:
                clash.append(f"front rail {name} {'left' if sg > 0 else 'right'}: no frame for its screw")
    # in-well rails: M4 x 4 inserts in the well-edge member's inner face, below its light tunnel; the same x both sides
    DECK_RAIL_SCREWS.clear()
    rx0, rx1 = P.DECK_RAIL["x"]
    zs = P.DECK_RAIL["screw_z"]
    for target in P.DECK_RAIL["screws_x"]:
        for dx in (0, 10, -10, 20, -20, 30, -30):
            x_ = target + dx
            holes = [cyl(P.INSERT_SHORT[0], P.INSERT_SHORT[1], (x_, sg * (P.Y_SLOT - 0.1), zs), (0, sg, 0)) for sg in (1, -1)]
            if all(not _hits(h, tun_list + screws) and any(_overlaps(p["shape"], h) and
                   p["shape"].intersect(h).Volume() >= 0.9 * h.Volume() for p in pieces) for h in holes):
                for h in holes:
                    _frame_insert(pieces, h, [], share=0.9)
                DECK_RAIL_SCREWS.append(x_)
                break
        else:
            clash.append(f"in-well rails: no frame for the screw near x {target:.0f}")
    log(f"speaker cup screws: {len(CUP_SCREWS)} of 8, front rail screws: {len(FRONT_RAIL_SCREWS)} of 4, in-well rail screws: "
        f"{2 * len(DECK_RAIL_SCREWS)} of {2 * len(P.DECK_RAIL['screws_x'])}" + (f"; check {clash}" if clash else ""))
    # a chunk that came loose from its piece (cut off by a slot or an insert) goes to the piece it touches, if any
    slivers = []
    for p in pieces:
        sol = sorted(p["shape"].Solids(), key=lambda x: -x.Volume())
        keep = [x for x in sol if x.Volume() > max(0.03 * sol[0].Volume(), min(2000.0, 0.06 * sol[0].Volume()))]
        for x in sol:
            if x in keep:
                continue
            home = next((o for o in pieces if o is not p and _overlaps(o["shape"], x, 0.3) and o["shape"].distance(x) < 0.2), None)
            if home is not None:
                fused = home["shape"].fuse(x).clean()
                if len(fused.Solids()) == len(home["shape"].Solids()):
                    home["shape"] = fused
                    slivers.append(f"{p['name']} {x.Volume():.0f} mm3 -> {home['name']}")
                    continue
            slivers.append(f"{p['name']} {x.Volume():.0f} mm3 at ({x.Center().x:.0f}, {x.Center().y:.0f}, "
                           f"{x.Center().z:.0f}) dropped")
        p["shape"] = keep[0] if len(keep) == 1 else cq.Compound.makeCompound(keep)
    for p in pieces:
        add(f"Body frame {p['name']}", p["shape"], "print", "body", bom=f"Body frame piece {p['name']}", kind="print",
            note="PETG, 0.6 mm nozzle, 2 walls, 10% gyroid")
    nclip = 0
    for i, p in enumerate(panels):
        a = B.slab(p["poly"], p["n"], P.MEM_W - P.REBATE_W + P.PANEL_GAP, P.CLIP_T, P.ACRYLIC_T, P.ACRYLIC_R)
        if p["n"].x < -0.9:                      # rear face: breaker, charge port, fill plug, USB-C
            for (yb, zb, r) in REAR_HOLES:
                a = a.cut(cyl(r, 30, (-P.FRAME_X - 10, yb, zb), (1, 0, 0)))
        u, w = B._plane_basis(p["n"])
        us = [V(*q).dot(u) for q in p["poly"]]
        ws = [V(*q).dot(w) for q in p["poly"]]
        dims = sorted([max(us) - min(us), max(ws) - min(ws)])
        door = abs(p["n"].y) > 0.9 and max(q[0] for q in p["poly"]) < P.SIDE_SPLIT_X + 1
        add(f"Panel {i:02d}{' (battery door)' if door else ''}", a, "acrylic", "body",
            bom="Frosted acrylic panel 1/8 in (owned)", kind="acrylic", note=f"{dims[1] / IN:.1f} x {dims[0] / IN:.1f} in outline")
        for k, c in enumerate(p["clips"]):
            short_ = any(d_ < P.INSERT[1] for _, _, d_ in c.get("bores", []))
            add(f"Panel clip {i:02d}-{k}", c["clip"], "print", "body", bom="Panel corner clip", kind="print",
                note="M4 x 6 button head into an M4 x 4 insert" if short_ else "M4 x 8 button head into an M4 x 4 insert (at the top of the 6.5 mm hole)")
            nclip += 1
        led = p.get("led_pieces") or []
        for k, piece in enumerate(led):
            add(f"LED loop panel {i:02d}" + (f" {chr(97 + k)}" if len(led) > 1 else ""), piece, "led", "body",
                bom="WS2812B strip 10 mm, 60/m (m)", kind="stock",
                note="on the rail behind the panel, LEDs across it; cut and jumped with 3 wires where a neighbour crosses")
    for tag, strip in B.build.frame_strips:
        add(f"LED strip frame {tag}", strip, "led", "body", bom="WS2812B strip 5 mm, 100/m (m)", kind="stock",
            note="pushed through the frame tunnel, LEDs out")
    log(f"body: {len(pieces)} frame pieces (loose chunks: {slivers or 'none'}), {len(panels)} panels, {nclip} clips, "
        f"LED strip {B.build.strips[0] / 1000:.1f} m in panel loops + {B.build.strips[1] / 1000:.1f} m in the frame")
    return panels
