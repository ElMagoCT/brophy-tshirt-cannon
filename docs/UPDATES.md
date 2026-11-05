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
