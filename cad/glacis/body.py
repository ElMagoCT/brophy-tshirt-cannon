"""Body: frosted acrylic panels recessed into a printed frame that follows every panel edge.

How the frame is made:
1. The body is a polyhedron: the side outline (x/z) extruded across the robot, intersected with the
   front-view trapezoid (side walls lean in by TUMBLE), minus the gun slot.
2. The frame is that solid shelled inward by MEM_H, open at the bottom, with a "window" cut through
   it wherever a panel shows (each panel inset by MEM_W). What stays is a network of members along every
   panel edge; their faces lie on the panel planes.
3. Each panel sits in a rebate REBATE_W wide and REBATE_D deep, CLIP_T below the outer face. A printed
   clip in a flush pocket at every convex panel corner holds it (one M3 into a heat-set insert), so any
   panel comes off with its clips. An LED channel runs through every member right under the panel's
   overlap: the strip threads through it facing out and backlights the panel.
4. The network is split into printable pieces: a node block at every vertex and straight segments of
   at most PRINT_MAX along each edge, joined by tapered mortise-and-tenon joints with an M4 cross screw.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
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


def body_solid():
    pts = [(x, z) for x, z in P.SIDE_OUTLINE]
    prism = (cq.Workplane("XZ", origin=(0, -P.Y_S - 200, 0)).polyline(pts).close().extrude(-2 * P.Y_S - 400)).val()
    return prism.intersect(_tumble_prism(0.0)).cut(slot_prism()).clean()


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


def inner_solid():
    """The body offset inward by MEM_H, open at the bottom (OCC's shell() output breaks booleans)."""
    ipts = _offset_outline(P.SIDE_OUTLINE, P.MEM_H, bottom_drop=40.0)
    prism = (cq.Workplane("XZ", origin=(0, -P.Y_S - 200, 0)).polyline(ipts).close().extrude(-2 * P.Y_S - 400)).val()
    return prism.intersect(_tumble_prism(P.MEM_H)).cut(slot_prism()).clean()


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
    """Gun well walls and floor (every face lying inside the well's width): left open, no panel."""
    return all(abs(v[1]) <= P.Y_SLOT + 0.5 for v in fi["verts"])


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
    for p in panels:
        recess.append(slab(p["poly"], p["n"], P.MEM_W - P.REBATE_W, -1.0, P.REBATE_D + 1.0))
        # LED channel through the member, right under the panel's overlap: the strip lies flat facing out
        # and backlights the panel edge band; a lip on the window side and the panel itself close it
        a = slab(p["poly"], p["n"], P.MEM_W - P.REBATE_W + P.LED_CH[2], P.REBATE_D - 0.01, P.LED_CH[1])
        b = slab(p["poly"], p["n"], P.MEM_W - P.LED_LIP, P.REBATE_D - 0.5, P.LED_CH[1] + 1.0)
        recess.append(a.cut(b))
        p["clips"] = corner_clips(p)
        for c in p["clips"]:
            recess += [c["pocket"], c["insert"]]
    frame = frame.cut(union(recess)).clean()
    log(f"frame network volume {frame.Volume() / 1e6:.2f} L, "
        f"{sum(len(p['clips']) for p in panels)} corner clips")
    return body, frame, panels


def corner_clips(p, d_out=4.0):
    """Printed clip in a flush pocket at every convex corner of the panel outline."""
    n = p["n"]
    pl, pts = _wp_on(p["poly"], n)
    w = cq.Workplane(pl).polyline(pts).close().wires().val().offset2D(-(P.MEM_W - P.REBATE_W), "intersection")[0]
    edges = [e for e in w.Edges()]
    corners = []
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
        inside = slab(p["poly"], n, P.MEM_W - P.REBATE_W, 0.0, 1.0).isInside(mid - n * 0.5, 0.1)
        if not inside:
            continue
        ctr = c - bis * d_out
        disc = cyl(P.CLIP_R, P.CLIP_T, ctr.toTuple(), (n * -1).toTuple())
        keep = slab(p["poly"], n, 4.0, 0.0, P.CLIP_T)
        clip = disc.intersect(keep).cut(cyl(1.7, 10, (ctr + n).toTuple(), (n * -1).toTuple()))
        pocket = cyl(P.CLIP_R + 0.2, P.CLIP_T + 1.0, (ctr + n).toTuple(), (n * -1).toTuple()).intersect(
            slab(p["poly"], n, 3.8, -1.0, P.CLIP_T + 1.0))
        insert = cyl(2.0, 6.0, (ctr - n * (P.CLIP_T - 0.1)).toTuple(), (n * -1).toTuple())
        corners.append(dict(clip=clip, pocket=pocket, insert=insert))
    return corners


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
        w, h = P.MEM_W + 2 * margin, P.MEM_H + 2 * margin
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


def _core_point(edge, panels, at, depth=None):
    """A point deep in the member's cross-section, clear of grooves and LED channels."""
    depth = P.CORE_DEPTH if depth is None else depth
    a, b = edge["a"], edge["b"]
    ps = [panels[i] for i in edge["panels"]]
    if len(ps) == 1:
        p = ps[0]
        return at + _inward_dir(p, a, b) * 7.0 - p["n"] * depth
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


def section(frame, panels, log=print, seg_max=215.0):
    """Split the frame network into printable pieces with tapered mortise-tenon joints."""
    edges = edges_of(panels)
    log(f"{len(edges)} edges")
    regions, joints = [], []          # regions: (name, solid); joints: (seg_index, end, edge, point, outward dir)
    for ei, ed in enumerate(edges):
        L = (ed["b"] - ed["a"]).Length
        s = P.NODE_SETBACK / L
        m = L - 2 * P.NODE_SETBACK
        if m < 40:
            continue
        n = max(1, math.ceil(m / seg_max))
        ts = [s + (1 - 2 * s) * k / n for k in range(n + 1)]
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
    for k, s in enumerate(nodes):
        pieces.append(dict(name=f"N{k:02d}", shape=s, edge=None, t0=None, t1=None))
    log(f"{len(pieces)} pieces ({len(nodes)} nodes)")
    return pieces, edges


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
            ten = _frustum(core, out, u, w, tw, tl, tt)
            if ten.intersect(shapes[nb["name"]]).Volume() < 0.95 * ten.Volume():
                ten = _frustum(core, out, u, w, 5.0, 10.0, 0.4)
                if ten.intersect(shapes[nb["name"]]).Volume() < 0.95 * ten.Volume():
                    skipped += 1
                    continue
            mort = _frustum(core - out * 0.01, out, u, w, tw + 2 * P.TENON_CLEAR, tl + 0.5, tt)
            mid = core + out * (tl / 2)
            clear_h = cyl(2.25, 45, (mid - u * 2).toTuple(), u.toTuple())
            pilot = cyl(1.65, 45, (mid - u * 3).toTuple(), u.toTuple())
            shapes[p["name"]] = shapes[p["name"]].fuse(ten).cut(pilot).clean()
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
