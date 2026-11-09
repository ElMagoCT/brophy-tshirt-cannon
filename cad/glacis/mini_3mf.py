"""Slice the desk mini kit (mini.py) into one editable OrcaSlicer project per printer, all four running at once.

    python mini_3mf.py               # slice the kit mini.py last built
    python mini_3mf.py --fit         # find the largest scale whose slowest plate is about 3 h on Ludicrous, build it

Plates (every piece is already in its print orientation; Orca arranges each plate):
  CC2 #1  body         white PETG, black PETG (everything below the bumper), PLA support interface
  CC2 #2  gun          white PETG, PLA support interface
  CC1 #1  black kit    black PETG: two speakers, the light bar, both chambers (they peg into the cradle)
  CC1 #2  red windows  red PETG: the eight acrylic windows, printed flat, outer face down
Glue-ins go in with a dot of CA; each seat leaves KIT_CLR (mini.py) per side.

0.4 nozzles, Orca's 0.20 mm Standard process for each printer, supports organic with slim branches. PLA only ever
touches PETG as support interface (it lets go cleanly, so no z gap). Profiles are Orca's own Elegoo presets, flattened
from github.com/SoftFever/OrcaSlicer resources/profiles (2026-11-08) into mini_orca/.

Ludicrous: the Centauri's speed modes are Silent 60 %, Balanced 100 %, Sport 133 %, Ludicrous 166 % (reviews of
the CC1; assumed the same on the CC2). Ludicrous only scales motion, and small parts are acceleration-bound, so
the budget is a Balanced estimate of NORMAL_BUDGET_H (about LUDICROUS_GAIN faster on Ludicrous).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mini")
PROF = os.path.join(HERE, "mini_orca")
WORK = os.path.join(tempfile.gettempdir(), "glacis_mini_slice")   # inputs, settings and Orca logs

TARGET_H = 3.0
LUDICROUS_GAIN = 1.5                     # realistic, below the nominal 1.66
NORMAL_BUDGET_H = TARGET_H * LUDICROUS_GAIN

WHITE, RED, BLACK, PLA = "#FFFFFF", "#C8102E", "#000000", "#F2E6A0"
CC2 = dict(machine="machine_Elegoo_Centauri_Carbon_2_0.4_nozzle.json",
           process="process_0.20mm_Standard_Elegoo_CC2_0.4_nozzle.json",
           petg="filament_Elegoo_PETG_ECC2.json", pla="filament_Elegoo_PLA_ECC2.json")
CC1 = dict(machine="machine_Elegoo_Centauri_Carbon_0.4_nozzle.json",
           process="process_0.20mm_Standard_Elegoo_CC_0.4_nozzle.json",
           petg="filament_Elegoo_PETG_ECC.json")


def plates(kit):
    black = [p["file"] for p in kit if p["colour"] == "black"]
    red = [p["file"] for p in kit if p["colour"] == "red"]
    return [
        dict(file="glacis_mini_CC2-1_body.3mf", printer=CC2, filaments=[(WHITE, "petg"), (BLACK, "petg"), (PLA, "pla")],
             objects={"body": [("body_white.stl", 1), ("body_black.stl", 2)]}, support=(2, 3)),
        dict(file="glacis_mini_CC2-2_gun.3mf", printer=CC2, filaments=[(WHITE, "petg"), (PLA, "pla")],
             objects={"gun": [("gun_white.stl", 1)]}, support=(1, 2)),
        dict(file="glacis_mini_CC1-1_black_kit.3mf", printer=CC1, filaments=[(BLACK, "petg")],
             objects={f[:-4]: [(f, 1)] for f in black}, support=(1, 1)),
        dict(file="glacis_mini_CC1-2_red_windows.3mf", printer=CC1, filaments=[(RED, "petg")],
             objects={f[:-4]: [(f, 1)] for f in red}, support=None),
    ]


SUPPORT = {
    "enable_support": "1",
    "support_type": "tree(auto)",
    "support_style": "organic",
    "tree_support_branch_diameter_organic": "1.5",      # slim branches (default 2)
    "tree_support_tip_diameter": "0.6",
    "support_interface_top_layers": "2",
    "support_on_build_plate_only": "1",                 # the bumper ring and barrels; notch roofs bridge, and supports
                                                        # up the body cost a filament change every layer
}


def orca_exe():
    exe = shutil.which("orca-slicer") or shutil.which("orca-slicer.exe")
    if not exe:
        sys.exit("orca-slicer not found: install OrcaSlicer")
    return exe


def write_input(path, objects):
    """A plain 3MF: one object per entry, each made of mesh components (its colour parts), and the Orca/Bambu
    model_settings.config that gives each part its filament slot. Orca arranges the plate."""
    meshes, objs, nid = [], [], 1
    for k, (name, parts) in enumerate(objects.items()):
        comps = []
        for f, slot in parts:
            m = trimesh.load(os.path.join(OUT, f))
            m.apply_translation((128.0 + 3.0 * k, 128.0, 0))
            meshes.append((nid, m))
            comps.append((nid, slot, f[:-4]))
            nid += 1
        objs.append((nid, name, comps))
        nid += 1
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
         '<resources>']
    for i, m in meshes:
        x.append(f'<object id="{i}" type="model"><mesh><vertices>')
        x += [f'<vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}"/>' for v in m.vertices]
        x.append('</vertices><triangles>')
        x += [f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces]
        x.append('</triangles></mesh></object>')
    for oid, name, comps in objs:
        x.append(f'<object id="{oid}" type="model" name="{name}"><components>')
        x += [f'<component objectid="{cid}"/>' for cid, _, _ in comps]
        x.append('</components></object>')
    x.append('</resources><build>')
    x += [f'<item objectid="{oid}"/>' for oid, _, _ in objs]
    x.append('</build></model>')
    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    for oid, name, comps in objs:
        cfg += [f'  <object id="{oid}">', f'    <metadata key="name" value="{name}"/>',
                '    <metadata key="extruder" value="1"/>']
        for cid, slot, pname in comps:
            cfg += [f'    <part id="{cid}" subtype="normal_part">', f'      <metadata key="name" value="{pname}"/>',
                    f'      <metadata key="extruder" value="{slot}"/>', '    </part>']
        cfg.append('  </object>')
    cfg.append('</config>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", "\n".join(x))
        z.writestr("Metadata/model_settings.config", "\n".join(cfg))


def write_settings(plate, tag):
    pr = plate["printer"]
    m = json.load(open(os.path.join(PROF, pr["machine"])))
    p = json.load(open(os.path.join(PROF, pr["process"])))
    p["name"] = f"{p['name']} - Glacis mini"
    p["from"] = "User"                                   # flattened: no "inherits" (the CLI can't resolve system presets)
    if plate["support"]:
        p.update(SUPPORT)
        base, iface = plate["support"]
        p["support_filament"], p["support_interface_filament"] = str(base), str(iface)
        if iface != base:                                # PLA interface on PETG: no gap
            p["support_top_z_distance"] = p["support_bottom_z_distance"] = "0"
    else:
        p["enable_support"] = "0"
    multi = len(plate["filaments"]) > 1
    p["enable_prime_tower"] = "1" if multi else "0"
    p["wipe_tower_x"], p["wipe_tower_y"] = ["215"], ["215"]
    files = {"machine.json": m, "process.json": p}
    fl = []
    for i, (colour, kind) in enumerate(plate["filaments"]):
        c = json.load(open(os.path.join(PROF, pr[kind])))
        c["filament_colour"] = [colour]
        # PLA interface on PETG: Orca refuses mixed temperatures unless each filament's print temperature sits in the
        # others' *recommended* range. Widen only those advisory ranges (print temperatures are unchanged)
        if multi and c["filament_type"] == ["PLA"]:
            c["nozzle_temperature_range_high"] = ["250"]
        elif multi:
            c["nozzle_temperature_range_low"] = ["210"]
        c["name"] = f"{c['name']} - Glacis mini slot {i + 1}"
        c["from"] = "User"
        fn = f"{tag}_filament_{i + 1}.json"
        files[fn] = c
        fl.append(fn)
    paths = {}
    for fn, c in files.items():
        out = os.path.join(WORK, fn if fn.startswith(tag) else f"{tag}_{fn}")
        with open(out, "w") as fh:
            json.dump(c, fh, indent=1)
        paths[fn] = out
    return [paths["machine.json"], paths["process.json"]], [paths[f] for f in fl]


def summary(path):
    """Balanced-mode print time (h), grams per slot and filament changes from a sliced project's plate G-code."""
    with zipfile.ZipFile(path) as z:
        g = z.read(next(n for n in z.namelist() if n.endswith(".gcode"))).decode("utf-8", "replace")
    lines = g.splitlines()
    head = "\n".join(l for l in lines[:400] + lines[-400:] if l.startswith(";"))
    t = re.search(r"; estimated printing time \(normal mode\) = ([^\n]+)", head).group(1).strip()
    hrs = sum(float(n) * {"d": 24, "h": 1, "m": 1 / 60, "s": 1 / 3600}[u] for n, u in re.findall(r"(\d+)([dhms])", t))
    used = re.search(r"; filament used \[g\] = ([^\n]+)", head)
    ch = re.search(r"; total filament change = (\d+)", head)
    return dict(time=t, hours=round(hrs, 2), ludicrous_h=round(hrs / LUDICROUS_GAIN, 2),
                grams=used.group(1).strip() if used else "?", changes=int(ch.group(1)) if ch else 0)


def slice_plate(plate):
    tag = plate["file"].split("_")[2]
    src = os.path.join(WORK, f"{tag}_parts.3mf")
    write_input(src, plate["objects"])
    st, fil = write_settings(plate, tag)
    dst = os.path.join(OUT, plate["file"])
    if os.path.exists(dst):
        os.remove(dst)
    cmd = [orca_exe(), "--load-settings", ";".join(st), "--load-filaments", ";".join(fil), "--arrange", "1",
           "--orient", "0", "--slice", "0", "--export-3mf", os.path.basename(dst), "--outputdir", OUT, src]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, cwd=WORK)
    log = (r.stdout or "") + (r.stderr or "")
    with open(os.path.join(WORK, f"{tag}_orca_log.txt"), "w", encoding="utf-8") as fh:
        fh.write(" ".join(cmd) + "\n\n" + log)
    if r.returncode != 0 or not os.path.exists(dst):
        print(log[-2000:])
        sys.exit(f"Orca failed on {plate['file']} (exit {r.returncode}); log in {WORK}")
    stray = os.path.join(OUT, "plate_1.gcode")              # Orca also drops the bare G-code next to the project
    if os.path.exists(stray):
        os.remove(stray)
    return summary(dst)


def slice_all():
    kit = json.load(open(os.path.join(OUT, "kit.json")))
    os.makedirs(WORK, exist_ok=True)
    res = {}
    for pl in plates(kit["pieces"]):
        res[pl["file"]] = slice_plate(pl)
        print(f"  {pl['file']}: {res[pl['file']]}", flush=True)
    return kit["scale"], res


def fit():
    """Largest scale (1:N, N >= mini.SCALE floor of a 2 in wheelbase... i.e. N <= 10) whose slowest plate fits."""
    import mini
    lo_n, hi_n = 10.0, 5.0                       # 1:10 floor (2 in wheelbase); 1:5 would overflow the bed
    best = None
    for _ in range(6):
        n = round((lo_n + hi_n) / 2, 2) if best else 10.0
        print(f"--- trying 1:{n:g}", flush=True)
        if not mini.build(n, render_previews=False):
            hi_n = n
            continue
        _, res = slice_all()
        slow = max(r["hours"] for r in res.values())
        print(f"    slowest plate {slow:.2f} h Balanced (~{slow / LUDICROUS_GAIN:.2f} h Ludicrous)", flush=True)
        if slow <= NORMAL_BUDGET_H:
            best, lo_n = n, n
        else:
            if n == 10.0:
                best = 10.0                      # can't go below the wheelbase floor
                break
            hi_n = n
        if best and abs(lo_n - hi_n) < 0.25:
            break
    print(f"=== best 1:{best:g}", flush=True)
    mini.build(best, render_previews=True)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true", help="search the scale, then build and slice the winner")
    a = ap.parse_args()
    if a.fit:
        fit()
    scale, res = slice_all()
    with open(os.path.join(OUT, "slice_report.json"), "w") as fh:
        json.dump(dict(scale=scale, target_ludicrous_h=TARGET_H, ludicrous_gain=LUDICROUS_GAIN, plates=res), fh,
                  indent=1)
    print(f"1:{scale:g} sliced; slowest plate ~{max(r['ludicrous_h'] for r in res.values()):.2f} h on Ludicrous")


if __name__ == "__main__":
    main()
