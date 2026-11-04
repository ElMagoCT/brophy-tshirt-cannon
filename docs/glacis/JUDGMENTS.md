# Glacis rev C.2: judgment calls

Rev C (2026-11-02), C.1 and C.2 (2026-11-03) are the redesign from your third to fifth rounds of notes:
- both chambers on the back of their cannons, in line, with the barrels as close together as they go
  (8 mm apart, rev C.2);
- the gun balanced on a pivot axis that runs between the two cannons;
- the old cannon's firing valve, plus a U.S. Solid one (your savings pick);
- small, cheap 2 in pipe chambers (0.53 L), sized by a shot simulation;
- the back tank moved to the right, and no room left for a pump;
- a 60 deg front, with the sides and back leaning more, and the open middle kept;
- the rear-panel controls at the bottom of the panel, and the electronics in the back bottom;
- a 60 rpm pivot motor;
- a custom 12 V fogger: smoke into both barrels ahead of the shirt, plus trail vents front and back;
- no check valves or fill block: a main valve, then one in valve per chamber, each metering its own chamber;
- an LED loop on a leaning rail 1.15 in behind each panel, aimed across it, and a 100/m strip pushed
  through a tunnel in every frame member, so the frame glows; corner clips chamfered and twice the size;
- two slim 100 W siren speakers high in the front-side corners (horn replacement), with their amp;
- the vector-style wheels from your TTB file.

Each item says what I picked and why. Numbers come from `cad/glacis/params.py` and the last clean run
(`cad/glacis/out/check_log.txt`).

**Checks on the final model:**
- no part overlaps another;
- nothing hits anything as the gun sweeps 0-90 deg, checked every 5 deg;
- every printed part fits a 256 mm bed;
- every part is a single solid.

**Where it is:** Onshape "Brophy Mark 5 - Glacis", saved as version "Glacis rev C.2"; the assembly is
"Glacis rev C (whole robot)". The parts list is the "Glacis BOM" tab: **$1,512.44** to buy (rev C.1 was
$1,707.39, rev B $1,555.11). Aluminum, acrylic, prints, Falcons, FRC stash parts and the old cannon's valve are all at $0.
The pneumatic and electrical diagrams are in the "Glacis air & wiring" artifact
(source `docs/glacis/air_wiring_artifact.html`).

## What I identified on the old cannon
1. **Firing valve: Atlantic Valves SZW-25.** The plate says SZW-25, not S2W.
   - It's a 1 in NPT stainless solenoid valve, normally closed, with a Viton seal.
   - It's semi-direct acting, with a 25 mm orifice and Cv 12. The 12 V DC coil is 16 W.
   - Rated **0-115 psi on the 12 V DC coil** (0-145 on the AC coils).
   - It's sold at electricsolenoidvalves.com, not Amazon: SZW-25-12VDC, **$127.56**, 29 in stock
     ([page](https://www.electricsolenoidvalves.com/1-inch-12-volt-dc-stainless-steel-electric-solenoid-valve/),
     [spec sheet](https://www.electricsolenoidvalves.com/content/Atlantic_Valves_SZW_Spec_Sheet.pdf)).
   - The old one is reused on the top cannon.
   - **The bottom cannon gets a U.S. Solid USS2-01023**, $59.80
     ([B0CXWR76GT](https://www.amazon.com/dp/B0CXWR76GT)): the same 1 in NPT 12 V DC size, rated 0.8 MPa
     (116 psi), which you read off the listing. That's just above the 110 psi cap, and $68 less.
   - **Check the old valve's coil label.** It has to be the 12 V DC one.
2. **Old chamber: a grey primed-steel ASME air tank with a 1 in NPT end port**, probably 1 gal. It's no
   longer used; see item 6 for the new chambers.
   - Its buyable twin was McMaster 9888K9 at $397.34
     ([link](https://www.mcmaster.com/9888K9/)), which is what pushed me to look for something better.
3. **Longacre 5 gal polished aluminum tank:** rated 125 psi
   ([52-50305](https://toolsid.com/longacre/5-gal-horizontal-silver-lightweight-air-tank-mpn-52-50305.html)).
   It can't go on the 200 psi tank side, so it's a spare.
4. **The screw-set regulator is gone.** Each chamber's in valve meters air into it against that
   chamber's transducer, so each cannon's pressure is set in software.
5. **Red "5 in ONE Universal" couplers:** brand and rating not confirmed, so they stay off the pressure
   side.

## Gun
6. **Chamber size, from a shot simulation.** I modelled a shot: the chamber, the valve opening over its
   real time (Cv 12), the air behind the shirt and the shirt itself (250 g with friction). Then I ran it
   against chamber size at 110 psi
   (`cad/glacis/shot_model.py`; numbers below are for a 50 ms valve opening):

   | Chamber | Exit speed | Shots per charge |
   |---|---|---|
   | **0.53 L (2 in x 8 in, picked)** | **22.7 m/s** | **about 20** |
   | 0.64 L (2 in x 10 in) | 24.0 m/s | about 17 |
   | 0.75 L (2 in x 12 in) | 24.9 m/s | about 15 |
   | 1.25 L | 27.0 m/s | about 9 |
   | 3.8 L (1 gal) | 29.0 m/s | about 4 |

   - With this slow a valve, the valve sets the shot, not the chamber. The 1 gal tank gives 28% more speed
     than 0.53 L, and you get a fifth of the shots.
   - The 10 in and 12 in nipples were modelled too. They swing the chambers low enough at the back to
     open the rear face down through the fill port, tank relief and charge port. The 8 in keeps the
     rear controls where you asked for them.
   - If the valve opened in 10 ms like a QEV, the same chamber would give about 38 m/s. That's the case
     for adding a QE5 later (item 9).
7. **Chamber: 2 in Sch 40 x 8 in steel nipple between two 2 x 1 malleable reducing couplings, about
   0.53 L.**
   - About $41 per chamber in pipe ($15 nipple and two $13 couplings), against $397 for the McMaster
     twin of the old tank.
   - The couplings are UL/FM listed, 150 lb class and factory pressure tested; the pipe is rated well over
     1,000 psi. Everything sits behind the 125 psi relief.
   - At 3 in across the couplings, the chambers are no wider than the barrels, which is what lets the
     barrels sit close.
8. **Two cannons stacked 8 mm apart** (84.2 mm between axes; rev C.1 had 3.8, you asked for 8).
   - Each one, back to front:
     1. port block;
     2. 1 x 1/4 bushing;
     3. reducing coupling;
     4. 2 in nipple;
     5. reducing coupling;
     6. 1 in close nipple;
     7. SZW-25;
     8. 1 in close nipple;
     9. CNC breech adapter;
     10. polycarbonate barrel.
   - The breech adapter is stash 6061 with a 1 in NPT tap ($16.99 on the list). The barrel slips over its
     spigot, so it's no wider than the barrel.
   - One printed breech block in two halves clamps both barrels onto their spigots. The muzzle collar is
     two halves meeting between the barrels.
   - **Balanced on the pivot.** The model finds the gun's centre of mass and slides both cannons along the
     barrel axis until it lands on the pivot axis. Valves end up 71 mm ahead of the axis, centre of mass
     within 0.3 mm, gun 11.4 kg: **0 N*m to hold at any angle.**
   - The valve (1.0 kg) and coupling (0.31 kg) masses are estimates; the pipe is computed. Weigh yours,
     update `gun.py`, and re-run before cutting the cradle plates.
9. **Pressures and the valve trade-off.**
   - 110 psi software cap on the chambers, just under the valve's 115 psi DC rating. Above that, the coil
     may not lift the valve; it fails closed, not open.
   - **Milton 1090-125** ASME reliefs ($16.87) go on each chamber. Their pull ring is the manual bleed.
     125 psi is above the cap, so they never simmer, and under the tanks' and transducers' 200. This replaces the settled "150 psi chambers" for this valve.
   - CLAUDE.md lists "big direct-acting solenoid as the firing valve: too slow vs a piloted QEV" as a dead
     end. The SZW-25 is semi-direct, so it's slower. It's in because you asked for the old valves and it
     worked on the old cannon.
   - The simulation says a QE5 QEV ($51.75) between the chamber and the barrel, with the SZW-25 as its
     pilot, would be the biggest single gain if you want more range later.
10. **Air budget:** each 0.53 L refill takes about 5 psi out of the two 6 L tanks, so a 200 psi charge
    gives **about 20 full-power shots** (2 loaded plus about 18 refills). Lower settings give more.
11. **Chamber fittings: a 1/4 NPT brass cross on the back of each chamber**, so nothing is drilled. Its
    four ports are exactly what's needed, so the 5-port block and its plug are gone (-$23, lighter gun):
    - in from the chamber's bushing;
    - fill push-to-connect straight out the back;
    - 125 psi relief pointing outward;
    - 0-200 psi transducer to the side.
12. **No check valves: a main valve, then one in valve per chamber** (your call, rev C.2).
    - The checks were only there because one fill valve fed both chambers through a shared block, so
      firing one would have drained the other back through it. With a valve per chamber, a closed in
      valve seals its chamber, so the checks and the fill block (with its sensor and relief) are gone.
    - **Main valve** (kept, as you asked): the tanks' shut-off. It opens only while a chamber fills, and
      it's on the safety-powered valve rail, so a trip closes it. *Rev C.3: now a manual ball valve (E2).*
    - **In valves A and B:** each pulses until its chamber's sensor reads that cannon's own setpoint
      (110 psi max). All three are the same Aignep 02F direct-acting 12 V valve ($41.36, 507 psi rated).
      Direct-acting means they open from 0 psi and don't need a pressure difference to work.
    - **Fill order:** open the main valve, meter the in valve, close the in valve, then the main valve.
      That leaves tank pressure on the in valves' inlet side, which pushes their seats shut. A solenoid
      valve isn't rated to hold pressure backwards, so the firmware never vents that line.
    - **No bleed valve.** The manual tank bleed is gone. To dump by hand, pull the relief rings:
      - the tank relief, which now points out through the rear panel where the bleed lever was;
      - the 200 psi relief on the valve cross;
      - the 125 psi relief on each chamber.
      With power, the firmware can empty the chambers by firing them.
    - **One relief I kept that you circled:** the brass between the main valve and the in valves holds
      tank pressure when both are shut, so it's its own pressure zone. The project rule is a hardware
      relief on every zone, so the cross carries a 200 psi relief ($16.30) instead of the fill block's
      125.
    - Air side: -$15.60 (checks, fill block, fill sensor, 125 relief and ball valve out; two in valves
      and a 200 relief in). Two more MOSFET channels, from the spares.
    - Two nylon service loops run from the in valves up to the gun and flex as it elevates. The sweep
      check skips them; give them slack when you route them.
13. **Firing valves switch on MOSFET modules, not relays,** to take the relay's ms off the shot. Add a
    flyback diode on each coil.
14. **Cradle:**
    - two 1/8 aluminum plates either side of the stack;
    - printed chamber saddles (one block between both pipes at each station), each pipe's outer half
      held by a printed cap with two M5 screws into the saddle (they replace the cam straps);
    - valve side blocks and the two-piece breech block;
    - a printed mantlet carrying the smoke vents beside the barrels and an LED groove;
    - a two-piece LED-groove muzzle collar.

## Elevation
15. **The 60 rpm motor is the goBILDA 5203 99.5:1.** It drives a 16T -> 56T HTD 9 mm belt (100T) to
    the right pivot stub.
    - That's about 17 rpm at the gun, so 0-90 deg takes about 0.9 s at full speed.
    - The gun is balanced, so the motor only fights friction and inertia. It has 46 N*m stall at the
      pivot.
16. **Two 1/2 hex steel stubs carry the pivot**, one per cradle plate, each through a printed hub
    bolted to the plate's outside face. The pivot axis still runs between the two cannons.
    - With the barrels 8 mm apart, there's no room for a shaft between the chambers' couplings.
    - The stubs sit in four flanged hex bearings, in two PA-CF blocks on 1x1 towers on the inner rails.
    - The pulley is on the right stub; the arm-angle pot is on the left stub through a printed coupler.
    - The two plates are tied together by the saddles, valve blocks, breech block and mantlet.
17. **The gun well follows the gun.** The model sweeps the gun 0-90 deg and cuts the well floor to that
    envelope plus 10 mm, so the body stays as closed as it can.
    - The floor is 437 mm high at the front, 388 at the back and 232 under the axle.
    - The well is 224 mm wide; the elevation pulley turns inside it.

## Body
18. **Front slant 60 deg** (was 70), the back leans 80 deg, and the sides lean in 8 deg (was 6). The deck
    is flat at 24.8 in.
19. **Size:**
    - 37.7 x 27.7 in over the bumpers.
    - With the gun level, the muzzles reach 44.9 in overall and the chambers stand 31.2 in tall.
    - At 90 deg it is 37.8 L x 50.1 H.
    - To get through a 40 in door, drive with the gun raised.
20. **9 panels.** Both side walls split at the battery bay; their rear panels are the battery doors.
21. **Each panel has its own LED loop, 1.15 in behind it, aimed across it** (rev C.2, your second note).
    - A printed rail hangs inside every window from a flange on the frame's inner face, leaning 15 deg
      toward the panel. A 10 mm 60/m strip sticks to its panel side, centred 35 mm behind the outer face
      (1.15 in behind the acrylic). The LEDs shine across the back of the panel and slightly at it.
    - The rail runs all the way round each window, so every panel is one closed loop and can be its own
      colour. The rail's back shades the next panel, so the light doesn't leak across.
    - **How far in:**
      - **42 mm from an edge shared with another panel.** Every corner on this body is 91-100 deg, and at
        any less the two panels' strips cross along the whole edge.
      - **29 mm from an open edge** (the bottom, the gun slot, the speaker notches), so the bottom runs
        sit low.
      - The rail corners round off at up to 45 mm.
    - **The bottom runs fit.** I moved parts out of the loops' way:
      - the batteries 15 mm inboard, and their SB50 plugs with them;
      - the side tanks 6 mm inboard and 20 mm back;
      - the elevation motor 22 mm lower, round its belt circle (same belt);
      - the pot bracket's top 20 mm lower;
      - the rear smoke tube up 15 mm, and the smoke box 10 mm back;
      - the rear manifold 5 mm lower, with its tank transducer pointing down from its underside.
      The rear panel's bottom run passes under the E-stop, charge port and smoke nozzle.
    - 12.1 m of strip, so three 5 m rolls (BTF-LIGHTING, Amazon, $13.99).
22. **The frame glows too: a strip tunnel through every member.**
    - A 6 x 2.6 mm rectangular tunnel runs down the middle of each member, so a 5 mm strip can't twist
      and its LEDs face out. That's 100 LED/m (5 mm, 2020 LEDs, AliExpress, $15.79 per 5 m). Print the
      frame in natural or white PETG.
    - It's centred across the member and stacked over the joint line: the tenons moved deeper (18.5 mm,
      was 15), and the tunnel sits 2.5 mm outward of them, so the M4 cross screws stop 2.75 mm short of it.
    - On the bottom edges, where the face meets the open bottom at a sharp angle (60 deg at the nose),
      the tenon and tunnel move in from the edge until they keep 2 mm of wall.
    - **Feed slots:** at each end of each member, a slot opens from the inside down to the tunnel. Push
      the strip in from one slot to the next; at the nodes, solder or plug the next member's strip in the
      slot. The slots stay 9.5 mm under every outer face and out of every joint.
    - 9.5 m in the tunnels. With the loops that's about 1,680 LEDs, so cap them at about 20% white on
      the 20 A buck.
    - Print the frame in natural PETG at 15% gyroid with 4 walls (your savings pick): lighter, and the
      glow comes out more even than at 25%.
    - **Frame:** 89 printed pieces, 101 tapered tenons with M4 cross screws, 40 corner clips and 2
      door latches. Short edges round the speaker notches set back less so they still get a
      segment, and the few nodes that still came out bigger than the bed are halved and glued.
    - Strips, rails and loops are in the model (red), so they show in Onshape.
23. **Corner clips: chamfered, twice the size.** Each is a corner plate with a straight chamfer across
    the panel corner instead of a round edge, legs 27 mm along the frame (rev C.1's discs reached about
    14). One M3 into a heat-set insert, 8 mm in from both edges.

## Speakers (rev C.2)
24. **Two slim 100 W siren speakers, one high in each front-side corner.** Your old list had a 20-30 W PA
    horn; that's quieter than a car horn at a parade. Siren speakers are built to replace a horn.
    - **UBL 100W Slim:** 11 ohm, 120-130 dB at 100 W, 400-4,000 Hz, 5.5 x 5.75 x 2 in, $79.99. Being 2 in
      deep is what lets them sit in the corners; the 5-6 in PA horns are 6-8 in deep.
    - Horn tones and voice sound right; music has no bass at 400 Hz up.
25. **Aim, as you asked for the top ones:** 45 deg out from straight and 30 deg up. Each sits 90 mm down the
    front-side corner from the top and seats 55 mm in from the corner edge.
    - **I didn't fit the bottom pair** (22.5 out, 15 up). The lower corner has the front wheel under it
      and the side tank behind it, and a 6 in speaker per notch leaves too little panel between two
      notches. Everywhere I tried, one of these broke:
      - the side panels pinched into two pieces;
      - the cups hit the front wheels;
      - the grilles pushed the robot to 28.8 in wide, past your 28 in door.
    - Two at about 26 W each is roughly car-horn loud at 1 m. If you want the bottom pair, a speaker
      about 4 in across would fit. Your call.
26. **Integration:** each speaker sits in a square notch cut into the corner. The body shape itself is
    notched, so the front and side panels, the frame, the LED rails and the loops all follow the notch.
    - A printed cup lines the notch and carries the speaker on 4 x M4 through its floor; a wire hole goes
      through the floor.
    - A printed grille covers the speaker face: 3 walls, no top or bottom layers, 12% gyroid, so it prints
      as an open mesh. Glue it or screw it to the cup.
    - The grille's top corner stands 4 mm above the deck.
27. **Driver:** the ESP32-S3 WiFi bridge streams sound from the web UI over I2S to a PCM5102A DAC. One
    TPA3116D2 board ($13.98) drives both speakers, one channel each.
    - It runs from a 12 -> 24 V 10 A boost converter ($39.99) on a PDH channel. On 24 V it puts about
      26 W into 11 ohm; on 12 V it's about 6 W, 6 dB quieter. Skip the boost if that's loud enough.
    - The amp and the boost sit on the middle of the bellypan, under the gun's swing.
    - Audio adds $199: two speakers $160, amp $14, boost $18, DAC $7.

## Layout
28. **The back tank moved to the right.** I read that as mirroring the left one, so both tanks lie along
    the sides over the front wheels, on cantilevered 1x1 arms with printed saddles and straps. No pump
    spot.
29. **Bottom of the rear panel:**
    - E-stop;
    - fill port (air in; rev C.3: an M-style plug with a check valve behind it, P3);
    - the tank relief's pull ring (the hand dump; there's no bleed valve);
    - SB50 charge port, to run or charge on standby power with the batteries in;
    - USB-C to the STM32.
30. **Rear manifold** (back bottom, left): tank lines, 0-300 psi transducer (pointing down underneath),
    and the line to the main valve. The fill port and the 200 psi relief go straight out through the rear panel.
31. **Electronics in the back bottom bay:**
    - PDH and main breaker on the bellypan;
    - STM32, both ESP32-S3s, the PWM gate, the drivers, the buck and the Spark MAX on a printed shelf;
    - the main valve, valve cross and in valves beside them (coils up).
    - Rev C.3 adds the PDH contactor and the logic supply here (E1); the main valve's handle has to reach
      the rear panel (E2).
32. **Batteries:** two spots, one per side, each on its own sled over a rear wheel, so you can swap one
    while the other runs. Each slides out through its side's rear panel.
    - **The battery doors latch at the top** (your call). Each door keeps its two bottom corner clips,
      which act as hooks, and gets a printed quarter-turn latch on an M4 screw at the middle of its top
      edge. Turn the latch, tip the door out from the top, and lift it off the hooks.

## Smoke
33. **Custom 12 V fogger with one 200 W fog heater core, and room for a second** (your savings pick), instead
    of the EVAP smoker. The tray, the heater bracket, two MOSFET channels and a PDH channel are left free,
    so the second core and its pump drop in later for twice the fog. About $55 of parts plus fluid.
    - **Why not the EVAP smoker:** it burns about 0.3 mL of oil a minute; a 400 W fogger moves 13-16 mL.
      That class can't make outdoor trails or fill two barrels.
    - **Why not a mains fogger:** a $30 400 W fogger plus a 500 W inverter draws about 40 A, puts mains
      wiring on the robot, and the inverter doesn't fit the bay
      ([BORGOVA](https://www.amazon.com/dp/B0F4XJMNFR) + [BESTEK](https://www.amazon.com/dp/B086SSRRZ7)).
    - **The core:** a cast fog-machine heat exchanger made for 12 V
      ([AliExpress, $22.42](https://www.aliexpress.us/item/3256805556610953.html)), 97 x 32 x 36 mm,
      about 17.5 A on its own 30 A PDH channel. One makes about as much fog as a 200 W mains fogger; two
      would match a 400 W one.
    - **Parts:**
      - a Kamoer 12 V peristaltic pump per core, fed from a printed 400 mL tank;
      - a MAX6675 thermocouple amp and K probe per core, read by the STM32;
      - a KSD301 250 C cutout and a 40 A relay per core;
      - a 5015 blower to push the fog into the splitter.
    - **Warm-up is 5-8 minutes** (heat on standby power before an event). Then about 40 s of continuous
      fog before a reheat.
    - The ready-made 12 V 200 W fogger on AliExpress ($58.49) uses the same class of heater, but it has one
      1-star review and no size listed.
34. **Control and safety.**
    - The STM32 holds each core at 220-240 C, with a firmware cut at 245 C. It switches the heaters
      slowly (about 1 Hz) on paired MOSFET channels, gated at 5 V through the spare 74AHCT125 buffers.
    - The pump and the blower are on their own MOSFET channels. With the firing and in valves that's
      8 channels of two 6-packs, which leaves 2 for a second core.
    - Each core's 40 A relay sits upstream of its MOSFETs. Its coil runs through the KSD301 and an STM32
      enable pin that's pulled low, so an overheated core, a shorted MOSFET or an STM32 reset all drop it.
      The KSD301 resets itself when it cools, so the firmware latches the fault.
    - Pump only within 10 C of the setpoint, with a pump timeout, and cut the heater if a thermocouple
      reads open.
    - The cores sit on an aluminum bracket with ceramic-fiber wrap, never on a print.
35. **Fluid:** water-based glycol fog fluid only. Oil (the EVAP fluid) cokes the core's 2.5 mm tube. Like
    any fogger, it can trip gym smoke detectors, so check with each venue.
36. **Ducts:** a printed outlet adapter feeds a printed 1-to-4 splitter, then your four flexible tubes.
    - **Two go to the barrels.** Each barrel has six 5 mm holes 205 mm from its breech end, just past a
      rolled shirt. A printed two-piece smoke collar clamps round both barrels over the holes. Its two
      ring grooves meet between the barrels, so one plenum feeds both.
      - Smoke fills each barrel ahead of the shirt and spills out of the muzzle. On a shot, the shirt
        pushes it out in front.
      - The holes sit ahead of the shirt, so they don't leak the shot until the shirt has passed.
      - Drill the polycarbonate slowly with a sharp bit and deburr; the clamps still never drill it.
      - These two tubes flex with elevation, like the air loops.
    - **One goes to a vent under the front bumper** (through the bellypan, front left).
    - **One goes to a nozzle low in the rear panel**, centred under the open middle. It runs along the
      bellypan, under the gun's swing and over the electronics shelf. That's the back trail.
    - Keep the ducts short and sloped so condensed fluid drains back. Check the core's tab layout and outlet
      tube when they arrive, before printing the tray and splitter.

## Wheels (from your vector-wheel file, TTB-0010)
37. **Same style as your TTB wheel, scaled to 10 in.**
    - 10 rollers, 42 mm across and 104 mm long (rev B had 14 at 30 mm).
    - A lobed hub rim with a printed cup round each roller end, like the TTB's hooked lugs.
    - One change: the rollers keep a true mecanum barrel profile instead of the TTB's straight
      cylinders. At 10 in, a straight roller rides on its corners and the wheel bumps.
    - Coverage +6%, with 5 mm between neighbouring rollers.
38. **Rollers on 608 2RS and a fixed M8 rod.**
    - PETG-CF core, 3 mm TPU 95A tread (1.8 mm at the ends), a 608 pressed 8 mm into each end.
    - The rod doesn't turn; the bearings do. It threads through a captured M8 nyloc in the outboard
      cup (Loctite 243) and bottoms in a blind hole in the inboard cup. The outboard plate covers the
      nut channels, so a rod can't back out.
    - Each cup's stub sits in the roller's end recess and presses only on the bearing's inner race.
    - Nuts, not tapped aluminum: the rods sit at 45 deg to the plates, so a flat plate can't be
      tapped square to them.
    - To change a roller: take off the outboard plate (8 nuts), unscrew the rod by a slot cut in its
      end, and the roller drops out.
39. **Hub: two halves, as big as the bed allows.**
    - Split at the roller centre plane. Each half is 242 mm across and prints face down.
    - The bed would take 250 mm, but the rim stops 6 mm inside the tread so it never touches the floor.
    - Each half is a lobed face web, a drum ring, 6 spokes and a 1/2 hex boss.
40. **Aluminum: 12 flat 1/8 in plates (waterjet), three per wheel.**
    - The inboard plate is the belt's inner flange.
    - A centre disc sits between the two halves.
    - The outboard plate is lobed, the same shape as the rim.
    - 8 x 1/4-20 x 5-1/2 in bolts clamp the stack (M6 x 130 fits the same holes). The plates' hex holes
      put the wheel load on the axle through aluminum, not plastic.
    - Each plate also has 12 lightening holes: the hub's 6, plus 6 x 16 mm between the bolts (your
      savings pick). None at 0 and 180 deg, where they'd meet the hub's holes; >= 7.7 mm of web everywhere.
41. **Pulley: 116T HTD 5M, 15 mm, printed into the inboard half.**
    - Its flange is 1.27 in off the floor. 118T would be 1.20 in.
    - 9.67:1 from the Falcon's 12T (was 10:1); free speed 28.8 ft/s.
    - The stock 140T belt still fits; the Falcons now sit 169 mm from the axle.
42. **Load.** Two 608s per roller rate 2.7 kN static. At 69 kg, a wheel carries about 170 N standing
    and about 500 N on a 3 g bump, often all on one roller: over 5x margin. The printed cups are the
    weakest link, and the plates and bolts carry their load to the axle.
43. **The cost of the width.**
    - Each wheel is 120 mm wide (rev B 94). The outer rails stay put (27.7 in over the bumpers), so
      the inner rails and Falcons moved 26.5 mm inboard: the inner rails are now 104-129 mm off centre.
    - The electronics shelf narrowed to +/-100 mm, with the boards rearranged on it.
    - The valve cross moved 25 mm inboard, clear of the rear-left wheel.
    - The tank lines now run inboard of the rail posts.
    - The pivot bearing blocks follow the rails and are now 20 mm wide (was 47); both flanged hex
      bearings still fit, and the pivot stubs are shorter to match.
44. **Weight: 3.3 kg a wheel** (rev B 2.4), so +3.6 kg for four.
45. **Cost: +$60.85.** The 608s, rod, nylocs, bolts and Loctite replace the 685ZZ and M5 lines. The
    Bolt Depot prices are from search snippets, so check stock when you order.

## Things I'd flag
46. **Cost: $1,512.44**, well inside the $2,000 ceiling.
    - By section: pressure side $425, gun $357, audio $199, drive $157, frame and body $131, controls
      $103, smoke $91, bumpers $30, elevation $19.
    - Your savings picks took off $439 (it was $1,951.55). What I didn't change, and why:
      - **#12, 1/4 NPT transducers:** FUSCH's 200 psi transducer only comes in 1/8 NPT, so the bushings
        stay.
      - **#13, HornBlasters VA-4:** it's $41.95 in stock, the same as the Aignep, and nothing says it's
        direct-acting. So the Aignep stays.
      - **The VA-4 as a firing valve:** it can't do the job. It's a 2.5 mm orifice (Cv about 0.15) against
        the 1 in valve's Cv 12, so a shot would barely leave the barrel.
      - **#10, the pipe tap:** it cuts the 1 in NPT threads inside the two aluminum breech adapters. It
        stays on the list; borrow one if the shop has it.
    - The speakers are now the biggest line (2 x $79.99).
47. **Weight is about 157 lb** (71.0 kg). The two siren speakers add about 4.8 kg (2.4 kg each, a guess from
    similar 100 W units); the gun is 11.5 kg.
48. **Check before ordering:**
    - the old valve's coil voltage (it must be the 12 V DC coil);
    - the U.S. Solid valve's coil voltage (12 V DC);
    - the Aignep coil and plug (you need 3 valves);
    - the AliExpress strip's sale price ($15.79 a roll);
    - the speakers' weight and mounting holes, and that the 4 x M4 pattern in the cups matches;
    - the fog cores' tabs and outlet tube when they arrive;
    - the AliExpress, Zoro and dollar-store prices (search snippets only).
49. **Found while checking: the battery doors are too narrow for the battery.** This goes back to rev C.
    The back leans 80 deg, so at the top of the battery the door window is about 163 mm wide, but the
    battery is 181 mm long; the LED rails take it to about 149. It slides out only if you tilt it. Fixes:
    move the door split forward about 40 mm, which runs the split's LED rail into the side tank, or lay
    the battery on its side. Your call; the new top latch doesn't change it.
50. **The Onshape model is imported STEP** (dumb solids), with the gun posed at 20 deg. To change it,
    edit `cad/glacis`, run `python robot.py`, and replace the changed tabs.

## Electronics and air review (rev C.3, 2026-11-03)
Your electronics review notes, then your pneumatics notes. Full electrical write-up: `electrical/README.md`.
Range math: `cad/glacis/range_model.py`. The parts list goes up $36.46 for all of this.

**Electronics**

E1. **The STM32 switches the whole PDH, and the logic has its own always-on circuit** (your call).
    - Main breaker -> 200 A contactor -> PDH. Ahead of the contactor, a 5 A fuse feeds a Pololu S13V30F5
      5 V buck-boost ($17.95): the logic rail for the STM32, both ESP32-S3s and every sensor.
    - Standby (contactor open) leaves the PDH dead but the STM32, sensors, web UI and remote alive, so you
      see pressures, fog fluid, temperatures and battery with the systems off. Arm from the UI.
    - Contactor: Hamolar RD-200 2-pack ($26.24, one spare), coil about 0.7 A through a spare MOSFET channel.
      The rear E-stop's second contact is in that coil, so the E-stop now kills the whole PDH in hardware;
      the first contact stays in the safety relay coil.
    - Buck-boost, not a buck: a drive sag can't brown out the controllers.
    - The 20 A buck now feeds only the LEDs, from the PDH. 1,680 WS2812s draw about 1 A even when dark,
      so they belong on the switched side.
E2. **Main valve is manual** (your call). A 1/4 NPT brass ball valve, the old cannon's if it's stamped
    200 psi or more (else a $6.55 Dwyer DBV-00). -$41.36 for the Aignep it replaces.
    - Open all session, closed for transport and gun work. Its handle needs to reach the rear panel:
      that's a CAD move I haven't made (the C.3 CAD session has the model open).
    - The in valves now hold tank pressure all session. They're rated 507 psi and normally closed on the
      valve rail, so a trip still isolates both chambers. A stuck in valve is caught by the chamber's
      125 psi relief, which flows 120 SCFM against a 2 mm orifice.
E3. **Smoke sensing.** The core temperature sensor was already there (MAX6675 + K probe). Added:
    - an XKC-Y25 capacitive level switch on the outside of the printed tank ($21.95; no hole in the tank);
    - a fluid gauge for free: the pump is peristaltic, so pump-seconds = mL used;
    - DS18B20 probes ($9.49 for 5) in the fogger box (heater off at 70 C, before the PETG tray softens),
      on the electronics shelf and in the battery bay. That last pair answers the "cooling system" question
      with data.
E4. **The STM32F411 is right for its job, not for Wi-Fi or video.** It has the ADC channels, timers and
    FPU for everything time-critical, and a drag-model trajectory solve takes it tens of ms. But it has no
    radio and 128 KB RAM, which is why the ESP32-S3 bridge does the web UI. Put the trajectory math in the
    browser: it's where the aim arc is drawn, and it costs the robot nothing.
E5. **Camera: a Pi Zero 2 W + Camera Module 3 Wide, about $50, on the logic rail.** H.264 over WebRTC at
    about 720p30 and 0.2 s lag. An ESP32S3 camera ($14-20) is cheaper but VGA MJPEG. Not on the list yet.
    - If 2.4 GHz turns out jammed at games, the better option is an ESP32-C5 bridge (5 GHz access point,
      $8-14) with a dual-band camera Pi. Test with one of your S3s at a game before buying.
E6. **Fixes from the review:**
    - battery and PDH volts on two ADC pins (the dashboard's battery goal had no sensor);
    - pull-downs so a cut transducer wire reads as a fault, not as an empty chamber to keep filling;
    - the gun-angle pot on 3.3 V, not 5 V (5 V would overdrive the ADC);
    - all three transducers are now the same 0-300 psi part;
    - firmware latches: no restart after an E-stop, a welded-contactor check, low-battery standby, an
      in-valve time limit;
    - LED power injection at every frame node.
E7. **Runtime:** about 25 A on average at an event, so two FRC batteries last roughly an hour. Swap one
    every ~30 minutes at long games. LEDs and fog are the big steady draws.

**Air**

P1. **The tanks aren't what's short. The gun is.** I modelled range with drag (250 g rolled shirt; its
    drag is the big unknown, so three cases):

    | Gun (110 psi max on the SZW-25) | Exit speed | Range | 200 ft at | 75 ft at |
    |---|---|---|---|---|
    | **rev C.2: 0.53 L, 22.5 in barrel** | 22.7 m/s | **108-132 ft** | can't | 77 psi |
    | 2.0 L, 36 in barrel | 35.3 m/s | 175-238 ft | 109 psi | 34 psi |
    | 2.0 L, 48 in barrel | 39.4 m/s | 194-271 ft | 89 psi | 40 psi |
    | 3.8 L (old 1 gal tank), 36 in barrel | 37.5 m/s | 185-256 ft | 93 psi | 22 psi |
    | QE5 QEV (opens in 10 ms), 1.0 L, 30 in | 35.2 m/s | 174-237 ft | 110 psi | 52 psi |

    - 200 ft needs about 35 m/s at the nominal drag (31-41 across the range). 75 ft needs only about 17.
    - So 75 ft x 6 already works. 200 ft doesn't with any pressure these valves allow: the SZW-25's DC
      coil stops at 115 psi, and its 50 ms opening is slower than the shirt's trip down a 22.5 in barrel.
      More pressure isn't available without a QEV.
    - What gets 200 ft back is the old cannon's recipe: about 2 L or more of chamber and a 36-48 in barrel.
P2. **Shot count is fine with the tanks you have.** One 200 ft shot then six 75 ft shots needs 4-6 L of
    tank, from shop air at 150 psi. The two 6 L tanks (12 L) cover it twice over. The rev C.2 gun gets
    15-23 shots at 75 ft per charge. Bigger tanks would only add shots, so I didn't change them.
    - Shot order: take the 200 ft shot first in a charge, while the tanks are highest. The dashboard can
      show when the big shot is still available.
    - Most shop compressors stop at 135-175 psi, not 200. Everything above assumes 150.
P3. **Fill port: your universal coupler.** A 1/4 MNPT M-style plug ($4.29) replaces the Schrader valve, so
    your EVOULTES couplers snap on like they do on your tanks. A plug is an open pipe, so a 250 psi brass
    check valve ($7.05) sits right behind it to hold the tanks. No kit to buy: you already have the
    hose-side coupler. +$2.19 net.
P4. **Fewer sizes.** All the air plumbing is 1/4 NPT with one 1/4 in tube and one push-fit. The only other
    sizes are the firing path (1 in), the chamber body (2 in) and the transducers' 1/8 NPT port. I looked
    for 1/4 NPT transducers to drop the bushings: the cheap ones are G1/4 (BSPP, which won't seal in NPT),
    so the bushings stay. The 0-200 and 0-300 psi transducers are now one part. A bigger gun in the old
    cannon's style (a 1 gal tank with its 1 in end port) would also drop the 2 in pipe and reducing couplings.
P5. **Open: which gun for 200 ft.** Bigger chambers and longer barrels change the gun's size, weight and
    balance, so the CAD has to be redone. I haven't changed the model or the list for it; that waits on your pick.
