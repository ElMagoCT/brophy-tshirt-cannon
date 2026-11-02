"""The elevating gun: two stacked clear polycarbonate barrels, each with a Humphrey QE5 3/4 in NPT quick
exhaust valve.

Gun-local frame (built at 0 deg, moved by robot.pose): origin on the pivot axis, +X along the barrels,
+Z up, Y as the robot. The top barrel's QEV sits on the pivot axis; the bottom one is PITCH below.
QE5 ports: inlet and exhaust on one axis (inlet at the back, exhaust forward to the barrel), cylinder
port on the side -> each short steel chamber runs sideways (0.4 L: 4 x 3/4 bushing into a 4 in cap).
The top chamber points left (+y) and lies on the pivot axis, so its cap carries the left trunnion; the
right stub shaft passes above the bottom chamber and carries the 56T elevation pulley.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, tube, hex_prism, union
from fittings import Chain, OD, ENG, relief_cap

IN = P.IN
QEV = dict(L=93.0, H=55.4, R=29.0, BOSS=46.0, BOSS_R=19.0)   # Humphrey QE5 (3.66 x 2.18 x 2.95 in)
CRADLE_T = P.PLATE_T
CRADLE_Y0 = 47.0                                             # inner faces of the two cradle plates
PARTS_LOCAL = []
H = [0.0, -P.PITCH]                                          # barrel heights: top on the pivot, bottom below
SIDES = [1, -1]                                              # chamber side per barrel
TAGS = ["top", "bottom"]
ZMAX, ZMIN = max(H), min(H)


def gadd(name, shape, color, group="gun", bom=None, kind="cots", note="", moving=True):
    PARTS_LOCAL.append(shape)
    return add(name, shape, color, "gun", bom=bom, kind=kind, moving=True, note=note)


def qev_body():
    body = cyl(QEV["R"], QEV["L"], (-QEV["L"] / 2, 0, 0), (1, 0, 0))
    return body.intersect(box(-60, 60, -40, 40, -QEV["H"] / 2, QEV["H"] / 2))


def qev(h, side):
    s = qev_body().fuse(cyl(QEV["BOSS_R"], QEV["BOSS"], (0, 0, 0), (0, side, 0)))
    for p, d in (((-QEV["L"] / 2, 0, 0), (1, 0, 0)), ((QEV["L"] / 2, 0, 0), (-1, 0, 0))):
        s = s.cut(cyl(OD["3/4"] / 2, ENG["3/4"], p, d))
    s = s.cut(cyl(OD["3/4"] / 2, ENG["3/4"], (0, side * QEV["BOSS"], 0), (0, -side, 0)))
    return s.translate(V(0, 0, h))


def adapter():
    """CNC breech adapter: 3/4 NPT female at the back, 3 in barrel socket at the front, split clamp
    (the polycarbonate is clamped, never drilled)."""
    L, od = 64.0, 84.0
    s = cyl(od / 2, L, (0, 0, 0), (1, 0, 0))
    s = s.cut(cyl(OD["3/4"] / 2, ENG["3/4"] + 1, (-0.5, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(10.5, L, (0, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(P.BARREL_OD / 2 + 0.15, 40.0, (L - 40.0, 0, 0), (1, 0, 0)))
    s = s.cut(box(L - 30, L + 1, -1.5, 1.5, 0, od))
    s = s.cut(cyl(3.3, 30, (L - 15, -15, od / 2 - 8), (0, 1, 0)))
    return s


def va4_coil(sign):
    """VA-4 coil standing off the valve body along local +/-Y; both barrels' coils point down."""
    return lambda length: cyl(18.0, 50.0, (0, sign * 11.0, length / 2), (0, sign, 0))


def build(log=print):
    PARTS_LOCAL.clear()
    chamber_end = {}
    supply_tip = {}
    for k, h in enumerate(H):
        sd, tag, qx = SIDES[k], TAGS[k], P.QX[k]
        gadd(f"QEV Humphrey QE5 {tag}", qev(h, sd).translate(V(qx, 0, 0)), "alu", bom="Humphrey QE5 3/4 NPT quick exhaust valve")
        # barrel side: exhaust -> 3/4 close nipple -> CNC adapter -> polycarbonate barrel
        ch = Chain((qx + QEV["L"] / 2, 0, h), (1, 0, 0), "F", gadd, f"{tag} ")
        ch.nipple("3/4")
        ax0 = ch.at(ch.s).x - ENG["3/4"]
        gadd(f"Breech adapter {tag}", adapter().translate(V(ax0, 0, h)), "alu",
             bom="Breech adapter (CNC 6061, stash bar)", kind="machined")
        b0 = ax0 + 64.0 - 40.0
        blen = P.BARREL_LEN - qx                       # muzzles flush
        barrel = tube(P.BARREL_OD / 2, P.BARREL_OD / 2 - P.BARREL_WALL, blen, (b0, 0, h), (1, 0, 0))
        gadd(f"Barrel {tag}", barrel, "pc", bom="Barrel: clear polycarbonate tube 3 in OD x 1/8 wall", kind="stock",
             note=f"{blen / IN:.1f} in")
        mz = cyl(43.0, 25.0, (b0 + blen - 25.0, 0, h), (1, 0, 0)).cut(
            cyl(P.BARREL_OD / 2 + 0.2, 30, (b0 + blen - 27.0, 0, h), (1, 0, 0)))
        mz = mz.cut(tube(41.0, 39.0, 6.0, (b0 + blen - 15.0, 0, h), (1, 0, 0)))
        gadd(f"Muzzle ring {tag}", mz, "print", bom="Muzzle ring (LED groove)", kind="print")
        # chamber side: cylinder port -> 3/4 close nipple -> 4 x 3/4 bushing -> 4 in cap (about 0.4 L)
        cc = Chain((qx, sd * QEV["BOSS"], h), (0, sd, 0), "F", gadd, f"{tag} chamber ")
        cc.nipple("3/4")
        cc.bushing_rev("4", "3/4", 124.5, 16.0, color="steel", bom="4 x 3/4 NPT hex bushing (malleable)")
        cc.cap("4", 53.0, 128.0, bom="4 in NPT cap (Class 150 malleable)")
        chamber_end[k] = cc.at(cc.s)
        # inlet pocket: 3/4 x 1/4 bushing -> 1/4 close nipple -> 5-port brass block
        #   chamber side: supply push-to-connect (check valve is on the fixed fill manifold)
        #   other side:   VA-4 dump valve + muffler, coil standing outward
        #   outward z:    150 psi relief with pull ring (doubles as the manual bleed)
        #   inward z:     chamber transducer (5-port block: no rear port)
        ic = Chain((qx - QEV["L"] / 2, 0, h), (-1, 0, 0), "F", gadd, f"{tag} inlet ")
        ic.bushing("3/4", "1/4", 27.0, 10.0, color="brass", bom="3/4 x 1/4 NPT hex bushing (brass)")
        ic.nipple("1/4", color="brass")
        out_z = 1 if k == 0 else -1
        sup, dump, rel, trans = ic.block(sides=((0, sd, 0), (0, -sd, 0), (0, 0, out_z), (0, 0, -out_z)), rear=False,
                                         bom="1/4 NPT brass 5-port block (Interstate CPT44-5)")
        sup.male_end("Push-to-connect supply", 22.0, 15.0, color="brass", bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
        supply_tip[k] = sup.at(sup.s)
        dump.nipple("1/4", color="brass")
        dump.ff("Dump valve VA-4", 38.0, 25.0, extra=va4_coil(-1 if k == 0 else 1), bom="HornBlasters VA-4 12 V 1/4 NPT valve (dump)")
        dump.male_end("Muffler 1/4", 22.0, 16.0, color="brass", bom="1/4 NPT sintered muffler (compact)")
        rel.male_end("Relief valve 150 psi", 46.0, 19.0, extra=relief_cap,
                     bom="Relief valve 150 psi 1/4 NPT, pull ring (CAS250150)")
        trans.bushing("1/4", "1/8", 14.0, 6.0, color="brass", bom="1/4 x 1/8 NPT hex bushing (brass)")
        trans.male_end("Chamber transducer 0-200 psi", 48.0, 20.0, size="1/8", color="steel",
                       bom="Pressure transducer 0-200 psi, 0.5-4.5 V, 1/8 NPT")

    # ---------------- cradle: two 1/8 in plates, QEV saddles and breech blocks between them
    xb = -71.0 + P.QX[1]                                         # bottom inlet block x
    for sy, tag in ((1, "left"), (-1, "right")):
        y0 = sy * CRADLE_Y0 if sy > 0 else -CRADLE_Y0 - CRADLE_T
        pts = [(-48, ZMIN - 60), (170, ZMIN - 60), (190, ZMIN - 30), (190, ZMAX + 30), (170, ZMAX + 60), (-48, ZMAX + 60)]
        pl = cq.Workplane("XZ", origin=(0, y0, 0)).polyline(pts).close().extrude(-CRADLE_T).val()
        pl = pl.cut(union([cyl(16.0, 20, (q, y0 - 5, h), (0, 1, 0)) for q, h, s in zip(P.QX, H, SIDES) if s == sy]))
        if sy > 0:                                               # notch for the bottom VA-4 and its coil
            pl = pl.cut(box(xb - 21, xb + 21, y0 - 5, y0 + 10, ZMIN - 70, H[1] + 13.0))
        for (x, z) in ((-30, ZMAX + 45), (150, ZMAX + 45), (150, ZMIN - 45), (8, ZMIN - 45), (100, (ZMIN + ZMAX) / 2)):
            pl = pl.cut(cyl(3.3, 10, (x, y0 - 2, z), (0, 1, 0)))
        if sy < 0:
            for a in range(6):
                pl = pl.cut(cyl(1.7, 10, (11.5 * math.cos(a * math.pi / 3), y0 - 2, 11.5 * math.sin(a * math.pi / 3)),
                                (0, 1, 0)))
        gadd(f"Cradle plate {tag} (1/8 Al)", pl, "alu", bom="Gun cradle plate (1/8 Al)", kind="stock")
    for k, h in enumerate(H):
        qx = P.QX[k]
        sad = box(qx - 34, qx + 34, -CRADLE_Y0, CRADLE_Y0, h - QEV["H"] / 2 - 8, h + QEV["H"] / 2 + 8)
        sad = sad.cut(qev(h, SIDES[k]).translate(V(qx, 0, 0)).fuse(
            cyl(QEV["R"] + 0.4, QEV["L"], (qx - QEV["L"] / 2, 0, h), (1, 0, 0))))
        sad = sad.cut(cyl(OD["3/4"] / 2 + 1, 120, (qx, -60, h), (0, 1, 0)))
        gadd(f"QEV saddle {TAGS[k]}", sad, "print", bom="QEV saddle", kind="print",
             note="PETG-CF, bolts through both cradle plates")
        bb = box(qx + 68, qx + 125, -CRADLE_Y0, CRADLE_Y0, h - P.PITCH / 2, h + 50 if k == 0 else h + P.PITCH / 2)
        bb = bb.cut(cyl(42.4, 80, (qx + 60, 0, h), (1, 0, 0)))
        gadd(f"Breech block {TAGS[k]}", bb, "print", bom="Breech block", kind="print", note="clamps the adapter")
    zc = (ZMIN + ZMAX) / 2
    mz0, mz1 = 160.0, 210.0
    span = ZMAX - ZMIN
    w0 = cq.Workplane("YZ", origin=(mz0, 0, zc)).rect(150, span + 140).val()
    w1 = cq.Workplane("YZ", origin=(mz1, 0, zc)).rect(120, span + 100).val()
    man = cq.Solid.makeLoft([cq.Wire.assembleEdges(w0.Edges()), cq.Wire.assembleEdges(w1.Edges())], True)
    i0 = cq.Workplane("YZ", origin=(mz0 - 1, 0, zc)).rect(150 - 12, span + 140 - 12).val()
    i1 = cq.Workplane("YZ", origin=(mz1 - 6, 0, zc)).rect(120 - 12, span + 100 - 12).val()
    man = man.cut(cq.Solid.makeLoft([cq.Wire.assembleEdges(i0.Edges()), cq.Wire.assembleEdges(i1.Edges())], True))
    for h in H:
        man = man.cut(cyl(P.BARREL_OD / 2 + 1.0, 80, (mz0 - 5, 0, h), (1, 0, 0)))
    for z0, z1, tag in ((ZMIN - 80, zc, "lower"), (zc, ZMAX + 80, "upper")):
        gadd(f"Mantlet {tag}", man.intersect(box(mz0 - 2, mz1 + 2, -80, 80, z0, z1)), "print",
             bom="Mantlet half (LED groove)", kind="print")

    # ---------------- trunnions
    y_hub = -CRADLE_Y0 - CRADLE_T
    hub = cyl(16.0, 12.0, (0, y_hub, 0), (0, -1, 0)).cut(hex_prism(12.8, 14.0, (0, y_hub + 1, 0), (0, -1, 0)))
    gadd("Trunnion hub right", hub, "print_d", bom="Trunnion hub", kind="print", note="PA-CF, 6 x M3 to the cradle plate")
    y_end = P.ELEV_PULLEY_Y[1] + 1.0
    gadd("Stub shaft right (1/2 hex)", hex_prism(12.7, y_end + y_hub, (0, y_hub, 0), (0, -1, 0)), "steel",
         bom="1/2 in hex shaft, steel (trunnion stubs)", kind="stock")
    pul = elevation_pulley().translate(V(0, -P.ELEV_PULLEY_Y[1], 0))
    gadd("Elevation pulley 56T", pul, "print_d", bom="Elevation pulley 56T HTD 9 mm", kind="print", note="hex bore")
    yc = chamber_end[0].y
    caphub = tube(70.0, 64.4, 30.0, (0, yc - 30.0, 0), (0, 1, 0)).fuse(
        cyl(70.0, 5.0, (0, yc, 0), (0, 1, 0))).cut(hex_prism(12.8, 7.0, (0, yc - 1, 0), (0, 1, 0)))
    gadd("Trunnion cap hub left", caphub, "print_d", bom="Trunnion cap hub", kind="print",
         note="PA-CF, clamps the 4 in cap, 2 x M5 pinch")
    shaft_l = hex_prism(12.7, P.ELEV_PULLEY_Y[0] + 6.0 - yc - 5.0, (0, yc + 5.0, 0), (0, 1, 0))
    gadd("Stub shaft left (1/2 hex)", shaft_l, "steel", bom="1/2 in hex shaft, steel (trunnion stubs)", kind="stock")

    # ---------------- supply tubes inside the cradle, out the left side behind the plate (service loops go on)
    t0, t1 = supply_tip[0], supply_tip[1]
    paths = {0: [t0, V(t0.x, 44.0, -6.0), V(-75.0, 44.0, -30.0), V(-75.0, 62.0, -30.0)],
             1: [t1, V(t1.x, -42.0, t1.z), V(-66.0, -42.0, t1.z), V(-66.0, 40.0, t1.z), V(-82.0, 40.0, -75.0),
                 V(-82.0, 62.0, -52.0)]}
    for k, pts in paths.items():
        gadd(f"Gun tube {TAGS[k]}", _tube_path(pts), "tube", bom="DOT nylon tube 1/4 OD (ft)", kind="stock")
    GUN_EXITS[:] = [paths[0][-1], paths[1][-1]]
    log("gun: built")
    return chamber_end


GUN_EXITS = []


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
    t, w, fl = P.ELEV_T[1], 9.0, 2.0
    pd = P.pd(t)
    s = cyl(pd / 2 - 0.57, w, (0, fl, 0), (0, 1, 0))
    s = s.fuse(cyl(pd / 2 + 2.5, fl, (0, 0, 0), (0, 1, 0))).fuse(cyl(pd / 2 + 2.5, fl, (0, fl + w, 0), (0, 1, 0)))
    return s.cut(hex_prism(12.8, w + 2 * fl + 2, (0, -1, 0), (0, 1, 0)))
