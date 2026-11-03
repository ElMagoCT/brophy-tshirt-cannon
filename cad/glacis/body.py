"""Body: frosted acrylic panels recessed into a printed frame that follows every panel edge.

How the frame is made:
1. The body is a polyhedron: the side outline (x/z) extruded across the robot, intersected with the
   front-view trapezoid (side walls lean in by TUMBLE), minus the gun slot.
2. The frame is that solid shelled inward by MEM_H, open at the bottom, with a "window" cut through
   it wherever a panel shows (each panel inset by MEM_W). What stays is a network of members along every
   panel edge; their faces lie on the panel planes.
3. Each panel sits in a rebate REBATE_W wide and REBATE_D deep, CLIP_T below the outer face. A printed
   clip in a flush pocket at every convex panel corner holds it (one M3 into a heat-set insert), so any
   panel comes off with its clips. Two lights: a printed rail hangs inside each window edge, tilted toward
   the panel, and carries a closed 60/m strip loop about 1.25 in behind the panel, aimed across it (its back
   shades the next panel); and a rectangular tunnel down the middle of every member (outward of the tenons,
   so the joint screws miss it) takes a 100/m strip pushed in from a feed slot on the inside at each end,
   LEDs facing out, so the frame glows.
4. The network is split into printable pieces: a node block at every vertex and straight segments of
   at most PRINT_MAX along each edge, joined by tapered mortise-and-tenon joints with an M4 cross screw.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
import speakers as SPK
from lib import add, box, cyl, union

EPS = 1e-6


# ------------------------------------------------------------------ the body polyhedron
def _tumble_prism(inset):
    """Front-view trapezoid (walls leaning in by TUMBLE), inset perpendicular to the walls, extruded along x."""
    t = math.tan(math.radians(P.TUMBLE))
    y0 = P.Y_S - inset / math.cos(math.radians(P.TUMBLE))
    z0, z1 = P.Z_WALL_BOT - 200.0, 1500.0
    yb, yt = y0 + (P.Z_WALL_BOT - z0) * t, y0 - (z1 - P.Z_WALL_BOT) * t
    pts = [(-yb, z0), (yb, z0), (yt, z1), (-yt, z1)]
    return cq.Workplane("YZ", origin=(-2000, 0, 0)).polyline(pts).close().extrude(4000).val()


SLOT_PTS = []          # gun well side profile (x, z), set from the gun's swing by set_slot_profile()


def set_slot_profile(env, step=20.0):
    """Well floor from the gun's sweep envelope {x: lowest z}: flat where it meets the front and back
    faces, following the swing in between (the floor is open, so its facets carry no panels)."""
    px = P.PIVOT[0]
    xs = sorted(env)
    x_lo, x_hi = px - 290.0, px + 230.0
    z_r = min(env[x] for x in xs if x <= x_lo)
    z_f = min(env[x] for x in xs if x >= x_hi)
    mid = []
    x = x_hi
    while x >= x_lo - 1e-6:
        near = [env[q] for q in xs if abs(q - x) <= step]
        mid.append((x, min(near + [z_f if x > px else z_r])))
        x -= step
    SLOT_PTS[:] = [(3000.0, z_f)] + mid + [(-3000.0, z_r), (-3000.0, 4000.0), (3000.0, 4000.0)]
    return z_f, z_r


def slot_prism():
    return cq.Workplane("XZ", origin=(0, P.Y_SLOT, 0)).polyline(SLOT_PTS).close().extrude(2 * P.Y_SLOT).val()


def body_solid(notched=True):
    """The body polyhedron; notched=True also cuts the four speaker pockets out of the front-side corners."""
    pts = [(x, z) for x, z in P.SIDE_OUTLINE]
    prism = (cq.Workplane("XZ", origin=(0, -P.Y_S - 200, 0)).polyline(pts).close().extrude(-2 * P.Y_S - 400)).val()
    solid = prism.intersect(_tumble_prism(0.0)).cut(slot_prism())
    if notched and SPK.cuts():
        solid = solid.cut(union(SPK.cuts()))
    return solid.clean()


def _offset_outline(pts, d, bottom_drop):
    """Offset every edge of the (counter-clockwise in x/z? either) outline inward by d, except the
    closing bottom edge (last -> first), which moves down by bottom_drop so the shell stays open."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1                    # +1: counter-clockwise, interior on the left
    lines = []
    for i in range(n):
        (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % n]
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz)
        nx, nz = -dz / L * sgn, dx / L * sgn       # inward normal
        off = d if i < n - 1 else -bottom_drop
        lines.append(((x0 + nx * off, z0 + nz * off), (dx, dz)))
    out = []
    for i in range(n):
        (p, u), (q, v) = lines[i - 1], lines[i]
        den = u[0] * v[1] - u[1] * v[0]
        t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
        out.append((p[0] + u[0] * t, p[1] + u[1] * t))
    return out


def inner_solid(d=None):
    """The body offset inward by d (MEM_H), open at the bottom (OCC's shell() output breaks booleans)."""
    d = P.MEM_H if d is None else d
    ipts = _offset_outline(P.SIDE_OUTLINE, d, bottom_drop=40.0)
    prism = (cq.Workplane("XZ", origin=(0, -P.Y_S - 200, 0)).polyline(ipts).close().extrude(-2 * P.Y_S - 400)).val()
    return prism.intersect(_tumble_prism(d)).cut(slot_prism()).clean()


def face_info(solid):
    """Planar faces with outward normal and outer-wire vertices (3D)."""
    out = []
    for f in solid.Faces():
        n = f.normalAt()
        c = f.Center()
        verts = [v.toTuple() for v in f.outerWire().Vertices()]
        out.append(dict(face=f, n=n, c=c, verts=verts, area=f.Area()))
    return out


# ------------------------------------------------------------------ panels
def _plane_basis(n):
    n = n.normalized()
    a = V(0, 0, 1) if abs(n.z) < 0.9 else V(1, 0, 0)
    u = a.cross(n).normalized()
    w = n.cross(u).normalized()
    return u, w


def _clip(poly, a, b, c):
    """Keep the part of a 2D polygon where a*x + b*y + c >= 0 (Sutherland-Hodgman, one edge)."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= -EPS:
            out.append(p)
        if (fp >= -EPS) != (fq >= -EPS):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    clean = []
    for p in out:
        if not clean or math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-4:
            clean.append(p)
    if len(clean) > 1 and math.hypot(clean[0][0] - clean[-1][0], clean[0][1] - clean[-1][1]) < 1e-4:
        clean.pop()
    return clean


def _fits(poly3, n):
    """Does the polygon's in-plane bounding box fit an 18 x 36 in sheet (either way round)?"""
    u, w = _plane_basis(n)
    us = [V(*p).dot(u) for p in poly3]
    ws = [V(*p).dot(w) for p in poly3]
    a, b = sorted([max(us) - min(us), max(ws) - min(ws)])
    return a <= P.PANEL_MAX[0] and b <= P.PANEL_MAX[1]


def is_open_face(fi):
    """Gun well walls and floor (every face lying inside the well's width) and the speaker notches: left open,
    no panel."""
    if all(abs(v[1]) <= P.Y_SLOT + 0.5 for v in fi["verts"]):
        return True
    return any(all(c.isInside(V(*v), 0.6) for v in fi["verts"]) for c in SPK.cuts())


def panels_for(fi):
    """A body face as one panel; the side walls split at SIDE_SPLIT_X (their rear panels are the
    battery doors) and anything bigger than one sheet splits once (deck along y = 0)."""
    n = fi["n"]
    if n.z < -0.99 or is_open_face(fi):
        return []
    poly = list(fi["verts"])
    side_wall = abs(n.y) > 0.9
    if _fits(poly, n) and not side_wall:
        return [poly]
    out = []
    for sgn in (1, -1):
        part = _clip3(poly, 0, P.SIDE_SPLIT_X, sgn) if abs(n.y) > 0.9 else _clip3(poly, 1, 0.0, sgn)
        if len(part) >= 3:
            out.append(part)
    assert all(_fits(p, n) for p in out), "panel still too big after one seam"
    return out


def _clip3(poly, k, val, sgn):
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = sgn * (p[k] - val), sgn * (q[k] - val)
        if fp >= -EPS:
            out.append(p)
        if (fp >= -EPS) != (fq >= -EPS):
            t = fp / (fp - fq)
            out.append(tuple(p[j] + t * (q[j] - p[j]) for j in range(3)))
    clean = []
    for p in out:
        if not clean or max(abs(p[j] - clean[-1][j]) for j in range(3)) > 1e-4:
            clean.append(p)
    if len(clean) > 1 and max(abs(clean[0][j] - clean[-1][j]) for j in range(3)) < 1e-4:
        clean.pop()
    return clean


def _wp_on(poly3, n):
    """Workplane in the panel plane plus the 2D coordinates of the polygon."""
    o = V(*poly3[0])
    u, w = _plane_basis(n)
    pl = cq.Plane(origin=o, xDir=u, normal=n)
    pts = [((V(*p) - o).dot(u), (V(*p) - o).dot(w)) for p in poly3]
    return pl, pts


def slab(poly3, n, inset, depth0, thick):
    """Prism of the panel polygon inset in-plane by `inset`, from depth0 to depth0+thick inward."""
    pl, pts = _wp_on(poly3, n)
    pl2 = cq.Plane(origin=pl.origin - n * depth0, xDir=pl.xDir, normal=n)
    wp = cq.Workplane(pl2).polyline(pts).close()
    if inset:
        wp = cq.Workplane(pl2).add(wp.wires().val().offset2D(-inset, "intersection")).toPending()
    return wp.extrude(-thick).val()


# ------------------------------------------------------------------ build
def build(log=print):
    body = body_solid()
    FACES[:] = face_info(body)
    log(f"body: {len(body.Faces())} faces, volume {body.Volume() / 1e6:.1f} L")
    shell = body.cut(inner_solid()).clean()
    log(f"shell volume {shell.Volume() / 1e6:.2f} L, {len(shell.Solids())} solid")

    panels = []
    for fi in face_info(body):
        for poly in panels_for(fi):
            panels.append(dict(poly=poly, n=fi["n"]))
    log(f"{len(panels)} panels")

    frame = shell.cut(union([slab(p["poly"], p["n"], P.MEM_W, -1.0, P.MEM_H + 2.0) for p in panels])).clean()
    recess = []
    mark_shared_edges(panels)
    for p in panels:
        recess.append(slab(p["poly"], p["n"], P.MEM_W - P.REBATE_W, -1.0, P.REBATE_D + 1.0))
        p["clips"] = corner_clips(p)
        for c in p["clips"]:
            recess += [c["pocket"], c["insert"]]
    frame = frame.cut(union(recess)).clean()
    # panel light: the tilted rail round each window, then the frame tunnels (their feed slots cut through it)
    frame = frame.fuse(union([led_rail(p) for p in panels])).clean()
    loop = 0.0
    for p in panels:
        p["led"], length = led_loop(p)
        loop += length
    tunnels, frame_strips, frame_strip = strip_tunnels(panels, body.cut(inner_solid(P.TUNNEL_SKIN)))
    frame = frame.cut(union(tunnels)).clean()
    log(f"frame network volume {frame.Volume() / 1e6:.2f} L, {sum(len(p['clips']) for p in panels)} corner clips, "
        f"strip {loop / 1000:.1f} m in {len(panels)} panel loops + {frame_strip / 1000:.1f} m in {len(frame_strips)} frame tunnels")
    build.strips, build.tunnels, build.frame_strips = (loop, frame_strip), tunnels, frame_strips
    return body, frame, panels


def _rail_inset(d):
    """Inset from a shared panel edge of the rail's panel-side face at depth d (it leans toward the panel)."""
    return P.LED_RAIL_INSET[0] + (d - P.LED_LOOP[2]) * math.tan(math.radians(P.LED_RAIL[3]))


def mark_shared_edges(panels):
    """p["shared"][k]: edge k of the panel outline meets another panel at a corner (not coplanar)."""
    for i, p in enumerate(panels):
        poly = [V(*q) for q in p["poly"]]
        flags = []
        for k in range(len(poly)):
            a, b = poly[k], poly[(k + 1) % len(poly)]
            hit = False
            for j, o in enumerate(panels):
                if j == i or abs(o["n"].dot(p["n"])) > 0.99:
                    continue
                oq = [V(*q) for q in o["poly"]]
                for m in range(len(oq)):
                    c, d = oq[m], oq[(m + 1) % len(oq)]
                    cd = d - c
                    for f in (0.25, 0.5, 0.75):
                        x = a + (b - a) * f
                        t = max(0.0, min(1.0, (x - c).dot(cd) / cd.dot(cd)))
                        if (c + cd * t - x).Length < 0.5:
                            hit = True
            flags.append(hit)
        p["shared"] = flags


def _drafted(p, d0, d1, i0, radii):
    """Region behind the panel from depth d0 to d1, inside the outline inset by i0 at d0 (i0 is measured from
    shared edges; open and coplanar edges sit LED_RAIL_INSET[0] - [1] closer), drafted inward at the rail's lean
    as it goes deeper. Corners round off at the first radius in radii the outline can take. Returns
    (region(extra) -> solid inset a further `extra`, radius)."""
    pl, pts = _wp_on(p["poly"], p["n"])
    n = p["n"]
    pl2 = cq.Plane(origin=pl.origin - n * d0, xDir=pl.xDir, normal=n)
    outline = cq.Workplane(pl2).polyline(pts).close().wires().val()
    shared = p.get("shared") or [True] * len(pts)
    poly = [V(*q) - n * d0 for q in p["poly"]]
    gap = P.LED_RAIL_INSET[0] - P.LED_RAIL_INSET[1]
    for r in radii:                            # a narrow neck by a speaker notch can't take the full radius
        try:
            base = outline.offset2D(-(i0 + r - gap), "intersection")
            if len(base) != 1:
                continue
            # pull the shared edges in by the extra gap: cut a band along each out of the base face
            face = cq.Workplane(pl2).add(base[0]).toPending().extrude(-1.0).val()
            w = i0 + r
            for k, sh in enumerate(shared):
                if not sh:
                    continue
                a, b = poly[k], poly[(k + 1) % len(poly)]
                e = (b - a).normalized()
                t = _inward_dir(p, a + n * d0, b + n * d0)
                side = 1.0 if t.dot(n.cross(e)) > 0 else -1.0
                L = (b - a).Length + 2 * w
                plb = cq.Plane(origin=(a - e * w + n * 5.0).toTuple(), xDir=e.toTuple(), normal=n.toTuple())
                band = cq.Workplane(plb).polyline([(0, 0), (L, 0), (L, side * w), (0, side * w)]).close().extrude(-20.0).val()
                face = face.cut(band)
            sols = face.Solids()
            if len(sols) != 1:
                continue
            wire0 = max(sols[0].Faces(), key=lambda f: (f.Center() - pl2.origin).dot(n)).outerWire()

            def region(extra, wire0=wire0, r=r):
                wire = wire0.offset2D(r - extra, "arc")[0]
                return cq.Solid.extrudeLinear(wire, [], n * -(d1 - d0), taper=P.LED_RAIL[3])
            region(0.0)
            return region, r
        except Exception:
            continue
    raise ValueError("panel outline too narrow for its LED rail")


def led_rail(p):
    """Printed rail inside the window, leaning toward the panel's centre, hung from a flange on the member's inner
    face: a closed loop, so each panel's strip lights only its own panel."""
    t, d0, d1, _ = P.LED_RAIL
    region, p["rail_r"] = _drafted(p, d0, d1, _rail_inset(d0) - t, (P.LED_CORNER, 30.0, 20.0, 10.0, 2.0))
    rail = region(0.0).cut(region(t))
    inner, _ = _drafted(p, d0, d0 + 6.0, _rail_inset(d0) - t + 1.0, (p["rail_r"],))
    flange = slab(p["poly"], p["n"], P.MEM_W - 4.0, d0, 6.0).cut(inner(0.0))
    return rail.fuse(flange)


def led_loop(p):
    """Simplified 60/m strip stuck to the rail's panel-side face, LEDs aimed across the panel and slightly at it;
    its corners follow the rail face's (shrinking) corner radius exactly."""
    w, th, dc = P.LED_LOOP
    t, r0 = P.LED_RAIL[0], P.LED_RAIL[1]
    h = w / 2 * math.cos(math.radians(P.LED_RAIL[3]))
    if "rail_r" not in p:
        led_rail(p)
    r = max(0.5, p["rail_r"] - t - (dc - h - r0) * math.tan(math.radians(P.LED_RAIL[3])))
    region, _ = _drafted(p, dc - h, dc + h, _rail_inset(dc - h), (r,))
    ring = region(0.0).cut(region(th))
    pl, pts = _wp_on(p["poly"], p["n"])
    wire = cq.Workplane(pl).polyline(pts).close().wires().val().offset2D(-P.LED_RAIL_INSET[1], "intersection")[0]
    return ring, sum(e.Length() for e in wire.Edges())


def _bar(o, e, u, w, length, w0, w1, u0, u1):
    """Box from o along e for length, spanning w0..w1 along w and u0..u1 along u (Plane yDir = e x w = -u)."""
    pl = cq.Plane(origin=o, xDir=w, normal=e)
    pts = [(w0, -u0), (w1, -u0), (w1, -u1), (w0, -u1)]
    return cq.Workplane(pl).polyline(pts).close().extrude(length).val()


def strip_tunnels(panels, skin):
    """Frame light: a rectangular tunnel down the middle of every member, TUNNEL_GAP outward of the tenon line so
    the joint screws stop short of it, and a feed slot from the inside at each end where the strip goes in and
    the next edge's strip is joined. Slots and tunnel ends are trimmed TUNNEL_SKIN under every outer face and
    kept out of every joint. Also returns a simplified strip lying on each tunnel's inner wall, LEDs out."""
    tw, th = P.TUNNEL
    s0, s1 = P.FEED
    cuts, strips, total = [], [], 0.0
    # keep slots out of every joint: tenon, mortise and the screw boss inward of them
    keep = []
    for ed in edges_of(panels):
        a, b = ed["a"], ed["b"]
        e, u, w = _axes(ed, panels)
        for t in _joint_ts((b - a).Length):
            at = a + (b - a) * t
            c = _core_point(ed, panels, at)
            c = c - e * e.dot(c - at)
            keep.append(_bar(c - e * 14.5, e, u, w, 29.0, -5.5, 5.5, -5.5, 30.0))
    skin = skin.fuse(union(keep))
    for k, ed in enumerate(edges_of(panels)):
        a, b = ed["a"], ed["b"]
        L = (b - a).Length
        if L < 2 * s1 + 30.0:
            continue
        e, u, w = _axes(ed, panels)
        c = _core_point(ed, panels, a) - u * P.TUNNEL_GAP
        c = c - e * e.dot(c - a)
        tun = _bar(c + e * s0, e, u, w, L - 2 * s0, -tw / 2, tw / 2, -th / 2, th / 2)
        fa = _bar(c + e * s0, e, u, w, s1 - s0, -tw / 2, tw / 2, -th / 2, 45.0)
        fb = _bar(c + e * (L - s1), e, u, w, s1 - s0, -tw / 2, tw / 2, -th / 2, 45.0)
        cuts += [x.cut(skin) for x in (tun, fa, fb)]
        ws, ts = P.FRAME_STRIP
        strip = _bar(c + e * (s1 + 10.0), e, u, w, L - 2 * s1 - 20.0, -ws / 2, ws / 2, th / 2 - ts, th / 2).intersect(cuts[-3])
        strips.append((f"E{k:02d}", strip))
        total += L - 2 * s0
    return cuts, strips, total


def corner_clips(p):
    """Printed clip in a flush pocket at every convex corner of the panel outline: a corner plate with a straight
    chamfer across the panel corner, legs CLIP_LEG along the frame, one M3 into a heat-set insert. A battery door
    keeps only its bottom clips (they act as hooks) and gets a quarter-turn latch at the middle of its top edge:
    turn it, tip the door out from the top and lift it off the hooks."""
    n = p["n"]
    door = abs(n.y) > 0.9 and max(q[0] for q in p["poly"]) < P.SIDE_SPLIT_X + 1
    zmid = sum(q[2] for q in p["poly"]) / len(p["poly"])
    pl, pts = _wp_on(p["poly"], n)
    reb = P.MEM_W - P.REBATE_W
    w = cq.Workplane(pl).polyline(pts).close().wires().val().offset2D(-reb, "intersection")[0]
    edges = [e for e in w.Edges()]
    corners, ks = [], []
    for v in w.Vertices():
        c = V(v.X, v.Y, v.Z)
        adj = [e for e in edges if min((V(*x.toTuple()) - c).Length for x in (e.startPoint(), e.endPoint())) < 1e-3]
        if len(adj) != 2:
            continue
        dirs = []
        for e in adj:
            a, b = V(*e.startPoint().toTuple()), V(*e.endPoint().toTuple())
            o = b if (a - c).Length < 1e-3 else a
            dirs.append((o - c).normalized())
        bis = dirs[0] + dirs[1]
        if bis.Length < 1e-6:
            continue
        bis = bis.normalized()
        mid = c + bis * 3.0                           # convex corner: a point just inside lies in the panel
        inside = slab(p["poly"], n, reb, 0.0, 1.0).isInside(mid - n * 0.5, 0.1)
        if not inside:
            continue
        cos_h = dirs[0].dot(bis)
        sin_h = max(0.2, math.sqrt(max(0.0, 1 - cos_h ** 2)))
        k = c - bis * ((reb - 4.0) / sin_h)          # corner of the clip's outline, 4 mm in from the face edges
        if door and k.z > zmid:
            continue                                  # the latch holds the door's top
        ks.append((k, bis, cos_h, sin_h))
    for k, bis, cos_h, sin_h in ks:
        gap = min([(k - k2).Length for k2, *_ in ks if k2 is not k] + [1e9])
        leg = min(P.CLIP_LEG, gap / 2 - 2.0)          # never into the next corner's clip
        reach = max(leg * cos_h, (reb - 4.0) / sin_h + 6.0)   # chamfer line, at least 6 mm past the panel
        ctr = k + bis * (4.0 / sin_h)                 # screw 8 mm in from both face edges

        def plate(r, i, d0, d1):
            half = cq.Workplane(cq.Plane(origin=k + n * 1.0, xDir=bis, normal=n)).polyline(
                [(r, -150), (r, 150), (r - 300, 150), (r - 300, -150)]).close().extrude(-(d1 + 1.0)).val()
            return slab(p["poly"], n, i, d0, d1 - d0).intersect(half)

        near = cyl(min(reach / cos_h + 4.0, gap / 2 - 1.0), 40.0, (k + n * 20.0).toTuple(), (n * -1).toTuple())   # own corner only
        clip = plate(reach, 4.0, 0.0, P.CLIP_T).intersect(near).cut(cyl(1.7, 10, (ctr + n).toTuple(), (n * -1).toTuple()))
        pocket = plate(reach + 0.2, 3.8, -1.0, P.CLIP_T).intersect(near)
        insert = cyl(2.0, 6.0, (ctr - n * (P.CLIP_T - 0.1)).toTuple(), (n * -1).toTuple())
        corners.append(dict(clip=clip, pocket=pocket, insert=insert))
    if door:
        corners.append(_door_latch(p))
    return corners


def _door_latch(p):
    """Quarter-turn latch: a printed tab on an M4 pivot 10 mm in from the door's top edge, across the panel's
    edge when locked; turn it 90 deg to open."""
    n = p["n"]
    poly = [V(*q) for q in p["poly"]]
    edges = [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
    a, b = max(edges, key=lambda e: e[0].z + e[1].z)
    e = (b - a).normalized()
    t = n.cross(e).normalized()
    m = (a + b) * 0.5
    if sum((q - m).dot(t) for q in poly) < 0:
        t = t * -1                                    # t points down the door, into the panel
    piv = m + t * 10.0

    def tab(x0, x1, w, d0, d1):
        pl = cq.Plane(origin=(piv - n * d0).toTuple(), xDir=t.toTuple(), normal=n.toTuple())
        return cq.Workplane(pl).center((x0 + x1) / 2, 0).rect(x1 - x0, 2 * w).extrude(-(d1 - d0)).val()

    clip = tab(-6.0, 18.0, 8.0, 0.0, P.CLIP_T).cut(cyl(2.2, 10, (piv + n).toTuple(), (n * -1).toTuple()))
    pocket = tab(-6.3, 18.3, 8.3, -1.0, P.CLIP_T)
    insert = cyl(2.6, 6.0, (piv - n * (P.CLIP_T - 0.1)).toTuple(), (n * -1).toTuple())
    return dict(clip=clip, pocket=pocket, insert=insert, latch=True)


# ------------------------------------------------------------------ edges of the panel network
def _key(p):
    return tuple(round(c, 2) for c in p)


def edges_of(panels):
    """Unique straight edges (split at every vertex lying on them) with their adjacent panels."""
    verts = {}
    for p in panels:
        for v in p["poly"]:
            verts[_key(v)] = V(*v)
    out = {}
    for i, p in enumerate(panels):
        poly = p["poly"]
        for j in range(len(poly)):
            a, b = V(*poly[j]), V(*poly[(j + 1) % len(poly)])
            d = b - a
            L = d.Length
            if L < 1e-6:
                continue
            ts = [0.0, 1.0]
            for v in verts.values():
                t = (v - a).dot(d) / (L * L)
                if 1e-4 < t < 1 - 1e-4 and ((a + d * t) - v).Length < 0.05:
                    ts.append(t)
            ts.sort()
            for t0, t1 in zip(ts, ts[1:]):
                pa, pb = a + d * t0, a + d * t1
                k = tuple(sorted([_key(pa.toTuple()), _key(pb.toTuple())]))
                e = out.setdefault(k, dict(a=V(*k[0]), b=V(*k[1]), panels=set()))
                e["panels"].add(i)
    return list(out.values())


def _inward_dir(panel, a, b):
    """Unit vector in the panel plane, perpendicular to edge ab, pointing into the panel (point-in-polygon
    test, so it also works on the U-shaped front panel whose centroid lies in the gun slot)."""
    n = panel["n"]
    e = (b - a).normalized()
    t = n.cross(e).normalized()
    pl, pts = _wp_on(panel["poly"], n)
    q = (a + b) * 0.5 + t * 2.0 - pl.origin
    if not _pip((q.dot(pl.xDir), q.dot(pl.yDir)), pts):
        t = t * -1
    return t


def _pip(p, poly):
    x, y = p
    inside = False
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _section_prism(edge, panels, t0, t1, margin=0.6):
    """Region covering this edge's member between parameters t0..t1 (fractions of the edge)."""
    a, b = edge["a"], edge["b"]
    d = b - a
    e = d.normalized()
    pa, pb = a + d * t0, a + d * t1
    regs = []
    for i in edge["panels"]:
        p = panels[i]
        n, t = p["n"], _inward_dir(p, a, b)
        o = pa - t * margin + n * margin
        L = (pb - pa).Length
        pl = cq.Plane(origin=o, xDir=t, normal=e)
        w = max(P.MEM_W, _rail_inset(P.LED_RAIL[2])) + 2 * margin   # the member plus its LED rail (and its flange)
        h = P.LED_RAIL[2] + 2 * margin
        pts = []                                   # in-plane t (0..w) x inward -n (0..h)
        for (u, v) in [(0, 0), (w, 0), (w, h), (0, h)]:
            q = o + t * u - n * v
            pts.append(((q - o).dot(pl.xDir), (q - o).dot(pl.yDir)))
        r = cq.Workplane(pl).polyline(pts).close().extrude(L).val()
        regs.append(r)
    ps = [panels[i] for i in edge["panels"]]
    if len(ps) == 2 and abs(ps[0]["n"].dot(ps[1]["n"])) < 0.99:
        # the square between the two members' depths: needed at concave (inside) corners
        nA, nB = ps[0]["n"], ps[1]["n"]
        h = P.MEM_H + margin
        corner = [pa + nA * margin + nB * margin, pa - nA * h + nB * margin,
                  pa - nA * h - nB * h, pa + nA * margin - nB * h]
        pl = cq.Plane(origin=pa, xDir=(corner[1] - corner[0]).normalized(), normal=e)
        pts = [((q - pa).dot(pl.xDir), (q - pa).dot(pl.yDir)) for q in corner]
        regs.append(cq.Workplane(pl).polyline(pts).close().extrude((pb - pa).Length).val())
    return union(regs)


FACES = []          # body faces, set by build(): single-panel members look up the open face beside them


def _open_angle(edge, p):
    """cos, sin of the interior angle between a single-panel member's panel and the open face (bottom, gun
    well) along the same edge."""
    a, b = edge["a"], edge["b"]
    for f in FACES:
        m = f["n"]
        if abs(m.dot(p["n"])) > 0.999:
            continue
        if abs((a - f["c"]).dot(m)) < 0.2 and abs((b - f["c"]).dot(m)) < 0.2:
            c = max(-1.0, min(1.0, -m.dot(p["n"])))
            return c, math.sqrt(1 - c * c)
    return 0.0, 1.0


def _core_point(edge, panels, at, depth=None):
    """A point deep in the member's cross-section, clear of the light tunnel. On a single-panel
    member it moves in from the edge until a tenon there keeps 2 mm of wall to an acute open face."""
    depth = P.CORE_DEPTH if depth is None else depth
    a, b = edge["a"], edge["b"]
    ps = [panels[i] for i in edge["panels"]]
    if len(ps) == 1:
        p = ps[0]
        c, s = _open_angle(edge, p)
        h = P.TENON[0] / 2
        inset = max(7.0, h + (2.0 + (P.CORE_DEPTH + h) * c) / max(s, 0.3))
        return at + _inward_dir(p, a, b) * inset - p["n"] * depth
    n1, n2 = ps[0]["n"], ps[1]["n"]
    c = max(-0.3, min(1.0, n1.dot(n2)))
    k = depth / (1 + c)
    return at - n1 * k - n2 * k


def _axes(edge, panels):
    a, b = edge["a"], edge["b"]
    e = (b - a).normalized()
    ps = [panels[i] for i in edge["panels"]]
    nav = V(0, 0, 0)
    for p in ps:
        nav = nav + p["n"]
    u = (nav * -1).normalized()                    # inward
    u = (u - e * u.dot(e)).normalized()
    w = e.cross(u).normalized()
    return e, u, w


def _frustum(base_c, e, u, w, size, length, taper):
    """Tapered square tenon from base centre along e."""
    s0, s1 = size / 2, size / 2 - taper
    pts0 = [base_c + u * a + w * b for a, b in ((-s0, -s0), (s0, -s0), (s0, s0), (-s0, s0))]
    tip = base_c + e * length
    pts1 = [tip + u * a + w * b for a, b in ((-s1, -s1), (s1, -s1), (s1, s1), (-s1, s1))]
    w0 = cq.Wire.makePolygon([p for p in pts0], close=True)
    w1 = cq.Wire.makePolygon([p for p in pts1], close=True)
    return cq.Solid.makeLoft([w0, w1], True)


def _joint_ts(L, seg_max=215.0):
    """Edge parameters of the cuts between a member's node ends and its straight segments ([] if none). Short
    edges (round the speaker notches) set back less, so their node ends don't merge into one oversize piece."""
    setback = min(P.NODE_SETBACK, max(14.0, (L - 30.0) / 2))
    s = setback / L
    m = L - 2 * setback
    if m < 20:
        return []
    n = max(1, math.ceil(m / seg_max))
    return [s + (1 - 2 * s) * k / n for k in range(n + 1)]


def section(frame, panels, log=print, seg_max=215.0):
    """Split the frame network into printable pieces with tapered mortise-tenon joints."""
    edges = edges_of(panels)
    log(f"{len(edges)} edges")
    regions, joints = [], []          # regions: (name, solid); joints: (seg_index, end, edge, point, outward dir)
    for ei, ed in enumerate(edges):
        ts = _joint_ts((ed["b"] - ed["a"]).Length, seg_max)
        n = len(ts) - 1
        for k in range(n):
            idx = len(regions)
            regions.append((f"E{ei:02d}S{k}", _section_prism(ed, panels, ts[k], ts[k + 1]), ed, ts[k], ts[k + 1]))
    # each segment takes the frame inside its region minus the regions before it (only those it touches);
    # the nodes are what is left after cutting every region out one at a time (one big fused region made
    # OCC drop parts of the oblique front-slant edges)
    pieces, done = [], []
    for name, reg, ed, t0, t1 in regions:
        piece = frame.intersect(reg)
        rb = reg.BoundingBox()
        for prev in done:
            pb = prev.BoundingBox()
            if rb.xmin < pb.xmax and pb.xmin < rb.xmax and rb.ymin < pb.ymax and pb.ymin < rb.ymax and \
                    rb.zmin < pb.zmax and pb.zmin < rb.zmax:
                piece = piece.cut(prev)
        done.append(reg)
        sol = [s for s in piece.Solids() if s.Volume() > 50]
        if not sol:
            continue
        pieces.append(dict(name=name, shape=cq.Compound.makeCompound(sol) if len(sol) > 1 else sol[0],
                           edge=ed, t0=t0, t1=t1))
    rest = frame
    for reg in done:
        rest = rest.cut(reg)
    nodes = [s for s in rest.Solids() if s.Volume() > 50]
    split = 0
    for k, s in enumerate(nodes):
        parts = _split_to_bed(s)
        split += len(parts) - 1
        for j, part in enumerate(parts):
            pieces.append(dict(name=f"N{k:02d}" + (chr(97 + j) if len(parts) > 1 else ""), shape=part, edge=None, t0=None,
                               t1=None))
    log(f"{len(pieces)} pieces ({len(nodes)} nodes, {split} extra glued splits to fit the bed)")
    return pieces, edges


def _split_to_bed(s, bed=245.0):
    """Halve a node along its longest side until it fits the bed (the nodes round the speaker pockets join up
    into one big piece); the halves are glued."""
    bb = s.BoundingBox()
    dims = sorted([bb.xlen, bb.ylen, bb.zlen])
    if dims[1] <= bed and dims[2] <= 330.0:
        return [s]
    k = max(range(3), key=lambda i: (bb.xlen, bb.ylen, bb.zlen)[i])
    c = bb.center
    lo = [bb.xmin - 1, bb.ymin - 1, bb.zmin - 1]
    hi = [bb.xmax + 1, bb.ymax + 1, bb.zmax + 1]
    out = []
    for half in ((lo[k], c.toTuple()[k]), (c.toTuple()[k], hi[k])):
        a, b = list(lo), list(hi)
        a[k], b[k] = half
        cut = s.intersect(box(a[0], b[0], a[1], b[1], a[2], b[2]))
        for sol in cut.Solids():
            if sol.Volume() > 50:
                out += _split_to_bed(sol, bed)
    return out


def add_joints(pieces, panels, log=print):
    """Tapered tenon on each segment end, mortise + M4 cross-screw hole in its neighbour."""
    tw, th, tl, tt = P.TENON
    ok = skipped = 0
    shapes = {p["name"]: p["shape"] for p in pieces}
    for p in pieces:
        ed = p["edge"]
        if ed is None:
            continue
        a, b = ed["a"], ed["b"]
        d = b - a
        e, u, w = _axes(ed, panels)
        for end, t in (("lo", p["t0"]), ("hi", p["t1"])):
            at = a + d * t
            out = e * (-1 if end == "lo" else 1)
            core = _core_point(ed, panels, at)
            core = core - e * e.dot(core - at)            # on the cut plane
            # neighbour = the piece that contains a point just past the cut
            probe = core + out * 4.0
            nb = next((q for q in pieces if q is not p and q["shape"].isInside(probe, 0.1)), None)
            if nb is None:
                skipped += 1
                continue
            # lower segment on an edge owns the tenon between two segments
            if nb["edge"] is ed and end == "lo":
                continue
            def fits(size, length, taper):        # tested 0.3 mm off the joint plane: coincident faces upset OCC
                t_ = _frustum(core + out * 0.3, out, u, w, size, length - 0.3, taper)
                return t_.intersect(shapes[nb["name"]]).Volume() >= 0.95 * t_.Volume()
            size, length, taper = tw, tl, tt
            ten = _frustum(core, out, u, w, size, length, taper)
            if not fits(size, length, taper):
                size, length, taper = 5.0, 10.0, 0.4
                ten = _frustum(core, out, u, w, size, length, taper)
                if not fits(size, length, taper):
                    skipped += 1
                    continue
            mort = _frustum(core - out * 0.01, out, u, w, tw + 2 * P.TENON_CLEAR, tl + 0.5, tt)
            mid = core + out * (tl / 2)
            clear_h = cyl(2.25, 45, (mid - u * 2).toTuple(), u.toTuple())
            pilot = cyl(1.65, 45, (mid - u * 3).toTuple(), u.toTuple())
            # the fused tenon starts 0.5 mm inside its own piece: OCC doesn't always merge solids that only touch
            root = _frustum(core - out * 0.5, out, u, w, size, length + 0.5, taper)
            shapes[p["name"]] = shapes[p["name"]].fuse(root).cut(pilot).clean()
            shapes[nb["name"]] = shapes[nb["name"]].cut(mort.fuse(ten)).cut(clear_h).clean()
            ok += 1
    for p in pieces:
        p["shape"] = shapes[p["name"]]
    log(f"joints: {ok} tapered tenons with M4 cross screws, {skipped} ends without a neighbour piece")
    return ok


if __name__ == "__main__":
    import time
    t = time.time()
    body, frame, panels = build()
    pieces, edges = section(frame, panels)
    add_joints(pieces, panels)
    big = []
    for p in pieces:
        bb = p["shape"].BoundingBox()
        dims = sorted([bb.xlen, bb.ylen, bb.zlen])
        if dims[1] > 250:
            big.append((p["name"], [round(x) for x in dims]))
    print("pieces over the bed:", big)
    print(f"{time.time() - t:.1f} s")
