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
from lib import add, box, cyl, tube, hex_prism, union
from drive import tube_part, fr8, _hull, bearing_seat
import pneu_parts as PP

IN = P.IN
IY = (P.INNER_RAIL_Y[0] + P.INNER_RAIL_Y[1]) / 2       # inner rail centre |y|
OY = (P.OUTER_RAIL_Y[0] + P.OUTER_RAIL_Y[1]) / 2


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
    if abs(x) > P.FRAME_X - 100.0 - 12.7 and abs(z0 - P.RAIL_Z[1]) < 0.1:
        z0 += P.PLATE_T                               # stands on the corner gusset
    return tube_part(name, "z", z0, z1, x, y, (1, 1))


# ------------------------------------------------------------------ pivot, elevation, angle sensor
def towers_and_pivot():
    px, pz = P.PIVOT
    x0, x1 = P.TOWER_X
    y0, y1 = P.BEARING_BLOCK_Y
    for sgn, side in ((1, "L"), (-1, "R")):
        yc = sgn * IY
        post(f"Turret tower {side} (1x1)", (x0 + x1) / 2, yc, P.RAIL_Z[1], pz + 28.0)   # flush with the block top
        for xf, d in ((x0, -1), (x1, 1)):
            leg_v = box(min(xf, xf + d * P.PLATE_T), max(xf, xf + d * P.PLATE_T), yc - 12.7, yc + 12.7,
                        P.RAIL_Z[1], P.RAIL_Z[1] + 60)
            leg_h = box(min(xf, xf + d * 15), max(xf, xf + d * 15), yc - 12.7, yc + 12.7,
                        P.RAIL_Z[1], P.RAIL_Z[1] + P.PLATE_T)
            add(f"Tower base gusset {side} {'rear' if d < 0 else 'front'}", leg_v.fuse(leg_h), "alu", "frame",
                bom="Tower base gusset (1/8 Al, bent)", kind="stock", note="3/16 rivets")
        # bearing block from the tower's front face forward to the axle: two flanged 1/2 hex bearings
        blk = box(x1, px + 25.0, min(sgn * y0, sgn * y1), max(sgn * y0, sgn * y1), pz - 28, pz + 28)
        blk = blk.cut(cyl(9.0, 800, (px, -400, pz), (0, 1, 0)))
        blk = blk.cut(bearing_seat(px, sgn * y0, pz, sgn, 7.94)).cut(bearing_seat(px, sgn * y1, pz, -sgn, 7.94))
        add(f"Pivot bearing block {side}", blk, "print_d", "frame", bom="Pivot bearing block", kind="print",
            note="PETG, 5 walls, 40% gyroid; 3 x 1/4-20 through the tower")
        for yb, d in ((y0, sgn), (y1, -sgn)):
            add(f"Pivot bearing {side} {yb:.0f}", fr8(px, sgn * yb, pz, d, hexbore=True), "steel", "frame",
                bom="Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)")
    # elevation: goBILDA 5203 (19.2:1, 312 rpm: backdrives easily when off) on a Spark MAX, 16T -> 112T HTD 5M 9 mm
    # belt on the right axle end (7:1, about 45 rpm free at the gun). Gearbox drawn at the 3-stage length (conservative)
    mx_, mz_ = P.ELEV_MOTOR_X, P.ELEV_MOTOR_Z
    ya, yb_ = P.ELEV_PULLEY_Y
    y_face = -(yb_ + 2.0)
    mot = cyl(18.0, 50.3, (mx_, y_face, mz_), (0, -1, 0)).fuse(cyl(18.75, 74.8, (mx_, y_face - 50.3, mz_), (0, -1, 0))).fuse(
        cyl(4.0, 23.5, (mx_, y_face, mz_), (0, 1, 0)))
    add("Elevation motor goBILDA 5203 19.2:1", mot, "black", "frame",
        bom="goBILDA 5203-2402-0019 Yellow Jacket 19.2:1, 312 rpm (FTC motor)", note="Spark MAX, brushed mode")
    pin = cyl(P.pd(P.ELEV_T[0]) / 2 + 2.5, yb_ - ya, (mx_, -yb_, mz_), (0, 1, 0)).cut(
        cyl(4.1, 40, (mx_, -yb_ - 5, mz_), (0, 1, 0)))
    add("Elevation pinion 16T", pin, "print_d", "frame", bom="Elevation pinion 16T HTD 9 mm (8 mm REX bore)", kind="print")
    yi, yo = y_face - 2.0, -P.Y_SLOT + 2.0                  # the bracket stays inside the gun well
    brk = union([box(px - 10.0, px + 25.0, yo, yi, mz_ - 20.0, pz - 28.0),          # web under the bearing block
                 box(px - 10.0, mx_ + 26.0, yo, yi, mz_ - 24.0, mz_ + 24.0)])        # arm out to the motor
    brk = brk.cut(cyl(18.3, 60, (mx_, yi + 5, mz_), (0, -1, 0)))
    add("Elevation motor bracket", brk, "print", "frame", bom="Elevation motor bracket", kind="print",
        note="PETG, 5 walls, 40% gyroid; hangs from the right bearing block; slotted for belt tension")
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
    # arm-angle pot on the end of the axle, outboard of the left bearing block (read by the STM32 ADC)
    yb = P.BEARING_BLOCK_Y[1]
    add("Pot coupler", cyl(9.0, 16.0, (px, yb + 1.0, pz), (0, 1, 0)).cut(cyl(7.45, 14.0, (px, yb + 0.5, pz), (0, 1, 0))),
        "print_d", "frame", bom="Pot coupler (1/2 hex to 1/4 in D)", kind="print")
    add("Arm-angle pot", cyl(12.0, 12.0, (px, yb + 25.0, pz), (0, 1, 0)).fuse(cyl(4.8, 8.0, (px, yb + 17.0, pz), (0, 1, 0))),
        "black", "frame", bom="10k linear pot, 1/4 in shaft (arm angle)")
    zb0 = max(pz - 30.0, P.Z_TOP + 1.0)                    # above the deck when the pivot is that high
    bri = box(px - 30, px + 30, yb + 37.0, yb + 40.2, zb0, pz + 10).cut(cyl(5.0, 10, (px, yb + 35, pz), (0, 1, 0)))
    for sx in (-1, 1):
        bri = bri.fuse(box(px + sx * 24 - 3, px + sx * 24 + 3, yb, yb + 37.0, zb0, pz + 10))
    add("Pot bracket", bri, "print", "frame", bom="Pot bracket", kind="print", note="screws to the left bearing block")
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
MAIN_Y = 40.0                                # main ball valve's elbow off the manifold's back face (y)
MAIN_OUT = []
FILL = (-248.6, 55.0, 200.0)                 # fill block centre (5-port), back bottom bay
CHECKS = []                                  # outlets of the two in valves (service loops start here)
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
        add(f"Tank elbow push-to-connect {side}", PP.ptc_elbow(V(xb0, sgn * ty, zp), (0, 0, -1), (1, 0, 0)), "brass", "pneu",
            bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT")
        tank_out[side] = (xb0 + 16.0, sgn * ty, zp - 13.0)
        for dx in (-80.0, 80.0):
            add(f"Tank plug {side} {dx:.0f}", PP.npt_plug(V(tx + dx, sgn * ty, zp), (0, 0, -1)), "brass", "pneu",
                bom="1/4 NPT brass plug")
        for xb in (-60.0, 200.0):
            post(f"Tank post {side} {xb:.0f} (1x1)", xb, sgn * IY, P.RAIL_Z[1], P.RAIL_Z[1] + 104.0)
            tube_part(f"Tank arm {side} {xb:.0f} (1x1)", "y", sgn * P.INNER_RAIL_Y[0], sgn * 262.0, xb,
                      P.RAIL_Z[1] + 104.0 + 12.7)
            add(f"Tank arm gusset {side} {xb:.0f}", box(xb - 12.7, xb + 12.7, min(sgn * P.INNER_RAIL_Y[0], sgn * 210.0),
                max(sgn * P.INNER_RAIL_Y[0], sgn * 210.0), P.RAIL_Z[1] + 129.4, P.RAIL_Z[1] + 129.4 + P.PLATE_T), "alu", "pneu",
                bom="Arm gusset (1/8 Al)", kind="stock")
            sad = box(xb - 14, xb + 14, sgn * ty - 68, sgn * ty + 68, P.RAIL_Z[1] + 129.4 + P.PLATE_T, tz).cut(
                cyl(R + 1.0, 60, (xb - 30, sgn * ty, tz), (1, 0, 0)))
            add(f"Tank saddle {side} {xb:.0f}", sad, "print", "pneu", bom="Tank saddle", kind="print")
        for xs in (tx - 40.0, tx + 40.0):
            add(f"Tank strap {side} {xs:.0f}", tube(R + 2.5, R + 0.5, 25.0, (xs - 12.5, sgn * ty, tz), (1, 0, 0)), "black",
                "pneu", bom="1 in cam-buckle strap")
    # rear manifold (200 psi zone), back bottom: tank lines and transducer on top, the fill port out through the
    # bottom of the rear panel, and the 200 psi relief beside it with its pull ring at the panel (the hand dump; no
    # bleed valve); line to the main valve on its front face
    mx, my, mz = REAR_MAN
    rear = P.rear_x(mz) + P.CLIP_T + P.ACRYLIC_T          # inner face of the rear panel at this height
    xo = P.rear_x(mz)
    xu = mx - 12.7 - 14.0                                  # main valve and fill U: one street elbow off the back face
    yb = my - 30.0                                         # fill plug through the panel here
    y_fill = yb + 57.0                                     # fill line back into the manifold
    stations = [(-38.0, (0, 0, 1)), (35.0, (0, 0, 1)), (-15.0, (0, 0, -1)), (MAIN_Y - my, (-1, 0, 0)),
                (y_fill - my, (-1, 0, 0)), (50.0, (-1, 0, 0))]
    blk, ports = PP.manifold(V(mx, my, mz), (0, 1, 0), (0, 0, 1), stations)
    add("Rear manifold", blk, "brass", "pneu", bom="Rear manifold: 1/4 NPT brass crosses + close nipples (built)")
    add("Tank transducer 0-300 psi", PP.transducer(ports[2][0], ports[2][1]), "steel", "pneu",
        bom="Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT (FUSCH)")
    tops = {}
    for k, tag in ((0, "right tank"), (1, "left tank")):          # left one clear of its battery sled
        add(f"Rear manifold push-to-connect {tag}", PP.ptc_straight(ports[k][0], ports[k][1]), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
        tops[tag.split()[0]] = ports[k][0] + V(0, 0, 18.0)
    # main valve (rev C.3, manual): a 1/4 ball valve off the manifold's back face, turned along -y by a street
    # elbow, its stem extended back through the rear panel to its lever outside (open all session, closed for
    # transport and gun work)
    add("Main valve elbow", PP.street_elbow(V(xu, MAIN_Y, mz), (0, -1, 0), (1, 0, 0)), "brass", "pneu",
        bom="1/4 NPT brass street elbow")
    add("Main valve nipple", PP.close_nipple(V(xu, MAIN_Y - 15.5, mz), (0, -1, 0)), "brass", "pneu",
        bom="1/4 NPT brass close nipple")
    vc = V(xu, MAIN_Y - 39.5, mz)
    add("Main valve (1/4 ball valve)", PP.ball_valve(vc, (0, -1, 0), (-1, 0, 0), stem_ext=xu - (xo - 6.0) - 10.0),
        "brass", "pneu", bom="Main valve: 1/4 NPT brass ball valve, FNPT x FNPT, 600 WOG (the old cannon's if it fits)",
        note="stem extended through the rear panel; its lever is outside: along the line = open")
    add("Main valve push-to-connect", PP.ptc_straight(vc - V(0, 22.5, 0), (0, -1, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    MAIN_OUT[:] = [vc - V(0, 22.5 + 18.0, 0)]
    # fill: universal-coupler M plug outside the panel, a nipple through it, then a U behind the panel through the
    # check valve (along +y) into the manifold's back face
    add("Fill plug (M-style)", PP.m_plug(V(xo - 2.0, yb, mz), (-1, 0, 0)), "brass", "pneu",
        bom="Fill plug: 1/4 MNPT industrial (M-style) plug, brass (Foster 10-3B)", note="your universal coupler snaps on")
    xn0, xn1 = xo - 2.0 + 10.2, xu - 14.0 + 10.0              # from the plug's thread to the elbow's port
    add("Fill nipple", PP.close_nipple(V((xn0 + xn1) / 2, yb, mz), (1, 0, 0), length=xn1 - xn0, hexed=False), "brass", "pneu",
        bom="1/4 NPT brass nipple x 1-1/2 in")
    add("Fill elbow panel", PP.street_elbow(V(xu, yb, mz), (-1, 0, 0), (0, 1, 0)), "brass", "pneu",
        bom="1/4 NPT brass street elbow")
    add("Fill check valve", PP.check_valve(V(xu, yb + 17.0, mz), (0, 1, 0)), "brass", "pneu",
        bom="Fill check valve, brass, 1/4 FNPT x 1/4 MNPT, 250 psi (Control Devices P2525-1WA)",
        note="holds the tanks behind the open plug")
    add("Fill elbow manifold", PP.street_elbow(V(xu, y_fill, mz), (0, -1, 0), (1, 0, 0)), "brass", "pneu",
        bom="1/4 NPT brass street elbow")
    add("Tank relief valve 200 psi", PP.relief_valve(ports[5][0], ports[5][1], length=ports[5][0].x - (xo - 4.0)), "brass",
        "pneu", bom="Relief valve 200 psi, 1/4 NPT, ASME, ring pull (McMaster 48435K72)", note="pull ring at the rear panel: the hand dump")
    # main valve (the tanks' shut-off, opens only while a chamber fills) into a brass cross; one in valve per chamber
    # off the cross meters its chamber against that chamber's transducer, and its closed seat is what keeps the
    # other cannon's shot from reaching it (no check valves). Main valve to in-valve seats is all brass at tank
    # pressure, so the cross carries its own 200 psi relief.
    fx, fy, fz = FILL
    sx1 = fx - 12.7 - 1.8

    add("Valve cross push-to-connect", PP.ptc_straight(V(fx - 12.7, fy, fz), (-1, 0, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    add("Valve cross", PP.npt_cross(V(fx, fy, fz), (1, 0, 0), (0, 1, 0)), "brass", "pneu",
        bom="1/4 NPT brass cross (ChillWaves)", note="close nipples to the in valves")
    add("Line relief valve 200 psi", PP.relief_valve(V(fx, fy + 12.7, fz), (0, 1, 0)), "brass", "pneu",
        bom="Relief valve 200 psi, 1/4 NPT, ASME, ring pull (McMaster 48435K72)")
    CHECKS.clear()
    for d, tag in ((V(1, 0, 0), "A (top cannon)"), (V(0, -1, 0), "B (bottom cannon)")):
        a0 = V(fx, fy, fz) + d * (12.7 + 1.8)
        add(f"In valve {tag}", PP.solenoid_02f(a0 + d * 18.5, d, (0, 0, 1)), "brass", "pneu",
            bom="2/2 NC 12 V direct-acting solenoid valve, 1/4 NPT (Aignep 02F)", note="coil up")
        add(f"In valve {tag} push-to-connect", PP.ptc_straight(a0 + d * 37.0, d), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
        CHECKS.append(a0 + d * 55.0)
    # tubes: tanks -> rear manifold, rear manifold -> main valve
    for side, dy in (("left", 35.0), ("right", -45.0)):
        t = tank_out[side]
        sg = 1 if side == "left" else -1
        # inboard of the rail posts (|y| 104+) and outside the gun, over the Falcons, then up between the sled
        # posts and across to the manifold above the sled rails
        xr = -295.0 if sg > 0 else -330.0                 # the right one rises behind service loop B
        e = tops[side]
        pts = [t, (t[0], sg * 98.0, 262.0), (xr, sg * 98.0, 245.0), (xr, sg * 98.0, 330.0),
               (e.x, e.y, 330.0), e.toTuple()]
        add(f"Tube tank {side}", tube_path(pts), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")
    m0 = MAIN_OUT[0]
    tf = [m0.toTuple(), (m0.x, m0.y - 12.0, mz), (sx1 - 40.0, m0.y - 12.0, mz - 20.0), (sx1 - 40.0, fy, mz - 25.0),
          (sx1 - 40.0, fy, fz), (fx - 12.7 - 18.0, fy, fz)]
    add("Tube main valve to cross", tube_path(tf), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")


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
            bom="Fog heater core 12 V 200 W (cast, 97 x 32 x 36 mm)", note="ceramic-fiber wrap; KSD301 + K probe clamped on")
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
    hub = hub.fuse(tube(5.4, 3.5, 16.0, (cx - 10, 0, z1 + 44), (0, 0, 1)))
    add("Fog splitter 1-3", hub, "print", "power", bom="Fog splitter 1 -> 3 (printed)", kind="print",
        note="22 mm barbs for the two trail tubes, a 3/8 barb for the gun's silicone line")
    FOG_OUT[:] = [V(cx - 10, 0, z1 + 60)]
    # front: down through the bellypan just ahead of the machine
    side_b = barbs[0]
    vx, vy = P.FOG_VENTS[0]
    add("Fog vent front", tube(13.0, 10.0, 14.0, (vx, vy, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1)).fuse(
        tube(16.0, 10.0, 3.0, (vx, vy, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1))), "print", "power",
        bom="Fog vent nozzle (under bumper)", kind="print", note="through a hole in the bellypan")
    add("Fog tube front", tube_path([side_b, (side_b[0] + 30, vy, side_b[2]), (vx, vy, P.BELLY_Z + 10.0),
                                     (vx, vy, P.BELLY_Z - P.PLATE_T)], r=11.0),
        "tube", "power", bom="Fog tube (owner's flexible tube)", kind="stock")
    # back: along the bellypan centreline, under the gun's swing, down through the bellypan just ahead of the
    # electronics bay (the trail comes out underneath, not straight out the back)
    side_b = barbs[1]
    rx, ry = P.FOG_VENTS[1]
    add("Fog vent rear", tube(13.0, 10.0, 14.0, (rx, ry, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1)).fuse(
        tube(16.0, 10.0, 3.0, (rx, ry, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1))), "print", "power",
        bom="Fog vent nozzle (under the belly)", kind="print", note="through a hole in the bellypan")
    add("Fog tube rear", tube_path([side_b, (side_b[0], -70.0, side_b[2]), (165.0, -70.0, side_b[2]), (165.0, ry, 125.0),
                                    (rx + 30.0, ry, 125.0), (rx, ry, P.BELLY_Z + 10.0), (rx, ry, P.BELLY_Z - P.PLATE_T)],
                                   r=11.0),
        "tube", "power", bom="Fog tube (owner's flexible tube)", kind="stock")


# ------------------------------------------------------------------ power + controls
def batteries_and_electronics():
    L, W, H = P.BATT
    zs = P.RAIL_Z[1] + 104.0 + 25.4                       # sled rail top
    for sgn, side in ((1, "left"), (-1, "right")):
        for xr in (-320.0, -215.0):
            post(f"Sled post {side} {xr:.0f} (1x1)", xr, sgn * IY, P.RAIL_Z[1], P.RAIL_Z[1] + 104.0)
            tube_part(f"Sled rail {side} {xr:.0f} (1x1)", "y", sgn * P.INNER_RAIL_Y[0], sgn * 262.0, xr,
                      P.RAIL_Z[1] + 104.0 + 12.7)
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
                                          300.0, 325.0), "red", "power", bom="Anderson SB50 pair + 6 AWG contacts (stash)")
    # back bottom bay: PDH and breaker on the bellypan, controls and the valve cross on a printed shelf
    zb = P.BELLY_Z
    add("Power distribution (REV PDH)", box(-370.0, -267.0, -86.5, 86.5, zb, zb + 36), "black", "power",
        bom="REV PDH (owned) + ATO breakers / fuses (stash)")
    add("Main breaker 120 A", box(-255.0, -218.0, -20.0, 20.0, zb, zb + 40), "black", "power", bom="120 A main breaker (stash)")
    shelf = box(-380.0, -180.0, -100.0, 100.0, 150.0, 154.0)          # between the inner rails (|y| 104+)
    for (x, y) in ((-372, -92), (-372, 92), (-188, -92), (-188, 92)):
        shelf = shelf.fuse(box(x - 5, x + 5, y - 5, y + 5, zb, 150.0))
    add("Electronics shelf", shelf, "print", "power", bom="Electronics shelf", kind="print")
    z = 154.0
    boards = [("STM32 Nucleo-F446RE (main controller)", -375, -305, -98, -16, 20, "pcb", "STM32 Nucleo-64 NUCLEO-F446RE"),
              ("ESP32-S3 WiFi bridge", -298, -229, -48, -20, 15, "pcb", "ESP32-S3-DevKitC-1 N8R8"),
              ("ESP32-S3 safety node", -298, -229, -84, -56, 15, "pcb", "ESP32-S3-DevKitC-1 N8R8"),
              ("PWM gate (74AHCT125)", -298, -248, -12, 14, 12, "pcb", "SN74AHCT125N quad buffer + perfboard"),
              ("Spark MAX (elevation)", -220, -185, -98, -28, 25, "black", "REV Spark MAX (owned)"),
              ("Safety relay 40 A", -220, -192, -20, -2, 36, "black", "12 V 40 A SPDT relay + socket"),
              ("Valve + fog drivers (relays, ULN2803A)", -378, -308, -6, 54, 32, "pcb", "12 V 40 A SPDT relay + socket"),
              ("Buck 12-5 V 20 A", -300, -244, 45, 95, 25, "black", "12->5 V 20 A buck (B089M5R3NJ)")]   # under the main valve
    boards.append(("Logic supply 5 V (PM02 buck-boost)", -378, -352, 60, 85, 10, "pcb",
                   "Logic supply: 5 V 5 A buck-boost (PM02, 3-20 V in)"))
    for name, x0, x1, y0, y1, h, col, bom in boards:
        add(name, box(x0, x1, y0, y1, z, z + h), col, "power", bom=bom)
    add("PDH contactor 200 A", box(-175.0, -100.0, -95.0, -35.0, zb, zb + 70.0), "black", "power",
        bom="Contactor 12 V 200 A continuous duty, isolated coil, 4 terminal, 2-pack (Hamolar RD-200)",
        note="main breaker -> contactor -> PDH; the STM32 closes it, the E-stop opens its coil")
    # bottom of the rear panel: E-stop, standby charge port (fill port and tank relief come out of the manifold)
    ey, ez = ESTOP
    xo = P.rear_x(ez)
    xi = xo + P.CLIP_T
    est = cyl(11.0, 12.0, (xi + 6.0, ey, ez), (-1, 0, 0)).fuse(
        cyl(20.0, 30.0, (xi + 34.0, ey, ez), (-1, 0, 0))).fuse(
        cq.Solid.makeSphere(22.0, V(xo - 2.0, ey, ez), angleDegrees1=0, angleDegrees2=90).rotate(
            V(xo - 2.0, ey, ez), V(xo - 2.0, ey + 1, ez), -90))
    add("E-stop", est, "red", "power", bom="Latching mushroom E-stop, 22 mm, NC", note="rear panel, bottom; in series with the safety relay coil")
    cy, cz = CHARGE
    xc = P.rear_x(cz)
    add("Charge port (SB50 panel mount)", box(xc - 4.0, xc + 26.0, cy - 18.0, cy + 18.0, cz - 14.0, cz + 14.0), "red", "power",
        bom="Anderson SB50 panel-mount charge port", note="rear panel, bottom: charge or run on standby power with the batteries in")
    xu = P.rear_x(USB[1])
    add("USB-C panel pass-through", cyl(8.5, 28.0, (xu - 2.0, USB[0], USB[1]), (1, 0, 0)), "black", "power",
        bom="Panel-mount USB-C extension (to the STM32)")


ESTOP = (-215.0, 255.0)     # (y, z) on the rear panel, bottom strip under the open middle
CHARGE = (-95.0, 255.0)
USB = (182.0, 255.0)


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
    # front light bar: Micah's Zmoon 12 in single-row bar (72 W, spot/flood combo) across the nose just above the
    # bumper, on two printed brackets screwed into the front panel's bottom member; the STM32 switches (and can PWM-dim)
    # it through a MOSFET channel
    L, hb, db, zc, yb = P.LIGHT_BAR
    xf = P.front_x(zc - hb / 2) + 8.0                      # bar's back, clear of the slant at its bottom edge (the front leans back)
    bar = box(xf, xf + db, -L / 2, L / 2, zc - hb / 2, zc + hb / 2)
    bar = bar.cut(box(xf + db - 2.0, xf + db + 1.0, -L / 2 + 14.0, L / 2 - 14.0, zc - hb / 2 + 5.0, zc + hb / 2 - 5.0))  # one lens strip
    add("LED light bar front", bar, "black", "power", mass=0.37,
        bom="Front light bar: Zmoon 12 in single-row LED bar, 72 W spot/flood combo, 12/24 V", note="straight ahead")
    nf = V(math.sin(math.radians(P.FRONT_ANGLE)), 0, math.cos(math.radians(P.FRONT_ANGLE)))
    tf = V(-math.cos(math.radians(P.FRONT_ANGLE)), 0, math.sin(math.radians(P.FRONT_ANGLE)))
    lip = P.MEM_W - P.REBATE_W                             # the solid lip below the acrylic's rebate
    for sg, side in ((1, "left"), (-1, "right")):
        brk = box(P.front_x(zc - hb / 2 - 6.0) - 20.0, xf + 6.0, sg * yb - 8.0, sg * yb + 8.0, zc - hb / 2 - 6.0, zc - hb / 2)
        brk = brk.fuse(box(xf - 6.0, xf, sg * yb - 8.0, sg * yb + 8.0, zc - hb / 2 - 6.0, zc + hb / 2))   # tab behind the bar
        # a back plate lying on the slant's bottom lip, 30 mm wide, screwed to it with 2 x M4
        pl_ = cq.Plane(origin=(P.FRAME_X, sg * yb, P.Z_WALL_BOT), xDir=tf.toTuple(), normal=nf.toTuple())
        back = cq.Workplane(pl_).center(lip / 2, 0).rect(lip - 1.0, 30.0).extrude(5.0).val()
        brk = brk.fuse(back).cut(plain)
        brk = brk.cut(cyl(3.2, 10.0, (xf - 8.0, sg * yb, zc), (1, 0, 0)))   # the bar's own bolt, through the tab
        for s_, at, dir_ in BAR_SCREWS:
            if s_ == sg:
                brk = brk.cut(cyl(2.25, 9.0, (at - dir_ * 7.0).toTuple(), dir_.toTuple()))
        add(f"LED light bar bracket {side}", brk, "print", "body", bom="Light bar bracket (printed)", kind="print",
            note=f"{sum(s_ == sg for s_, _, _ in BAR_SCREWS)} x M4 x 8 into inserts in the front's bottom lip; "
                 "the bar's own bolt through its hole")
    zb = P.BELLY_Z                             # middle of the bellypan, beside the smoke tube and under the gun's swing
    add("Audio amp (TPA3255)", box(-135.0, -13.0, 22.0, 95.0, zb, zb + 30.0), "pcb", "power",
        bom="TPA3255 2 x 300 W amp board", note="one channel per speaker, about 100 W each on 48 V")
    add("Audio boost 12-48 V 1500 W", box(-10.0, 120.0, -100.0, -24.0, zb, zb + 60.0), "black", "power",
        bom="1500 W 30 A boost converter, set to 48 V", note="feeds the amp from a 40 A PDH channel; size not listed, "
             "drawn 130 x 76 x 60")


# ------------------------------------------------------------------ bumpers
def bumpers():
    zb0, zb1 = P.BUMP_Z
    r = P.NOODLE_D / 2
    t = P.BUMP_BACK_T
    xf, yo = P.FRAME_X, P.OUTER_RAIL_Y[1]
    reach = t + P.NOODLE_D
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
                note="joins the ring outside the corner, under the noodles; 4 x #10-32 x 1/2 in from the rail side "
                     "into heat-set inserts. 4 walls, 25%")
    corner_cut = union([c_.translate(V(0, 0, 0)) for c_ in corners])
    for name, sgm in segs.items():
        a0, a1 = sgm["span"]
        ox, oy = sgm["out"]
        if sgm["axis"] == "y":
            bx0, bx1 = sorted([sgm["pos"], sgm["pos"] + ox * t])
            backing = box(bx0, bx1, -yo_, yo_, zb0, zb1 - 8)
        else:
            by0, by1 = sorted([sgm["pos"], sgm["pos"] + oy * t])
            backing = box(-xf, xf, by0, by1, zb0, zb1 - 8)
        piece = backing
        zr = (P.RAIL_Z[0] + P.RAIL_Z[1]) / 2
        if sgm["axis"] == "x":                        # side strips: open-bottom slots past the axle end screws (a
            for sx in (-1, 1):                        # closed hole would catch the washer as the ring slides down)
                piece = piece.cut(cyl(14.0, 40, (sx * P.AX_X, sgm["pos"] - 20 * oy, P.AXLE_Z), (0, oy, 0)))
                piece = piece.cut(box(sx * P.AX_X - 8.0, sx * P.AX_X + 8.0, *sorted([sgm["pos"] - 5 * oy, sgm["pos"] + 12 * oy]),
                                      zb0 - 1.0, P.AXLE_Z))
            for x in P.BUMP_SIDE_X:
                piece = piece.cut(cyl(P.TNUT, t + 2, (x, sgm["pos"] - oy, zr), (0, oy, 0)))
            for kind, sg_, h_ in ring_holes:
                if kind == "side" and sg_ == oy:
                    piece = piece.cut(h_)
        else:
            for kind, sg_, h_ in ring_holes:
                if kind == "end" and sg_ == ox:
                    piece = piece.cut(h_)
        add(f"Bumper backing {name}", piece, "wood", "bumper", bom="Bumper backing, 1/4 in plywood", kind="stock",
            note=("#10-32 x 1/2 in from inside the outer rail into a 4-prong T-nut at x -80, 0, 80" if sgm["axis"] == "x"
                  else "no screws to the robot: held by the side strips through the corner brackets"))
        for i, zc in enumerate((zb0 + r, zb0 + 3 * r)):
            if sgm["axis"] == "y":
                c = sgm["pos"] + ox * (t + r)
                nd = _mitre(cyl(r, a1 - a0, (c, a0, zc), (0, 1, 0)), sgm, yo, xf, reach)
            else:
                c = sgm["pos"] + oy * (t + r)
                nd = _mitre(cyl(r, a1 - a0, (a0, c, zc), (1, 0, 0)), sgm, yo, xf, reach)
            nd = nd.cut(cyl(12.7, 3000, (c if sgm["axis"] == "y" else -1500, -1500 if sgm["axis"] == "y" else c, zc),
                            (0, 1, 0) if sgm["axis"] == "y" else (1, 0, 0)))
            nd = nd.cut(corner_cut)                   # notched round the corner brackets (crumbs dropped)
            nd = max(nd.Solids(), key=lambda x: x.Volume()) if len(nd.Solids()) > 1 else nd
            add(f"Pool noodle {name} {i + 1}", nd, "foam", "bumper", bom="Pool noodle 2.5 in (white)", kind="stock")
        if sgm["axis"] == "y":
            c0, c1 = sorted([sgm["pos"] + ox * t, sgm["pos"] + ox * (t + 2 * r + 1.5)])
            outer = box(c0, c1, -(yo + reach) + 1, yo + reach - 1, zb0 - 1, zb1 + 1)
            inner = box(c0 + (0 if ox > 0 else 1.5), c1 - (1.5 if ox > 0 else 0), -(yo + reach), yo + reach, zb0, zb1)
        else:
            c0, c1 = sorted([sgm["pos"] + oy * t, sgm["pos"] + oy * (t + 2 * r + 1.5)])
            outer = box(-(xf + reach) + 1, xf + reach - 1, c0, c1, zb0 - 1, zb1 + 1)
            inner = box(-(xf + reach), xf + reach, c0 + (0 if oy > 0 else 1.5), c1 - (1.5 if oy > 0 else 0), zb0, zb1)
        add(f"Bumper cover {name}", _mitre(outer.cut(inner), sgm, yo, xf, reach), "foam", "bumper",
            bom="Bumper fabric cover (white canvas, owner's pick)", kind="stock")


def underglow():
    """Underglow: a printed 45 deg strip bracket under the outer and end rails, just inside the bumper backing, each
    carrying a 60/m strip aimed down and out. The light passes under the bumper (its bottom is 3 in up) and pools on
    the floor round the robot; a strip inside the bumper would mostly light the noodles."""
    dz = 0.0                                              # flat on the rail; relieved under the corner gussets
    sec = [(u, z + dz) for u, z in ((-19.0, 84.6), (-5.0, 98.6), (-5.0, 101.6), (-25.0, 101.6), (-25.0, 98.6), (-9.2, 98.6),
                                    (-21.1, 86.7))]
    c, d, nn = (-12.0, 91.6 + dz), (0.7071, 0.7071), (0.7071, -0.7071)
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
        # where the rail is covered: the bottom corner gussets (relief in the flange's top) and the heads of the
        # frame-mount posts' rail screws (a 12 mm hole through the flange)
        if ox == 0:
            ug = [box(*sorted([sg_ * (P.FRAME_X - 100.0), sg_ * (P.FRAME_X + 1.0)]), -400, 400, -1000, 1000) for sg_ in (-1, 1)]
            heads = [(x_, oy * sum(P.OUTER_RAIL_Y) / 2) for x_ in P.SIDE_MOUNT_X]
        else:
            ug = [box(-500, 500, *sorted([sg_ * P.INNER_RAIL_Y[0], sg_ * 400.0]), -1000, 1000) for sg_ in (-1, 1)]
            heads = [(ox * (P.FRAME_X - 7.0), y_) for y_ in P.END_MOUNT_Y]
        under = union(ug)                                 # under a gusset the flange steps down by the plate
        top = box(-1000, 1000, -1000, 1000, 98.2, 102.0)
        clear_ = union([cyl(6.0, 30.0, (hx, hy, 80.0), (0, 0, 1)) for hx, hy in heads])
        for k in range(n):
            a0 = -half + 2 * half * k / n
            b_lo, b_hi = a0 + 0.5, a0 + 2 * half / n - 0.5
            low = prism([(-25.0, 95.0), (-5.0, 95.0), (-5.0, 98.2), (-25.0, 98.2)], b_lo, b_hi).intersect(under)
            seg_ = prism(sec, b_lo, b_hi).cut(top.intersect(under)).fuse(low).cut(clear_).clean()
            screws_ = []                                  # 2 x M4 up into the rail (or the gusset), clear of the post screws
            for f_ in (0.25, 0.75, 0.4, 0.6, 0.1, 0.9):
                at_ = b_lo + (b_hi - b_lo) * f_
                xy = (at_, oy * (pos - 15.0)) if ox == 0 else (ox * (pos - 15.0), at_)
                if clear_.intersect(cyl(6.0, 12.0, (xy[0], xy[1], 90.0), (0, 0, 1))).Volume() < 0.5 and \
                        all(abs(at_ - o_) > 30.0 for o_ in screws_):
                    seg_ = seg_.cut(cyl(2.25, 14.0, (xy[0], xy[1], 90.0), (0, 0, 1)))
                    screws_.append(at_)
                if len(screws_) == 2:
                    break
            add(f"Underglow bracket {tag} {k + 1}", seg_, "print", "bumper",
                bom="Underglow bracket (printed, 45 deg)", kind="print",
                note=f"{len(screws_)} x M4 up into the rail (into the corner gusset where it steps down); strip on its outer face")
        add(f"LED strip underglow {tag}", prism(strip, -half + 5.0, half - 5.0), "led", "bumper",
            bom="WS2812B strip 10 mm, 60/m (m)", kind="stock", note="aimed 45 deg down and out, under the bumper")
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
        out.append((f"tower {side}", V(sum(P.TOWER_X) / 2, sgn * (P.Y_SLOT + 10.0), P.Z_TOP - P.MEM_H)))
    for sx, end, dh in ((1, "front", 22.0), (-1, "rear", 17.5)):
        xe = P.front_x(zb) if sx > 0 else P.rear_x(zb)
        for y in P.END_MOUNT_Y:
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


def frame_mounts():
    """The chassis side of mount_points(), sized for Micah's own #10-32s. A printed post on each outer and end rail
    station is held by a 2-1/2 in #10-32 up through the rail (and gusset) into a heat-set insert in its foot, with a
    relief above the insert for the screw's tip. The frame's own 1/2 in #10-32 goes up through the post's 4 mm top
    into the frame; its head sits in a pocket that opens outward, behind the bumper (take the bumper ring off and
    every frame screw is in reach). Each turret tower gets a bracket on its outer face, held by two 1/2 in #10-32s in
    vertical slots (set its height against the deck at assembly) into rivnuts in the tower wall, so nothing pokes
    into the gun well."""
    zb, zr0, zr1 = P.Z_WALL_BOT, P.RAIL_Z[0], P.RAIL_Z[1]
    top_t = 4.0                                           # post top under the frame: 4 + 0.5 gap + 8.2 in the insert
    clear = lambda q, t=top_t: cyl(2.6, t + 2.0, (q.x, q.y, q.z - 0.5 - t - 1.0), (0, 0, 1))

    def foot(x, y, z0):                                   # the rail screw's insert, and room past it for its tip
        return cyl(P.INSERT_1032[0], P.INSERT_1032[1], (x, y, z0), (0, 0, 1)).fuse(cyl(2.6, 13.5, (x, y, z0), (0, 0, 1)))
    for name, q in mount_points():
        if name.startswith(("L ", "R ")):
            sgn = 1 if name[0] == "L" else -1
            y_in, y_out = P.OUTER_RAIL_Y
            yc = sgn * (y_in + y_out) / 2
            post = box(q.x - 15, q.x + 15, min(sgn * y_in, sgn * y_out), max(sgn * y_in, sgn * y_out), zr1, zb - 0.5)
            ya, yb_ = sorted([q.y - sgn * 6.0, sgn * (y_out + 3.0)])
            pocket = box(q.x - 7, q.x + 7, ya, yb_, zr1 + 16.0, zb - 0.5 - top_t)
            post = post.cut(pocket).cut(clear(q)).cut(foot(q.x, yc, zr1))
            add(f"Frame mount {name}", post, "print", "body", bom="Frame mount post (printed)", kind="print",
                note="2-1/2 in #10-32 up through the rail into its insert; the frame's 1/2 in #10-32 up from the outer "
                     "pocket into the frame tab (bumper ring off first)")
        elif name.startswith("tower"):
            sgn = 1 if name.endswith("L") else -1
            x0, x1 = P.TOWER_X
            yt = P.INNER_RAIL_Y[1]                        # tower's outer face
            web = box(x0, x1, min(sgn * yt, sgn * (yt + 8)), max(sgn * yt, sgn * (yt + 8)), q.z - 45.0, q.z - 0.5)
            plate = box(x0, x1, min(sgn * yt, sgn * (q.y * sgn + 9.0)), max(sgn * yt, sgn * (q.y * sgn + 9.0)),
                        q.z - 7.5, q.z - 0.5)
            brk = web.fuse(plate).cut(clear(q, 7.0))
            xm = (x0 + x1) / 2
            for zs in (q.z - 18.0, q.z - 34.0):          # two #10-32 x 1/2 in into rivnuts, slotted +-3 mm
                y0_, y1_ = sorted([sgn * (yt - 1.0), sgn * (yt + 9.0)])
                brk = brk.cut(box(xm - 2.6, xm + 2.6, y0_, y1_, zs - 5.6, zs + 5.6))
                brk = brk.cut(cyl(5.5, 1.2, (xm, sgn * yt, zs), (0, sgn, 0)))     # the rivnut's flange
            add(f"Tower bracket {name[-1]}", brk, "print", "body", bom="Turret tower bracket (printed)", kind="print",
                note="2 x #10-32 x 1/2 in in slots into rivnuts in the tower wall; the deck's 1/2 in #10-32 up "
                     "through its plate. Print it on an end face (the L flat on the bed)")
        else:
            sx = 1 if name.startswith("front") else -1
            xi, xo = sx * (P.FRAME_X - P.RAIL_W), sx * P.FRAME_X
            z0 = zr1 + (P.PLATE_T if abs(q.y) + 15 > P.INNER_RAIL_Y[0] else 0.0)   # on the corner gusset
            post = box(min(xi, xo), max(xi, xo), q.y - 15, q.y + 15, z0, zb - 0.5)
            inner = q.x - sx * 6.0                        # the pocket's inner end, round the screw head
            if (inner - xi) * sx < 3.0:                   # too close to the rail's inner edge: a cap over it,
                cap_x = xi - sx * 7.0                     # high above the wheel, keeps 3 mm of skin
                post = post.fuse(box(min(cap_x, xi), max(cap_x, xi), q.y - 15, q.y + 15, zb - 20.0, zb - 0.5))
                inner = xi - sx * 4.0
            pocket = box(min(inner, xo + sx * 3.0), max(inner, xo + sx * 3.0), q.y - 7, q.y + 7, z0 + 16.0,
                         zb - 0.5 - top_t)
            post = post.cut(pocket).cut(clear(q)).cut(foot(sx * (P.FRAME_X - 7.0), q.y, z0))
            add(f"Frame mount {name}", post, "print", "body", bom="Frame mount post (printed)", kind="print",
                note="2-1/2 in #10-32 up through the end rail" + (" and gusset" if z0 > zr1 else "") + " into its "
                     "insert; the frame's 1/2 in #10-32 from the outer pocket (bumper ring off first)")


REAR_HOLES = ((REAR_MAN[1] - 30.0, REAR_MAN[2], 9.0), (REAR_MAN[1] + 50.0, REAR_MAN[2], 14.0), (ESTOP[0], ESTOP[1], 23.0),
              (MAIN_Y - 39.5, REAR_MAN[2], 6.0),
              (CHARGE[0], CHARGE[1], 26.0), (USB[0], USB[1], 10.0))


CUP_SCREWS, BAR_SCREWS = [], []          # (point on the part's face, direction into the frame): set by body_parts


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
    # light bar brackets: a plate on the front slant's bottom lip with 2 x M4 into inserts square to the face
    BAR_SCREWS.clear()
    nf = V(math.sin(math.radians(P.FRONT_ANGLE)), 0, math.cos(math.radians(P.FRONT_ANGLE)))
    tf = V(-math.cos(math.radians(P.FRONT_ANGLE)), 0, math.sin(math.radians(P.FRONT_ANGLE)))
    for sg in (1, -1):
        for dy in (-8.0, 8.0):
            at = V(P.FRAME_X, sg * P.LIGHT_BAR[4] + dy, P.Z_WALL_BOT) + tf * 8.5
            hole = cyl(P.INSERT[0], P.INSERT[1], (at + nf * 0.1).toTuple(), (nf * -1).toTuple())
            if _frame_insert(pieces, hole, tun_list + screws, share=0.9):
                BAR_SCREWS.append((sg, at, nf * -1))
            else:
                clash.append(f"light bar bracket screw at y {sg * P.LIGHT_BAR[4] + dy:.0f} found no frame")
    log(f"speaker cup screws: {len(CUP_SCREWS)} of 8, light bar bracket screws: {len(BAR_SCREWS)} of 4"
        + (f"; check {clash}" if clash else ""))
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
        if p["n"].x < -0.9:                      # rear face: fill port, tank relief, E-stop, charge port, USB-C
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
                note="M4 x 6 button head into an M4 x 4 insert" if short_ else "M4 x 8 button head into an M4 x 6 insert")
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
