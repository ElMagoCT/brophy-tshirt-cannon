# Glacis rev D.1: judgment calls

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

## Rev D gun and air (proposal, 2026-11-03)
Your picks after the range math: the top cannon on the old chamber, the bottom on a smaller one, both
barrels the same length, and the top able to run at full tank pressure. Targets: 200 ft from the top
cannon; 120 ft shots, 6 per cannon (12) per tank charge, 10 each (20) ideally. Numbers: `cad/glacis/range_model.py`.
Not in the CAD yet (D6).

D1. **Top firing valve: U.S. Solid USS-HSV04, $98.19.** 1 in NPT, 12 V DC, normally closed, pilot-operated,
    rated 1-50 bar (725 psi) on air, Cv 11.67 (the SZW-25 is 12), 25 mm, 16 W, PTFE seal, 3.86 lb.
    - What else I found: every 1 in 12 V valve on Amazon and AliExpress tops out at 0.8-1.0 MPa
      (116-145 psi). One U.S. Solid listing claims 230 psi, but its own spec table says 7 bar. ASCO's 1 in
      high-flow valve is rated 350 psi on air (price not checked; ASCO is usually several hundred). The
      1/2 in train-horn valves are rated high enough (HornBlasters 210 psi, Kleinn VX7004 250 psi), but at
      Cv 5.5 they flow under half as much.
    - Its opening time isn't published, so the model brackets it at 50 and 80 ms. Bench-test it with a
      phone in slow-motion before cutting the barrels.
    - It replaces the U.S. Solid USS2-01023 (116 psi, $59.80). The old SZW-25 moves to the bottom cannon.
D2. **Top chamber: the old 1 gal ASME tank (3.8 L)**, its 1 in end port straight onto the HSV04.
    - Read its nameplate. It needs 200 psi or more to run at full tank pressure; otherwise cap it 10% under
      the plate. Also check which small ports it has (fill, transducer, relief) and its diameter and length.
    - Software cap 190 psi, with a 200 psi relief (the same Interstate V200-4 as the tanks). It can't fill
      past the tanks anyway.
D3. **Bottom chamber: 3 in Sch 40 x 10 in nipple between two 3 x 1 reducing couplings, about 1.35 L** (you
    asked for 3 in pipe). It stays on the SZW-25 with the 110 psi cap and the 125 psi relief. 2 L would be
    a 3 in x 16 in pipe; 1.35 L does the 120 ft shot at 69 psi, so the extra length buys nothing.
D4. **Both barrels 36 in** (two 4 ft sticks, +$84.48):

    | 36 in barrels | Top, 200 psi | 200 ft at | 120 ft at |
    |---|---|---|---|
    | HSV04 opens in 50 ms | 46.5 m/s, about 263 ft | 96 psi | 42 psi |
    | HSV04 opens in 80 ms | 39.2 m/s, about 224 ft | 151 psi | 65 psi |
    | Bottom, 1.35 L on the SZW-25 | 33.0 m/s at 110 psi | can't | 69 psi |

    - 48 in barrels (the option you picked) were for a 110 psi valve. With 200 psi on the top they add range
      you don't need and make the gun a foot longer. Go to 42 in if the HSV04 bench-tests slower than ~60 ms.
D5. **Tanks: five of the same 6 L aluminum 200 psi tank (30 L), +$170.** Tank needed for 120 ft shots:

    | Charge | 6 + 6 shots | 10 + 10 shots |
    |---|---|---|
    | 200 psi | 13-18 L | 22-30 L |
    | 175 psi | 16-22 L | 28-38 L |
    | 150 psi | 22-29 L | 37-50 L |

    (Ranges are the 50 ms and 80 ms cases, with 15% lost to the tanks cooling as they empty.)
    - 30 L gives 10 + 10 from a 200 psi charge and 6 + 6 from 150-175. Three tanks (18 L, -$113 from this)
      would give 6 + 6 only from a 200 psi charge.
    - One part number, daisy-chained. More fittings and straps are on the list.
    - **"Full 200" needs a compressor that reaches 200 psi.** Most shop compressors stop at 135-175.
    - The other way to get a whole event from one fill: a 4,500 psi carbon-fibre paintball tank holds more
      air than all five tanks in about 1.5 kg, but it's filled at a paintball or scuba shop, not with shop air.
D6. **CAD (not done).** A 1 gal tank (about 6 in across) and a 3.5 in chamber can't both sit in line behind
    barrels 84 mm apart. Stagger them along the barrel axis or spread the barrels. The gun also gets longer
    and roughly 5 kg heavier, which changes its balance. That's the gun CAD, which the C.3 session has open.
D7. **Cost: +$360.07**, so $1,908.97 on the committed list. That's close to the $2,000 ceiling (about
    $1,964 with the other session's C.3 rows). The biggest adds are tanks +$170, barrels +$84 and the valve +$38.
D8. **Electronics:** the web UI's access point moves to 5 GHz on an ESP32-C5 ($13.99); the camera is deferred.
    The "STM32 with WiFi" question is answered in `electrical/README.md`.

## Rev D.1: both chambers in 3 in pipe, three tanks (proposal, 2026-11-03)
Your notes on rev D: five tanks is too many and too expensive; put a bigger or third tank where you
circled (low in the front half, under the gun); the old tank is too big, so make the top chamber like the
bottom one but longer; barrel spacing, the top elevation (60 deg is fine), the pivot and the drive motors
can all move. Supersedes D2, D5 and D6.

D9. **Both chambers are 3 in Sch 40 pipe between 3 x 1 reducing couplings.** Top: 12 in nipple, about
    1.59 L, on the HSV04 (up to 190 psi). Bottom: 10 in nipple, about 1.35 L, on the SZW-25 (110 psi).
    Both use 36 in barrels:

    | Top chamber on the HSV04 | 200 ft at | 120 ft at | Air per 120 ft shot |
    |---|---|---|---|
    | 10 in (same as the bottom) | 127-184 psi | 70-96 psi | 95-129 L*psi |
    | **12 in (picked)** | **120-176 psi** | **64-89 psi** | **102-142** |
    | 18 in | 107-163 psi | 52-76 psi | 122-177 |
    | old 1 gal tank (rev D) | 96-151 psi | 42-65 psi | 159-246 |

    - Past 12 in, a longer chamber barely adds speed (the valve limits it), and it burns more air on every
      120 ft shot. 12 in keeps the 200 ft shot under the 190 psi cap even if the valve opens slowly.
    - The smaller top chamber uses about 40% less air per shot than the old tank, which is what lets the
      tank count drop.
D10. **Barrel spacing: about 112 mm between axes (barrels about 36 mm apart, was 8).** A 3 in coupling is
    4.28 in (109 mm) across, so two of them side by side set the spacing.
    - Staggering the couplings only gets it to about 102 mm (a coupling still has to clear the other
      chamber's 3.5 in pipe), and it takes a longer nipple on one cannon. Not worth 10 mm.
    - 2.5 in pipe would fit at about 95 mm, but the chambers grow to 17-21 in long.
D11. **Tanks: the two side tanks plus a third 6 L of the same part (18 L), in the space you circled.**
    120 ft shots per charge, both cannons alternating:

    | Tanks | Total | Fast valve (150/175/200 psi) | Slow valve | Cost of the third |
    |---|---|---|---|---|
    | two side tanks only | 12 L | 9 / 11 / 15 | 6 / 8 / 10 | - |
    | **+ third 6 L (picked)** | **18 L** | **13 / 17 / 21** | **8 / 12 / 16** | **$56.60** |
    | + Viair 2.5 gal steel, 6 x 23.5 in | 21.5 L | 15 / 21 / 25 | 10 / 14 / 18 | $109.25 |
    | + 3 gal aluminum, 7 x 18.9 in (Ridetech) | 23.4 L | 17 / 23 / 27 | 10 / 16 / 20 | about $145 |

    - The third 6 L gets your 12-shot target from a 175 psi charge, and 16-21 shots from 200 psi.
    - The bigger ones add 2-6 shots for $53-88 more. The Viair is likely too long for that spot, and Ridetech
      doesn't publish the 3 gal tank's pressure rating (ask before buying). AccuAir's 2 gal seamless tank is
      $174.95.
    - The spot you circled is where the side tanks and, above 60 deg, the chambers' swing already are. So the
      CAD has to make room: cap elevation at 60 deg, move the pivot or the Falcons, or move the side tanks.
      That's a CAD call (the C.3 session); if a 3 gal fits there, it's the upgrade.
D12. **Money, each round** (parts list on committed rows):

    | Round | Change | Total |
    |---|---|---|
    | rev C.2 | | $1,512.44 |
    | C.3 electronics + air review | +$36.46 | $1,548.90 |
    | rev D (old tank on a 725 psi valve, 5 tanks, 36 in barrels, 5 GHz bridge) | +$360.07 | $1,908.97 |
    | rev D.1 (3 in top chamber, 3 tanks) | -$17.83 | $1,891.14 |
    | rev D.1 as modelled (two tanks, underglow, hood lights) | -$2.77 | $1,888.37 |
    | D.1.1 your cuts: no rivets, old 9 in mecanum (printed-wheel hardware off), goBILDA owned, light bar | -$225.30 | $1,663.07 |
    | **D.1.1 cost-down: cheapest of AliExpress (logged in), Amazon, McMaster** | **-$303.16** | **$1,359.91** |

    - Rev D.1 in detail: two fewer tanks -$113.20 and one fewer pack of straps -$8.99; the top chamber
      (12 in nipple $31.59, two couplings $63.78, a bushing $8.99) +$104.36. The old tank goes back to spare.
    - The other session's C.3 rows (elevation, smoke, body) add about $55 on top.
    - The biggest lines now: speakers $160, barrels $169, the three tanks $170, the HSV04 $98.
D13. **Search: one tank, 200 psi, bigger than the three 6 L tanks (18 L) and under their $169.80.**
    None found that also fits. 200 psi tanks over about 12 L are long and thin (24-30 in). The robot's
    longest straight run in the spot you circled is about 18-20 in across, and only if the Falcons and
    fogger move. Shorter, fatter 5 gal tanks exist, but they're 125-150 psi.

    | 200 psi tank | Volume | Size | Price | Verdict |
    |---|---|---|---|---|
    | **6 L aluminum (current)** | 6 L | 6 x 14.2 in | $56.60 | Fits anywhere; $9.43/L, the cheapest per litre |
    | Viair 91028 steel | 9.5 L | 6 x 23.5 in | $109.25 | Too long to go across |
    | Ridetech 3 gal aluminum | 11.4 L | 7 x 18.9 in | $141-145 | Might fit across; pressure rating not published |
    | Generic 3 gal aluminum (eBay) | 11.4 L | 6.7 x 20.5 in | $48-58 | Listed 200 psi but out of stock; generic like the 6 L |
    | Seamless / Speedway 2 gal | 7.6 L | 6.6 x 18 in | $175-201 | Over budget |
    | Air Lift 4 gal aluminum | 15 L | 6 x 30 in | not checked | Too long |
    | Vixen 5 gal steel | 19 L | 7 x 30 in | not checked | Too long |
    | "Bomb" 5 gal | 19 L | 20 in long, 12.5 in high | about $230 (EUR 199) | Over budget, 1/2 in ports |

    - **So the three 6 L tanks stay (18 L, $169.80).** The only upgrade worth it is a 3 gal as the third tank
      (23.4 L total), if one is confirmed 200 psi and the CAD shows it fits across. That's +$0 to +$88.
    - Skipped: 150 psi tanks (Viair 91050, Firestone, Kleinn, HornBlasters) and anything with G (BSP) ports.
D14. **CAD test-fit (the C.3 session): no room for a third tank, so it's two 6 L tanks (12 L).**
    - The side tanks already fill your circled band in side view (x -134..226 mm, z 280-440). Between them
      only about 295 mm is free lengthwise, and a 6 L needs 360. The gun's rear swing is behind that and
      the front face is ahead of it.
    - Across the robot (x ~80, z ~335, ends in the middle of each front side window) a 3 gal fits: the
      generic 170 x 520 mm and the Ridetech 178 x 479. But it takes the side tanks' place, so 11.4 L would
      replace 12 L. The Viair 2.5 gal (597 mm) doesn't fit.
    - The CAD now has the pivot at z 645 and **45 deg max elevation** (you'd allowed 60), slot +/-133 mm.
    - 120 ft shots per charge with 12 L: **9 / 11 / 15** from a 150 / 175 / 200 psi fill if the HSV04 opens
      fast, **6 / 8 / 10** if slow. Your 12-shot target needs a 200 psi fill and a fast valve. More would take
      a bigger relayout: the side tanks need somewhere new, and the battery bay is behind them.
    - **Money: -$65.59** (one fewer tank -$56.60, one fewer pack of straps -$8.99), so **$1,825.55** on the
      committed rows. The other session's C.3 parts rows (elevation, smoke) are still uncommitted.

## Model: rev C.3 body and rev D.1 gun (CAD, 2026-11-03)
Your body notes, then the D.1 gun above, as built and checked in `cad/glacis/` (Onshape version "Glacis rev D.1").
These replace items 14-17 and 20-26 where they disagree.

M1. **Frame and acrylic.** The acrylic now laps 7 mm onto the print (was 14): members are 19 mm wide, the outer lip
    stays 12. Windows, acrylic and clips all have rounded corners (22.5 mm windows, 28 mm acrylic). Each clip is a
    round head lapping 6 mm over the acrylic's corner plus a tail to its screw, which goes into an M4 heat-set
    insert where the acrylic's corner is cut away. M4 x 12 is now the only screw on the body; the M3 pack is off
    the list.
M2. **Front.** The front panel stops at the gun-well floor, so it's one plain rectangle (no arms up the sides).
    Above it, each side is one printed cheek round the speaker pocket (it replaces the cluster of small pieces you
    named). The speakers sit 13 mm deeper.
M3. **LED loops.** Corners are 22.5 mm (half) and stand square to the panel, so the strip bends the easy way; the
    15 deg lean only happens on the straight runs and twists in over 40 mm. How far in each run sits:
    - **42 mm on edges shared with another panel.** I tried 8. A neighbour's rail hangs square to its own panel, so
      any closer it sits right behind this panel's acrylic (a dark shelf, and it hit the acrylic) and its cross runs
      cut through this loop. The corners still come in: about 66 mm from the panel corner, was 78.
    - **19 mm on edges with no neighbour** (bottom, front cut, the seams in the deck and side walls): just behind the
      window edge, so those dim bands are gone. 24 on the gun-well edges (clear of the pivot blocks), 30 on the
      speaker notches, 46 under the speaker cups.
    - A flange from the member's inner face carries each rail. 10.6 m of 60/m strip in the loops.
M4. **Battery doors.** The side walls now split at x -105 (was -150) and the batteries sit 17 mm further forward,
    so a battery passes between the door's LED rails with a few mm each end.
M5. **Underglow:** a printed 45 deg bracket under each outer and end rail, just inside the bumper, with 60/m strip
    aimed down and out. Light passes under the bumper (3 in off the floor) and pools round the robot. 2.5 m, from
    the rest of the third 60/m roll. A strip inside the bumper would mostly light the noodles.
M6. **Hood lights:** two mini 12 V 3 W spots (30 deg beam, 32 x 19 mm, $3.86 each on AliExpress) in printed pods at
    the low front corners, just above the bumper, aimed straight ahead; dimmed together on the last spare MOSFET.
    The cheeks were the first spot, but the wider gun well left them only about 20 mm wide.
M7. **Gun (rev D.1).** Both chambers 3 in Sch 40 between 3 x 1 couplings: 12 in on the HSV04 (1.63 L) on top, 10 in on
    the SZW-25 (1.38 L) below; barrels 112 mm apart and 36 in long. Valve faces line up; the core is 148 mm wide
    for the couplings plus the fill and smoke lines beside them. Gun 20.3 kg, balanced on the pivot.
    - **Elevation 0-45 deg, pivot raised 73 mm to z 645.** The chambers reach 460 mm behind the pivot. At 60 deg
      they swung down through the electronics shelf and the rear manifold, fill plug and main-valve lever; 45 deg
      is about the best range angle anyway. The bearing towers now stand about 15 mm above the deck, inside the
      gun well, which is 266 mm wide (was 224).
    - Envelope: 62.2 in long with the gun level (the muzzles reach 25 in past the front bumper), 30.9 in tall.
    - Elevation belt 150T (was 135T) so the motor stays above the side tanks.
M8. **Third tank: no room.** The side tanks already fill the zone you circled (x -134..226, |y| 87-239, z 280-440).
    Between them, a 6 L lengthwise needs 360 mm but about 295 is free (the gun's rear swing behind, the front face
    ahead). A tank across the robot (3 gal 170 x 520 or Ridetech 178 x 479) fits at x ~80, z ~335 with its ends in
    the middle of the front side windows, but only in place of the two side tanks. So D.1 keeps two 6 L tanks (12 L).
M9. **Detailed pneumatics in Onshape.** Every air part is now a recognisable fitting (hex bodies, thread stubs,
    push-to-connect collets, valve coils and levers, relief pull rings, transducer plugs; `cad/glacis/pneu_parts.py`),
    and each one's Onshape Description says what it does.
M10. **Onshape is grouped by system:** sub-assemblies for the body panels, body frame, lights & speakers, bumpers,
    pneumatics, power & smoke, chassis & drive, and the gun. Click one's eye to hide or show it.
M11. **Checks:** sweep 0-45 deg clean, nothing over the bed, every part one solid. Two fittings' hex bodies touch
    (146 and 64 mm3) at the valve cross and the manifold's fill elbow, where a real close nipple would space them.
    Weight 174 lb (gun 20.3 kg). Parts $1,888.37.

## Rev D.1.1: LEDs, light bar, tanks, parts cost-down (2026-11-04)
Onshape version "Glacis rev D.1.1"; renders in `docs/glacis/render_d1_1_*.png`.

N1. **LED loops (your notes).** Every corner radius is 2/3 of C.3's (windows 15 mm, acrylic 18.7, LED corners 15), and
    each kind has its own variable in `params.py`: `WINDOW_R`, `ACRYLIC_R`, `LED_CORNER`, `FLANGE_ROUND`, `CLIP_ROUND`,
    `RAIL_EDGE_R`. The rail's free back edge rounds over (2.5 mm).
    - The strip face now starts right at the window edge on every side (19 mm in), so the dead band is gone. On an
      edge shared with another panel the two rails meet back to back in a point.
    - The strip is 5 mm closer to the acrylic (0.96 in behind the panel, was 1.15) and the rail is 5 mm shorter.
    - Where three panels meet, a neighbour's corner turn crosses the loop. The strip is cut there and jumped with 3 wires:
      8 jumpers on the robot.
N2. **Front light bar: your Zmoon 12 in** (72 W, spot/flood) across the nose just above the bumper, on two printed
    brackets. Its face stays inside the bumper line.
    - The STM32 switches it, and can PWM-dim it, through a MOSFET channel (about 6 A).
    - Amazon lists only "12 in", so it's modelled 330 x 30 x 45 mm [UNVERIFIED].
    - The lens-pod bars from the AliExpress search are out.
N3. **Tanks: the EVIL ENERGY 2.5 gal (9.5 L, 200 psi, 498 x 200 x 160 mm, steel 4.55 kg, $98.99) isn't worth it.**
    The CAD test-fit:
    - **Sides, lengthwise:** about 381 mm is free ahead of the battery bays, but the tank needs 498. At every position
      tried it runs into a battery and pokes through the side wall.
    - **Across the front:** one fits, at x 60 and z 330. It only needs the fog line to the gun rerouted. But it sits in
      the same space as the two side tanks, so it can only replace them.

    Shots at 120 ft per charge to 150 / 175 / 200 psi, both cannons alternating:

    | Air | Cost | HSV04 opens in 50 ms | in 80 ms | Fits? |
    |---|---|---|---|---|
    | **Two 6 L (now), 12 L** | $112.62 | 9 / 11 / 14 | 6 / 8 / 10 | yes |
    | One EVIL instead, 9.5 L | $98.99 | 7 / 9 / 11 | 4 / 6 / 8 | yes, in their place |
    | Two EVIL, 18.9 L | $197.98 | 13 / 17 / 22 | 8 / 12 / 16 | no |
    | Two 6 L + one EVIL, 21.5 L | $211.61 | 15 / 21 / 25 | 10 / 14 / 18 | no |

    - **For the EVIL:** steel, 6 ports, well reviewed. Two of them would nearly double the shots.
    - **Against:** two don't fit without moving the batteries back and growing the body. One alone holds less air than
      now, and the steel adds about 6 kg over two.
    - **The cheaper lever is the valve:** bench-test the HSV04 and charge to 200 psi.
N4. **Parts cost-down: $1,888.37 to $1,359.91.** Every line is now the cheapest of AliExpress (your logged-in
    prices), Amazon and McMaster.
    - **Your cuts:** no rivets (your screws), the old 9 in mecanum for now (608s, M8 rod, nylocs, hub bolts and 140T
      belts off), and the goBILDA owned.
    - **Biggest savings:**
      - relief valves -$39.09 (McMaster 48435K72: ASME, ring pull, $6.67);
      - speakers -$40 (SoundAlert $59.99, 2 in deep like the old pick, 8 ohm);
      - barrels -$36.86 (3 ft tubes are the 36 in barrels);
      - couplings -$31.60;
      - LED strips -$23.24;
      - one push-to-connect pack instead of two -$19.99 (the CAD uses 8);
      - E-stops -$17.48;
      - most electronics moved to AliExpress.
    - **What went up:**
      - fog core +$11.97 ($22.42 was the new-shopper price);
      - check valve +$8.82 (Zoro isn't one of the three; AliExpress check valves are 145 psi);
      - Zmoon bar +$12.74 over the AliExpress bar;
      - sealant +$4.53;
      - an estimated $15 for McMaster shipping.
    - **Still off the three sellers, on purpose:**
      - the Aignep in valves: nothing at the three is 1/4 NPT, direct-acting and rated 200 psi under $155;
      - the HSV04: Amazon's only 200+ psi 1 in valve is $156.66;
      - the pool noodles: Amazon's are $33 for six.
    - **Kept the dearer, rated part on the pressure side:**
      - AliExpress relief valves are $2.69 but unrated;
      - its brass crosses state 850 kPa (123 psi);
      - the cheaper transducer doesn't state 0.5-4.5 V.
N5. **Not checked yet:**
    - AliExpress started showing a slider captcha after the parallel lookups, so the cheapest siren speakers there weren't
      searched. Solve the slider once in your browser and I'll look.
    - The M5 insert price is assumed equal to the M4 pack.
    - The canvas colour on Amazon, the Zmoon's size and the SoundAlert's height are unconfirmed. The speaker cup may need
      a few mm once it's in hand.
N6. **Checks:**
    - The light bar clears everything.
    - Sweep 0-45 deg is clean, nothing is over the bed, and every part is one solid.
    - The same two fitting slivers as D.1 remain (146 and 64 mm3): where two male threads overlap inside a 1/4 cross, the
      model engages them deeper than a real joint does.

## Rev D.1.2: the LED band is the window wall (2026-11-04)
Onshape version "Glacis rev D.1.2"; sections in `docs/glacis/led_sections_d1_2.png`. This replaces N1's rail.

N7. **Your fix list:**
    - **No rail, no flange.** The window wall runs straight back from the ledge the acrylic sits on (the only step) and
      carries on past the member as a 2.5 mm web.
    - **The strip** sits on that wall's last 10 mm, centred 25 mm behind the acrylic. It leans 10 deg toward the panel
      on the straight runs and stands square round the corners. The bend into the lean is the only "chamfer".
    - The strip needs only about 8 mm to stick to; the band is 10 mm, the strip's width.
N8. **No strip touches another strip, a web or the frame**: 0 overlaps, 0 jumpers, with 99-100% of every loop kept.
    The rule that does it:
    - **Shared corners:** each panel's web and strip stay on their own side of the corner's bisector, so the two
      neighbours' strips meet back to back at a point. That puts the window edge 31-36 mm in from a shared edge,
      depending on the angle (91 deg 36, 94 deg 35, 98 deg 32.5, 100 deg 31.4): in between the old 42 and the 19
      that overlapped. At 19, each web hung into the neighbour's window and ran into its seams and corners.
    - **Every other edge** stays at 19 (gun-well edges 24). The build pushes in any edge whose strip would hit frame,
      4 mm at a time. None needed it.
    - **The cost:** wider solid members on the shared edges, so the frame is 5.64 L of PETG (was 4.44). Hollowing their
      hidden back would only win about a third of that back, because the neighbour's member already fills most of
      the extra width.
N9. **Clip inserts no longer break out of a slanted face.** Each hole is tested against the outer surface with a 1 mm
    skin and shortened if needed. At the two deck-front corners, where two clips merge, the second screw would break
    out whatever the depth, so each of those clips keeps one screw.
N10. **Also fixed:** the light bar brackets' upright tab now sits behind the bar instead of inside it (2,880 mm3 each).
     Checks:
     - interference: only the two known fitting slivers;
     - sweep 0-45 deg clean;
     - nothing over the bed;
     - every part one solid.

## Rev D.1.3: chamfered window wall, filled LED corners, bent frame strips (2026-11-04)
Onshape version "Glacis rev D.1.3". Replaces N7's straight wall.

N11. **The thick edge is chamfered away, everywhere.** The acrylic keeps its 7 mm ledge (the only step). From the ledge's
     edge, which follows a line MEM_W in from the panel edge rounded at the corners, the wall chamfers straight down to
     the top of the LED band, then the band, then the skin.
     - Below the member the window cut is only a 4 mm ring inside the LED line. It clears the strip and nothing else.
     - Frame 5.17 L of PETG, down from 5.64 L (D.1.2), even with the corners filled.
N12. **The gap between back-to-back LED corners is filled.** On the 10 edges shared by two panels at an angle, the
     corner is solid between the two skins. The two strips sit on one V-shaped ridge that comes to a point, with no slot
     between them. Every way in for a joint screw there would come through the ridge or a surface you see through the
     acrylic, so those 24 joints are tapered tenons glued with epoxy. The other 57 keep their M4 cross screws.
N13. **Frame (interior) strips are modelled as one piece per member.**
     - Each strip lies on its tunnel's inner wall with the LEDs facing out.
     - At each end it bends the easy way (about its width), up to 8 mm radius, up into the feed slot. It runs out to the
       slot's mouth at the bottom of the ridge, where it's soldered to the next member's strip. Each bend is sized so the
       whole strip width stays inside the slot.
     - On 6 short members the slot at one end is too short for even a 3 mm bend. There the strip ends straight at the
       slot and is soldered in place.
     - 8.7 m in all.
N14. **Checks:**
     - No strip touches another strip, a skin, a corner fill or the frame; 0 jumpers.
     - Sweep clean, nothing over the bed, every part one solid.
     - Only the two known fitting slivers.
     - An independent code review caught and fixed: the joint counterbore cutting both LED bands, a corner-fill gap at
       mismatched corners, buried solder ends, and the contact check not seeing strips.

## Rev D.1.4: printable frame, mounts, bumper ring, Xprite speakers (2026-11-05)
Micah's asks:
- hollow the prints to 2 mm and estimate plates, PETG and hours (0.6 mm nozzle, 2 walls, 10%, no slicing, frame only);
- review and clean up every part (clip 01-2, E04S0 + N13, N11, E28S0 + N14) and cut everything to the CC1/CC2 beds;
- tie the frame to the chassis perimeter and the turret towers (screwed from below into threaded inserts);
- bumpers that slide off the bottom, held by #10-32s from inside the chassis into wood inserts.

A nine-agent review of all 121 printed body parts then found 39 more problems (26 survived a skeptic, the
critic added 13), and the fixes are below. Onshape version "Glacis rev D.1.4". Your custom tank edits were versioned first,
as "Micah's edits (custom tank), before rev D.1.4".

N15. **Print plan** (docs/glacis/print_plan.md, from render/part_report.py):
     - each part in the orientation it prints in;
     - support from a ray cast, so tunnel roofs count as bridges;
     - plates packed from the real footprints.
     - **45 frame pieces on 11 plates: 2.97 kg PETG** (145 g of it support), **73 machine-hours, about 37 h with
       the CC1 and CC2 both running** (0.6 mm, 2 walls, 10% gyroid). Treat it as +/-25%: a slicer run will be closer.
     - At 3 walls (2 mm walls): 4.05 kg, about 50 h on both printers.
     - The other printed body parts (78 clips, posts, brackets, cups, grilles at 4 walls, 25%): 2.03 kg, 6 plates,
       about 27 h on both printers.
     - E13S0 and E31S0 touch the bed on a narrow strip: give them a brim.
N16. **Nothing is hollowed in the CAD.** At 2 walls and 10% gyroid the slicer already prints every piece as a
     1.3 mm shell over sparse infill, so a modelled 2 mm hollow would only add inner walls. If "2 mm" means the wall
     thickness, that's 3 walls (the plan gives both).
N17. **Your examples:**
     - Clip 01-2 (and its mirror 05-0) lapped the acrylic by 0 mm³. That panel's face ends in a spike by the
       speaker notch, and the acrylic's corner sits about 75 mm back from the tip. The two tip corners now act as
       one: the clip runs down the spike to the acrylic's corner, with its screw where both members are wide
       enough to clear their light tunnels. Every clip now has to lap at least 120 mm³; all 38 do.
     - E04S0 is part of the cheek, and N13 (now N12) is merged into its neighbour.
     - E28S0 + N14 (now E29S0 + N10 + E28S0) and its mirror are merged, along with the two lone sticks at the
       rear-top corners. Short segments merge into their one off-edge neighbour when the union fits the bed and
       lies flat.
     - N11 (now N00): the node across the gun well's front is still the only glued split. Its halves are merged
       into E05S0 and E05S1, and both fit the bed.
     - The rear one (N09) is gone: its region now leans out along the well floor.
     - 45 frame pieces, mirrored left and right (a mirror-consistent cut order), 51 tenons, no loose ends.
N18. **Frame to chassis.** Sized for your #10-32s (1/2 and 2-1/2 in):
     - **Side walls:** the bottom member sits right on the bumper, so each side station has a tab on the frame's
       inner face, out over the outer rail. A post on the rail holds it: 2-1/2 in up through the rail into the
       post's foot insert, then 1/2 in up from the post's outer pocket into the tab.
     - **Ends:** posts on the end rails at y 0 and +/-170. The outer two stand on the corner gussets.
     - **Towers:** a bracket on each tower's outer face, two 1/2 in screws in +/-3 mm slots into rivnuts. Nothing
       pokes into the gun well, and you set the height against the deck at assembly.
     - The x -150 station moved to -205: there its tab blocked a frame joint's cross screw. The build now checks
       every tab and insert against the joint screws and tunnels.
N19. **Bumpers are one ring.**
     - **Screws:** the old front, rear and outer side screws were unreachable (behind the wheels, the PDH and the
       bellypan). The 6 that hold the ring are at x -80, 0, 80 through each side rail, driven from the open bay
       underneath.
     - **Corners:** printed brackets join the four plywood strips (2 x 1/2 in per leg from the rail side, heads
       counterbored flush).
     - **T-nuts:** #10-32 4-prong T-nuts replace the wood inserts. A 10 mm insert doesn't fit 1/4 in ply. The T-nut
       goes in from the noodle side, so the screw pulls its flange into the ply; file its barrel to 6 mm.
     - **Axle screws:** the side strips have open-bottom slots past the axle-end screws.
N20. **Clips and panels:**
     - **Inserts and screws:** M4 x 6 inserts (5 mm OD, 4.7 mm hole, as bought) with M4 x 8 screws. Where two
       neighbouring panels' clip screws met inside a node (10 pairs), or a face was close, a short M4 x 4 insert
       and an M4 x 6 screw (12 clips).
     - **Battery doors:** ordinary clips. The quarter-turn latch couldn't turn in its pocket, and its insert ran
       through a light tunnel.
     - **Acrylic:** cut 1 mm under per side, with 1/16 in foam tape on the ledge (the rebate is 0.7 mm deeper) so
       the clips clamp it.
N21. **Speakers: Xprite 200 W (B01DMSR4L4).**
     - **Cups:** sunk 7.4 mm deeper so the face stays put. Each cup is screwed to the frame by 4 M4 through its
       walls (it was only sitting in the notch).
     - **Amp:** "100 W drivers" read as the amps: a TPA3255 board on a 1500 W boost set to 48 V, about 100 W a
       speaker, on a 40 A PDH channel. If you meant something else, say.
N22. **Light bar brackets:** a plate on the front slant's bottom lip with 2 x M4 into inserts. The front and rear
     bottom members lose their light tunnel: it ran under the acrylic's rebate with paper-thin walls. A jumper wire
     goes round each. The front's LED web moved in to 23 mm, so those pieces have a flat face to print on.
N23. **Underglow brackets** sit flat on the rails again, stepping down under the corner gussets. Each has 2 x M4 and
     a clearance hole round the post screws' heads.
N24. **Joints:** TENON_CLEAR is 0.3 mm a side for the 0.6 mm nozzle; print a test joint first. Small 5 mm tenons get
     their own mortise and are glued. Where a tenon would push a piece past the bed, the neighbour carries it.
     Merges keep 2 mm of bed margin.
N25. **PETG for everything.** The notes that said PA-CF or PETG-CF now say PETG, 5 walls, 40% gyroid.
N26. **Still open (your call, or later):**
     - Diagonal placement on the 256 bed would allow longer segments and fewer joints.
     - The glow through 2-wall gyroid will show the infill: the plan suggests a 100% modifier on the lit lip.
     - Cap the 100/m frame strips' brightness in firmware: heat in PETG in the sun.
     - The rivnut grip range is [UNVERIFIED].
N27. **Checks (build 15):**
     - interference: only the two known fitting slivers (146 and 64 mm³);
     - the 0-45 deg sweep is clean;
     - every printed part fits the 250 mm bed, and every part is one solid;
     - every clip laps its acrylic, no two clip screws meet, and no clip insert crosses a light tunnel;
     - every segment end has a neighbour piece;
     - every insert found frame clear of the tunnels and joint screws: 16 frame-mount, 8 speaker-cup, 4 light-bar;
     - LED strips: 0 overlaps, 0 jumpers.

## Rev D.2 proposal: listing re-check, one controller, bumper foam (2026-11-06)
Micah's asks: review every part (pneumatics with every thread confirmed from its listing, electronics), find better or
cheaper parts, a stronger single-board controller with WiFi (and Bluetooth for music the dashboard still controls),
drop the PWM gate, GoTo Foam for the bumpers, a female fill valve, a 1x6 bumper backing at the next CAD update, the LED
lean 0.75 closer to the panels at the next Onshape update; no Onshape changes until he green-lights the parts list.
Artifact "Glacis air & wiring" (same URL) is now four tabs: an air sim, a power sim, the parts list, the review.

P1. **Fill line genders were wrong.** The male McMaster 1077T17 plug went onto a male 1-1/2 in nipple, and the
    "FNPT x MNPT" check valve (B076K8SLBZ) is male on both ends (listing photo). Now: Milton 728 1/4 FNPT M-style plug
    (300 psi per Lord Co./Toolsid; box of 10, $9.99) threaded onto the check valve, which itself passes through the
    rear panel, then two street elbows into the manifold. The 1-1/2 in nipple is freed. Micah: "the fill valve should
    be female".
P2. **Three street elbows were missing** from the parts list (the CAD has them: main valve, fill line). 5-pack $11.99.
P3. **Top chamber fittings: listing ratings below 190 psi.** Supply Giant's 3 x 1 coupling and 1 x 1/4 bushing both say
    "pressures up to 150 lb". ASME B16.3 rates Class 150 malleable iron at 300 psi up to 150 F, but the rule is rated
    parts by their listing. Proposed: 304 stainless 1 x 1/4 bushings, 350 psi (B0C7N73YVZ, $7.99, cheaper) on both
    chambers; MSI Products 3 x 1 couplings "150-300 psi" (Global Industrial, $27.95) on the top only. Micah's call: those,
    or cap the top at 150.
P4. **HSV04 thread is "NPT / G"**, one version, no option (the old note said to pick NPT). Test-fit a 1 in NPT nipple
    before trusting it at 190 psi. Price $98.19 confirmed.
P5. **SZW-25 listing now says 0-90 psi** for the 12 V DC valve (old note: 0-115). Bottom capped at 90 until Micah reads
    the plate. The 125 psi relief stays.
P6. **Tank**: photos show 2 side bungs + an end port and welded feet; the CAD has 3 bungs underneath and strap saddles.
    $56.60 list ($46.81 is a new-shopper deal). Fix at the next CAD update.
P7. Confirmed from listings (2026-11-06): relief 48435K72 1/4 MNPT, ASME VIII, 125 and 200 set options, $6.67;
    transducer 1/8-27 MNPT, 0.5-4.5 V, +/-1% FS; 9151K91 1/4 M x 1/8 F, 1,000 psi; crosses 1/4 FNPT x4; close nipples
    and plugs 1/4 MNPT, 1,200 psi; DOT tube 1/4 OD J844 1,150 psi; push-to-connects 1/4 tube x 1/4 MNPT 250 psi J1131;
    Aignep 02F 1/4 NPTF both ends, 2 mm, 0-35 bar, $41.36. Not re-read: the Dwyer ball valve (Zoro blocks reads) and
    McMaster 44615K416. No psi stated: the 3 in nipples, the street elbows, the barrels.
E1. **One controller: ESP32-P4 + ESP32-C5 on one board** (Wireless Tag WTDKP4C5-S1, $29.29 AliExpress). Replaces the
    STM32F411 + ESP32-C5 bridge + their UART. Keeps 2.4 + 5 GHz WiFi 6, adds MIPI-CSI + H.264 (camera), 16 parallel LED
    lanes, a UART for a lidar. ADS1115 ($7.99) for the transducers (settled: ESP32 ADCs too nonlinear); the P4 ADC reads
    the pot and battery volts. Catches: new board (3 sold), ESP-IDF wanted for camera/LEDs, Arduino partial.
    Considered: ESP32-S31 (the only one-chip WiFi + Bluetooth Classic, but 2.4 GHz only, ESP-IDF preview, no Arduino),
    Arduino GIGA R1 WiFi ($65.54, 2.4 GHz only, no A2DP in the Arduino libraries, Mbed core being retired), Pico 2 W.
E2. **Bluetooth music** needs Bluetooth Classic (A2DP); only the original ESP32 and the S31 have it. A $8.99 ESP32
    WROOM board is the phone's speaker and streams I2S into the P4, which mixes the horn/effects and sends volume/pause
    back over a UART. If it dies only phone music stops. Alternative: songs stored on the robot, picked from the dashboard.
E3. **PWM gate removed** (Micah). The contactor is the cut-off: its coil runs through rear E-stop contact 1, the safety
    node's switch and the main controller's MOSFET in series. The safety node's only job is holding that coil while the
    remote's and the controller's heartbeats are alive. The valve arm relay stays (coil from the PDH through E-stop
    contact 2, armed by the controller). 74AHCT125s now only level-shift the LED data; the new MOSFET modules trigger
    from 3.3 V.
E4. Firmware latch modelled in the sim: power lost without a command = stays off until Enable is pressed again.
B1. **Bumper foam**: GoTo Foam 5 x 24 x 24 in, 43 ILD, $19.99 (Micah's pick) replaces the noodles. **Backing becomes a
    1x6** (Micah, next CAD update): 3/4 in is 1/2 in thicker per side than the 1/4 ply, so the foam is cut 2 in deep
    (not 2.5) to stay 27.75 in wide under the 28 in door limit; 5-1/2 in tall vs 5 in of foam (rip it or let the canvas
    cover the step); T-nut screws become the 1-1/4 in #10-32s. Lumber price is an estimate ($9 a board).
C1. Cost-downs: barrels to K-mac on Amazon (same 3.00 x 2.75 x 1/8 x 36 in PC tube, $45.81 vs $66.05), fog core now
    $26.38 at his price, one contactor ($12.99), diymore logic buck-boost ($8.17), MOSFET 10-pack ($6.29), Hillman tee
    nuts, FogUp gallon for a quart's price, light bar $17.99, McMaster shipping $10 (no long box). Kept: TPA3255 + 48 V
    boost (100 W into 8 ohm needs ~28 V RMS), Xprite speakers (cheapest real 200 W), the potted 20 A buck.
D12 (rev D.2). **Money**: $1,373.42 -> **$1,382.62 (+$9.20)**: cost-downs -$73.98, fixes +$26.34, Micah's changes
    +$56.84 (controller swap +$11.87, ADS1115 +$7.99, music board +$8.99, foam +$9.99, 1x6 est. +$18.00).
Queued for the next Onshape update (after the green light): LED lean 10 -> 10.75 deg ("0.75 closer to the panels";
read as degrees, to confirm), 1x6 backing + 2 in foam, the fill line re-route, the real tank ports and feet, one
controller board + music board + ADS1115 + one contactor on the shelf, MSI couplings and stainless bushings on top.

### Rev D.2, Micah's follow-ups and the green light (2026-11-06)
F1. **Bottom cannon to full tank pressure** ("the bottom has to do the full 200"): a second U.S. Solid HSV04 ($98.19)
    replaces the SZW-25 (now spare, listed 0-90 psi); MSI 150-300 psi couplings on both chambers (the Supply Giant pair
    is gone); a 200 psi relief on both chambers (four 48435K72 at 200, the 125 psi one is gone). Both caps 190 psi: the
    tanks are rated 200, so a chamber can't usefully exceed the tank, and 190 keeps the 200 psi reliefs from simmering.
    +$106.11. The gun re-balances itself (gun.py solves the CoM onto the axle).
F2. **Fill line, corrected again:** the check valve can't pass through the panel (its 1/4 NPT male end is ~10 mm and
    the panel is 5.7 mm, leaving ~4 mm for the plug). Final chain: female Milton 728 outside <- the owned 1-1/2 in
    nipple through the panel (the elbow sits 27.7 mm behind the outer face, so the nipple reaches the plug with ~3 mm to
    spare) -> 1/4 FNPT x FNPT 90 deg elbow (ChillWaves 2-pack, $7.99, 1,200 psi) <- male x male check valve -> street
    elbow -> rear manifold. Street elbows used: 2.
F3. **Open ports audit:** rear manifold ends 2 + up to 3 spare bungs per tank (photos show 3-4) = 8 of the 10 hex plugs;
    the valve cross and chamber crosses have no open port. One low tank plug doubles as the drain.
F4. **LED lean 17.5 deg** (Micah; supersedes the 10.75 reading of "0.75 closer"). params.LED_BAND.
F5. **Bumper backing 1x6 ripped to 5 in** (3/4 in), foam 2 in deep x 5 in: the envelope stays 27.75 x 37.74 in and the
    5 in bumper height, so nothing above it moves. Foam modelled as one mitred strip per side (cut from 24 in lengths).
F6. **E-stop placement** (his question): stays in the contactor's coil circuit, a hardwired power wire, not data. A 22 mm
    E-stop's contacts are rated ~10 A and the main line peaks near 160 A; the contactor switches the current, the
    E-stop cuts its coil, so no software can hold power on. The 120 A breaker is the main-line manual kill.
F7. **Compute headroom (estimate)** for the ESP32-P4: with the web UI to 8 browsers, 1 kHz control, 1,680 LEDs at
    60 fps on 8 PARLIO lanes, audio mixing, 720p H.264 to one viewer and a lidar: ~30% of the network/camera core and
    ~20% of the control core busy (65-75% headroom each); ~500 KB of 768 KB SRAM and ~20 of 32 MB PSRAM free. Video
    bandwidth through the C5 link and WiFi airtime is the real limit (one 720p or two 480p streams, ~10-20 Mbps).
F8. **Barrels, cheaper pipe:** clear PC (K-mac) $91.62 for two vs one 10 ft stick of 3 in Sch 40 solid PVC (Charlotte,
    $37.31 at Home Depot) for both: -$54.31, but opaque, 3.04 in bore, 3.5 in OD (spigot and four prints resize).
    Not changed: Micah's call.
D12 (rev D.2 final). **Money:** $1,373.42 -> **$1,496.72 (+$123.30)**: cost-downs -$73.98, fixes +$34.33 (incl. the
    FxF elbow), Micah's changes +$162.95 (controller swap +$11.87, ADS1115 +$7.99, music board +$8.99, foam +$9.99,
    1x6 est. +$18.00, bottom cannon to 200 psi +$106.11).
