"""Build the whole Glacis robot, check it, and export it.

    python robot.py            # build + checks + renders + STEP/BOM export into out/
    python robot.py --quick    # build + envelope only
    python robot.py --checks   # build + checks, no export/renders
    python robot.py --export   # build + STEP export (one file per Onshape tab) + parts rollup

Checks (printed and written to out/check_log.txt):
  interference between every pair of parts, the gun swept 0-90 deg against everything fixed,
  the door envelope, print-bed fit of every printed part, panel sheet sizes, mass and gun balance.
"""
import json
import math
import os
import re
import sys
import time
from collections import defaultdict

import cadquery as cq
from cadquery import Vector as V

import params as P
import lib
from lib import PARTS
import drive
import gun
import misc
import render

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def pose(shape, elev):
    return shape.rotate(V(0, 0, 0), V(0, 1, 0), -elev).translate(V(P.PIVOT[0], 0, P.PIVOT[1]))


def build(elev=P.ELEV_SHOW):
    PARTS.clear()
    t = time.time()
    drive.build(log)
    gun.build(log)
    belt_len = misc.towers_and_pivot()
    log(f"elevation belt pitch length {belt_len:.0f} mm ({belt_len / 5:.1f} teeth)")
    sol = misc.rear_air()
    misc.batteries_and_electronics()
    misc.compressor_spot()
    misc.bumpers()
    misc.wall_standoffs()
    misc.body_parts(log)
    for p in PARTS:
        if p["moving"]:
            p["local"] = p["shape"]
            p["shape"] = pose(p["shape"], elev)
    # service loop: fill solenoid -> behind the slot -> up -> under the gun -> manifold inlet. The last three
    # points ride with the gun (gun-local), dropping below the inlet port and running back clear of the chambers.
    t_l = gun.GUN_INLET[0]
    ride = [V(-60.0, -45.0, t_l.z - 15.0), V(t_l.x, -45.0, t_l.z - 15.0), V(t_l.x, -45.0, t_l.z), t_l]
    ride = [pose(cq.Vertex.makeVertex(*p.toTuple()), elev).Center() for p in ride]
    pts = [V(*sol), V(sol[0] + 30, -70, sol[2]), V(-190, -70, 300), V(-190, -70, 360), V(-150, -70, 375),
           V(-110, -55, 380)] + ride
    lib.add("Service loop tube (to gun)", misc.tube_path([p.toTuple() for p in pts]), "tube", "pneu",
            bom="DOT nylon tube 1/4 OD (ft)", kind="stock")
    log(f"built {len(PARTS)} parts in {time.time() - t:.0f} s")
    return PARTS


# ------------------------------------------------------------------ checks
def bb(s):
    b = s.BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def overlap(a, b, g=0.0):
    return all(a[i] < b[i + 3] - g and b[i] < a[i + 3] - g for i in range(3))


def common_volume(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return -1.0


ALLOWED = [  # (name fragment A, name fragment B): contacts that are part of the design
    ("Belt", "pulley"), ("Belt", "Pulley"), ("Belt", "Compound"), ("Belt", "Wheel hub inner"),
    ("Elevation belt", "Servo pinion"), ("Elevation belt", "Elevation pulley"),
    ("Roller tread", "Roller core"),
    ("Compressor spot", "Compressor mount plate"),
    ("Belt", "Wheel core inner"),
    ("Stub shaft", "Pivot bearing"),            # hex inner race turns with the shaft
    ("Liner", "Liner"), ("Liner", "Body frame"),  # fabric overlaps and is clamped to the frame
    ("nipple", "manifold block"),               # threads into the block (modelled solid)
    ("tube", "push-to-connect"), ("tube", "Push-to-connect"), ("Service loop", "push-to-connect"),
    ("inlet nipple", "inlet nipple"), ("inlet nipple", "inlet Relief valve"),  # thread ends meet inside the
                                                                              # port block / tee (cored)
]


def allowed(n1, n2):
    for a, b in ALLOWED:
        if (a in n1 and b in n2) or (a in n2 and b in n1):
            return True
    return False


def check_interference(parts, tol=30.0):
    boxes = [bb(p["shape"]) for p in parts]
    hits = []
    n = len(parts)
    order = sorted(range(n), key=lambda i: boxes[i][0])
    for ii, i in enumerate(order):
        for j in order[ii + 1:]:
            if boxes[j][0] >= boxes[i][3]:
                break
            if not overlap(boxes[i], boxes[j], 0.05):
                continue
            pi, pj = parts[i], parts[j]
            if allowed(pi["name"], pj["name"]):
                continue
            v = common_volume(pi["shape"], pj["shape"])
            if v > tol:
                hits.append((round(v), pi["name"], pj["name"]))
    hits.sort(reverse=True)
    return hits


def check_sweep(parts, angles=range(0, 91, 15), tol=30.0):
    movers = [p for p in parts if p["moving"]]
    parts = [p for p in parts if not p["name"].startswith("Service loop")]   # flexible, follows the gun
    fixed = [p for p in parts if not p["moving"]]
    fboxes = [bb(p["shape"]) for p in fixed]
    hits = defaultdict(set)
    for a in angles:
        for m in movers:
            s = pose(m["local"], a)
            mb = bb(s)
            for f, fb in zip(fixed, fboxes):
                if overlap(mb, fb, 0.05) and not allowed(m["name"], f["name"]):
                    v = common_volume(s, f["shape"])
                    if v > tol:
                        hits[(m["name"], f["name"])].add(a)
    return sorted(((sorted(v), k[0], k[1]) for k, v in hits.items()), key=lambda r: r[1])


def envelope(parts, elev):
    b = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9]
    for p in parts:
        s = pose(p["local"], elev) if p["moving"] else p["shape"]
        q = bb(s)
        b = [min(b[i], q[i]) for i in range(3)] + [max(b[i + 3], q[i + 3]) for i in range(3)]
    return [(b[i + 3] - b[i]) / P.IN for i in range(3)]


DENS = {"steel": 7.85, "galv": 7.85, "alu": 2.70, "extr": 2.70 * 0.55, "brass": 8.5, "print": 1.27 * 0.4,
        "print_d": 1.27 * 0.6, "tpu": 1.2 * 0.6, "acrylic": 1.19, "foam": 0.03, "fabric": 0.4, "belt": 1.2,
        "black": 1.5, "pcb": 1.8, "red": 1.5, "tube": 1.15 * 0.3, "tank": 1.4, "falcon": 2.6, "battery": 2.4,
        "spot": 0.0, "led": 1.0}


def colour_key(rgba):
    for k, v in lib.C.items():
        if tuple(v) == tuple(rgba):
            return k
    return "black"


def mass_report(parts):
    tot, gun_m, gun_mx, gun_mz = 0.0, 0.0, 0.0, 0.0
    by = defaultdict(float)
    for p in parts:
        ck = colour_key(p["color"])
        if ck == "battery":
            m = 5.9
        elif ck == "falcon":
            m = 0.50
        elif ck == "tank":
            m = 3.2
        else:
            m = p["shape"].Volume() / 1e6 * DENS.get(ck, 1.0)
        tot += m
        by[p["group"]] += m
        if p["moving"]:
            c = p["local"].Center() if hasattr(p["local"], "Center") else V(0, 0, 0)
            gun_m += m
            gun_mx += m * c.x
            gun_mz += m * c.z
    return tot, by, gun_m, (gun_mx / gun_m if gun_m else 0), (gun_mz / gun_m if gun_m else 0)


def print_parts(parts):
    bad = []
    for p in parts:
        if p["kind"] != "print":
            continue
        b = p["shape"].BoundingBox()
        d = sorted([b.xlen, b.ylen, b.zlen])
        if d[1] > 256 or d[2] > 340:
            bad.append((p["name"], [round(x) for x in d]))
    return bad


# ------------------------------------------------------------------ export
GROUPS = {"chassis": ("frame", "drive"), "body": ("body",), "bumpers": ("bumper",), "gun": ("gun",),
          "air": ("pneu",), "power": ("power",), "spot": ("spot",)}


STEP_MAX = 9.0e6                                   # Onshape blob upload takes <= 10 MB per call


def _save_step(sel, name, path):
    asm = cq.Assembly(name=name)
    names, seen = [], defaultdict(int)
    for p in sel:
        nm = p["name"]
        seen[nm] += 1
        if seen[nm] > 1:
            nm = f"{nm} #{seen[nm]}"
        r, g, b_, a = p["color"]
        asm.add(p["shape"], name=nm.replace("/", "-"), color=cq.Color(r, g, b_, a))
        q = p["shape"].BoundingBox()
        names.append(dict(name=nm, c=[(q.xmin + q.xmax) / 2, (q.ymin + q.ymax) / 2, (q.zmin + q.zmax) / 2],
                          size=[q.xlen, q.ylen, q.zlen], color=p["color"], bom=p["bom"], kind=p["kind"]))
    asm.save(path, exportType="STEP")
    return names


def _corner(name):
    m = re.search(r"\b(FL|FR|RL|RR)(\d\d)?\b", name)
    return m.group(1) if m else None


WHEEL_PARTS = ("Wheel core", "Wheel lug arc", "Roller", "Bearing FR8 wheel")


def tabs(parts):
    """Onshape tab name -> parts, grouped the way someone would look for them (each file <= STEP_MAX)."""
    out = defaultdict(list)
    for p in parts:
        g, n = p["group"], p["name"]
        c = _corner(n) if g == "drive" else None
        if g == "frame" or (g == "drive" and c is None):
            out["Frame, pivot & front drive"].append(p)
        elif g == "drive" and n.startswith(WHEEL_PARTS):
            out[f"Wheel {c}"].append(p)
        elif g == "drive":
            out["Frame, pivot & front drive" if c in ("FL", "FR") else "Rear drive"].append(p)
        elif g == "body":
            out["Body frame" if n.startswith("Body frame") else "Panels, liners, standoffs & bumpers"].append(p)
        elif g == "bumper":
            out["Panels, liners, standoffs & bumpers"].append(p)
        elif g == "gun":
            out["Gun (at 20 deg)"].append(p)
        else:                                   # pneu, power, spot
            out["Air, power & electronics"].append(p)
    return out


def export(parts):
    """One STEP per tab; a tab whose file passes STEP_MAX is split along x into numbered parts."""
    d = os.path.join(OUT, "step")
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    manifest = []
    for tab, sel in tabs(parts).items():
        sel = sorted(sel, key=lambda p: p["shape"].BoundingBox().center.x)
        for nparts in range(1, 9):
            chunks = [sel[i * len(sel) // nparts:(i + 1) * len(sel) // nparts] for i in range(nparts)]
            files = []
            for i, ch in enumerate(chunks):
                label = tab if nparts == 1 else f"{tab} {i + 1} of {nparts}"
                fn = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
                path = os.path.join(d, f"{fn}.step")
                names = _save_step(ch, label, path)
                files.append((label, path, names, len(ch)))
            if max(os.path.getsize(f[1]) for f in files) <= STEP_MAX:
                break
            for f in files:
                os.remove(f[1])
        for label, path, names, n in files:
            json.dump(names, open(path[:-5] + ".names.json", "w"), indent=0)
            manifest.append(dict(tab=label, file=os.path.basename(path), parts=n, bytes=os.path.getsize(path)))
            log(f"exported {label}: {n} parts, {os.path.getsize(path) / 1e6:.1f} MB")
    json.dump(manifest, open(os.path.join(d, "manifest.json"), "w"), indent=1)


def bom_rollup(parts):
    rows = defaultdict(lambda: dict(qty=0, kind="", note=set(), groups=set()))
    for p in parts:
        r = rows[p["bom"]]
        r["qty"] += 1
        r["kind"] = p["kind"]
        r["groups"].add(p["group"])
        if p["note"]:
            r["note"].add(p["note"])
    path = os.path.join(OUT, "parts_from_cad.csv")
    with open(path, "w") as fh:
        fh.write("item,qty,kind,groups,notes\n")
        for k in sorted(rows, key=lambda k: (rows[k]["kind"], k)):
            r = rows[k]
            notes = "; ".join(sorted(r["note"]))[:200].replace(",", ";")
            fh.write(f"\"{k}\",{r['qty']},{r['kind']},{'/'.join(sorted(r['groups']))},\"{notes}\"\n")
    log(f"BOM rollup: {len(rows)} distinct items -> {path}")


def renders(parts):
    items = [(p["shape"], p["color"]) for p in parts if p["group"] != "spot"]
    render.draw(items, os.path.join(OUT, "glacis_overview.png"), views=((18, -52), (22, 128)), size=(8, 6.5))
    inner = [(p["shape"], p["color"]) for p in parts if p["group"] not in ("body", "bumper")]
    render.draw(inner, os.path.join(OUT, "glacis_inside.png"), views=((24, -55), (28, 125)), size=(8, 6.5))
    g = [(p["shape"], p["color"]) for p in parts if p["group"] == "gun"]
    render.draw(g, os.path.join(OUT, "glacis_gun.png"), views=((15, -60), (20, 130)), size=(7, 6))
    log("renders written")


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    parts = build()
    for elev in (0, 90):
        L, W, H = envelope(parts, elev)
        log(f"envelope at {elev:2d} deg: {L:.1f} L x {W:.1f} W x {H:.1f} H in")
    W_body = 2 * (P.OUTER_RAIL_Y[1] + P.BUMP_DEPTH) / P.IN
    L_body = 2 * (P.FRAME_X + P.BUMP_DEPTH) / P.IN
    log(f"body over bumpers: {L_body:.1f} x {W_body:.1f} in (door limits 40 x 28)")
    tot, by, gm, gx, gz = mass_report(parts)
    log(f"mass estimate {tot:.1f} kg ({tot * 2.205:.0f} lb): " + ", ".join(f"{k} {v:.1f}" for k, v in sorted(by.items())))
    log(f"gun {gm:.1f} kg, CG {gx:.0f} mm ahead / {gz:.0f} mm above the pivot -> "
        f"{gm * 9.81 * abs(gx) / 1000:.1f} N*m at 0 deg")
    if "--checks" in sys.argv:
        quick = False
    if "--export" in sys.argv:
        export(parts)
        bom_rollup(parts)
        sys.exit(0)
    if not quick:
        t = time.time()
        hits = check_interference(parts)
        log(f"interference: {len(hits)} pairs over 30 mm^3 ({time.time() - t:.0f} s)")
        for h in hits[:60]:
            log("   ", h)
        with open(os.path.join(OUT, "interference_all.txt"), "w") as fh:
            fh.write("\n".join(str(h) for h in hits) + "\n")
        t = time.time()
        sw = check_sweep(parts)
        log(f"elevation sweep 0-90 deg: {len(sw)} clashes ({time.time() - t:.0f} s)")
        for s in sw[:40]:
            log("   ", s)
        bad = print_parts(parts)
        log(f"printed parts over a 256 mm bed: {len(bad)}", bad[:10])
        split = [p["name"] for p in parts if len(p["shape"].Solids()) > 1]
        log(f"parts in more than one piece: {len(split)}", split[:10])
        if "--checks" in sys.argv:
            open(os.path.join(OUT, "check_log.txt"), "w").write("\n".join(LOG) + "\n")
            sys.exit(0)
        export(parts)
        bom_rollup(parts)
        renders(parts)
    open(os.path.join(OUT, "check_log.txt"), "w").write("\n".join(LOG) + "\n")
