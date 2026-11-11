# Gun cradle plates (waterjet)

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
| `gun_plate_left.dxf` | 489.5 x 226.2 mm | 0.70 kg | 21 x dia 4.5 |
| `gun_plate_right.dxf` | 489.5 x 226.2 mm | 0.70 kg | 23 x dia 4.5 |

Note: both files are drawn in the same X/Y frame (looking at the gun from its left). The plates are flat and
symmetric through their thickness, so no mirroring is needed when cutting.
