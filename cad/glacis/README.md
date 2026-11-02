# Glacis CAD (CadQuery)

The whole Glacis robot as a parametric CadQuery model. Every shared number is in `params.py`.

```bash
../.venv/bin/python robot.py            # build, checks, STEP export, parts rollup, renders (~8 min)
../.venv/bin/python robot.py --checks   # build + checks only (~2 min)
../.venv/bin/python robot.py --export   # build + STEP export + parts rollup
```

| File | What it builds |
|---|---|
| `params.py` | Layout: frame bands, belts, rollers, body outline, pivot, gun, tanks, pump spot |
| `drive.py` | 1x2/1x1 box-tube frame, gussets, drive plates, Falcons, belts, printed mecanum (hub, aluminum side plates, rollers), hex axles |
| `gun.py` | Two polycarbonate barrels, QE5 valves, 4 in cap chambers, 5-port inlet blocks, cradle, mantlet, trunnions, supply tubes |
| `fittings.py` | NPT fittings placed along a run with real thread make-up |
| `body.py` | Body shell (one front slant, flat deck, leaning sides), panels, printed frame, panel recesses, corner clips, LED slots, sectioning, tapered tenons |
| `misc.py` | Towers, pivot, elevation motor and pot, tanks, rear manifold, fill cross, battery sled, electronics, bumpers, standoffs |
| `robot.py` | Assembly, checks, export |

**Checks** (written to `out/check_log.txt`):
- interference between every pair of parts;
- the gun swept 0-90 deg (every 5 deg) against everything fixed, including the pump spot;
- the door envelope;
- printed parts against a 256 mm bed;
- parts that come out in more than one piece;
- mass and gun balance.

**Outputs** in `out/`:
- renders (`glacis_*.png`);
- `parts_from_cad.csv`, which the parts list in `../../bom/glacis_bom.py` is checked against;
- `step/`: one STEP per Onshape tab, each under 9 MB for the upload limit, plus a `.names.json` for
  each. Not committed; regenerate it.

**Onshape:** document "Brophy Mark 5 - Glacis". Each STEP is uploaded with
`POST /api/v6/blobelements` (translate, flattenAssemblies), which keeps the part names. The
"Glacis rev B (whole robot)" assembly inserts every Part Studio whole, at the origin. When something changes,
replace only the tabs whose STEP changed: delete the Part Studio and its BLOB tab together, then upload
the new file.

Design decisions and their reasons: `../../docs/glacis/JUDGMENTS.md`.
