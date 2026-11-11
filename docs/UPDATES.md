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
