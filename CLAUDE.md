# Brophy T-Shirt Cannon Mark 5 — Claude Code Handoff

Drop this file in the root of the project repo as `CLAUDE.md`. Claude Code reads it automatically every session.

---

## How to work on this project (read first)

You are the lead engineer on a high school robotics build. Think like the best high school robotics student in the world: scrappy, clever, allergic to overpaying, and obsessed with things actually working on event day.

1. **Be hyper creative.** Before accepting the "normal" part for a job, ask: could this be a 3D print, a repurposed FRC stash part, an automotive / train-horn / air-ride part, a hardware-store part, or an AliExpress part at a fraction of the price? Offer the clever option, not just the catalog option.
2. **Make it as affordable as possible.** The budget ceiling is ~$2,000, but the target is *as cheap as possible*. Every line item should have a reason it can't be cheaper.
3. **Trust 3D prints about twice as much as conventional wisdom does.** Prints are strong. Default to printing brackets, mounts, gearbox housings, wheel hubs, mecanum rollers, sensor housings, cable management, enclosures, LED diffusers, and structural nodes. Size printed parts with roughly half the safety margin people usually demand for prints. Use smart orientation, more perimeters, and the right material instead of reaching for metal.
   - **The one hard exception: nothing printed on the pressure boundary.** Tanks, firing chambers, valves, fittings, and anything holding 150 PSI air stays rated metal / rated commercial parts. A printed part failing under pressure near a crowd is shrapnel. This is not up for debate.
   - Material: assume outdoor use in Arizona heat. PLA will creep and soften in a sun-baked robot. Prefer PETG, ASA, or PA-CF / PETG-CF for structure and TPU for rollers, bumper parts, and vibration isolators.
4. **Search the web fast and often.** Don't recommend a part from memory. Find the actual best product for the purpose, confirm it is in stock, confirm the price, and record the link and date checked. If a listing can't be verified (Amazon often blocks scraping), say so and mark it `[UNVERIFIED]` instead of guessing specs.
5. **Check thread standards every time.** Cheap import pneumatic parts are often G/BSPP, not NPT. Confirm NPT on every valve, QEV, and fitting before it goes on the BOM.
6. **Don't re-argue settled decisions** (see Key Decisions). If you think one is wrong, flag it with evidence, then wait for Micah.

---

## TL;DR

Mark 5 is a ground-up rebuild of Brophy College Prep's t-shirt cannon robot, built and operated by the Broncobots robotics club on behalf of student council for parades, games, and gym events. It's a three-barrel pneumatic cannon on a mecanum drive, controlled by an ESP32 over a WebSocket web UI so any laptop/phone can drive it with no special software.

**Status:** Design phase. Pneumatic architecture is chosen (150 PSI, Option A). The "Glacis" design (rev C.2, two in-line cannons 8 mm apart balanced on a pivot axis between them, the old cannon's Atlantic Valves SZW-25 firing valves, 0.53 L 2 in pipe chambers, a main valve then one in valve per chamber with no check valves) is fully modelled in `cad/glacis/` (CadQuery) and imported to Onshape ("Brophy Mark 5 - Glacis"); its parts list is the "Glacis BOM" tab ($1,512.44, 2026-11-03) and its decisions are in `docs/glacis/JUDGMENTS.md`, awaiting Micah's review. Nothing has been purchased or built. No firmware or dashboard code yet. Video is still goal-level only.

---

## Goal / what "done" looks like

A reliable, good-looking, self-contained cannon that:
- Boots in under 3 seconds and needs near-zero setup at events (Mark 4's biggest failure)
- Fires three barrels at variable, software-set pressure up to 150 PSI
- Refills itself from an onboard 12V compressor, quietly enough for a crowd
- Drives on gym floors, turf, and ideally grass/gravel/ramps
- Elevates 0–90°
- Is controlled from any device's browser via WebSocket, with any HID / keyboard / trackpad mappable from the UI
- Shows a dashboard: per-tank pressure, a robot rendering (with its lights), battery level, and video feed
- Has LEDs (cannon, underglow, glowing acrylic body, under the bumper foam), a speaker horn, and fog effects
- Doesn't fall apart and is easy to service

---

## Current state

| Subsystem | Status |
|---|---|
| Goals | Done — Google Doc (full text in Appendix A) |
| Pneumatic architecture | Decided (Option A, 150 PSI); QEV size pending (3/4" Parker proposed, see Open questions) — parts not purchased |
| Compressor | Closed 2026-11-01: ZHSYMX SQ420, 1.41 CFM free air, 100% duty @ 100 PSI (seller spec) — not purchased |
| Sensors / ADC | Glacis rev C.3 proposal: three identical 0-300 psi 0.5-4.5 V transducers (tank, two chambers), the arm-angle pot (on 3.3 V), battery and PDH volts into the STM32 ADC; fog core thermocouple, fog fluid level switch, three DS18B20s; no dial gauges |
| Power / electrical | Glacis rev C.3 proposal (2026-11-03, Micah's call): main breaker -> STM32-switched 200 A contactor -> PDH; an always-on 5 V buck-boost logic rail (STM32, ESP32s, sensors) tapped ahead of it, so status works with the PDH dead; rear E-stop opens both the contactor and the valve-rail relay. Main valve is now a manual ball valve. Full write-up in `electrical/README.md` |
| Fog machine control | Glacis rev C.1 proposal (2026-11-03): custom 12 V fogger, two 200 W cast fog heater cores (AliExpress, $22.42 each) with peristaltic pumps, MAX6675 thermocouples, KSD301 250 C cutouts and a relay per core, a 5015 blower; printed splitter to a smoke collar over holes in both barrels and trail vents front and rear. Replaces the XLR-remote plan if Micah agrees |
| Drive motors / control | Glacis rev C proposal: Falcon 500s on STM32 PWM through a safety-gated buffer; ESP32-S3 is the WiFi bridge only; ESP-NOW safety node + handheld remote |
| BOM | In `/bom/` (Micah's xlsx + CSV mirrors via `bom/xlsx_to_csv.py`). Pneumatics + electronics re-verified live 2026-11-01: Tier A $1,213, A+B $2,283 (over the ceiling; cuts proposed in `docs/decisions.md`). Chassis/drive/aesthetics still Aug-2026 estimates |
| Chassis | Glacis rev C (2026-11-02): 1x2/1x1 x 1/16 aluminum box tube + 1/8 in gussets, printed body frame (60 deg front, leaning sides and back), recessed frosted acrylic with chamfered corner clips; rev C.2: a 60/m LED loop on a leaning rail 1.15 in behind each panel, a 100/m strip through a tunnel in every frame member so the frame glows, and two slim 100 W siren speakers in notches high in the front-side corners. Awaiting Micah's review |
| Mecanum wheels | Glacis rev C (2026-11-02, from Micah's TTB-0010 vector wheel): 10 in vector-style printed mecanum, 10 rollers (42 mm) on 608 2RS + fixed M8 rods, two-half PETG-CF hub with a 116T pulley (flange 1.27 in off the floor), three flat 1/8 in aluminum plates; Falcon 12T one-stage belt 9.67:1, 1/2 hex live axles. Not printed or tested |
| Elevation (0–90°) | Glacis rev C: gun balanced on a 1/2 hex axle between the two cannons; goBILDA 5203 99.5:1 (60 rpm) on a Spark MAX, 16T->56T 9 mm belt, pot on the axle. Not built |
| LEDs, horn, video, dashboard UI | Glacis rev C.2: LEDs and horn speakers modelled (see Chassis); video and dashboard UI not designed |
| Firmware | Not started (rev B splits it: STM32 main, ESP32 WiFi bridge, ESP32 safety node, ESP32 remote) |
| CAD | `cad/glacis/` (CadQuery, checks clean) -> Onshape "Brophy Mark 5 - Glacis" (STEP import) |

---

## Key decisions (settled — don't undo without asking)

**Pneumatics: Option A, 150 PSI**
- Two pressure zones. High side: 3-gallon-class tank + fill valve at 150 PSI. Chamber side: capped in software *and* by a hardware relief valve.
- One shared fill solenoid + one fill-manifold pressure sensor feeding all three barrels.
- Each barrel: check valve → small steel firing chamber → **1" NPT quick exhaust valve (QEV)** as the firing valve, piloted by a small 3-way solenoid (dump solenoid, Vixen VXA7164 or equivalent 1/4" NPT 12V horn valve, ~$12 each).
- Why 150 not 200: every 1" QEV found is rated 150 PSI max, and a 1" QEV at 150 PSI moves roughly 3x the air of a 1/2" QEV at 200 PSI. Valve bore limits shot performance more than pressure does.
- Why QEV: opens full-port in ~10 ms vs ~80 ms for a big direct solenoid, and it's cheap.
- Variable pressure: meter air from the reservoir into each firing chamber with a ~$22 direct-acting solenoid, closed-loop against a pressure transducer. Rejected a ~$250 proportional regulator.
- (2026-11-03, Micah, Glacis rev C.2) The shared fill solenoid, fill-manifold sensor and per-barrel check valves are replaced by a main valve (tank shut-off) and one direct-acting in valve per chamber, each metering against its own chamber transducer. No manual bleed valve: the relief pull rings are the hand dump.
- 200 PSI is a future upgrade path (swap tank + valves, reuse chambers, sensors, electronics).
- Option A was estimated at roughly $455–545 for the full 3-barrel pneumatic system (pre-verification).

**Air supply**
- Tank volume beats compressor CFM. A 12V compressor can't keep up with live firing; its job is recovery between volleys.
- Reality check on the goals doc: "10 shots stored, refill 1 shot per 5 minutes" is backwards from what these pumps do. A ~2 CFM 12V compressor recovers roughly one shot every 30–60 seconds, indefinitely.
- Candidate: **ZHSYMX 300 PSI ultra-quiet 12V, ~$128, Amazon ASIN B0D6ZYBT4T.** Confirmed: 69 dB, 300 PSI max, 20 A, 1/4" NPT outlet. **Confirmed 2026-11-01 (seller spec chart): 1.41 CFM free air, 100% duty at 100 PSI, 242.7 × 127.9 × 181 mm; "300 PSI" is intermittent, 200 working. Weight still unlisted.**
- Pair the compressor with a Vixen tank kit (includes 170/200 PSI pressure switch + safety relief valve). Note the switch range vs the 150 PSI operating plan — see Open Questions. *(2026-11-01: the Vixen kit didn't verify — a standalone Viair 91028 2.5 gal / 200 PSI tank is on the BOM instead; see `docs/decisions.md`.)*
- Reference/benchmark pumps: Viair 400C / 444C (~$150–190, honest specs), HornBlasters HB-3Q (~$266, genuinely engineered quiet, published fill data).
- Noise is solved at the system level, not by buying a premium pump: wide pressure-switch differential, remote/relocated intake, vibration isolation mounts (printed TPU is perfect), and pre-charging from a shop compressor before events.

**Sensors & plumbing**
- Stainless 0–300 PSI (tank) and 0–200 PSI (chambers) transducers, 0.5–4.5 V output, read through an **ADS1115 16-bit ADC** (ESP32's built-in ADC is too nonlinear).
- Chamber side tubing: DOT nylon air-brake tubing, 1/4" OD (150 PSI working / 950 PSI burst), brass compression fittings.
- (2026-11-01) Every chamber gets its own 150 PSI relief, bleed valve and gauge on a 2"×1/4" bushing service port: it is sealed behind its check valve and the QEV diaphragm, so the manifold relief and bleed can't reach it, and sun heating takes 150 PSIG to ~170. The tank → fill valve run is hard-plumbed brass; nylon only downstream of the fill valve. FRC stash pneumatics (~120–125 PSI rated) never go on the 150 side.

**Electronics & drive**
- **ESP32** is the brain. WebSocket control, no FRC control system ("no FRC nonsense").
- Motors: use the old **FRC stash 12V motors** — free, and they take the same PWM.
- Falcon 500s are a fallback only: the Talon FX accepts plain 1–2 ms PWM on its green/yellow CAN pair (1.5 ms neutral, period 2.9–100 ms), so an ESP32 LEDC channel drives it directly with no CAN transceiver. Skipped because Falcon-spline adapters cost money and the stash motors are free.
- FRC stash covers at $0: motors, ESCs/motor controllers, batteries, charger, main breaker hardware.

**Fog machine**
- Use Micah's existing fog machine, which has a 3-pin XLR "REMOTE CONTROL" jack. Rejected: BORGOVA (ASIN B0F4XJMNFR) — no remote jack.
- Plan: female Neutrik NC3FXX plug (no machine modification) → opto-isolated relay module (SRD-05VDC type) across the fog-trigger pins. Optional PC817 optocoupler from the heater-ready pin to an ESP32 GPIO for closed-loop timing.
- Before wiring: map the pinout with a multimeter and measure voltage on each pin with the machine on (could be low-voltage DC *or* mains). Common convention is pin 1 = common, pin 2 = fog trigger, pin 3 = heater-ready — **verify, don't assume.**
- Firmware duty cycle: ~10–15 s bursts, 30–60 s recovery. Don't switch the machine's mains power as the control (heater warm-up). AUTO mode disabled; the ESP32 owns timing.

**Approach**
- Off-the-shelf automotive / train-horn / air-ride pneumatics + custom 3D-printed everything-else.
- Tiered BOM: Tier A minimum viable (~$900), Tier B recommended (~$1,700 total, ~$300 headroom), Tier C stretch / cut-first, Tier H FRC stash ($0). *(Verified 2026-11-01: Tier A $1,213.35 now includes one complete barrel; A+B $2,282.56.)*
- Safety redundancy: hardware relief valves and caps in addition to software limits.

---

## Constraints

- Budget: ~$2,000 hard ceiling, cheaper is better. No timeline pressure.
- Operating environments: gym floors, turf, parades (outdoors, crowds, heat).
- Fab access: plasma cutter, CNC, waterjet, 3D printers.
- Must be easy to service even if the chassis is welded.
- Control must work from any device with a browser. No special drivers, apps, or FRC Driver Station.
- USB straight to the robot; boot in under 3 seconds.
- Pressure boundary: rated parts only, NPT threads confirmed, hardware relief on every pressure zone.

---

## Next steps (start here)

1. **Set up the repo.** Suggested layout:
   ```
   /CLAUDE.md            this file
   /docs/decisions.md    running decision log (append, don't rewrite)
   /docs/goals.md        Appendix A, kept current
   /bom/                 BOM (Micah's existing xlsx + a CSV mirror you keep in sync)
   /firmware/            PlatformIO ESP32 project
   /dashboard/           web UI served by the ESP32 (WebSocket client)
   /cad/                 parametric printable parts (CadQuery or OpenSCAD) + STL exports
   /electrical/          wiring diagram, pinout table, power budget
   ```
2. **Ask Micah to drop the existing BOM spreadsheet into `/bom/`.** It was built in a claude.ai chat (openpyxl + formula recalc, yellow editable cells, a Design Notes sheet and a cut-priority list). Don't rebuild it from scratch if he has it.
3. **Re-verify every BOM line live**: in stock, current price, link, date checked, NPT confirmed. Hunt for cheaper substitutes, especially printable ones. Flag anything that changed.
4. **Close the compressor question**: find CFM and duty cycle for the ZHSYMX (Amazon Q&A, seller, reviews, YouTube tests, sister listings of the same OEM pump). If you can't, compare against a Viair 400C/444C or a well-reviewed 480C clone and recommend.
5. **Verify 1" NPT QEVs** that are actually in stock, rated ≥150 PSI, with real NPT threads.

   *Steps 1–5 done 2026-11-01 (see `docs/decisions.md`). Before firmware: Micah's calls on the QEV size, pressure-switch scheme and budget cuts.*
6. **Firmware skeleton** (PlatformIO, ESP32): WiFi AP mode, WebSocket server, serve the dashboard from flash, ADS1115 pressure reads, LEDC PWM drive outputs, a fire sequence state machine (meter → hold → arm → fire → vent), and a software pressure cap. Boot target < 3 s.
7. **Dashboard v0**: drive controls with remappable keyboard/HID/gamepad bindings, per-tank pressure, battery, fire buttons, arm switch.
8. **Then** the open subsystems: chassis, printed mecanum, elevation, LEDs, horn, video, fog. Propose clever, cheap options for each with live-verified parts.

---

## Open questions (who resolves)

- **Chassis**: aluminum extrusion (T-slot accessorizing) vs welded steel? (Micah) — you can propose a hybrid, e.g. welded steel base with T-slot uprights.
- **Barrel layout**: goals listed triple barrel / magazine / rotary / revolver. Pneumatics were designed for 3 fixed barrels. Confirm triple barrel is final. (Micah)
- **Mecanum on grass/gravel**: mecanum is weak on soft and loose terrain; this was flagged in the BOM notes. Is gym + turf enough, or does it need a different drive? Custom printed mecanum with TPU rollers is the stated preference. (Micah, with your analysis)
- **QEV size**: no 1" QEV is in stock, affordable, ≥150 PSI and NPT on all three ports (ROSS $486 backordered, AIGNEP $256, Mead quote-only). Proposed: Parker 0R75B 3/4" NPTF ($101–125, in stock); likely flows at least as well as those 1" valves (inferred). (Micah)
- **Pressure switch mismatch**: Vixen kit switch is 170/200 PSI but the plan is 150 PSI operating. Decide: lower-range switch, regulator between tank and fill side, or software-controlled compressor relay. (You propose, Micah decides) — **Proposed 2026-11-01:** ESP32 relay off the tank transducer (quiet mode), a $23 120/150 switch in series with the relay coil as backstop, 165 PSI tank relief.
- **Budget**: verified A+B is $2,282.56, $282.56 over the ceiling. Proposed cuts in `docs/decisions.md` (horn valves, stash wire/aluminum, printed rollers/brackets) bring it to ~$1,970. (Micah)
- **Fittings**: DOT push-to-connect instead of the settled brass compression (same price, DOT-rated 250 PSI, easier service; the compression listing didn't confirm nylon-tube inserts). (Micah can veto)
- **Which FRC stash motors** exactly (CIM? mini-CIM? 775?), which motor controllers, and how many? `[UNKNOWN]` (Micah)
- **Which ESP32 variant**? An S3 gives native USB. Video livefeed may need a separate ESP32-CAM or a cheap USB camera + another board. `[UNKNOWN]` (You propose) — **Proposed:** ESP32-S3-DevKitC-1-N8R8; video on a Pi Zero 2 W so it can't delay fire commands. *(2026-11-03, rev D: the bridge is an ESP32-C5 on 5 GHz; one of Micah's S3s is the safety node, the other is spare; camera deferred. No STM32 has WiFi built in, so the STM32F411 stays for the real-time work. See `electrical/README.md`.)*
- **Range (2026-11-03, rev D proposal, Micah's picks):** targets are one 200 ft shot (top cannon) and 120 ft shots, 6 per cannon (12) per tank charge, 10 each ideally. Top = old 1 gal tank on a U.S. Solid USS-HSV04 (725 psi, so it runs to full tank pressure); bottom = 3 in Sch 40 x 10 in chamber (~1.35 L) on the old SZW-25 (110 cap); both barrels 36 in; five 6 L tanks (30 L). Not in the CAD yet. Open: the old tank's nameplate rating, the HSV04's opening time (bench test), a compressor that reaches 200 psi. See JUDGMENTS D1-D8 and `cad/glacis/range_model.py`.
- **Which fog machine model** Micah owns, and its measured XLR pinout. `[UNKNOWN]` (Micah)
- **What's salvageable from Mark 4** (tanks, valves, barrels, battery)? `[UNKNOWN]` (Micah)
- **Turret** (nice-to-have) and **cooling system** (purpose unclear: compressor cooling? electronics in heat?) `[UNKNOWN]` (Micah)
- **Tank count/size**: architecture assumes a ~3-gallon reservoir; final tank not chosen. — **2026-11-01:** Viair 91028 2.5 gal / 200 PSI on the BOM; second tank moved to Tier C (the three charged chambers are the burst).

---

## Dead ends (don't retry)

- **BORGOVA fog machine** (ASIN B0F4XJMNFR): no remote jack.
- **200 PSI build (Option B)**: weaker real-world shots because QEVs that size are 1/2"; costs more ($535–635).
- **Proportional regulator for variable pressure** (~$250): replaced by a ~$22 metering solenoid + transducer.
- **Big direct-acting solenoid as the firing valve**: too slow (~80 ms) vs a piloted QEV.
- **ESP32 built-in ADC for pressure**: nonlinear; use ADS1115.
- **Running CAN to Falcons from the ESP32**: unnecessary, PWM works; and stash motors are free anyway.
- **Buying a premium quiet compressor to solve noise**: system-level fixes are cheaper and work better.
- **Scraping Amazon listings**: Amazon blocks automated access. Use search snippets, Q&A, reviews, and other retailers.

---

## Context

- **Brophy** = Brophy College Preparatory (Phoenix, AZ). **Broncobots** = its FRC/FTC/VEX robotics team.
- **Micah Tucker** = project lead, Education Chair on Broncobots senior leadership. Designs in Onshape. Uses ESP32s regularly.
- **Mark 4** = the current cannon: falling apart, ugly, built on 15-year-old FRC parts, heavy setup burden, unreliable.
- **QEV** = quick exhaust valve. **NPT vs G/BSPP** = US tapered pipe thread vs British parallel thread; they don't mate properly.
- Goals Google Doc: "Brophy T-Shirt Cannon - Mark 5" in Micah's Drive (not public). Text copied in Appendix A.

---

## How Micah works

- Wants it cheap, clever, and verified. Show the price, the link, and that it's in stock.
- Likes tiered BOMs (minimum viable → recommended → stretch → stash).
- Prefers 3D printing aggressively and off-the-shelf automotive pneumatics.
- Values safety redundancy (hardware + software) without letting it bloat the budget.
- Direct and fast. Lead with the answer, keep explanations tight.

---

## Appendix A — Goals doc (verbatim content, lightly formatted)

```
Brophy T-Shirt Cannon - Mark 5
Team: Micah Tucker

Goals:
- Construction
  - Aluminum extrusion construction
    - T-slot or other for accessorizing?
    - Maybe welded steel so it literally can't fall apart for the chassis
  - Frosted acrylic body
  - Clear tube?
  - Soft bumpers
    - White
    - Backlit?
  - 1in thinner for doors
- Functionality
  - Multi shot
    - Triple barrel
    - Magazine (ref: https://www.youtube.com/watch?v=Yn_wtP6Gjho)
    - Rotary (ref: https://www.youtube.com/watch?v=1Zqx96xyHDk)
    - Revolver
  - Self-sufficient air system
    - 10 shots in permanently fixed tank
    - Fills 1 shot worth every 5 minutes
  - 0-90 degree range
  - Speaker horn (different tones, control volume, etc)
    - Music?
    - How custom do we want this...
  - All terrain mecanum
    - like gravel, grass, and ramps
    - Good for gym floors
    - Custom?
    - (an AliExpress all-terrain mecanum set at ~$108 was noted as "expensive")
  - Variable pressure
    - Rapid actuator to secondary tank
  - Turret (might be doing too much but would be super cool)
  - Cooling system
  - 150psi
- Electronics
  - Runs off ESP32 or other
  - Control via WebSocket (any remote usable)
    - Any device
    - easier to code
    - No frc nonsense
  - USB straight to robot
    - <3 sec boot
  - Dashboard
    - Show pressure (of each tank)
    - Robot rendering (with lights)
    - Battery
  - Video livefeed
- Aesthetics
  - LEDs
    - Cannon
    - Underneath
    - Acrylic body glow
    - Under bumper foam
  - Smoke machine
    - Out of cannon
    - Under bumper

Context (Micah's words, cleaned up):
Mark 4 is literally falling apart, looks terrible, uses 15-year-old FRC parts,
and has a ton of setup and reliability issues. We want more shots and variable
shots. Maybe weld the chassis if it can still be easily serviced. I want it
controlled via an ESP32 and a WebSocket that lets you connect any HID or use
keyboard/trackpad, so anyone with a Mac could connect and we don't need specific
hardware or software. I think custom 3D printed mecanum wheels would be good.
We have a plasma cutter, CNC, and waterjet. The robotics club operates it for
student council.
```

---

## AUDIT

**Reread as a stranger:** The pneumatic plan is solid and specific. Everything else (chassis, drive, elevation, aesthetics, video) is goal-level only, so expect to do real design work there, not just implementation.

**Most likely missing or wrong:**
1. The BOM spreadsheet itself isn't here, and its prices are from early September 2026. Treat every price as stale until re-checked.
2. The "1" in thinner for doors" goal is unexplained.
3. Tank size (~3 gal) and the pressure-switch range vs 150 PSI operation aren't fully reconciled.

**Questions for Micah before handing off:**
1. Can you add the BOM .xlsx and any Mark 4 parts you plan to reuse?
2. Which exact stash motors/controllers, and which fog machine model?
3. Is triple barrel final, and is gym + turf enough for the drive, or must it handle grass/gravel?
