# Decision log

Append new entries at the bottom; don't rewrite old ones. If a decision is
reversed, add a new entry that says so.

Decisions settled before this repo existed (Option A pneumatics at 150 PSI,
ESP32 + WebSocket, stash motors on PWM, fog via the XLR remote jack, the tier
scheme) live in `CLAUDE.md` → "Key decisions". The verified parts, with links,
stock and threads, are in `bom/` (the xlsx and its CSV mirror).

---

## 2026-11-01: BOM re-verified live (pneumatics + electronics)

Pneumatic and electronics lines were checked against live listings for price,
stock, link and thread. Chassis, drive and aesthetic lines are still Aug-2026
estimates and are labelled that way in the sheet.

- **Tier A: $1,213.35** (was ~$900). **Recommended A+B: $2,282.56**, which is
  $282.56 over the $2,000 ceiling. See "Budget" below.
- Where the Tier A increase came from:
  - **+$179:** the spreadsheet's Tier A had no firing valve, dump valve or
    barrel (all were Tier B), so Tier A could not actually fire.
  - **+$141:** the ~$110 compressor + tank kit doesn't exist in a usable form.
    The parts are now bought separately.
  - **+$22:** a per-chamber relief, bleed valve and bushing (safety, see below).

### Compressor: closed

- **ZHSYMX SQ420** (Amazon B0D6ZYBT4T), $127.99, 19 left.
- **Flow and duty:** 1.41 CFM free air, 100% duty at 100 PSI. Both come from
  the seller's own spec chart; no temperature is given.
- **Pressure:** the "300 PSI" is the intermittent maximum. Working pressure is
  200.
- **Size:** 242.7 × 127.9 × 181 mm. Weight is not listed.
- **In the box:** a leader hose with a check valve, a remote intake filter and
  vibration isolators. No switch or relay.
- **Recovery:** flow at 100 and 150 PSI is unpublished; estimated about 0.8 and
  0.57 CFM. That works out to about 25–30 s per 0.91 L chamber at 120 PSI.
- **Kept over the Viair 444C** ($215.80, published flow table): $88 cheaper,
  quieter, and it already includes the hose, check valve, filter and isolators.
  The 444C is the upgrade if recovery is too slow.

### Tank: Viair 91028, standalone

- **The part:** Viair 91028, 2.5 gal steel, rated 200 PSI, six 1/4" NPT ports,
  $99.99 at Summit.
- **Why not the kits:**
  - Vixen 3 gal kit: price unverified, its 170/200 switch would need swapping,
    and the relief setting isn't stated.
  - Cheap kits: either the tank rating is unverified or the tank is rated only
    150.
- **Availability:** a search snippet says Viair discontinued the 91028, so buy
  it soon.

### Shot math

- One shot from a 0.91 L chamber at 120 PSI uses about 7.4 L of free air.
- Taking the tank from 150 down to 120 PSI refills about 2.6 chambers.
- **Three barrels:** about 5 full-power shots back to back, then one every
  ~25–30 s.
- **Tier A (one barrel):** about 3–4 shots, then the same rate.

### QEV: proposed change from 1" to 3/4"; Micah decides

- **No usable 1" option.** No 1" QEV is in stock, affordable, rated ≥150 PSI
  and NPT on all three ports.
  - **ROSS 1868A6005:** $486, backordered.
  - **AIGNEP 82650-16:** $256, and possibly 2-port.
  - **Mead 6QEV:** quote only.
  - **Cheap "1 inch" QEVs:** G/BSPP, or the thread type isn't stated.
- **Proposal:** Parker 0R75B, 3/4" NPTF on all three ports, rated 150 PSI.
  $101.16 at General Industrial (2 in stock) or $124.95 on Amazon (14 left).
- **Flow (inferred):** it is the largest valve in Parker's 0R series, which
  spans Cv 2.7–10 and 150–550 SCFM, so it probably flows at least as well as
  the 1" valves found (ROSS Cv 7.2, Mead Cv 4.12). Parker doesn't publish Cv
  per model.

### Tier A = one complete barrel

Tier A now buys barrel 1's whole firing chain: QEV, dump valve, check valve,
chamber, barrel and service port. Tier B adds barrels 2 and 3.

### Per-barrel chain (replaces "three QEVs off one shared chamber")

- **Path:** manifold → check valve → QEV inlet, with the dump valve tee'd in
  right there. The QEV cylinder port goes to the chamber; the exhaust goes to
  the barrel.
- **Fail-safe:** a 2-way normally-closed dump plus the check valve does what a
  3-way pilot would, and it cannot fire on power loss.
- **Firmware/electrical:** add pull-downs on the dump relay inputs so it can't
  twitch at boot. The E-stop cuts power to the fill and dump solenoids.

### Safety: every pressure zone has its own relief, including each chamber

- **The problem:** each chamber is sealed behind its check valve and the QEV
  diaphragm. The manifold relief and the manifold bleed can't reach it.
- **Heat:** a chamber charged to 150 PSIG and left in the sun reaches about
  170 PSIG.
- **Fix:** replace each chamber's end cap with a 2"×1/4" bushing. Tee off it
  to a 150 PSI relief (Conrader AS250150, $6.95), a bleed ball valve ($5.29)
  and a gauge ($5.95).
- **Zones:**
  - Tank: AS250165 relief + 120/150 switch.
  - Manifold: AS250150 relief.
  - Each chamber: AS250150 relief + bleed valve + gauge.
- **Fittings:** Class 150 malleable fittings are rated 300 PSI only up to
  150°F, so keep the chambers shaded.

### Pressure switch: proposal, Micah decides

- **Primary:** the ESP32 runs the compressor relay off the tank transducer.
  That allows a quiet mode, such as holding the pump during announcements.
- **Backstop:** a FridayParts VXA7150L 120/150 PSI switch ($23.09, 1/4" NPT),
  wired in series with the relay coil.
- **Last line:** the 165 PSI tank relief.
- Three independent layers, and no regulator needed.

### Valves: HornBlasters VA-4 for fill and dump (one SKU)

- **The part:** $34.99, 1/4" NPT female on both ports, 210 PSI, 2.5 mm
  orifice.
- **Dump valve:** it threads directly onto the QEV inlet tee. The smallest
  dump volume gives the fastest QEV.
- **Rejected:**
  - Vixen VXA7164: now $19.08, and it is a horn-mount valve with a 1/8"
    compression inlet.
  - HornBlasters VA-4S-W: thread standard not stated (its SMC part number
    lacks the "N" for NPT).
- **No $22 option:** no direct-acting valve rated ≥200 PSI exists at the
  planned $22.
- **Fill fallback if the VA-4 meters poorly:** Aignep 02F 2/2 direct-acting,
  1/4" NPTF, $62.04.

### Plumbing

- **High side:** tank → fill valve is hard-plumbed in brass.
- **Nylon tubing:** only on the manifold/chamber side. SAE J844 nylon is rated
  150 PSI working and weakens in heat.
- **Fittings (flagged; Micah can veto):** DOT push-to-connect (Boeray, 250 PSI)
  instead of the settled brass compression. Same ~$2 per piece, and the
  compression listing doesn't confirm that nylon-tube inserts are included.

### Sensors

The settled ranges are confirmed in stock:

- 0–300 PSI transducer, 1/8"-27 NPT, $15.58.
- 0–200 PSI transducer, 1/8"-27 NPT, $15.20.
- ADS1115: Adafruit 1085, $14.95.

### Electronics

- **ESP32 variant (proposed):** ESP32-S3-DevKitC-1-N8R8, for native USB.
- **Relays:** 40 A automotive relays drive the compressor and the horn-valve
  coils.
- **Coil driver:** a ULN2803A ($3.84) drives the relay coils, replacing the
  $12 driver board.

### Other line changes

- **Second tank:** moved from Tier B to Tier C. The old $45, 150 PSI tank isn't
  allowed under a 165 PSI relief; a legal one costs $99.99. The three charged
  chambers already give a three-shot burst.
- **Fog line:** now an XLR plug plus relay, matching the settled "use Micah's
  existing fog machine".
- **FRC stash pneumatics:** Clippard tanks, Nason switches, 125 PSI reliefs and
  FRC tubing are rated ~120–125 PSI. Never put them on the 150 PSI side.

### Budget: A+B is $282.56 over the ceiling; proposed cuts

These are not applied in the sheet yet; each needs Micah's OK or a bench test.

1. **$7 horn valves:** QWORK CA7109 2-pack ($14.35, 200 PSI, normally closed)
   for the fill valve and all three dumps, instead of four VA-4s. **−$111.26.**
   Bench-test that they meter and dump well first.
2. **FRC stash wire and aluminum:** use stash wire, lugs and heat shrink ($70)
   and aluminum offcuts ($65) before buying. **Up to −$135.**
3. **Print instead of buy:** plain-bearing printed mecanum rollers
   (−$36 in 608 bearings), plus printed tank saddles, valve/gauge panel and
   brackets against the $60 hardware allowance. **About −$66.**

Cuts 1–3 together bring A+B to about $1,970.

## 2026-11-02 - Glacis full design (proposed, waiting on Micah)

Micah asked for the Glacis concept designed in full. The model is in `cad/glacis/` and in Onshape as
"Brophy Mark 5 - Glacis". The parts list is the "Glacis BOM" tab ($2,102.30 with owned items at $0).
Every call is listed with its reason in `docs/glacis/JUDGMENTS.md`. The ones that touch earlier
decisions:

- **QEV:** Humphrey QE5 3/4 NPT ($51.75, rated 150 psi) instead of the proposed Parker 0R75B
  ($101-125). It has the same port layout.
- **Chambers:** a 4 in malleable stack (~1.0 L, $130.10 each) running sideways from the QEV's side
  port, instead of the 2 in x 18 in nipple. A long chamber doesn't fit inside 28 in.
- **Per-chamber safety:** the relief, bleed and muffler sit in each barrel's inlet pocket, between the
  check valve and the QEV, not on a chamber tee.
- **Tanks:** Micah's two AliExpress 1.6 gal / 200 psi tanks, not the Viair 91028. No onboard pump yet;
  a spot is reserved behind the pivot.
- **Drive:** Falcons on a 40:1 two-stage HTD belt, not the stash CIMs. Micah specified Falcons for
  Glacis.
- **Elevation:** two FEETECH STS3215 bus servos replace the linear actuator and the AS5600.

## 2026-11-02 - Glacis rev B (proposed, waiting on Micah)

Micah's second round of notes reshaped Glacis. Model, Onshape tabs and the "Glacis BOM" tab are all
rev B now ($1,555.11 to buy; aluminum, acrylic, prints, Falcons and FRC stash parts at $0). Every call
is in `docs/glacis/JUDGMENTS.md`. The ones that change earlier decisions:

- **Two barrels, not three.** Clear polycarbonate 3 in x 1/8 wall barrels (McMaster 8585K38).
- **Chambers:** 4 x 3/4 bushing straight into a 4 in cap (~0.4 L), still sideways off the QE5. PVC is
  out (OSHA: shatters under air pressure); copper was not needed once the chambers got short.
- **Per-chamber safety:** a 5-port brass block per barrel carries the dump, supply, 150 psi relief
  (its pull ring is the manual bleed) and a transducer. Check valves moved to the fixed fill cross.
- **Every pressure goes to the controller** (tank, fill line, both chambers); no dial gauges.
- **Controls:** STM32 Nucleo-F446RE is the main controller; an ESP32-S3 is only the WiFi bridge. An
  independent ESP32-S3 safety node and a handheld ESP32-S3 remote talk over ESP-NOW; the node holds the
  valve-rail relay and the PWM gate, with the robot E-stop in series.
- **Drive:** one-stage 10:1 belt into a 10 in printed hub, 1/2 hex live axles in FRC hex bearings.
- **Elevation:** goBILDA 5203 on a Spark MAX with a pot, replacing the STS3215 servos.
- **Power:** REV PDH replaces the fuse block; batteries on a sled behind a removable side panel.

## 2026-11-02 - Glacis rev C (proposed, waiting on Micah)

Micah's third round of notes reshaped the gun and reused the old cannon's pneumatics. Model, Onshape
tabs ("Glacis rev C (whole robot)") and the "Glacis BOM" tab are all rev C now ($1,827.38 to buy).
Every call is in `docs/glacis/JUDGMENTS.md`. The ones that change earlier decisions:

- **Firing valve: the old cannon's Atlantic Valves SZW-25** (1 in NPT stainless, semi-direct, 12 V DC
  rated 0-115 psi) plus one more ($127.56), instead of a QEV. This is the CLAUDE.md dead end ("big
  direct-acting solenoid ... too slow vs a piloted QEV"); Micah asked for the old valves. A QE5 can be
  added later between the chamber and the barrel, with the SZW-25 as its pilot.
- **Chamber side: 110 psi software cap, 125 psi ASME relief** (Milton 1090-125), set by the valve's
  rating. The tanks stay at 200 psi.
- **Chambers: the old 1 gal steel ASME tank plus one more** (McMaster 9888K9 is the twin at $397.34;
  the old tank's nameplate is still unread), on the back of each cannon in line. The gun is balanced on
  a 1/2 hex axle that runs between the two cannons.
- **Fog: a 12 V automotive EVAP smoke machine** (AutoLine Pro HyperSmoke, $47.99) on STM32 MOSFETs,
  with printed ducts to the gun mantlet and under the front bumper. This replaces the XLR-remote stage
  fogger plan.
- **Layout:** both tanks lie along the sides (the back tank moved to the right), and there is no pump
  spot. The electronics, rear manifold, E-stop, fill, bleed and SB50 charge port are all at the back
  bottom.
- **Body:** 60 deg front, more lean on the sides and back. The LED strips run in a channel through every
  frame member, backlighting the panels.
