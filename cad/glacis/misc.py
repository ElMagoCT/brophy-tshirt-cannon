"""Everything else: towers and pivot bearings, the elevation motor, belt and angle pot, both reservoir tanks,
the rear manifold and fill block, the battery sleds, the back-bottom electronics bay, the smoke machine and its
ducts, FRC-style bumpers, wall standoffs, the recessed acrylic panels with their corner clips, and the
printed body-frame pieces."""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
import body as B
from lib import add, box, cyl, tube, hex_prism, union
from drive import tube_part, fr8, _hull, bearing_seat

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
            note="PA-CF, 3 x 1/4-20 through the tower")
        for yb, d in ((y0, sgn), (y1, -sgn)):
            add(f"Pivot bearing {side} {yb:.0f}", fr8(px, sgn * yb, pz, d, hexbore=True), "steel", "frame",
                bom="Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)")
    # elevation: goBILDA 5203 (99.5:1, 60 rpm) on a Spark MAX, 16T -> 56T HTD 5M 9 mm belt on the right axle end
    mx_, mz_ = P.ELEV_MOTOR_X, P.ELEV_MOTOR_Z
    ya, yb_ = P.ELEV_PULLEY_Y
    y_face = -(yb_ + 2.0)
    mot = cyl(18.0, 50.3, (mx_, y_face, mz_), (0, -1, 0)).fuse(cyl(18.75, 74.8, (mx_, y_face - 50.3, mz_), (0, -1, 0))).fuse(
        cyl(4.0, 23.5, (mx_, y_face, mz_), (0, 1, 0)))
    add("Elevation motor goBILDA 5203 99.5:1", mot, "black", "frame",
        bom="goBILDA 5203-2402-0100 Yellow Jacket 99.5:1, 60 rpm (FTC motor)", note="Spark MAX, brushed mode")
    pin = cyl(P.pd(P.ELEV_T[0]) / 2 + 2.5, yb_ - ya, (mx_, -yb_, mz_), (0, 1, 0)).cut(
        cyl(4.1, 40, (mx_, -yb_ - 5, mz_), (0, 1, 0)))
    add("Elevation pinion 16T", pin, "print_d", "frame", bom="Elevation pinion 16T HTD 9 mm (8 mm REX bore)", kind="print")
    yi, yo = y_face - 2.0, y_face - 30.0
    brk = union([box(px - 10.0, px + 25.0, yo, yi, mz_ - 20.0, pz - 28.0),          # web under the bearing block
                 box(px - 10.0, mx_ + 26.0, yo, yi, mz_ - 24.0, mz_ + 24.0)])        # arm out to the motor
    brk = brk.cut(cyl(18.3, 60, (mx_, yi + 5, mz_), (0, -1, 0)))
    add("Elevation motor bracket", brk, "print", "frame", bom="Elevation motor bracket", kind="print",
        note="PA-CF, hangs from the right bearing block; slotted for belt tension")
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
    bri = box(px - 30, px + 30, yb + 37.0, yb + 40.2, pz - 30, pz + 30).cut(cyl(5.0, 10, (px, yb + 35, pz), (0, 1, 0)))
    for sx in (-1, 1):
        bri = bri.fuse(box(px + sx * 24 - 3, px + sx * 24 + 3, yb, yb + 37.0, pz - 30, pz + 30))
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


REAR_MAN = (-347.0, 93.5, 255.0)             # rear manifold centre, back bottom, behind the rear panel
FILL = (-248.6, 80.0, 200.0)                 # fill block centre (5-port), back bottom bay
CHECKS = []                                  # outlets of the two inline check valves (service loops start here)
FOG_OUT = []                                 # fog splitter barbs for the two gun lines


def air():
    L, R = P.TANK_L, P.TANK_D / 2
    tx, ty, tz = P.TANK_SIDE
    zp = tz - R - 8
    tank_out = {}
    for sgn, side in ((1, "left"), (-1, "right")):
        c = (tx, sgn * ty, tz)
        shell = _tank_shell("x", c)
        for dx in (-80.0, 0.0, 80.0):
            shell = shell.fuse(cyl(9.0, 12.0, (tx + dx, sgn * ty, tz - R + 4), (0, 0, -1)))
        add(f"Air tank {side} (6 L 200 psi)", shell, "tank", "pneu",
            bom="Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT (owner's AliExpress pick)")
        xb0 = tx - 80.0
        el = cyl(7.5, 10.0, (xb0, sgn * ty, zp), (0, 0, -1)).fuse(cyl(7.0, 16.0, (xb0, sgn * ty, zp - 6), (-1, 0, 0)))
        add(f"Tank elbow push-to-connect {side}", el, "brass", "pneu", bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT")
        tank_out[side] = (xb0 - 16.0, sgn * ty, zp - 6)
        for dx in (0.0, 80.0):
            add(f"Tank plug {side} {dx:.0f}", cyl(9.0, 12.0, (tx + dx, sgn * ty, zp), (0, 0, -1)), "brass", "pneu",
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
        for xs in (26.0, 106.0):
            add(f"Tank strap {side} {xs:.0f}", tube(R + 2.5, R + 0.5, 25.0, (xs - 12.5, sgn * ty, tz), (1, 0, 0)), "black",
                "pneu", bom="1 in cam-buckle strap")
    # rear manifold (200 psi zone), back bottom: tank lines and transducer on top, 200 psi relief, Schrader fill
    # port and manual bleed out through the bottom of the rear panel, line to the fill valve on its front face
    mx, my, mz = REAR_MAN
    add("Rear manifold block", box(mx - 12.7, mx + 12.7, my - 63.5, my + 63.5, mz - 12.7, mz + 12.7), "brass", "pneu",
        bom="Rear manifold: 1/4 NPT brass crosses + close nipples (built)")
    top = mz + 12.7
    add("Tank relief valve 200 psi", cyl(9.5, 44.0, (mx, my + 15.0, top), (0, 0, 1)), "brass", "pneu",
        bom="Relief valve 200 psi 1/4 NPT, pull ring (CAS250200)")
    add("Tank transducer 0-300 psi", cyl(10.0, 55.0, (mx, my - 15.0, top), (0, 0, 1)), "steel", "pneu",
        bom="Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT")
    for dy, tag in ((-45.0, "right tank"), (45.0, "left tank")):
        add(f"Rear manifold push-to-connect {tag}", cyl(7.5, 18.0, (mx, my + dy, top), (0, 0, 1)), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    add("Rear manifold push-to-connect fill out", cyl(7.5, 18.0, (mx + 12.7, my - 40.0, mz), (1, 0, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    rear = P.rear_x(mz) + P.CLIP_T + P.ACRYLIC_T          # inner face of the rear panel at this height
    for name, dy, kind in (("Fill port (Schrader)", -30.0, "fill"), ("Bleed ball valve (rear)", 30.0, "bleed")):
        yb = my + dy
        add(f"{name} nipple", cyl(6.86, mx - 12.7 - rear + 2, (mx - 12.7 + 2, yb, mz), (-1, 0, 0)), "brass", "pneu",
            bom="1/4 NPT brass nipple x 1-1/2 in")
        if kind == "fill":
            add(name, cyl(6.0, 22.0, (rear, yb, mz), (-1, 0, 0)), "brass", "pneu", bom="1/4 MNPT tank fill valve (Schrader)")
        else:
            xo = P.rear_x(mz) - 0.5
            vb = cyl(11.0, rear + 10.2 - (xo - 6), (rear + 10.2, yb, mz), (-1, 0, 0)).cut(
                cyl(6.86, 10.2, (rear + 10.3, yb, mz), (-1, 0, 0)))
            add(name, vb.fuse(box(xo - 6, xo - 2, yb, yb + 40, mz - 3, mz + 3)), "brass", "pneu",          # lever lies sideways
                bom="1/4 FNPT mini ball valve (manual bleed)", note="lever outside the rear panel")
    # fill valve + 5-port fill block (chamber zone: 110 psi software cap, 125 psi relief): transducer up, relief +y, two outlets through
    # inline check valves (one per cannon, so one shot can't vent the other chamber)
    fx, fy, fz = FILL
    sx1 = fx - 12.7 - 1.8
    add("Fill solenoid", box(sx1 - 37.0, sx1, fy - 14, fy + 14, fz - 19, fz + 19).fuse(
        cyl(15.0, 38.0, (sx1 - 18.5, fy + 14, fz), (0, 1, 0))), "brass", "pneu",
        bom="2/2 NC 12 V solenoid valve, 1/4 NPT (fill / metering)", note="coil to the side")
    add("Fill solenoid push-to-connect", cyl(7.5, 22.0, (sx1 - 37.0, fy, fz), (-1, 0, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    add("Fill block", box(fx - 12.7, fx + 12.7, fy - 12.7, fy + 12.7, fz - 12.7, fz + 12.7), "brass", "pneu",
        bom="1/4 NPT brass 5-port block (Interstate CPT44-5)", note="close nipple from the fill valve")
    add("Fill transducer 0-200 psi", cyl(10.0, 55.0, (fx, fy, fz + 12.7), (0, 0, 1)), "steel", "pneu",
        bom="Pressure transducer 0-200 psi, 0.5-4.5 V, 1/8 NPT (+ 1/4 x 1/8 bushing)")
    add("Fill relief valve 125 psi", cyl(9.5, 44.0, (fx, fy + 12.7, fz), (0, 1, 0)), "brass", "pneu",
        bom="Relief valve 125 psi 1/4 MNPT, ASME, pull ring (Milton 1090-125)")
    CHECKS.clear()
    for d, tag in ((V(1, 0, 0), "A (top cannon)"), (V(0, -1, 0), "B (bottom cannon)")):
        a0 = V(fx, fy, fz) + d * 12.7
        cart = cyl(11.0, 54.0, (a0 + d * 15.0).toTuple(), d.toTuple()).fuse(cyl(7.5, 84.0, a0.toTuple(), d.toTuple()))
        add(f"Check valve inline {tag}", cart, "brass", "pneu",
            bom="Brass check valve 1/4 FNPT, 250 psi (Conrader) + nipple + push-to-connect", note="on the fill block")
        CHECKS.append(a0 + d * 88.0)
    # tubes: tanks -> rear manifold, rear manifold -> fill valve
    for side, dy in (("left", 45.0), ("right", -45.0)):
        t = tank_out[side]
        sg = 1 if side == "left" else -1
        if sg > 0:                                         # under the sled rails' inboard ends, then up beside the manifold
            mid = [(-325.0, 112.0, 245.0), (-325.0, 112.0, 330.0)]
        else:                                              # across the bay above the boards
            mid = [(-330.0, -40.0, 245.0), (mx + 2.0, my + dy, 330.0)]
        pts = [t, (t[0] - 20.0, sg * 120.0, 262.0), (-200.0, sg * 112.0, 245.0)] + mid + \
              [(mx, my + dy, 330.0), (mx, my + dy, top + 18.0)]
        add(f"Tube tank {side}", tube_path(pts), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")
    tf = [(mx + 12.7 + 18.0, my - 40.0, mz), (sx1 - 70.0, fy, mz - 20.0), (sx1 - 70.0, fy, fz), (sx1 - 37.0 - 22.0, fy, fz)]
    add("Tube to fill valve", tube_path(tf), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")


# ------------------------------------------------------------------ fog
def fog():
    """12 V automotive (EVAP) smoke machine in the front bay, printed 1 -> 4 splitter: two lines to vents under the
    front bumper, two flexible lines up to the vents in the gun's mantlet."""
    (x0, x1), (y0, y1), (z0, z1) = P.FOG_BOX
    add("Smoke machine (12 V EVAP smoker)", box(x0, x1, y0, y1, z0, z1), "black", "power",
        bom="Smoke machine: AutoLine Pro HyperSmoke 12 V EVAP smoker", note="heater and pump on MOSFETs from the STM32; box is a placeholder")
    add("Fog machine cradle", box(x0 - 6, x1 + 6, y0 - 6, y1 + 6, P.BELLY_Z, z0 + 20).cut(box(x0, x1, y0, y1, z0, z0 + 21)).cut(
        box(x0 + 20, x1 - 20, y0 + 15, y1 - 15, P.BELLY_Z - 1, z0 + 1)),
        "print", "power", bom="Fog machine cradle", kind="print")
    cx = (x0 + x1) / 2
    add("Fog outlet adapter", tube(13.0, 10.0, 14.0, (cx, 0, z1), (0, 0, 1)), "print", "power",
        bom="Fog outlet adapter (measure the nozzle first)", kind="print")
    hub = box(cx - 22, cx + 22, -28, 28, z1 + 14, z1 + 44).cut(box(cx - 19, cx + 19, -25, 25, z1 + 13, z1 + 41))
    barbs = []
    for sy in (1, -1):                                     # bumper lines out the sides, gun lines out the top
        hub = hub.fuse(tube(11.0, 8.5, 16.0, (cx, sy * 28.0, z1 + 29), (0, sy, 0)))
        hub = hub.fuse(tube(11.0, 8.5, 16.0, (cx - 10, sy * 14.0, z1 + 44), (0, 0, 1)))
        barbs.append(((cx, sy * 44.0, z1 + 29), (cx - 10, sy * 14.0, z1 + 60)))
    add("Fog splitter 1-4", hub, "print", "power", bom="Fog splitter 1 -> 4 (printed)", kind="print",
        note="22 mm barbs for the four flexible tubes")
    FOG_OUT.clear()
    for k, sy in enumerate((1, -1)):
        side_b, top_b = barbs[k]
        vx, vy = 368.0, sy * 80.0
        add(f"Fog vent bumper {'L' if sy > 0 else 'R'}", tube(13.0, 10.0, 14.0, (vx, vy, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1)).fuse(
            tube(16.0, 10.0, 3.0, (vx, vy, P.BELLY_Z - P.PLATE_T - 14.0), (0, 0, 1))), "print", "power",
            bom="Fog vent nozzle (under bumper)", kind="print", note="through a hole in the bellypan")
        add(f"Fog tube bumper {'L' if sy > 0 else 'R'}", tube_path([side_b, (side_b[0] + 30, vy, side_b[2]), (vx, vy, P.BELLY_Z + 10.0),
                                                                     (vx, vy, P.BELLY_Z - P.PLATE_T)], r=11.0),
            "tube", "power", bom="Fog tube (owner's flexible tube)", kind="stock")
        FOG_OUT.append(V(*top_b))


# ------------------------------------------------------------------ power + controls
def batteries_and_electronics():
    L, W, H = P.BATT
    zs = P.RAIL_Z[1] + 104.0 + 25.4                       # sled rail top
    for sgn, side in ((1, "left"), (-1, "right")):
        for xr in (-320.0, -215.0):
            post(f"Sled post {side} {xr:.0f} (1x1)", xr, sgn * IY, P.RAIL_Z[1], P.RAIL_Z[1] + 104.0)
            tube_part(f"Sled rail {side} {xr:.0f} (1x1)", "y", sgn * 118.0, sgn * 262.0, xr, P.RAIL_Z[1] + 104.0 + 12.7)
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
        add(f"Anderson SB50 {side}", box(-252.0, -232.0, min(sgn * 128.0, sgn * 152.0), max(sgn * 128.0, sgn * 152.0),
                                          300.0, 325.0), "red", "power", bom="Anderson SB50 pair + 6 AWG contacts (stash)")
    # back bottom bay: PDH and breaker on the bellypan, controls and the fill block on a printed shelf
    zb = P.BELLY_Z
    add("Power distribution (REV PDH)", box(-370.0, -267.0, -86.5, 86.5, zb, zb + 36), "black", "power",
        bom="REV PDH (owned) + ATO breakers / fuses (stash)")
    add("Main breaker 120 A", box(-255.0, -218.0, -20.0, 20.0, zb, zb + 40), "black", "power", bom="120 A main breaker (stash)")
    shelf = box(-380.0, -180.0, -125.0, 125.0, 150.0, 154.0)
    for (x, y) in ((-372, -117), (-372, 117), (-188, -117), (-188, 117)):
        shelf = shelf.fuse(box(x - 5, x + 5, y - 5, y + 5, zb, 150.0))
    add("Electronics shelf", shelf, "print", "power", bom="Electronics shelf", kind="print")
    z = 154.0
    boards = [("STM32 Nucleo-F446RE (main controller)", -375, -305, -102, -20, 20, "pcb", "STM32 Nucleo-64 NUCLEO-F446RE"),
              ("ESP32-S3 WiFi bridge", -295, -226, -48, -20, 15, "pcb", "ESP32-S3-DevKitC-1 N8R8"),
              ("ESP32-S3 safety node", -295, -226, -84, -56, 15, "pcb", "ESP32-S3-DevKitC-1 N8R8"),
              ("PWM gate (74AHCT125)", -295, -245, -122, -96, 12, "pcb", "SN74AHCT125N quad buffer + perfboard"),
              ("Spark MAX (elevation)", -220, -185, -125, -55, 25, "black", "REV Spark MAX (owned)"),
              ("Safety relay 40 A", -375, -347, -125, -107, 36, "black", "12 V 40 A SPDT relay + socket"),
              ("Valve + fog drivers (relays, ULN2803A)", -378, -308, 10, 70, 32, "pcb", "12 V 40 A SPDT relay + socket"),
              ("Buck 12-5 V 20 A", -378, -322, 75, 125, 25, "black", "12->5 V 20 A buck (B089M5R3NJ)")]
    for name, x0, x1, y0, y1, h, col, bom in boards:
        add(name, box(x0, x1, y0, y1, z, z + h), col, "power", bom=bom)
    # bottom of the rear panel: E-stop, standby charge port (fill port and bleed come out of the manifold)
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


ESTOP = (-170.0, 255.0)     # (y, z) on the rear panel, bottom strip under the open middle
CHARGE = (-95.0, 255.0)
USB = (182.0, 255.0)


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
    for name, sgm in segs.items():
        a0, a1 = sgm["span"]
        ox, oy = sgm["out"]
        if sgm["axis"] == "y":
            bx0, bx1 = sorted([sgm["pos"], sgm["pos"] + ox * t])
            backing = box(bx0, bx1, -yo, yo, zb0, zb1 - 8)
        else:
            by0, by1 = sorted([sgm["pos"], sgm["pos"] + oy * t])
            backing = box(-xf, xf, by0, by1, zb0, zb1 - 8)
        n = math.ceil(abs((yo if sgm["axis"] == "y" else xf) * 2) / 230.0)
        for k in range(n):
            if sgm["axis"] == "y":
                lo = -yo + 2 * yo * k / n
                piece = backing.intersect(box(-1000, 1000, lo, lo + 2 * yo / n, -1000, 1000))
            else:
                lo = -xf + 2 * xf * k / n
                piece = backing.intersect(box(lo, lo + 2 * xf / n, -1000, 1000, -1000, 1000))
            if sgm["axis"] == "x":                    # side backings: pockets for the axle end screws
                for sx in (-1, 1):
                    piece = piece.cut(cyl(14.0, 40, (sx * P.AX_X, sgm["pos"] - 20 * oy, P.AXLE_Z), (0, oy, 0)))
            add(f"Bumper backing {name} {k + 1}", piece, "print", "bumper", bom="Bumper backing segment", kind="print",
                note="bolts through the rail with #10-32 + nylocks")
        for i, zc in enumerate((zb0 + r, zb0 + 3 * r)):
            if sgm["axis"] == "y":
                c = sgm["pos"] + ox * (t + r)
                nd = _mitre(cyl(r, a1 - a0, (c, a0, zc), (0, 1, 0)), sgm, yo, xf, reach)
            else:
                c = sgm["pos"] + oy * (t + r)
                nd = _mitre(cyl(r, a1 - a0, (a0, c, zc), (1, 0, 0)), sgm, yo, xf, reach)
            nd = nd.cut(cyl(12.7, 3000, (c if sgm["axis"] == "y" else -1500, -1500 if sgm["axis"] == "y" else c, zc),
                            (0, 1, 0) if sgm["axis"] == "y" else (1, 0, 0)))
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


def wall_standoffs():
    """Printed posts on the outer rails; the side-wall frame bolts to their outer face (2 x M4, heat-set)."""
    for sgn, side in ((1, "L"), (-1, "R")):
        y_in, y_out = P.OUTER_RAIL_Y
        for x in (-280.0, -120.0, 100.0, 280.0):
            v = box(x - 15, x + 15, min(sgn * y_in, sgn * y_out), max(sgn * y_in, sgn * y_out), P.RAIL_Z[1],
                    P.Z_WALL_BOT - 0.5).fuse(box(x - 15, x + 15, min(sgn * y_out, sgn * 288.0), max(sgn * y_out, sgn * 288.0),
                                                 P.Z_WALL_BOT - 6.0, P.Z_WALL_BOT - 0.5))
            add(f"Wall standoff {side} {x:.0f}", v, "print", "body", bom="Wall standoff", kind="print",
                note="#10-32 through the rail; the wall frame sits on its lip, 2 x M4 up into it")


REAR_HOLES = ((REAR_MAN[1] - 30.0, REAR_MAN[2], 9.0), (REAR_MAN[1] + 30.0, REAR_MAN[2], 14.0), (ESTOP[0], ESTOP[1], 23.0),
              (CHARGE[0], CHARGE[1], 26.0), (USB[0], USB[1], 10.0))


def body_parts(log=print):
    body, frame, panels = B.build(log=log)
    pieces, edges = B.section(frame, panels, log=log)
    B.add_joints(pieces, panels, log=log)
    slivers = 0
    for p in pieces:
        sol = sorted(p["shape"].Solids(), key=lambda x: -x.Volume())
        keep = [x for x in sol if x.Volume() > 0.03 * sol[0].Volume()]
        slivers += len(sol) - len(keep)
        p["shape"] = keep[0] if len(keep) == 1 else cq.Compound.makeCompound(keep)
        add(f"Body frame {p['name']}", p["shape"], "print", "body", bom=f"Body frame piece {p['name']}", kind="print",
            note="PETG/ASA, 4 walls, 25% gyroid")
    led = 0.0
    nclip = 0
    for i, p in enumerate(panels):
        a = B.slab(p["poly"], p["n"], P.MEM_W - P.REBATE_W + 0.3, P.CLIP_T, P.ACRYLIC_T)
        if p["n"].x < -0.9:                      # rear face: fill port, bleed lever, E-stop, charge port, USB-C
            for (yb, zb, r) in REAR_HOLES:
                a = a.cut(cyl(r, 30, (-P.FRAME_X - 10, yb, zb), (1, 0, 0)))
        u, w = B._plane_basis(p["n"])
        us = [V(*q).dot(u) for q in p["poly"]]
        ws = [V(*q).dot(w) for q in p["poly"]]
        dims = sorted([max(us) - min(us), max(ws) - min(ws)])
        door = abs(p["n"].y) > 0.9 and max(q[0] for q in p["poly"]) < P.SIDE_SPLIT_X + 1
        add(f"Panel {i:02d}{' (battery door)' if door else ''}", a, "acrylic", "body",
            bom="Frosted acrylic panel 1/8 in (owned)", kind="acrylic", note=f"{dims[1] / IN:.1f} x {dims[0] / IN:.1f} in outline")
        led += _perimeter(p)
        for k, c in enumerate(p["clips"]):
            add(f"Panel clip {i:02d}-{k}", c["clip"], "print", "body", bom="Panel corner clip", kind="print",
                note="M3 x 8 into a heat-set insert")
            nclip += 1
    log(f"body: {len(pieces)} frame pieces ({slivers} slivers dropped), {len(panels)} panels, {nclip} clips, "
        f"LED slot {led / 1000:.1f} m")
    return panels


def _perimeter(p):
    pl, pts = B._wp_on(p["poly"], p["n"])
    w = cq.Workplane(pl).polyline(pts).close().wires().val().offset2D(-P.MEM_W, "intersection")[0]
    return sum(e.Length() for e in w.Edges())
