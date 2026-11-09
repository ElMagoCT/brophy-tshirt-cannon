"""Printable desk mini of Glacis as a kit (1:9 by default; never under 1:10, a 2 in wheelbase): the body and the
gun, joined by a piece of 1.75 mm filament so the gun elevates like the real one, plus glue-in colour pieces (red
windows; black speakers, light bar and chambers). Slice with mini_3mf.py; how to print and assemble it is in
docs/glacis/mini_model.md.

    python mini.py               # build, check, write out/mini/*.stl, kit.json and previews
    python mini.py --scale 10    # 1:10 instead

Shape comes from the real model, not copied numbers:
  - body: body.body_solid() (side outline, tumbled walls, speaker notches) with the gun well cut from the mini gun's
    own 0-45 deg sweep (body.set_slot_profile), the bumper ring, the four wheels, and a pocket inside its frame member
    for every acrylic panel (body.panels_for, MEM_W in, acrylic corner radius); everything below the bumper is black;
  - gun: gun.build() parts, simplified to solids that print at this size (barrels, chambers, valves, cradle core,
    breech block, mantlet, smoke collar, muzzle ring), balanced on the same pivot.

Pivot: a 2.05 mm hole goes in through the left bearing block's outer face, through the gun's cradle core and stops
blind inside the right bearing block (PIN_WALL short of its outer face), so the filament can't come out the far side.
The bearing blocks stand in for the real printed ones and sit on the deck either side of the well; the gun's flat
cradle sides run CLEAR from them, so nothing pinches it. The gun balances on the pin like the real one, so it holds
any angle with light friction.
"""
import argparse
import json
import math
import os
import sys
import time

import cadquery as cq
from cadquery import Vector as V

import params as P
import body as B
import gun as G
import speakers as SPK
from lib import box, cyl, union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mini")

# all mini-scale sizes in printed mm
PIN_D = 2.05            # hole for 1.75 mm filament (Micah, 2026-11-08)
PIN_WALL = 1.6          # blind end: this much plastic left past the hole in the right bearing block
CLEAR = 0.4             # gap between the gun's cradle sides and the bearing blocks, per side
SWEEP_CLEAR = 0.8       # gun to well floor, over the whole swing
PANEL_POCKET = 0.8      # acrylic panels: pocket this deep in the frame colour, two 0.4 lines of red in it...
WINDOW_RECESS = 0.2     # ... whose face sits this far below the frame (the real 2.5 mm recess would vanish)
KIT_CLR = 0.15          # glue-in pieces: gap per side in their seats
LIGHT_SEAT = 0.6        # light bar sits this deep in its pocket in the front slant
PEG_D, PEG_L, PEG_CLR = 2.0, 2.5, 0.1   # peg on the cradle's back face into each chamber: diameter, length, clearance
SCALE = 9.0             # 1:N, the largest whose slowest plate is about 3 h on Ludicrous (mini_3mf.py --fit)
BORE_WALL = 1.0         # barrel wall left round the muzzle bore
BORE_DEPTH = 4.0
MIN_WHEELBASE = 2.0 * 25.4   # Micah: never smaller than a 2 in wheelbase (1:10)
FLAT = 0.4              # wheel bottoms flattened this much so they stand on the plate
BLOCK_R = 4.0           # bearing block: radius round the pin
BLOCK_OUT = 4.0         # ... and how far it stands outboard of the well wall, on the deck


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ gun (gun-local, real mm: origin on the pivot, +x down the barrels)
def _bb(name):
    hits = [p["shape"].BoundingBox() for p in G.LOCAL if p["name"].startswith(name)]
    assert hits, name
    return hits[0]


def gun_solid():
    G.build(log=lambda *a: None)
    parts = []
    # cradle core: the plates' side profile, solid between them (it reads as one block from outside)
    pl = _bb("Cradle plate left")
    x0, x1, zo = pl.xmin, pl.xmax, pl.zmax
    yw = pl.ymax
    pts = [(x0, -zo), (x1 - 20, -zo), (x1, -zo + 20), (x1, zo - 20), (x1 - 20, zo), (x0, zo)]
    core = cq.Workplane("XZ", origin=(0, yw, 0)).polyline(pts).close().extrude(2 * yw).val()
    parts.append(core)
    chambers = []                                           # printed black (where they show outside the core)
    rb = P.BARREL_OD / 2
    for k, tag in enumerate(G.TAGS):
        h = G.H[k]
        # valve as modelled (it's already solid); chamber as reducers + pipe + the 1/4 NPT port block behind
        parts.append(next(p["shape"] for p in G.LOCAL if p["name"].startswith(f"Firing valve {tag}")))
        for nm, r in ((f"{tag} chamber reducer 1x3", G.R_CH), (f"{tag} chamber reducer 3x1", G.R_CH),
                      (f"{tag} chamber nipple 3x", G.R_PIPE), (f"{tag} chamber nipple 1x", 16.7)):
            b = _bb(nm)
            chambers.append(cyl(r, b.xmax - b.xmin, (b.xmin, 0, h), (1, 0, 0)))
        b0, b1 = _bb(f"{tag} chamber port block"), _bb(f"{tag} chamber reducer 3x1")   # bushing + port block
        chambers.append(cyl(16.0, b1.xmin + 2.0 - b0.xmin, (b0.xmin, 0, h), (1, 0, 0)))
        b = _bb(f"Barrel {tag}")
        parts.append(cyl(rb, b.xmax - b.xmin, (b.xmin, 0, h), (1, 0, 0)))
    for nm in ("Breech block upper", "Breech block lower"):
        b = _bb(nm)
        parts.append(box(b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))
    # mantlet: the real loft's outer sections, filled
    m = _bb("Mantlet")
    mz0, mz1 = m.xmin, m.xmax
    W0, H0 = m.ymax - m.ymin + 2.0, m.zmax - m.zmin
    W1, H1 = P.BARREL_OD + 12.0, P.PITCH + P.BARREL_OD + 12.0
    secs = [(mz0, W0, H0, 16.0), (mz0 + 28.0, (W0 + W1) / 2 + 1.0, (H0 + H1) / 2 + 1.0, 30.0),
            (mz1 - 5.0, W1, H1, W1 / 2 - 1.0), (mz1, W1 - 6.0, H1 - 6.0, W1 / 2 - 4.0)]
    parts.append(cq.Solid.makeLoft([G._rrect(*s) for s in secs], False))
    for nm in ("Smoke collar", "Muzzle ring"):
        b = _bb(nm)
        W, Hh = b.ymax - b.ymin, b.zmax - b.zmin
        parts.append(G._rounded_prism(b.xmin, b.xmax - b.xmin, W, Hh, W / 2 - 0.5, edge=3.0))
    gun = union(parts + chambers).clean()
    return gun, union(chambers).cut(core).clean(), _bb("Barrel top").xmax, yw


def pose(shape, elev):
    return shape.rotate(V(0, 0, 0), V(0, 1, 0), -elev).translate(V(P.PIVOT[0], 0, P.PIVOT[1]))


def sweep_env(shape, margin, step=2.5):
    """Lowest world z the gun reaches at each 10 mm of x over the elevation range (as gun.sweep_profile)."""
    px, pz = P.PIVOT
    verts, tris = shape.tessellate(2.0, 0.5)
    vs = [(v.x, v.z) for v in verts]
    pts = list(vs)
    for tri in tris:
        for i0, i1 in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            (xa, za), (xb, zb) = vs[i0], vs[i1]
            n = int(math.hypot(xb - xa, zb - za) // 15.0)
            pts += [(xa + (xb - xa) * j / (n + 1), za + (zb - za) * j / (n + 1)) for j in range(1, n + 1)]
    env, a = {}, 0.0
    while a <= P.ELEV_RANGE[1] + 1e-6:
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        for x, z in pts:
            wx, wz = px + x * c - z * s_, pz + x * s_ + z * c
            kx = int(math.floor(wx / 10.0))
            env[kx] = min(env.get(kx, 1e9), wz)
        a += step
    return {k * 10.0: v - margin for k, v in env.items()}


# ------------------------------------------------------------------ body (world, real mm)
def _side(n):
    if n.y > 0.7:
        return "left"
    if n.y < -0.7:
        return "right"
    if n.z > 0.95:
        return "deck"
    return "front" if n.x > 0 else "rear"


def body_solid(gun, s, y_core):
    """The body as printed in place: {"main": white, "black": everything below the bumper (wheels, skid)}; the
    glue-in kit [dict(name, shape, colour, down)] (down: the world direction that goes on the print bed); the panel
    count; the bearing blocks' outer |y|."""
    B.set_slot_profile(sweep_env(gun, SWEEP_CLEAR / s))
    b = B.body_solid(notched=True)
    plain = B.body_solid(notched=False)
    kit = []
    # acrylic panels: a pocket inside each frame member; the red window glues in WINDOW_RECESS below the frame face
    n_pan = 0
    for fi in B.face_info(b):
        for poly in B.panels_for(fi):
            try:
                pocket = B.slab(poly, fi["n"], P.MEM_W, -1.0, 1.0 + PANEL_POCKET / s, R=P.ACRYLIC_R)
                win = B.slab(poly, fi["n"], P.MEM_W + KIT_CLR / s, WINDOW_RECESS / s,
                             (PANEL_POCKET - WINDOW_RECESS) / s, R=P.ACRYLIC_R)
                b = b.cut(pocket)
                n_pan += 1
                side = _side(fi["n"])
                c = win.Center()
                tag = side + (f" {'front' if c.x > P.SIDE_SPLIT_X else 'rear'}" if side in ("left", "right") else
                              f" {'left' if c.y > 0 else 'right'}" if side == "deck" else "")
                kit.append(dict(name=f"window {tag}", shape=win, colour="red", down=fi["n"]))   # outer face down
            except Exception as e:                       # a sliver face: leave it plain
                log(f"  panel skipped ({e.__class__.__name__})")
    # speakers: each corner notch takes a black block from its cup's back wall out to the grille face
    w, h, d = P.SPEAKER
    for pod in SPK.pods():
        h1 = h / 2 + P.SPK_CLEAR + P.SPK_WALL - KIT_CLR / s
        h2 = w / 2 + P.SPK_CLEAR + P.SPK_WALL - KIT_CLR / s
        fill = SPK._prism(pod["q"], pod["a"], pod["b1"], pod["b2"], h1, h2, P.SPK_WALL, d + 0.5 + P.SPK_GRILLE)
        kit.append(dict(name=f"speaker {pod['name'].split()[-1]}", shape=fill.intersect(plain), colour="black",
                        down=pod["a"] * -1))                                                      # back face down
    # front light bar (Zmoon 12 in): sits LIGHT_SEAT deep in a pocket in the front slant
    L, hb, db, zc, _ = P.LIGHT_BAR
    xf = P.front_x(zc - hb / 2) + 8.0
    bar = box(P.front_x(zc + hb / 2) - 30.0, xf + db, -L / 2, L / 2, zc - hb / 2, zc + hb / 2)
    bar = bar.cut(B.inner_solid(LIGHT_SEAT / s))
    b = b.cut(bar)
    kit.append(dict(name="light bar", shape=bar, colour="black", down=V(1, 0, 0)))             # front face down
    # bumper ring (foam + backing as one band) and a skid under the belly so it stands square
    bx, by = P.FRAME_X + P.BUMP_DEPTH, P.FW / 2 + P.BUMP_DEPTH
    bump = cq.Workplane("XY", origin=(0, 0, P.BUMP_Z[0])).rect(2 * bx, 2 * by).extrude(
        P.Z_WALL_BOT + 0.5 - P.BUMP_Z[0]).edges("|Z").fillet(25.0).val()
    f = FLAT / s
    parts = [b, bump, box(-P.AX_X + P.WHEEL_R * 0.2, P.AX_X - P.WHEEL_R * 0.2, -P.WHEEL_Y[0] + 4, P.WHEEL_Y[0] - 4,
                          f, P.BUMP_Z[0] + 1)]
    for sx in (1, -1):
        for sy in (1, -1):
            y0, y1 = sorted((sy * P.WHEEL_Y[0], sy * P.WHEEL_Y[1]))
            parts.append(cyl(P.WHEEL_R, y1 - y0, (sx * P.AX_X, y0, P.AXLE_Z), (0, 1, 0)))
    # bearing blocks: from the well floor up round the pin, from CLEAR off the gun's cradle side out past the well
    # wall onto the deck
    px, pz = P.PIVOT
    r = BLOCK_R / s
    y_in, y_out = y_core + CLEAR / s, P.Y_SLOT + BLOCK_OUT / s
    def block(sy, g=0.0):
        ya, yb = sorted((sy * y_in, sy * (y_out + g)))
        return box(px - r - g, px + r + g, ya, yb, pz - 160, pz).fuse(cyl(r + g, yb - ya, (px, ya, pz), (0, 1, 0)))
    for sy in (1, -1):
        parts.append(block(sy))
    keep_out = union([block(sy, KIT_CLR / s) for sy in (1, -1)])     # the deck windows notch round the blocks
    for kp in kit:
        if kp["name"].startswith("window deck"):
            kp["shape"] = kp["shape"].cut(keep_out).clean()
    body = union(parts).cut(box(-2000, 2000, -2000, 2000, -100, f)).clean()
    under = box(-2000, 2000, -2000, 2000, -100, P.BUMP_Z[0])         # everything below the bumper prints black
    cols = dict(main=body.cut(under).clean(), black=body.intersect(under).clean())
    return cols, kit, n_pan, y_out


def lay_flat(shape, down):
    """Rotate so `down` points at the bed, then sit it on z = 0, centred on x = y = 0."""
    dn, tgt = V(*down.toTuple()).normalized(), V(0, 0, -1)
    ax = dn.cross(tgt)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, dn.dot(tgt)))))
    if ax.Length < 1e-9:
        ax = V(1, 0, 0)
    out = shape.rotate(V(0, 0, 0), ax, ang) if ang > 1e-6 else shape
    bb = out.BoundingBox()
    return out.translate(V(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def export(shape, path):
    cq.exporters.export(cq.Workplane().add(shape), path, tolerance=0.02, angularTolerance=0.1)


# ------------------------------------------------------------------ build + checks
def build(scale, render_previews=True):
    s = 1.0 / scale
    t = time.time()
    gun, gun_black, x_muzzle, y_core = gun_solid()
    log(f"1:{scale:g}  gun simplified: {len(gun.Solids())} solid, cradle sides at y +/-{y_core:.1f}")
    cols, kit, n_pan, y_out = body_solid(gun, s, y_core)

    # muzzle bores (cosmetic)
    rb = P.BARREL_OD / 2
    for h in G.H:
        gun = gun.cut(cyl(rb - BORE_WALL / s, BORE_DEPTH / s + 1, (x_muzzle - BORE_DEPTH / s, 0, h), (1, 0, 0)))
    # chambers: black glue-ins, each butting on the cradle's back face with a peg into it
    gun_white = gun.cut(gun_black).clean()
    for k, h in enumerate(G.H):
        piece = union([c for c in gun_black.Solids() if abs(c.Center().z - h) < 30.0])
        xe = piece.BoundingBox().xmax                                  # the face against the cradle
        # peg on the cradle (prints sideways with the gun), hole in the chamber (it prints standing on that face)
        gun_white = gun_white.fuse(cyl(PEG_D / 2 / s, PEG_L / s + 0.5, (xe + 0.5, 0, h), (-1, 0, 0))).clean()
        piece = piece.cut(cyl((PEG_D / 2 + PEG_CLR) / s, (PEG_L + 0.3) / s + 0.1, (xe + 0.1, 0, h), (-1, 0, 0))).clean()
        kit.append(dict(name=f"chamber {G.TAGS[k]}", shape=piece, colour="black", down=V(1, 0, 0), gun=True))

    # to printed mm: body world frame at 1:N (wheels on z = 0); gun keeps its pivot at its own origin
    cols = {k: v.scale(s) for k, v in cols.items()}
    for kp in kit:
        kp["shape"] = kp["shape"].scale(s)
    gun_white, gun = gun_white.scale(s), gun.scale(s)
    px, pz = P.PIVOT[0] * s, P.PIVOT[1] * s
    zmin = min(v.BoundingBox().zmin for v in cols.values())
    cols = {k: v.translate(V(0, 0, -zmin)) for k, v in cols.items()}
    for kp in kit:
        if not kp.get("gun"):
            kp["shape"] = kp["shape"].translate(V(0, 0, -zmin))
    pz -= zmin
    # pin: in from the left block's outer face (+y), through the gun, blind in the right block
    y_left, y_right = y_out * s, -y_out * s
    y_end = y_right + PIN_WALL
    cols["main"] = cols["main"].cut(cyl(PIN_D / 2, y_left + 1 - y_end, (px, y_end, pz), (0, 1, 0))).clean()
    pin = cyl(PIN_D / 2, 2 * y_core * s + 2, (0, -y_core * s - 1, 0), (0, 1, 0))
    gun_white, gun = gun_white.cut(pin).clean(), gun.cut(pin).clean()
    pin_len = y_left - y_end

    def posed(sh, e):
        return sh.rotate(V(0, 0, 0), V(0, 1, 0), -e).translate(V(px, 0, pz))

    body_all = union(list(cols.values()) + [kp["shape"] for kp in kit if not kp.get("gun")])
    gun_all = union([gun_white] + [kp["shape"] for kp in kit if kp.get("gun")])

    # checks
    ok = True
    worst = 0.0
    for e in range(0, int(P.ELEV_RANGE[1]) + 1, 5):
        v = body_all.intersect(posed(gun_all, e)).Volume()
        worst = max(worst, v)
        if v > 1e-3:
            ok = False
            log(f"  CLASH at {e} deg: {v:.3f} mm3")
    log(f"sweep 0-{P.ELEV_RANGE[1]:.0f} deg: {'clear' if worst <= 1e-3 else 'CLASH'} (worst {worst:.4f} mm3)")
    for kp in kit:                                                    # every glue-in sits in its seat, not in the part
        home = gun_white if kp.get("gun") else cols["main"]
        v = home.intersect(kp["shape"]).Volume()
        if v > 1e-3:
            ok = False
            log(f"  {kp['name']} overlaps its seat by {v:.3f} mm3")
    bb_b, bb_g = body_all.BoundingBox(), gun_all.BoundingBox()
    log(f"body {bb_b.xlen:.1f} x {bb_b.ylen:.1f} x {bb_b.zlen:.1f} mm ({bb_b.xlen / 25.4:.2f} x {bb_b.ylen / 25.4:.2f} x "
        f"{bb_b.zlen / 25.4:.2f} in); gun {bb_g.xlen:.1f} long")
    g20 = posed(gun_all, P.ELEV_SHOW).BoundingBox()
    wb = 2 * P.AX_X * s
    log(f"assembled at {P.ELEV_SHOW:.0f} deg: {max(bb_b.xmax, g20.xmax) - min(bb_b.xmin, g20.xmin):.1f} long x "
        f"{max(bb_b.zmax, g20.zmax):.1f} tall mm; wheelbase {wb / 25.4:.2f} in")
    if wb < MIN_WHEELBASE - 1e-6:
        ok = False
        log(f"  wheelbase {wb:.1f} mm is under the {MIN_WHEELBASE:.1f} mm minimum")
    for nm, sh in (("body", cols["main"]), ("gun", gun_white)) + tuple((kp["name"], kp["shape"]) for kp in kit):
        if len(sh.Solids()) != 1:
            ok = False
            log(f"  {nm} is {len(sh.Solids())} pieces")
    body = cols["main"]
    blind = body.isInside(V(px, y_end - 0.5, pz)) and body.isInside(V(px, y_right + 0.3, pz))
    opens = not body.isInside(V(px, y_left - 0.3, pz)) and not body.isInside(V(px, y_end + 0.3, pz))
    opens &= not gun_white.isInside(V(0, 0, 0)) and gun_white.isInside(V(0, 0, PIN_D))
    ok &= blind and opens
    log(f"pin: {PIN_D} mm hole, open on the left block, blind {PIN_WALL} mm short of the right block's face; "
        f"cut the filament to {pin_len - 0.5:.1f} mm ({'ok' if blind and opens else 'WRONG'})")

    # export: every piece already in its print orientation
    os.makedirs(OUT, exist_ok=True)
    for fn in os.listdir(OUT):
        if fn.endswith(".stl"):
            os.remove(os.path.join(OUT, fn))
    export(body_all, os.path.join(OUT, "glacis_mini_body_all.stl"))           # one-colour body, for reference
    export(cols["main"], os.path.join(OUT, "body_white.stl"))
    export(cols["black"], os.path.join(OUT, "body_black.stl"))
    side = gun_white.rotate(V(0, 0, 0), V(1, 0, 0), -90)                      # gun on its side, pin hole vertical
    export(side.translate(V(0, 0, -side.BoundingBox().zmin)), os.path.join(OUT, "gun_white.stl"))
    manifest = []
    for kp in kit:
        fn = kp["name"].replace(" ", "_") + ".stl"
        flat = lay_flat(kp["shape"], kp["down"])
        bb = flat.BoundingBox()
        if max(bb.xlen, bb.ylen) > P.BED[0]:
            ok = False
            log(f"  {kp['name']} over the bed")
        export(flat, os.path.join(OUT, fn))
        manifest.append(dict(name=kp["name"], file=fn, colour=kp["colour"],
                             size=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 2)]))
    with open(os.path.join(OUT, "kit.json"), "w") as fh:
        json.dump(dict(scale=scale, pin_mm=round(pin_len - 0.5, 1), pieces=manifest), fh, indent=1)
    cq.exporters.export(cq.Workplane().add(body_all).add(posed(gun_all, P.ELEV_SHOW)),
                        os.path.join(OUT, "glacis_mini_assembled.step"))
    if render_previews:
        import render
        rgba = dict(main=(0.93, 0.93, 0.95, 1.0), red=(0.85, 0.12, 0.12, 1.0), black=(0.12, 0.12, 0.13, 1.0))
        for e in (0, P.ELEV_SHOW, P.ELEV_RANGE[1]):
            items = [(cols["main"], rgba["main"]), (cols["black"], rgba["black"]), (posed(gun_white, e), rgba["main"])]
            items += [(posed(kp["shape"], e) if kp.get("gun") else kp["shape"], rgba[kp["colour"]]) for kp in kit]
            render.draw(items, os.path.join(OUT, f"preview_{e:.0f}deg.png"), views=((22, -58), (12, -125)),
                        size=(6, 5), dpi=100)
    with open(os.path.join(OUT, "mini_log.txt"), "w") as fh:
        fh.write(f"scale 1:{scale:g}\nbody {bb_b.xlen:.1f} x {bb_b.ylen:.1f} x {bb_b.zlen:.1f} mm\n"
                 f"gun {bb_g.xlen:.1f} long\nsweep worst {worst:.4f} mm3\nkit pieces {len(kit)}\n"
                 f"pin hole {PIN_D} mm, filament {pin_len - 0.5:.1f} mm\nchecks {'clean' if ok else 'FAILED'}\n")
    log(f"{len(kit)} glue-in pieces; {'checks clean' if ok else 'CHECKS FAILED'}; wrote {OUT} in {time.time() - t:.0f} s")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=SCALE, help=f"1:N (default {SCALE:g})")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    return 0 if build(a.scale, not a.no_render) else 1


if __name__ == "__main__":
    sys.exit(main())
