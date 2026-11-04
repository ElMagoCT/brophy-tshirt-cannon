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

## 2026-11-02 - Glacis rev C.1: pipe chambers, barrels together (proposed, waiting on Micah)

- **Chambers: 2 in Sch 40 x 8 in nipple between two 2 x 1 malleable reducing couplings (0.53 L)**,
  instead of the old 1 gal tank plus a $397 McMaster twin.
  - A shot simulation (`cad/glacis/shot_model.py`) shows the slow SZW-25 limits the shot: 0.53 L gives
    78% of the 1 gal's exit speed and about 20 shots per charge instead of 4.
  - Longer nipples were modelled. They swing the chambers low enough at the back to open the rear face
    down through its controls.
  - A pair costs about $82 in pipe.
  - The old grey tank is a spare.
- **Barrels 3.8 mm apart** (80 mm between axes, was 164). The breech adapter is now a spigot the barrel
  slips over, and one printed breech block clamps both barrels.
- **Pivot on two hex stubs**, one per cradle plate. The axis still runs between the cannons, but there's
  no room for a through-shaft between the chambers' couplings.
- **Chamber fittings move to a 5-port block on the back of each chamber**, so nothing is drilled.
- **Smoke: a custom 12 V fogger with two 200 W cast fog heater cores** (pumps, thermocouples, 250 C
  cutouts, a relay per core, a blower) replaces the EVAP smoker, which makes too little smoke for trails.
  - Each barrel gets six 5 mm holes just past the shirt, under a printed smoke collar, so smoke fills the
    barrel and spills out before a shot.
  - Trail vents go under the front bumper and low in the rear panel.
- **Merged with the rev C wheel branch** (glacis-wheel-c, 9ded015) into one update: Onshape version
  "Glacis rev C.1" and the Glacis BOM tab at $1,707.39.
## 2026-11-02 - Glacis rev C wheels: vector style on 608s (proposed, waiting on Micah)

Micah sent a small 3D-printed vector wheel (TTB-0010) and asked for the same style, much larger and able
to carry a lot of weight: aluminum-reinforced but with flat parts, 608 2RS bearings and M8 threaded rod,
the biggest hub the bed takes, and an integrated 15 mm HTD 5M pulley 1.25 in off the floor. Details are in
`docs/glacis/JUDGMENTS.md` (Wheels).

- **10 rollers, 42 mm x 104 mm** (was 14 at 30 mm), each on two 608 2RS turning on a fixed M8 rod held
  by a captured nyloc in the outboard cup. Barrel profile kept (not the TTB's straight cylinders).
- **Hub in two PETG-CF halves, 242 mm across**, split at the roller centre plane; the inboard half
  carries a **116T** pulley (flange 1.27 in off the floor). Ratio 9.67:1 (was 10:1).
- **Three flat 1/8 in aluminum plates per wheel** on 8 x 1/4-20 through-bolts.
- **Wheels are 120 mm wide (was 94)**: the inner rails and Falcons moved 26.5 mm inboard; the
  electronics shelf, fill block and tank lines were refit around them.
- Parts list +$60.85, now $1,888.23. Wheels +0.9 kg each.

## 2026-11-03 - Glacis rev C.2: in valves, LED loops and glowing frame, chamfered clips, corner speakers (proposed, waiting on Micah)

Micah's notes on the rev C.1 diagrams and follow-ups in the same session. Details in `docs/glacis/JUDGMENTS.md`.

- **Air:** drop the check valves and go from the tanks to each chamber through a valve that opens and closes
  on the target pressure, with no bleed valve, keeping the valve between the tanks and the firing system.
  - Built as main valve (kept) -> brass cross -> one Aignep 02F in valve per chamber, each metering against
    its own chamber sensor.
  - The check valves, fill block, fill sensor (PT2), its 125 relief and the rear ball-valve bleed are gone.
  - Sensors are now PT1 tank, PT2 top chamber, PT3 bottom chamber.
  - **Kept against the circle:** a 200 psi relief on the cross, because the brass between the main valve and
    the in valves is its own pressure zone (hardware relief on every zone). The hand dump is the relief pull
    rings; the tank relief now points out through the rear panel.
  - **Fill order:** close the in valve before the main valve, so tank pressure holds the in valves' seats
    shut.
- **Panel light:** Micah first asked for LEDs pointing along the panels, then for a 60/m loop 1-1.5 in behind
  each panel at a slight angle toward it, one complete loop per panel so light doesn't leak between panels,
  with a spot on the bottom.
  - Each window gets a printed rail on a flange, leaning 15 deg toward the panel. A 10 mm 60/m strip on it
    sits 1.15 in behind the acrylic, 42 mm in from edges shared with another panel (so neighbours' strips
    don't cross at the 91-100 deg corners) and 29 mm in from open edges.
  - To make room for the loops and the speaker notches: batteries (and their SB50s) 15 mm inboard, side
    tanks 6 mm inboard and 20 mm back, elevation motor 22 mm lower, smoke box 10 mm back, the pot
    bracket's top lower, the rear smoke tube raised, and the rear manifold 5 mm lower with its transducer underneath.
- **Frame light:** a centred rectangular tunnel down every member, missing the screws, so the frame glows.
  - It's 6 x 2.6 mm, 100/m 5 mm strip, 2.5 mm outward of the tenons, which moved deeper (18.5 mm).
  - Feed slots from the inside at each node.
- **Corner clips:** chamfered instead of round and twice the size (27 mm legs).
- **Speakers:** loud enough for a crowd, replacing the horn, two a side at the top and bottom of the front
  corners. Top: 45 deg out, 30 up. Bottom: 22.5 out, 15 up. Chamfer the panels to fit, with a printed mesh
  grille (3 walls, no top/bottom, 12% gyroid).
  - Built with two UBL 100W Slim siren speakers (11 ohm, 120-130 dB, 2 in deep), one high in each corner, in
    printed cups in notches cut into the body shape.
  - Driven by an I2S DAC from the ESP32-S3 bridge and one TPA3116D2 on a 24 V boost.
  - **The bottom pair doesn't fit** with 6 in speakers: the side panels pinch in two, the cups hit the front
    wheels, or the grilles push the width past 28 in. Micah allowed two ("if you go for 4"); a 4 in speaker
    would fit the bottom.
  - The old list's 20-30 W PA horn and TDA7297 are dropped.
- **Barrels 8 mm apart** (was 3.8), Micah's call; the gun rebalances on the pivot by itself.
- **Strip sourcing:** Micah prefers Amazon or AliExpress for LEDs. The 5 mm strip is AliExpress
  ($15.79 per 5 m at 100/m) and the 10 mm loop strip is BTF-LIGHTING on Amazon.
- Frame: 89 printed pieces, 101 tenons, 40 clips, 2 door latches. Parts list $1,512.44 after the savings. Onshape version
  "Glacis rev C.2".
- **Savings (Micah's picks from a list of 20, same pressure and air capacity):**
  - U.S. Solid USS2-01023 for the second firing valve (0.8 MPa = 116 psi, above the 110 cap).
  - STM32F411 Black Pill instead of the Nucleo; his own two ESP32-S3s; his own goBILDA 5203; Loctite owned.
  - Brass crosses instead of the 5-port chamber blocks; printed chamber caps instead of cam straps.
  - Dollar-store noodles; heavy-duty 12 oz canvas; a 5 A boost module; Zoro M8 rod; 25 ft of DOT tube.
  - Remote: an ESP32-S3 Super Mini with the E-stop and a link LED; the dead-man trigger and screen are gone.
  - One fog core now, room left for a second. Two battery spots kept (live swap). The battery doors latch
    at the top. Wheel plates get 6 more lightening holes; the frame prints at 15% infill.
  - Not changed: 1/4 NPT transducers (FUSCH 200 psi is 1/8 NPT only); HornBlasters VA-4 in valves (no
    cheaper than the Aignep, and not confirmed direct-acting); the VA-4 can't be a firing valve (Cv about
    0.15 against 12).

## 2026-11-03 - Glacis rev C.3 body + rev D.1 gun, modelled (proposed, waiting on Micah)
- Body (Micah's notes): acrylic ledge halved to 7 mm (19 mm members); rounded windows, acrylic and clips; M4 heat-set
  inserts for every panel screw (no M3); front panel cut at the gun-well floor with one printed cheek each side;
  speakers 13 mm deeper; LED corners 22.5 mm and square to the panel, lean only on straight runs; 42 mm stays on
  shared edges (any less puts the neighbour's rail behind the acrylic), 19 mm on edges without a neighbour; battery
  doors split at x -105 so a battery clears the rails.
- Added: 45 deg underglow brackets under the bumpers; two 3 W hood lights at the low front corners.
- Gun (rev D.1 from the electronics/air session): 3 in chambers (12 in on the HSV04, 10 in on the SZW-25), barrels
  112 mm apart and 36 in long, pivot raised to z 645, elevation capped at 45 deg (60 hit the rear bay). One-piece
  smoke collar, muzzle ring and mantlet; fill and smoke lines run inside the core and out the bottom behind the
  pivot; 312 rpm elevation motor at 7:1; rear smoke vents down through the bellypan.
- A third 6 L tank doesn't fit with the two side tanks (see JUDGMENTS M8). Two tanks, 12 L.
- Onshape: one sub-assembly per system; every pneumatic part detailed and described. Parts $1,888.37.

## 2026-11-04 - Glacis rev D.1.1: LEDs, light bar, cost-down

- LED loops at 2/3 radii, with rounded rail edges. Rails back to back on shared edges. Strip 0.96 in behind the panel.
  8 jumpers where loops cross at three-panel corners.
- Micah's Zmoon 12 in light bar across the nose, switched and dimmed by the STM32 through a MOSFET. The hood lights
  and the lens-pod bars are out.
- EVIL ENERGY 2.5 gal tanks: two don't fit (sides blocked by the batteries), and one can only replace both 6 L tanks
  for less air. Keep the two 6 L (JUDGMENTS N3).
- Parts: cheapest of AliExpress (Micah's logged-in prices), Amazon and McMaster. No rivets, old 9 in mecanum for now,
  goBILDA motors owned. $1,888.37 -> $1,359.91. Onshape version "Glacis rev D.1.1".

## 2026-11-04 - Glacis rev D.1.2: LED band = window wall

- Micah: the D.1.1 rails overlapped. The window wall now runs from the acrylic ledge straight back to the strip
  (25 mm behind the acrylic, 10 deg lean), with no rail or flange.
- Shared edges set by the corner bisector (31-36 mm), so neighbours' strips meet back to back with no overlap.
- Frame 4.44 -> 5.64 L. Clip inserts kept inside slanted faces. Onshape version "Glacis rev D.1.2".

## 2026-11-04 - Glacis rev D.1.3: chamfered window wall, filled LED corners

- Micah: chamfer the thick edge from the 7 mm ledge right to the LED; fill the gap between the close LED corners;
  model the interior (frame tunnel) strips so they bend well.
- Wall: ledge, straight chamfer, LED band. Shared corners are solid V ridges, with their 24 joints glued (no screw
  access). Frame strips are continuous, with easy-way bends into the feed slots (straight ends on 6 short slots).
- Frame 5.17 L. 0 contacts.
