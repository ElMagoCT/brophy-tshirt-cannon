"""The elevating gun (rev C.1): two in-line cannons stacked one above the other; the pivot axis passes
between them.

Each cannon, back to front on one axis: 1/4 NPT brass cross (fill push-to-connect at the back, 125 psi relief
outward, transducer to the side) -> 1 x 1/4 bushing -> chamber (2 x 1 reducing coupling, 2 in Sch 40 x 8 in
nipple, 2 x 1 reducing coupling, about 0.53 L) -> 1 in close nipple -> 1 in solenoid valve (the old Atlantic
Valves SZW-25 on top, a U.S. Solid USS2-01023 below; 12 V DC, normally closed, coil pointing outward) -> 1 in close nipple -> CNC breech adapter (the
barrel slips over its spigot) -> clear polycarbonate barrel. The barrels sit GUN_GAP apart.
Rev C.3: a narrow core (cradle plates CRADLE_Y0 off the centre plane); a one-piece flowing mantlet, smoke collar
and muzzle ring that slide on from the muzzle; every tube (both fill lines and the smoke line) runs inside the core
and leaves through the bottom just behind the pivot, so the service loops barely move as the gun swings.
Gun-local frame: origin on the pivot axis, +X along the barrels, +Z up. The cannons are built, their centre of
mass is found from the parts' masses, and they are shifted so it lands on the axis: the gun balances in any
pose. The axis is carried by two 1/2 hex stubs, one bolted to each cradle plate.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, tube, hex_prism, union, C
from fittings import Chain, OD, ENG, BORE, relief_cap

IN = P.IN
R_CH = P.RED["OD_OUT"] / 2                                   # widest part of a chamber
R_PIPE = OD[P.CH_PIPE] / 2
BORE_PIPE = BORE[P.CH_PIPE]
CRADLE_Y0 = P.CRADLE_Y0                                      # inner faces of the two cradle plates
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


AD_BODY, AD_SHOULDER, AD_SPIGOT = 30.0, 10.0, 40.0              # breech adapter lengths along the axis
SMOKE_HOLE_X = AD_SPIGOT + 165.0                             # from the barrel's breech end: just past a 6 in rolled shirt
ACCENT_T = 8.5                                               # wall of the smoke collar and muzzle ring round the barrels
SMOKE_Y = 22.0                                               # smoke line: in the valley between the barrels, z = 0
FILL_LANES = (-10.0, -22.0)                                  # fill lines (top, bottom cannon): y in the chambers' valley
FILL_DOWN = ((-20.0, -44.0), (-30.0, -44.0))                 # (x, y) where each fill line drops out of the core
SMOKE_DOWN = (-8.0, 42.0)                                    # ... and the smoke line (where the bottom reducer is narrow)


def _rounded_prism(x0, L, W, H, r, edge=0.0):
    """Rounded rectangle W (y) x H (z), corner radius r, along +x from x0; edge > 0 rounds both end faces' rims."""
    s = cq.Workplane("YZ", origin=(x0, 0, 0)).rect(W, H).extrude(L).edges("|X").fillet(r)
    if edge:
        s = s.faces("<X or >X").edges().fillet(edge)
    return s.val()


def _rrect(x, W, H, r):
    f = cq.Face.makeFromWires(cq.Workplane("YZ", origin=(x, 0, 0)).rect(W, H).val())
    return f.fillet2D(r, f.Vertices()).outerWire()


def _groove(xg, W, H, r, w=6.0, d=2.5):
    """Band round a rounded-rectangle part's outside: a 5 mm LED strip groove w wide and d deep at x = xg."""
    return _rounded_prism(xg - w / 2, w, W + 4, H + 4, r + 2).cut(
        _rounded_prism(xg - w / 2 - 1, w + 2, W - 2 * d, H - 2 * d, r - d))


def adapter():
    """CNC breech adapter: 1 in NPT female at the back, a shoulder the barrel butts against and a spigot the
    barrel slips over (no wider than the barrel, so the barrels can sit close; the breech block clamps the
    polycarbonate over the spigot, never drilled)."""
    x1, x2 = AD_BODY, AD_BODY + AD_SHOULDER
    s = cyl(25.0, x1, (0, 0, 0), (1, 0, 0)).fuse(cyl(P.BARREL_OD / 2, AD_SHOULDER, (x1, 0, 0), (1, 0, 0)))
    s = s.fuse(cyl(P.BARREL_OD / 2 - P.BARREL_WALL - 0.15, AD_SPIGOT, (x2, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(OD["1"] / 2, ENG["1"] + 1, (-0.5, 0, 0), (1, 0, 0)))
    s = s.cut(cyl(13.3, x2, (0, 0, 0), (1, 0, 0)))
    return s.cut(cyl(P.BARREL_OD / 2 - P.BARREL_WALL - 4.0, AD_SPIGOT + 1, (x2, 0, 0), (1, 0, 0)))


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
    b0 = ax0 + AD_BODY + AD_SHOULDER
    bar = tube(P.BARREL_OD / 2, P.BARREL_OD / 2 - P.BARREL_WALL, P.BARREL_LEN, (b0, 0, h), (1, 0, 0))
    xh = b0 + SMOKE_HOLE_X
    for i in range(6):                                       # smoke holes just ahead of where the shirt sits
        a = math.radians(30 + 60 * i)
        bar = bar.cut(cyl(2.5, 20, (xh, 0, h), (0, math.cos(a), math.sin(a))))
    gadd(f"Barrel {tag}", bar, "pc", bom="Barrel: clear polycarbonate tube 3 in OD x 1/8 wall", kind="stock",
         note=f"{P.BARREL_LEN / IN:.1f} in; 6 x 5 mm smoke holes {SMOKE_HOLE_X:.0f} mm from the breech end")
    ci = Chain((xv - hl, 0, h), (-1, 0, 0), "F", gadd, f"{tag} chamber ")
    ci.nipple("1", bom="1 in Sch 40 close nipple (1-1/2 in)")
    r = P.RED
    red_bom = "Chamber: 2 x 1 black malleable reducing coupling, 150 lb (Supply Giant CNSD4005)"
    vol = ci.reducer("1", P.CH_PIPE, r["L"], r["OD_IN"], r["OD_OUT"], r["BAND_IN"], r["BAND_OUT"], bom=red_bom,
                     mass=r["MASS"])
    ci.nipple(P.CH_PIPE, length=P.CH_NIPPLE_L, bom="Chamber: 2 in Sch 40 black steel nipple x 8 in (Supply Giant OQCM2080)")
    vol += ci.reducer(P.CH_PIPE, "1", r["L"], r["OD_OUT"], r["OD_IN"], r["BAND_OUT"], r["BAND_IN"], bom=red_bom,
                      mass=r["MASS"])
    vol += math.pi * (BORE_PIPE / 2) ** 2 * P.CH_NIPPLE_L / 1000.0
    CH_VOL[:] = [vol]
    ci.bushing("1", "1/4", 34.9, 7.0, bom="1 x 1/4 NPT black malleable hex bushing (Supply Giant CNCV3003)")
    ci.nipple("1/4", color="brass", bom="1/4 NPT brass close nipple 7/8 in")
    ports = ci.block("1/4", side=32.0, sides=((0, 0, s), (0, 1, 0)),     # transducer left, tubes run right
                     bom="1/4 NPT brass cross (ChillWaves)")
    ci.male_end("fill push-to-connect", 22.0, 15.0, bom="DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)")
    tip = ci.at(ci.s)
    ports[0].male_end("relief 125 psi", 44.0, 19.0, bom="Relief valve 125 psi 1/4 MNPT, ASME, pull ring (Milton 1090-125)",
                      extra=relief_cap)
    ports[1].male_end("transducer 0-300 psi", 56.0, 20.0, color="steel",
                      bom="Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT (FUSCH) (+ 1/4 x 1/8 bushing)")
    return tip, ax0


def _build(xv):
    LOCAL.clear()
    fills, ax0s = [], []
    for k in range(2):
        t, ax0 = _cannon(k, xv)
        fills.append(t)
        ax0s.append(ax0)
    b0s = [a + AD_BODY + AD_SHOULDER for a in ax0s]
    ax0 = ax0s[0]
    hl = P.VALVE["L"] / 2
    xr = xv - hl                                             # valve rear face
    xs_list = [xr - sv for sv in P.CH_SADDLE_S]              # chamber saddles, on the 2 in nipples
    zo = P.PITCH / 2 + R_CH + 12.0
    xb1 = ax0 + AD_BODY + AD_SHOULDER + AD_SPIGOT            # end of the barrel spigots = front of the breech block
    # cradle: two 1/8 in plates outside everything, from the rear saddle to the breech block
    x0, x1 = min(xs_list) - 30.0, xb1
    for sy, tag in ((1, "left"), (-1, "right")):
        y0 = CRADLE_Y0 if sy > 0 else -CRADLE_Y0 - P.PLATE_T
        pts = [(x0, -zo), (x1 - 20, -zo), (x1, -zo + 20), (x1, zo - 20), (x1 - 20, zo), (x0, zo)]
        pl = cq.Workplane("XZ", origin=(0, y0, 0)).polyline(pts).close().extrude(-P.PLATE_T).val()
        pl = pl.cut(hex_prism(12.9, 20, (0, y0 - 5, 0), (0, 1, 0)))
        for a in range(6):
            pl = pl.cut(cyl(1.7, 10, (11.5 * math.cos(a * math.pi / 3), y0 - 2, 11.5 * math.sin(a * math.pi / 3)), (0, 1, 0)))
        for (x, z) in ((x0 + 15, zo - 15), (x0 + 15, -zo + 15), (x1 - 25, zo - 30), (x1 - 25, -zo + 30),
                       (xv, zo - 12), (xv, -zo + 12)):
            pl = pl.cut(cyl(3.3, 10, (x, y0 - 2, z), (0, 1, 0)))
        gadd(f"Cradle plate {tag} (1/8 Al)", pl, "alu", bom="Gun cradle plate (1/8 Al)", kind="stock")
    # chamber saddles: one block between the two nipples at each station, a printed cap bolted over each outer half
    cyls = [cyl(R_PIPE + 0.5, 1200, (xr - 1100, 0, h), (1, 0, 0)) for h in H]
    lanes = union([cyl(3.8, 1200, (xr - 1100, y, 0), (1, 0, 0)) for y in FILL_LANES])   # fill lines pass through
    for xs in xs_list:
        sad = box(xs - 14, xs + 14, -CRADLE_Y0, CRADLE_Y0, H[1], H[0]).cut(cyls[0]).cut(cyls[1]).cut(lanes)
        gadd(f"Chamber saddle {xs:.0f}", sad, "print", bom="Chamber saddle", kind="print",
             note="PETG-CF, screws through both cradle plates; caps close the outer halves")
        for k, h in enumerate(H):
            s = OUT[k]
            z0, z1 = (h + 0.5, h + 200) if s > 0 else (h - 200, h - 0.5)
            cap = tube(R_PIPE + 6.0, R_PIPE + 0.5, 20.0, (xs - 10, 0, h), (1, 0, 0)).intersect(box(xs - 11, xs + 11, -200, 200, z0, z1))
            fz0, fz1 = (h + 0.5, h + 6.5) if s > 0 else (h - 6.5, h - 0.5)
            yh = (R_PIPE + 6.0 + CRADLE_Y0 - 0.5) / 2 + 1.0       # M5 head clears the cap's ring
            for sy in (1, -1):                                  # flanges onto the saddle, one M5 each into an insert
                fl = box(xs - 10, xs + 10, min(sy * (R_PIPE + 3.0), sy * (CRADLE_Y0 - 0.5)),
                         max(sy * (R_PIPE + 3.0), sy * (CRADLE_Y0 - 0.5)), fz0, fz1)
                cap = cap.fuse(fl.cut(cyl(2.75, 20, (xs, sy * yh, fz0 - 1), (0, 0, 1))))
            gadd(f"Chamber cap {TAGS[k]} {xs:.0f}", cap.clean(), "print", bom="Chamber cap", kind="print",
                 note="PETG-CF, 2 x M5 into heat-set inserts in the saddle")
    for k, h in enumerate(H):
        vb = box(xv - hl + 4, xv + hl - 4, -CRADLE_Y0, CRADLE_Y0, h - 18, h + 18)
        vb = vb.cut(box(xv - hl - 1, xv + hl + 1, -P.VALVE["W"] / 2 - 0.4, P.VALVE["W"] / 2 + 0.4, h - 40, h + 40))
        for yy in (1, -1):
            gadd(f"Valve side block {TAGS[k]} {'L' if yy > 0 else 'R'}",
                 vb.intersect(box(-1000, 1000, 0 if yy > 0 else -500, 500 if yy > 0 else 0, -1000, 1000)), "print",
                 bom="Valve side block", kind="print", note="clamps the valve body between the cradle plates")
    # one breech block round both barrel spigots (the barrels are only GUN_GAP apart), split top and bottom
    bz = P.PITCH / 2 + P.BARREL_OD / 2 + 10.0
    bb = box(ax0 + AD_BODY - 2.0, xb1, -CRADLE_Y0, CRADLE_Y0, -bz, bz)
    for h in H:
        bb = bb.cut(cyl(P.BARREL_OD / 2 + 0.3, 200, (ax0, 0, h), (1, 0, 0))).cut(cyl(25.5, 40, (ax0 - 5, 0, h), (1, 0, 0)))
    bb = bb.cut(cyl(6.6, 200, (ax0 - 50, SMOKE_Y, 0), (1, 0, 0)))             # smoke line channel, split by the halves
    for z0, z1, tag in ((0.0, bz, "upper"), (-bz, 0.0, "lower")):
        gadd(f"Breech block {tag}", bb.intersect(box(-1000, 1000, -500, 500, z0 + (0.5 if z0 == 0 else 0), z1 - (0.5 if z1 == 0 else 0))),
             "print", bom="Breech block half", kind="print", note="the halves clamp both barrels onto their spigots")
    # mantlet, smoke collar and muzzle ring: one-piece prints that slide on from the muzzle in that order, all
    # rounded rectangles round both barrels with rounded rims; the mantlet flows (smooth loft) from the breech
    # block's face to a stadium hugging the barrels. LED grooves on the mantlet and muzzle ring
    rb = P.BARREL_OD / 2
    mz0, mz1 = xb1 + 2.0, xb1 + 50.0
    W0, H0 = 2 * CRADLE_Y0 - 2.0, 2 * bz
    W1, H1 = P.BARREL_OD + 12.0, P.PITCH + P.BARREL_OD + 12.0
    secs = [(mz0, W0, H0, 16.0), (mz0 + 28.0, (W0 + W1) / 2 + 1.0, (H0 + H1) / 2 + 1.0, 30.0),
            (mz1 - 5.0, W1, H1, W1 / 2 - 1.0), (mz1, W1 - 6.0, H1 - 6.0, W1 / 2 - 4.0)]
    man = cq.Solid.makeLoft([_rrect(*s) for s in secs], False)
    inner = [(mz0 - 1.0, W0 - 8.0, H0 - 8.0, 12.0), (mz0 + 28.0, secs[1][1] - 8.0, secs[1][2] - 8.0, 26.0),
             (mz1 - 8.0, W1 - 8.0, H1 - 8.0, W1 / 2 - 5.0)]
    man = man.cut(cq.Solid.makeLoft([_rrect(*s) for s in inner], False))
    for h in H:
        man = man.cut(cyl(rb + 1.0, 80, (mz0 - 5, 0, h), (1, 0, 0)))
    man = man.cut(cyl(6.9, 80, (mz0 - 5, SMOKE_Y, 0), (1, 0, 0)))
    man = man.cut(_groove(mz0 + 14.0, (W0 + secs[1][1]) / 2, (H0 + secs[1][2]) / 2, 23.0))
    gadd("Mantlet", man.clean(), "print", bom="Mantlet (printed, one piece, LED groove)", kind="print",
         note="slides on from the muzzle first and screws to the breech block; a 5 mm strip in its groove")
    # smoke collar: one plenum (the two ring grooves meet between the barrels) over the six holes in each barrel,
    # fed from the back by the gun's smoke line in a socket at z = 0
    xc = b0s[0] + SMOKE_HOLE_X
    Wa, Ha = 2 * (rb + ACCENT_T), P.PITCH + 2 * (rb + ACCENT_T)
    col = _rounded_prism(xc - 16, 32.0, Wa, Ha, rb + ACCENT_T - 0.5, edge=3.0)
    for h in H:
        col = col.cut(cyl(rb + 0.3, 40, (xc - 20, 0, h), (1, 0, 0))).cut(tube(rb + 5.0, rb, 14.0, (xc - 7, 0, h), (1, 0, 0)))
    col = col.cut(cyl(6.5, 10.0, (xc - 17, SMOKE_Y, 0), (1, 0, 0))).cut(cyl(3.5, 9.0, (xc - 8, SMOKE_Y, 0), (1, 0, 0)))
    col = col.cut(cyl(3.5, SMOKE_Y + 1.0, (xc, SMOKE_Y, 0), (0, -1, 0)))
    gadd("Smoke collar", col, "print", bom="Smoke collar (printed, one piece)", kind="print",
         note="slides on from the muzzle; seals on the barrels with a bead of RTV; the smoke line plugs into its rear port")
    xe = b0s[0] + P.BARREL_LEN
    mz = _rounded_prism(xe - 25.0, 25.0, Wa, Ha, rb + ACCENT_T - 0.5, edge=3.0)
    for h in H:
        mz = mz.cut(cyl(rb + 0.2, 30, (xe - 27.0, 0, h), (1, 0, 0)))
    mz = mz.cut(_groove(xe - 12.5, Wa, Ha, rb + ACCENT_T - 0.5))
    gadd("Muzzle ring", mz, "print", bom="Muzzle ring (printed, one piece, LED groove)", kind="print",
         note="slides on last, flush with the barrel ends; a 5 mm strip in its groove")
    # pivot: a 1/2 hex stub per side, through a hub on the plate's outer face, flush with its inner face
    ya = P.BEARING_BLOCK_Y[1] + 1.0
    for sy, tag, y_lo, y_hi in ((1, "left", CRADLE_Y0, ya + 12.0), (-1, "right", -ya, -CRADLE_Y0)):
        gadd(f"Pivot axle stub {tag} (1/2 hex)", hex_prism(12.7, y_hi - y_lo, (0, y_lo, 0), (0, 1, 0)), "steel",
             bom="1/2 in hex shaft, steel (pivot stub)", kind="stock", note=f"{(y_hi - y_lo) / IN:.1f} in, 1/4-20 tapped end")
        y_h = sy * (CRADLE_Y0 + P.PLATE_T)
        hub = cyl(16.0, 10.0, (0, y_h, 0), (0, sy, 0)).cut(hex_prism(12.9, 14.0, (0, y_h - sy, 0), (0, sy, 0)))
        gadd(f"Axle hub {tag}", hub, "print_d", bom="Axle hub", kind="print", note="PA-CF, 6 x M3 to the cradle plate")
    pul = elevation_pulley().translate(V(0, -P.ELEV_PULLEY_Y[1], 0))
    gadd(f"Elevation pulley {P.ELEV_T[1]}T", pul, "print_d", bom=f"Elevation pulley {P.ELEV_T[1]}T HTD 9 mm", kind="print",
         note="hex bore")
    # every tube runs inside the core and drops out of its bottom just behind the pivot: each fill line from its
    # chamber's push-to-connect round the back, forward in the valley between the chambers (through the saddles),
    # out beside the bottom reducer; the smoke line from the collar back along the barrels' valley, through the
    # mantlet and breech block, between the valves
    z_exit = -(zo + 4.0)
    exits = []
    for k, t in enumerate(fills):
        xd, yd = FILL_DOWN[k]
        xb = t.x - 18.0
        pts = [t, V(xb, 0, t.z), V(xb, FILL_LANES[k], 0), V(xd, FILL_LANES[k], 0), V(xd, yd, 0), V(xd, yd, z_exit)]
        gadd(f"Gun tube {TAGS[k]}", _tube_path(pts), "tube", bom="DOT nylon tube 1/4 OD (ft)", kind="stock",
             note="inside the core; leaves the bottom behind the pivot")
        exits.append(pts[-1])
    xd, yd = SMOKE_DOWN
    pts = [V(xc - 7.5, SMOKE_Y, 0), V(xd, SMOKE_Y, 0), V(xd, yd, 0), V(xd, yd, z_exit)]
    gadd("Gun smoke tube", _tube_path(pts, r=6.35), "tube", bom="Silicone tube 3/8 ID x 1/2 OD (ft)", kind="stock",
         note="collar to the bottom of the core")
    return exits, [pts[-1]]


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
    log(f"gun: valves at x {xv:.1f} from the axis, centre of mass ({cg:.1f}, {cgz:.1f}) mm, {mtot:.1f} kg; "
        f"chambers {CH_VOL[0] / 1000:.2f} L each, barrels {P.GUN_GAP:.1f} mm apart")


GUN_EXITS, FOG_EXITS, BALANCE, CH_VOL = [], [], {}, [0.0]


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
