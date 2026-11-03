# Glacis CAD (CadQuery)

The whole Glacis robot as a parametric CadQuery model. Every shared number is in `params.py`.

```bash
../.venv/bin/python robot.py            # build, checks, STEP export, parts rollup, renders (~8 min)
../.venv/bin/python robot.py --checks   # build + checks only (~2 min)
../.venv/bin/python robot.py --export   # build + STEP export + parts rollup
```

| File | What it builds |
|---|---|
| `params.py` | Layout: frame bands, belts, rollers, body outline, pivot, gun, tanks, smoke machine |
| `drive.py` | 1x2/1x1 box-tube frame, gussets, drive plates, Falcons, belts, printed mecanum (hub, aluminum side plates, rollers), hex axles |
| `gun.py` | Two in-line cannons (1 gal chamber -> Atlantic Valves SZW-25 -> breech adapter -> polycarbonate barrel), balanced on the axle between them; cradle, mantlet with smoke vents, pivot axle, elevation pulley, its sweep envelope |
| `fittings.py` | NPT fittings placed along a run with real thread make-up |
| `body.py` | Body shell (60 deg front, flat deck, leaning sides and back, gun well cut to the sweep envelope), panels, printed frame, panel recesses, corner clips, LED channels, sectioning, tapered tenons |
| `misc.py` | Towers, bearing blocks, elevation motor and pot, side tanks, rear manifold, fill block, smoke machine and ducts, battery sleds, back-bottom electronics, rear-panel controls, bumpers, standoffs |
| `robot.py` | Assembly, checks, export |

**Checks** (written to `out/check_log.txt`):
- interference between every pair of parts;
- the gun swept 0-90 deg (every 5 deg) against everything fixed;
- the door envelope;
- printed parts against a 256 mm bed;
- parts that come out in more than one piece;
- mass and gun balance (the gun solves its own position so its centre of mass sits on the axle).

**Outputs** in `out/`:
- renders (`glacis_*.png`);
- `parts_from_cad.csv`, which the parts list in `../../bom/glacis_bom.py` is checked against;
- `step/`: one STEP per Onshape tab, each under 9 MB for the upload limit, plus a `.names.json` for
  each. Not committed; regenerate it.

**Onshape:** document "Brophy Mark 5 - Glacis". Each STEP is uploaded with
`POST /api/v6/blobelements` (translate, flattenAssemblies), which keeps the part names. The
"Glacis rev C (whole robot)" assembly inserts every Part Studio whole, at the origin. When something changes,
replace only the tabs whose STEP changed: delete the Part Studio and its BLOB tab together, then upload
the new file.

Design decisions and their reasons: `../../docs/glacis/JUDGMENTS.md`.
