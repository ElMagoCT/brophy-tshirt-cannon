# Glacis rev C: judgment calls

Rev C (2026-11-02) is the redesign from your third round of notes:
- both chambers on the back of their cannons, in line;
- the gun balanced on an axle that runs between the two cannons;
- the old cannon's firing valve and chamber, plus one more of each;
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
robot)" assembly (484 parts). The parts list is the "Glacis BOM" tab: **$1,888.23** to buy (rev B was
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
2. **Chamber: a grey primed-steel ASME air tank with a 1 in NPT end port.** The "Tighten All Plugs"
   label is the kind these tanks ship with. Confidence is low to medium.
   - I sized it from video frames as the 1 gal, 6 x 11 in, 200 psi tank (Manchester 304978 class).
     The research pass guessed 8 in across, which would be 2-3 gal.
   - The buyable twin is **McMaster 9888K9, $397.34**: 1 gal, 6 x 11-3/4 in, 200 psi. It has one 1 in,
     four 3/4 and two 1/2 NPT ports, plugs included ([link](https://www.mcmaster.com/9888K9/)).
   - **Read the old tank's nameplate before ordering.** The same tank from a compressor dealer, or used,
     should be far cheaper; I found no live price for the Manchester.
   - If it turns out to be bigger, change `CH_D`/`CH_L` and its mass. The gun re-balances itself, and
     the checks will show whether the well still clears.
3. **Longacre 5 gal polished aluminum tank:** rated 125 psi
   ([52-50305](https://toolsid.com/longacre/5-gal-horizontal-silver-lightweight-air-tank-mpn-52-50305.html)).
   It can't go on the 200 psi tank side, so it's a spare.
4. **The screw-set regulator is gone.** The fill valve meters air into the chambers against their
   transducers, so the pressure is set in software.
5. **Red "5 in ONE Universal" couplers:** brand and rating not confirmed, so they stay off the pressure
   side.

## Gun
6. **Two cannons stacked, the axle between them.** Each one, back to front: chamber tank -> 1 in close
   nipple -> SZW-25 -> close nipple -> CNC breech adapter -> clear polycarbonate barrel.
   - The breech adapter is stash 6061 bar with a 1 in NPT tap ($16.99 tap on the list).
   - The chambers sit on the back of the cannons, in line, as you asked. Their axes are 164 mm apart.
7. **Balanced on the axle.** The model takes every part's mass, finds the gun's centre of mass and
   slides both cannons along the barrel axis until it lands on the axle.
   - Result: valves 61 mm ahead of the axle, centre of mass within 0.2 mm.
   - The gun weighs 13.6 kg, so it needs **0 N*m to hold at any angle**.
   - The valve (1.0 kg) and tank (2.7 kg) masses are estimates. Weigh yours, update them in `gun.py`,
     and re-run before cutting the cradle plates.
8. **Pressures: 110 psi software cap on the chambers, 125 psi relief, tanks at 200.**
   - 110 psi sits just under the valve's 115 psi DC rating. Above that, the coil may not lift the
     valve; it fails closed, not open.
   - **Milton 1090-125** ASME reliefs ($16.87) go on each chamber and on the fill block. Their pull
     ring is the manual bleed.
   - 125 psi is above the cap, so they never simmer, and well under the tanks' and transducers' 200.
   - This replaces the settled "150 psi chambers" for this valve.
9. **The trade-off you're taking on.** CLAUDE.md lists "big direct-acting solenoid as the firing
   valve: too slow vs a piloted QEV" as a dead end.
   - The SZW-25 is semi-direct, so it opens slower than a QEV: tens of ms against about 10.
   - You said it worked on the old cannon, and you asked for the same valves, so it's in.
   - The 1 gal chamber holds about 7 times the air of rev B's 0.4 L at 150 psi, which makes up range.
   - If the shots fall short, a QE5 QEV ($51.75) can go between the chamber and the barrel later and use
     the SZW-25 as its pilot.
10. **Air budget.**
    - Each refill of a 1 gal chamber from empty to 110 psi takes about 35 psi out of the two 6 L tanks.
      Starting at 200 psi, that's 2-3 refills before the tanks drop below 110.
    - That's about **4-5 full-power shots per shop-compressor charge**: 2 loaded, plus 2-3 refills.
      Lower settings give more.
    - The old cannon's 5 gal tank at 125 psi held about the same air.
11. **Chamber fittings, on each tank's outward side:**
    - fill push-to-connect elbow;
    - 125 psi relief;
    - 0-200 psi transducer;
    - each on a 3/4 x 1/4 bushing, with the spare ports plugged.
12. **Check valves stay on the fill block**, one per cannon, so one shot can't vent the other chamber.
    Two nylon service loops run from there up to the gun and flex as it elevates. The sweep check skips
    them; give them slack when you route them.
13. **Firing valves switch on MOSFET modules, not relays,** to take the relay's ms off the shot. Add a
    flyback diode on each coil.
14. **Cradle:**
    - two 1/8 aluminum plates either side of the stack;
    - printed chamber saddles and straps, valve side blocks and breech blocks;
    - a printed mantlet carrying the smoke vents and an LED groove;
    - LED-groove muzzle rings.

## Elevation
15. **The 60 rpm motor is the goBILDA 5203 99.5:1.** It drives a 16T -> 56T HTD 9 mm belt (100T) to
    the right end of the axle.
    - That's about 17 rpm at the gun, so 0-90 deg takes about 0.9 s at full speed.
    - The gun is balanced, so the motor only fights friction and inertia. It has 46 N*m stall at the
      axle.
16. **One 1/2 hex steel axle** runs through both cradle plates, between the cannons.
    - It sits in four flanged hex bearings, in two PA-CF blocks on 1x1 towers on the inner rails.
    - The arm-angle pot is on the left end through a printed coupler.
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

## Wheels (from your vector-wheel file, TTB-0010)
32. **Same style as your TTB wheel, scaled to 10 in.**
    - 10 rollers, 42 mm across and 104 mm long (rev B had 14 at 30 mm).
    - A lobed hub rim with a printed cup round each roller end, like the TTB's hooked lugs.
    - One change: the rollers keep a true mecanum barrel profile instead of the TTB's straight
      cylinders. At 10 in, a straight roller rides on its corners and the wheel bumps.
    - Coverage +6%, with 5 mm between neighbouring rollers.
33. **Rollers on 608 2RS and a fixed M8 rod.**
    - PETG-CF core, 3 mm TPU 95A tread (1.8 mm at the ends), a 608 pressed 8 mm into each end.
    - The rod doesn't turn; the bearings do. It threads through a captured M8 nyloc in the outboard
      cup (Loctite 243) and bottoms in a blind hole in the inboard cup. The outboard plate covers the
      nut channels, so a rod can't back out.
    - Each cup's stub sits in the roller's end recess and presses only on the bearing's inner race.
    - Nuts, not tapped aluminum: the rods sit at 45 deg to the plates, so a flat plate can't be
      tapped square to them.
    - To change a roller: take off the outboard plate (8 nuts), unscrew the rod by a slot cut in its
      end, and the roller drops out.
34. **Hub: two halves, as big as the bed allows.**
    - Split at the roller centre plane. Each half is 242 mm across and prints face down.
    - The bed would take 250 mm, but the rim stops 6 mm inside the tread so it never touches the floor.
    - Each half is a lobed face web, a drum ring, 6 spokes and a 1/2 hex boss.
35. **Aluminum: 12 flat 1/8 in plates (waterjet), three per wheel.**
    - The inboard plate is the belt's inner flange.
    - A centre disc sits between the two halves.
    - The outboard plate is lobed, the same shape as the rim.
    - 8 x 1/4-20 x 5-1/2 in bolts clamp the stack (M6 x 130 fits the same holes). The plates' hex holes
      put the wheel load on the axle through aluminum, not plastic.
36. **Pulley: 116T HTD 5M, 15 mm, printed into the inboard half.**
    - Its flange is 1.27 in off the floor. 118T would be 1.20 in.
    - 9.67:1 from the Falcon's 12T (was 10:1); free speed 28.8 ft/s.
    - The stock 140T belt still fits; the Falcons now sit 169 mm from the axle.
37. **Load.** Two 608s per roller rate 2.7 kN static. At 69 kg, a wheel carries about 170 N standing
    and about 500 N on a 3 g bump, often all on one roller: over 5x margin. The printed cups are the
    weakest link, and the plates and bolts carry their load to the axle.
38. **The cost of the width.**
    - Each wheel is 120 mm wide (rev B 94). The outer rails stay put (27.7 in over the bumpers), so
      the inner rails and Falcons moved 26.5 mm inboard: the inner rails are now 104-129 mm off centre.
    - The electronics shelf narrowed to +/-100 mm, with the boards rearranged on it.
    - The fill block moved 25 mm inboard, clear of the rear-left wheel.
    - The tank lines now run inboard of the rail posts.
    - The pivot bearing blocks follow the rails and are now 20 mm wide (was 47); both flanged hex
      bearings still fit, and the pivot axle is 53 mm shorter.
39. **Weight: 3.3 kg a wheel** (rev B 2.4), so +3.6 kg for four.
40. **Cost: +$60.85.** The 608s, rod, nylocs, bolts and Loctite replace the 685ZZ and M5 lines. The
    Bolt Depot prices are from search snippets, so check stock when you order.

## Things I'd flag
41. **Cost: $1,888.23.**
    - By section: gun $843, pressure side $344, controls $208, drive $191, frame and body $92, bumpers
      $89, elevation $74, smoke $48.
    - The chamber ($397) is the biggest line. The old tank's nameplate and a compressor-dealer or used
      price could cut most of it.
42. **Weight is about 151 lb** (68.6 kg, with the new wheels); the gun is 13.5 kg.
43. **Check before ordering:**
    - the old valve's coil voltage and the old tank's nameplate;
    - the CPT44-5 pack count;
    - the Aignep coil and plug;
    - the smoker's size, current and outlet.
44. **The Onshape model is imported STEP** (dumb solids), with the gun posed at 20 deg. To change it,
    edit `cad/glacis`, run `python robot.py`, and replace the changed tabs.
