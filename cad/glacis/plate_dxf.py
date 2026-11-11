"""Gun cradle plates -> one flat DXF each (mm), from the exported STEP, so the DXF is exactly what the CAD checked.
Usage (from cad/glacis): ../.venv/Scripts/python plate_dxf.py [step dir] [out dir]"""
import sys, os, json
import cadquery as cq
from cadquery import exporters

step_dir = sys.argv[1] if len(sys.argv) > 1 else "out/step"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "../../docs/glacis/gun_plates"
os.makedirs(out_dir, exist_ok=True)
names = json.load(open(os.path.join(step_dir, "gun_pivots.names.json"), encoding="utf-8"))
shape = cq.importers.importStep(os.path.join(step_dir, "gun_pivots.step"))
solids = shape.solids().vals()
if isinstance(names, dict):
    names = names.get("names") or names.get("parts") or list(names.values())
names = [n if isinstance(n, str) else n.get("name") for n in names]
assert len(names) == len(solids), (len(names), len(solids))
README = []
HEAD = """# Gun cradle plates (waterjet)

Two plates, 1/8 in (3.175 mm) 6061 aluminium sheet, one DXF each, in millimetres, cut from the CAD's own STEP export
by `cad/glacis/plate_dxf.py` (run it again after any change to the plates).

- X runs along the barrels (muzzle end is +X), Y is up, and Y = 0 is the plate's centreline (the pivot axis height).
- The left and right plates share the outline and the pockets. They differ only in the bolt circle round the pivot:
  the left plate has the axle hub's 4 holes, the right plate has the 6 holes for the 112T ring pulley's standoffs.
- Every round hole is 4.5 mm for an M4 and has a part behind it (insert, nyloc, T-nut or standoff). The hexagon is the
  1/2 in hex for the pivot stub: cut it on the line and file to a snug fit.
- The pockets (chevrons and the X round the hub) are lightening cut-outs with 4 mm corner radii.

| File | Outline | Mass | Round holes |
|---|---|---|---|
"""
TAIL = """

Note: both files are drawn in the same X/Y frame (looking at the gun from its left). The plates are flat and
symmetric through their thickness, so no mirroring is needed when cutting.
"""
for n, s in zip(names, solids):
    if not n.startswith("Cradle plate"):
        continue
    bb = s.BoundingBox()
    ymid = (bb.ymin + bb.ymax) / 2
    # plate lies in the x-z plane: turn it flat (y -> z) and cut it at mid thickness
    flat = s.translate(cq.Vector(0, -ymid, -(bb.zmin + bb.zmax) / 2)).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90)   # x along the barrels, y up, 0 at mid height (the pivot axis)
    w = cq.Workplane("XY").add(flat).section(0)
    tag = "left" if "left" in n else "right"
    path = os.path.join(out_dir, f"gun_plate_{tag}.dxf")
    exporters.exportDXF(w, path)
    edges = w.edges().vals()
    kinds = {}
    for e in edges:
        kinds[e.geomType()] = kinds.get(e.geomType(), 0) + 1
    fb = flat.BoundingBox()
    wires = w.wires().vals() if w.wires().size() else []
    print(f"{n}: {bb.xlen:.1f} x {bb.zlen:.1f} x {bb.ylen:.3f} mm -> {path}; {len(edges)} edges {kinds}; "
          f"flat bbox x {fb.xmin:.1f}..{fb.xmax:.1f}, y {fb.ymin:.1f}..{fb.ymax:.1f}")
    holes = {}
    for e in edges:
        if e.geomType() == "CIRCLE" and e.IsClosed():
            d = round(2 * e.radius(), 2)
            holes[d] = holes.get(d, 0) + 1
    README.append(f"| `gun_plate_{tag}.dxf` | {bb.xlen:.1f} x {bb.zlen:.1f} mm | {flat.Volume() * 2.70e-6:.2f} kg | "
                  + ", ".join(f"{c} x dia {d:g}" for d, c in sorted(holes.items())) + " |")
open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8", newline="\n").write(HEAD + "\n".join(README) + TAIL)
print(open(os.path.join(out_dir, "README.md"), encoding="utf-8").read())
