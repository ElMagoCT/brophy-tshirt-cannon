"""Everything else: towers and pivot bearings, the elevation servos and belt, tanks and the rear air
manifold, batteries, electronics, the compressor spot, FRC-style bumpers, wall standoffs, the acrylic
panels, the denim/aramid liner sheets and the printed body-frame pieces."""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
import body as B
from lib import add, box, cyl, tube, hex_prism, union
from drive import extrusion, ext, fr8, _hull, bearing_seat

IN = P.IN


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


def towers_and_pivot():
    x0, x1 = P.TOWER_XS
    for sgn, side in ((1, "L"), (-1, "R")):
        yc = sgn * (P.OUTER_RAIL_Y[0] + P.OUTER_RAIL_Y[1]) / 2
        ext(f"Turret tower {side} (1x1)", "z", P.RAIL_Z[1], 700.0, (x0 + x1) / 2, yc, (1, 1))
        for xf, d in ((x0, -1), (x1, 1)):
            leg_v = box(min(xf, xf + d * P.PLATE_T), max(xf, xf + d * P.PLATE_T), yc - 12.7, yc + 12.7,
                        P.RAIL_Z[1], P.RAIL_Z[1] + 60)
            leg_h = box(min(xf, xf + d * 45), max(xf, xf + d * 45), yc - 12.7, yc + 12.7,
                        P.RAIL_Z[1], P.RAIL_Z[1] + P.PLATE_T)
            add(f"Tower base angle {side} {'front' if d < 0 else 'back'}", leg_v.fuse(leg_h), "alu", "frame",
                bom="Tower base angle (1/8 Al, bent)", kind="stock")
        # bearing block on the tower's front face, two flanged 1/2 hex bearings
        y0, y1 = P.BEARING_BLOCK_Y
        blk = box(x1, P.PIVOT[0] + 28, min(sgn * y0, sgn * y1), max(sgn * y0, sgn * y1), P.PIVOT[1] - 28, P.PIVOT[1] + 28)
        blk = blk.cut(cyl(9.0, 800, (P.PIVOT[0], -400, P.PIVOT[1]), (0, 1, 0)))
        blk = blk.cut(bearing_seat(P.PIVOT[0], sgn * y0, P.PIVOT[1], sgn, 7.94))
        blk = blk.cut(bearing_seat(P.PIVOT[0], sgn * y1, P.PIVOT[1], -sgn, 7.94))
        add(f"Pivot bearing block {side}", blk, "print_d", "frame", bom="Pivot bearing block", kind="print",
            note="PA-CF, 2 x 1/4-20 into the tower")
        for yb, d in ((y0, sgn), (y1, -sgn)):
            add(f"Pivot bearing {side} {yb:.0f}", fr8(P.PIVOT[0], sgn * yb, P.PIVOT[1], d, hexbore=True), "steel", "frame",
                bom="Flanged bearing 1/2 hex bore (WCP)")
    # elevation servos (right side, y<0) driving the 56T pulley with a 9 mm belt
    ya, yb_ = P.ELEV_PULLEY_Y
    for i, (sx, sz) in enumerate(P.SERVO_PINIONS):
        body = box(sx - 17.5, sx + 17.5, -(yb_ + 0.5 + 24.7), -(yb_ + 0.5), sz - 12.0, sz + 33.2)
        add(f"Servo STS3215 {i + 1}", body, "black", "frame", bom="FEETECH STS3215 12 V servo (2-pack)")
        pin = cyl(12.7 + 2.0, 13.0, (sx, -(yb_), sz), (0, 1, 0)).cut(cyl(3.0, 15, (sx, -(yb_ + 1), sz), (0, 1, 0)))
        add(f"Servo pinion 16T {i + 1}", pin, "print_d", "frame", bom="Servo pinion 16T HTD 9 mm", kind="print")
    shelf = box(P.SERVO_PINIONS[0][0] - 25, P.SERVO_PINIONS[1][0] + 25, -P.OUTER_RAIL_Y[0], -(yb_ + 0.5),
                P.SERVO_PINIONS[0][1] - 26.0, P.SERVO_PINIONS[0][1] - 12.0)
    tab = box(P.TOWER_XS[0] - 2, P.TOWER_XS[1] + 2, -P.OUTER_RAIL_Y[0] + 0.0, -(yb_ + 0.5),
              P.SERVO_PINIONS[0][1] - 26.0, P.SERVO_PINIONS[0][1] + 40.0)
    add("Servo bracket", shelf.fuse(tab), "print", "frame", bom="Servo bracket", kind="print")
    # belt round the pulley and both pinions
    circles = [(P.PIVOT[0], P.PIVOT[1], P.pd(56) / 2)] + [(x, z, P.pd(16) / 2) for x, z in P.SERVO_PINIONS]
    pts = []
    for (x, z, r) in circles:
        for k in range(72):
            a = 2 * math.pi * k / 72
            pts.append((x + r * math.cos(a), z + r * math.sin(a)))
    hull = _hull(pts)
    per = sum(math.hypot(hull[i][0] - hull[i - 1][0], hull[i][1] - hull[i - 1][1]) for i in range(len(hull)))
    w = cq.Workplane("XZ", origin=(0, -(ya + 2.0), 0)).polyline(hull).close().wires().val()
    face = cq.Face.makeFromWires(w.offset2D(0.9, "arc")[0], [w.offset2D(-0.9, "arc")[0]])
    belt = cq.Solid.extrudeLinear(face, V(0, -9.0, 0))
    add("Elevation belt", belt, "belt", "frame", bom=f"HTD 5M 9 mm belt, {5 * round(per / 5 / 5)}T", note=f"{per:.0f} mm pitch length")
    return per


def rear_air():
    """Two 1.6 gal / 200 psi tanks stacked across the rear, printed cradles, rear manifold."""
    x0, x1 = -384.7, -217.3
    for sgn, side in ((1, "L"), (-1, "R")):
        yc = sgn * (P.INNER_RAIL_Y[0] + P.INNER_RAIL_Y[1]) / 2
        for xp in (-230.0, -372.0):                    # rear post clear of the rear wall frame
            ext(f"Tank rack post {side} {xp:.0f} (1x1)", "z", P.RAIL_Z[1], 307.3, xp, yc, (1, 1))
        ext(f"Tank rack rail {side} (1x1)", "x", x0, x1, yc, 320.0, (1, 1))
    tanks = []
    for i, zc in enumerate(P.TANK_Z):
        L, R = P.TANK_L, P.TANK_D / 2
        shell = cq.Workplane("XZ", origin=(0, L / 2, 0)).center(P.TANK_X, zc).circle(R).extrude(L).edges().fillet(30.0).val()
        for yb in (-80.0, 0.0, 80.0):
            shell = shell.fuse(cyl(9.0, 12.0, (P.TANK_X - R + 4, yb, zc), (-1, 0, 0)))
        add(f"Air tank {'lower' if i == 0 else 'upper'} (1.6 gal 200 psi)", shell, "tank", "pneu",
            bom="Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT (owner's AliExpress pick)")
        tanks.append((zc, R))
        x_port = P.TANK_X - R - 8                      # face of the tank's 1/4 NPT bosses
        y_ptc = -80.0 if i == 0 else 80.0              # lower tank feeds from -y, upper from +y
        elbow = cyl(7.5, 14.0, (x_port, y_ptc, zc), (-1, 0, 0)).fuse(
            cyl(7.0, 16.0, (x_port - 8.0, y_ptc, zc), (0, 0, -1)))
        add(f"Tank elbow push-to-connect {i}", elbow, "brass", "pneu",
            bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT")
        add(f"Tank drain plug {i}", cyl(9.0, 12.0, (x_port, 0, zc), (-1, 0, 0)), "brass", "pneu",
            bom="1/4 NPT brass plug")
        add(f"Tank spare-port plug {i}", cyl(9.0, 12.0, (x_port, -y_ptc, zc), (-1, 0, 0)), "brass", "pneu",
            bom="1/4 NPT brass plug", note="the upper tank's spare port is the future pump inlet" if i else "")
        for yb in (-140.0, 140.0):                     # clear of the cradles and the tank ports
            strap = tube(R + 2.5, R + 0.5, 25.0, (P.TANK_X, yb - 12.5, zc), (0, 1, 0))
            add(f"Tank strap {i} {yb:.0f}", strap, "black", "pneu", bom="1 in ratchet / cam strap")
    # cradles: two printed ladders on the rack rails holding both tanks at fixed spacing
    for sgn, side in ((1, "L"), (-1, "R")):
        yc = sgn * 108.75
        cr = box(P.TANK_X - P.TANK_D / 2 - 12, P.TANK_X + P.TANK_D / 2 + 12, yc - 14, yc + 14, 332.7, P.TANK_Z[1] + 40)
        for zc, R in tanks:                            # each tank sits in a ring, 1 mm clearance
            cr = cr.cut(cyl(R + 1.0, 60, (P.TANK_X, yc - 30, zc), (0, 1, 0)))
        for z0, z1, tag in ((332.7, 502.0, "lower"), (502.0, P.TANK_Z[1] + 40, "upper")):
            add(f"Tank cradle {side} {tag}", cr.intersect(box(-1000, 1000, -1000, 1000, z0, z1)), "print", "pneu",
                bom="Tank cradle half", kind="print")
    # rear manifold low behind the tanks. Top: two tank tubes, transducer, 200 psi relief. Rear face:
    # gauge, fill port, bleed (through the rear panel). Front face: the Aignep fill solenoid.
    mx, mz = -372.0, 300.0
    add("Rear manifold block", box(mx - 12.7, mx + 12.7, -63.5, 63.5, mz - 12.7, mz + 12.7), "brass", "pneu",
        bom="1/4 NPT brass manifold, 1 in x 5 in, 8-port")
    rear = -P.FRAME_X + P.LIP + P.ACRYLIC_T
    items = [
        ("Tank gauge 0-300 psi", -45.0, "gauge"), ("Fill port (Schrader)", 0.0, "fill"),
        ("Bleed ball valve (rear)", 45.0, "bleed")]
    for name, yb, kind in items:
        add(f"{name} nipple", cyl(6.86, mx - 12.7 - rear + 2, (mx - 12.7 + 2, yb, mz), (-1, 0, 0)), "brass", "pneu",
            bom="1/4 NPT brass nipple x 1-1/2 in")
        if kind == "gauge":
            add(name, cyl(26.0, 14.0, (rear - 0.0, yb, mz), (-1, 0, 0)), "steel", "pneu",
                bom="Gauge 0-300 psi 2 in, 1/4 NPT back mount (ECO-B300)")
        elif kind == "fill":
            add(name, cyl(6.0, 22.0, (rear, yb, mz), (-1, 0, 0)), "brass", "pneu",
                bom="1/4 MNPT tank fill valve (Milton S-684-4W)")
        else:
            xo = rear - P.ACRYLIC_T - 0.5                # just outside the rear panel
            vb = cyl(11.0, rear + 10.2 - (xo - 6), (rear + 10.2, yb, mz), (-1, 0, 0)).cut(
                cyl(6.86, 10.2, (rear + 10.3, yb, mz), (-1, 0, 0)))
            add(name, vb.fuse(box(xo - 6, xo - 2, yb - 3, yb + 3, mz, mz + 45)),
                "brass", "pneu", bom="1/4 FNPT mini ball valve (manual bleed)", note="lever outside the rear panel")
    top = mz + 12.7
    add("Tank relief valve 200 psi", cyl(9.5, 44.0, (mx, 15.0, top), (0, 0, 1)), "brass", "pneu",
        bom="Relief valve 200 psi 1/4 NPT (CAS250200)")
    add("Tank transducer 0-300 psi", cyl(10.0, 55.0, (mx, -15.0, top), (0, 0, 1)), "steel", "pneu",
        bom="Pressure transducer 0-300 psi 1/8 NPT (autopro)")
    for yb in (-45.0, 45.0):
        add(f"Rear manifold push-to-connect {yb:.0f}", cyl(7.5, 18.0, (mx, yb, top), (0, 0, 1)), "brass", "pneu",
            bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    add("Fill solenoid Aignep 02F", box(mx + 12.7, mx + 50, -14, 14, mz - 22, mz + 16).fuse(
        cyl(15.0, 40.0, (mx + 31, 0, mz - 22), (0, 0, -1))), "brass", "pneu",
        bom="Aignep 02F 2/2 NC direct-acting 12 V, 1/4 NPTF (fill / metering)", note="coil hangs down, clear of the tank")
    add("Fill solenoid push-to-connect", cyl(7.5, 26.0, (mx + 50, 0, mz), (1, 0, 0)), "brass", "pneu",
        bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    xe = P.TANK_X - P.TANK_D / 2 - 16.0                # elbow outlet x
    lo, up = tanks[0][0], tanks[1][0]
    runs = {
        0: [(xe, -80.0, lo - 16), (xe, -80.0, top + 45), (mx, -45.0, top + 45), (mx, -45.0, top + 18)],
        1: [(xe, 80.0, up - 16), (xe, 80.0, lo + 30), (mx - 9.0, 80.0, lo + 20), (mx - 9.0, 80.0, top + 45),
            (mx, 45.0, top + 45), (mx, 45.0, top + 18)],
    }
    for i, pts in runs.items():
        add(f"Tube tank {i}", tube_path(pts), "tube", "pneu", bom="DOT nylon tube 1/4 OD (ft)", note="SAE J844")
    return (mx + 76.0, 0.0, mz)


def batteries_and_electronics():
    L, W, H = P.BATT
    for sgn, tag in ((1, "left"), (-1, "right")):
        y0 = sgn * 3.0
        b = box(-L / 2, L / 2, min(y0, y0 + sgn * W), max(y0, y0 + sgn * W), P.BELLY_Z, P.BELLY_Z + H - 12)
        for dx in (-L / 2 + 25, L / 2 - 25):
            b = b.fuse(box(dx - 8, dx + 8, min(y0, y0 + sgn * W) + 25, min(y0, y0 + sgn * W) + 45,
                           P.BELLY_Z + H - 12, P.BELLY_Z + H))
        add(f"FRC battery {tag}", b, "battery", "power", bom="FRC 12 V 18 Ah battery (owned, MK ES17-12)")
    cr = box(-L / 2 - 8, L / 2 + 8, -W - 11, W + 11, P.BELLY_Z, P.BELLY_Z + 70)
    cr = cr.cut(box(-L / 2 - 0.5, L / 2 + 0.5, -W - 3.5, W + 3.5, P.BELLY_Z - 1, P.BELLY_Z + 80))
    for dx in (-50, 50):
        cr = cr.cut(box(dx - 14, dx + 14, -W - 20, W + 20, P.BELLY_Z + 30, P.BELLY_Z + 34))
    for x0, x1, tag in ((-L / 2 - 8, 0, "rear"), (0, L / 2 + 8, "front")):
        add(f"Battery cradle {tag}", cr.intersect(box(x0, x1, -200, 200, 0, 500)), "print", "power",
            bom="Battery cradle half (two batteries side by side)", kind="print")
    for i, yb in enumerate((-40.0, 40.0)):
        add(f"Anderson SB50 {i + 1}", box(136, 166, yb - 11, yb + 11, P.BELLY_Z, P.BELLY_Z + 25), "red", "power",
            bom="Anderson SB50 pair + 6 AWG contacts (WCP-2533/2534)")
    ex0 = 266.0
    add("Power distribution (REV PDH)", box(ex0, ex0 + 102, -78.5, 78.5, P.BELLY_Z, P.BELLY_Z + 36), "black",
        "power", bom="Power distribution: REV PDH or CTRE PDP (stash)")
    add("Main breaker 120 A", box(225, 262, -20, 20, P.BELLY_Z, P.BELLY_Z + 40), "black", "power",
        bom="120 A main breaker (stash)")
    shelf = box(222, 378, -90, 90, 178.0, 183.0)
    for (x0, y0, x1, y1) in ((222, -90, 232, -80), (368, -90, 378, -80), (222, 80, 232, 90), (368, 80, 378, 90)):
        shelf = shelf.fuse(box(x0, x1, y0, y1, P.BELLY_Z + 36, 178.0))
    add("Electronics shelf", shelf, "print", "power", bom="Electronics shelf", kind="print")
    boards = [("ESP32-S3 DevKitC-1", 240, 309, -70, -42, 15, "pcb", "ESP32-S3-DevKitC-1 N8R8 (+1 spare)"),
              ("Relay module 4-ch", 240, 315, -30, 25, 18, "pcb", "4-ch 12 V relay module, opto inputs"),
              ("Buck 12-5 V 20 A", 320, 372, -70, -14, 25, "black", "12->5 V 20 A buck (B089M5R3NJ)"),
              ("Bus servo adapter", 320, 355, 0, 25, 10, "pcb", "Waveshare Bus Servo Adapter (A)"),
              ("ADS1115", 345, 373, 40, 58, 6, "pcb", "ADS1115 16-bit ADC (Adafruit 1085)"),
              ("Fuse block 6-way", 240, 340, 35, 85, 30, "black", "6-way blade fuse block + fuses")]
    for name, x0, x1, y0, y1, h, col, bom in boards:
        add(name, box(x0, x1, y0, y1, 183.0, 183.0 + h), col, "power", bom=bom)
    # E-stop on the rear face, upper right; USB-C pass-through on the rear face
    xo = -P.FRAME_X + P.LIP                          # outer face of the rear panel
    est = cyl(11.0, 12.0, (xo + 6.0, ESTOP[0], ESTOP[1]), (-1, 0, 0)).fuse(
        cyl(20.0, 30.0, (xo + 34.0, ESTOP[0], ESTOP[1]), (-1, 0, 0))).fuse(
        cq.Solid.makeSphere(22.0, V(xo - 2.0, ESTOP[0], ESTOP[1]), angleDegrees1=0, angleDegrees2=90).rotate(
            V(xo - 2.0, ESTOP[0], ESTOP[1]), V(xo - 2.0, ESTOP[0] + 1, ESTOP[1]), -90))
    add("E-stop", est, "red", "power", bom="Latching mushroom E-stop, 22 mm, NC (Friday Parts)",
        note="rear face, upper right")
    add("USB-C panel pass-through", cyl(8.5, 28.0, (xo - 2.0, USB[0], USB[1]), (1, 0, 0)), "black", "power",
        bom="Panel-mount USB-C extension (Parts Express 130-033)")


ESTOP = (-150.0, 600.0)     # (y, z) on the rear face
USB = (130.0, 402.0)


def compressor_spot():
    (x0, x1), (y0, y1), (z0, z1) = P.COMP_SPOT
    add("Compressor spot (ZHSYMX SQ420, later)", box(x0, x1, y0, y1, z0, z1), "spot", "spot", bom="(spot only)",
        note="243 x 128 x 181 mm pump standing up; not bought")
    plate = box(x0 - 2, x1 + 2, y0 - 2, y1 + 2, z0 - 6, z0)
    add("Compressor mount plate", plate, "print", "spot", bom="(with the pump) Compressor mount plate", kind="print",
        note="sits on two 1x1 posts from the outer rail; add with the pump")


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
            if sgm["axis"] == "x":                    # side backings: pockets for the axle bolt heads
                for sx in (-1, 1):
                    piece = piece.cut(cyl(14.0, 40, (sx * P.AX_X, sgm["pos"] - 20 * oy, P.AXLE_Z), (0, oy, 0)))
            add(f"Bumper backing {name} {k + 1}", piece, "print", "bumper", bom="Bumper backing segment", kind="print",
                note="bolts to the rail with 1/4-20 + T-nuts")
        for i, zc in enumerate((zb0 + r, zb0 + 3 * r)):
            if sgm["axis"] == "y":
                c = sgm["pos"] + ox * (t + r)
                nd = _mitre(cyl(r, a1 - a0, (c, a0, zc), (0, 1, 0)), sgm, yo, xf, reach)
            else:
                c = sgm["pos"] + oy * (t + r)
                nd = cyl(r, a1 - a0, (a0, c, zc), (1, 0, 0))
                nd = _mitre(nd, sgm, yo, xf, reach)
            nd = nd.cut(cyl(12.7, 3000, (c if sgm["axis"] == "y" else -1500, -1500 if sgm["axis"] == "y" else c, zc),
                            (0, 1, 0) if sgm["axis"] == "y" else (1, 0, 0)))
            add(f"Pool noodle {name} {i + 1}", nd, "foam", "bumper", bom="Pool noodle 2.5 in (white)", kind="stock")
        # fabric cover: a thin wrap round both noodles
        if sgm["axis"] == "y":
            c0, c1 = sorted([sgm["pos"] + ox * t, sgm["pos"] + ox * (t + 2 * r + 1.5)])
            outer = box(c0, c1, -(yo + reach) + 1, yo + reach - 1, zb0 - 1, zb1 + 1)
            inner = box(c0 + (0 if ox > 0 else 1.5), c1 - (1.5 if ox > 0 else 0), -(yo + reach), yo + reach, zb0, zb1)
        else:
            c0, c1 = sorted([sgm["pos"] + oy * t, sgm["pos"] + oy * (t + 2 * r + 1.5)])
            outer = box(-(xf + reach) + 1, xf + reach - 1, c0, c1, zb0 - 1, zb1 + 1)
            inner = box(-(xf + reach), xf + reach, c0 + (0 if oy > 0 else 1.5), c1 - (1.5 if oy > 0 else 0), zb0, zb1)
        cover = _mitre(outer.cut(inner), sgm, yo, xf, reach)
        add(f"Bumper cover {name}", cover, "foam", "bumper", bom="Bumper fabric cover (white canvas, owner's pick)",
            kind="stock")


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
            n = V(sy, -sx, 0).normalized()          # normal of the corner diagonal
            ox, oy = sgm["out"]
            mid = V(sgm["pos"] + ox * reach / 2, 0, 0) if sgm["axis"] == "y" else V(0, sgm["pos"] + oy * reach / 2, 0)
            m = n * -1 if n.dot(mid - c) > 0 else n  # remove the half-plane away from this run's middle
            pts = [c + d * big, c - d * big, c - d * big + m * big, c + d * big + m * big]
            half = cq.Workplane("XY", origin=(0, 0, -100)).polyline([(p.x, p.y) for p in pts]).close().extrude(800).val()
            out = out.cut(half)
    return out


def wall_standoffs():
    """Printed posts on the outer rails; the side-wall frame bolts to their outer face (2 x M4, heat-set)."""
    for sgn, side in ((1, "L"), (-1, "R")):
        y_in, y_out = P.OUTER_RAIL_Y
        for x in (-330.0, -150.0, 180.0, 340.0):
            v = box(x - 15, x + 15, min(sgn * y_in, sgn * y_out), max(sgn * y_in, sgn * y_out), P.RAIL_Z[1],
                    P.Z_WALL_BOT + 12.0)
            add(f"Wall standoff {side} {x:.0f}", v, "print", "body", bom="Wall standoff", kind="print",
                note="1/4-20 into the rail, 2 x M4 sideways into the wall frame")


REAR_HOLES = ((-45.0, 300.0, 27.0), (0.0, 300.0, 8.0), (45.0, 300.0, 13.0), (USB[0], USB[1], 9.0),
              (ESTOP[0], ESTOP[1], 11.5))


def body_parts(log=print):
    body, frame, panels = B.build(log=log)
    pieces, edges = B.section(frame, panels, log=log)
    B.add_joints(pieces, panels, log=log)
    slivers = 0
    for p in pieces:
        sol = sorted(p["shape"].Solids(), key=lambda x: -x.Volume())
        keep = [x for x in sol if x.Volume() > 0.03 * sol[0].Volume()]
        slivers += len(sol) - len(keep)                # thin strips left where two grooves meet
        p["shape"] = keep[0] if len(keep) == 1 else cq.Compound.makeCompound(keep)
        add(f"Body frame {p['name']}", p["shape"], "print", "body", bom=f"Body frame piece {p['name']}", kind="print",
            note="PETG/ASA, 4 walls, 25% gyroid")
    liner_ok = 0
    for i, p in enumerate(panels):
        a = B.slab(p["poly"], p["n"], P.MEM_W - P.GROOVE_D + 0.4, P.LIP + 0.2, P.ACRYLIC_T)
        if p["n"].x < -0.99:                     # rear face: gauge, fill port, bleed lever, USB-C
            for (yb, zb, r) in REAR_HOLES:
                a = a.cut(cyl(r, 30, (-P.FRAME_X - 10, yb, zb), (1, 0, 0)))
        u, w = B._plane_basis(p["n"])
        us = [V(*q).dot(u) for q in p["poly"]]
        ws = [V(*q).dot(w) for q in p["poly"]]
        dims = sorted([max(us) - min(us), max(ws) - min(ws)])
        add(f"Panel {i:02d}", a, "acrylic", "body", bom="Frosted acrylic panel 1/8 in (owned)", kind="acrylic",
            note=f"{dims[1] / IN:.1f} x {dims[0] / IN:.1f} in outline")
        front = min(v[0] for v in p["poly"]) > 300
        floor = p["n"].z > 0.99 and abs(max(v[2] for v in p["poly"]) - P.Z_SLOT_FLOOR) < 1
        if not front and not floor:
            ln = B.slab(p["poly"], p["n"], P.MEM_W - 4.0, P.MEM_H + 0.3, 1.0)
            for sg in (-1, 1):                    # turret towers stand against the side walls
                yo = P.OUTER_RAIL_Y
                ln = ln.cut(box(P.TOWER_XS[0] - 1, P.TOWER_XS[1] + 1, min(sg * (yo[0] - 1), sg * (yo[1] + 2)),
                                max(sg * (yo[0] - 1), sg * (yo[1] + 2)), P.RAIL_Z[1], 701))
            if p["n"].x < -0.99:
                for (yb, zb, r) in REAR_HOLES:
                    ln = ln.cut(cyl(max(r, 22.0) if (yb, zb) == ESTOP else r, 60, (-P.FRAME_X - 10, yb, zb), (1, 0, 0)))
            add(f"Liner {i:02d}", ln, "fabric", "body", bom="Liner sheet (denim / 1050D nylon / aramid)", kind="fabric",
                note="clamped to the frame's inner face with printed clips")
            liner_ok += 1
    log(f"body: {len(pieces)} frame pieces ({slivers} groove slivers dropped), {len(panels)} panels, {liner_ok} liners")
    return panels
