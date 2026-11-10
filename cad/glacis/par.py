"""Run the slow, independent OCC jobs on every core (Micah 2026-11-10: "run it a bit harder").

OCC shapes can't be pickled, so each job's shapes go to a scratch directory as .brep files once; worker processes
load them (and keep them) by path. Used by body.section (one job per frame region), robot's interference and sweep
checks (one job per candidate pair) and robot.export (one job per Onshape tab). Set GLACIS_JOBS=1 to run serially.
"""
import math
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor

import cadquery as cq
from cadquery import Vector as V

JOBS = int(os.environ.get("GLACIS_JOBS", max(1, int((os.cpu_count() or 2) * 0.9))))   # Micah: up to 90% of the CPU
_TMP = None
_CACHE = {}
_POOL = None


def tmpdir():
    global _TMP
    if _TMP is None:
        _TMP = tempfile.mkdtemp(prefix="glacis_par_")
    return _TMP


_N = [0]


def save(shape, key):
    _N[0] += 1                                        # unique per save: workers cache shapes by path
    path = os.path.join(tmpdir(), f"{key}_{_N[0]}.brep")
    shape.exportBrep(path)
    return path


def load(path):
    s = _CACHE.get(path)
    if s is None:
        s = cq.Shape.importBrep(path)
        if len(_CACHE) > 400:
            _CACHE.clear()
        _CACHE[path] = s
    return s


def pool():
    global _POOL
    if _POOL is None:
        _POOL = ProcessPoolExecutor(max_workers=JOBS)
    return _POOL


def run(fn, jobs, chunk=1):
    """fn(job) for every job, on the pool (in order); serially when GLACIS_JOBS=1."""
    jobs = list(jobs)
    if JOBS <= 1 or len(jobs) <= 1:
        return [fn(j) for j in jobs]
    return list(pool().map(fn, jobs, chunksize=chunk))


def _bb(s):
    b = s.BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def _over(a, b, g=0.0):
    return all(a[i] < b[i + 3] - g and b[i] < a[i + 3] - g for i in range(3))


# ------------------------------------------------------------------ body.section: one frame region per job
def section_piece(job):
    frame_p, reg_ps, k = job
    import body
    frame, reg = load(frame_p), load(reg_ps[k])
    piece = body._robust(frame.intersect, reg)
    rb = _bb(reg)
    for j in range(k):
        prev = load(reg_ps[j])
        if _over(rb, _bb(prev)):
            piece = body._robust(piece.cut, prev)
    sol = [s for s in piece.Solids() if s.Volume() > 50]
    if not sol:
        return None
    return save(cq.Compound.makeCompound(sol) if len(sol) > 1 else sol[0], f"piece{k}")


def section_rest(job):
    frame_p, reg_ps = job
    import body
    rest = load(frame_p)
    for p in reg_ps:
        rest = body._robust(rest.cut, load(p))
    return save(rest, "rest")


def section_all(frame, regs):
    """(pieces per region or None, what's left of the frame) for body.section, with the leftover as one more job."""
    fp = save(frame, "frame")
    rps = [save(r, f"reg{k}") for k, r in enumerate(regs)]
    jobs = [("rest", (fp, rps))] + [("piece", (fp, rps, k)) for k in range(len(rps))]
    out = run(_section_dispatch, jobs)
    rest = load(out[0])
    return [load(p) if p else None for p in out[1:]], rest


def _section_dispatch(job):
    kind, args = job
    return section_rest(args) if kind == "rest" else section_piece(args)


# ------------------------------------------------------------------ checks: one candidate pair per job
def _common(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return -1.0


def pair_volume(job):
    pa, pb = job
    return _common(load(pa), load(pb))


def pose(shape, elev, pivot):
    return shape.rotate(V(0, 0, 0), V(0, 1, 0), -elev).translate(V(pivot[0], 0, pivot[1]))


def swept_volume(job):
    pm, ang, pf, pivot = job
    return _common(pose(load(pm), ang, pivot), load(pf))


# ------------------------------------------------------------------ export: one Onshape tab per job
def export_tab(job):
    tab, items, d, step_max = job
    import re
    import robot
    sel = []
    for it in items:
        s = load(it["path"])
        sel.append(dict(it, shape=s, local=s, moving=False))
    for nparts in range(1, 25):
        chunks = [sel[i * len(sel) // nparts:(i + 1) * len(sel) // nparts] for i in range(nparts)]
        files = []
        for i, ch in enumerate(chunks):
            label = tab if nparts == 1 else f"{tab} {i + 1} of {nparts}"
            fn = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
            path = os.path.join(d, f"{fn}.step")
            names = robot._save_step(ch, label, path)
            files.append((label, path, names, len(ch)))
        if max(os.path.getsize(f[1]) for f in files) <= step_max or nparts == 24:
            return files
        for f in files:
            os.remove(f[1])


# ------------------------------------------------------------------ body.section: which pieces touch (the slow bit)
def piece_dist(job):
    pa, pb = job
    try:
        return load(pa).distance(load(pb))
    except Exception:
        return -1.0                                   # body.section treats a failed distance as it always did


def touch_table(shapes, margin=1.0):
    """{(i, j): distance} for every pair of shapes whose boxes come within margin, on the pool (i < j)."""
    bbs = [_bb(s) for s in shapes]
    cand = [(i, j) for i in range(len(shapes)) for j in range(i + 1, len(shapes))
            if all(bbs[i][k] < bbs[j][k + 3] + margin and bbs[j][k] < bbs[i][k + 3] + margin for k in range(3))]
    paths = {k: save(shapes[k], f"tp{k}") for k in sorted({k for c in cand for k in c})}
    return dict(zip(cand, run(piece_dist, [(paths[i], paths[j]) for i, j in cand], chunk=2)))


def fuse_try(job):
    """body.section's node-into-segment trial: (union's brep, single solid that fits the bed) or None."""
    ps, pn = job
    import body
    try:
        u = load(ps).fuse(load(pn)).clean()
    except Exception:
        return None
    return save(u, f"fu_{os.path.basename(ps)[:-5]}_{os.path.basename(pn)[:-5]}"),         len(u.Solids()) == 1 and body.fits_bed(u, body.MERGE_BED)


def inside_first(job):
    """body.add_joints: index of the first piece that holds the probe point, or None."""
    paths, pt = job
    for k, pp in enumerate(paths):
        s = load(pp)
        b = _bb(s)
        if all(b[i] - 0.2 <= pt[i] <= b[i + 3] + 0.2 for i in range(3)) and s.isInside(V(*pt), 0.1):
            return k
    return None
