# Glacis rev B: judgment calls

Rev B (2026-11-02) is the redesign from your second round of notes: aluminum box tube, two barrels,
10 in wheels at 3 in clearance, a one-stage belt, a flat deck with leaning sides and one front slant,
the turret pushed back and lower, one tank on the left and one standing at the back, smaller
chambers, polycarbonate barrels, an FTC motor on a Spark MAX with a pot, the PDH, an STM32 with an
independent radio failsafe, every pressure read by the controller, recessed panels with corner clips,
and no liner. Each item says what I picked and why. Numbers come from `cad/glacis/params.py` and the
last clean run (`cad/glacis/out/check_log.txt`).

**Checks on the final model:** no part overlaps another, nothing hits anything as the gun sweeps 0-90
deg (checked every 5 deg), every printed part fits a 256 mm bed, and every part is a single solid.

**Where it is:** Onshape "Brophy Mark 5 - Glacis" (rev B tabs and the "Glacis rev B (whole robot)"
assembly). The parts list is the "Glacis BOM" tab: **$1,555.11** to buy (rev A was $2,102.30), with aluminum, acrylic, prints,
Falcons and standard FRC stash parts at $0.

## Size and shape
1. **37.7 L x 27.7 W in over the bumpers, deck 22.8 in high** (it was 29.3 in at the turret). With the
   gun level the muzzles reach 39.4 in overall; at 90 deg it is 37.8 x 27.8 x 43.3 in.
2. **One front slant at 70 deg** from the nose bumper straight up to the deck, as you asked. 70 is as
   shallow as it can be: the left tank's front end sits right behind it.
3. **Flat deck at one height, sides leaning in 6 deg.** The deck is 21 in wide at the top, so it is
   two panels split down the middle (each 25.7 x 10.4 in, L-shaped round the gun slot).
4. **9 panels total.** Front (one U-shaped sheet round the slot), deck x2, slot floor, left wall, right
   wall x2 (the rear one is the battery door), rear face, rear chamfer. The slot walls inside the turret
   have no panels.
5. **Turret pushed back 6.7 in** (pivot at x = -130 mm, was +40) and its top lowered from 29.3 in to
   the 22.8 in deck. At 0 deg the whole gun sits inside the slot, below the deck.

## Body frame (printed)
6. **Panels sit in a recess, not a groove.** Each 1/8 in panel drops into an 8 mm wide rebate, 2.5 mm
   below the face, and a printed clip in a flush pocket at every convex corner holds it (one M3 into a
   heat-set insert). 42 clips. Any panel comes off with its clips, which is also how the battery door
   works. Only corners are clipped, as you said; if a long edge rattles, add a mid-edge clip.
7. **LEDs:** a 2.6 mm slot right behind each panel at the window edge, 14.8 m in all (three 5 m reels).
8. **72 frame pieces with 81 tapered mortise-and-tenon joints** (6.5 mm tenons, M4 cross screws). Every
   piece fits a 256 mm bed. Where two recesses meet at a corner they leave thin strips; I delete those.
9. **Wall frame to chassis:** printed standoffs on the outer rails; the side-wall frame sits on their lip
   and screws down into them. Posts can't go up the outer rails any more because the walls lean in.

## Frame and drive
10. **1x2 and 1x1 x 1/16 aluminum box tube, 1/8 in gussets, 3/16 aluminum rivets** (McMaster 97447A050).
    U-shaped gussets top and bottom round each wheel end. Aluminum isn't on the parts list (you have it).
11. **One-stage belt, 10:1:** Falcon 12T (WCP-0319) on a 140T belt straight to a 120T printed into the
    wheel hub. The 120T is the biggest that leaves 1.1 in under the belt at the floor.
    - **Free speed is 27.8 ft/s**, so cap the drive in firmware (about 40% output gives 11 ft/s) and set
      a Talon FX supply current limit. Torque is plenty, as you said.
12. **10 in fully printed mecanum, 14 rollers** (78 mm long, 15 mm max radius; 6.9 mm between rollers,
    contact overlap +8%).
    - The hub is one PETG print, 243 x 246 mm, with the 120T pulley, both lug rings and a 1/2 hex bore.
    - **Two 1/8 in aluminum plates sandwich it** on 6 x M5 through-bolts; the inner plate is the belt's
      inboard flange.
    - Rollers: PETG core, TPU 95A tread, two 685ZZ bearings on an M5 x 100 axle each.
13. **Standard FRC axles:** a 1/2 in hex live axle per wheel in two flanged hex bearings (WCP-0783), one
    in the inner rail, one in the outer rail. Tapped 10-32 ends with button heads. Ground clearance is
    3 in at the bumpers; the bellypan is at 3.9 in.

## Gun and pneumatics
14. **Two stacked barrels, clear polycarbonate 3 in OD x 1/8 wall** (McMaster 8585K38, one 4 ft stick).
    - McMaster gives no pressure rating for it. Hoop stress from its 8,900 psi tensile is about 740 psi
      burst; the barrel only sees pressure for a few milliseconds behind the shirt.
    - The adapter clamps it; never drill polycarbonate.
15. **Smaller chambers, same place:** each chamber is now just a 4 x 3/4 bushing threaded into a 4 in cap
    (about 0.4 L, was 1.0 L), still sideways off the QE5. That drops the coupling and nipple, so each
    chamber is about $36 and much lighter. It stores about 40% of the old chamber's air, so bench-test
    the range; if shots fall short, a 4 in coupling and close nipple between bushing and cap doubles it.
16. **Why not copper or PVC:** PVC shatters into shrapnel under air pressure (OSHA has warned against it
    for compressed air since 1988), so it can't be on the pressure side. Copper works (2 in Type L
    soldered with 95/5 is rated well over 200 psi), but with the short chambers there's no long tube
    left to replace, so I kept threaded steel. Every air line is DOT nylon tube.
17. **The bottom barrel's QEV sits 30 mm ahead of the top one** (its barrel is 30 mm shorter so the
    muzzles line up). That keeps the two inlet blocks from facing each other.
18. **Each barrel's inlet pocket is one 5-port brass block** (Interstate CPT44-5, rated 1000 psi) right
    behind its QE5: VA-4 dump on one side, supply push-to-connect on the other, 150 psi relief outward,
    transducer inward. The gun now reaches only 3.5 in behind the pivot at 0 deg (it was 6.5 in), which
    is what lets the rear tank stand behind it.
19. **The relief's pull ring is each chamber's manual bleed** (Interstate V150-4, ASME). That replaces
    the separate ball valve and muffler per barrel.
20. **Check valves moved off the gun** to the fixed fill cross beside the pivot, inline in each barrel's
    tube (Conrader 250 psi; both lie horizontal, as that valve needs). Two flexible tubes run from there
    to the gun.
21. **Every pressure goes to the controller:** tank (0-300 psi), fill line (0-200 psi) and both chambers
    (0-200 psi), all 0.5-4.5 V into the STM32's ADC through dividers. The dial gauge is gone; with the
    power off, open the rear bleed and pull both chamber rings before working on it.
22. **150 psi at the chambers, 200 psi in the tanks.** The QE5 is rated 150 psi. McMaster lists its
    Class 150 malleable cap at 150 psi (ASME B16.3 rates Class 150 at 300 psi up to 150 F).
23. **Tanks:** your two AliExpress 6 L / 200 psi tanks.
    - Left: lying along the left side above the front-left wheel, on two cantilevered 1x1 arms with
      printed saddles and straps. Its front port is the future pump inlet.
    - Rear: standing in the rear centre on a printed cup on the bellypan, held by a half clamp and strap
      to the back of the left tower.
24. **Rear manifold** (left rear corner): tank lines, 200 psi relief, tank transducer, Schrader fill port
    and manual bleed through the rear panel, and the line to the fill valve.
25. **No onboard pump.** Its spot is in the front bay, lying flat (ZHSYMX, 243 x 128 x 181 mm).

## Elevation
26. **goBILDA 5203 Yellow Jacket 99.5:1 on a Spark MAX** (brushed mode, PWM from the STM32), 16T -> 56T
    on a 9 mm 145T belt (WCP), 3.5:1. About 17 rpm at the trunnion and 46 N*m stall; the gun needs at
    most about 10 N*m.
27. **Arm angle from a 10k pot** on the end of the left trunnion stub, read by the STM32 (it closes the
    position loop and sends the Spark MAX a PWM command).
28. **Towers are 1x1 on the inner rails**, the left one behind the pivot and the right one ahead of it,
    each with a printed bearing block and two flanged hex bearings.

## Electronics and power
29. **Batteries reachable:** both FRC batteries ride a printed sled over the rear-right wheel. Take the
    four clips off the right wall's rear panel and slide the sled out the side.
30. **Your PDH** in the middle bay with the 120 A main breaker; the fuse block is gone.
31. **STM32 Nucleo-F446RE is the main controller.** It does everything time-critical: drive mixing and
    PWM to the Falcons and Spark MAX, the valves, fill metering from the transducers, and the elevation
    loop. An ESP32-S3 is only the WiFi bridge for the web UI (WebSocket), talking to the STM32 over UART.
32. **Failsafe, independent of WiFi:**
    - A handheld safety remote (Adafruit ESP32-S3 Feather, E-stop button, dead-man trigger) talks to a
      separate ESP32-S3 safety node on the robot over ESP-NOW: direct radio between the two boards, no
      router or network.
    - The safety node holds the safety relay that feeds the 12 V valve rail, and the 74AHCT125 gate that
      passes PWM to the Falcons and the Spark MAX. No OK from it means no air valves and no drive.
    - It drops both if the remote's heartbeat stops for 200 ms, the remote's E-stop is pressed, the
      STM32's heartbeat line stops toggling, or the tank transducer reads over 210 psi.
    - The robot E-stop is wired in series with the safety relay coil, so it works with no software.
    - Firing needs two people: the web UI asks, and the remote's trigger must be held.
33. **ESP-NOW is still 2.4 GHz radio.** If you'd rather nothing wireless at all, the remote can use a
    tether cable on the same pins.

## Things I'd flag
34. **Cost: $1,555.11**, inside the $2,500 cap but still over the $1,000 aim.
    - By section: gun $595, pressure side $376, controls and failsafe $198, drive $130, frame and body
      $92, bumpers $89, elevation $76.
    - The biggest lines are the two tanks ($113), the QE5s ($104) and the polycarbonate tube ($84).
    - Most parts come from Amazon or McMaster. Three don't: the QE5 (TECO, because Amazon's Parker 0R75B
      is $125), the Aignep fill valve (Hose Warehouse; no 12 V, 200 psi direct-acting valve at McMaster or
      Amazon), and the safety-remote Feather and LiPo (Adafruit).
    - Check before ordering: the CPT44-5 port block listing may be a 5-pack, and the Bourns pot's travel.
35. **Weight is about 144 lb** (65 kg), down from 211. The gun is 17 kg.
36. **Fitting sizes are catalog-typical** and the 4 in listings publish no OD, so check the cap and
    bushing in hand before printing the trunnion cap hub.
37. **The Onshape model is imported STEP** (dumb solids). To change it, edit `cad/glacis` and re-run
    `python robot.py --export`, then replace the changed tabs. The gun is posed at 20 deg.
38. **Old T-shirt cannon:** once you send its parts list, anything it has (tanks, valves, gauges,
    fittings) comes off this list.
