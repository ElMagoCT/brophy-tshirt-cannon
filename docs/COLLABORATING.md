# Editing the design with your own Claude

The robot ("Glacis", Brophy T-shirt cannon Mark 5) is a parametric CadQuery model in this repo. Several people and
several Claude chats edit it, so the repo is the single source of truth and [UPDATES.md](UPDATES.md) is how
everyone knows what changed and who's working on what. Micah decides; everyone else proposes through pull requests.

## Setup (once)

1. Micah adds your GitHub account to the private repo `ElMagoCT/brophy-tshirt-cannon`; accept the invite.
2. Clone it and set up Python 3.12:
   ```bash
   git clone https://github.com/ElMagoCT/brophy-tshirt-cannon.git
   cd brophy-tshirt-cannon/cad
   python3.12 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
   (Windows: `py -3.12 -m venv .venv`, then `.venv\Scripts\pip install -r requirements.txt`.)
3. Claude Code reads `CLAUDE.md` automatically: it holds the project's rules and settled decisions.

## Every session

1. **Start:** `git pull`, then read the "In progress" table and the newest entries in [UPDATES.md](UPDATES.md), and
   `gh pr list` for open pull requests. Don't redo or undo someone else's open work.
2. **Claim:** add a line to "In progress" with the files you'll change, commit just that, and push it to `main`
   (`git commit -m "Claim: <topic>" docs/UPDATES.md && git push`). If a file you need is claimed, wait or ask Micah.
3. **Branch:** do the work on `<your-name>/<topic>` (for example `mckenna/battery-door-latch`), not on `main`.
4. **Change the design** (see "Where things are" below). Keep to the rules in `CLAUDE.md`:
   - nothing printed on the pressure boundary; rated parts and NPT threads only; a hardware relief on every pressure zone;
   - PETG for printed parts;
   - don't undo a settled decision: write it up under "Questions for Micah" instead.
5. **Check:** from `cad/glacis`, run `../.venv/bin/python robot.py --checks` while iterating, then
   `../.venv/bin/python robot.py` once for the STEP export, parts rollup and renders. The results are in
   `out/check_log.txt`. The checks cover:
   - interference;
   - the 0-45 deg gun sweep;
   - the 250 mm print bed;
   - parts that come out in more than one piece.

   A full build takes 10-45 min and a lot of memory, so run only one at a time.
6. **Parts list:** if parts change, edit `bom/glacis_bom.py` (never the CSV/JSON by hand) and run it
   (`cad/.venv/bin/python bom/glacis_bom.py`). Each new price needs:
   - a live link;
   - the date you checked;
   - `[UNVERIFIED]` if you couldn't confirm it.
7. **Finish:**
   - Add an entry at the top of UPDATES.md using its template, and remove your "In progress" line.
   - Commit (message `Glacis: <what changed>`) and push the branch.
   - `gh pr create --fill`, then paste your UPDATES entry as the PR description.
   - Don't merge your own PR. Micah (or his main chat) reviews, merges, imports to Onshape and syncs the parts Sheet.

## Only Micah's chats do these

Leave them under "Not done" in your entry:
- the Onshape import and named versions (document "Brophy Mark 5 - Aurora Broncoalis");
- the "Glacis BOM" Google Sheet and the parts artifact;
- anything that buys, sends, publishes or signs in;
- revision names (D.1.4 and so on). Name your change by topic.

## Where things are

| File | What it is |
|---|---|
| `cad/glacis/params.py` | Every shared number: frame, rails, bumpers, body outline, gun, tanks, speakers, mount stations |
| `cad/glacis/body.py` | Body shell, panels, printed frame, LED window walls, tunnels, sectioning into printable pieces, joints |
| `cad/glacis/misc.py` | Towers, tanks, smoke, electronics, bumpers, frame mounts, speakers and light bar placement |
| `cad/glacis/drive.py`, `gun.py`, `speakers.py`, `pneu_parts.py` | Chassis and wheels, the two cannons, speaker pods, pneumatic parts |
| `cad/glacis/robot.py` | Assembly, checks, export |
| `cad/glacis/render/print_plan.py`, `part_report.py` | Print estimate and printability report for the printed parts |
| `bom/glacis_bom.py` | The parts list (writes `glacis_bom.csv`, `glacis_bom_sheet.json`) |
| `docs/glacis/JUDGMENTS.md` | Every design call and why, awaiting Micah's review |
| `docs/decisions.md` | The running decision log |

`cad/glacis/out/step/` is generated: don't commit it.
