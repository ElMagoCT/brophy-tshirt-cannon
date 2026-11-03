"""The elevating gun (rev C): two in-line cannons stacked one above the other; the pivot axle passes
between them.

Each cannon, back to front on one axis: chamber tank (1 gal, 200 psi ASME steel, 1 in NPT end port) ->
1 in close nipple -> Atlantic Valves SZW-25 1 in stainless solenoid valve (12 V DC, normally closed, coil
pointing outward) -> 1 in close nipple -> CNC breech adapter -> clear polycarbonate barrel.
Gun-local frame: origin on the axle, +X along the barrels, +Z up. The cannons are built, their centre of
mass is found from the parts' masses, and they are shifted so it lands on the axle: the gun balances in
any pose. Each chamber carries a fill push-to-connect, a 125 psi relief (its pull ring is the manual
bleed) and a transducer on its outward side.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, tube, hex_prism, union, C
from fittings import Chain, OD, ENG, relief_cap

IN = P.IN
R_CH = P.CH_D / 2
CRADLE_Y0 = R_CH + 3.5                                       # inner faces of the two cradle plates
TAGS = ["top", "bottom"]
H = [P.PITCH / 2, -P.PITCH / 2]
OUT = [1, -1]                                                # outward direction (coil, fittings) per cannon
LOCAL = []                                                   # (name, shape, color, bom, kind, note, mass)
DENS = {"steel": 7.85, "alu": 2.70, "brass": 8.5, "print": 1.27 * 0.4, "print_d": 1.27 * 0.6, "pc": 1.2,
        "tube": 1.15 * 0.3, "black": 1.5, "tank": 7.85}


def gadd(name, shape, color, group="gun", bom=None, kind="cots", note="", moving=True, mass=None):
    if isinstance(shape, cq.Workplane):
        shape = shape.val()
    LOCAL.append(dict(name=name, shape=shape, color=color, bom=bom or name, kind=kind, note=note, mass=mass))
    return shape


def _mass(p):
    if p["mass"] is not None:
        return p["mass"]
    return p["shape"].Volume() / 1e6 * DENS.get(p["color"], 1.0)


def valve(xv, h, s):
    """Atlantic Valves SZW-25: stainless body (1 in NPT both ends), bonnet and 12 V coil toward `s`."""
    v = P.VALVE
    hl = v["L"] / 2
    z0, z1 = sorted([h - s * (-v["BODY"][0]), h + s * v["BODY"][1]])
    body = box(xv - hl, xv + hl, -v["W"] / 2, v["W"] / 2, z0, z1)
    for x0, d in ((xv - hl, 1), (xv + hl, -1)):
        body = body.cut(cyl(OD["1"] / 2, ENG["1"], (x0, 0, h), (d, 0, 0)))
    ztop = h + s * v["BODY"][1]
    coil = cyl(v["COIL_R"], v["COIL_TOP"] - v["BODY"][1], (xv, 0, ztop), (0, 0, s))
    nut = hex_prism(19.0, 8.0, (xv, 0, h + s * v["COIL_TOP"]), (0, 0, s))
    return union([body, coil, nut])


def adapter():
    """CNC breech adapter: 1 in NPT female at the back, 3 in barrel socket at the front, split clamp
    (the polycarbonate is clamped, never drilled)."""
    L, od = 64.0, 84.0
    s = cyl(od / 2, L, (0, 0, 0), (1, 0, 0))
    s = s.cut(cyl(OD["1"] / 2, ENG["1"] + 1, (-0.5, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(13.3, L, (0, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(P.BARREL_OD / 2 + 0.15, 40.0, (L - 40.0, 0, 0), (1, 0, 0)))
    s = s.cut(box(L - 30, L + 1, -1.5, 1.5, 0, od))
    return s.cut(cyl(3.3, 30, (L - 15, -15, od / 2 - 8), (0, 1, 0)))


def chamber(x_front, h, s, fit_x):
    """1 gal ASME tank lying on the cannon axis, its 1 in end port facing forward at x_front and three
    1/4 NPT bosses on its outward side."""
    L = P.CH_L - P.CH_BOSS
    shell = cq.Workplane("YZ", origin=(x_front - P.CH_BOSS - L, 0, 0)).center(0, h).circle(R_CH).extrude(L) \
        .edges().fillet(R_CH * 0.55).val()
    parts = [shell, cyl(21.0, P.CH_BOSS, (x_front - P.CH_BOSS, 0, h), (1, 0, 0))]
    parts += [cyl(9.0, 12.0, (x, 0, h + s * (R_CH - 4)), (0, 0, s)) for x in fit_x]
    return union(parts).cut(cyl(OD["1"] / 2 + 0.3, ENG["1"], (x_front + 0.1, 0, h), (-1, 0, 0)))


def _cannon(k, xv):
    """One cannon in gun-local coordinates with its valve centre at x = xv. Returns its tank-fill tip."""
    h, s, tag = H[k], OUT[k], TAGS[k]
    hl = P.VALVE["L"] / 2
    gadd(f"Firing valve {tag} (Atlantic Valves SZW-25)", valve(xv, h, s), "steel",
         bom="Firing valve: Atlantic Valves SZW-25 1 in NPT stainless solenoid, 12 V DC, NC", mass=1.0)
    ch = Chain((xv + hl, 0, h), (1, 0, 0), "F", gadd, f"{tag} ")
    ch.nipple("1", bom="1 in Sch 40 close nipple (1-1/2 in)")
    ax0 = ch.at(ch.s).x - ENG["1"]
    gadd(f"Breech adapter {tag}", adapter().translate(V(ax0, 0, h)), "alu",
         bom="Breech adapter (CNC 6061, stash bar, 1 in NPT tap)", kind="machined")
    b0 = ax0 + 24.0
    gadd(f"Barrel {tag}", tube(P.BARREL_OD / 2, P.BARREL_OD / 2 - P.BARREL_WALL, P.BARREL_LEN, (b0, 0, h), (1, 0, 0)),
         "pc", bom="Barrel: clear polycarbonate tube 3 in OD x 1/8 wall", kind="stock", note=f"{P.BARREL_LEN / IN:.1f} in")
    xe = b0 + P.BARREL_LEN
    mz = cyl(43.0, 25.0, (xe - 25.0, 0, h), (1, 0, 0)).cut(cyl(P.BARREL_OD / 2 + 0.2, 30, (xe - 27.0, 0, h), (1, 0, 0)))
    mz = mz.cut(tube(41.0, 39.0, 6.0, (xe - 15.0, 0, h), (1, 0, 0)))
    gadd(f"Muzzle ring {tag}", mz, "print", bom="Muzzle ring (LED groove)", kind="print")
    ci = Chain((xv - hl, 0, h), (-1, 0, 0), "F", gadd, f"{tag} chamber ")
    ci.nipple("1", bom="1 in Sch 40 close nipple (1-1/2 in)")
    x_front = ci.at(ci.s).x + ENG["1"]                      # tank port face takes the nipple
    fit_x = [xf + (xv - P.X_VALVE) for xf in P.CH_FIT_X]
    gadd(f"Chamber {tag} (1 gal tank)", chamber(x_front, h, s, fit_x), "tank",
         bom="Chamber: 1 gal 200 psi ASME steel air tank, 1 in NPT end port", mass=2.7)
    # outward fittings on the tank: fill push-to-connect elbow, 125 psi relief, transducer
    zs = h + s * R_CH
    tips = None
    for i, (xf, kind) in enumerate(zip(P.CH_FIT_X, ("fill", "relief", "trans"))):
        x = xf + (xv - P.X_VALVE)
        z0 = zs + s * 8
        if kind == "fill":
            el = cyl(7.5, 14.0, (x, 0, z0), (0, 0, s)).fuse(cyl(7.0, 18.0, (x, 0, z0 + s * 7), (-1, 0, 0)))
            gadd(f"{tag} chamber fill push-to-connect", el, "brass",
                 bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT", mass=0.03)
            tips = V(x - 18.0, 0, z0 + s * 7)
        elif kind == "relief":
            r = cyl(9.5, 44.0, (x, 0, z0), (0, 0, s)).fuse(cyl(13.0, 2.0, (x, 0, z0 + s * 30), (0, 0, s)))
            gadd(f"{tag} chamber relief 125 psi", r, "brass", bom="Relief valve 125 psi 1/4 MNPT, ASME, pull ring (Milton 1090-125)", mass=0.1)
        else:
            t = cyl(8.0, 6.0, (x, 0, z0), (0, 0, s)).fuse(cyl(10.0, 48.0, (x, 0, z0 + s * 6), (0, 0, s)))
            gadd(f"{tag} chamber transducer 0-200 psi", t, "steel",
                 bom="Pressure transducer 0-200 psi, 0.5-4.5 V, 1/8 NPT (+ 1/4 x 1/8 bushing)", mass=0.08)
    return tips, x_front, ax0


def _build(xv):
    LOCAL.clear()
    fills, fronts, ax0s = [], [], []
    for k in range(2):
        t, xf, ax0 = _cannon(k, xv)
        fills.append(t)
        fronts.append(xf)
        ax0s.append(ax0)
    xf, ax0 = fronts[0], ax0s[0]
    hl = P.VALVE["L"] / 2
    zo = P.PITCH / 2 + R_CH + 10.0
    # cradle: two 1/8 in plates outside the tanks, from mid-tank to the breech blocks
    x0, x1 = xf - 175.0, ax0 + 60.0
    for sy, tag in ((1, "left"), (-1, "right")):
        y0 = CRADLE_Y0 if sy > 0 else -CRADLE_Y0 - P.PLATE_T
        pts = [(x0, -zo), (x1 - 20, -zo), (x1, -zo + 20), (x1, zo - 20), (x1 - 20, zo), (x0, zo)]
        pl = cq.Workplane("XZ", origin=(0, y0, 0)).polyline(pts).close().extrude(-P.PLATE_T).val()
        pl = pl.cut(hex_prism(12.9, 20, (0, y0 - 5, 0), (0, 1, 0)))
        for a in range(6):
            pl = pl.cut(cyl(1.7, 10, (11.5 * math.cos(a * math.pi / 3), y0 - 2, 11.5 * math.sin(a * math.pi / 3)), (0, 1, 0)))
        for (x, z) in ((x0 + 25, zo - 25), (x0 + 25, -zo + 25), (x1 - 25, zo - 40), (x1 - 25, -zo + 40),
                       (xv, zo - 15), (xv, -zo + 15)):
            pl = pl.cut(cyl(3.3, 10, (x, y0 - 2, z), (0, 1, 0)))
        gadd(f"Cradle plate {tag} (1/8 Al)", pl, "alu", bom="Gun cradle plate (1/8 Al)", kind="stock")
    for k, h in enumerate(H):
        s = OUT[k]
        cyl_ch = cyl(R_CH + 0.5, 600, (xf - 590, 0, h), (1, 0, 0))
        for xs in (xf - 40.0, xf - 160.0):                    # tank saddles, inward half (straps go round)
            zlo, zhi = sorted([0.0, h])
            sad = box(xs - 14, xs + 14, -CRADLE_Y0, CRADLE_Y0, zlo + (2.0 if h > 0 else -2.0), zhi).cut(cyl_ch)
            sad = sad.intersect(box(xs - 14, xs + 14, -CRADLE_Y0, CRADLE_Y0, h if h < 0 else 2.0,
                                    h if h > 0 else -2.0))
            gadd(f"Chamber saddle {TAGS[k]} {xs:.0f}", sad, "print", bom="Chamber saddle", kind="print",
                 note="PETG-CF, screws through both cradle plates; a strap closes the outer half")
            gadd(f"Chamber strap {TAGS[k]} {xs:.0f}", tube(R_CH + 2.5, R_CH + 0.5, 20.0, (xs - 10, 0, h), (1, 0, 0)).intersect(
                box(xs - 11, xs + 11, -200, 200, h + 0.5 if s > 0 else h - 200, h + 200 if s > 0 else h - 0.5)),
                "black", bom="1 in cam-buckle strap")
        vb = box(xv - hl + 4, xv + hl - 4, -CRADLE_Y0, CRADLE_Y0, h - 22, h + 22)
        vb = vb.cut(box(xv - hl - 1, xv + hl + 1, -P.VALVE["W"] / 2 - 0.4, P.VALVE["W"] / 2 + 0.4, h - 40, h + 40))
        for yy in (1, -1):
            gadd(f"Valve side block {TAGS[k]} {'L' if yy > 0 else 'R'}",
                 vb.intersect(box(-1000, 1000, 0 if yy > 0 else -500, 500 if yy > 0 else 0, -1000, 1000)), "print",
                 bom="Valve side block", kind="print", note="clamps the valve body between the cradle plates")
        bb = box(ax0 + 6, ax0 + 60, -CRADLE_Y0, CRADLE_Y0, h - 45 if s > 0 else h - 44, h + 44 if s > 0 else h + 45)
        bb = bb.cut(cyl(42.4, 80, (ax0, 0, h), (1, 0, 0)))
        gadd(f"Breech block {TAGS[k]}", bb, "print", bom="Breech block", kind="print", note="clamps the adapter")
    # mantlet with two fog vents between the barrels
    mz0, mz1 = ax0 + 64.0, ax0 + 112.0
    span = P.PITCH
    w0 = cq.Workplane("YZ", origin=(mz0, 0, 0)).rect(2 * CRADLE_Y0 - 4, span + 130).val()
    w1 = cq.Workplane("YZ", origin=(mz1, 0, 0)).rect(2 * CRADLE_Y0 - 34, span + 90).val()
    man = cq.Solid.makeLoft([cq.Wire.assembleEdges(w0.Edges()), cq.Wire.assembleEdges(w1.Edges())], True)
    i0 = cq.Workplane("YZ", origin=(mz0 - 1, 0, 0)).rect(2 * CRADLE_Y0 - 16, span + 118).val()
    i1 = cq.Workplane("YZ", origin=(mz1 - 6, 0, 0)).rect(2 * CRADLE_Y0 - 46, span + 78).val()
    man = man.cut(cq.Solid.makeLoft([cq.Wire.assembleEdges(i0.Edges()), cq.Wire.assembleEdges(i1.Edges())], True))
    for h in H:
        man = man.cut(cyl(P.BARREL_OD / 2 + 1.0, 80, (mz0 - 5, 0, h), (1, 0, 0)))
    fog_tips = []
    yv = 56.0                                                # fog vents between the barrels, inside the mantlet sides
    for yy in (1, -1):
        man = man.cut(cyl(11.3, 80, (mz0 - 5, yy * yv, 0), (1, 0, 0)))
        man = man.cut(cyl(11.3, 200, (mz0 + 10, yy * yv, 0), (0, 0, -1)))
    for z0, z1, tag in ((-span / 2 - 70, 0, "lower"), (0, span / 2 + 70, "upper")):
        gadd(f"Mantlet {tag}", man.intersect(box(mz0 - 2, mz1 + 2, -100, 100, z0, z1)), "print",
             bom="Mantlet half (LED groove, fog vents)", kind="print")
    zl = -(P.PITCH / 2 + 70.0)
    for yy in (1, -1):
        nz = union([cyl(11.0, mz1 + 10.0 - (mz0 + 10.0), (mz0 + 10.0, yy * yv, 0), (1, 0, 0)),
                    cyl(11.0, -zl, (mz0 + 10.0, yy * yv, 0), (0, 0, -1)),
                    cq.Solid.makeSphere(11.0, V(mz0 + 10.0, yy * yv, 0), angleDegrees1=-90, angleDegrees2=90)])
        nz = nz.cut(union([cyl(9.0, 200, (mz0 + 10.0, yy * yv, 0), (1, 0, 0)), cyl(9.0, 200, (mz0 + 10.0, yy * yv, 0), (0, 0, -1)),
                           cq.Solid.makeSphere(9.0, V(mz0 + 10.0, yy * yv, 0), angleDegrees1=-90, angleDegrees2=90)]))
        gadd(f"Fog vent gun {'L' if yy > 0 else 'R'}", nz, "print", bom="Fog vent nozzle (gun)", kind="print",
             note="PETG elbow: inlet out the bottom of the mantlet, outlet between the barrels")
        fog_tips.append(V(mz0 + 10.0, yy * yv, zl))
    # axle (through both plates, between the cannons), hubs, elevation pulley
    ya = P.BEARING_BLOCK_Y[1] + 1.0
    gadd("Pivot axle (1/2 hex)", hex_prism(12.7, 2 * ya + 12.0, (0, -ya, 0), (0, 1, 0)), "steel",
         bom="1/2 in hex shaft, steel (pivot axle)", kind="stock", note=f"{(2 * ya + 12) / IN:.1f} in")
    for sy, tag in ((1, "left"), (-1, "right")):
        y_h = sy * (CRADLE_Y0 + P.PLATE_T)
        hub = cyl(16.0, 10.0, (0, y_h, 0), (0, sy, 0)).cut(hex_prism(12.9, 14.0, (0, y_h - sy, 0), (0, sy, 0)))
        gadd(f"Axle hub {tag}", hub, "print_d", bom="Axle hub", kind="print", note="PA-CF, 6 x M3 to the cradle plate")
    pul = elevation_pulley().translate(V(0, -P.ELEV_PULLEY_Y[1], 0))
    gadd("Elevation pulley 56T", pul, "print_d", bom="Elevation pulley 56T HTD 9 mm", kind="print", note="hex bore")
    # supply tubes from each chamber's fill elbow, round the back of the cradle plate, out the left side
    exits = []
    for k, t in enumerate(fills):
        s = OUT[k]
        xb, yb = fronts[k] - P.CH_L - 14.0, -30.0
        pts = [t, V(t.x, yb, t.z), V(xb, yb, t.z), V(xb, yb, s * 40.0)]
        gadd(f"Gun tube {TAGS[k]}", _tube_path(pts), "tube", bom="DOT nylon tube 1/4 OD (ft)", kind="stock")
        exits.append(pts[-1])
    return exits, fog_tips


def build(log=print):
    """Build once, find the centre of mass, shift the cannons so it sits on the axle, rebuild, register."""
    xv = P.X_VALVE
    for _ in range(3):
        exits, fogs = _build(xv)
        mtot = sum(_mass(p) for p in LOCAL)
        cg = sum(_mass(p) * p["shape"].Center().x for p in LOCAL) / mtot
        if abs(cg) < 1.0:
            break
        xv -= cg
    cgz = sum(_mass(p) * p["shape"].Center().z for p in LOCAL) / mtot
    BALANCE.update(xv=xv, cg_x=cg, cg_z=cgz, mass=mtot)
    for p in LOCAL:
        add(p["name"], p["shape"], p["color"], "gun", bom=p["bom"], kind=p["kind"], moving=True, note=p["note"],
            mass=p["mass"])
    GUN_EXITS[:] = exits
    FOG_EXITS[:] = fogs
    log(f"gun: valves at x {xv:.1f} from the axle, centre of mass ({cg:.1f}, {cgz:.1f}) mm, {mtot:.1f} kg")


GUN_EXITS, FOG_EXITS, BALANCE = [], [], {}


def sweep_profile(step=2.5, margin=10.0, ybins=None):
    """Lowest world z the gun reaches at each x over 0-90 deg (parts inside the well width only)."""
    px, pz = P.PIVOT
    pts = []
    for p in LOCAL:
        b = p["shape"].BoundingBox()
        if b.ymax < -P.Y_SLOT - 5 or b.ymin > P.Y_SLOT + 5:
            continue
        verts, tris = p["shape"].tessellate(2.0, 0.5)
        vs = [(v.x, v.z) for v in verts]
        pts += vs
        for tri in tris:                                   # long cylinder facets: add points along the edges
            for i0, i1 in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                (xa, za), (xb, zb) = vs[i0], vs[i1]
                n = int(math.hypot(xb - xa, zb - za) // 15.0)
                for j in range(1, n + 1):
                    f = j / (n + 1)
                    pts.append((xa + (xb - xa) * f, za + (zb - za) * f))
    env = {}
    a = 0.0
    while a <= P.ELEV_RANGE[1] + 1e-6:
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        for x, z in pts:
            wx, wz = px + x * c - z * s_, pz + x * s_ + z * c
            kx = int(math.floor(wx / 10.0))
            if kx not in env or wz < env[kx]:
                env[kx] = wz
        a += step
    return {k * 10.0: v - margin for k, v in env.items()}


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
