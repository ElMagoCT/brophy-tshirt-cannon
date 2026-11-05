"""Printability numbers for every printed body part (frame pieces, clips, mounts, brackets, cups, grilles), from the
exported STEPs. No slicing. Run from cad/glacis after robot.py, with nothing else heavy running:
    ../.venv/bin/python render/part_report.py

For each part: volume, area, oriented box, and the best of a few lie-flat orientations (each oriented-box face and
each of the largest flat faces down): bed contact area, area that needs support (faces within 45 deg of straight down
that aren't on the bed), print height, and whether it fits a 250 mm cube. Also lists the printed parts each one touches
(within 0.3 mm). Writes out/part_report.json and docs/glacis/part_report.md.
"""
import json
import os
import sys

import cadquery as cq
import numpy as np
import trimesh
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

HERE = os.path.dirname(os.path.abspath(__file__))
STEP = os.path.join(HERE, "..", "out", "step")
OUT = os.path.join(HERE, "..", "out", "part_report.json")
DOC = os.path.join(HERE, "..", "..", "..", "docs", "glacis", "part_report.md")
BED = 250.0
FILES = ("body_frame", "body_panels_clips", "bumpers_wall_standoffs", "lights_speakers")


def load():
    out = []
    for f in sorted(os.listdir(STEP)):
        if not (f.startswith(FILES) and f.endswith(".step")):
            continue
        names = json.load(open(os.path.join(STEP, f[:-5] + ".names.json")))
        sols = cq.importers.importStep(os.path.join(STEP, f)).val().Solids()
        for n in names:
            if n.get("kind") != "print":
                continue
            c = cq.Vector(*n["c"])
            s = min(sols, key=lambda s: (s.BoundingBox().center - c).Length)
            out.append(dict(name=n["name"], bom=n.get("bom", ""), file=f, shape=s))
    return out


def tris(s):
    vs, ts = s.tessellate(0.5, 0.3)
    P = np.array([v.toTuple() for v in vs])
    T = np.array(ts)
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    n = np.cross(b - a, c - a)
    area = np.linalg.norm(n, axis=1) / 2
    nz = np.where(area[:, None] > 1e-9, n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-12), 0)
    return P, (a + b + c) / 3, nz, area


def orientations(s, P):
    """Candidate 'down' directions: the oriented box's six axes and the normals of the six largest flat faces."""
    A = P - P.mean(0)
    _, _, vt = np.linalg.svd(A, full_matrices=False)
    ds = [vt[i] * sg for i in range(3) for sg in (1, -1)]
    flats = []
    for f in s.Faces():
        if f.geomType() == "PLANE":
            n = f.normalAt()
            flats.append((f.Area(), np.array(n.toTuple())))
    for _, n in sorted(flats, key=lambda t: -t[0])[:6]:
        ds.append(n)
    uniq = []
    for d in ds:
        d = d / np.linalg.norm(d)
        if all(np.dot(d, u) < 0.999 for u in uniq):
            uniq.append(d)
    return uniq


def evaluate(d, P, C, N, area, mesh=None):
    h = P @ d                                  # height along 'down'; the bed is at max(h)
    hb = h.max()
    hc = C @ d
    down = N @ d                               # 1 = faces straight down onto the bed
    on_bed = (down > 0.999) & (hc > hb - 0.2)
    sup = (down > np.cos(np.radians(45))) & ~on_bed & (hc < hb - 0.2)
    sup_vol = 0.0
    if mesh is not None and sup.any():
        # cast straight down from each overhanging face: part within 8 mm below is a bridge the printer spans (a
        # tunnel roof, a hole): no support. Otherwise support from there to the bed or the part, at about 12%
        idx = np.nonzero(sup)[0]
        org = C[idx] + d * 0.05
        dirs = np.tile(d, (len(idx), 1))
        hit = np.full(len(idx), np.inf)
        try:
            locs, ri, _ = mesh.ray.intersects_location(org, dirs, multiple_hits=False)
            for k_, loc in zip(ri, locs):
                hit[k_] = float(np.dot(loc - org[k_], d))
        except Exception:
            pass
        bridge = hit < 8.0
        sup[idx[bridge]] = False
        gap = np.where(np.isfinite(hit), hit, hb - hc[idx])[~bridge]
        sup_vol = float((area[idx[~bridge]] * gap).sum() * 0.12)
    # footprint: project onto the plane normal to d, take its 2D oriented box
    u = np.cross(d, [1, 0, 0] if abs(d[0]) < 0.9 else [0, 1, 0])
    u /= np.linalg.norm(u)
    w = np.cross(d, u)
    Q = np.stack([P @ u, P @ w], 1)
    Q = Q - Q.mean(0)
    _, _, v2 = np.linalg.svd(Q, full_matrices=False)
    E = Q @ v2.T
    fp = sorted((E.max(0) - E.min(0)).tolist(), reverse=True)
    height = float(hb - h.min())
    return dict(bed=float(area[on_bed].sum()), support=float(area[sup].sum()), height=height, footprint=fp,
                fits=bool(fp[0] <= BED and fp[1] <= BED and height <= BED), sup_vol=sup_vol)


def sheets(parts, rows, per=12):
    """Contact sheets, `per` parts each: every part in its chosen print orientation, seen from above (the bed view)
    and from two sides, shaded by facing; red = faces that need support."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    d_out = os.path.join(HERE, "..", "out", "part_sheets")
    os.makedirs(d_out, exist_ok=True)
    for f in os.listdir(d_out):
        os.remove(os.path.join(d_out, f))
    order = sorted(range(len(rows)), key=lambda i: rows[i]["name"])
    for k in range(0, len(order), per):
        idx = order[k:k + per]
        fig, axs = plt.subplots(len(idx), 3, figsize=(10, 2.6 * len(idx)))
        axs = np.atleast_2d(axs)
        for row, i in enumerate(idx):
            r, s = rows[i], parts[i]["shape"]
            vs, ts = s.tessellate(0.8, 0.4)
            P = np.array([v.toTuple() for v in vs])
            T = np.array(ts)
            d = np.array(r["down"], float)
            u = np.cross(d, [1, 0, 0] if abs(d[0]) < 0.9 else [0, 1, 0])
            u /= np.linalg.norm(u)
            w = np.cross(d, u)
            up = -d
            a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
            n = np.cross(b - a, c - a)
            n = n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-12)
            hb = (P @ d).max()
            need = ((n @ d) > np.cos(np.radians(45))) & (((a + b + c) / 3 @ d) < hb - 0.2)
            for col, (ex, ey, look) in enumerate(((w, u, up), (u, up, w), (w, up, -u))):
                ax = axs[row, col]
                depth = ((a + b + c) / 3) @ look
                o = np.argsort(depth)
                polys = np.stack([np.stack([X @ ex, X @ ey], 1) for X in (a, b, c)], 1)[o]
                shade = np.clip(0.2 + 0.75 * np.abs(n @ look), 0, 1)[o]
                cols = np.stack([shade, shade, shade, np.ones_like(shade)], 1)
                cols[need[o]] = [0.9, 0.25, 0.2, 1.0]
                ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="none"))
                ax.autoscale()
                ax.set_aspect("equal")
                ax.tick_params(labelsize=6)
                if col == 0:
                    ax.set_title(f"{r['name']}  (bed view)", fontsize=8, loc="left")
                else:
                    ax.set_title("side, bed at the bottom", fontsize=7, loc="left")
        fig.tight_layout()
        fig.savefig(os.path.join(d_out, f"sheet_{k // per + 1:02d}.png"), dpi=70)
        plt.close(fig)


def main():
    parts = load()
    rows = []
    for p in parts:
        s = p["shape"]
        P, C, N, area = tris(s)
        vs, ts = s.tessellate(0.5, 0.3)
        mesh = trimesh.Trimesh(vertices=np.array([v.toTuple() for v in vs]), faces=np.array(ts), process=False)
        best = None
        for d in orientations(s, P):
            e = evaluate(d, P, C, N, area, mesh)
            # mm2: support costs, bed contact helps, and height costs (a long member stood on end is slow,
            # wobbly and weak across its layers): each 10 mm of height counts like 0.6 cm2 of support
            score = e["support"] - 0.5 * e["bed"] + 60.0 * e["height"] / 10.0 + (0 if e["fits"] else 1e7)
            if best is None or score < best[0]:
                best = (score, d, e)
        _, d, e = best
        A = P - P.mean(0)
        _, _, vt = np.linalg.svd(A, full_matrices=False)
        ex = A @ vt.T
        obb = sorted((ex.max(0) - ex.min(0)).tolist(), reverse=True)
        rows.append(dict(name=p["name"], bom=p["bom"], file=p["file"], volume_cm3=s.Volume() / 1000,
                         area_cm2=s.Area() / 100, solids=len(s.Solids()), obb_mm=obb,
                         down=[round(float(x), 3) for x in d], bed_cm2=e["bed"] / 100, support_cm2=e["support"] / 100,
                         support_cm3=e["sup_vol"] / 1000,
                         height_mm=e["height"], footprint_mm=e["footprint"], fits_250=e["fits"],
                         bbox=[s.BoundingBox().xmin, s.BoundingBox().ymin, s.BoundingBox().zmin,
                               s.BoundingBox().xmax, s.BoundingBox().ymax, s.BoundingBox().zmax]))
    # neighbours: printed parts within 0.3 mm
    for i, r in enumerate(rows):
        r["touches"] = []
    for i in range(len(rows)):
        bi = parts[i]["shape"].BoundingBox()
        for j in range(i + 1, len(rows)):
            bj = parts[j]["shape"].BoundingBox()
            if bi.xmin > bj.xmax + 0.3 or bj.xmin > bi.xmax + 0.3 or bi.ymin > bj.ymax + 0.3 or bj.ymin > bi.ymax + 0.3 \
                    or bi.zmin > bj.zmax + 0.3 or bj.zmin > bi.zmax + 0.3:
                continue
            dd = BRepExtrema_DistShapeShape(parts[i]["shape"].wrapped, parts[j]["shape"].wrapped)
            if dd.IsDone() and dd.Value() <= 0.3:
                rows[i]["touches"].append(rows[j]["name"])
                rows[j]["touches"].append(rows[i]["name"])
    json.dump(rows, open(OUT, "w"), indent=1)
    sheets(parts, rows)
    L = ["# Glacis printed body parts: printability report (from the CAD, not sliced)", "",
         "Best of the lie-flat orientations tried (each oriented-box face and each of the six largest flat faces down), "
         "scored on support, bed contact and height. Support = faces within 45 deg of straight down that aren't on the "
         "bed and have no part within 8 mm below them (closer is a bridge). Touches = printed parts within 0.3 mm.", "",
         "| Part | Vol (cm3) | Oriented box (mm) | Print height | Bed (cm2) | Support (cm2) | Fits 250 | Touches |",
         "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["name"]):
        L.append(f"| {r['name']} | {r['volume_cm3']:.1f} | {' x '.join(f'{x:.0f}' for x in r['obb_mm'])} | "
                 f"{r['height_mm']:.0f} | {r['bed_cm2']:.1f} | {r['support_cm2']:.1f} | {'yes' if r['fits_250'] else 'NO'} | "
                 f"{', '.join(sorted(r['touches']))} |")
    open(DOC, "w").write("\n".join(L) + "\n")
    print(f"{len(rows)} printed parts -> {os.path.relpath(OUT)}, {os.path.relpath(DOC)}")


if __name__ == "__main__":
    main()
