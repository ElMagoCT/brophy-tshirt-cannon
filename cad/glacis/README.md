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
| `drive.py` | 1x2/1x1 box-tube frame, gussets, drive plates, Falcons, belts, vector-style printed mecanum (two-half hub with the 116T, 3 flat aluminum plates, rollers on 608s and fixed M8 rods), hex axles |
| `gun.py` | Two in-line cannons 8 mm apart (0.53 L 2 in pipe chamber -> Atlantic Valves SZW-25 -> spigot breech adapter -> polycarbonate barrel with smoke holes), balanced on the pivot axis between them; cradle, breech block, mantlet, smoke collar, pivot stubs, elevation pulley, its sweep envelope |
| `shot_model.py` | Lumped shot model (chamber, valve opening time, barrel, shirt) used to size the chambers |
| `fittings.py` | NPT fittings placed along a run with real thread make-up |
| `body.py` | Body shell (60 deg front, flat deck, leaning sides and back, gun well cut to the sweep envelope), panels, printed frame, panel recesses, edge-light grooves, corner clips, frame strip tunnels and feed slots, sectioning, tapered tenons |
| `misc.py` | Towers, bearing blocks, elevation motor and pot, side tanks, rear manifold, main valve and in valves, custom 12 V fogger and smoke ducts, battery sleds, back-bottom electronics, rear-panel controls, bumpers, standoffs |
| `speakers.py` | The two slim siren speakers: where each corner notch goes, its aim, the pocket, cup and grille solids |
| `pneu_parts.py` | Detailed pneumatic parts (NPT fittings, push-to-connects, ball and solenoid valves, reliefs, check valve, M plug, transducer, the rear manifold) and the one-line purpose of each part that goes into its Onshape Description |
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
