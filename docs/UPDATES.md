# Design updates (shared log)

Everyone who edits this design, whether a person or any Claude chat, reads this file before starting and writes
here when they finish. Newest entry first. How it works: [COLLABORATING.md](COLLABORATING.md).

## In progress

Claim the files you're about to change, and push the claim before you edit. Remove your line when your entry
below lands. If someone else has claimed a file you need, wait or ask Micah.

| Who (and which chat) | Started | Working on | Files |
|---|---|---|---|

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

## 2026-11-08 - Micah's Windows computer (Claude Code) - Printable mini kit of Glacis
- Branch / commit: `micah-windows/mini-model`, https://github.com/ElMagoCT/brophy-tshirt-cannon/pull/1
- Changed (no change to the robot design):
  - a 1:9 desk mini of the rev D.2 body form (2.22 in wheelbase; Micah's floor is 2 in, 1:10), built from the real
    model (`body.body_solid`, `panels_for`, speaker pods, light bar, `gun.build` parts and pivot);
  - the gun elevates on a 1.75 mm filament pin, in a 2.05 mm hole that is open on the left bearing block and blind
    in the right;
  - colour comes from glue-in pieces, not in-place colour (that took 10-16 h and 265-469 filament changes):
    - red windows;
    - black speakers, light bar, and chambers (the chambers peg onto the cradle);
    - the body prints black below the bumper;
  - four sliced OrcaSlicer projects, one per printer, all printing at once:
    - CC2 #1 body, 4 h 21 m Balanced (~2 h 55 m Ludicrous);
    - CC2 #2 gun, 1 h 22 m;
    - CC1 #1 black kit, 25 m;
    - CC1 #2 red windows, 17 m;
  - PETG, 0.4 nozzle, Orca's 0.20 mm Standard; organic slim supports from the plate only, with PLA interface;
  - the scale is the largest whose slowest plate fits about 3 h on Ludicrous (`mini_3mf.py --fit` found 1:8.91);
  - print and assembly guide: `docs/glacis/mini_model.md`.
- Files:
  - `cad/glacis/mini.py`, `mini_3mf.py` (new);
  - `cad/glacis/mini_orca/` (Orca's Elegoo CC1/CC2 presets, flattened);
  - `cad/glacis/out/mini/` (STLs, 4 projects, previews, kit.json, slice_report.json);
  - `docs/glacis/mini_model.md`.
- Checks:
  - `robot.py --checks` (85 min on this PC): interference is only the two known fitting slivers (146, 64 mm3); the
    elevation sweep is 0-45 deg clean; no part comes out in more than one piece; 47 frame pieces;
  - the mini's own checks:
    - the gun swing, every 5 deg from 0 to 45, is clear of the body with every glue-in in place;
    - each glue-in is clear of its seat;
    - every piece is one solid and fits the bed;
    - the pin hole is blind.
  - The Ludicrous times are Orca's Balanced estimate / 1.5; the Ludicrous % (166) comes from CC1 reviews, so the
    times are unverified on a real print.
- Parts list: no change.
- Not done: nothing printed yet; no Onshape or Sheet change needed.
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
