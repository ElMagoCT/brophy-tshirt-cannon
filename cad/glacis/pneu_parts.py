"""Recognisable pneumatic parts for the Onshape import (rev C.3): brass NPT fittings, push-to-connects, valves,
sensors and the rear manifold, each one light solid (no threads) placed by a point and an axis.

Placement: every builder makes its part along +Z in a local frame (+X is the 'up' or roll reference) and moves it
with place(p, d, up). Port-mounted parts (plug, push-to-connect, relief, transducer, M plug, tank boss) take `p` at
the port face and `d` pointing out of the port; their thread stub sits behind `p`. Inline parts (cross, tee, ball
valve, solenoid) take `p` at the body centre and `d` along the run or flow. Sizes are catalog-typical.

PURPOSE / purpose(name): one plain-English line per part, for each Onshape part's Description.
"""
import math
import cadquery as cq
from cadquery import Vector as V
from lib import cyl, tube, hex_prism, union

ENG = {"1/8": 6.7, "1/4": 10.2}                # thread engagement
OD = {"1/8": 10.29, "1/4": 13.72}              # male thread OD
TUBE_OD = 6.35                                 # 1/4 in DOT tube


def _perp(d):
    a = V(1, 0, 0) if abs(d.x) < 0.9 else V(0, 1, 0)
    return (a - d * a.dot(d)).normalized()


def place(shape, p, d, up=None):
    """Local part (built along +Z, roll reference +X) -> global, at p with +Z along d and +X toward up."""
    d = V(*d).normalized()
    x = _perp(d) if up is None else V(*up)
    x = (x - d * x.dot(d)).normalized()
    pl = cq.Plane(origin=V(*p), xDir=x, normal=d)
    return shape.transformShape(pl.rG)


def _ring(z, r, w, rin=0.0):
    return tube(r, rin, w, (0, 0, z)) if rin else cyl(r, w, (0, 0, z))


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _port(z, d=(0, 0, 1), size="1/4", depth=None):
    """Female port bore cutter starting at local point (0,0,z) going along d (into the body is -d)."""
    return cyl(OD[size] / 2 + 0.1, depth or ENG[size], (0, 0, z), d)


def _bossed(c2e, dirs, body_r=8.5, band=1.2, size="1/4"):
    """Forged brass body: a rounded core with a round boss (and end band) toward each direction in dirs."""
    core = cq.Solid.makeSphere(body_r + 1.5, V(0, 0, 0))
    parts = [core]
    for dd in dirs:
        dv = V(*dd).normalized()
        parts.append(cyl(body_r, c2e - band, (0, 0, 0), dv.toTuple()))
        parts.append(cyl(body_r + 0.8, band, (dv * (c2e - band)).toTuple(), dv.toTuple()))
    body = union(parts)
    for dd in dirs:
        dv = V(*dd).normalized()
        body = body.cut(cyl(OD[size] / 2 + 0.1, ENG[size], (dv * (c2e - ENG[size])).toTuple(), dv.toTuple()))
    return body


# ------------------------------------------------------------------ NPT fittings
def npt_cross(p, d, up, c2e=12.7, size="1/4"):
    """Brass cross: run along d (both ways), branches along +-up. p = centre."""
    s = _bossed(c2e, [(0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0)], size=size)
    return place(s, p, d, up)


def npt_tee(p, d, up, c2e=12.7, size="1/4"):
    """Brass tee: run along d (both ways), branch along +up. p = centre."""
    return place(_bossed(c2e, [(0, 0, 1), (0, 0, -1), (1, 0, 0)], size=size), p, d, up)


def street_elbow(p, d, d2, c2e=14.0, size="1/4"):
    """Brass 90 deg street elbow. p = corner centre; female leg toward d, male leg toward d2."""
    d, d2 = V(*d).normalized(), V(*d2).normalized()
    s = union([cq.Solid.makeSphere(8.0, V(0, 0, 0)), cyl(7.5, c2e, (0, 0, 0), (0, 0, 1)),
               cyl(8.3, 1.5, (0, 0, c2e - 1.5)), cyl(OD[size] / 2, c2e + ENG[size] - 2.0, (0, 0, 0), (1, 0, 0))])
    s = s.cut(_port(c2e - ENG[size])).cut(cyl(3.5, c2e + ENG[size], (0, 0, 0), (1, 0, 0)))
    return place(s, p, d, d2)


def close_nipple(p, d, length=22.2, size="1/4", hexed=True):
    """Hex (or plain close) nipple centred at p along d."""
    r = OD[size] / 2
    s = tube(r, 4.6, length, (0, 0, -length / 2))
    if hexed and length > 18:
        s = s.fuse(hex_prism(14.3, 5.0, (0, 0, -2.5)).cut(cyl(4.6, 6, (0, 0, -3))))
    return place(s, p, d)


def npt_plug(p, d, size="1/4"):
    """Hex-head plug in a port: thread behind p, hex head out along d."""
    s = cyl(OD[size] / 2, ENG[size], (0, 0, -ENG[size])).fuse(hex_prism(14.3, 6.0)).fuse(cyl(5.5, 1.0, (0, 0, 6.0)))
    return place(s, p, d)


def npt_bushing(p, d, male="1/4", female="1/8", hex_af=17.5):
    """Hex bushing in a port: male thread behind p, hex with the smaller female port out along d."""
    s = cyl(OD[male] / 2, ENG[male], (0, 0, -ENG[male])).fuse(hex_prism(hex_af, 6.0))
    return place(s.cut(_port(6.0 - ENG[female], size=female)), p, d)


def tank_boss(p, d, size="1/4"):
    """Weld bung on a tank shell: flange on the skin, a round boss, the female port opening along d."""
    s = cyl(11.0, 2.0, (0, 0, -2.0)).fuse(cyl(9.0, 10.0)).fuse(cyl(9.6, 1.2, (0, 0, 8.8)))
    return place(s.cut(_port(10.0 - ENG[size])), p, d)


# ------------------------------------------------------------------ push-to-connects
def _collet(z):
    return union([cyl(6.4, 4.0, (0, 0, z)), cyl(5.6, 2.5, (0, 0, z + 4.0))])


def ptc_straight(p, d, length=18.0):
    """Straight push-to-connect, 1/4 tube x 1/4 NPT: thread behind p, hex, body, release collet; tube bore."""
    s = union([cyl(OD["1/4"] / 2, ENG["1/4"], (0, 0, -ENG["1/4"])), hex_prism(14.3, 5.0),
               cyl(7.5, length - 11.5, (0, 0, 5.0)), _collet(length - 6.5)])
    return place(s.cut(cyl(TUBE_OD / 2 + 0.1, 12.0, (0, 0, length - 11.0))), p, d)


def ptc_elbow(p, d, out, reach=16.0):
    """Swivel elbow push-to-connect: thread behind p, hex, a swivel body up d, the tube leg toward out."""
    s = union([cyl(OD["1/4"] / 2, ENG["1/4"], (0, 0, -ENG["1/4"])), hex_prism(14.3, 4.0),
               cyl(7.0, 12.0, (0, 0, 4.0)), cq.Solid.makeSphere(7.0, V(0, 0, 13.0)),
               cyl(7.0, reach - 6.5, (0, 0, 13.0), (1, 0, 0)), _collet(0).rotate(V(0, 0, 0), V(0, 1, 0), 90).translate(
                   V(reach - 6.5, 0, 13.0))])
    s = s.cut(cyl(TUBE_OD / 2 + 0.1, 12.0, (reach - 9.0, 0, 13.0), (1, 0, 0)))
    return place(s, p, d, out)


# ------------------------------------------------------------------ valves
def ball_valve(p, d, up, lever_angle=0.0, stem_ext=0.0, length=45.0):
    """1/4 NPT brass ball valve, FNPT x FNPT. p = centre, d = flow, up = stem. lever_angle 0 = along the flow
    (open), 90 = across it (closed). stem_ext lengthens the stem (a panel-mount extension) before the lever."""
    hl = length / 2
    s = union([hex_prism(19.0, 11.0, (0, 0, -hl)), hex_prism(19.0, 11.0, (0, 0, hl - 11.0)),
               cyl(11.5, length - 18.0, (0, 0, -hl + 9.0)), cyl(6.0, 10.0, (0, 0, 0), (1, 0, 0))])
    s = s.cut(_port(-hl, (0, 0, 1))).cut(_port(hl - ENG["1/4"]))
    top = 10.0 + stem_ext                                  # stem (and any extension) out along +X (up)
    stem = cyl(3.0, top - 6.0 + 1.0, (6.0, 0, 0), (1, 0, 0))
    nut = hex_prism(8.0, 4.0, (top, 0, 0), (1, 0, 0))
    lever = _box(top + 1.0, top + 4.0, -6.0, 6.0, -6.0, 60.0).fuse(_box(top - 6.0, top + 4.0, -7.0, 7.0, 46.0, 62.0))
    lever = lever.rotate(V(0, 0, 0), V(1, 0, 0), lever_angle)   # flat bar along the flow when open
    return place(union([s, stem, nut, lever]), p, d, up)


def solenoid_02f(p, d, up, length=37.0):
    """2/2 NC solenoid valve, 1/4 NPT (Aignep 02F style): body (along d), armature tube and coil toward up, DIN
    connector off the coil's side. p = body centre."""
    hl = length / 2
    body = _box(-16.0, 14.0, -14.0, 14.0, -hl, hl).cut(_port(-hl, (0, 0, 1))).cut(_port(hl - ENG["1/4"]))
    s = union([body, cyl(6.0, 8.0, (14.0, 0, 0), (1, 0, 0)), cyl(15.0, 28.0, (20.0, 0, 0), (1, 0, 0)),
               hex_prism(12.0, 5.0, (48.0, 0, 0), (1, 0, 0)), _box(22.0, 46.0, 14.0, 32.0, -12.0, 12.0),
               cyl(5.0, 10.0, (34.0, 32.0, 0), (0, 1, 0))])
    return place(s, p, d, up)


def solenoid_gogo(p, d, up, plug=1):
    """In valve (Brophy Borealis, Micah via the Mac chat): GOGO GPG-M03 2/2 NC direct-acting, G1/4 both ends, from the
    seller drawing: brass body 40 along the flow x 26 across, port centre 9 above its bottom, 76 overall to the top
    nut, coil 38 wide, coil + DIN plug 82 long (24 from the valve centre to the coil's far side, 58 to the plug end).
    p = body centre on the port axis, d = flow, up = the coil; plug = which side the DIN plug points (+1 / -1)."""
    g = 6.6                                            # G1/4 male OD 13.16
    body = _box(-9.0, 17.0, -13.0, 13.0, -20.0, 20.0)
    for z0, dz in ((-20.0, 1), (20.0, -1)):
        body = body.cut(cyl(g + 0.1, 12.0, (0, 0, z0 - dz * 0.01), (0, 0, dz)))
    s = union([body, cyl(6.0, 4.0, (17.0, 0, 0), (1, 0, 0)), _box(21.0, 59.0, -24.0, 14.0, -15.0, 15.0),
               cyl(4.5, 4.0, (59.0, 0, 0), (1, 0, 0)), hex_prism(12.0, 4.0, (63.0, 0, 0), (1, 0, 0)),
               _box(27.0, 55.0, 14.0, 58.0, -13.0, 13.0)])
    if plug < 0:
        s = s.mirror("XZ")
    return place(s, p, d, up)


def hex_nipple_g(p, d):
    """G1/4 BSPP male x 1/4 NPT male hex nipple, 304: the G1/4 end (12 mm) behind p in the valve's port, a 19 mm hex at
    p, the 1/4 NPT end out along d (3.8 mm of it left showing when it's made up)."""
    s = union([cyl(6.58, 12.0, (0, 0, -12.0)), hex_prism(19.0, 8.0), cyl(OD["1/4"] / 2, 14.0, (0, 0, 8.0))])
    return place(s.cut(cyl(3.5, 40.0, (0, 0, -15.0))), p, d)


def relief_valve(p, d, length=44.0, ring=True):
    """Relief valve with a pull ring: thread behind p, hex, spring body, cap, ring on the stem. length = how far it
    stands out of the port."""
    body_l = max(8.0, length - 30.0)
    s = union([cyl(OD["1/4"] / 2, ENG["1/4"], (0, 0, -ENG["1/4"])), hex_prism(19.0, 7.0),
               cyl(9.5, body_l, (0, 0, 7.0)), cyl(7.0, 6.0, (0, 0, 7.0 + body_l)), cyl(1.6, 8.0, (0, 0, 13.0 + body_l))])
    if ring:
        z = 13.0 + body_l + 8.0 + 6.0
        s = s.fuse(cq.Solid.makeTorus(6.0, 1.4, V(0, 0, z), V(0, 1, 0))).fuse(cyl(1.6, 2.5, (0, 0, z - 7.4)))
    return place(s, p, d)


def check_valve(p, d, length=36.0):
    """Inline check valve FNPT x MNPT: female hex at p, round body with a flow arrow, male thread at the far end
    (flow along d)."""
    s = union([hex_prism(19.0, 12.0), cyl(9.0, length - 12.0 - ENG["1/4"], (0, 0, 12.0)),
               cyl(OD["1/4"] / 2, ENG["1/4"], (0, 0, length - ENG["1/4"]))])
    arrow = cq.Workplane("YZ").polyline([(-2.0, 14.0), (2.0, 14.0), (2.0, 20.0), (4.0, 20.0), (0, 25.0), (-4.0, 20.0),
                                         (-2.0, 20.0)]).close().extrude(10.0).val()
    s = s.fuse(arrow).cut(_port(0.0, depth=ENG["1/4"])).cut(cyl(3.5, length, (0, 0, 0)))
    return place(s, p, d)


def elbow_ff(p, d, d2, c2e=17.0, size="1/4"):
    """Brass 90 deg elbow, female both ends (rev D.2 fill line). p = corner centre; legs toward d and d2."""
    s = union([cq.Solid.makeSphere(8.5, V(0, 0, 0)), cyl(8.5, c2e, (0, 0, 0), (0, 0, 1)), cyl(8.5, c2e, (0, 0, 0), (1, 0, 0))])
    s = s.cut(_port(c2e - ENG[size])).cut(cyl(OD[size] / 2 + 0.1, ENG[size], (c2e - ENG[size], 0, 0), (1, 0, 0)))
    s = s.cut(cyl(3.5, c2e, (0, 0, 0), (0, 0, 1))).cut(cyl(3.5, c2e, (0, 0, 0), (1, 0, 0)))
    return place(s, p, d, d2)


def check_valve_mm(p, d, length=49.4):
    """Inline check valve MNPT x MNPT (American Made B076K8SLBZ): inlet thread tip at p, hex, round body with a flow
    arrow, outlet thread at the far end (flow along d)."""
    e = ENG["1/4"]
    s = union([cyl(OD["1/4"] / 2, e, (0, 0, 0)), hex_prism(19.0, 12.0, (0, 0, e)), cyl(9.0, length - 2 * e - 12.0, (0, 0, e + 12.0)),
               cyl(OD["1/4"] / 2, e, (0, 0, length - e))])
    arrow = cq.Workplane("YZ").polyline([(-2.0, 14.0), (2.0, 14.0), (2.0, 20.0), (4.0, 20.0), (0, 25.0), (-4.0, 20.0),
                                         (-2.0, 20.0)]).close().extrude(10.0).val().translate(V(0, 0, e + 8.0))
    s = s.fuse(arrow).cut(cyl(3.5, length + 1.0, (0, 0, -0.5)))
    return place(s, p, d)


def m_plug_f(p, d, length=28.0):
    """Industrial (M-style) coupler plug with a 1/4 FNPT body (Milton 728): the male thread it screws onto ends at p
    (behind p, inside the hex); the nipple with its locking groove points out along d."""
    e = ENG["1/4"]
    s = union([hex_prism(15.9, e + 5.0, (0, 0, -e - 1.0)), cyl(6.5, length - 14.0, (0, 0, 4.0)), cyl(4.7, 10.0, (0, 0, length - 10.0))])
    s = s.cut(cyl(OD["1/4"] / 2 + 0.1, e + 1.1, (0, 0, -e - 1.1))).cut(tube(7.0, 5.4, 2.0, (0, 0, length - 16.0)))
    s = s.cut(cyl(3.0, length + e + 4.0, (0, 0, -e - 2.0)))
    return place(s, p, d)


def m_plug(p, d, length=26.0):
    """Industrial (M-style) coupler plug: thread behind p, hex, the nipple with its locking groove out along d."""
    s = union([cyl(OD["1/4"] / 2, ENG["1/4"], (0, 0, -ENG["1/4"])), hex_prism(14.3, 6.0), cyl(6.5, length - 16.0, (0, 0, 6.0)),
               cyl(4.7, 10.0, (0, 0, length - 10.0))])
    s = s.cut(tube(7.0, 5.4, 2.0, (0, 0, length - 18.0))).cut(cyl(3.0, length + 2.0, (0, 0, -1.0)))
    return place(s, p, d)


def transducer(p, d, length=55.0, size="1/8", connector="packard"):
    """0.5-4.5 V pressure transducer: thread behind p, hex, steel body, connector at the far end."""
    s = union([cyl(OD[size] / 2, ENG[size], (0, 0, -ENG[size])), hex_prism(22.0, 8.0), cyl(10.0, length - 22.0, (0, 0, 8.0))])
    z = length - 14.0
    if connector == "packard":
        s = s.fuse(_box(-6.0, 6.0, -9.0, 9.0, z, length)).fuse(_box(-7.0, 7.0, -3.0, 3.0, z + 4.0, z + 10.0))
    else:                                      # M12
        s = s.fuse(cyl(7.5, 6.0, (0, 0, z))).fuse(cyl(6.0, 8.0, (0, 0, z + 6.0)))
    return place(s, p, d)


# ------------------------------------------------------------------ rear manifold
def manifold(p, d, up, stations, half_len=63.5, side=25.4, size="1/4", gap_merge=25.0):
    """A row of 1/4 NPT brass port blocks joined by hex close nipples, along d centred on p, inside a side x side
    section, half_len each way, with hex plugs on the open ends. stations: [(s, (dx, dy, dz)), ...] with s along d
    from p and each direction a port face normal (global). Ports closer than gap_merge share one block.
    Returns (solid, [(port face point, direction)]) in the order given."""
    d = V(*d).normalized()
    order = sorted(range(len(stations)), key=lambda i: stations[i][0])
    groups = []
    for i in order:
        s = stations[i][0]
        if groups and s - groups[-1][-1][0] < gap_merge:
            groups[-1].append((s, i))
        else:
            groups.append([(s, i)])
    h = side / 2
    parts, ports = [], [None] * len(stations)
    spans = []
    for g in groups:
        a = max(-half_len, g[0][0] - 11.0)
        b = min(half_len, g[-1][0] + 11.0)
        spans.append((a, b))
        c = p + d * ((a + b) / 2)
        blk = cq.Workplane("XY").box(side, side, b - a).edges("|Z").chamfer(1.5).val()
        blk = place(blk, c, d, up)
        for s, i in g:
            n = V(*stations[i][1]).normalized()
            q = p + d * s
            face = q + n * h
            blk = blk.cut(cyl(OD[size] / 2 + 0.1, ENG[size], (face - n * ENG[size]).toTuple(), n.toTuple()))
            ports[i] = (face, n)
        parts.append(blk)
    for (a0, b0), (a1, b1) in zip(spans, spans[1:]):
        L = a1 - b0
        if L > 0.5:
            parts.append(close_nipple(p + d * ((b0 + a1) / 2), d, L + 2 * ENG[size] - 1.0, hexed=L > 8.0))
    for end, sgn in ((spans[0][0], -1), (spans[-1][1], 1)):
        if abs(end) < half_len - 7.0:          # room for a plug inside the envelope
            parts.append(npt_plug(p + d * end, d * sgn))
    return union(parts), ports


# ------------------------------------------------------------------ what each part is for (Onshape Description)
PURPOSE = [   # (substring of the part name, purpose); first match wins, so specific names come first
    ("Rear manifold push-to-connect", "Takes a tank line into the rear manifold."),
    ("Rear manifold", "Joins both tanks, the fill port, the tank transducer, the tank relief and the main valve: the 200 psi hub."),
    ("Tank transducer", "PT1: reads tank pressure for the web UI and the safety node's 210 psi trip."),
    ("Tank relief valve", "Vents the tanks above 200 psi; pull its ring at the rear panel to dump them by hand."),
    ("Tank elbow push-to-connect", "Tank outlet: turns the tank's port into the 1/4 in line to the rear manifold."),
    ("Tank plug", "Plugs a tank port that isn't used."),
    ("Tank strap", "Cam strap holding the tank in its saddles."),
    ("Tank saddle", "Printed cradle the tank sits in."),
    ("Tank arm", "Aluminum arm carrying the tank saddles."),
    ("Tank post", "Upright that holds a tank arm off the inner rail."),
    ("Air tank", "Stores the shot air: 6 L at up to 200 psi, refilled from a shop compressor through the fill plug."),
    ("Fill plug", "Where the shop compressor's universal (M-style) coupler snaps on to fill the tanks."),
    ("Fill nipple", "Carries the fill line through the rear panel."),
    ("Fill elbow", "Turns the fill line behind the rear panel toward the manifold."),
    ("Fill check valve", "Lets air in from the fill plug but holds the tanks once the hose comes off."),
    ("Main valve lever", "Main valve handle outside the rear panel: up = open, across = closed."),
    ("Main valve elbow", "Turns the rear manifold's outlet into the main valve."),
    ("Main valve push-to-connect", "Line from the main valve forward to the valve cross."),
    ("Main valve", "Manual shut-off for both tanks: open all session, closed for transport and any work on the gun."),
    ("Valve cross push-to-connect", "Feed from the main valve into the valve cross."),
    ("Valve cross", "Splits the main valve's air to the two in valves and the line relief."),
    ("Line relief", "Protects the line between the main valve and the in valves: vents above 200 psi."),
    ("In valve A", "Meters air into the top cannon's chamber until PT2 reads its setpoint; closed, it isolates that chamber."),
    ("In valve B", "Meters air into the bottom cannon's chamber until PT3 reads its setpoint; closed, it isolates that chamber."),
    ("Tube main valve", "1/4 in DOT tube from the main valve to the valve cross."),
    ("Tube tank", "1/4 in DOT tube from a tank to the rear manifold."),
    ("Service loop", "Flexible 1/4 in line from an in valve up to its chamber; slack so the gun can elevate."),
    ("Gun tube", "1/4 in line inside the gun's core from the service loop to the chamber's fill push-to-connect."),
    ("fill push-to-connect", "Chamber inlet: the line from its in valve pushes in here."),
    ("relief 125 psi", "Chamber relief: vents this chamber above 125 psi; its ring is the hand bleed."),
    ("relief 200 psi", "Chamber relief: vents this chamber above 200 psi; its ring is the hand bleed."),
    ("transducer", "Chamber pressure sensor (PT2 top, PT3 bottom): the in valve meters against it."),
    ("port block", "Brass block on the back of the chamber: fill, relief and transducer ports."),
    ("cross 1/4", "Brass cross on the back of the chamber: fill, relief and transducer ports."),
    ("bushing", "Steps the chamber's 1 in end down to the 1/4 in fittings."),
    ("reducer", "Reducing coupling: the chamber's end cap, stepping down to the 1 in firing path."),
    ("chamber nipple", "Pipe: part of the chamber or its connection to the firing valve."),
    ("Firing valve", "Fires the cannon: opens to dump the chamber into the barrel."),
    ("nipple", "Close nipple joining the firing valve to the breech adapter."),
    ("Breech adapter", "Machined adapter: 1 in NPT from the valve to the barrel's spigot."),
    ("Barrel", "Polycarbonate barrel; smoke enters through six holes just ahead of the shirt."),
    ("Chamber cap", "Printed cap holding the chamber pipe down on its saddle."),
    ("Chamber saddle", "Printed block carrying both chambers between the cradle plates."),
]


def purpose(name):
    for key, text in PURPOSE:
        if key.lower() in name.lower():
            return text
    return ""
