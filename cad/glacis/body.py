"""Body: frosted acrylic panels held in a printed frame that follows every panel edge.

How the frame is made:
1. The body is a polyhedron (side outline x/z extruded across the robot, minus the gun slot).
2. The frame is that solid shelled inward by MEM_H, open at the bottom, with a "window"
   cut through it wherever a panel shows (each panel inset by MEM_W). What stays is a
   network of members along every panel edge and seam; their faces lie on the panel planes,
   so every groove angle comes out right automatically.
3. Each panel cuts its own groove (edge 8 mm deep, 2 mm lip in front) and an LED channel
   behind its hidden edge, so the strip lights the frosted edge from behind.
4. The network is split into printable pieces: a node block at every vertex and straight
   segments of at most PRINT_MAX along each edge, joined by tapered mortise-and-tenon
   joints with an M4 cross screw.
"""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P
from lib import add, box, cyl, union

EPS = 1e-6


# ------------------------------------------------------------------ the body polyhedron
def body_solid():
    pts = [(x, z) for x, z in P.SIDE_OUTLINE]
    prism = (cq.Workplane("XZ", origin=(0, -P.Y_S, 0)).polyline(pts).close().extrude(-2 * P.Y_S)).val()
    slot = box(P.X_SLOT_REAR, 2000, -P.Y_SLOT, P.Y_SLOT, P.Z_SLOT_FLOOR, 3000)
    return prism.cut(slot).clean()


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
    yi = P.Y_S - P.MEM_H
    prism = (cq.Workplane("XZ", origin=(0, -yi, 0)).polyline(ipts).close().extrude(-2 * yi)).val()
    g = P.MEM_H
    slot = box(P.X_SLOT_REAR, 2000, -P.Y_SLOT, P.Y_SLOT, P.Z_SLOT_FLOOR - g, 3000)
    return prism.cut(slot).clean()


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
    """Gun-slot walls and slot rear wall: left open (no panel, no frame)."""
    n, c = fi["n"], fi["c"]
    slot_wall = abs(n.y) > 0.99 and abs(abs(c.y) - P.Y_SLOT) < 1
    slot_rear = n.x > 0.99 and abs(c.x - P.X_SLOT_REAR) < 1
    return slot_wall or slot_rear


def panels_for(fi):
    """A body face as one panel, or two split at the tower line if it cannot fit one sheet."""
    n = fi["n"]
    if n.z < -0.99 or is_open_face(fi):
        return []
    poly = list(fi["verts"])
    if _fits(poly, n):
        return [poly]
    out = []
    for sgn in (1, -1):
        part = _clip3(poly, 0, P.TOWER_X, sgn) if abs(n.x) < 0.99 else _clip3(poly, 1, 0.0, sgn)
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


def _wall(p):
    """Slot wall position and the direction from its surface into the body (away from the slot)."""
    s = 1 if p["n"].y > 0 else -1
    return -s * P.Y_SLOT, -s


def ycyl(r, y0, y1, x=None, z=None):
    lo, hi = min(y0, y1), max(y0, y1)
    return cyl(r, hi - lo, (P.PIVOT[0] if x is None else x, lo, P.PIVOT[1] if z is None else z), (0, 1, 0))


def xz_prism(pts, y0, y1):
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Workplane("XZ", origin=(0, lo, 0)).polyline(pts).close().extrude(-(hi - lo)).val()


# ------------------------------------------------------------------ build
def build(log=print):
    body = body_solid()
    log(f"body: {len(body.Faces())} faces, volume {body.Volume() / 1e6:.1f} L")
    shell = body.cut(inner_solid()).clean()
    log(f"shell volume {shell.Volume() / 1e6:.2f} L, {len(shell.Solids())} solid")

    panels = []
    for fi in face_info(body):
        for poly in panels_for(fi):
            panels.append(dict(poly=poly, n=fi["n"], hole=None))
    log(f"{len(panels)} panels")

    frame = shell
    cuts = []
    for p in panels:
        w = slab(p["poly"], p["n"], P.MEM_W, -1.0, P.MEM_H + 2.0)
        if p["hole"]:
            w = w.cut(_ring_keep(p))
        cuts.append(w)
        if p["hole"]:
            cuts.append(_hole_through(p))
    frame = frame.cut(union(cuts)).clean()
    grooves = []
    for p in panels:
        g = slab(p["poly"], p["n"], P.MEM_W - P.GROOVE_D, P.LIP, P.GROOVE_W)
        # LED slot on the window edge: the strip stands on edge behind the groove and shines across
        # the back of the panel (two flat channels met at every corner and cut the member in two)
        led = slab(p["poly"], p["n"], P.MEM_W - P.LED_SLOT[0], P.LIP + P.GROOVE_W - 0.01, P.LED_SLOT[1])
        if p["hole"]:
            g = g.cut(_disc_region(p, P.DISC_HOLE_R + P.MEM_W - P.GROOVE_D))
            led = led.cut(_disc_region(p, P.DISC_HOLE_R + P.MEM_W - P.LED_SLOT[0]))
        grooves += [g, led]
    frame = frame.cut(union(grooves)).clean()
    log(f"frame network volume {frame.Volume() / 1e6:.2f} L")
    return body, frame, panels


def _ring_keep(p):
    """Material to keep around the slot-wall hole: annulus R..R+MEM_W through the shell depth."""
    yw, out = _wall(p)
    return ycyl(P.DISC_HOLE_R + P.MEM_W, yw - out * 2, yw + out * (P.MEM_H + 2)).cut(
        ycyl(P.DISC_HOLE_R, yw - out * 3, yw + out * (P.MEM_H + 3)))


def _hole_through(p):
    yw, out = _wall(p)
    return ycyl(P.DISC_HOLE_R, yw - out * 3, yw + out * (P.MEM_H + 3))


def _disc_region(p, r):
    yw, out = _wall(p)
    return ycyl(r, yw - out * 20, yw + out * 40)


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
    """Unit vector in the panel plane, perpendicular to edge ab, pointing into the panel."""
    n = panel["n"]
    e = (b - a).normalized()
    t = n.cross(e).normalized()
    # make sure it points toward the panel centroid
    c = V(*[sum(v[k] for v in panel["poly"]) / len(panel["poly"]) for k in range(3)])
    if (c - a).dot(t) < 0:
        t = t * -1
    return t


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


def _core_point(edge, panels, at, depth=10.5):
    """A point deep in the member's cross-section, clear of grooves and LED channels."""
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
    # ring segments around the slot-wall disc holes
    for p in panels:
        if not p["hole"]:
            continue
        yw, out = _wall(p)
        for k in range(6):
            a0 = math.radians(k * 60 + 15)
            a1 = a0 + math.radians(60)
            cx, cz = P.PIVOT
            sector = xz_prism([(cx, cz), (cx + 300 * math.cos(a0), cz + 300 * math.sin(a0)),
                               (cx + 300 * math.cos((a0 + a1) / 2), cz + 300 * math.sin((a0 + a1) / 2)),
                               (cx + 300 * math.cos(a1), cz + 300 * math.sin(a1))],
                              yw - out * 1.0, yw + out * (P.MEM_H + 1.0))
            ann = ycyl(P.DISC_HOLE_R + P.MEM_W + 0.6, yw - out * 1.5, yw + out * (P.MEM_H + 1.5)).cut(
                ycyl(P.DISC_HOLE_R - 1, yw - out * 2, yw + out * (P.MEM_H + 2)))
            regions.append((f"R{'R' if yw < 0 else 'L'}{k}", sector.intersect(ann), None, None, None))

    pieces, claimed = [], None
    for name, reg, ed, t0, t1 in regions:
        piece = frame.intersect(reg)
        if claimed is not None:
            piece = piece.cut(claimed)
        claimed = reg if claimed is None else claimed.fuse(reg)
        sol = [s for s in piece.Solids() if s.Volume() > 50]
        if not sol:
            continue
        pieces.append(dict(name=name, shape=cq.Compound.makeCompound(sol) if len(sol) > 1 else sol[0],
                           edge=ed, t0=t0, t1=t1))
    rest = frame.cut(claimed)
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
