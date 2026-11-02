"""Everything else: towers and pivot bearings, the elevation motor, belt and angle pot, both tanks and the
rear air manifold, the battery sled, electronics, the compressor spot, FRC-style bumpers, wall standoffs,
the recessed acrylic panels with their corner clips, and the printed body-frame pieces."""
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
    for sgn, side, (x0, x1) in ((1, "L", P.TOWER_L_X), (-1, "R", P.TOWER_R_X)):
        yc = sgn * IY
        post(f"Turret tower {side} (1x1)", (x0 + x1) / 2, yc, P.RAIL_Z[1], pz + 40.0)
        for xf, d in ((x0, -1), (x1, 1)):
            leg_v = box(min(xf, xf + d * P.PLATE_T), max(xf, xf + d * P.PLATE_T), yc - 12.7, yc + 12.7,
                        P.RAIL_Z[1], P.RAIL_Z[1] + 60)
            leg_h = box(min(xf, xf + d * 15), max(xf, xf + d * 15), yc - 12.7, yc + 12.7,
                        P.RAIL_Z[1], P.RAIL_Z[1] + P.PLATE_T)
            add(f"Tower base gusset {side} {'rear' if d < 0 else 'front'}", leg_v.fuse(leg_h), "alu", "frame",
                bom="Tower base gusset (1/8 Al, bent)", kind="stock", note="3/16 rivets")
        # bearing block bridging from the tower to the pivot: two flanged 1/2 hex bearings
        y0, y1 = P.BEARING_BLOCK_Y
        bx = (x1, px + 25.0) if sgn > 0 else (px - 25.0, x0)
        blk = box(bx[0], bx[1], min(sgn * y0, sgn * y1), max(sgn * y0, sgn * y1), pz - 28, pz + 28)
        blk = blk.cut(cyl(9.0, 800, (px, -400, pz), (0, 1, 0)))
        blk = blk.cut(bearing_seat(px, sgn * y0, pz, sgn, 7.94)).cut(bearing_seat(px, sgn * y1, pz, -sgn, 7.94))
        add(f"Pivot bearing block {side}", blk, "print_d", "frame", bom="Pivot bearing block", kind="print",
            note="PA-CF, 2 x 1/4-20 through the tower")
        for yb, d in ((y0, sgn), (y1, -sgn)):
            add(f"Pivot bearing {side} {yb:.0f}", fr8(px, sgn * yb, pz, d, hexbore=True), "steel", "frame",
                bom="Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)")
    # elevation: goBILDA 5203 (99.5:1) on a Spark MAX, 16T -> 56T HTD 5M 9 mm belt on the right stub
    mx_, mz_ = P.ELEV_MOTOR_X, P.ELEV_MOTOR_Z
    ya, yb_ = P.ELEV_PULLEY_Y
    y_face = -(ya - 2.0)
    mot = cyl(18.0, 50.3, (mx_, y_face, mz_), (0, 1, 0)).fuse(cyl(18.75, 74.8, (mx_, y_face + 50.3, mz_), (0, 1, 0))).fuse(
        cyl(4.0, 23.5, (mx_, y_face, mz_), (0, -1, 0)))
    add("Elevation motor goBILDA 5203 99.5:1", mot, "black", "frame",
        bom="goBILDA 5203-2402-0100 Yellow Jacket 99.5:1 (FTC motor)", note="Spark MAX, brushed mode")
    pin = cyl(P.pd(P.ELEV_T[0]) / 2 + 2.5, yb_ - ya, (mx_, -yb_, mz_), (0, 1, 0)).cut(
        cyl(4.1, 40, (mx_, -yb_ - 5, mz_), (0, 1, 0)))
    add("Elevation pinion 16T", pin, "print_d", "frame", bom="Elevation pinion 16T HTD 9 mm (8 mm REX bore)",
        kind="print")
    brk = box(mx_ - 24, mx_ + 24, -P.INNER_RAIL_Y[1], -140.0, P.RAIL_Z[1], mz_ + 24)
    brk = brk.cut(cyl(18.3, 60, (mx_, -170, mz_), (0, 1, 0))).cut(cyl(19.0, 40, (mx_, y_face + 50.0, mz_), (0, 1, 0)))
    add("Elevation motor bracket", brk, "print", "frame", bom="Elevation motor bracket", kind="print",
        note="on the right inner rail, slotted for belt tension")
    circles = [(P.PIVOT[0], P.PIVOT[1], P.pd(P.ELEV_T[1]) / 2), (mx_, mz_, P.pd(P.ELEV_T[0]) / 2)]
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
    # arm-angle pot on the end of the left stub (read by the STM32 ADC)
    add("Pot coupler", cyl(9.0, 13.0, (px, 157.0, pz), (0, 1, 0)).cut(cyl(7.45, 7.5, (px, 156.5, pz), (0, 1, 0))),
        "print_d", "frame", bom="Pot coupler (1/2 hex to 6 mm D)", kind="print")
    add("Arm-angle pot", cyl(12.0, 12.0, (px, 176.0, pz), (0, 1, 0)).fuse(cyl(4.8, 6.0, (px, 170.0, pz), (0, 1, 0))),
        "black", "frame", bom="10k linear pot, 6 mm shaft (arm angle)")
    bri = box(px - 30, px + 30, 188.0, 191.2, pz - 30, pz + 30).cut(cyl(5.0, 10, (px, 186, pz), (0, 1, 0)))
    for sx in (-1, 1):
        bri = bri.fuse(box(px + sx * 24 - 3, px + sx * 24 + 3, P.BEARING_BLOCK_Y[1], 188.0, pz - 30, pz + 30))
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


REAR_MAN = (-372.0, 183.5, 300.0)            # rear manifold centre (left rear corner, above the wheel)
FILL = (-128.5, 210.0, 330.0)                # fill cross centre (left side beside the pivot)
CHECKS = []                                  # outlet points of the two inline check valves (service loops start here)


def air():
    L, R = P.TANK_L, P.TANK_D / 2
    # left tank, lying along x on two cantilevered 1x1 arms over the front-left wheel, ports facing down
    tx, ty, tz = P.TANK_LEFT
    shell = _tank_shell("x", P.TANK_LEFT)
    for dx in (-80.0, 0.0, 80.0):
        shell = shell.fuse(cyl(9.0, 12.0, (tx + dx, ty, tz - R + 4), (0, 0, -1)))
    add("Air tank left (6 L 200 psi)", shell, "tank", "pneu", bom="Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT (owner's AliExpress pick)")
    xb0 = tx - 80.0
    zp = tz - R - 8
    el = cyl(7.5, 10.0, (xb0, ty, zp), (0, 0, -1)).fuse(cyl(7.0, 16.0, (xb0, ty, zp - 6), (-1, 0, 0)))
    add("Tank elbow push-to-connect left", el, "brass", "pneu", bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT")
    for dx, note in ((0.0, ""), (80.0, "future pump inlet")):
        add(f"Tank plug left {dx:.0f}", cyl(9.0, 12.0, (tx + dx, ty, zp), (0, 0, -1)), "brass", "pneu",
            bom="1/4 NPT brass plug", note=note)
    for xb in (-30.0, 240.0):
        post(f"Tank post {xb:.0f} (1x1)", xb, IY, P.RAIL_Z[1], P.RAIL_Z[1] + 104.0)
        tube_part(f"Tank arm {xb:.0f} (1x1)", "y", P.INNER_RAIL_Y[0], 270.0, xb, P.RAIL_Z[1] + 104.0 + 12.7)
        add(f"Tank arm gusset {xb:.0f}", box(xb - 12.7, xb + 12.7, P.INNER_RAIL_Y[0], P.INNER_RAIL_Y[0] + 80.0,
            P.RAIL_Z[1] + 129.4, P.RAIL_Z[1] + 129.4 + P.PLATE_T), "alu", "pneu", bom="Arm gusset (1/8 Al)", kind="stock")
        sad = box(xb - 14, xb + 14, ty - 68, ty + 72, P.RAIL_Z[1] + 129.4 + P.PLATE_T, tz).cut(
            cyl(R + 1.0, 60, (xb - 30, ty, tz), (1, 0, 0)))
        add(f"Tank saddle left {xb:.0f}", sad, "print", "pneu", bom="Tank saddle", kind="print")
    for xs in (0.0, 165.0):
        add(f"Tank strap left {xs:.0f}", tube(R + 2.5, R + 0.5, 25.0, (xs - 12.5, ty, tz), (1, 0, 0)), "black", "pneu",
            bom="1 in cam-buckle strap")
    # rear tank, standing in the rear centre on a printed base cup, steadied by an arm to the left tower
    rx, ry, rz = P.TANK_REAR
    shell = _tank_shell("z", P.TANK_REAR)
    for dz in (-80.0, 0.0, 80.0):
        shell = shell.fuse(cyl(9.0, 12.0, (rx, ry + R - 4, rz + dz), (0, 1, 0)))
    add("Air tank rear (6 L 200 psi)", shell, "tank", "pneu", bom="Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT (owner's AliExpress pick)")
    zr = rz + 80.0
    el = cyl(7.5, 10.0, (rx, ry + R + 8, zr), (0, 1, 0)).fuse(cyl(7.0, 16.0, (rx, ry + R + 14, zr), (0, 0, 1)))
    add("Tank elbow push-to-connect rear", el, "brass", "pneu", bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT")
    for dz in (-80.0, 0.0):
        add(f"Tank plug rear {dz:.0f}", cyl(9.0, 12.0, (rx, ry + R + 8, rz + dz), (0, 1, 0)), "brass", "pneu",
            bom="1/4 NPT brass plug")
    z0 = rz - L / 2
    cup = cyl(R + 8.0, 31.0, (rx, ry, P.BELLY_Z), (0, 0, 1)).cut(cyl(R + 0.5, 40, (rx, ry, z0), (0, 0, 1)))
    cup = cup.cut(box(rx - 200, rx + 200, ry + R - 20, ry + R + 30, z0, z0 + 40)).cut(
        box(-1000, -P.FRAME_X + P.RAIL_W + 0.5, -500, 500, 0, 500))
    add("Rear tank base cup", cup, "print", "pneu", bom="Rear tank base cup", kind="print", note="bolts through the bellypan")
    za = 315.0                                        # between the tank's ports, under the left chamber
    arm = tube(R + 8.0, R + 0.5, 25.0, (rx, ry, za), (0, 0, 1)).intersect(box(rx - 200, rx + 200, ry, ry + 200, 0, 900)).fuse(
        box(P.TOWER_L_X[0] - 6, P.TOWER_L_X[0], ry + R, P.INNER_RAIL_Y[1], za, za + 25)).fuse(
        box(rx + 40, P.TOWER_L_X[0], ry + R - 10, ry + R + 6, za, za + 25))
    arm = arm.cut(cyl(R + 0.5, 60, (rx, ry, za - 10), (0, 0, 1)))
    add("Rear tank clamp arm", arm, "print", "pneu", bom="Rear tank clamp arm", kind="print",
        note="half clamp + strap round the tank, bolts to the back of the left tower")
    # rear manifold (200 psi zone): top = rear tank tube, transducer, 200 psi relief; front = left tank tube and
    # the line to the fill valve; rear face = Schrader fill port and manual bleed, through the rear panel
    mx, my, mz = REAR_MAN
    add("Rear manifold block", box(mx - 12.7, mx + 12.7, my - 63.5, my + 63.5, mz - 12.7, mz + 12.7), "brass", "pneu",
        bom="Rear manifold: 1/4 NPT brass crosses + close nipples (built)")
    top = mz + 12.7
    add("Tank relief valve 200 psi", cyl(9.5, 44.0, (mx, my + 15.0, top), (0, 0, 1)), "brass", "pneu",
        bom="Relief valve 200 psi 1/4 NPT, pull ring (CAS250200)")
    add("Tank transducer 0-300 psi", cyl(10.0, 55.0, (mx, my - 15.0, top), (0, 0, 1)), "steel", "pneu",
        bom="Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT")
    add("Rear manifold push-to-connect top", cyl(7.5, 18.0, (mx, my - 45.0, top), (0, 0, 1)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    for dy, tag in ((0.0, "fill out"), (45.0, "left tank")):
        add(f"Rear manifold push-to-connect {tag}", cyl(7.5, 18.0, (mx + 12.7, my + dy, mz), (1, 0, 0)), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    rear = -P.FRAME_X + P.CLIP_T + P.ACRYLIC_T          # inner face of the rear panel
    for name, dy, kind in (("Fill port (Schrader)", -30.0, "fill"), ("Bleed ball valve (rear)", 30.0, "bleed")):
        yb = my + dy
        add(f"{name} nipple", cyl(6.86, mx - 12.7 - rear + 2, (mx - 12.7 + 2, yb, mz), (-1, 0, 0)), "brass", "pneu",
            bom="1/4 NPT brass nipple x 1-1/2 in")
        if kind == "fill":
            add(name, cyl(6.0, 22.0, (rear, yb, mz), (-1, 0, 0)), "brass", "pneu", bom="1/4 MNPT tank fill valve (Schrader)")
        else:
            xo = -P.FRAME_X - 0.5
            vb = cyl(11.0, rear + 10.2 - (xo - 6), (rear + 10.2, yb, mz), (-1, 0, 0)).cut(
                cyl(6.86, 10.2, (rear + 10.3, yb, mz), (-1, 0, 0)))
            add(name, vb.fuse(box(xo - 6, xo - 2, yb - 3, yb + 3, mz, mz + 45)), "brass", "pneu",
                bom="1/4 FNPT mini ball valve (manual bleed)", note="lever outside the rear panel")
    # fill valve + fill cross (150 psi zone) beside the pivot: transducer up, relief down, two outlets through
    # inline check valves to the barrels (one per barrel, so one shot can't vent the other chamber)
    fx, fy, fz = FILL
    sx1 = fx - 12.7 - 1.8
    add("Fill solenoid", box(sx1 - 37.0, sx1, fy - 14, fy + 14, fz - 22, fz + 16).fuse(
        cyl(15.0, 38.0, (sx1 - 18.5, fy, fz - 22), (0, 0, -1))), "brass", "pneu",
        bom="2/2 NC 12 V solenoid valve, 1/4 NPT (fill / metering)", note="coil hangs down")
    add("Fill solenoid push-to-connect", cyl(7.5, 22.0, (sx1 - 37.0, fy, fz), (-1, 0, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    add("Fill cross", box(fx - 12.7, fx + 12.7, fy - 12.7, fy + 12.7, fz - 12.7, fz + 12.7), "brass", "pneu",
        bom="1/4 NPT brass cross (4-way)", note="with a close nipple from the solenoid and a plug on the far end")
    add("Fill transducer 0-200 psi", cyl(10.0, 55.0, (fx, fy, fz + 12.7), (0, 0, 1)), "steel", "pneu",
        bom="Pressure transducer 0-200 psi, 0.5-4.5 V, 1/8 NPT")
    add("Fill relief valve 150 psi", cyl(9.5, 44.0, (fx, fy, fz - 12.7), (0, 0, -1)), "brass", "pneu",
        bom="Relief valve 150 psi 1/4 NPT, pull ring (CAS250150)")
    CHECKS.clear()
    for sgn, tag in ((-1, "A (top barrel)"), (1, "B (bottom barrel)")):
        y0 = fy + sgn * 12.7
        add(f"Fill push-to-connect {tag}", cyl(7.5, 18.0, (fx, y0, fz), (0, sgn, 0)), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
        if sgn < 0:                                 # A runs in along -y beside the pivot
            a0, d = V(fx, y0 - 22.0, fz), V(0, -1, 0)
        else:                                       # B turns back along -x
            a0, d = V(fx - 8.0, y0 + 26.0, fz), V(-1, 0, 0)
        cart = cyl(11.0, 54.0, (a0 + d * 15.0).toTuple(), d.toTuple()).fuse(
            cyl(7.5, 84.0, a0.toTuple(), d.toTuple()))
        add(f"Check valve inline {tag}", cart, "brass", "pneu",
            bom="Brass check valve 1/4 FNPT (Midland 46510) + 2 straight push-to-connect", note="inline in the tube")
        CHECKS.append(a0 + d * 88.0)
    add("Tube fill A stub", tube_path([(fx, fy - 30.7, fz), (fx, fy - 35.0, fz)]), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)")
    add("Tube fill B stub", tube_path([(fx, fy + 30.7, fz), (fx, fy + 36.0, fz), (fx - 8.0, fy + 38.7, fz)]), "tube", "pneu",
        bom="DOT nylon tube 1/4 OD (ft)")
    # tubes
    tl = [(xb0 - 16.0, ty, zp - 6), (xb0 - 30.0, 120.0, 262.0), (-200.0, 120.0, 262.0), (-300.0, my + 45.0, 290.0),
          (mx + 12.7 + 18.0, my + 45.0, mz)]
    add("Tube tank left", tube_path(tl), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")
    tr = [(rx, ry + R + 14, zr + 16), (rx, ry + R + 14, 470.0), (mx, my - 45.0, 470.0), (mx, my - 45.0, top + 18.0)]
    add("Tube tank rear", tube_path(tr), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")
    tf = [(mx + 12.7 + 18.0, my, mz), (-300.0, fy, 318.0), (sx1 - 37.0 - 22.0, fy, fz)]
    add("Tube to fill valve", tube_path(tf), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")


# ------------------------------------------------------------------ power + controls
def batteries_and_electronics():
    L, W, H = P.BATT
    # sled rails over the rear-right wheel; the sled slides out the right side through the battery door
    for xr in (-360.0, -255.0):
        post(f"Sled post {xr:.0f} (1x1)", xr, -IY, P.RAIL_Z[1], P.RAIL_Z[1] + 104.0)
        tube_part(f"Sled rail {xr:.0f} (1x1)", "y", -72.0, -270.0, xr, P.RAIL_Z[1] + 104.0 + 12.7)
    zs = P.RAIL_Z[1] + 129.4
    sled = box(-387.0, -227.0, -256.0, -68.0, zs, P.BATT_Z)
    for (x0, x1, y0, y1) in ((-387.0, -385.2, -256.0, -68.0), (-228.8, -227.0, -256.0, -68.0), (-387.0, -227.0, -70.0, -68.0)):
        sled = sled.fuse(box(x0, x1, y0, y1, P.BATT_Z, P.BATT_Z + 25.0))
    sled = sled.fuse(box(-340.0, -275.0, -266.0, -256.0, zs, zs + 14.0))
    add("Battery sled", sled, "print", "power", bom="Battery sled (pull handle out the battery door)", kind="print")
    xs = (P.BATT_X[0], P.BATT_X[0] + W, P.BATT_X[0] + W + 3.0, P.BATT_X[0] + 2 * W + 3.0)
    for i, (x0, x1) in enumerate(((xs[0], xs[1]), (xs[2], xs[3]))):
        b = box(x0, x1, P.BATT_Y[0], P.BATT_Y[1], P.BATT_Z, P.BATT_Z + H - 12)
        for dy in (25.0, L - 25.0):
            b = b.fuse(box(x0 + 25, x0 + 45, P.BATT_Y[0] + dy - 8, P.BATT_Y[0] + dy + 8, P.BATT_Z + H - 12, P.BATT_Z + H))
        add(f"FRC battery {i + 1}", b, "battery", "power", bom="FRC 12 V 18 Ah battery (owned, MK ES17-12)")
    for i, (y0, y1) in enumerate(((-245.0, -220.0), (-212.0, -187.0))):
        add(f"Anderson SB50 {i + 1}", box(-226.0, -206.0, y0, y1, 300.0, 325.0), "red", "power",
            bom="Anderson SB50 pair + 6 AWG contacts (stash)")
    # middle bay: PDH and breaker on the bellypan, controls on a printed shelf under the elevation motor
    zb = P.BELLY_Z
    add("Power distribution (REV PDH)", box(-20.0, 83.0, -86.5, 86.5, zb, zb + 36), "black", "power",
        bom="REV PDH (owned) + ATO breakers / fuses (stash)")
    add("Main breaker 120 A", box(-60.0, -23.0, -20.0, 20.0, zb, zb + 40), "black", "power", bom="120 A main breaker (stash)")
    shelf = box(-80.0, 80.0, -120.0, 120.0, 160.0, 164.0)
    for (x, y) in ((-75, -115), (-75, 115), (75, -115), (75, 115)):
        shelf = shelf.fuse(box(x - 5, x + 5, y - 5, y + 5, zb, 160.0))
    add("Electronics shelf", shelf, "print", "power", bom="Electronics shelf", kind="print")
    z = 164.0
    boards = [("STM32 Nucleo-F446RE (main controller)", -78, -8, 20, 102, 20, "pcb", "STM32 Nucleo-64 NUCLEO-F446RE"),
              ("ESP32-S3 WiFi bridge", 2, 71, 72, 100, 15, "pcb", "ESP32-S3-DevKitC-1 N8R8"),
              ("ESP32-S3 safety node", 2, 71, 36, 64, 15, "pcb", "ESP32-S3-DevKitC-1 N8R8"),
              ("PWM gate (74AHCT125)", 2, 52, 4, 30, 12, "pcb", "SN74AHCT125N quad buffer + perfboard"),
              ("Valve driver 4-ch", -78, -3, -62, -4, 18, "pcb", "4-ch 12 V relay module, opto inputs (2 dumps + fill)"),
              ("Buck 12-5 V 20 A", 6, 62, -62, -6, 25, "black", "12->5 V 20 A buck (B089M5R3NJ)"),
              ("Safety relay 40 A", 20, 50, -100, -70, 32, "black", "12 V 40 A SPDT relay + socket"),
              ("Spark MAX (elevation)", -78, -8, -118, -82, 25, "black", "REV Spark MAX (owned)")]
    for name, x0, x1, y0, y1, h, col, bom in boards:
        add(name, box(x0, x1, y0, y1, z, z + h), col, "power", bom=bom)
    # E-stop and USB-C on the rear face, upper left
    xo = -P.FRAME_X + P.CLIP_T
    ey, ez = ESTOP
    est = cyl(11.0, 12.0, (xo + 6.0, ey, ez), (-1, 0, 0)).fuse(
        cyl(20.0, 30.0, (xo + 34.0, ey, ez), (-1, 0, 0))).fuse(
        cq.Solid.makeSphere(22.0, V(xo - 2.0, ey, ez), angleDegrees1=0, angleDegrees2=90).rotate(
            V(xo - 2.0, ey, ez), V(xo - 2.0, ey + 1, ez), -90))
    add("E-stop", est, "red", "power", bom="Latching mushroom E-stop, 22 mm, NC", note="rear face; in series with the safety relay coil")
    add("USB-C panel pass-through", cyl(8.5, 28.0, (xo - 2.0, USB[0], USB[1]), (1, 0, 0)), "black", "power",
        bom="Panel-mount USB-C extension (to the STM32)")


ESTOP = (200.0, 455.0)     # (y, z) on the rear face
USB = (110.0, 455.0)


def compressor_spot():
    (x0, x1), (y0, y1), (z0, z1) = P.COMP_SPOT
    add("Compressor spot (ZHSYMX SQ420, later)", box(x0, x1, y0, y1, z0 + 6.0, z1 + 6.0), "spot", "spot", bom="(spot only)",
        note="243 x 128 x 181 mm pump lying flat in the front bay; not bought")
    add("Compressor mount plate", box(x0 - 2, x1 + 2, y0 - 2, y1 + 2, z0, z0 + 6.0), "print", "spot",
        bom="(with the pump) Compressor mount plate", kind="print", note="bolts through the bellypan; add with the pump")


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


REAR_HOLES = ((REAR_MAN[1] - 30.0, REAR_MAN[2], 8.0), (REAR_MAN[1] + 30.0, REAR_MAN[2], 13.0), (USB[0], USB[1], 9.0),
              (ESTOP[0], ESTOP[1], 11.5))


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
        if p["n"].x < -0.99:                     # rear face: fill port, bleed lever, USB-C, E-stop
            for (yb, zb, r) in REAR_HOLES:
                a = a.cut(cyl(r, 30, (-P.FRAME_X - 10, yb, zb), (1, 0, 0)))
        u, w = B._plane_basis(p["n"])
        us = [V(*q).dot(u) for q in p["poly"]]
        ws = [V(*q).dot(w) for q in p["poly"]]
        dims = sorted([max(us) - min(us), max(ws) - min(ws)])
        door = p["n"].y < -0.9 and max(q[0] for q in p["poly"]) < P.SIDE_SPLIT_X + 1
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
