"""Print estimate for the body frame (no slicing): PETG, 0.6 mm nozzle, 0.3 mm layers, 2 walls, 10% gyroid, on an
Elegoo Centauri Carbon (CC1) and Centauri Carbon 2 (CC2), both 256 mm cubed (250 x 250 usable).

    cd cad/glacis && ../.venv/bin/python render/part_report.py && ../.venv/bin/python render/print_plan.py

Reads out/part_report.json (each printed part in the orientation it prints in) and writes docs/glacis/print_plan.md.
The model, per piece, from its volume V, surface area A and its support estimate S (part_report: overhangs with no
part within 8 mm below them, filled at about 12%):
  shell  = min(V, A x t)  t = the wall thickness: 2 walls of a 0.6 mm nozzle is about 1.3 mm (3 walls, 1.95)
  infill = 10% of (V - shell)
  extra  = 3% for brims and purge, plus S
  time   = extruded volume / 9 mm3/s (the CC's real average with 0.6 mm PETG: walls, travel, small layers) + 6 min a plate
Plates are packed from each part's footprint in its print orientation (MaxRects), 6 mm apart.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "..", "out", "part_report.json")
DOC = os.path.join(HERE, "..", "..", "..", "docs", "glacis", "print_plan.md")

BED, GAP = 250.0, 6.0
WALL, INFILL, EXTRA, RATE, PLATE_MIN, RHO = 1.3, 0.10, 0.03, 9.0, 6.0, 1.27
WALL3 = 1.95                                      # 3 walls: Micah's "hollow to 2 mm" read literally
SMALL_WALL, SMALL_INFILL = 2.6, 0.25              # clips, mounts, brackets, cups: 4 walls, 25%
PRICE_KG = 13.0                                   # PETG, about $13 a kg (Elegoo/Sunlu 1 kg spools)


def extrusion(r, wall, infill):
    V, A = r["volume_cm3"] * 1000, r["area_cm2"] * 100
    shell = min(V, A * wall)
    return (shell + infill * max(0.0, V - shell)) * (1 + EXTRA) + r.get("support_cm3", 0.0) * 1000


def pack(items):
    """MaxRects (best short side fit) packing of (name, w, d) footprints, each grown by GAP, into BED x BED plates;
    each piece may turn 90 deg. Tries a few orders and keeps the one with the fewest plates, then the fullest first
    plates."""
    best = None
    for key in (lambda t: -max(t[1], t[2]), lambda t: -t[1] * t[2], lambda t: -min(t[1], t[2])):
        plates = _maxrects(sorted(items, key=key))
        score = (len(plates), -sum(len(p["items"]) ** 2 for p in plates))
        if best is None or score < best[0]:
            best = (score, plates)
    return best[1]


def _maxrects(items):
    S = BED + GAP                                  # each footprint carries a GAP margin on two sides
    plates = []
    for name, a, b in items:
        w0, d0 = a + GAP, b + GAP
        choice = None
        for pi, pl in enumerate(plates + [dict(free=[(0.0, 0.0, S, S)], items=[])]):
            for fx, fy, fw, fh in pl["free"]:
                for w, d in ((w0, d0), (d0, w0)):
                    if w <= fw + 1e-6 and d <= fh + 1e-6:
                        sc = (pi, min(fw - w, fh - d), max(fw - w, fh - d))
                        if choice is None or sc < choice[0]:
                            choice = (sc, pi, (fx, fy, w, d))
            if choice is not None and choice[1] == pi:
                break                                  # first plate it fits on
        _, pi, r = choice
        if pi == len(plates):
            plates.append(dict(free=[(0.0, 0.0, S, S)], items=[]))
        pl = plates[pi]
        pl["items"].append(name)
        rx, ry, rw, rh = r
        new = []
        for fx, fy, fw, fh in pl["free"]:              # split every free rect the new piece overlaps
            if rx >= fx + fw or rx + rw <= fx or ry >= fy + fh or ry + rh <= fy:
                new.append((fx, fy, fw, fh))
                continue
            if rx > fx:
                new.append((fx, fy, rx - fx, fh))
            if rx + rw < fx + fw:
                new.append((rx + rw, fy, fx + fw - rx - rw, fh))
            if ry > fy:
                new.append((fx, fy, fw, ry - fy))
            if ry + rh < fy + fh:
                new.append((fx, ry + rh, fw, fy + fh - ry - rh))
        new = list(dict.fromkeys(f for f in new if f[2] > 1e-6 and f[3] > 1e-6))
        pl["free"] = [f for i, f in enumerate(new) if not any(j != i and g[0] <= f[0] and g[1] <= f[1] and
                                                              g[0] + g[2] >= f[0] + f[2] and g[1] + g[3] >= f[1] + f[3]
                                                              for j, g in enumerate(new))]
    return plates


def plan(rows, wall, infill):
    for r in rows:
        r["ext"] = extrusion(r, wall, infill)
        r["g"] = r["ext"] / 1000 * RHO
        r["min"] = r["ext"] / RATE / 60
    by = {r["name"]: r for r in rows}
    plates = pack([(r["name"], r["footprint_mm"][0], r["footprint_mm"][1]) for r in rows])
    for pl in plates:
        pl["min"] = sum(by[n]["min"] for n in pl["items"]) + PLATE_MIN
        pl["g"] = sum(by[n]["g"] for n in pl["items"])
    load = {"CC1": 0.0, "CC2": 0.0}                # two printers: longest plate first to whichever finishes sooner
    for pl in sorted(plates, key=lambda p: -p["min"]):
        k = min(load, key=load.get)
        pl["printer"] = k
        load[k] += pl["min"]
    return plates, load


def main():
    rows = json.load(open(REPORT))
    frame = [dict(r, name=r["name"].replace("Body frame ", "")) for r in rows if r["name"].startswith("Body frame")]
    other = [r for r in rows if not r["name"].startswith("Body frame")]
    plates, load = plan(frame, WALL, INFILL)
    tot_g = sum(r["g"] for r in frame)
    sup_g = sum(r.get("support_cm3", 0.0) for r in frame) * RHO
    tot_min = sum(pl["min"] for pl in plates)
    plates3, load3 = plan([dict(r) for r in frame], WALL3, INFILL)
    g3 = sum(extrusion(r, WALL3, INFILL) for r in frame) / 1000 * RHO
    oplates, oload = plan(other, SMALL_WALL, SMALL_INFILL)
    og = sum(r["g"] for r in other)
    flags = []
    for r in frame:
        if r["volume_cm3"] < 30:
            flags.append(f"{r['name']}: small ({r['volume_cm3']:.0f} cm3)")
        if r["bed_cm2"] < 2:
            flags.append(f"{r['name']}: only {r['bed_cm2']:.1f} cm2 on the bed: use a brim")
        if r.get("support_cm3", 0) > 8:
            flags.append(f"{r['name']}: {r['support_cm3']:.0f} cm3 of support")
    L = ["# Glacis body frame: print plan (estimate, not sliced)", "",
         f"PETG, 0.6 mm nozzle, 0.3 mm layers, 2 walls, 10% gyroid. Elegoo Centauri Carbon (CC1) and Centauri Carbon 2 "
         f"(CC2), both 256 mm cubed, packed to {BED:.0f} x {BED:.0f} mm.", "",
         "## Totals", "",
         f"- **{len(frame)} frame pieces on {len(plates)} plates**",
         f"- **PETG: {tot_g / 1000:.2f} kg** (about ${tot_g / 1000 * PRICE_KG:.0f} at ${PRICE_KG:.0f}/kg), including "
         f"{sup_g:.0f} g of support and 3% for brims and purge",
         f"- **Machine time: {tot_min / 60:.0f} h** in all; with both printers going, **{max(load.values()) / 60:.0f} h** "
         f"(CC1 {load['CC1'] / 60:.0f} h, CC2 {load['CC2'] / 60:.0f} h)",
         f"- \"Hollow to 2 mm\" read as walls 2 mm thick is 3 walls: {g3 / 1000:.2f} kg and "
         f"{max(load3.values()) / 60:.0f} h on both printers. Nothing is hollowed in the CAD: the slicer makes every "
         "piece a shell over sparse infill already, and a modelled hollow would add inner walls.",
         f"- The other printed body parts (clips, mount posts, tower and corner brackets, underglow and light bar "
         f"brackets, speaker cups and grilles; 4 walls, 25%): {len(other)} parts, {og / 1000:.2f} kg, "
         f"{len(oplates)} plates, {max(oload.values()) / 60:.0f} h on both printers.",
         f"- Model: shell = surface area x {WALL} mm, infill 10% of the rest, support from part_report (overhangs "
         f"with nothing within 8 mm below, at 12%), at {RATE:.0f} mm3/s average plus {PLATE_MIN:.0f} min a plate. "
         "Treat it as +/-25%: a slicer run on the CC's PETG profile will be closer.", "",
         "## Before the frame", "",
         "- Print a test joint first on each printer: two 40 mm stubs with one tapered tenon (TENON_CLEAR is 0.3 mm a "
         "side for the 0.6 nozzle). If it doesn't seat fully by hand, raise TENON_CLEAR and rebuild before the plates.",
         "- Lit faces: the frame glows through its outer 7 mm. Sparse gyroid there shows as dark lines, so give the 12 mm "
         "lip a 100% infill modifier (about +10% plastic) or print the lit pieces at 4 walls. Don't put 4-wall modifiers "
         "round the tenons and inserts on lit faces: they show as dark spots.",
         "- Glued joints (the filled LED corners): before the epoxy, push a strip offcut through the tunnel across the "
         "joint and pull it out after, so squeeze-out can't block the strip.", "",
         "## Plates", "", "| Plate | Printer | Pieces | PETG (g) | Time (h) |", "|---|---|---|---|---|"]
    for i, pl in enumerate(sorted(plates, key=lambda p: (p["printer"], -p["min"]))):
        L.append(f"| {i + 1} | {pl['printer']} | {', '.join(sorted(pl['items']))} | {pl['g']:.0f} | {pl['min'] / 60:.1f} |")
    L += ["", "## Pieces", "", "| Piece | Footprint x height (mm) | Volume (cm3) | Support (cm3) | PETG (g) | Time (min) |",
          "|---|---|---|---|---|---|"]
    for r in sorted(frame, key=lambda r: r["name"]):
        L.append(f"| {r['name']} | {r['footprint_mm'][0]:.0f} x {r['footprint_mm'][1]:.0f} x {r['height_mm']:.0f} | "
                 f"{r['volume_cm3']:.1f} | {r.get('support_cm3', 0):.1f} | {r['g']:.0f} | {r['min']:.0f} |")
    if flags:
        L += ["", "## Worth a look", ""] + [f"- {f}" for f in flags]
    open(DOC, "w").write("\n".join(L) + "\n")
    print(f"{len(frame)} pieces, {len(plates)} plates, {tot_g / 1000:.2f} kg PETG ({sup_g:.0f} g support), "
          f"{tot_min / 60:.0f} h machine, {max(load.values()) / 60:.0f} h on two printers; 3 walls {g3 / 1000:.2f} kg; "
          f"other parts {og / 1000:.2f} kg -> {os.path.relpath(DOC)}")


if __name__ == "__main__":
    main()
