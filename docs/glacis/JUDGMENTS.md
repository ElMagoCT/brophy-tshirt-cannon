# Glacis: judgment calls

Decisions I made while turning the Glacis concept into a full design (2026-11-02). Each says what I
picked, why, and what you'd change to undo it. Numbers come from `cad/glacis/params.py` and the last
clean run (`cad/glacis/out/check_log.txt`); part facts were checked live on 2026-11-01/02 (links in the
"Glacis BOM" tab of your parts sheet).

**Where it is:** Onshape "Brophy Mark 5 - Glacis" (12 Part Studios plus the "Glacis (whole robot)"
assembly, 561 parts). The parts list is the "Glacis BOM" tab: **$2,102.30**, owned items at $0.

**Checks on the final model:** no part overlaps another, nothing hits anything as the gun sweeps
0-90 deg, every printed part fits a 256 mm bed, and every part is a single solid.

## Size and shape
1. **Under 28 in wide:** 27.7 in over the side bumpers (27.8 in counting the axle bolt heads). The
   body is 37.7 in long over the bumpers. Level, the barrels stick out past the nose (47.0 in overall),
   so take it through doors with the gun at 90 deg: 37.8 L x 27.8 W x 47.5 H in.
2. **Side walls run straight to the nose**, and the front is one sloped glacis panel. The inside of the
   turret (slot walls and slot rear) has no panels, as you asked.
3. **Panels only split where a face can't take an 18 x 36 sheet.** That only happens on the side walls
   (one seam each, at the tower). 15 panels total.

## Body frame (printed)
4. **The printed frame comes from the body itself.** It's the body shelled 22 mm inward, with a window
   wherever a panel shows. Every member's faces lie on its panels' planes, so the grooves come out at
   the right angle.
5. **Groove:** 1/8 in acrylic sits 8 mm deep in a 3.6 mm groove behind a 2 mm lip.
6. **LEDs stand on edge in a 2.6 mm slot on the window edge** and shine across the back of the panel.
   I first had a flat 12 mm channel behind each panel edge, but two of them met at every corner and
   cut the 18 mm member in two along its whole length.
7. **Joints: tapered mortise and tenon, 98 of them.**
   - The tenon is 6.5 mm square, tapers 0.5 mm per side over 12 mm, and takes one M4 cross screw.
   - I shrank it from 8 mm so there's 1.8 mm of wall between the mortise and both the groove and the
     LED slot.
   - The frame is 87 pieces.
   - Where two grooves meet at a corner they leave 2 mm loose strips. I delete those (each is under
     2% of its piece).
8. **Print bed assumed 256 mm** (X1/P1 class). There are 320 printed parts from 113 designs. With a
   bigger bed, raise `PRINT_MAX`/`seg_max` and `N_ARCS` and the piece count drops.
9. **Frame to chassis:** printed posts on the outer rails, with the side-wall frame bolted to their
   outer face (2 x M4 into heat-set inserts). The side walls start 1.5 mm above the bumpers so the
   bumper cover's top lip slides under them.

## Drive
10. **Two-stage belt, 40:1, 8.4 ft/s free.**
    - Falcon 12T (WCP-0319) drives a printed 72T on an 80T belt.
    - A printed 18T on the same compound drives a printed 120T on a **150T belt** (it was 140T).
    - The longer belt puts the compound pulley and its nut outside the wheel's swept circle. With
      140T the rollers would have hit it.
    - Both belts are stock WCP sizes, so the centres are exact and need no tensioners.
11. **Compound pulley:** one print, with an FR8 and an R8 pressed into the 72T from its inboard face,
    running on a dead 1/2-13 x 4 in bolt. The 18T is too small to hold a bearing.
12. **12 in printed mecanum with 16 small rollers** (82 mm long, 17 mm max radius). It was 14 large
    ones, which touched their neighbours and swept 99 mm wide, past the pulley on one side and the
    rail on the other.
    - The new rollers leave 4.9 mm between neighbours and overlap their contact by 7%.
    - The wheel sweeps a 78 mm band.
    - Each roller has two 685ZZ bearings on an M5 x 100 axle, with a TPU tread over a PETG core.
13. **Wheel hubs print as a core plus four lug arcs per side**, because a one-piece 12 in hub is 286 mm
    across. The inner core is the 120T pulley. Each arc screws to its core with 2 x M4 into heat-set
    inserts, and the 16 roller axles tie the inner and outer arcs together.
14. **Dead 1/2-13 x 8 in axle** through both 1x2 rails (drill the rails). The bolt heads sit in pockets
    in the bumper backing; at axle height the noodles curve away, so they clear.
15. **Set the Talon FX supply current limit once in Phoenix Tuner** (it saves to the motor). CTRE doesn't
    say outright that a saved limit applies under plain PWM, so check it with a clamp meter.

## Gun and pneumatics
16. **150 psi at the chambers, 200 psi in the tanks.** The QE5 is rated 1-150 psi (on TECO's spec
    table), and no in-stock 3/4 or 1 in NPT quick exhaust valve goes above that except a $305 stainless
    Versa (175). Everything else on the gun is rated at least 200, so a better valve can drop in later.
17. **QEV: Humphrey QE5 3/4 NPT, $51.75.** Your eBay XQ172500 has PT/BSPT threads and is rated 145 psi.
18. **Firing pilot: HornBlasters VA-4** (210 psi), with a check valve per barrel. **Fill/metering:
    Aignep 02F direct-acting** (580 psi body), $41.36 at Hose Warehouse instead of $62 at Global
    Industrial. Confirm the coil and DIN plug come with it.
19. **The QEV ports set the layout.** The inlet and exhaust share an axis and the cylinder port is on
    the side, so each ~1.0 L chamber runs sideways from the gun:
    - 3/4 close nipple, 4 x 3/4 bushing, 4 in coupling, 4 in close nipple, 4 in cap.
    - The chambers alternate sides.
    - Each 4 in stack costs $130.10, and the coupling alone is $54.
20. **The middle chamber is the left (+y) trunnion.** A printed hub clamps its cap and carries a hex stub
    into the left bearing block. The right stub passes between the top and bottom chambers and carries
    the elevation pulley. (Earlier notes had left and right swapped.)
21. **Each barrel's safety sits in its inlet pocket** (between the check valve and the QEV): a 150 psi
    relief, a manual bleed ball valve and a muffler. The chamber can't rise above its inlet pocket
    without the QEV venting it out the barrel. Opening a bleed fires that barrel without a shirt, so
    point it up first.
22. **Manifolds are built from rated 1/4 NPT brass crosses** (1200 psi, about $4 each) joined by close
    nipples: 2 crosses on the gun and 3 at the rear. Rated brass manifold blocks were $145-159 each.
    The CAD still draws them as blocks.
23. **Supply lines:** a swivel-elbow push-to-connect on each barrel's check valve keeps every gun tube
    within 80 mm of the centre line, clear of the pump spot as the gun swings.
24. **Barrels: 3 in OD x 1/16 in wall** (WCP-1275, two 23.5 in barrels per 47 in stick). That's about a
    fifth of the weight of 3.5 in x 0.5 in wall.
25. **Tanks: your two AliExpress 200 psi tanks** (the listing says 6 L / 1.6 gal, not 2 gal). They're
    stacked across the rear in printed ring cradles that sit on the 1x1 rack, strapped down at +/-140 mm.
26. **No onboard pump.** Precharge from a shop compressor; most top out at 135-175 psi.
    - **Pump spot:** the ZHSYMX (243 x 128 x 181 mm) stands in the left turret half *behind* the pivot.
    - Its first spot, in front of the pivot, overlapped the middle chamber.
    - The upper tank's spare port is the future pump inlet.
27. **Liner:** a fabric sheet clamped inside the frame behind every panel except the glacis and the slot
    floor. 1050D ballistic nylon is $15.33/yd and 3 yd covers it; denim works too. Neither is rated to
    stop fragments, so it backs up the relief valves rather than replacing them.

## Elevation
28. **Your FEETECH STS3215 servos on a 16T -> 56T 9 mm belt**, on the right trunnion. That's 3.5:1,
    about 20 N*m from the two. The gun needs 4.7 N*m at 0 deg because it's balanced on the pivot.
    - The servos' own encoders give the angle in multi-turn mode, so the AS5600 is dropped.
    - Add the $5 Waveshare bus adapter.
    - The pinions are placed so the belt loop is exactly 575 mm, a stock 115T belt (WCP-0629). Slot one
      servo's mounting holes a few mm for tension.
29. **Towers sit just ahead of the pivot bearings**, and the printed bearing blocks bolt to their back
    face. Behind the pivot, the bearing would have stuck into the tower.

## Electronics and power
30. **Two FRC batteries side by side** in a printed cradle on the bellypan, wired in parallel through
    two Anderson SB50s. The SB50s sit ahead of the battery cross member.
31. **Electronics in the front bay under the glacis.**
    - The bay holds the power distribution, main breaker, ESP32-S3, relays, 5 V buck, bus adapter,
      ADS1115 and fuse block.
    - **The E-stop is on the rear face, upper right**, beside the tank gauge, fill port, bleed lever
      and USB-C. On the rear deck its body would have sat on the upper tank.
32. **LEDs:** 18.7 m of strip (four 5 m reels, 1,122 LEDs). Cap the brightness in firmware so it stays
    inside the 20 A buck.

## Bumpers
33. **FRC style on all four sides:** two 2.5 in pool noodles stacked on a printed backing (sectioned,
    bolted to the rails with 1/4-20), your white canvas over them, mitred at the corners, 4 in to 9 in
    off the floor.

## Things I'd flag
34. **Cost is $2,102.30, under the $2,500 cap but not near $1,000.**
    - The gun is $931 of it, and each extra barrel is about $261.
    - Building one barrel first brings it to about **$1,526**; the space and plumbing for barrels 2 and
      3 stay.
    - The aluminum sheet is at $0 on your note that the stash has it. If it doesn't, add about $200
      for four 12 x 24 sheets.
    - Yesterday's cut list had $7 QWORK CA7109 horn valves (200 psi NC). Using them for the three dumps
      would save about $76, but bench-test that they fire the QE5 cleanly first.
35. **Weight is about 211 lb** (95.8 kg). The gun is 39.5 kg of that, mostly the 4 in malleable
    chambers. Smaller chambers or fewer barrels save the most.
36. **Fitting sizes are catalog-typical** and none of the 4 in listings publish an OD, so the model can
    be off by a few mm. Check the 4 in fittings in hand before cutting the cradle plates, and measure
    the muffler length (the CAD assumes 22 mm).
37. **The Onshape model is imported STEP** (dumb solids), not Onshape features. To change it, edit
    `cad/glacis` and re-run `python robot.py --export`, then replace the changed tabs. The gun is posed
    at 20 deg.
