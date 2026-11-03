# Glacis rev C: judgment calls

Rev C (2026-11-02) is the redesign from your third round of notes:
- both chambers on the back of their cannons, in line;
- the gun balanced on a pivot axis that runs between the two cannons;
- the old cannon's firing valve, plus one more;
- small, cheap 2 in pipe chambers (0.53 L), sized by a shot simulation, with the barrels as close as they go;
- the back tank moved to the right, and no room left for a pump;
- a 60 deg front, with the sides and back leaning more;
- the rear-panel controls at the bottom of the panel, and the electronics in the back bottom;
- a 60 rpm pivot motor;
- a 12 V smoke machine with printed ducts;
- LED strips run through the frame to backlight the panels.

Each item says what I picked and why. Numbers come from `cad/glacis/params.py` and the last clean run
(`cad/glacis/out/check_log.txt`).

**Checks on the final model:**
- no part overlaps another;
- nothing hits anything as the gun sweeps 0-90 deg, checked every 5 deg;
- every printed part fits a 256 mm bed;
- every part is a single solid.

**Where it is:** Onshape "Brophy Mark 5 - Glacis" holds the rev C tabs and the "Glacis rev C (whole
robot)" assembly (468 parts). The parts list is the "Glacis BOM" tab: **$1,827.38** to buy (rev B was
$1,555.11). Aluminum, acrylic, prints, Falcons, FRC stash parts and the old cannon's valve and chamber
are all at $0.

## What I identified on the old cannon
1. **Firing valve: Atlantic Valves SZW-25.** The plate says SZW-25, not S2W.
   - It's a 1 in NPT stainless solenoid valve, normally closed, with a Viton seal.
   - It's semi-direct acting, with a 25 mm orifice and Cv 12. The 12 V DC coil is 16 W.
   - Rated **0-115 psi on the 12 V DC coil** (0-145 on the AC coils).
   - It's sold at electricsolenoidvalves.com, not Amazon: SZW-25-12VDC, **$127.56**, 29 in stock
     ([page](https://www.electricsolenoidvalves.com/1-inch-12-volt-dc-stainless-steel-electric-solenoid-valve/),
     [spec sheet](https://www.electricsolenoidvalves.com/content/Atlantic_Valves_SZW_Spec_Sheet.pdf)).
   - The old one is reused and one more is on the list.
   - Same-spec Amazon option: U.S. Solid USS2-01023, $59.80
     ([B0CXWR76GT](https://www.amazon.com/dp/B0CXWR76GT)). Its listing contradicts itself on pressure.
   - **Check the old valve's coil label.** It has to be the 12 V DC one.
2. **Old chamber: a grey primed-steel ASME air tank with a 1 in NPT end port**, probably 1 gal. It's no
   longer used; see item 6 for the new chambers.
   - Its buyable twin was McMaster 9888K9 at $397.34
     ([link](https://www.mcmaster.com/9888K9/)), which is what pushed me to look for something better.
3. **Longacre 5 gal polished aluminum tank:** rated 125 psi
   ([52-50305](https://toolsid.com/longacre/5-gal-horizontal-silver-lightweight-air-tank-mpn-52-50305.html)).
   It can't go on the 200 psi tank side, so it's a spare.
4. **The screw-set regulator is gone.** The fill valve meters air into the chambers against their
   transducers, so the pressure is set in software.
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
     open the rear face down through the fill, bleed and charge port. The 8 in keeps the rear controls
     where you asked for them.
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
8. **Two cannons stacked 3.8 mm apart** (80 mm between axes, was 164).
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
   - **Milton 1090-125** ASME reliefs ($16.87) go on each chamber and on the fill block. Their pull ring is
     the manual bleed. 125 psi is above the cap, so they never simmer, and under the tanks' and
     transducers' 200. This replaces the settled "150 psi chambers" for this valve.
   - CLAUDE.md lists "big direct-acting solenoid as the firing valve: too slow vs a piloted QEV" as a dead
     end. The SZW-25 is semi-direct, so it's slower. It's in because you asked for the old valves and it
     worked on the old cannon.
   - The simulation says a QE5 QEV ($51.75) between the chamber and the barrel, with the SZW-25 as its
     pilot, would be the biggest single gain if you want more range later.
10. **Air budget:** each 0.53 L refill takes about 5 psi out of the two 6 L tanks, so a 200 psi charge
    gives **about 20 full-power shots** (2 loaded plus about 18 refills). Lower settings give more.
11. **Chamber fittings: a 5-port brass block on the back of each chamber**, so nothing is drilled.
    - fill push-to-connect straight out the back;
    - 125 psi relief pointing outward;
    - 0-200 psi transducer to the side;
    - a plug in the last port.
12. **Check valves stay on the fill block**, one per cannon, so one shot can't vent the other chamber.
    Two nylon service loops run from there up to the gun and flex as it elevates. The sweep check skips
    them; give them slack when you route them.
13. **Firing valves switch on MOSFET modules, not relays,** to take the relay's ms off the shot. Add a
    flyback diode on each coil.
14. **Cradle:**
    - two 1/8 aluminum plates either side of the stack;
    - printed chamber saddles (one block between both pipes at each station) with a strap round each
      outer half;
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
    - With the barrels 3.8 mm apart, there's no room for a shaft between the chambers' couplings.
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
21. **LEDs backlight the panels.**
    - A channel runs down the middle of every frame member, right under the panel's overlap.
    - The strip lies flat in it, facing out, and shines straight into the back of the panel's edge band.
    - A 1.2 mm lip on the window side and the panel itself close the channel.
    - 12.4 m in all, so three 5 m reels.
22. **Frame:** 56 printed pieces, 60 tapered tenons with M4 cross screws, 40 corner clips. Six piece
    ends have no neighbour; they're open ends at the well.

## Layout
23. **The back tank moved to the right.** I read that as mirroring the left one, so both tanks lie along
    the sides over the front wheels, on cantilevered 1x1 arms with printed saddles and straps. No pump
    spot.
24. **Bottom of the rear panel:**
    - E-stop;
    - Schrader fill port (air in);
    - tank bleed lever;
    - SB50 charge port, to run or charge on standby power with the batteries in;
    - USB-C to the STM32.
25. **Rear manifold** (back bottom, left): tank lines, 200 psi relief, 0-300 psi transducer, and the line
    to the fill valve. The fill and bleed go straight out through the rear panel.
26. **Electronics in the back bottom bay:**
    - PDH and main breaker on the bellypan;
    - STM32, both ESP32-S3s, the PWM gate, the drivers, the buck and the Spark MAX on a printed shelf;
    - the fill valve and fill block beside them.
27. **Batteries:** one per side, each on its own sled over a rear wheel. Each slides out through its
    side's rear panel.

## Smoke
28. **Pick: AutoLine Pro HyperSmoke, a 12 V automotive EVAP smoke machine, $47.99**
    ([B0DNRY9NCV](https://www.amazon.com/dp/B0DNRY9NCV), 4.6 stars from 1.1K reviews, 2 bottles of fluid
    included).
    - Mains foggers need a ~$60 inverter and draw 35-40 A at 12 V, with a 4 min warm-up
      ([VIRFUN](https://www.amazon.com/dp/B081YNQG29) + [Ampeak](https://www.amazon.com/dp/B07PWDR869)
      = $99).
    - The $40 battery "foggers" are 80 g tabletop units
      ([StageFogger](https://www.amazon.com/dp/B0GVP7X53X)).
    - A car smoke tester is built to run off a 12 V battery. It warms up instantly, has its own air pump
      and pushes dense smoke down a hose, which is what the ducts need.
    - It's $8 over your $40. The in-budget option is the M-T at $39.99, rated 3.7 stars.
29. **The 12 V hack.**
    - Power it from a fused PDH channel.
    - Open it and put its heater and pump on two MOSFET channels from the STM32: the heater pre-heats,
      and the pump puffs on command.
    - Keep its thermal cutout.
    - Measure its current first; the MOSFET modules are rated 15 A.
30. **Fluid:** EVAP smoke is mineral-oil based, and baby oil is the cheap refill. Like any fogger, it can
    trip gym smoke detectors, and it leaves a film in tight spaces, so check with each venue.
31. **Ducts:**
    - A printed outlet adapter feeds a printed 1-to-4 splitter, then your four flexible tubes.
    - Two tubes go up to the vents in the gun's mantlet, between the barrels. They're service loops that
      flex with elevation.
    - Two go to vents under the front bumper, through holes in the bellypan.
    - The smoker's box in the CAD is a placeholder. Measure the real one and its outlet before printing
      the cradle and adapter.

## Things I'd flag
32. **Cost: $1,827.38.**
    - By section: gun $843, pressure side $344, controls $208, drive $130, frame and body $92, bumpers
      $89, elevation $74, smoke $48.
    - The chamber ($397) is the biggest line. The old tank's nameplate and a compressor-dealer or used
      price could cut most of it.
33. **Weight is about 146 lb** (66 kg); the gun is 13.6 kg.
34. **Check before ordering:**
    - the old valve's coil voltage and the old tank's nameplate;
    - the CPT44-5 pack count;
    - the Aignep coil and plug;
    - the smoker's size, current and outlet.
35. **The Onshape model is imported STEP** (dumb solids), with the gun posed at 20 deg. To change it,
    edit `cad/glacis`, run `python robot.py`, and replace the changed tabs.
