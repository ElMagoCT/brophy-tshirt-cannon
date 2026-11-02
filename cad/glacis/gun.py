"""The elevating gun: three stacked barrels, each with a Humphrey QE5 3/4 in NPT quick exhaust valve.

Gun-local frame (built at 0 deg, moved by robot.pose_gun): origin on the pivot axis, +X along the
barrels, +Z up, Y as the robot. QE5 ports: inlet and exhaust on one axis (inlet at the back,
exhaust forward to the barrel), cylinder port on the side -> the steel chamber runs sideways.
Chambers alternate sides; the middle chamber lies on the pivot axis and doubles as the left (+y)
trunnion (a printed hub on its cap carries the left stub shaft). The right stub shaft passes
between the top and bottom chambers and carries the 56T elevation pulley.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, tube, hex_prism, union
from fittings import Chain, OD, ENG, va4_coil, relief_cap, ball_lever

IN = P.IN
QEV = dict(L=93.0, H=55.4, R=29.0, BOSS=46.0, BOSS_R=19.0)   # Humphrey QE5 (3.66 x 2.18 x 2.95 in)
CRADLE_T = P.PLATE_T
CRADLE_Y0 = 47.0                                             # inner faces of the two cradle plates
PARTS_LOCAL = []                                             # (shape) envelopes used to cut plate holes


def gadd(name, shape, color, group="gun", bom=None, kind="cots", note="", moving=True):
    PARTS_LOCAL.append(shape)
    return add(name, shape, color, "gun", bom=bom, kind=kind, moving=True, note=note)


def qev_body():
    body = cyl(QEV["R"], QEV["L"], (-QEV["L"] / 2, 0, 0), (1, 0, 0))
    body = body.intersect(box(-60, 60, -40, 40, -QEV["H"] / 2, QEV["H"] / 2))
    return body


def qev(h, side):
    b = qev_body()
    boss = cyl(QEV["BOSS_R"], QEV["BOSS"], (0, 0, 0), (0, side, 0))
    s = b.fuse(boss)
    for p, d in (((-QEV["L"] / 2, 0, 0), (1, 0, 0)), ((QEV["L"] / 2, 0, 0), (-1, 0, 0))):
        s = s.cut(cyl(OD["3/4"] / 2, ENG["3/4"], p, d))
    s = s.cut(cyl(OD["3/4"] / 2, ENG["3/4"], (0, side * QEV["BOSS"], 0), (0, -side, 0)))
    return s.translate(V(0, 0, h))


def adapter():
    """CNC breech adapter: 3/4 NPT female at the back, 3 in barrel socket at the front, clamp slot."""
    L, od = 64.0, 84.0
    s = cyl(od / 2, L, (0, 0, 0), (1, 0, 0))
    s = s.cut(cyl(OD["3/4"] / 2, ENG["3/4"] + 1, (-0.5, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(10.5, L, (0, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(P.BARREL_OD / 2 + 0.15, 40.0, (L - 40.0, 0, 0), (1, 0, 0)))
    s = s.cut(box(L - 30, L + 1, -1.5, 1.5, 0, od))                 # pinch slot
    s = s.cut(cyl(3.3, 30, (L - 15, -15, od / 2 - 8), (0, 1, 0)))    # M6 pinch screw
    return s


def build(log=print):
    PARTS_LOCAL.clear()
    n = P.N_BARRELS
    sides = [-1, 1, -1][:n]
    chamber_end, supply_tip = {}, {}
    for k in range(n):
        h = (k - (n - 1) / 2) * P.PITCH
        sd = sides[k]
        tag = ["bottom", "middle", "top"][k]
        gadd(f"QEV Humphrey QE5 {tag}", qev(h, sd), "alu", bom="Humphrey QE5 3/4 NPT quick exhaust valve")
        # barrel side: exhaust -> 3/4 close nipple -> CNC adapter -> barrel
        ch = Chain((QEV["L"] / 2, 0, h), (1, 0, 0), "F", gadd, f"{tag} ")
        ch.nipple("3/4")
        ax0 = ch.at(ch.s).x - ENG["3/4"]                        # adapter's female port takes the nipple
        gadd(f"Breech adapter {tag}", adapter().translate(V(ax0, 0, h)), "alu",
             bom="Breech adapter (CNC 6061, 3.5 in bar)", kind="machined")
        b0 = ax0 + 64.0 - 40.0
        barrel = tube(P.BARREL_OD / 2, P.BARREL_OD / 2 - P.BARREL_WALL, P.BARREL_LEN, (b0, 0, h), (1, 0, 0))
        gadd(f"Barrel {tag}", barrel, "alu", bom="Barrel 3 in OD x 0.0625 wall (WCP-1275, 2 per 47 in)",
             kind="stock")
        mz = cyl(43.0, 25.0, (b0 + P.BARREL_LEN - 25.0, 0, h), (1, 0, 0)).cut(
            cyl(P.BARREL_OD / 2 + 0.2, 30, (b0 + P.BARREL_LEN - 27.0, 0, h), (1, 0, 0)))
        mz = mz.cut(tube(41.0, 39.0, 6.0, (b0 + P.BARREL_LEN - 15.0, 0, h), (1, 0, 0)))  # LED groove
        gadd(f"Muzzle ring {tag}", mz, "print", bom="Muzzle ring (LED groove)", kind="print")
        # chamber side: cylinder port -> 3/4 close nipple -> 4 x 3/4 bushing -> 4 in coupling
        #               -> 4 in close nipple -> 4 in cap
        cc = Chain((0, sd * QEV["BOSS"], h), (0, sd, 0), "F", gadd, f"{tag} chamber ")
        cc.nipple("3/4")
        cc.bushing_rev("4", "3/4", 124.5, 16.0, color="steel", bom="4 x 3/4 NPT hex bushing (malleable)")
        cc.coupling("4", 99.0, 130.0, bom="4 in NPT coupling (Class 150 malleable)")
        cc.nipple("4", 73.0, bom="4 in Sch 40 close nipple (2-7/8 in)")
        cc.cap("4", 53.0, 128.0, bom="4 in NPT cap (Class 150 malleable)")
        chamber_end[k] = cc.at(cc.s)                            # world point at the cap's end
        # inlet side: 3/4 x 1/4 bushing -> 1/4 close nipple -> port block
        #   block rear: nipple -> tee (branch +side: 150 psi relief) -> nipple -> VA-4 dump -> muffler
        #   block -side: check valve + push-to-connect (supply)
        #   block +side: manual bleed ball valve + muffler
        ic = Chain((-QEV["L"] / 2, 0, h), (-1, 0, 0), "F", gadd, f"{tag} inlet ")
        ic.bushing("3/4", "1/4", 27.0, 10.0, color="brass", bom="3/4 x 1/4 NPT hex bushing (brass)")
        ic.nipple("1/4", color="brass")
        sup, bleed = ic.block(sides=((0, -sd, 0), (0, sd, 0)))
        ic.nipple("1/4", color="brass")
        relief = ic.tee("1/4", 28.0, 19.0, (0, sd, 0))
        relief.male_end("Relief valve 150 psi", 46.0, 19.0, extra=relief_cap,
                        bom="Relief valve 150 psi 1/4 NPT (CAS250150)")
        ic.nipple("1/4", color="brass")
        ic.ff("Dump valve VA-4", 38.0, 25.0, extra=va4_coil, bom="HornBlasters VA-4 12 V 1/4 NPT valve (dump)")
        ic.male_end("Muffler 1/4", 22.0, 16.0, color="brass", bom="1/4 NPT sintered muffler (compact)")
        sup.nipple("1/4", color="brass")
        sup.ff("Check valve", 54.0, 22.0, bom="Midland 46510 check valve 1/4 FNPT")
        sup.male_end("Push-to-connect elbow 1/4 tube", 26.0, 15.0, color="brass",
                     extra=lambda L: cyl(7.0, 18.0, (0, 0, L - 7.5), (-1, 0, 0)),
                     bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT")
        supply_tip[k] = sup.at(sup.s - 7.5) + V(-18.0, 0, 0)      # tube leaves the elbow going back
        bleed.nipple("1/4", color="brass")
        bleed.ff("Bleed ball valve", 40.0, 22.0, extra=ball_lever, bom="1/4 FNPT mini ball valve (manual bleed)")
        bleed.male_end("Muffler 1/4", 22.0, 16.0, color="brass", bom="1/4 NPT sintered muffler (compact)")

    # ---------------- cradle: two 1/8 in plates, QEV saddles and a breech block between them
    top = (n - 1) / 2 * P.PITCH
    clear = union([s for s in PARTS_LOCAL])
    for sy, tag in ((1, "left"), (-1, "right")):
        y0 = sy * CRADLE_Y0 if sy > 0 else -CRADLE_Y0 - CRADLE_T
        pts = [(-48, -top - 60), (130, -top - 60), (150, -top - 30), (150, top + 30), (130, top + 60), (-48, top + 60)]
        pl = cq.Workplane("XZ", origin=(0, y0, 0)).polyline(pts).close().extrude(-CRADLE_T).val()
        holes = [cyl(16.0, 20, (0, y0 - 5, (k - (n - 1) / 2) * P.PITCH), (0, 1, 0)) for k in range(n)]
        pl = pl.cut(union(holes))
        for (x, z) in ((-30, -top - 45), (-30, top + 45), (110, -top - 45), (110, top + 45), (60, 0), (-30, 0)):
            pl = pl.cut(cyl(3.3, 10, (x, y0 - 2, z), (0, 1, 0)))
        if sy < 0:
            for a in range(6):
                pl = pl.cut(cyl(1.7, 10, (11.5 * math.cos(a * math.pi / 3), y0 - 2, 11.5 * math.sin(a * math.pi / 3)), (0, 1, 0)))
        gadd(f"Cradle plate {tag} (1/8 Al)", pl, "alu", bom="Gun cradle plate (1/8 Al, waterjet)", kind="stock")
    for k in range(n):
        h = (k - (n - 1) / 2) * P.PITCH
        sad = box(-34, 34, -CRADLE_Y0, CRADLE_Y0, h - QEV["H"] / 2 - 8, h + QEV["H"] / 2 + 8)
        sad = sad.cut(qev(h, sides[k]).fuse(cyl(QEV["R"] + 0.4, QEV["L"], (-QEV["L"] / 2, 0, h), (1, 0, 0))))
        sad = sad.cut(cyl(OD["3/4"] / 2 + 1, 120, (0, -60, h), (0, 1, 0)))
        gadd(f"QEV saddle {['bottom', 'middle', 'top'][k]}", sad, "print", bom="QEV saddle", kind="print",
             note="PETG-CF, bolts through both cradle plates")
    bb = box(68, 125, -CRADLE_Y0, CRADLE_Y0, -top - 50, top + 50)
    for k in range(n):
        bb = bb.cut(cyl(42.4, 80, (60, 0, (k - (n - 1) / 2) * P.PITCH), (1, 0, 0)))
    for z0, z1, tag in ((-top - 50, 0, "lower"), (0, top + 50, "upper")):
        gadd(f"Breech block {tag}", bb.intersect(box(60, 130, -60, 60, z0, z1)), "print",
             bom="Breech block half", kind="print", note="clamps the three adapters")
    # mantlet: faceted cover over the breech, LED groove round its face
    mz0, mz1 = 125.0, 175.0
    w0 = cq.Workplane("YZ", origin=(mz0, 0, 0)).rect(150, 2 * top + 140).val()
    w1 = cq.Workplane("YZ", origin=(mz1, 0, 0)).rect(120, 2 * top + 100).val()
    man = cq.Solid.makeLoft([cq.Wire.assembleEdges(w0.Edges()), cq.Wire.assembleEdges(w1.Edges())], True)
    i0 = cq.Workplane("YZ", origin=(mz0 - 1, 0, 0)).rect(150 - 12, 2 * top + 140 - 12).val()
    i1 = cq.Workplane("YZ", origin=(mz1 - 6, 0, 0)).rect(120 - 12, 2 * top + 100 - 12).val()
    man = man.cut(cq.Solid.makeLoft([cq.Wire.assembleEdges(i0.Edges()), cq.Wire.assembleEdges(i1.Edges())], True))
    for k in range(n):
        man = man.cut(cyl(P.BARREL_OD / 2 + 1.0, 80, (mz0 - 5, 0, (k - (n - 1) / 2) * P.PITCH), (1, 0, 0)))
    for z0, z1, tag in ((-top - 80, 0, "lower"), (0, top + 80, "upper")):
        gadd(f"Mantlet {tag}", man.intersect(box(mz0 - 2, mz1 + 2, -80, 80, z0, z1)), "print",
             bom="Mantlet half (LED groove)", kind="print")

    # ---------------- trunnions
    # right (-y): hub on the right cradle plate, 1/2 in hex stub between the top and bottom chambers
    y_hub = -CRADLE_Y0 - CRADLE_T
    hub = cyl(16.0, 12.0, (0, y_hub, 0), (0, -1, 0)).cut(hex_prism(12.8, 14.0, (0, y_hub + 1, 0), (0, -1, 0)))
    gadd("Trunnion hub right", hub, "print_d", bom="Trunnion hub", kind="print", note="PA-CF, 6 x M3 to the cradle plate")
    y_tow = P.OUTER_RAIL_Y[1]
    shaft = hex_prism(12.7, y_tow - 1.0 - CRADLE_Y0 - CRADLE_T, (0, y_hub, 0), (0, -1, 0))
    gadd("Stub shaft right (1/2 hex)", shaft, "steel", bom="1/2 in hex shaft, steel", kind="stock")
    yp0 = -(P.ELEV_PULLEY_Y[1])
    pul = elevation_pulley().translate(V(0, yp0, 0))
    gadd("Elevation pulley 56T", pul, "print_d", bom="Elevation pulley 56T HTD 9 mm", kind="print", note="hex bore")
    # left (+y): hub clamped on the middle chamber's cap, 1/2 in hex stub to the left tower
    yc = chamber_end[1].y
    caphub = tube(70.0, 64.4, 30.0, (0, yc - 30.0, 0), (0, 1, 0)).fuse(
        cyl(70.0, 10.0, (0, yc, 0), (0, 1, 0))).cut(hex_prism(12.8, 12.0, (0, yc - 1, 0), (0, 1, 0)))
    gadd("Trunnion cap hub left", caphub, "print_d", bom="Trunnion cap hub", kind="print",
         note="PA-CF, clamps the 4 in cap, 2 x M5 pinch")
    shaft_l = hex_prism(12.7, y_tow - 1.0 - yc - 10.0, (0, yc + 10.0, 0), (0, 1, 0))
    gadd("Stub shaft left (1/2 hex)", shaft_l, "steel", bom="1/2 in hex shaft, steel", kind="stock")

    # ---------------- gun manifold (fed through a service loop) and its three supply tubes
    mx, mzm = -10.0, -top - 70.0                     # relief tip stays inside the slot floor's swing
    blk = box(mx - 38, mx + 38, -13, 13, mzm - 13, mzm + 13)
    gadd("Gun manifold block", blk, "brass", bom="1/4 NPT brass manifold, 1 in x 3 in, 6-port")
    ports = {0: (20.0, 1), 2: (-20.0, 1), 1: (-15.0, -1), "in": (25.0, -1)}
    tips = {}
    for key, (dx, sy) in ports.items():
        gadd(f"Gun manifold push-to-connect {key}", cyl(7.5, 22.0, (mx + dx, sy * 13, mzm), (0, sy, 0)), "brass",
             bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
        tips[key] = V(mx + dx, sy * 35.0, mzm)
    for k in range(n):
        h = (k - (n - 1) / 2) * P.PITCH
        t = supply_tip[k]
        xr = {0: -91.0, 1: -103.0, 2: -115.0}[k]                 # vertical runs behind the inlet blocks
        pts = [t, V(xr, t.y, h), V(xr, t.y, mzm)]
        if k == 1:                                              # -y side: in along y, clear of the bushings
            pts += [V(xr, tips[k].y, mzm)]
        pts += [tips[k]]
        gadd(f"Gun tube {['bottom', 'middle', 'top'][k]}", _tube_path(pts), "tube",
             bom="DOT nylon tube 1/4 OD (ft)", kind="stock")
    GUN_INLET[:] = [tips["in"]]
    gadd("Gun relief valve 150 psi", cyl(9.5, 44.0, (mx - 38, 0, mzm), (-1, 0, 0)), "brass",
         bom="Relief valve 150 psi 1/4 NPT (CAS250150)")
    gadd("Gun transducer 0-200 psi", cyl(10.0, 55.0, (mx + 38, 0, mzm), (1, 0, 0)), "steel",
         bom="Pressure transducer 0-200 psi 1/8 NPT (speedreplace)")
    bracket = box(mx - 45, mx + 45, -CRADLE_Y0, CRADLE_Y0, mzm + 13, -top - QEV["H"] / 2 - 8)
    gadd("Gun manifold bracket", bracket, "print", bom="Gun manifold bracket", kind="print")
    log("gun: built")
    return chamber_end


GUN_INLET = []


def _tube_path(points, r=3.175):
    segs = []
    pts = [V(*p) if not isinstance(p, V) else p for p in points]
    for a, b in zip(pts, pts[1:]):
        d = b - a
        if d.Length > 0.5:
            segs.append(cyl(r, d.Length, a.toTuple(), d.normalized().toTuple()))
    for p in pts[1:-1]:
        segs.append(cq.Solid.makeSphere(r, p, angleDegrees1=-90, angleDegrees2=90))
    return union(segs)


def elevation_pulley():
    t, w, fl = 56, 9.0, 2.0
    pd = P.pd(t)
    s = cyl(pd / 2 - 0.57, w, (0, fl, 0), (0, 1, 0))
    s = s.fuse(cyl(pd / 2 + 2.5, fl, (0, 0, 0), (0, 1, 0))).fuse(cyl(pd / 2 + 2.5, fl, (0, fl + w, 0), (0, 1, 0)))
    s = s.cut(hex_prism(12.8, w + 2 * fl + 2, (0, -1, 0), (0, 1, 0)))
    return s
