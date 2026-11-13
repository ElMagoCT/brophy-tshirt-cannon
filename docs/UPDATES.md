# Design updates (shared log)

Everyone who edits this design, whether a person or any Claude chat, reads this file before starting and writes
here when they finish. Newest entry first. How it works: [COLLABORATING.md](COLLABORATING.md).

## In progress

Claim the files you're about to change, and push the claim before you edit. Remove your line when your entry
below lands. If someone else has claimed a file you need, wait or ask Micah.

| Who (and which chat) | Started | Working on | Files |
|---|---|---|---|
| Micah's Windows computer (Claude Code) | 2026-11-08 | Printable mini kit (gun on a filament pin) + sliced projects for 2 CC2 / 2 CC1 | `cad/glacis/mini.py`, `mini_3mf.py`, `mini_orca/`, `out/mini/`, `docs/glacis/mini_model.md` (all new) |

## Entry template

```
## YYYY-MM-DD - <who> (<which Claude chat or tool>) - <short title>
- Branch / commit: <branch name, PR link or commit>
- Changed: <what's different in the design, in plain words>
- Files: <files touched>
- Checks: <robot.py result: interference, sweep, bed fit, multi-piece; anything not checked>
- Parts list: <rows added/changed and the new total, or "no change">
- Not done: <Onshape import/version, Google Sheet, artifact, anything left for Micah>
- Questions for Micah: <decisions that are his, or "none">
```

## 2026-11-12 - Micah's Windows computer (Claude Code) - Frame in 40x40 T-slot (design branch)
- Branch / commit: micah-windows/extrusion-4040 (design branch, not merged; nothing on borealis or main changed)
- Changed: every 1x2 / 1x1 box tube member is 40x40 20-series T-slot (24 members, 7.47 m), joined by M5 end taps through 10 mm access holes, M5 T-nut plates and 13 cast 40-series corner brackets; no rivets. FW 627.5 mm (gun side fixed at GUN_RAIL_Y 129.35); live hex axles kept, flanged bearings pressed through two 1/8 plates each (side plate + inner bearing plate; two outer bearing plates), no axle hole in any extrusion, wheel drops out of the side plate's slot. Sled rails up 19.6 mm (8.7 mm over the wheel), tank arms kept at 281.8 with the posts at x 0 / 165 and the tanks at x 47.5. Bumpers on 6 printed hanger blocks, underglow and frame mounts on T-nuts. Details: JUDGMENTS B30.
- Files: `cad/glacis/params.py`, `lib.py`, `drive.py`, `misc.py`, `brackets.py`, `robot.py`, `partcodes.py`, `docs/glacis/waterjet/*`, `docs/glacis/cut_list_4040.csv` (new; `tube_drilling.csv` removed on this branch), `docs/glacis/JUDGMENTS.md`
- Checks: full build with the body (629 parts, 1 h 53 min): interference 2 pairs over 30 mm3, both the old gun-internal ones (cradle plate vs gun tubes, 115 / 110, same as before the branch); it also flagged the tank lines against the wider body's rear frame (46-74 mm3), rerouted and rechecked against the exported body STEPs: 0 mm3. Gun sweep 0-90 every 5: 0. check_fasteners: 273 T-nut screws + 56 end taps, 0 off a slot line / core, 0 too close, 0 missed. Every print fits the 250 mm bed; no part in more than one piece. Arms 8.7 mm (sleds) and 6.9 mm (front tank arms) off the wheels' 127 mm swept circle.
- Parts list: no change (Micah: not yet). Hardware delta in B30.
- Not done: Onshape (STEPs for the changed tabs in `cad/glacis/out/step_4040/` with manifest.json, for an Onshape branch); the parts list; the Falcon spline engagement (9.9 mm, was 14.6).
- Questions for Micah: M5 heat-set inserts in the body too (one screw size everywhere)? Brackets under the arms don't fit beside the wheels: OK on end taps alone?
- Onshape: branch (workspace) "40x40 extrusion frame" from version "Rear panel: no E-stop, one tight row": 28 tabs re-imported (chassis 9, wheels 4, body frame 7, lights 3, add-on rails, power, bumpers, panels, pneumatics), 587 parts coded (the 13 cast corner brackets show X: not on the parts list yet), old tabs/STEPs deleted in the branch, rigid groups rebuilt, every assembly feature OK including the main assembly's gun mates; version "40x40 extrusion frame (2026-11-12)". Main workspace untouched.

## 2026-11-12 - Micah's Windows computer (Claude Code) - Rear panel cleanup: no E-stop, one tight row
- Branch / commit: micah-windows/borealis (PR #2), commits 73fc60e, 4df65ac
- Changed (Micah): the rear E-stop is gone; the 120 A breaker's red trip button is the kill switch (it kills everything, logic included). The contactor coil now runs logic tap -> safety node -> controller MOSFET; the valve arm relay is fed from the PDH and armed by the controller. The rear panel is one tight row at z 255: breaker (y -135), SB50 charge port (-75), fill plug (-26.5), USB-C (+10), was spread over -238..+192. The breaker stays outside the tank lines that drop beside the rear cross. Also: the tank transducer moved to the right tank's FRONT bung (the rear bung hit the tank-arm knee plate, found by an independent review).
- Files: `cad/glacis/misc.py`, `electrical/README.md`, `bom/*`, `docs/glacis/air_wiring_artifact.html`
- Checks: robot build without the body, brackets included: the panel row, every pneumatic part and tube against everything, 0 hits over 30 mm3. The body panels were rebuilt alone (body solid + panels + clips, no frame sectioning) for their new holes.
- Parts list: E-stop row 2 -> 1 (the remote's). Total $1,476.84 pre-tax. Sheet synced.
- Onshape: Body panels & clips, Power, electronics & smoke, and Pneumatics re-imported and coded, old tabs/STEPs deleted, rigid groups rebuilt, every feature OK; versions "Before rear panel cleanup" and "Rear panel: no E-stop, one tight row" (2026-11-12). Artifact republished.
- Not done: the new tabs sit at the root of the tab bar (drag them into their folders).
- Questions for Micah: none

## 2026-11-12 - Micah's Windows computer (Claude Code) - No QDs but the fill, 10 straight push-to-connects, flat rear cross, CheeMuii tube; concept branch
- Branch / commit: micah-windows/borealis (PR #2), commits a89ba23, 0fd9680
- Changed (Micah): every quick disconnect removed except the fill plug (the push-to-connects come off if the gun or a tank must); push-to-connects are 10, all straight (tank outlets straight down, chamber inlets straight into their bungs); the F x F elbow and the 2-1/2 in nipple are gone: the rear cross lies flat with the fill check valve straight out its back face through the rear panel (fill plug on its end) and the main ball valve straight off its front face inside the robot (no stem through the panel); tanks into its sides. The cross sits 120 mm to the right of the old manifold spot, clear of in valve A. Tube is now CheeMuii 30 ft (B0DBSNY5X2, DOT SAE J844, 500 psi, $9.99).
- Fixed: the LED groove helper picked a random face when a part's section was in pieces; on the smoke collar that cut it into 3 bodies (seen in the Onshape import). It now uses the largest face; the collar is one solid again.
- Files: `cad/glacis/misc.py`, `gun.py`, `robot.py`, `pneu_parts.py`, `partcodes.py`, `bom/*`, `docs/glacis/air_wiring_artifact.html`
- Checks (no full rebuild, Micah: "just build the new stuff"): robot build without body/brackets, the new pneumatic parts, tubes, chamber inlets and service loops against every part: 0 hits over 30 mm3; chamber inlet push-to-connects swung 0-90 deg every 5 against everything fixed: 0 hits; gun-only build: every gun part one solid.
- Parts list: P04 QD couplers, P12 F x F elbow, P18 swivel elbows and P22 nipple removed; P17 straight push-to-connects 2 packs -> 1; P16 tube -> CheeMuii. Total $1,546.94 -> $1,482.09 pre-tax. Sheet synced (rows deleted, notes updated).
- Onshape: Pneumatics (46 parts) and Gun (pivots) 1-3 of 3 (42 parts) re-imported and coded, old tabs and STEPs deleted, rigid groups rebuilt, every assembly feature OK; versions "Before straight connectors + flat rear cross" and "Straight connectors, flat rear cross, no QDs" (2026-11-12). New branch "Concept: in valves + sensors on the chambers": each chamber's in valve, cross, transducer, relief and outlet push-to-connect moved onto its back end (service loops removed there), concept only, clashes allowed; version saved in the branch.
- Not done: the new Pneumatics and Gun tabs are at the root of the tab bar (automation can't drag tabs into an existing folder); drag them into "System part studios" / "Gun part studios".
- Questions for Micah: none

## 2026-11-12 - Micah's Windows computer (Claude Code) - Rear manifold is one real cross; tank relief and main-line QD removed
- Branch / commit: micah-windows/borealis (PR #2)
- Changed: the rear manifold (P10-1) was a drawn block, not real parts; it is now one ChillWaves cross: right tank up, left tank in from below (swivel push-to-connect), main ball valve straight off one end, fill check valve straight into the other (fill nipple now 2-1/2 in). Tank transducer moved to the right tank's front bung (the rear one hit the tank-arm knee; caught by the review). Removed (Micah): the QD on the main valve line (P04-1 / P05-2) and the rear manifold's tank relief (P02-1); the valve cross relief now covers the tanks only while the main valve is open (JUDGMENTS B27 has the warning). Rear panel: relief hole gone, fill hole moved.
- Files: `cad/glacis/misc.py`, `pneu_parts.py`, `robot.py`, `partcodes.py`, `bom/glacis_bom.py`, `glacis_bom_codes.json`, `glacis_bom_sheet.json`, `glacis_bom.csv`, `docs/glacis/JUDGMENTS.md`
- Checks: robot build without the body/brackets (the full build with body panels ran past 25 min): the manifold, main valve, fill line, tank transducer, tank tubes, QDs, valve cross and line relief against every part, 0 hits over 30 mm3 (the two-cross version first hit the left sled post, so it went to one upright cross). Rear panel holes recomputed from the same numbers (fill at manifold y + 10, main valve stem), not rebuilt here. Independent two-agent review of the plumbing and parts-list counts.
- Parts list: crosses one 6-pack $16.99 (was two 3-packs $25.98); fill nipple Legines 2-1/2 in $8.49 (was 1-1/2 in $7.49); street elbow row removed (-$7.49); notes on P02, P04, P05, P06, P10, P11, P14, P17, P18. Total $1,562.42 -> $1,546.94 pre-tax (Order 1 $1,072.80, $1,170.42 with tax). Sheet synced.
- Onshape: Pneumatics re-imported (60 parts, all coded and named; codes renumber, e.g. the line relief is now P02-1), old studio + STEP deleted, the sub-assembly's rigid group rebuilt, every assembly feature OK; versions "Before single-cross rear manifold" and "Single-cross rear manifold, no tank relief" (2026-11-12).
- Not done: the new Pneumatics part studio sits at the root of the tab bar; it needs dragging into "System part studios" (automation can't move tabs into an existing folder).
- Questions for Micah: none

## 2026-11-12 - Micah's Windows computer (Claude Code) - Smooth smoke channels (baffles scrapped), 5.5 mm LED bands all round
- Branch / commit: micah-windows/borealis (PR #2)
- Changed: smoke collar 60 mm long with six swept 3/8 in channels curving smoothly into holes that now lean 45 deg (baffles removed); LED groove 5.5 x 2.5 mm (his COB strips) cut from each part's real section so it is open all round, on the mantlet (fixes the partial slot), the smoke collar (new) and the muzzle ring. JUDGMENTS B26.
- Files: cad/glacis/gun.py, bom/glacis_bom.py (barrel note), docs
- Checks: gun rebuild: 0 clashes, 0 sweep, no multi-piece parts; no channel breaks out of the collar; gun 18.7 kg balanced. Full robot.py not re-run.
- Parts list: no change ($1,562.42); Sheet barrel note updated
- Onshape: re-imported (Gun (pivots) 1-3 of 3 in "Gun part studios", 42 parts coded, old tabs + STEPs deleted, all assembly features OK), version "Smooth smoke channels + 5.5 mm LED bands (2026-11-12)"
- Questions for Micah: none

## 2026-11-12 - Micah's Windows computer (Claude Code) - Bigger angled smoke holes, baffles in the smoke collar
- Branch / commit: micah-windows/borealis (PR #2)
- Changed: barrel smoke holes are 3/8 in (were 5 mm), still 3 per barrel facing the other barrel, now leaning 40 deg toward the muzzle so the shot's air streams past them; the smoke collar is 42 mm long with the line's socket, then a chamber with two cone baffles (forward-pointing lips: smoke passes, blast air coming back is caught in the pockets), then one 7 mm channel per hole.
- Files: cad/glacis/gun.py
- Checks: gun-only rebuild (smoke_test): 0 clashes over 30 mm3, 0 sweep clashes 0-90, no multi-piece parts, collar 42 x 94 x 196 mm; gun 18.9 kg, balanced. Full robot.py not re-run.
- Parts list: no change
- Not done: (Onshape re-import done later the same day: Gun (pivots) 1-3 of 3 in folder "Gun part studios", 42 parts coded, version "Breech pucks + angled smoke holes + collar baffles")
- Then (same day): breech puck replaces the turned adapter (JUDGMENTS B25): 2.5D from 1 in 6061 bar, JB Welded in the barrel; barrel + puck slide into the core and screw onto the valve nipple. Files also bom/glacis_bom.py, glacis_bom_codes.json, partcodes.py, pneu_parts.py. Gun rebuild clean (0 clashes, 0 sweep, 18.7 kg). Parts list $1,562.42 pre-tax (Order 1 $1,187.31 with tax); Sheet row P32 added, P29/P31 notes updated. Puck bar price [UNVERIFIED].
- Questions for Micah: none

## 2026-11-12 - Micah's Windows computer (Claude Code) - CAD matches the list, Sheet notes, LED wiring, centred 3/4 in smoke line, visuals
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B23, B24):
  - Every list module is in the CAD (relay driver, fog relays, MOSFET modules, MAX6675, fuse holder, DS18B20s), five quick disconnects in the air lines, real HTD 5M teeth on the 112T ring and 16T pinion, the rear fog tube up at z 235, the drive belts (D06) on the list.
  - Micah's Sheet notes, all answered and cleared: level shifter, level switch, KSD301 cutout, M4 x 6s, rivnuts, coupling nuts and pin headers gone; underglow brackets taped on; ring standoffs printed on the ring; cheaper USB-C, remote charger, canvas, PETG, rivets; nylocs, 1x6s and 3 mm tube owned.
  - LED wiring: 22 AWG 3-pin wire + servo-lead pigtails, five data lines (left panels, right panels, left frame, right frame, underglow), nothing in parallel.
  - Gun smoke line 3/4 x 1 in, dead centre between the barrels, oblong holes; new smoke collar with one channel per barrel hole (3 per barrel, now actually through the wall); solid mantlet loft; core clamp screws above and below the barrels.
  - New "Visuals" STEP (floor, smoke, t-shirts, window glow, headlight beam), never in the checks or the list.
- Files: `cad/glacis/gun.py`, `misc.py`, `lib.py`, `params.py`, `robot.py`, `partcodes.py`, `visuals.py` (new), `out/`, `docs/glacis/waterjet/`, `docs/glacis/tube_drilling.csv`, `bom/glacis_bom.py` (+ csv/json/codes), `electrical/README.md`, `docs/glacis/JUDGMENTS.md`
- Checks: full robot.py: interference only the old 64 mm3 fill elbow sliver; sweep 0-90 deg 0 clashes; every print on the bed; 0 multi-piece; gun 18.8 kg, balanced.
- Parts list: $1,566.22 -> $1,532.42 pre-tax (Order 1 $1,058.28 / $1,154.58 with tax, Order 2 $474.14 / $517.29). Sheet rewritten to match.
- McMaster: nothing needs to be McMaster; switching away saved about $235 overall (the one dearer swap, rated Sch 80 nipples, is about +$7 net, under the $20 line), so it stays switched.
- Onshape: backup version "Before modules, QDs, centred smoke line, visuals (2026-11-12)"; gun (now 2 studios), chassis (6), power, pneumatics and bumpers re-imported and swapped (old tabs and their STEPs deleted, new ones in "System part studios"); 343 parts given their Part number and "<code> <name>". New "Visuals" part studio and a "Visuals" sub-assembly (in "Sub-assemblies", grouped to the chassis in the main assembly), each with five configuration checkboxes: Hide floor / smoke / t-shirts / window glow / headlight beam (all off = everything shown). Version "Modules, QDs, pulley teeth, centred 3/4 in smoke line, visuals with hide switches (2026-11-12)".
- Questions for Micah: none.

## 2026-11-11 - Micah's Windows computer (Claude Code) - Onshape part names carry their parts-list code
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (Micah: "every part should be named, i want to see what aligns with what on the order list"): every one of the 599 Onshape parts is renamed "<code> <name>" (e.g. "B15-1 Bumper backing rear", "P05-1 Fill plug"), so the assembly tree reads against column A of the order tabs. The 9 sub-assemblies have Part numbers too (ASM-P1 Pneumatics, ASM-P2 Gun, ASM-D, ASM-C, ASM-L, ASM-B1/B2/B3, ASM-R; the main assembly ASM-TC5), so the structured BOM has no blank rows.
- Rule for every future re-import: after the swap, set Part numbers from `cad/glacis/out/part_codes.json` (matched on the STEP's plain names), then rename each part to "<Part number> <name>". The STEPs keep the plain names, so `partcodes.py` matching is unchanged.
- CAD vs parts list check (out/part_codes.json against bom/glacis_bom.csv): every coded CAD part is on the list. List rows not modelled in the CAD are fasteners, consumables, chips and kits, plus these small modules: fog relays (C06 x2, Order 2), MOSFET modules (F11), MAX6675 (F03), level switch (F04), DS18B20s (F05), thermal cutouts (F06), QD couplers (P04), fuse holder (C17), and the handheld safety remote (C13, C19, second E-stop). The CAD's printed 10 in wheels (code W: 4 x 140T belts, 40 roller rods) are deferred; the list uses the old 9 in wheels (D03).
- Onshape: version "Part names start with their parts-list code (2026-11-11)".

## 2026-11-11 - Micah's Windows computer (Claude Code) - Tube holes for the CNC, lower underglow on tape, axles inside the rail, 3/16 in bumper gap
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B22):
  - Every hole in the box tubes is cut in the CAD and listed in `docs/glacis/tube_drilling.csv` for the CNC program: 303 holes in 24 tubes (138 dome rivets, 100 countersunk, bearings, axle access, bumper screws, underglow rivnuts, frame mounts).
  - The underglow bracket is new and lower: the strip's centre is just under the bumper's bottom edge. The strip is held on with 3M tape, and the brackets screw into M4 rivnuts in the rails. The corner gussets have the matching holes.
  - Axles end in the outer rail's bearing (the bearing sits in the rail's inner wall), so the bumper has no axle holes.
  - The bumper ring sits 3/16 in off the chassis on printed spacers; the foam is cut 1-13/16 in deep so the robot stays 27.75 in wide.
- Files: `cad/glacis/lib.py`, `drive.py`, `misc.py`, `brackets.py`, `params.py`, `robot.py`, `out/` (check log, renders, parts csv, part codes), `docs/glacis/tube_drilling.csv` (new), `docs/glacis/waterjet/`, `bom/glacis_bom.py` (+ csv/json/codes), `docs/glacis/JUDGMENTS.md`
- Checks: full robot.py: interference only the old 64 mm3 fill elbow sliver; sweep 0-90 deg 0 clashes; every print on the bed; 37 waterjet parts, 238 rivets.
- Parts list: $1,538.00 -> $1,566.22 pre-tax (+ L05 3M tape $15.99, + B20 M4 rivnuts $5.49, M4 x 8s 1 -> 2 packs). Sheet: both rows added, text updated; Order 2 $656.65 with tax. `_sheet()` now starts items at row 5 (the Mac chat's per-seller row 3).
- Onshape: backup version "Before tube holes, lower underglow, bumper gap (2026-11-11)"; chassis (6), bumpers and lights (3) re-imported and swapped (old tabs and STEPs deleted, new ones filed in their folders); every part's Part number re-set (599); version saved.
- Questions for Micah: the rivnut listing doesn't give a grip range; check it covers a 1/16 in wall (plus the 1/8 in gusset at the corners).

## 2026-11-11 - Micah's Windows computer (Claude Code) - Electronics on the bellypan, breaker at the rear, part numbers
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B21): every board and module on a one-piece CNC'd bellypan (footprints engraved, boards on printed trays), the shelf gone; the main breaker (the on / off switch) on the rear panel beside the E-stop; a code for every list row and a Part number on every Onshape part; the main valve and 1-1/2 in nipple are buys; audio is in Order 2; M5 fog-heater standoffs listed.
- Files: `cad/glacis/misc.py`, `brackets.py`, `partcodes.py` (new), `out/` (check log, renders, parts csv, part_codes.json/.csv, STEPs), `docs/glacis/waterjet/` (bellypan now CNC, not nested), `docs/glacis/acrylic_cuts/` (rear panel's breaker hole), `bom/glacis_bom.py` (+ csv/json, `glacis_bom_codes.json` new), `docs/glacis/JUDGMENTS.md`
- Checks: full robot.py (only the old 64 mm3 sliver; sweep 0 clashes; prints fit; 0 multi-piece), then the board trays: 0 hits against everything and the swing.
- Parts list: $1,514.52 -> $1,538.00 pre-tax (+$15.99 main valve, +$7.49 nipple). Sheet: rows moved, column A codes, audio moved, tabs renamed "Borealis Order 1 - pneumatics, electronics" ($1,052.09 with tax) and "Borealis Order 2 - materials, LEDs, smoke, audio" ($625.86).
- Onshape: backup version "Before electronics on the bellypan + part numbers (2026-11-11)"; chassis (6), power and body panels re-imported and swapped, old tabs deleted, new ones filed; every part's Part number set; version saved.
- Sidenote: Cannon home (total $1,538.00, Pneumatic $844.20, latest paragraph), Pneumatic (main valve and nipple are buys), Lights/Wiring (breaker / E-stop sticky, PDH box).
- Questions for Micah: none.

## 2026-11-11 - Micah's Windows computer (Claude Code) - Acrylic and aluminium in hand; CNC only for the cannon
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (Micah: "only cnc for the cannon, everything else waterjet. i have aluminum for this so no need to add it. also remove acrylic from the total, i found enough"): the Lesnlok acrylic 2-pack ($86.98) and the aluminium stock row are off the parts list; the owned-acrylic, breech adapter, waterjet bracket and gun plate rows say the material is his. The gun's two side plates are the only CNC router parts; every other plate is waterjet.
- Files: `bom/glacis_bom.py` (+ csv/json), `docs/glacis/air_wiring_artifact.html` (parts data; the "aluminium is unpriced" open item gone)
- Parts list: $1,601.50 -> $1,514.52 pre-tax. Sheet synced (Order 2 $518.48 with tax). Sidenote: Body (Shell) board (rivets, riveter, waterjet bracket row; acrylic and stock boxes removed; design notes), the gun plate box on Pneumatic, the Cannon home page (total, Body subtotal, latest paragraph). "Glacis air & wiring" artifact republished.
- Questions for Micah: none.

## 2026-11-11 - Micah's Windows computer (Claude Code) - Flat waterjet brackets, riveted and tied together
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B20): new `cad/glacis/brackets.py`: side plates (the Falcon plates grown into every post), inboard plates, arm knees, drilled corner gussets, flat tower plates + spacer strips, a 3-piece bellypan with seam straps; every rivet hole drilled through the tube under it in the CAD. Bent parts and the old drive plates / top arm gussets gone; tank saddles step down onto the arms.
- Files: `cad/glacis/brackets.py` (new), `drive.py`, `misc.py`, `robot.py`, `out/` (check log, renders, parts csv, STEPs: the chassis tab is now 6 files), `docs/glacis/waterjet/` (new: one DXF per part, the 12 x 12 nest, README), `bom/glacis_bom.py` (+ csv/json), `docs/glacis/JUDGMENTS.md`
- Checks: full robot.py (sweep 0-90 deg 0 clashes; interference: the old 64 mm3 sliver, and the tank line through the lowered saddle, fixed and re-checked: 0; prints fit; 0 multi-piece). `out/check_log.txt` predates the saddle fix.
- Parts list: $1,525.57 -> $1,601.50 pre-tax (+$75.93: 2 packs of dome rivets, 3 of countersunk; brackets are stash sheet). Sheet synced (Order 2 $613.37 with tax).
- Onshape: backup version "Before waterjet brackets (2026-11-11)"; the chassis part studio replaced by 6 (110 parts) and pneumatics re-imported, swapped into their sub-assemblies, rigid groups rebuilt, all assemblies OK; old studios and STEPs deleted, new ones filed in System part studios; version "Waterjet brackets: flat, riveted, interconnected (2026-11-11)".
- Questions for Micah: the gun cradle plates (490 x 226 mm) don't fit the 12 x 12 waterjet. Answered: "ill use a cnc" (the router); the parts list, the plates' README and the CAD label say so.

## 2026-11-11 - Micah's Windows computer (Claude Code) - Review pass: holes, one gun core, electronics shelf, parts list
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B19): every plate hole has something behind it (tie holes gone, saddles / caps / core screwed from the sides); valve blocks + breech block + mantlet are one printed gun core in left and right halves; hub flange 3 mm, ring standoff screws counterbored, stubs tapped both ends; the electronics shelf matches rev D.2.1 (Waveshare board, PCA9685, two ADS1115s, two battery relays, 1200 W boost); robot.py measures gun prints level.
- Files: `cad/glacis/gun.py`, `plates.py`, `misc.py`, `robot.py`, `plate_dxf.py` (new), `out/` (check log, renders, parts csv, STEPs), `docs/glacis/gun_plates/` (new: one DXF per plate, mm), `bom/glacis_bom.py` (+ csv/json), `docs/glacis/air_wiring_artifact.html` + `parts_section.py`, `docs/glacis/JUDGMENTS.md`, `CLAUDE.md` (status lines)
- Checks: full robot.py (interference 1 pair, the old 64 mm3 sliver; sweep 0-90 deg 0 clashes; 0 multi-piece; 50 frame pieces), the shelf rebuilt alone against everything and the gun swing: 0 hits. `out/check_log.txt` predates the shelf fix and the level bed check.
- Parts list: $1,489.58 -> $1,525.57 pre-tax (+$35.99, the second PETG spool; +$3.56 inserts, -$0.17 logic supply, plus earlier same-day swaps). Sheet synced (Order 1 $1,133.87, Order 2 $530.53 with tax). Sidenote Cannon boards and home page updated. "Glacis air & wiring" artifact republished.
- Onshape: backup version "Before review pass (2026-11-11)"; new STEPs for the gun, add-on rails, body frame 1 and 2, lights 1 and power imported and swapped by name into their sub-assemblies (Gun, Add-on rails, Body frame, Lights & speakers, Power & smoke; the power tab drops the old controller, music board, single ADC and 1500 W boost and gains the Waveshare board, PCA9685, two ADS1115s, two battery relays and the 1200 W boost), rigid groups rebuilt, every assembly's features OK. The six replaced part studios and their STEPs are deleted, the new tabs renamed and filed (System part studios, Body frame parts, Lights & speakers parts, CAD Imports): only the main assembly is outside a folder. Version "Review pass: one gun core, backed holes, electronics shelf (2026-11-11)".
- Questions for Micah: none (the core is split left / right, not top / bottom: see B19).

## 2026-11-10 - Micah's Windows computer (Claude Code) - Gun restyle: chevron/turret-wheel plates, cannons closer, V rear holder
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B18): new side plates (swallowtail back, turret boss round the pivot, 3 + 3 side chevrons and an X of 4 round the hub, 717 g each, was 846); cannons 30% closer (gap 25.1 mm, axes 101 mm); V-shaped rear chamber holder lined up with the plates' back; chamber caps that fill out to the plates (no open corners) and saddles screwed to the plates; printed end covers on the chambers' back ends; a slim left hub; gun rails 276 mm.
- Files: `cad/glacis/plates.py` (new), `gun.py`, `params.py`, `out/` (check log, renders, parts csv), `bom/glacis_bom.py` (+ csv/json), `docs/glacis/JUDGMENTS.md`
- Checks: full robot.py on the first plate version (interference 1 pair, the old 64 mm3 sliver; sweep 0-90 deg 0 clashes; prints fit; 0 multi-piece; well floor re-cut; 50 frame pieces, 58 tenons), then the final gun swapped into those STEPs and checked against everything over the swing: 0 hits; no clashes inside the gun; gun 18.5 kg, balanced. `out/check_log.txt` and the renders are from the full run, so they show the first plate version.
- Parts list: no price change ($1,485.85 pre-tax): M4 x 8 +12 (saddles), M4 x 12 +4 (hub), M4 inserts +12 (86 of 100), M4 x 30 back to 10. Sheet matches.
- Onshape: backup version "Before chevron plates (2026-11-10)"; 12 part studios replaced (gun, add-on rails, chassis, pneumatics, power, body panels, body frame 1-6), parts swapped by name into their sub-assemblies, rigid groups rebuilt; version "Chevron gun plates (2026-11-10)". Then (Micah: "always delete the old stuff. make sure everything but the main assembly is in folders") the 12 replaced part studios and their 12 old STEPs were deleted (the backup version keeps them), and every tab but the main assembly is in a folder: Body frame parts, Lights & speakers parts, System part studios, Wheels, CAD Imports, Sub-assemblies, and a new "Micah's studios" for Part Studio 1 and Variable Studio 1.
- Questions for Micah: none.

## 2026-11-10 - Micah's Windows computer (Claude Code) - Elevation ring pulley on standoffs, belt centred
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B17): the 112T gun pulley is a ring on 6 standoffs (M4 x 10 stainless coupling nuts) 10 mm off the right cradle plate; the belt runs centred between the plate and the bearing block; the 16T pinion moved 8 mm out on the motor's 8 mm REX shaft (printed from Micah's pulley design); a printed sleeve on the right stub locates the gun. Ratio and belt unchanged.
- Files: `cad/glacis/gun.py`, `params.py`, `misc.py`, `bom/glacis_bom.py` (+ csv/json), `docs/glacis/JUDGMENTS.md`
- Checks: partial rebuild only (gun + tower/pivot/elevation parts, swapped into the last full build's STEPs): rebuilt chassis parts vs everything and the gun's 0-90 deg swing vs everything fixed, 0 hits over 30 mm3; prints fit the bed; belt 750 mm (150T). robot.py not re-run in full, so `out/check_log.txt` and the renders are from the previous full build.
- Parts list: + M4 x 10 coupling nuts 10-pack $4.99 (Amazon); M4 x 30 now 14 used, nylocs 4, M4 x 8 and M4 x 12 +6 each. Pre-tax $1,485.85. Sheet matches.
- Onshape: new Gun and Chassis part studios swapped into their sub-assemblies (53/53 and 229/229 rigid), all 10 top-level features OK, version "Elevation ring pulley on standoffs (2026-11-10)". The replaced ones are kept as "Gun (pivots) (old)" and "Chassis, pivot & drive (old)".
- Questions for Micah: delete the two "(old)" part studios and their STEPs?

## 2026-11-10 - Micah's Windows computer (Claude Code) - Pivot hubs, origin fastens, Kenzo's parts list
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B14 amended, B15, B16):
  - **Pivot hubs:** a 72 mm printed boss on each cradle plate out to the inner pivot bearing, with a lip on its inner race (locates the gun sideways). The right one is the 112T pulley, bolted to the plate (4 x M4 x 30 + nylocs) with a round bore, so the pulley no longer drives through the axle. The plates' M3 hub holes became the 4 M4 holes.
  - **Onshape:** the 8 static sub-assemblies are fastened to the origin again (a lock alone let the chassis rotate when the pivot solved); the gun stays on its one revolute with the Gun min / max angle limits. Gun part studio replaced from the new STEP (old one kept as "Gun (pivots) (old)"), Gun sub-assembly 44 parts + its 2 rails, rigid group 46/46, all 10 top-level features OK. Version "Pivot hubs: pulley bolted to the plate (2026-11-10)".
  - **Parts list:** Kenzo's "Cheaper Parts" tab reviewed (notes on each row of his tab); the good swaps applied, everything on Amazon or AliExpress except the Home Depot 1x6s; M4 nylocs added for the hubs.
- Files: `cad/glacis/gun.py`, `cad/glacis/out/` (checks, renders, parts csv), `bom/glacis_bom.py` (+ csv/json), `docs/glacis/JUDGMENTS.md`
- Checks: robot.py (47 min): interference 1 pair over 30 mm3 (the 64 mm3 fill elbow sliver from rev D.2), elevation sweep 0-90 deg 0 clashes, every print fits the bed, 0 multi-piece parts, 49 frame pieces, 57 tenons, speaker cups 8/8, front rail screws 4/4, in-well rail screws 10/10; gun 19.0 kg, CG on the axle.
- Parts list: pre-tax $1,480.86 (Order 1 $1,039.12, Order 2 $441.74), was $1,505.06 before today's hub nylocs and swaps. Sheet Order tabs match.
- Cleanup (Micah's OK): "Gun (pivots) (old)" and its STEP deleted (no assembly used them; the earlier versions keep them); the new Gun part studio is in "System part studios".
- Questions for Micah: none.

## 2026-11-10 - Micah's Windows computer (Claude Code) - Onshape gun mate: variable limits, 0-90 deg
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS B14): elevation range 0-90 deg (was 0-85; the pass-2 build clears to 95). Onshape top assembly: one "Gun pivot" revolute whose limits are the configuration variables "Gun min angle" / "Gun max angle" (0-90, + = barrels up); the 8 fastens and the angle-lock mate are deleted and the 8 non-gun sub-assemblies are locked; the gun's 20x20 rails now live in the Gun sub-assembly; the Gun instance was replaced (the old one was stuck off its pivot).
- Files: `cad/glacis/params.py` (ELEV_RANGE), `cad/glacis/robot.py` (comment), `docs/glacis/JUDGMENTS.md`
- Checks: swing check of the pass-2 STEP export, gun parts vs everything else at 80-95 deg: no clash with anything fixed (only the gun's own rails and the flexible loops, which move with it). No robot.py rebuild: the next one re-cuts the well floor for 90 and sweeps 0-90.
- Parts list: no change.
- Onshape: version "Gun pivot limits as config variables (2026-11-10)". Both mates OK; solved poses checked at 0 / 45 / 90 deg (muzzle level, up 45, straight up over the pivot). Changing the variables doesn't re-pose the gun in the viewport; drag it, or use the mate's "Apply limit position". Refresh any open Onshape tab.
- Questions for Micah: none.

## 2026-11-10 - Micah's Windows computer (Claude Code) - Borealis pass 2: front hole, in-well rails, welded chambers, 85 deg, GOGO valves
- Branch / commit: `micah-windows/borealis` (PR #2, not merged)
- Changed (JUDGMENTS "Brophy Borealis" B9-B13):
  - **Front light bar hole:** a plain hole from the bumper to 4.5 in above it, open at the bottom, no liner (the front acrylic is one U-shaped sheet; 8 panels). Two 372 mm 20x20 rails cross it behind the shell, screwed from inside (M4 x 8 into inserts); the bar stands on the lower one on its own brackets. Front frame mounts: 2 posts at y +-205 (was 3).
  - **In-well rails:** one 470 mm rail each side inside the gun well over the cut-down towers. The bearing blocks sit on them (pivot z 645 -> 656), and a 1/8 in tower plate wraps each tower, runs the rail's length and climbs the block. M4 x 30s across the rail into the well-edge member. Tower brackets, rivnuts and the deck acrylic's U-slots are gone.
  - **Welded chambers** (3 in Sch 40 + 3/8 in discs, 1.56 / 1.32 L, the valve on a 1 in nipple welded through the front disc, a 1/4 NPT bung near the front). Each chamber's transducer and relief moved to a cross after its in valve on the chassis. The gun is 18.9 kg (was 21.4).
  - **Elevation 0-85 deg** (was 45). The well floor reaches z 281 under the axle.
  - **GOGO GPG-M03 in valves** with G1/4 x 1/4 NPT hex nipples. The valve cross moved 51 mm back to clear the rear Falcon.
  - **Smaller items:** 1/2 in smoke line and passages; M4 hardware throughout; joints whose tenon only shed a crumb aren't reported as loose any more; the print-bed check accepts near-square parts that fit square.
  - **Acrylic:** cut plan for two 24 x 48 sheets on the 18 x 36 laser (`docs/glacis/acrylic_cuts/`: saw lines + one DXF per strip, mm).
- Files: `cad/glacis/` (gun, misc, lightbar, params, pneu_parts, body, robot), `bom/glacis_bom.py` (+ csv/json), `docs/glacis/JUDGMENTS.md`, `docs/glacis/acrylic_cuts/`
- Checks: robot.py (55 min on 14 cores): interference 1 pair over 30 mm3 (the 64 mm3 fill elbow / rear manifold sliver from rev D.2; the 146 mm3 valve cross one is gone), elevation sweep 0-85 deg 0 clashes, every print fits the bed (the electronics shelf is 200 x 200 mm; it was flagged only because the oriented-box check turned it 45 deg, and the check is fixed), 0 multi-piece parts, 49 frame pieces, 57 tenons, speaker cups 8/8, front rail screws 4/4, in-well rail screws 10/10, LEDs 0 overlaps.
- Parts list: `bom/glacis_bom.py` now mirrors the Sheet (both order tabs folded in, Micah's column J notes and the answers in COMMENTS). Then: acrylic $150 -> $86.98 (Lesnlok 24 x 48 2-pack), close nipples 2 packs -> 1, rivnuts 0, counts for this pass, tower plates (stash). Pre-tax $1,505.06 (Order 1 $1,057.97 + $10 shipping, Order 2 $437.09). Sheet cells updated to match.
- Onshape: backup version "Before Borealis pass 2 (2026-11-10)", then 16 new part studios (part counts match the export) swapped into the 9 sub-assemblies with their rigid groups rebuilt (Body frame is 6 tabs now). Both Pivot connectors moved to z 656, all 11 top-level features OK, version "Brophy Borealis pass 2 (2026-11-10)". Then (Micah's OK) the 19 replaced part studios and their 19 old STEP blobs were deleted (the backup version keeps them), and the part studios went into tab folders: "Body frame parts" (6), "Lights & speakers parts" (3), "Wheels" (4), "System part studios" (chassis, gun, add-on rails, bumpers, panels, power & smoke, pneumatics); Onshape's own "CAD Imports" folder holds the STEP files. Micah's Part Studio 1 and Variable Studio 1 were left where they were.
- Questions for Micah: none.

## 2026-11-10 - Micah's Windows computer (Claude Code) - Brophy Borealis
- Branch / commit: `micah-windows/borealis` (PR, not merged)
- Changed (Micah's asks, JUDGMENTS "Brophy Borealis" B1-B8):
  - name Brophy Borealis (Onshape, CLAUDE.md, Sheet); the BOM split into two orders with owned/stash under each;
  - Milton M-style interior quick disconnects (5 joints) and an M-style stainless fill plug;
  - the light bar recessed 20 mm in a lined pocket in the front slant, with a 3 in blank sensor band above it;
  - 20x20 rails: one inside each gun cradle plate, two pieces each side of the deck (split round the pivot); the deck
    screws go outboard of the member's light tunnel through U-slots in the deck acrylic's edge;
  - LED lean 22.5 deg, reached 15 mm after each corner arc (no flat stretch), 2 mm square lead-in;
  - `par.py`: the slow OCC steps run on 90% of the cores; robot.py ~2 h 40 min -> 55 min, same results;
  - BOM review: unused rows gone, cheaper transducers and QDs.
- Files: `cad/glacis/params.py`, `body.py`, `misc.py`, `gun.py`, `robot.py`, `lightbar.py`, `par.py` (new), `lib.py`;
  `bom/glacis_bom.py` (+ csv/json); `CLAUDE.md`; `docs/glacis/JUDGMENTS.md`.
- Checks (robot.py, 55 min, 14 workers): interference only the two known fitting slivers from rev D.2 (146, 64 mm3);
  elevation sweep 0-45 deg clean; every print fits the 250 mm bed; no multi-piece parts; LED strips 0 overlaps, loops
  100%, 0 jumpers; 52 frame pieces, 54 tenons (38 screwed, 16 glued), 46 clips; deck rail screws 8 of 8, light bar
  liner 6, speaker cups 8 of 8. body.build now stops on an invalid window cut (a 0 mm square lead-in deleted the frame).
- Parts list: $2,002.43 -> **$1,777.71** (Order 1 $1,259.68 + $10 shipping, Order 2 $508.03). Sheet tabs synced.
- Onshape ("TC5 - Brophy Borealis"): version "Before Borealis rebuild swap (2026-11-10)", then body frame (9 tabs),
  lights (3), panels, add-on rails and power & smoke swapped into their sub-assemblies (part counts match the export);
  each sub-assembly has an "All parts (rigid)" group and an "Origin" connector, Chassis and Gun a "Pivot" connector;
  every sub-assembly but the gun fastened to the origin; gun revolute + "Gun angle" configuration (Range / Free /
  Upmost / Downmost). Version "Brophy Borealis (2026-11-10)". His custom tank instances, Part Studio 1 and Variable
  Studio 1 untouched.
- Not done: the Upmost / Downmost settings don't re-pose the gun. Onshape keeps one stored position for every
  configuration and doesn't re-solve on a switch (server renders of all four settings are identical, 45 deg up).
  Range / Free drag works.
- Questions for Micah: MSI chamber couplings or the Supply Giant B016F1LPTW ($23.99)? Is a drag-to-angle Range good
  enough, or should Upmost / Downmost become separate gun instances shown per setting?

## 2026-11-09 - Micah's Mac Claude Code chat ("Product photos for Cannon component boxes") - Glacis rev D.2.1: Waveshare controller, speaker tap, battery relays
- Branch / commit: main, eeb953a. **Overlap:** the Windows "Brophy Borealis" claim (c0acf20) landed while this was being
  edited, and both touch `bom/glacis_bom.py` (+ csv/json) and `docs/glacis/JUDGMENTS.md`. Windows chat: `git pull`
  before your BOM edits and keep these rows; this chat won't touch those files or the Sheet tab until your entry lands.
- Changed (Micah's asks, JUDGMENTS "Rev D.2.1" W1-W5):
  - controller: Waveshare ESP32-P4-Module-DEV-KIT (P4 + C6, 2.4 GHz only, USB-A + 2 USB-C, 40-pin header), $28.79 Amazon;
  - a PCA9685 for 12 slow outputs and a second ADS1115 (2-pack) for battery A/B, bus and PDH volts;
  - audio: the board's ES8311 + NS4150B speaker output into the TPA3255 through a two-stage RC tap; PCM5102A to LATER;
  - battery relays: a 200 A relay (the contactor's part) in each FRC battery's + lead with a 4.7 ohm bypass; firmware
    keeps only the fuller pack connected until the two are within 0.3 V (electrical/README, D.2.1 box);
  - safety remote: one of Micah's C3 SuperMinis instead of the $3.79 S3.
- Files: `bom/glacis_bom.py` (+ csv/json), `electrical/README.md`, `docs/glacis/JUDGMENTS.md`.
- Checks: no CAD change, so no robot.py run. glacis_bom.py runs clean: 119 rows.
- Parts list: $1,702.75 -> $1,733.78 (+$31.03).
- Not done: Google Sheet tab (claimed by the Windows chat), CAD/Onshape shelf (Waveshare footprint, two relays,
  PCA9685, second ADS1115), the "Glacis air & wiring" artifact. The Sidenote Cannon boards are updated.
- Questions for Micah: none.

## 2026-11-06 (evening) - Micah's main Claude Code chat - Glacis rev D.2 green light: CAD, Sheet, Onshape
- Branch / commit: main (this commit)
- Changed (Micah's follow-ups, JUDGMENTS "Rev D.2, Micah's follow-ups" F1-F8):
  - bottom cannon to full tank pressure: a second HSV04, MSI couplings on both chambers, 200 psi relief on both, caps 190;
  - fill line: female plug on the 1-1/2 in nipple through the panel, F x F elbow, male x male check valve, street elbow;
  - LED lean 17.5 deg; bumper backing a 1x6 ripped to 5 in with 2 in x 5 in foam (envelope unchanged);
  - electronics shelf: ESP32-P4 + C5 board, music ESP32, ADS1115, valve arm relay, one contactor; no PWM gate;
  - a second MOSFET 10-pack (the safety node's coil channel);
  - Micah's own Sheet edits folded into the script (TPA3255 $27.00, breakout board row, PETG $40, acrylic $150, tanks ordered).
- Files: `cad/glacis/params.py`, `gun.py`, `misc.py`, `pneu_parts.py`; `bom/glacis_bom.py` (+ csv/json);
  `docs/glacis/air_wiring_artifact.html`, `docs/glacis/img/elbow_ff.jpg`, `docs/glacis/JUDGMENTS.md`, `CLAUDE.md`.
- Checks (robot.py --checks, 56 min on this Mac under heavy swap): interference only the two known fitting slivers (146, 64 mm3) plus one new 53 mm3 nipple/check-valve overlap, fixed by modelling the F x F elbow at 17 mm per leg (re-checked in isolation: 0); elevation sweep 0-45 deg clean; every print fits the 250 mm bed; no multi-piece parts; LED strips 0 overlaps, every loop kept 100%; 47 frame pieces; envelope 37.7 x 27.7 in over the bumpers; gun 21.1 kg balanced on the pivot (valves at x 174.5).
- Parts list: $1,702.75 (D.1.4 $1,373.42; this round's changes +$129.59, Micah's Sheet edits +$199.74). Sheet synced.
- Onshape: Micah's view edits since D.1.4 (hide/show only) versioned first as "Micah's view edits (bumper covers hidden), before rev D.2"; then 14 tabs swapped into their sub-assemblies (Body frame now 7 tabs, 47 pieces; Lights 1-2; Body panels; Bumpers 46 parts; Pneumatics 46; Power 40; Gun 53), part counts checked against the manifest, descriptions re-set on 45 pneumatic and 30 gun parts, version "Glacis rev D.2" saved. Chassis and wheels unchanged (their STEPs differ by under 100 bytes). His custom tank Part Studio, its two instances and his mate group (on the Gun sub-assembly) untouched. Render: docs/glacis/onshape_rev_d2.jpg. His bumper-cover hides applied to the old instances, so the new covers show again.
- Questions for Micah: the breakout board row (which board, what price); the tanks' real port layout vs your custom tank.

## 2026-11-06 - Micah's main Claude Code chat - Glacis rev D.2 proposal: listing re-check, one controller, bumper foam
- Branch / commit: main (this commit)
- Changed (proposal, parts list and artifact only; no CAD):
  - every pneumatic listing re-read for thread size and gender; fill line fixed (female Milton 728 plug on the male x
    male check valve, which passes through the panel); 3 missing street elbows added;
  - top chamber fittings: the Amazon listings say "up to 150 lb" at 190 psi, so 304 stainless bushings (350 psi) and
    MSI couplings (150-300 psi) are proposed; HSV04 thread is "NPT / G" (test-fit); SZW-25 listing says 0-90 psi;
  - one ESP32-P4 + C5 board replaces the STM32 + C5 bridge; ADS1115; a classic ESP32 for Bluetooth music; PWM gate gone;
  - GoTo Foam bumpers, 1x6 backing (next CAD update), cost-downs (K-mac barrels, fog core, contactor, logic supply...).
  JUDGMENTS "Rev D.2 proposal".
- Files: `bom/glacis_bom.py` (+ csv/json), `docs/glacis/air_wiring_artifact.html`, `docs/glacis/parts_section.py`,
  `docs/glacis/img/` (product photos), `docs/glacis/JUDGMENTS.md`, `electrical/README.md`, `CLAUDE.md`.
- Checks: no CAD change. The artifact's shot model matches `range_model.py` (43.16 m/s, 245 ft at 190 psi top).
- Parts list: $1,373.42 -> $1,382.62 (+$9.20; the 1x6 boards are an $18 estimate).
- Not done (waiting on Micah's green light): Onshape update (queued: LED lean 10 -> 10.75 deg, 1x6 backing, fill line,
  tank ports and feet, controller shelf, top fittings), the Google Sheet (still D.1.4).
- Questions for Micah: top couplings (MSI) vs a 150 psi top cap; read the SZW-25 plate; keep the music board?;
  "0.75 closer" = degrees?

## 2026-11-05 - Micah's main Claude Code chat - Glacis rev D.1.4: printable frame, mounts, bumper ring, Xprite speakers
- Branch / commit: main, 230889f (+ the Onshape note after it)
- Changed:
  - the frame screws down to the chassis: side tabs on rail posts, end posts, tower brackets on rivnuts;
  - all #10-32s are the 1/2 and 2-1/2 in lengths Micah has;
  - bumpers are one plywood ring on T-nuts, held by 6 side screws reachable from below;
  - every clip laps its acrylic;
  - 45 mirrored, printable frame pieces;
  - Xprite 200 W speakers on a TPA3255 and a 48 V boost, with their cups screwed to the frame;
  - a print plan.
  JUDGMENTS N15-N27.
- Files:
  - `cad/glacis/params.py`, `body.py`, `misc.py`, `robot.py`, `lib.py`, `gun.py`, `drive.py`;
  - `render/print_plan.py`, `part_report.py`, `clip_check.py`;
  - `cad/requirements.txt` (rtree);
  - `bom/glacis_bom.py`;
  - `electrical/README.md`;
  - `docs/glacis/print_plan.md`, `part_report.md`, `JUDGMENTS.md`, `air_wiring_artifact.html`;
  - `docs/decisions.md`, `CLAUDE.md`.
- Checks (build 15):
  - interference: only the two known fitting slivers;
  - sweep clean;
  - every printed part within 250 mm and one solid;
  - every clip laps its acrylic, and no screws or inserts clash.
- Parts list: $1,373.42. Added: T-nuts, rivnuts, M4 x 8 and x 6 screws, M4 x 4 inserts, foam tape. Speakers are -$54. The Sheet and the air & wiring page are synced.
- Print estimate: 45 frame pieces on 11 plates, 2.97 kg PETG, about 37 h on CC1 + CC2.
- Onshape: 11 changed tabs swapped into their sub-assemblies, and version "Glacis rev D.1.4" saved. Micah's own edits (the
  custom tank Part Studio, its two instances and his mate group) are untouched, and versioned first as "Micah's
  edits (custom tank), before rev D.1.4".
- Questions for Micah:
  - "100 W drivers" read as the amps: confirm;
  - the T-nuts in place of wood inserts (1/4 in ply is too thin for them);
  - the open items in JUDGMENTS N26.

## 2026-11-04 - Micah's main Claude Code chat - Glacis rev D.1.3
- Branch / commit: main, 535d101 and 054765e
- Changed: each window wall chamfers from the acrylic's 7 mm ledge straight to its LED strip; the gap between
  back-to-back LED corners is filled (V ridges, those 24 joints glued); frame-tunnel strips modelled as one bent
  piece per member.
- Files: `cad/glacis/body.py`, `params.py`, `misc.py`, `robot.py`, docs
- Checks: 0 LED contacts, sweep clean, nothing over the bed, every part one solid
- Parts list: no change ($1,359.91)
- Not done: none (Onshape version "Glacis rev D.1.3" saved)
- Questions for Micah: none

## 2026-11-04 - Micah's main Claude Code chat - Glacis rev D.1.2
- Branch / commit: main, 75f1404 and 6df386a
- Changed: the LED band is the window wall, 25 mm behind the acrylic; shared-edge insets by the corner bisector
  (31-36 mm), so neighbouring strips meet back to back and never overlap.
- Checks: clean. Onshape version "Glacis rev D.1.2".

## 2026-11-03 - Micah's main Claude Code chat - Glacis rev D.1.1
- Branch / commit: main, 10d22a5
- Changed: LED loops, Micah's Zmoon 12 in light bar (STM32 PWM), tank fit (two 6 L), parts cost-down to
  $1,359.91 (cheapest of AliExpress, Amazon and McMaster).
- Checks: clean. Onshape version "Glacis rev D.1.1".

Older history: `git log` and [decisions.md](decisions.md).
