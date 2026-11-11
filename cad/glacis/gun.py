"""The elevating gun (rev C.1): two in-line cannons stacked one above the other; the pivot axis passes
between them. Brophy Borealis (2026-11-10): the chambers are welded (3 in Sch 40 pipe between two 3/8 in discs, the
valve on a 1 in nipple welded through the front one, a 1/4 NPT bung near the front for the fill line); the notes
below describe the threaded chambers they replace.

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
import pneu_parts as PP
import plates
from lib import add, box, cyl, tube, hex_prism, union, C, t_slot
from fittings import Chain, OD, ENG, BORE, relief_cap

OD.setdefault("3", 88.9)                                     # 3 in Sch 40 chambers (rev D.1)
ENG.setdefault("3", 26.0)
BORE.setdefault("3", 77.9)

IN = P.IN
R_CH = OD[P.CH_PIPE] / 2                                     # widest part of a chamber (welded: the pipe itself)
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


def valve(xv, h, s, v=P.VALVE):
    """Firing valve (the SZW-25 or the HSV04): body (1 in NPT both ends), bonnet and 12 V coil toward `s`."""
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
FILL_LANES = (-59.0, -67.0)                                  # fill lines (top, bottom cannon): y beside the couplings
FILL_DOWN = ((-20.0, -59.0), (-30.0, -67.0))                 # (x, y) where each fill line drops out of the core
# Pivot hubs (Micah, 2026-11-10: "clean up the cannon hub"; "the pulley should screw to the aluminum side plate instead
# of going through the axle"): a 72 mm boss on each cradle plate's outer face that fills the gap to the inner pivot
# bearing (a lip bears on its inner race, so the gun can't slide sideways); the right one is the 112T pulley. 4 x M4 x 30
# from the outer face (counterbored) through the plate into nylocs inside, at angles that clear the fill and smoke lines
# and the valve side blocks inside the plates (checked against the pass-2 gun)
HUB_FL_R, HUB_FL_T, HUB_BOLT_R = 36.0, 3.0, 28.0              # left hub flange radius / thickness (3 mm: an M4 x 12
                                                             # then reaches right through the nyloc), bolt circle
HUB_BOLTS = tuple((HUB_BOLT_R * math.cos(math.radians(a)), HUB_BOLT_R * math.sin(math.radians(a))) for a in (30, 120, 195, 300))
# Right side (Micah, 2026-11-10: "the cannon pulley should be a ring and have standoffs so its screwed to and floating on
# the side"): the 112T ring's 6 standoffs sit on a 78 mm circle at angles whose M4 heads inside the plate clear the
# valve side blocks and the fill lines
RING_IN, RING_BOLT_R, RING_CB = 68.0, 78.0, 5.5                # ring bore radius, standoff circle, counterbore depth
                                                             # (5.5: the M4 x 12 and the M4 x 8 don't meet inside the 10 mm nut)
RING_BOLTS = tuple((RING_BOLT_R * math.cos(math.radians(a)), RING_BOLT_R * math.sin(math.radians(a)))
                   for a in (10, 90, 150, 210, 270, 350))
SMOKE_DOWN = (-8.0, 63.0)                                    # ... and the smoke line, on the other side


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


VALVE_INFO = (("U.S. Solid USS-HSV04", "Firing valve top: U.S. Solid USS-HSV04 1 in NPT, 12 V DC, NC, pilot, 725 psi", 1.75),
              ("U.S. Solid USS-HSV04", "Firing valve bottom: U.S. Solid USS-HSV04 1 in NPT, 12 V DC, NC, pilot, 725 psi", 1.75))


def _cannon(k, xf):
    """One cannon in gun-local coordinates with its valve's front face at x = xf. Returns its tank-fill tip."""
    h, s, tag = H[k], OUT[k], TAGS[k]
    v = P.VALVES[k]
    hl = v["L"] / 2
    xv = xf - hl
    name, vbom, vmass = VALVE_INFO[k]
    gadd(f"Firing valve {tag} ({name})", valve(xv, h, s, v), "steel", bom=vbom, mass=vmass)
    ch = Chain((xv + hl, 0, h), (1, 0, 0), "F", gadd, f"{tag} ")
    ch.nipple("1", bom="1 in NPT close nipple (1-1/2 in), seamless steel, Sch 80")
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
    # Brophy Borealis welded chamber (Micah, 2026-11-10): half of a 1 x 4 in nipple (its threaded end into the valve)
    # welded through a 3/8 in A36 front disc (1.33 in hole), flush with the disc's inner face; 3 in Sch 40 plain-end
    # pipe between the two 3.5 in discs; the back disc is blank. The 1/4 NPT weld bung sits 1 in behind the front disc
    # on the tube-lane side (-y), turned 30 deg toward the axis, with a swivel push-to-connect elbow.
    # The transducer and relief moved to a cross after the in valve on the chassis (misc.air)
    e1, T = ENG["1"], P.CH_DISC_T
    xr0 = xv - hl                                            # the valve's rear face
    toe = P.CH_TOE_L
    xpi = xr0 + e1 - toe                                     # pipe's front end = the front disc's inner face
    nl = P.CH_PIPE_L[k]
    gadd(f"Chamber outlet nipple {tag}", tube(OD["1"] / 2, BORE["1"] / 2, toe, (xpi, 0, h), (1, 0, 0)), "steel",
         bom="Chamber outlet: 1 in TOE nipple (half of a 1 x 4 in black nipple), welded through the front disc", kind="stock")
    disc_f = cyl(R_PIPE, T, (xpi, 0, h), (1, 0, 0)).cut(cyl(1.33 * IN / 2, T + 2, (xpi - 1, 0, h), (1, 0, 0)))
    gadd(f"Chamber front disc {tag}", disc_f, "steel", bom="Chamber end disc: 3/8 in A36, 3.5 in OD (waterjet)",
         kind="machined", note="1.33 in hole for the outlet nipple; welded to the pipe and the nipple")
    gadd(f"Chamber pipe {tag}", tube(R_PIPE, BORE_PIPE / 2, nl, (xpi - nl, 0, h), (1, 0, 0)), "steel",
         bom="Chamber: 3 in Sch 40 steel pipe, plain end (cut)", kind="stock", note=f"{nl / IN:.1f} in")
    gadd(f"Chamber back disc {tag}", cyl(R_PIPE, T, (xpi - nl - T, 0, h), (1, 0, 0)), "steel",
         bom="Chamber end disc: 3/8 in A36, 3.5 in OD (waterjet)", kind="machined", note="blank; welded on")
    # printed end cover over the welded back end (Micah 2026-11-10: "make the back more interesting"): a sleeve that
    # pushes onto the pipe over the disc and weld, a short chevron-faceted nose and an LED groove; cosmetic only, the
    # steel disc is the pressure boundary
    xe = xpi - nl - T                                        # the back disc's outer face
    ri, ro = R_PIPE + 0.8, R_PIPE + 4.0
    cov = tube(ro, ri, 30.0, (xe - 4.0, 0, h), (1, 0, 0)).fuse(cyl(ro, 4.0, (xe - 4.0, 0, h), (1, 0, 0)))
    sides = 8                                               # octagonal faceted nose, 18 mm long
    ring0 = [V(xe - 4.0, ro * math.cos(2 * math.pi * i / sides + math.pi / 8), h + ro * math.sin(2 * math.pi * i / sides + math.pi / 8))
             for i in range(sides)]
    ring1 = [V(xe - 22.0, 0.45 * ro * math.cos(2 * math.pi * i / sides + math.pi / 8), h + 0.45 * ro * math.sin(2 * math.pi * i / sides + math.pi / 8))
             for i in range(sides)]
    nose = cq.Solid.makeLoft([cq.Wire.makePolygon(ring0, close=True), cq.Wire.makePolygon(ring1, close=True)], True)
    cov = cov.fuse(nose).cut(tube(ro + 1, ro - 2.0, 6.0, (xe + 12.0, 0, h), (1, 0, 0)))
    gadd(f"Chamber end cover {tag}", cov.clean(), "print", bom="Chamber end cover (printed)", kind="print",
         note="PETG, 4 walls; pushes onto the chamber's welded back end with a bead of RTV; LED groove for a 5 mm strip; "
              "cosmetic, not on the pressure boundary")
    CH_VOL[k] = math.pi * (BORE_PIPE / 2) ** 2 * nl / 1000.0
    xb_ = xpi - P.CH_BUNG_X                                  # the inlet bung, 1 in behind the front disc
    dn = V(0, -math.sin(math.radians(60)), -s * 0.5)         # toward the tube lane, 30 deg toward the axis (the two
                                                             # elbows then clear each other between the chambers)
    base = V(xb_, 0, h) + dn * (R_PIPE - 6.0)
    top = V(xb_, 0, h) + dn * (R_PIPE + P.CH_BUNG_H)
    bung = cyl(11.0, P.CH_BUNG_H + 6.0, base.toTuple(), dn.toTuple()).cut(
        cyl(7.0, P.CH_BUNG_H + 8.0, (base - dn * 1.0).toTuple(), dn.toTuple())).cut(
        cyl(R_PIPE, 60, (xb_ - 30, 0, h), (1, 0, 0)))
    gadd(f"Chamber inlet bung {tag}", bung, "steel", bom="Chamber inlet: 1/4 NPT female steel weld-on bung", kind="stock",
         note="welded over a 1/2 in hole in the pipe wall")
    out = V(1, 0, 0)                                         # forward, to where its tube drops out of the core
    gadd(f"Chamber inlet elbow {tag}", PP.ptc_elbow(top, dn.toTuple(), out.toTuple()), "brass",
         bom="DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT (Boeray)")
    tip = top + dn * 13.0 + out * 16.0
    return tip, ax0


def _build(xv):
    LOCAL.clear()
    fills, ax0s = [], []
    for k in range(2):
        t, ax0 = _cannon(k, xv)                              # xv: the valves' front faces (they line up)
        fills.append(t)
        ax0s.append(ax0)
    b0s = [a + AD_BODY + AD_SHOULDER for a in ax0s]
    ax0 = ax0s[0]
    xr = xv - max(v["L"] for v in P.VALVES)                  # rear face of the longer valve
    xs_list = [xv - sv for sv in P.CH_SADDLE_S]              # chamber saddles, where both 3 in pipes run
    zo = P.PITCH / 2 + R_CH + 12.0
    xb1 = ax0 + AD_BODY + AD_SHOULDER + AD_SPIGOT            # end of the barrel spigots = front of the breech block
    # cradle: two 1/8 in plates outside everything, from the rear saddle to the breech block
    x0, x1 = min(xs_list) - 4.0, xb1                         # Micah: shorter at the back (was rear saddle - 30)
    rx0, rx1 = x0 + 22.0, min(xv - 58.0, x0 + 22.0 + 300.0)        # the 20x20 add-on rail inside each top edge
    # Hole review (Micah 2026-11-10: "the screw holes that don't have anything behind them ... should be moved"): the six
    # 6.6 mm tie holes had nothing behind them and are gone. Every hole in a plate now has an insert, nut, T-nut or
    # standoff behind it: saddles (sad_holes), chamber caps (cap_holes), the gun core halves (core_holes), the hub /
    # ring, the rail's T-nuts and the hex stub
    bx0 = ax0 + AD_BODY - 2.0                                 # the breech block's rear face
    zc_ = P.PITCH / 2 + 18.0
    lay = plates.layout(min(xs_list) - 4.0, zo, xs_list, bx0, cap_z=zc_)
    core_holes = [(x, sg * z) for sg in (1, -1) for x, z in
                  ((plates.core_web_x(lay, 0, P.PITCH / 2), P.PITCH / 2),      # in the web between front chevrons 1 and 2
                   (xv - P.VALVES[0]["L"] + 34.0, P.PITCH / 2 - 10.0), (bx0 + 16.0, 45.0))]
    # M4 x 8 into inserts in each saddle's side, on the web between two side chevrons (plates.layout)
    xsf, xsr = max(xs_list), min(xs_list)
    sad_holes = plates.saddle_screws([xsf], lay)
    # the rear chamber holder follows the plate's swallowtail (Micah: "align it with the indent on the back ... make it
    # match the profile"): a V band 24 mm wide, 4 mm in from the plate's back edge
    vx = lambda z: plates.rear_edge_x(x0, zo, z) + 4.0              # holder's back face at height z
    sad_holes += [(vx(30.0) + 12.0, 30.0), (vx(30.0) + 12.0, -30.0)]
    cap_holes = [(xsf, zc_), (xsf, -zc_), (vx(zc_) + 12.0, zc_), (vx(zc_) + 12.0, -zc_)]
    side_holes = sad_holes + cap_holes + core_holes           # all M4 x 8 through the plate into M4 inserts

    def inserts(shape, pts):
        """Insert holes in a printed part's two side faces at the plates' screw points."""
        for (x, z) in pts:
            for sy in (1, -1):
                shape = shape.cut(cyl(P.INSERT[0], P.INSERT[1], (x, sy * CRADLE_Y0, z), (0, -sy, 0)))
        return shape
    # Brophy Borealis plate (Micah 2026-11-10: "combine chevron and turret wheel. make the wheel chevrons"): see plates.py
    flat = plates.plate_2d(P.PLATE_T, x0, x1, zo, xs_list, ax0 + AD_BODY - 2.0, (rx0, rx1),
                           [(x, z, 5.5) for x, z in side_holes],
                           list(RING_BOLTS) + list(HUB_BOLTS), cap_z=zc_)
    for sy, tag in ((1, "left"), (-1, "right")):
        y0 = CRADLE_Y0 if sy > 0 else -CRADLE_Y0 - P.PLATE_T
        pl = plates.to_side(flat, y0)
        pl = pl.cut(hex_prism(12.9, 20, (0, y0 - 5, 0), (0, 1, 0)))
        for (hx, hz) in (HUB_BOLTS if sy > 0 else RING_BOLTS):   # the left hub's bolts / the right ring's standoffs
            pl = pl.cut(cyl(2.25, 10, (hx, y0 - 2, hz), (0, 1, 0)))
        for (x, z) in side_holes:
            pl = pl.cut(cyl(2.25, 10, (x, y0 - 2, z), (0, 1, 0)))
        # Brophy Borealis: a 20x20 T-slot rail inside each plate along its top edge, flush with it, for add-ons;
        # 3 x M4 x 8 through the plate into drop-in T-nuts in the rail's outer slot (clear of the plate's own holes)
        ry = (CRADLE_Y0 - P.RAIL20, CRADLE_Y0) if sy > 0 else (-CRADLE_Y0, -CRADLE_Y0 + P.RAIL20)
        rz = (zo - P.RAIL20, zo)
        for xs_ in (rx0 + 30.0, (rx0 + rx1) / 2, rx1 - 30.0):
            pl = pl.cut(cyl(2.25, 10, (xs_, y0 - 2, zo - P.RAIL20 / 2), (0, 1, 0)))
        gadd(f"Cradle plate {tag} (1/8 Al)", pl, "alu", bom="Gun cradle plate (1/8 Al, CNC router)", kind="stock",
             note="Chevron + turret wheel: swallowtail back, round boss round the pivot, chevron pockets (CNC router: too big for the 12 x 12 waterjet)")
        gadd(f"Rail 20x20 gun {tag}", t_slot(rx0, rx1, ry, rz), "alu", bom="20x20 T-slot extrusion (owned spare, cut)",
             kind="stock", mass=0.47 * (rx1 - rx0) / 1000.0,
             note=f"{rx1 - rx0:.0f} mm; 3 x M4 x 8 through the cradle plate into M4 drop-in T-nuts; top flush with the plate")
    # chamber saddles: one block between the two nipples at each station, a printed cap bolted over each outer half
    cyls = [cyl(R_PIPE + 0.5, 1200, (xr - 1100, 0, h), (1, 0, 0)) for h in H]
    lanes = union([cyl(3.8, 1200, (xr - 1100, y, 0), (1, 0, 0)) for y in FILL_LANES])   # fill lines pass through
    for xs in [xsf]:
        sad = box(xs - 14, xs + 14, -CRADLE_Y0, CRADLE_Y0, H[1], H[0]).cut(cyls[0]).cut(cyls[1]).cut(lanes)
        sad = inserts(sad, sad_holes[:2])
        gadd(f"Chamber saddle {xs:.0f}", sad, "print", bom="Chamber saddle", kind="print",
             note="PETG, 5 walls, 40% gyroid; 2 x M4 x 8 through each cradle plate into inserts in its sides; caps close "
                  "the outer halves")
        # caps (Micah 2026-11-10: "fix these holes", "make the chamber caps better"): a solid block over each pipe's
        # outer half that fills out to the plates (under the add-on rail on top), so there are no open corners
        # round the pipe; held by one M4 x 8 through each cradle plate into an insert in each side
        yw, yn = CRADLE_Y0 - 0.5, CRADLE_Y0 - P.RAIL20 - 0.5          # full width / beside the rail
        for k, h in enumerate(H):
            s = OUT[k]
            e = abs(h) + R_PIPE + 6.0                                  # the cap's outer face, |z|
            if s > 0:
                zw = min(e, zo - P.RAIL20 - 0.5)
                prof = [(-yw, h + 0.5), (yw, h + 0.5), (yw, zw), (yn, zw), (yn, e - 6), (yn - 6, e), (-yn + 6, e),
                        (-yn, e - 6), (-yn, zw), (-yw, zw)]
            else:
                prof = [(-yw, h - 0.5), (yw, h - 0.5), (yw, -e + 8), (yw - 8, -e), (-yw + 8, -e), (-yw, -e + 8)]
            cap = cq.Workplane("YZ", origin=(xs - 10, 0, 0)).polyline(prof).close().extrude(20.0).val()
            cap = cap.cut(cyl(R_PIPE + 0.5, 30, (xs - 15, 0, h), (1, 0, 0)))
            cap = inserts(cap, [cap_holes[0] if s > 0 else cap_holes[1]])
            gadd(f"Chamber cap {TAGS[k]} {xs:.0f}", cap.clean(), "print", bom="Chamber cap", kind="print",
                 note="PETG, 5 walls, 40% gyroid; fills out to the cradle plates; one M4 x 8 through each plate into an "
                      "M4 insert in each side (the old top screws sat under the add-on rail)")
    # rear chamber holder: saddle + 2 caps, each a V band that follows the plate's swallowtail back
    def vband(za, zb, ya, yb, w=24.0):
        zs = sorted({za, zb} | ({0.0} if za < 0 < zb else set()))
        back = [(vx(z), z) for z in zs]
        front = [(vx(z) + w, z) for z in reversed(zs)]
        return cq.Workplane("XZ", origin=(0, yb, 0)).polyline(back + front).close().extrude(yb - ya).val()
    xc = lambda z: vx(z) + 12.0
    sad = inserts(vband(H[1], H[0], -CRADLE_Y0, CRADLE_Y0).cut(cyls[0]).cut(cyls[1]).cut(lanes), sad_holes[2:])
    gadd("Chamber saddle rear", sad, "print", bom="Chamber saddle", kind="print",
         note="PETG, 5 walls, 40% gyroid; V-shaped to follow the plates' swallowtail back; 2 x M4 x 8 through each "
              "cradle plate into inserts in its sides; caps close the outer halves")
    yw, yn = CRADLE_Y0 - 0.5, CRADLE_Y0 - P.RAIL20 - 0.5
    for k, h in enumerate(H):
        s = OUT[k]
        e = abs(h) + R_PIPE + 6.0
        if s > 0:
            zw = min(e, zo - P.RAIL20 - 0.5)
            cap = vband(h + 0.5, zw, -yw, yw).fuse(vband(zw, e, -yn, yn))
        else:
            cap = vband(-e, h - 0.5, -yw, yw)
        cap = cap.cut(cyls[k])
        cap = inserts(cap, [cap_holes[2] if s > 0 else cap_holes[3]])
        gadd(f"Chamber cap {TAGS[k]} rear", cap.clean(), "print", bom="Chamber cap", kind="print",
             note="PETG, 5 walls, 40% gyroid; V-shaped like the plates' back; fills out to the plates; one M4 x 8 through "
                  "each plate into an M4 insert in each side")
    # Gun core (Micah 2026-11-10: combine the mantlet, the breech block and the valve side blocks): one printed left
    # half and one right half, split on the gun's centre plane (y = 0) with a 1 mm gap. Each half is one side's two
    # valve blocks (run forward into the breech block), half of the breech block round both barrel spigots and half of
    # the mantlet. Split left / right, the halves close round both barrels like a clamshell (split top / bottom, each
    # half would be a closed ring round its own barrel: nothing would clamp, and it could only slide on from the
    # muzzle). 2 x M4 x 12 across the split between the barrels clamp them onto their spigots; each half then takes
    # 6 x M4 x 8 through its own cradle plate into inserts
    bz = P.PITCH / 2 + P.BARREL_OD / 2 + 10.0
    core = box(bx0, xb1, -CRADLE_Y0, CRADLE_Y0, -bz, bz)
    for h in H:
        core = core.cut(cyl(P.BARREL_OD / 2 + 0.1, 200, (ax0, 0, h), (1, 0, 0))).cut(cyl(25.5, 40, (ax0 - 5, 0, h), (1, 0, 0)))
    core = core.cut(cyl(P.SMOKE_R + 0.35, 200, (ax0 - 50, SMOKE_Y, 0), (1, 0, 0)))         # smoke line channel (in the left half)
    for k, h in enumerate(H):
        vk = P.VALVES[k]
        x0v = xv - vk["L"]
        vb = box(x0v + 22, bx0 + 1, -CRADLE_Y0, CRADLE_Y0, h - 18, h + 18)                # +22: the half stays on a 250 mm bed
        core = core.fuse(vb.cut(box(x0v - 1, bx0 + 2, -vk["W"] / 2 - 0.4, vk["W"] / 2 + 0.4, h - 40, h + 40)))
    # mantlet: flows (smooth loft) from the breech block's face to a stadium hugging the barrels; LED groove
    rb = P.BARREL_OD / 2
    mz0, mz1 = xb1 - 0.5, xb1 + 50.0
    W0, H0 = 2 * CRADLE_Y0 - 2.0, 2 * bz
    W1, H1 = P.BARREL_OD + 12.0, P.PITCH + P.BARREL_OD + 12.0
    secs = [(mz0, W0, H0, 16.0), (mz0 + 28.0, (W0 + W1) / 2 + 1.0, (H0 + H1) / 2 + 1.0, 30.0),
            (mz1 - 5.0, W1, H1, W1 / 2 - 1.0), (mz1, W1 - 6.0, H1 - 6.0, W1 / 2 - 4.0)]
    man = cq.Solid.makeLoft([_rrect(*s_) for s_ in secs], False)
    inner = [(xb1, W0 - 8.0, H0 - 8.0, 12.0), (mz0 + 28.0, secs[1][1] - 8.0, secs[1][2] - 8.0, 26.0),
             (mz1 - 8.0, W1 - 8.0, H1 - 8.0, W1 / 2 - 5.0)]
    man = man.cut(cq.Solid.makeLoft([_rrect(*s_) for s_ in inner], False))
    for h in H:
        man = man.cut(cyl(rb + 1.0, 80, (mz0 - 5, 0, h), (1, 0, 0)))
    man = man.cut(cyl(P.SMOKE_R + 0.65, 80, (mz0 - 5, SMOKE_Y, 0), (1, 0, 0)))
    man = man.cut(_groove(mz0 + 14.0, (W0 + secs[1][1]) / 2, (H0 + secs[1][2]) / 2, 23.0))
    core = inserts(core.fuse(man), core_holes)
    for xcl in (bx0 + 12.0, bx0 + 40.0):                     # clamp screws between the barrels, head in the right half
        core = core.cut(cyl(2.25, 14.0, (xcl, -7.0, 0.0), (0, 1, 0)))
        core = core.cut(cyl(4.6, 100.0, (xcl, -7.0, 0.0), (0, -1, 0)))                     # counterbore out to the half's side
        core = core.cut(cyl(P.INSERT[0], P.INSERT[1], (xcl, 0.5, 0.0), (0, 1, 0)))
    for y0_, y1_, tag in ((0.5, 500.0, "left"), (-500.0, -0.5, "right")):
        half = core.intersect(box(-1000, 2000, y0_, y1_, -500, 500))
        gadd(f"Gun core {tag}", half.clean(), "print", bom="Gun core half (valve blocks + breech block + mantlet, printed)",
             kind="print",
             note="PETG, 5 walls, 40% gyroid, printed outer face down; the two halves close round both valves and both "
                  "barrels: 2 x M4 x 12 across the split (heads in the right half, inserts in the left) clamp the "
                  "barrels onto their spigots, then 6 x M4 x 8 through each cradle plate into M4 inserts; a 5 mm LED "
                  "strip in the mantlet groove")
    # smoke collar: one plenum (the two ring grooves meet between the barrels) over the six holes in each barrel,
    # fed from the back by the gun's smoke line in a socket at z = 0
    xc = b0s[0] + SMOKE_HOLE_X
    Wa, Ha = 2 * (rb + ACCENT_T), P.PITCH + 2 * (rb + ACCENT_T)
    col = _rounded_prism(xc - 16, 32.0, Wa, Ha, rb + ACCENT_T - 0.5, edge=3.0)
    for h in H:
        col = col.cut(cyl(rb + 0.3, 40, (xc - 20, 0, h), (1, 0, 0))).cut(tube(rb + 5.0, rb, 14.0, (xc - 7, 0, h), (1, 0, 0)))
    col = col.cut(cyl(P.SMOKE_R + 0.25, 10.0, (xc - 17, SMOKE_Y, 0), (1, 0, 0))).cut(cyl(5.25, 9.0, (xc - 8, SMOKE_Y, 0), (1, 0, 0)))
    col = col.cut(cyl(5.25, SMOKE_Y + 1.0, (xc, SMOKE_Y, 0), (0, -1, 0)))
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
             bom="1/2 in hex shaft, steel (pivot stub)", kind="stock", note=f"{(y_hi - y_lo) / IN:.1f} in, tapped 1/4-20 both ends: a bolt and washer inside the cradle plate and one "
                  "outside the outer bearing keep it from sliding")
    # hubs: boss on the plate's outer face out to just short of the inner bearing, a lip on its inner race
    yp = CRADLE_Y0 + P.PLATE_T                                   # plate outer face
    yb = P.BEARING_BLOCK_Y[0]                                    # inner bearing face (flange counterbored flush)
    # left (Micah 2026-11-10: "the turret hub needs to be cleaned up"): a slim flanged hub, keyed on the stub (it turns
    # the pot): a 3 mm flange on the plate carries the 4 bolts, a 44 mm barrel runs to the inner bearing with a lip on
    # its inner race; the plate's turret boss is the visual hub now
    hub = cyl(HUB_FL_R, HUB_FL_T, (0, yp, 0), (0, 1, 0)).fuse(cyl(22.0, yb - 1.5 - yp, (0, yp, 0), (0, 1, 0)))
    hub = hub.fuse(cyl(9.5, 1.7, (0, yb - 2.0, 0), (0, 1, 0)))
    hub = hub.cut(hex_prism(12.9, yb - yp + 2, (0, yp - 1, 0), (0, 1, 0)))
    for (hx, hz) in HUB_BOLTS:
        hub = hub.cut(cyl(2.25, HUB_FL_T + 2, (hx, yp - 1, hz), (0, 1, 0)))
    gadd("Axle hub left", hub.clean(), "print_d", bom="Axle hub", kind="print",
         note="PETG, 5 walls, 40% gyroid; hex bore on the pivot stub; 4 x M4 x 12 through its flange and the cradle "
              "plate into nylocs; its lip bears on the inner bearing's inner race")
    # right (Micah 2026-11-10): the 112T pulley is a ring floating on 6 standoffs off the cradle plate, in a belt plane
    # centred between the plate and the bearing block; a printed sleeve on the stub does the old hub's locating job
    y0r, y1r = P.ELEV_PULLEY_Y
    ring = elevation_pulley().translate(V(0, -y1r, 0)).cut(cyl(RING_IN, 40, (0, -y1r - 5, 0), (0, 1, 0)))
    for (hx, hz) in RING_BOLTS:
        ring = ring.cut(cyl(2.25, 20, (hx, -y1r - 1, hz), (0, 1, 0)))
        ring = ring.cut(cyl(4.6, RING_CB + 0.01, (hx, -y1r - 0.01, hz), (0, 1, 0)))     # counterbore for the M4 x 12 head
        gadd("Elevation pulley standoff", hex_prism(7.0, P.ELEV_STANDOFF, (hx, -yp, hz), (0, -1, 0)), "alu",
             bom="M4 x 10 mm hex coupling nut (standoff), 304 stainless", kind="cots",
             note="M4 x 8 from inside the cradle plate into one end, M4 x 12 through the ring (counterbored) into the other")
    gadd(f"Elevation pulley {P.ELEV_T[1]}T ring", ring.clean(), "print_d",
         bom=f"Elevation pulley {P.ELEV_T[1]}T HTD 9 mm ring (printed)", kind="print",
         note=f"PETG, 5 walls, 40% gyroid; a ring ({2 * RING_IN:.0f} mm bore) on 6 standoffs {P.ELEV_STANDOFF:.0f} mm off the "
              "right cradle plate; the axle passes through its open middle")
    sl = cyl(9.5, yb - 0.3 - yp, (0, -yp, 0), (0, -1, 0)).cut(hex_prism(12.9, yb - yp + 2, (0, -yp + 1, 0), (0, -1, 0)))
    gadd("Axle spacer right", sl, "print_d", bom="Axle spacer (printed)", kind="print",
         note="hex bore on the right stub, from the cradle plate to the inner bearing's inner race: locates the gun sideways")
    # every tube runs inside the core and drops out of its bottom just behind the pivot: each fill line from its
    # chamber's inlet elbow back between the chambers, then out beside the bottom one; the smoke line from the collar
    # back along the barrels' valley, through the mantlet and breech block, between the valves
    z_exit = -(zo + 4.0)
    exits = []
    for k, t in enumerate(fills):
        xd, yd = FILL_DOWN[k]
        pts = [t, V(xd, t.y, t.z), V(xd, yd, t.z), V(xd, yd, z_exit)]
        gadd(f"Gun tube {TAGS[k]}", _tube_path(pts), "tube", bom="DOT nylon tube 1/4 OD (ft)", kind="stock",
             note="inside the core; leaves the bottom behind the pivot")
        exits.append(pts[-1])
    xd, yd = SMOKE_DOWN
    xt = xv - 40.0                                           # crosses over beside the valves, where the reducers are clear
    pts = [V(xc - 7.5, SMOKE_Y, 0), V(xt, SMOKE_Y, 0), V(xt, yd, 0), V(xd, yd, 0), V(xd, yd, z_exit)]
    gadd("Gun smoke tube", _tube_path(pts, r=P.SMOKE_R), "tube", bom="Silicone tube 1/2 ID x 5/8 OD (ft)", kind="stock",
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
        f"chambers {CH_VOL[0] / 1000:.2f} L (top) and {CH_VOL[1] / 1000:.2f} L (bottom), barrels {P.GUN_GAP:.1f} mm apart")


GUN_EXITS, FOG_EXITS, BALANCE, CH_VOL = [], [], {}, [0.0, 0.0]


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
    return s.fuse(cyl(pd / 2 + 2.5, fl, (0, 0, 0), (0, 1, 0))).fuse(cyl(pd / 2 + 2.5, fl, (0, fl + w, 0), (0, 1, 0)))
