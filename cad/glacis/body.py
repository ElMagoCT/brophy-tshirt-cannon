"""Body: frosted acrylic panels recessed into a printed frame that follows every panel edge.

How the frame is made:
1. The body is a polyhedron: the side outline (x/z) extruded across the robot, intersected with the
   front-view trapezoid (side walls lean in by TUMBLE), minus the gun slot.
2. The frame is that solid shelled inward by MEM_H, open at the bottom, with a "window" cut through
   it wherever a panel shows (each panel inset by MEM_W). What stays is a network of members along every
   panel edge; their faces lie on the panel planes.
3. Each panel sits in a rebate REBATE_W wide and REBATE_D deep, CLIP_T below the outer face. A printed
   clip in a flush pocket at every convex panel corner holds it (one M4 into a heat-set insert where the
   acrylic's rounded corner leaves room), so any panel comes off with its clips. Windows, acrylic and clips
   all have rounded corners. Two lights: a printed rail hangs just behind each window edge and carries a
   closed 60/m strip loop 1.15 in behind the panel, aimed across it (leaning toward it along the straight runs,
   square at the corners); and a rectangular tunnel down the middle of every member (outward of the tenons,
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
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.TopAbs import TopAbs_REVERSED

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


FRONT_CUT = [None]


def front_cut():
    """Height of the gun-well floor where it meets the front: the front panel stops here, and the front face
    beside the gun well above it is solid printed frame (one cheek piece each side, round the speaker)."""
    return FRONT_CUT[0]


def _tidy(poly, merge=4.0, dev=0.5):
    """Drop vertices closer than `merge` to the previous one or within `dev` of the line through their
    neighbours (the speaker notch leaves 2 mm stubs where it crosses the front cut)."""
    pts = [V(*q) for q in poly]
    changed = True
    while changed and len(pts) > 3:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            ac = c - a
            off = (b - a).cross(ac).Length / max(ac.Length, 1e-9)
            if (b - a).Length < merge or off < dev:
                pts.pop(i)
                changed = True
                break
    return [q.toTuple() for q in pts]


def panels_for(fi):
    """A body face as one panel; the side walls split at SIDE_SPLIT_X (their rear panels are the
    battery doors), the front slant stops at the well floor, and anything bigger than one sheet splits once
    (along y = 0)."""
    n = fi["n"]
    if n.z < -0.99 or is_open_face(fi):
        return []
    poly = list(fi["verts"])
    if n.x > 0.5 and n.z > 0.2:
        FRONT_CUT[0] = min(v[2] for v in poly if abs(v[1]) <= P.Y_SLOT + 0.5)
        poly = _tidy(_clip3(poly, 2, FRONT_CUT[0], -1))
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


def _area(wire):
    return cq.Face.makeFromWires(wire).Area()


def round_wire(wire, inset, R, fallback=(0.66, 0.4, 0.2)):
    """Planar wire offset inward by `inset`, convex and concave corners rounded at R (smaller where a neck is
    too narrow for it)."""
    for r in [R] + [R * f for f in fallback] + [0.0]:
        try:
            if r <= 0.0:
                return max(wire.offset2D(-inset, "intersection"), key=_area)
            a = wire.offset2D(-(inset + r), "intersection")
            if len(a) != 1:
                continue
            b = a[0].offset2D(r, "arc")                       # convex corners
            c = b[0].offset2D(r, "arc")[0].offset2D(-r, "arc") if len(b) == 1 else []   # then concave ones
            if len(c) == 1:
                return c[0]
        except Exception:
            continue


def slab(poly3, n, inset, depth0, thick, R=0.0):
    """Prism of the panel polygon inset in-plane by `inset` (corners rounded at R), from depth0 to depth0+thick
    inward."""
    pl, pts = _wp_on(poly3, n)
    pl2 = cq.Plane(origin=pl.origin - n * depth0, xDir=pl.xDir, normal=n)
    wp = cq.Workplane(pl2).polyline(pts).close()
    if inset or R:
        w = wp.wires().val()
        w = round_wire(w, inset, R) if R else w.offset2D(-inset, "intersection")[0]
        wp = cq.Workplane(pl2).add(w).toPending()
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

    # each window's edge is also its LED surface: set per edge (edge_kinds), corners rounded at WINDOW_R
    edge_kinds(panels, log)
    _settle_insets(panels, shell, log)
    fills = corner_fills(panels, log)
    raw = shell.fuse(union(fills).intersect(body)) if fills else shell
    frame = raw.cut(union([_window_prism(p) for p in panels])).clean()
    log(f"corner fills: {len(fills)} shared edges filled solid between their back-to-back LED skins")
    recess, short, out = [], 0, 0
    for p in panels:
        recess.append(slab(p["poly"], p["n"], P.MEM_W - P.REBATE_W, -1.0, P.REBATE_D + 1.0, P.ACRYLIC_R + 0.3))
        p["clips"] = corner_clips(p)
        for c in p["clips"]:
            if c.get("holes"):                            # an insert near a slanted face mustn't break out of it:
                keep = []                                 # shorten it (an M4 x 8 there), or drop that screw
                for S in c["holes"]:
                    at, dn = (S - p["n"] * (P.CLIP_T - 0.1)).toTuple(), (p["n"] * -1).toTuple()
                    for depth, sk in ((P.INSERT[1], 1.0), (8.0, 1.0), (7.0, 1.0), (7.0, 0.5), (6.5, 0.5)):
                        if cyl(P.INSERT[0] + sk, depth + sk, at, dn).cut(body).Volume() < 0.5:
                            keep.append(cyl(P.INSERT[0], depth, at, dn))
                            short += depth < P.INSERT[1]
                            break
                    else:
                        out += 1
                        log(f"  clip screw dropped (its insert would break out) at ({S.x:.0f}, {S.y:.0f}, {S.z:.0f})")
                c["insert"] = union(keep) if keep else cyl(0.1, 0.1, c["holes"][0].toTuple(), (0, 0, 1))
            recess += [c["pocket"], c["insert"]]
    log(f"clip inserts: {short} shortened to stay inside a slanted face (M4 x 8 there), {out} screws dropped")
    frame = frame.cut(union(recess)).clean()
    # panel light: the web that carries the window wall back to the strip (kept out of the speaker pockets), then
    # the frame tunnels (their feed slots cut through it)
    webs = union([r for r in (led_web(p) for p in panels) if r is not None])
    frame = frame.fuse(webs.cut(union(SPK.cuts())) if SPK.cuts() else webs).clean()
    loop = 0.0
    for p in panels:
        p["led"], length = led_loop(p)
        loop += length
    tunnels, frame_strips, frame_strip = strip_tunnels(panels, body.cut(inner_solid(P.TUNNEL_SKIN)), frame)
    skipped = 0
    for k in range(0, len(tunnels), 3):                    # one edge (tunnel + two feed slots) at a time: a single
        cut = union(tunnels[k:k + 3])                     # fused cut silently skipped some of them
        try:
            nxt = frame.cut(cut)
            if nxt.Solids() and nxt.Volume() < frame.Volume() - 1.0:
                frame = nxt
                continue
        except ValueError:
            pass
        skipped += 1
    for k, (_, strip) in enumerate(frame_strips):        # a cut that only half-went: retry its three solids alone
        if frame.intersect(strip).Volume() > 10.0:
            for t in tunnels[3 * k:3 * k + 3]:
                try:
                    frame = frame.cut(t)
                except ValueError:
                    pass
            if frame.intersect(strip).Volume() > 10.0:
                skipped += 1
    frame = frame.clean()
    if skipped:
        log(f"frame tunnels: {skipped} edges' tunnels didn't cut")
    log(f"frame network volume {frame.Volume() / 1e6:.2f} L, {sum(len(p['clips']) for p in panels)} corner clips, "
        f"strip {loop / 1000:.1f} m in {len(panels)} panel loops + {frame_strip / 1000:.1f} m in {len(frame_strips)} frame tunnels")
    # where three faces meet, the neighbours' rails and loops cross this loop's corner: the strip is cut there at
    # its nearest cut mark and jumped with three wires, so trim the model strip to match and count the jumpers
    jumpers, pairs, worst = 0, 0, 0.0
    for i, p in enumerate(panels):                         # before trimming: where would two strips run into each other?
        for q in panels[:i]:
            if p["led"] is None or q["led"] is None:
                continue
            x = p["led"].intersect(q["led"])
            v = x.Volume()
            if v > 1.0:
                pairs, worst = pairs + 1, max(worst, v)
                c = x.BoundingBox().center
                log(f"  strips {_label(q)} / {_label(p)} overlap {v:.0f} mm3 at ({c.x:.0f}, {c.y:.0f}, {c.z:.0f})")
    log(f"LED strips overlapping before trimming: {pairs} pairs, worst {worst:.0f} mm3")
    spk = union(SPK.cuts()) if SPK.cuts() else None
    for i, p in enumerate(panels):
        if p["led"] is None:
            p["led_pieces"] = []
            continue
        inside = _robust(p["led"].intersect, frame)
        for x in inside.Solids():
            if x.Volume() > 5.0:
                c = x.BoundingBox().center
                log(f"  strip {_label(p)} runs into the frame: {x.Volume():.0f} mm3 at ({c.x:.0f}, {c.y:.0f}, {c.z:.0f})")
        ring = _robust(p["led"].cut, frame)
        if spk is not None:
            ring = _robust(ring.cut, spk)
        for q in panels[:i]:
            for piece in q.get("led_pieces", []):
                bb, pb = ring.BoundingBox(), piece.BoundingBox()
                if bb.xmin < pb.xmax and pb.xmin < bb.xmax and bb.ymin < pb.ymax and pb.ymin < bb.ymax and \
                        bb.zmin < pb.zmax and pb.zmin < bb.zmax:
                    ring = _robust(ring.cut, piece)
        p["led_pieces"] = sorted([s for s in ring.Solids() if s.Volume() > 50.0], key=lambda s: -s.Volume())
        jumpers += max(0, len(p["led_pieces"]) - 1)
        p["led_kept"] = sum(s.Volume() for s in p["led_pieces"]) / max(1.0, p["led"].Volume())
    log(f"LED loops: {jumpers} jumpers where neighbours' webs or loops cross a corner; strip kept per panel "
        + ", ".join(f"{p.get('led_kept', 0) * 100:.0f}%" for p in panels))
    build.strips, build.tunnels, build.frame_strips = (loop, frame_strip), tunnels, frame_strips
    build.jumpers = jumpers
    return body, frame, panels


def _label(p):
    """Short panel name for logs."""
    n = p["n"]
    c = sum((V(*q) for q in p["poly"]), V(0, 0, 0)) * (1.0 / len(p["poly"]))
    side = "deck" if n.z > 0.9 else "front" if n.x > 0.3 else "rear" if n.x < -0.3 else ("left" if n.y > 0 else "right")
    return f"{side}@x{c.x:.0f}"


def _ordered_edges(wire):
    """Edges in wire order, each with whether it runs against the wire."""
    ex, out = BRepTools_WireExplorer(wire.wrapped), []
    while ex.More():
        out.append((cq.Edge(ex.Current()), ex.Orientation() == TopAbs_REVERSED))
        ex.Next()
    return out


def edge_kinds(panels, log=None):
    """p["kinds"][k]: edge k of the panel outline is "shared" (with a panel at an angle), "coplanar" (a seam in
    one face), "notch" (a speaker pocket's edge), "slot" (the gun well) or "open" (the bottom, the front cut).
    p["ins"][k]: how far in from that edge the window edge (the LED surface) sits. On an edge shared with a panel
    at interior angle phi, the web (square to the panel, `ins` in from the edge, down to LED_END) must stay on this
    panel's side of the bisector, a point at distance x from the edge and depth y being inside when
    y < x tan(phi / 2): the two neighbours' strips then meet back to back in a point at the corner."""
    seen = {}
    for i, p in enumerate(panels):
        poly = [V(*q) for q in p["poly"]]
        kinds, ins = [], []
        for k in range(len(poly)):
            a, b = poly[k], poly[(k + 1) % len(poly)]
            mids = [a + (b - a) * f for f in (0.25, 0.5, 0.75)]
            shared = coplanar = False
            nb = None
            for j, o in enumerate(panels):
                if j == i:
                    continue
                hit = False
                oq = [V(*q) for q in o["poly"]]
                for m in range(len(oq)):
                    c, d = oq[m], oq[(m + 1) % len(oq)]
                    cd = d - c
                    for x in mids:
                        t = max(0.0, min(1.0, (x - c).dot(cd) / cd.dot(cd)))
                        hit |= (c + cd * t - x).Length < 0.5
                if hit:
                    if abs(o["n"].dot(p["n"])) > 0.99:
                        coplanar = True
                    else:
                        shared, nb = True, o["n"]
            notch = any(c.isInside(mids[1], 1.0) for c in SPK.cuts())
            slot = all(abs(abs(q.y) - P.Y_SLOT) < 0.5 for q in (a, b))
            notch |= p["n"].z > 0.9 and all(abs(q.x - P.X_TOP_FRONT) < 1.0 for q in (a, b))   # deck front: over the cups
            kind = ("coplanar" if coplanar else "shared" if shared else
                    ("notch_top" if p["n"].z > 0.9 else "notch") if notch else "slot" if slot else "open")
            d = P.WINDOW_IN[kind]
            if kind == "shared":
                phi = math.pi - math.acos(max(-1.0, min(1.0, p["n"].dot(nb))))
                tn, t = math.tan(phi / 2), P.LED_BAND[3]
                r, g = min(P.RAIL_EDGE_R, t), P.LED_GAP / 2
                d = min(P.WINDOW_IN_MAX, max(d, (P.LED_END - r + g) / tn + t, (P.LED_END + g) / tn))
                seen[round(math.degrees(phi))] = round(d, 1)
            kinds.append(kind)
            ins.append(d)
        p["kinds"], p["ins"] = kinds, ins
    if log:
        log("shared edges, interior angle -> window/LED inset (mm): " +
            ", ".join(f"{a} deg -> {d}" for a, d in sorted(seen.items())))


def _window_outline(p, pl, pts):
    """The window edge, which is also the LED surface: each edge inset by p["ins"], corners rounded at WINDOW_R
    (less where a neck is too narrow)."""
    ins = p.get("ins") or [P.MEM_W] * len(pts)
    i0 = min(ins)
    outline = cq.Workplane(pl).polyline(pts).close().wires().val()
    poly = [pl.origin + pl.xDir * x + pl.yDir * y for x, y in pts]
    for r in (P.WINDOW_R, 10.0, 6.0, 3.0):
        try:
            base = outline.offset2D(-(i0 + r), "intersection")
            if len(base) != 1:
                continue
            face = cq.Workplane(pl).add(base[0]).toPending().extrude(-1.0).val()
            for k, ik in enumerate(ins):
                if ik <= i0:
                    continue
                a, b = poly[k], poly[(k + 1) % len(poly)]
                e = (b - a).normalized()
                w = ik + r
                t = _inward_dir(p, a, b)
                side = 1.0 if t.dot(p["n"].cross(e)) > 0 else -1.0
                plb = cq.Plane(origin=(a - e * w + p["n"] * 5.0).toTuple(), xDir=e.toTuple(), normal=p["n"].toTuple())
                L = (b - a).Length + 2 * w
                face = face.cut(cq.Workplane(plb).polyline([(0, 0), (L, 0), (L, side * w), (0, side * w)]).close()
                                .extrude(-20.0).val())
            sols = sorted(face.Solids(), key=lambda x: -x.Volume())
            if not sols:
                continue
            top = max(sols[0].Faces(), key=lambda f: f.Center().dot(p["n"])).outerWire()
            a1 = top.offset2D(r, "arc")
            if len(a1) != 1:
                continue
            c1 = a1[0].offset2D(r, "arc")[0].offset2D(-r, "arc")
            if len(c1) == 1:
                return c1[0], r
        except Exception:
            continue
    return None, 0.0                                       # too narrow: the panel goes without a loop


def _dist_seg(c, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (c - a).dot(ab) / ab.dot(ab)))
    return (a + ab * t - c).Length


def _settle_insets(panels, shell, log, rounds=4, step=4.0):
    """Push a window edge (= LED surface) further in wherever its strip would run into frame that stays (another
    face's member, a speaker cheek, the bottom shell), `step` mm a round, up to WINDOW_IN_MAX."""
    for rnd in range(rounds):
        for p in panels:
            p.pop("rail_path", None)
            p.pop("chamfer", None)
        rest = shell.cut(union([_window_prism(p, test=True) for p in panels]))
        moved = []
        for p in panels:
            ring, _ = led_loop(p)
            if ring is None:
                continue
            poly = [V(*q) for q in p["poly"]]
            bump = set()
            for x in _robust(ring.intersect, rest).Solids():
                if x.Volume() < 5.0:
                    continue
                c = x.BoundingBox().center
                bump.add(min(range(len(poly)), key=lambda k: _dist_seg(c, poly[k], poly[(k + 1) % len(poly)])))
            for k in bump:
                if p["ins"][k] < P.WINDOW_IN_MAX:
                    p["ins"][k] = min(P.WINDOW_IN_MAX, p["ins"][k] + step)
                    moved.append(f"{_label(p)} edge {k} ({p['kinds'][k]}) -> {p['ins'][k]:.0f}")
        if not moved:
            break
        log(f"  round {rnd + 1}: " + "; ".join(moved))
    for p in panels:
        p.pop("rail_path", None)
        p.pop("chamfer", None)
    log("window/LED insets: " + " | ".join(f"{_label(p)} " + " ".join(f"{d:.0f}" for d in p["ins"]) for p in panels))


def _ledge_2d(p):
    """The ledge line (panel outline inset MEM_W, corners at WINDOW_R) as a 2D polyline in the panel plane."""
    pl, pts = _wp_on(p["poly"], p["n"])
    w = round_wire(cq.Workplane(pl).polyline(pts).close().wires().val(), P.MEM_W, P.WINDOW_R)
    o, ux, uy = pl.origin, pl.xDir, pl.yDir
    out = []
    for ed, rev in _ordered_edges(w):
        n = 1 if ed.geomType() == "LINE" else max(4, math.ceil(ed.Length() / 2.0))
        ps = [ed.positionAt(k / n) for k in range(n + 1)]
        ps = ps[::-1] if rev else ps
        out += [((v - o).dot(ux), (v - o).dot(uy)) for v in ps[:-1]]
    return out


def _chamfer(p):
    """Per sample of the LED line: its offset out to the ledge line (MEM_W in from the panel edge, rounded at
    WINDOW_R), found along the sample's own normal, so the wall chamfers straight from the acrylic's 7 mm ledge
    down to the LED band all round, corners included; and the skin's back there (a true LED_BAND[3] across the
    slope)."""
    if "chamfer" in p:
        return p["chamfer"]
    _, xy, nrm, _ = _rail_path(p)
    ledge = _ledge_2d(p)
    c = []
    for (x, y), (nx, ny) in zip(xy, nrm):
        k = math.hypot(nx, ny)
        dx, dy = -nx / k, -ny / k                     # outward
        best = None
        for i in range(len(ledge)):
            (ax, ay), (bx, by) = ledge[i], ledge[(i + 1) % len(ledge)]
            ex, ey = bx - ax, by - ay
            den = dx * ey - dy * ex
            if abs(den) < 1e-12:
                continue
            t = ((ax - x) * ey - (ay - y) * ex) / den
            u_ = ((ax - x) * dy - (ay - y) * dx) / den
            if -1e-9 <= u_ <= 1 + 1e-9 and t > -0.5 and (best is None or t < best):
                best = t
        c.append(-max(0.0, best) / k if best is not None and best < 80.0 else 0.0)
    h = P.LED_D0 - P.REBATE_D
    p["chamfer"] = (c, [ci - P.LED_BAND[3] * math.hypot(1.0, ci / h) for ci in c])
    return p["chamfer"]


def _window_prism(p, test=False):
    """The window cut: the ledge line down to the acrylic's ledge, a chamfer straight to the top of the LED band on
    the window/LED line, then the whole window to just past the member; below that only a WINDOW_RING-wide ring
    inside the LED line down past the skin (it clears the strip and the corner fills' window side and nothing
    else). test=True: without the ring, so a strip that runs into other frame still shows."""
    if _rail_path(p) is None:
        return slab(p["poly"], p["n"], P.MEM_W, -1.0, (P.MEM_H if test else P.LED_END) + 3.0, P.WINDOW_R)
    c, _ = _chamfer(p)
    full = _rail_region(p, 0, 0, 0, sections=[(-1.0, c), (P.REBATE_D, c), (P.LED_D0, 0.0), (P.MEM_H + 3.0, 0.0)])
    if test:
        return full
    # sections break at LED_D0 like every other LED surface: the lean starts there, and a loft that skipped it would
    # sit a hair off the strip's back face along the leaning runs
    ring = _rail_region(p, 0, 0, 0, sections=[(P.LED_D0 - 0.5, 0.0), (P.LED_D0, 0.0), (P.LED_END + 2.0, 0.0)]).cut(
        _rail_region(p, 0, 0, 0, sections=[(P.LED_D0 - 1.0, P.WINDOW_RING), (P.LED_D0, P.WINDOW_RING),
                                           (P.LED_END + 3.0, P.WINDOW_RING)]))
    return full.fuse(ring)


def _edge_index(p, a, b):
    """Index of the panel outline edge lying on segment ab."""
    m = (a + b) * 0.5
    poly = [V(*q) for q in p["poly"]]
    return min(range(len(poly)), key=lambda k: _dist_seg(m, poly[k], poly[(k + 1) % len(poly)]))


def corner_fills(panels, log=print):
    """Solid between two neighbours' LED skins along a shared edge, so their back-to-back strips sit on one V-shaped
    ridge with no gap between them. Generous on the window sides: the window cuts trim it to the chamfers and bands."""
    out = []
    for ed in edges_of(panels):
        groups = []                                       # one panel per plane (a side wall split at its battery
        for i in ed["panels"]:                            # door is two coplanar panels on one edge)
            if not any(abs(panels[i]["n"].dot(panels[j]["n"])) > 0.99 for j in groups):
                groups.append(i)
        if len(groups) != 2:
            continue
        A, B = (panels[i] for i in groups)
        a, b = ed["a"], ed["b"]
        side = []
        for q in (A, B):
            t, ins = _inward_dir(q, a, b), q["ins"][_edge_index(q, a, b)]
            o_ = P.WINDOW_RING - 1.0                      # inside the window ring, which trims it back to the band
            side.append((a + t * (ins + o_), a + t * (ins + o_) - q["n"] * P.LED_END, a + t * ins - q["n"] * P.LED_END))
        e = (b - a).normalized()                          # exactly square to the edge (a panel's edges can sit
        poly = [q - e * e.dot(q - a) for q in         # a hair off its plane, which OCC calls non-planar)
                [a, side[0][0], side[0][1], side[0][2], side[1][2], side[1][1], side[1][0]]]
        try:
            f = cq.Face.makeFromWires(cq.Wire.makePolygon(poly, close=True))
            out.append(cq.Solid.extrudeLinear(f, b - a))
        except Exception as ex:
            log(f"  corner fill skipped at ({a.x:.0f}, {a.y:.0f}, {a.z:.0f}): {repr(ex)[:60]}")
    return out


def _rail_path(p):
    """The rail's strip face at the strip's centre depth, sampled: 2D points (panel-plane u, w), the outward
    miter offset per point (unit-offset vector) and the lean weight (0 on corners, 1 along the straight runs)."""
    if "rail_path" in p:
        return p["rail_path"]
    pl, pts = _wp_on(p["poly"], p["n"])
    wire, p["rail_r"] = _window_outline(p, pl, pts)
    if wire is None:
        p["rail_path"] = None
        return None
    o, u, w = pl.origin, pl.xDir, pl.yDir
    q2 = lambda v: ((V(*v.toTuple()) - o).dot(u), (V(*v.toTuple()) - o).dot(w))
    xy, wt = [], []
    for ed, rev in _ordered_edges(wire):
        L = ed.Length()
        line = ed.geomType() == "LINE"
        if line:
            T0 = min(P.LED_TWIST, L / 4)                  # square for this far from each corner (the neighbours'
            T = min(P.LED_TWIST, L / 4)                   # loops turn their corners there), then twists in over T
            ss = sorted(set([0.0, T0, L - T0, L / 2] + [T0 + T * k / 8 for k in range(1, 9)] +
                            [L - T0 - T * k / 8 for k in range(1, 9)]))
        else:
            ss = [L * k / max(2, math.ceil(L / 4.0)) for k in range(max(2, math.ceil(L / 4.0)))]
        a = [q2(ed.positionAt(s / L)) for s in ss]
        if not line:
            ss.append(L)
            a.append(q2(ed.positionAt(1.0)))
        if rev:
            a, ss = a[::-1], [L - s for s in ss[::-1]]
        for (x, y), s in zip(a, ss):
            if xy and math.hypot(x - xy[-1][0], y - xy[-1][1]) < 0.05:
                continue
            xy.append((x, y))
            if line:
                f = max(0.0, min(s, L - s) - T0) / T
                wt.append(f * f * (3 - 2 * f) if f < 1 else 1.0)       # smoothstep: the strip twists in gently
            else:
                wt.append(0.0)
    if math.hypot(xy[0][0] - xy[-1][0], xy[0][1] - xy[-1][1]) < 0.05:
        xy.pop(), wt.pop()
    area = sum(xy[i][0] * xy[(i + 1) % len(xy)][1] - xy[(i + 1) % len(xy)][0] * xy[i][1] for i in range(len(xy)))
    sg = 1.0 if area > 0 else -1.0
    nrm = []
    for i in range(len(xy)):
        (x0, y0), (x1, y1), (x2, y2) = xy[i - 1], xy[i], xy[(i + 1) % len(xy)]
        ns = []
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)), ((x1, y1), (x2, y2))):
            L = math.hypot(bx - ax, by - ay)
            ns.append((-(by - ay) / L * sg, (bx - ax) / L * sg))     # inward (left of a counter-clockwise run)
        bx, by = ns[0][0] + ns[1][0], ns[0][1] + ns[1][1]
        bl = math.hypot(bx, by)
        bx, by = (bx / bl, by / bl) if bl > 1e-9 else ns[0]
        k = 1.0 / max(0.3, bx * ns[0][0] + by * ns[0][1])           # miter: a true offset of the polyline
        nrm.append((bx * k, by * k))
    p["rail_path"] = (pl, xy, nrm, wt)
    return p["rail_path"]


def _rail_region(p, d0, d1, off, sections=None):
    """Solid behind the panel from depth d0 to d1, inside the window/LED line shifted `off` inward (or through
    `sections`, a list of (depth, off), off a number or one per sample). Above the strip the wall stands square to the panel; from the strip's
    top edge down it leans LED_BAND[2] toward the panel along the straight runs, and round the corners it stays
    square, so the strip only bends the easy way there."""
    pl, xy, nrm, wt = _rail_path(p)
    n, tl = p["n"], math.tan(math.radians(P.LED_BAND[2]))
    wires = []
    for d, off in (sections or ((d0, off), (d1, off))):
        offs = off if isinstance(off, (list, tuple)) else [off] * len(xy)
        pts = []
        for (x, y), (nx, ny), f, o in zip(xy, nrm, wt, offs):
            s = o + max(0.0, d - P.LED_D0) * tl * f
            pts.append(pl.origin + pl.xDir * (x + nx * s) + pl.yDir * (y + ny * s) - n * d)
        wires.append(cq.Wire.makePolygon(pts, close=True))
    return cq.Solid.makeLoft(wires, True)


def led_web(p):
    """The skin behind the window wall: from the ledge down the chamfer and the LED band to just below the strip,
    LED_BAND[3] thick, its back edge rounded over at the bottom. A closed loop, so each panel's strip lights only its
    own panel."""
    t = P.LED_BAND[3]
    if _rail_path(p) is None:
        return None
    c, sk = _chamfer(p)
    r = min(P.RAIL_EDGE_R, t)
    d1 = P.LED_END
    back = [(P.REBATE_D + 0.5, sk), (P.LED_D0, -t)] + [(d1 - r + r * math.sin(a), -t + r - r * math.cos(a))
                                                      for a in (math.radians(k * 22.5) for k in range(5))]
    face = [(P.REBATE_D - 0.5, c), (P.REBATE_D, c), (P.LED_D0, 0.0), (d1 + 1.0, 0.0)]
    return _rail_region(p, 0, 0, 0, sections=back).cut(_rail_region(p, 0, 0, 0, sections=face))


def led_loop(p):
    """Simplified 60/m strip stuck to the web's face, LEDs aimed across the panel (and slightly at it along the
    straight runs)."""
    th = P.LED_STRIP_T
    if _rail_path(p) is None:
        return None, 0.0
    ring = _rail_region(p, 0, 0, 0, sections=[(P.LED_D0, 0.0), (P.LED_D1, 0.0)]).cut(
        _rail_region(p, 0, 0, 0, sections=[(P.LED_D0 - 1.0, th), (P.LED_D0, th), (P.LED_D1 + 1.0, th)]))
    _, xy, _, _ = _rail_path(p)
    return ring, sum(math.hypot(xy[i][0] - xy[i - 1][0], xy[i][1] - xy[i - 1][1]) for i in range(len(xy)))


def _bar(o, e, u, w, length, w0, w1, u0, u1):
    """Box from o along e for length, spanning w0..w1 along w and u0..u1 along u (Plane yDir = e x w = -u)."""
    pl = cq.Plane(origin=o, xDir=w, normal=e)
    pts = [(w0, -u0), (w1, -u0), (w1, -u1), (w0, -u1)]
    return cq.Workplane(pl).polyline(pts).close().extrude(length).val()


def _bend_pts(c, e, u, s_, sgn, R, tail, uc):
    """Centre-line points of one end's bend (from the run, up into the slot) and its tail; sgn +1 at the start
    end (the run goes +e), -1 at the far end."""
    k = math.sqrt(0.5)
    cs = s_ + sgn * R                                 # bend centre along the edge
    return [c + e * s_ + u * (uc + R + tail), c + e * s_ + u * (uc + R),
            c + e * (cs - sgn * R * k) + u * (uc + R - R * k), c + e * cs + u * uc]


def _frame_strip(c, e, u, w, L, ends=None):
    """The frame strip along one edge's tunnel, lying on the tunnel's inner wall with its LEDs facing out, bent the
    easy way (about its width) up into the feed slot at each end and on up to the slot's mouth, where it's
    soldered to the next edge's strip. `ends`: per end, (R, tail), or None for a straight end at the slot where
    the slot is too short to bend into. Returns (solid, strip length)."""
    ws, ts = P.FRAME_STRIP
    uc = P.TUNNEL[1] / 2 - ts / 2
    sc = (P.FEED[0] + P.FEED[1]) / 2
    ends = ends or (P.FRAME_BEND, P.FRAME_BEND)
    eds = []
    a_ = _bend_pts(c, e, u, sc, 1, *ends[0], uc) if ends[0] else None
    b_ = _bend_pts(c, e, u, L - sc, -1, *ends[1], uc) if ends[1] else None
    run0 = a_[3] if a_ else c + e * sc + u * uc
    run1 = b_[3] if b_ else c + e * (L - sc) + u * uc
    if a_:
        if ends[0][1] > 0.2:
            eds.append(cq.Edge.makeLine(a_[0], a_[1]))
        eds.append(cq.Edge.makeThreePointArc(a_[1], a_[2], a_[3]))
    eds.append(cq.Edge.makeLine(run0, run1))
    if b_:
        eds.append(cq.Edge.makeThreePointArc(b_[3], b_[2], b_[1]))
        if ends[1][1] > 0.2:
            eds.append(cq.Edge.makeLine(b_[1], b_[0]))
    path = cq.Wire.assembleEdges(eds)
    start = (a_[0] if ends[0][1] > 0.2 else a_[1]) if a_ else run0
    first = (eds[0].endPoint() - eds[0].startPoint()).normalized()
    prof = cq.Workplane(cq.Plane(origin=start.toTuple(), xDir=w.toTuple(), normal=first.toTuple())).rect(ws, ts)
    return prof.sweep(cq.Workplane(obj=path), transition="round").val(), path.Length()


def strip_tunnels(panels, skin, frame=None):
    """Frame light: a rectangular tunnel down the middle of every member, TUNNEL_GAP outward of the tenon line so
    the joint screws stop short of it, and a feed slot from the inside at each end where the strip goes in and
    the next edge's strip is joined. Slots and tunnel ends are trimmed TUNNEL_SKIN under every outer face and
    kept out of every joint. Also returns each edge's strip (_frame_strip), bent up into both its slots."""
    tw, th = P.TUNNEL
    s0, s1 = P.FEED
    cuts, strips, total, short = [], [], 0.0, []
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
        # per end: the largest bend whose whole footprint (centre line and both strip edges) lies in the slot and
        # tunnel, then a tail out to where the slot leaves the frame (the mouth, where the joint is soldered); a
        # straight end where not even a 3 mm bend fits
        room = union(cuts[-3:])
        sc, uc = (s0 + s1) / 2, th / 2 - P.FRAME_STRIP[1] / 2
        ends = []
        for s_, sgn in ((sc, 1), (L - sc, -1)):
            pick = None
            for R_ in (P.FRAME_BEND[0], 6.0, 4.5, 3.0):
                pts = _bend_pts(c, e, u, s_, sgn, R_, 0.0, uc)
                arc = [pts[1], pts[2], pts[3], c + e * (s_ + sgn * R_ * 0.3) + u * (uc + R_ * 0.05)]
                if all(room.isInside(q + w * dw, 0.05) for q in arc for dw in (-2.2, 0.0, 2.2)):
                    pick = R_
                    break
            if pick is None:
                ends.append(None)
                continue
            mouth = P.FRAME_BEND[1]
            if frame is not None:                         # where the slot axis leaves the frame
                seg = cq.Edge.makeLine(c + e * s_ + u * (uc + pick), c + e * s_ + u * 50.0)
                ins_ = [x for x in frame.intersect(seg).Edges()]
                if ins_:
                    near = min(ins_, key=lambda x: min((x.startPoint() - seg.startPoint()).Length,
                                                       (x.endPoint() - seg.startPoint()).Length))
                    mouth = max((near.startPoint() - seg.startPoint()).Length, (near.endPoint() - seg.startPoint()).Length) + 1.0
            top = uc + pick + mouth                       # never past the slot's own open length
            while top > uc + pick and not room.isInside(c + e * s_ + u * top, 0.05):
                top -= 1.0
            ends.append((pick, max(0.0, top - uc - pick)))
        strip, length = _frame_strip(c, e, u, w, L, ends)
        kept = strip.intersect(room)
        if kept.Volume() < 0.97 * strip.Volume() or len(kept.Solids()) > 1:
            short.append(f"E{k:02d} {kept.Volume() / strip.Volume() * 100:.0f}%")
        if any(x is None for x in ends):
            short.append(f"E{k:02d} straight end")
        strips.append((f"E{k:02d}", max(kept.Solids(), key=lambda x: x.Volume()) if kept.Solids() else strip))
        total += length
    if short:
        print("frame strips: " + ", ".join(short))
    return cuts, strips, total


def corner_clips(p):
    """Printed clip in a flush pocket at every convex corner of the panel: a round head that laps CLIP_OVER over
    the acrylic's rounded corner and a rounded tail to the screw, which goes into an M4 heat-set insert in the
    frame where the acrylic's corner is cut away. A battery door keeps only its bottom clips (they act as hooks)
    and gets a quarter-turn latch at the middle of its top edge: turn it, tip the door out from the top and lift
    it off the hooks."""
    n = p["n"]
    door = abs(n.y) > 0.9 and max(q[0] for q in p["poly"]) < P.SIDE_SPLIT_X + 1
    zmid = sum(q[2] for q in p["poly"]) / len(p["poly"])
    pl, pts = _wp_on(p["poly"], n)
    m = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % m][1] - pts[(i + 1) % m][0] * pts[i][1] for i in range(m))
    reb = P.MEM_W - P.REBATE_W
    face4 = slab(p["poly"], n, 4.0, 0.0, P.CLIP_T, P.CLIP_ROUND)     # clips stay 4 mm in from the face edges
    pocket4 = slab(p["poly"], n, 3.8, -1.0, P.CLIP_T + 1.0, P.CLIP_ROUND + 0.2)
    o3 = lambda x, y: pl.origin + pl.xDir * x + pl.yDir * y
    found = []
    for i in range(m):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[(i + 1) % m]
        cr = (x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)
        if cr * (1.0 if area > 0 else -1.0) <= 1e-3:
            continue                                          # concave or straight: no clip
        a = (x0 - x1, y0 - y1)
        b = (x2 - x1, y2 - y1)
        la, lb = math.hypot(*a), math.hypot(*b)
        a, b = (a[0] / la, a[1] / la), (b[0] / lb, b[1] / lb)
        bis = (a[0] + b[0], a[1] + b[1])
        bl = math.hypot(*bis)
        if bl < 1e-6:
            continue
        bis = (bis[0] / bl, bis[1] / bl)
        half = math.acos(max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1]))) / 2
        sin_h, cos_h = math.sin(half), math.cos(half)
        d_s = min(12.0 / sin_h, (P.FEED[0] - P.INSERT[0] - 1.0) / cos_h)   # the screw: clear of the tunnel feed slots
        d_apex = (reb + 0.3 + P.ACRYLIC_R) / sin_h - P.ACRYLIC_R            # tip of the acrylic's rounded corner
        found.append(((x1, y1), bis, d_s, d_apex + P.CLIP_OVER, min(la, lb)))
    corners = []
    for (x1, y1), bis, d_s, reach, short in found:
        far = min([math.hypot(x1 - x, y1 - y) for (x, y), *_ in found if (x, y) != (x1, y1)] + [1e9])
        reach = min(reach, far / 2 - 2.0, short / 2 - 2.0)
        rho = min(P.CLIP_R, max(6.0, reach - d_s + 7.0))
        d_q = max(d_s, reach - rho)
        sx, sy = x1 + bis[0] * d_s, y1 + bis[1] * d_s
        qx, qy = x1 + bis[0] * d_q, y1 + bis[1] * d_q
        S = o3(sx, sy)
        if door and S.z > zmid:
            continue                                          # the latch holds the door's top

        def head(grow, d0, d1):
            wp = cq.Workplane(cq.Plane(origin=pl.origin - n * d0, xDir=pl.xDir, normal=n))
            sh = [wp.center(qx, qy).circle(rho + grow).extrude(-(d1 - d0)).val(),
                  wp.center(sx, sy).circle(7.0 + grow).extrude(-(d1 - d0)).val()]
            if d_q - d_s > 0.5:
                px, py = -bis[1], bis[0]
                quad = [(sx + px * (7 + grow), sy + py * (7 + grow)), (qx + px * (rho + grow), qy + py * (rho + grow)),
                        (qx - px * (rho + grow), qy - py * (rho + grow)), (sx - px * (7 + grow), sy - py * (7 + grow))]
                sh.append(wp.polyline(quad).close().extrude(-(d1 - d0)).val())
            return union(sh)

        clip = head(0.0, 0.0, P.CLIP_T).intersect(face4).cut(cyl(2.25, 10, (S + n).toTuple(), (n * -1).toTuple()))
        pocket = head(0.2, -1.0, P.CLIP_T).intersect(pocket4)
        insert = cyl(P.INSERT[0], P.INSERT[1], (S - n * (P.CLIP_T - 0.1)).toTuple(), (n * -1).toTuple())
        for c in corners:                                 # a short edge: two clips that meet become one
            if c["clip"].intersect(clip).Volume() > 1.0 or c["pocket"].intersect(pocket).Volume() > 1.0:
                c["clip"] = c["clip"].fuse(clip).cut(cyl(2.25, 10, (S + n).toTuple(), (n * -1).toTuple()))
                c["pocket"] = c["pocket"].fuse(pocket)
                c["insert"] = c["insert"].fuse(insert)
                c["holes"].append(S)
                break
        else:
            corners.append(dict(clip=clip, pocket=pocket, insert=insert, holes=[S]))
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
    insert = cyl(P.INSERT[0], P.INSERT[1], (piv - n * (P.CLIP_T - 0.1)).toTuple(), (n * -1).toTuple())
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
        w = max(P.MEM_W, P.WINDOW_IN_MAX) + 3.0 + 2 * margin   # the member plus its LED web
        h = P.LED_END + 2 * margin
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
        inset = min(P.MEM_W - h - 1.0, max(7.0, h + (2.0 + (P.CORE_DEPTH + h) * c) / max(s, 0.3)))
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
        piece = _robust(frame.intersect, reg)
        rb = reg.BoundingBox()
        for prev in done:
            pb = prev.BoundingBox()
            if rb.xmin < pb.xmax and pb.xmin < rb.xmax and rb.ymin < pb.ymax and pb.ymin < rb.ymax and \
                    rb.zmin < pb.zmax and pb.zmin < rb.zmax:
                piece = _robust(piece.cut, prev)
        done.append(reg)
        sol = [s for s in piece.Solids() if s.Volume() > 50]
        if not sol:
            continue
        pieces.append(dict(name=name, shape=cq.Compound.makeCompound(sol) if len(sol) > 1 else sol[0],
                           edge=ed, t0=t0, t1=t1))
    rest = frame
    for reg in done:
        rest = _robust(rest.cut, reg)
    nodes = [s for s in rest.Solids() if s.Volume() > 50]
    pieces, nodes = _merge_cheeks(pieces, nodes, log)
    split = 0
    for k, s in enumerate(nodes):
        parts = _split_to_bed(s)
        split += len(parts) - 1
        for j, part in enumerate(parts):
            pieces.append(dict(name=f"N{k:02d}" + (chr(97 + j) if len(parts) > 1 else ""), shape=part, edge=None, t0=None,
                               t1=None))
    log(f"{len(pieces)} pieces ({len(nodes)} nodes, {split} extra glued splits to fit the bed)")
    return pieces, edges


def _robust(op, other):
    """A boolean that retries with a small fuzzy tolerance (the twisted rail faces sometimes upset OCC)."""
    if not op.__self__.Solids():
        return op.__self__                                # nothing to cut from
    for tol in (None, 0.01, 0.05):
        try:
            r = op(other, tol=tol) if tol else op(other)
            if r.isValid() or tol == 0.05:
                return r
        except ValueError:
            continue
    raise ValueError("boolean failed even with a fuzzy tolerance")


def _merge_cheeks(pieces, nodes, log):
    """The solid front face beside the gun well (no panel above the well floor), the speaker notch round it and
    the deck's front edge make one printed cheek each side instead of a cluster of short segments and nodes:
    segments centred in the cheek zone join it whole, nodes are cut at the zone's boundary (a glued seam)."""
    zf = front_cut()
    out_p, out_n, cheeks = list(pieces), list(nodes), []
    for sg, tag in ((1, "L"), (-1, "R")):
        y0, y1 = sorted([sg * (P.Y_SLOT - 0.5), sg * (P.Y_S + 30.0)])
        zone = box(60.0, P.FRAME_X + 10.0, y0, y1, zf - 30.0, P.Z_TOP + 5.0)

        def inside(s, m=15.0):
            b = s.BoundingBox()
            return b.xmin >= 60.0 - m and b.xmax <= P.FRAME_X + 10.0 + m and b.ymin >= y0 - m and b.ymax <= y1 + m \
                and b.zmin >= zf - 30.0 - m and b.zmax <= P.Z_TOP + 5.0 + m
        sp = [q for q in out_p if q["edge"] is not None and inside(q["shape"])]
        if not sp:
            continue
        core = union([q["shape"] for q in sp])
        parts, keep = [], []
        for nd in out_n:
            bb = nd.BoundingBox()
            inn = [] if bb.xmax < 60.0 or bb.ymax < y0 or bb.ymin > y1 or bb.zmax < zf - 30.0 else \
                [x for x in _robust(nd.intersect, zone).Solids() if x.Volume() > 50 and x.distance(core) < 0.05]
            if not inn:
                keep.append(nd)                           # doesn't reach the cheek: the node stays whole
                continue
            parts += inn
            rest = _robust(nd.cut, union(inn))
            keep += [x for x in rest.Solids() if x.Volume() > 50]
        shapes = [q["shape"] for q in sp] + parts
        fused = shapes[0].fuse(*shapes[1:]) if len(shapes) > 1 else shapes[0]
        try:
            fused = fused.clean()
        except Exception:                                  # OCC's upgrader sometimes trips on the rail faces
            pass
        sols = sorted([x for x in fused.Solids() if x.Volume() > 50], key=lambda x: -x.Volume())
        out_p = [q for q in out_p if not any(q is x for x in sp)]
        out_n = keep
        for j, sol in enumerate(sols):
            cheeks.append(dict(name=f"cheek {tag}" + (str(j + 1) if j else ""), shape=sol, edge=None, t0=None, t1=None))
        bb = sols[0].BoundingBox()
        log(f"cheek {tag}: {len(sp)} segments + {len(parts)} node parts -> {len(sols)} piece(s), main "
            f"{[round(v) for v in sorted([bb.xlen, bb.ylen, bb.zlen])]}")
    return out_p + cheeks, out_n


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
    ok = skipped = glued = 0
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
            ps2 = [panels[i] for i in ed["panels"]]
            ps2 = [q for k, q in enumerate(ps2) if not any(abs(q["n"].dot(r["n"])) > 0.99 for r in ps2[:k])]
            if len(ps2) == 2:
                # a filled corner (corner_fills): every way in for a screw head is a surface seen through the acrylic
                # or the LED ridge, so this joint is a tapered tenon glued with epoxy, no cross screw
                clear_h = pilot = cyl(0.01, 0.01, mid.toTuple(), u.toTuple())
                glued += 1
            # the fused tenon starts 0.5 mm inside its own piece: OCC doesn't always merge solids that only touch
            root = _frustum(core - out * 0.5, out, u, w, size, length + 0.5, taper)
            shapes[p["name"]] = shapes[p["name"]].fuse(root).cut(pilot).clean()
            hole = mort.fuse(ten).fuse(clear_h)
            hb = hole.BoundingBox()
            for q in pieces:                              # every piece the tenon reaches (a joint can sit across two)
                if q is p:
                    continue
                qb = shapes[q["name"]].BoundingBox()
                if hb.xmin < qb.xmax and qb.xmin < hb.xmax and hb.ymin < qb.ymax and qb.ymin < hb.ymax and \
                        hb.zmin < qb.zmax and qb.zmin < hb.zmax and (q is nb or shapes[q["name"]].intersect(ten).Volume() > 1.0):
                    shapes[q["name"]] = shapes[q["name"]].cut(hole).clean()
            ok += 1
    for p in pieces:
        p["shape"] = shapes[p["name"]]
    log(f"joints: {ok} tapered tenons, {ok - glued} with M4 cross screws and {glued} glued (filled corners), "
        f"{skipped} ends without a neighbour piece")
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
