"""Brophy Borealis parts list (was Glacis; rev D.2.1 2026-11-09, Borealis changes 2026-11-10): source of the two order
tabs in the parts-list Google Sheet ("Borealis Order 1" and "Borealis Order 2").

    python glacis_bom.py            # writes glacis_bom.csv and glacis_bom_sheet.json (rows for both order tabs)

Two orders (Micah, 2026-11-10): Order 1 is the pneumatics, the important electronics and the speakers; Order 2 is the
materials, the LEDs and the smoke. ORDER_OF maps each section to its order.

Row = (name, seller, qty, unit $, link, type, purpose, notes). A row with qty None is a section header.
Quantities come from cad/glacis/out/parts_from_cad.csv. Sellers: McMaster, Amazon and AliExpress first.
Prices were read on 2026-11-01/02 (L = live page, S = search snippet). Aluminum (box tube, sheet, bar),
acrylic, prints, Falcons and standard FRC stash parts are $0 or left off. Rev C reuses the old cannon's
firing valve and buys one more; the chambers are 2 in pipe (0.53 L each). Rev C.2 (2026-11-03): a main valve and
one in valve per chamber replace the fill block and check valves; a 60/m LED loop behind each panel and 100/m strip
through the frame; two slim siren speakers in the front corners with their amp. Then Micah's picks from the savings
list: a U.S. Solid second firing valve, a Black Pill STM32, his own ESP32-S3s and goBILDA, crosses for the chamber
blocks, printed chamber caps, one fog core with room for a second, cheaper bumper and boost parts.
"""
import csv
import json
import os

D = "2026-11-02"
V = "2026-11-06"   # rev D.2 listing check
B2 = "2026-11-09"  # Brophy Borealis listing check
W = "2026-11-09"   # rev D.2.1: Waveshare controller, speaker tap, battery relays
STASH = "Standard FRC stash part; buy only if the stash is out"
OLD = "From the old cannon"
ROWS = [
    ('PRESSURE SIDE - tanks, rear manifold, main valve and in valves (200 psi)', None),
    ('Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT, aluminum (your pick)', 'Aliexpress', 2, 56.6, 'https://www.aliexpress.us/item/3256804024554756.html', 'Motion', 'Two, 12 L: left and right over the front wheels. The CAD test-fit found no room for a third alongside them; 9-15 shots at 120 ft per 150-200 psi charge with a fast top valve, 6-10 with a slow one', '200 psi, 1/4 NPT female bungs (photos: 2 along the side, one in an end); it ships with welded feet the CAD saddles ignore. $56.60 list; a $46.81 welcome deal shows for new shoppers. 4.9 stars, 90 sold (2026-11-06, L)'),
    ('Relief valve 200 psi, 1/4 NPT male, ASME, ring pull, brass, 2-pack (Loner ST25-1A200, B0F4QP9CG2)', 'Amazon', 2, 12.99, 'https://www.amazon.com/dp/B0F4QP9CG2', 'Motion', "Tank zone (rear manifold; its ring at the rear panel is the hand dump), the valve cross, and the cross after each in valve on the chassis (its ring is that chamber's bleed)", "ASME, 200 psi set, 1/4 MNPT, stainless pull ring, 178 cfm; was McMaster 48435K72 4 x $6.67 (Amazon/Ali only, Micah 2026-11-10). Only 8 packs left (2026-11-10, Kenzo's list, re-checked L)"),
    ('Pressure transducer 0-300 psi, 0.5-4.5 V, 5 V, 1/8 NPT, stainless, with plug cable (pick "1set-300PSI")', 'Aliexpress', 3, 6.08, 'https://www.aliexpress.us/item/3256812969389519.html', 'Electrical', 'One part number for all three: the tank, and one per chamber on the chassis cross after its in valve (Brophy Borealis compact gun), so no sensor wires cross the pivot. Fill in short pulses and read between them: the hose reads a little high while air is flowing. +$1.99 shipping', 'Universal 5 V sender, 30-1000 psi options, connector included; 3K+ sold, 4.8 stars, $10.69 (2026-11-09, L). Was the FUSCH on Amazon at $17.69 each (B0CRQWKDNC). Check the 0.5-4.5 V output on the option page before ordering'),
    ('Quick disconnects: 1/4 NPT female M-style couplers, brass, 300 psi, 5-pack (RUBY.Q B0BPXT6V2F)', 'Amazon', 1, 9.99, 'https://www.amazon.com/dp/B0BPXT6V2F', 'Motion', "The 5 interior quick disconnects: tank line to the main valve, rear manifold to each in valve (2), each chassis cross to its chamber hose (2). Couplers have the shut-off, so they go on the supply side; the fifth threads straight onto the port that the old kit's F x F coupling + male-thread coupler sat on", "300 psi working; with the plugs below replaces the $27.98 Lnrueg 45-pc kit (2026-11-10, Kenzo's list, re-checked L)"),
    ("QD plugs + fill plug: 1/4 NPT FEMALE-thread M-style plugs, brass, 10 pcs (ZKZX B081F9J3VF, pick 'Female NPT')", 'Amazon', 1, 8.99, 'https://www.amazon.com/dp/B081F9J3VF', 'Motion', '6 used: the fill plug outside the rear panel (on the 1-1/2 in nipple; your universal couplers snap on) and one per interior QD. Still an open plug, so the check valve behind it stays', "Kenzo's pick was the Male NPT option, which doesn't thread onto the nipples; no psi on the listing (the couplers are the 300 psi parts) (2026-11-10, Kenzo's list, re-checked L)"),
    ('Fill check valve, 304 stainless, 1/4 NPT male x male (your AliExpress pick)', 'Aliexpress', 1, 7.36, 'https://www.aliexpress.us/item/3256809743394012.html', 'Motion', 'Behind the panel, between the female elbow and the street elbow. Holds the tanks shut when the hose comes off (the plug is an open pipe). No pressure rating listed, so leak-test it at 200 psi with soapy water', "Male on both ends (listing photo), not FNPT x MNPT as an older note hoped. The listing gives no pressure rating (an older note's '250 psi, brass' was a different valve), so leak-test it at 200 psi before it holds air. Fit it with the flow arrow pointing in (2026-11-06, L; note corrected 2026-11-11)"),
    ('In valves: GOGO GPG-M03 2/2 NC direct-acting 12 V DC, G1/4 (BSPP), 2.5 mm, 0-35 bar (option 1/4", DC12V, 2.5mm 35bar)', 'Aliexpress', 2, 24.23, 'https://www.aliexpress.us/item/2251801845365429.html', 'Structure', 'One in valve per chamber, metering it against the transducer on its chassis cross; they hold tank pressure all session. G1/4 ports: a G1/4 x 1/4 NPT adapter with a bonded seal in each (rows below). Flow arrow toward the chamber; soap-test at 200 psi', "GOGO Automatic Company Ltd. (GOGO's own store), 290 sold. $18.22 each + $12.01 shipping split over the two, logged-in price. Brass, NBR seal, DIN plug; body 40 x 26 mm, 76 mm tall, 82 mm long with the plug, 2 x M5 x 8 mounting holes underneath. Coil power not listed (likely 15-20 W: fine on its 15 A MOSFET channel). Replaces the Aignep 02F ($41.36 at Hose Warehouse, 2 mm), Micah's pick (2026-11-10, L)"),
    ('Adapters: G1/4 BSPP male x 1/4 NPT male hex nipple, 304 stainless (pick "G1/4 BSPP / 1/4 NPT / Male to male")', 'Aliexpress', 4, 3.19, 'https://www.aliexpress.us/item/3256808338257876.html', 'Structure', 'Both ports of both in valves: inlet to its QD plug, outlet to its chassis cross. They take the place of 4 close nipples. Bonded seal on the G1/4 side, sealant on the NPT side only', 'China Pneumatic Factory Store, 386 sold. $1.77 each + $5.69 shipping split over the four, logged-in price (2026-11-10, L)'),
    ('Bonded seals: self-centering NBR, 14 mm (fits G1/4), 20 pcs (pick "14mm")', 'Aliexpress', 1, 4.77, 'https://www.aliexpress.us/item/3256801441120875.html', 'Structure', "One under each adapter's hex at the in valve ports (4 of 20): G1/4 is a parallel thread, so it seals on the face, not the thread", 'SOREKARA, 317 sold, 5.0 stars. $2.78 + $1.99 shipping; the $1.09 it shows is a new-shopper price (2026-11-10, L)'),
    ('1/4 NPT brass cross (4-way), 3-pack (ChillWaves)', 'Amazon', 2, 12.99, 'https://www.amazon.com/dp/B0FCMV6ML9', 'Motion', "Rear manifold, the valve cross, and one on the chassis right after each in valve: its chamber's transducer, relief and hose out (moved off the gun, Brophy Borealis)", 'NPT, 1200 psi (2026-11-02, L)'),
    ('1/4 NPT brass close nipple, 5-pack, 250 psi (FLOFLEX B0CRVX12WC)', 'Amazon', 1, 6.99, 'https://www.amazon.com/dp/B0CRVX12WC', 'Motion', "2 used (CAD count, Brophy Borealis): one joining the rear manifold's two port blocks, one between the main valve's street elbow and the ball valve. The in valves' ports take the G1/4 adapters, which screw straight into the valve cross and the chamber crosses, so one pack is enough (3 spare)", "250 psi rated, 1/4 MNPT both ends; was Legines $7.99 (2026-11-10, Kenzo's list, re-checked L)"),
    ('1/4 NPT brass 90 deg elbow, FNPT x FNPT, 2-pack (ChillWaves B0B7544Y62)', 'Amazon', 1, 6.39, 'https://www.amazon.com/dp/B0B7544Y62', 'Motion', 'Fill line behind the panel: the nipple in one side, the male x male check valve in the other (1 spare)', "1/4 NPT female both ends, barstock brass, 1,200 psi; now $6.39, only 8 left (2026-11-10, Kenzo's list, re-checked L)"),
    ('1/4 NPT brass street elbow 90 deg, MNPT x FNPT, 2 pcs (CX Wonderland B0BCZFCFQ7)', 'Amazon', 1, 7.49, 'https://www.amazon.com/dp/B0BCZFCFQ7', 'Motion', '2 used: main valve off the rear manifold, and the check valve into the rear manifold', "Brass, 1/4 MNPT x 1/4 FNPT; no psi on the listing (the old 5-pack had none either); was $11.99 for 5 (2026-11-10, Kenzo's list, re-checked L)"),
    ('1/4 NPT plug, 304 stainless, hex socket, 10 pcs (Neprift B0H6X8VCSZ)', 'Amazon', 1, 7.99, 'https://www.amazon.com/dp/B0H6X8VCSZ', 'Motion', 'Every open port (rev D.2 audit): 2 rear-manifold ends + up to 3 spare bungs per tank (photos show 3-4 ports; one is the outlet) = 8 of 10. The valve cross and the chassis crosses have no open port', "8 used, 2 spare; one 10-pack instead of two brass 5-packs ($15.98) (2026-11-10, Kenzo's list, re-checked L)"),
    ('1/4 NPT male x 1/8 NPT female hex bushing, brass, 5 pcs (Litoexpe B0BFW3Q864)', 'Amazon', 1, 5.49, 'https://www.amazon.com/dp/B0BFW3Q864', 'Motion', '3 transducers', "1200 psi rated; was McMaster 9151K91 3 x $2.16 (2026-11-10, Kenzo's list, re-checked L)"),
    ('DOT nylon air-brake tube 1/4 in OD, SAE J844 PA12, 35 ft, with cutter (Boeray B0CYFWGSYS)', 'Amazon', 1, 11.99, 'https://www.amazon.com/dp/B0CYFWGSYS', 'Motion', 'Every air line, including the two service loops to the gun (about 15 ft used)', "500 psi working, 4.35 mm ID; 10 ft more than the old 25 ft roll for less (2026-11-10, Kenzo's list, re-checked L)"),
    ('DOT push-to-connect 1/4 tube x 1/4 NPT male, straight, 10-pack (Boeray)', 'Amazon', 2, 19.99, 'https://www.amazon.com/dp/B0D8PX7Z94', 'Motion', '16 used: both halves of the 5 quick disconnects (10), rear manifold (2), main valve, valve cross, and the hose out of each chassis cross (2). One row now: the quick-disconnect row was the same listing', '1/4 tube x 1/4 NPT male, 250 psi, SAE J1131 + J844, brass; 18 left (2026-11-06, L)'),
    ('DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT, 5-pack (Boeray)', 'Amazon', 1, 17.99, 'https://www.amazon.com/dp/B0D8Q2618F', 'Motion', '4 used: the two tank outlets and the two chamber inlets (in the weld-on bungs, pointing at the pivot); 1 spare', '1/4 tube x 1/4 NPT male, 250 psi, SAE J1131 (2026-11-06, L)'),
    ('Pipe thread sealant, RectorSeal T Plus 2 (B0002YPAFY)', 'Amazon', 1, 8.78, 'https://www.amazon.com/dp/B0002YPAFY', 'Tool', 'Every NPT joint', "Skip it if you have pipe dope or PTFE tape (Home Depot's $4.25 isn't one of your sellers) (2026-11-04, L)"),
    ('1 in cam-buckle strap 1 m, 4-pack', 'Aliexpress', 1, 5.2, 'https://www.aliexpress.us/item/3256813026868231.html', 'Structure', '4 used: two per side tank', 'Free shipping; 12 sold, 5 stars. Was $8.99 on Amazon (2026-11-04, L)'),
    ('Main valve: 1/4 NPT brass ball valve, FNPT x FNPT, 600 WOG, 2-pack (B0FKHG6VVT)', 'Amazon', 1, 15.99, 'https://www.amazon.com/dp/B0FKHG6VVT', 'Motion', 'Manual tank shut-off (rev C.3): open for a session, closed for transport and before working on the gun; handle at the rear panel', "You don't have one (Micah, 2026-11-11), so it's a buy: heavy-duty brass, female both ends, 600 WOG (over 4 x the 190 psi it sees); 4.5 stars. One spare (2026-11-11, L)"),
    ('1/4 NPT brass nipple 1-1/2 in, male x male, 1200 psi, 2-pack (B0747JC92M)', 'Amazon', 1, 7.49, 'https://www.amazon.com/dp/B0747JC92M', 'Motion', "Through the rear panel: the female plug outside, the female elbow inside. A check valve's 10 mm male end is too short to cross the panel itself", "You don't have one (Micah, 2026-11-11), so it's a buy; 4.7 stars. One spare (2026-11-11, L)"),

    ('GUN - welded 3 in pipe chambers (Brophy Borealis): top 1.56 L, bottom 1.32 L, both on HSV04 valves to 190 psi; 36 in barrels', None),
    ('Firing valves: U.S. Solid USS-HSV04, 1 in NPT, 12 V DC, NC, pilot-operated, 1-50 bar (725 psi), PTFE seal (Amazon B0BSNHJ4WQ)', 'Amazon', 2, 106.99, 'https://www.amazon.com/dp/B0BSNHJ4WQ', 'Motion', 'One per cannon (rev D.2: the bottom one too, so both run to full tank pressure, capped at 190 under the 200 psi reliefs)', 'In stock, one version only. Thread is listed as NPT / G (a dual thread, no option to pick), so true NPT is NOT confirmed: test-fit a 1 in NPT nipple before trusting it at 190 psi. Cv 11.67, 25 mm, PTFE seal, junction box. Opening time unpublished: bench-test before cutting barrels (2026-11-06, L)'),
    ('Chamber end plates: 3/8 in A36 hot-rolled steel, 4 x 16 in (B08C2FD1QH)', 'Amazon', 1, 16.0, 'https://www.amazon.com/dp/B08C2FD1QH', 'Structure', 'Waterjet four 3.5 in discs, flush with the pipe: each front disc gets a 1.33 in hole for its outlet nipple, the back discs are blank. Bevel the pipe ends 37.5 deg and weld all the way through. 3/8 in is about twice the thickness 200 psi needs', 'Four 3.5 in discs fit on the 4 x 16 in bar with room for the kerf. Replaces the four MSI chamber couplings ($111.80) now the chambers are welded. Plain steel has no part rating: the welded chamber is the pressure part, water-tested to 300 psi before it holds air (2026-11-10, L)'),
    ('Chambers: 3 in Sch 40 steel pipe, plain end, 24 in (A500, B0FLF5VJMG)', 'Amazon', 1, 40.48, 'https://www.amazon.com/dp/B0FLF5VJMG', 'Structure', "Cut 12.9 in for the top chamber (about 1.56 L) and 10.9 in for the bottom (about 1.32 L). Water-test each welded chamber to 300 psi for 10 minutes before it holds air (borrow a hand test pump and a 0-600 psi gauge). A steel-yard drop works too if it's cheaper", 'Plain-end A500, 0.216 in wall; the listing states no psi. 12.9 + 10.9 in leaves 0.2 in of the 24: make it one bandsaw cut, and if the pipe arrives short or out of square take both chambers down 1/16 in. The 16 in ($28.52) + 12 in ($20.24) lengths cost $8.28 more and leave room to face the ends (2026-11-10 review, L)'),
    ('Chamber inlets: 1/4 NPT female steel weld-on step bung, 2-pack (B0H6VR9N6R)', 'Amazon', 1, 9.99, 'https://www.amazon.com/dp/B0H6VR9N6R', 'Motion', 'One per chamber on the pipe wall about 1 in behind the front plate, facing the pivot side, so the inlet and outlet are at the same end. A swivel push-to-connect elbow screws in', "1/4-18 NPT, collar OD 24.8 mm x 16.5 mm (the CAD draws the 22 mm AC Performance one: drill the pipe to this one's step); only 15 left (2026-11-10, Kenzo's list, re-checked L)"),
    ('1 in NPT close nipple (1-1/2 in), seamless steel, Sch 80, ASTM A106, 300 psi (Grainger-approved B007IBN8T4)', 'Amazon', 2, 11.68, 'https://www.amazon.com/dp/B007IBN8T4', 'Motion', 'Each firing valve to its breech adapter (the chamber side is now the welded nipple in the next row)', "Sch 80: same 1.315 in OD (no CAD change), bore 24.3 mm vs 26.6 mm, about the HSV04's own orifice; the only Sch 40 ones on Amazon are 150 psi decorative pipe. Was McMaster 44615K416 2 x $3.13 (2026-11-10, Kenzo's list, re-checked L)"),
    ('Chamber outlets: 1 in x 4 in black steel pipe nipple (LDR 300 1X4, B0002YV7GU)', 'Amazon', 1, 7.99, 'https://www.amazon.com/dp/B0002YV7GU', 'Motion', "Cut in half: each cut end is welded through its chamber's front plate, and the HSV04 screws onto the threaded end", ''),
    ('1 in - 11-1/2 NPT pipe tap', 'Amazon', 1, 16.99, 'https://www.amazon.com/dp/B0BB3H8ZHP', 'Tool', "Cuts the 1 in NPT threads through the two aluminium breech pucks. Each puck is JB Welded into the back of its barrel, and the whole barrel screws onto its firing valve's nipple", 'Borrow one if the shop has it. 4.6 stars (2026-11-02, S)'),
    ('MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger, 10-pack (B0GGHY11RL)', 'Amazon', 1, 6.29, 'https://www.amazon.com/dp/B0GGHY11RL', 'Electrical', '6 used in this order: firing valves (2), in valves (2), and the contactor coil twice in series (one channel for the main controller, one for the safety node). The light bar and smoke get their own pack in Order 2', 'Triggers from 3.3 V, so the controller drives them directly (no buffer). Flyback diode across each valve coil; was two 6-packs $10.98 (2026-11-06, L)'),
    ('Barrels: clear extruded polycarbonate tube 3.00 in OD x 2.75 ID x 1/8 wall x 36 in (K-mac B09NLCGBWB)', 'Amazon', 2, 45.81, 'https://www.amazon.com/dp/B09NLCGBWB', 'Structure', 'Two 36 in barrels as they come. Three 3/8 in smoke holes each, leaning 40 deg to the muzzle; drill them after the barrel is screwed home so they face the other barrel', 'Same tube as McMaster 8585K38 ($66.05), free delivery; only 2 left. No pressure rating (none published at McMaster either); clamp it. Not acrylic: it shatters (2026-11-06, L)'),
    ('Gun cradle plates: 1/8 in aluminium sheet (stash), 2, CNC router', 'Stash', 2, 0.0, '', 'Structure', "The gun's two side plates (chevron + turret wheel), 490 x 226 mm each, about 0.7 kg. Every hole is 4.5 mm for an M4 and has a part behind it: 14 side screws into inserts in the saddles, chamber caps and gun core halves, 3 into the add-on rail's T-nuts, the hub's 4 (left plate) or the ring pulley's 6 standoffs (right plate), plus the 1/2 in hex for the pivot stub", "From your aluminium (Micah, 2026-11-11). One DXF per plate in docs/glacis/gun_plates/ (mm). The only CNC router parts: 490 x 226 mm is too big for the 12 x 12 in waterjet. The pockets' inside corners are 4 mm radius, so a 1/4 in end mill or smaller reaches them; drill or helix the 4.5 mm holes"),
    ('Breech pucks: 6061 flat bar 1 in x 4 in x 8 in, T6511 (B0CCGN9HSQ, pick the length)', 'Amazon', 1, 30.0, 'https://www.amazon.com/dp/B0CCGN9HSQ', 'Structure', 'Two pucks, 2.5D on the CNC: a 3 in x 1/4 in flange the barrel butts on and a 2.74 in x 3/4 in spigot JB Welded inside it, 1 in NPT tapped straight through (the tap is on this list). Barrel + puck is then one piece: it slides into the gun core from the front and screws onto the firing valve nipple', '[UNVERIFIED price: Amazon listing not readable, estimate; Zoro sells 1 x 4 x 6 at $26.19] Not the 1 x 3 bar: no clean-up round the 3 in flange (Micah 2026-11-12: no aluminium stock, 2.5D only)'),
    ('Printed gun parts (PETG): 2 gun core halves, 2 chamber saddles, 4 chamber caps, 2 chamber end covers, axle hub, axle spacer, 112T ring pulley (its 6 standoff posts printed on, an M4 insert in each), 16T pinion, smoke collar, muzzle ring', 'Owned', 1, 0.0, '', 'Structure', "Gun core halves (left / right): each is one side's valve blocks, half the breech block and half the mantlet; 2 x M4 x 12 across the split clamp both barrels onto their spigots, then 6 x M4 x 8 through each side plate. Saddles and caps hold the chambers (the rear set is V-shaped like the plates' back). 5 walls, 40% gyroid", 'Filament is the PETG row. Every part fits a 250 mm bed (a core half is 242 x 197 x 74 mm, printed outer face down)'),

    ('ELEVATION - 312 rpm FTC motor on a Spark MAX (backdrives when off), pot for the angle', None),
    ('HTD 5M 9 mm belt, 150T (750 mm) (uxcell B0DF57XRZ8)', 'Amazon', 1, 7.81, 'https://www.amazon.com/dp/B0DF57XRZ8', 'Motion', 'goBILDA 16T pinion to the printed 112T pivot pulley (CAD loop is exactly 750 mm)', "9 mm to match goBILDA's HTD pulleys (AliExpress only has 10 mm); was $8.99 at WCP (2026-11-04, L)"),
    ('goBILDA 5203-2402-0019 Yellow Jacket 19.2:1 (312 rpm), 8 mm REX (owned)', 'Owned', 1, 0.0, 'https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-19-2-1-ratio-24mm-length-8mm-rex-shaft-312-rpm-3-3-5v-encoder/', 'Motion', "16T -> 112T belt to the ring pulley on the gun's right cradle plate (7:1, about 45 rpm free at the gun, 16.7 N*m stall)", 'Owned: Micah has every goBILDA motor (2026-11-04)'),
    ('REV Spark MAX (owned)', 'Stash', 1, 0.0, '', 'Electrical', 'Drives the goBILDA in brushed mode from PWM', 'Owned'),
    ('10k linear pot (one of yours)', 'Owned', 1, 0.0, '', 'Electrical', "Gun angle on the end of the left pivot stub through a printed coupler (it passes through the tower plate's hole), to the main controller's own ADC on 3.3 V (both ADS1115s are full)", 'Owned (Micah, via the Mac chat 2026-11-10)'),

    ('CONTROLS, FAILSAFE + POWER - back bottom bay', None),
    ('Anderson SB50 flush-mount bracket + dust cover kit', 'Aliexpress', 1, 2.0, 'https://www.aliexpress.us/item/3256806307889526.html', 'Electrical', 'Standby charge / shore-power port, bottom of the rear panel (a stash SB50 housing goes in it)', '5 stars, 68 sold. Was $9.99 (2026-11-04, L)'),
    ('Main controller: Waveshare ESP32-P4-Module-DEV-KIT, ESP32-P4 + ESP32-C6 (B0FDWZ6KWT)', 'Amazon', 1, 28.79, 'https://www.amazon.com/dp/B0FDWZ6KWT', 'Electrical', 'One board does it all (rev D.2.1): web UI and WebSocket on 2.4 GHz WiFi 6 (the C6 on the board), valves and chamber metering, elevation loop, every LED strip, audio mixing out of its own speaker amp into the siren amp, MIPI camera later, lidar on a UART, the PDH contactor and both battery relays. 5 V from the logic rail on its SH1.0 power header', 'Micah picked it 2026-11-09 over the WTDKP4C5-S1 ($29.29) for the USB plugs: 4 USB-A + 2 USB-C, RJ45 (PoE header), a 40-pin Pi-style header with 28 GPIO (takes Pi HATs), ES8311 codec + NS4150B 2 W speaker amp + mic, speaker included. 2.4 GHz only, so the access point runs 2.4 GHz. Sold by UeeKKoo, 3.6 stars (10); Waveshare store $19.99 + shipping, AliExpress from $27.89 (2026-11-09, L)'),
    ('ADS1115 16-bit 4-channel ADC module, I2C, 2-pack (B0DZSP4CG8)', 'Amazon', 1, 7.99, 'https://www.amazon.com/dp/B0DZSP4CG8', 'Electrical', '#1: the three pressure transducers + the 5 V reference. #2: battery A, battery B, the bus and the PDH volts, so the battery relays compare the two packs to a few mV. Both on I2C to the main controller (its own ADC only reads the pot)', 'Settled call: ESP32 ADCs are too nonlinear for pressure. Two for the price of the single (B0FLPZMQJY, $7.99); 5 stars (3), 50+ bought last month (2026-11-09, L)'),
    ('PWM expander: PCA9685 16-channel, I2C (Dorhea B07RMTN4NZ)', 'Amazon', 1, 5.99, 'https://www.amazon.com/dp/B07RMTN4NZ', 'Electrical', "12 of 16 used: drive PWM to the 4 Falcons and the elevation Spark MAX, fog heater (2), pump, blower, light bar, both battery relays. Valves, LED data and the contactor stay on the board's own pins (timing and safety). OE is pulled up and held low by the controller, so a reset or crash turns every output off", "The 28 header pins can't take all ~38 D.2 signals; this frees 12. One PWM frequency for all 16 (about 200 Hz suits the Falcons, Spark MAX and light bar; on/off loads use full-on/full-off). 4.5 stars (104), 200+ bought last month (2026-11-09, L)"),
    ('12 V 40 A relay with pre-wired socket', 'Aliexpress', 1, 2.02, 'https://www.aliexpress.us/item/3256810529693206.html', 'Electrical', 'Valve arm relay (valve rail, fed from the PDH); flyback diode on the coil. The two fog relays are in Order 2', '4-pin option; 211 sold. Replaces the Nilight 5-pack ($12.14) and the Gebildet 2-pack ($7.99) (2026-11-04, L)'),
    ('ULN2803A Darlington driver DIP-18, 10-pack', 'Aliexpress', 1, 2.49, 'https://www.aliexpress.us/item/3256810280411957.html', 'Electrical', 'Relay coils from 3.3 V logic: the valve arm relay, both battery relays and the two fog relays (0.15 A coils; COM to +12 V clamps the flyback)', '16 sold. Was $3.84 at DigiKey (2026-11-04, L)'),
    ('Contactor + battery relays: 12 V 200 A continuous duty, isolated coil, 4-pin (B0D97PSZBB)', 'Amazon', 3, 11.99, 'https://www.amazon.com/dp/B0D97PSZBB', 'Electrical', "1: the power cut-off between the main breaker and the PDH. Its coil runs through the rear E-stop, the safety node's switch and the main controller's MOSFET in series, so any one of them kills drive, valves, LEDs, audio and fog. 2: one in each battery's + lead, between its SB50 and the shared bus; the controller keeps only the fuller pack connected until the other is within 0.3 V, so a fresh battery never dumps 20-40 A into a flat one", "200 A continuous, 4-pin; only 8 left (3 needed); was $12.99 B07T48QKQB (2026-11-10, Kenzo's list, re-checked L)"),
    ('Battery relay bypass: 4.7 ohm 5 W cement resistor, 10-pack (B0FG25KG8C)', 'Amazon', 1, 5.79, 'https://www.amazon.com/dp/B0FG25KG8C', 'Electrical', 'One across each battery relay (2 used): feeds the logic rail and boots the controller while both relays are open (power-up, or a dead controller), and trickle-balances the packs at well under 1 A', 'Under 1 W each in the worst case: a fresh and a flat pack, one relay open, full drive load. 5 stars (7) (2026-11-09, L)'),
    ('Logic supply: 5 V 5 A buck-boost module, 3.6-32 V in (pick "5V")', 'Aliexpress', 1, 2.67, 'https://www.aliexpress.us/item/3256808244937735.html', 'Electrical', 'Always-on 5 V logic rail, tapped ahead of the contactor: main controller (its 5 V header), safety node, every sensor', "The row had no link: this is the 3.6-32 V to 5 V / 9 V / 12 V 5 A module, $2.67, 4.8 stars, 413 sold; pick the 5V option. Short-circuit, over-temperature and TVS protection; holds 5 V down to 3.6 V in, so a drive sag can't reset the controllers. Was the PM02 at $13.30 (2026-11-10 review, L)"),
    ('Latching mushroom E-stop 22 mm, 2 NC (LA38)', 'Aliexpress', 2, 5.25, 'https://www.aliexpress.us/item/3256806731686244.html', 'Electrical', 'Rear panel: one contact in the contactor coil (kills the PDH), the other in the valve arm relay coil; + the handheld remote', 'Pick the 2 NC option; 180 sold, 4.9 stars. Was $13.99 each (2026-11-04, L)'),
    ('Panel-mount USB-C extension, 30 cm, IP67, male to female, USB 2.0 (pick "0.3m")', 'Aliexpress', 1, 4.92, 'https://www.aliexpress.us/item/3256805524391829.html', 'Electrical', 'USB to the main controller through the rear panel (30 cm reaches the controller on the bellypan)', '600+ sold; USB 2.0 is all the ESP32-P4 needs to program. Was the 10 cm one ($2.06): too short (Micah). Check the panel hole size on the listing before cutting the acrylic (2026-11-11, L)'),
    ('Printed board trays (3DP): one under each board on the bellypan, 6 mm standoff posts with heat-staked pegs', 'Owned', 1, 0.0, '', 'Electrical', 'Seven trays (controller, safety node, PCA9685, both ADS1115s, drivers board, logic supply): each board drops onto four printed pegs that a soldering iron mushrooms over (no screws, nothing conductive under the board); each tray takes 2 x M4 x 12 up through the bellypan into M4 inserts', 'Filament is the PETG row (2026-11-11, L)'),
    ('Safety remote: TP4056 Type-C 18650 charger board with protection (pick "TP4056 Module TYPE-C", "1PCS") + a stash 18650 cell', 'Aliexpress', 1, 1.09, 'https://www.aliexpress.us/item/3256809139500038.html', 'Electrical', "Remote power, charged over USB-C, inside your custom printed remote case: OUT+ through a slide switch to the C3 SuperMini's 5V pin (its regulator holds 3.3 V down to about 3.4 V on the cell), OUT- to GND. Charge with the remote switched off, and never plug USB into the C3 with the cell connected", '1,000+ sold, free shipping, overcharge / over-discharge / short protection. Replaces the $3.29 battery shield: no 5 V boost needed (Micah: just the board) (2026-11-11, L)'),
    ('FRC 12 V battery + charger (owned)', 'Stash', 2, 0.0, '', 'Electrical', 'One per side on its own slide-out sled, each through its own battery relay (below)', 'Owned'),
    ('REV PDH + ATO breakers, 120 A main breaker, SB50s, wire and lugs', 'Stash', 1, 0.0, '', 'Electrical', "Main power: the 120 A breaker is the robot's on / off switch, on the rear panel beside the E-stop (its trip button and reset lever through a 42 mm hole). The E-stop only drops the contactor; the logic rail stays up until the breaker is off", 'Owned / Standard FRC stash part; buy only if the stash is out'),
    ('ESP32-S3 boards (your two)', 'Owned', 2, 0.0, '', 'Electrical', '1: safety node (ESP-NOW to the remote; holds the PDH contactor in only while the remote and the main controller are alive). 2: spare', 'Owned'),
    ('Inline ATO fuse holder + 5 A fuse', 'Stash', 1, 0.0, '', 'Electrical', 'Logic tap, right after the main breaker', 'Standard FRC stash part; buy only if the stash is out'),
    ('Resistors and caps (kit): ADC dividers, pull-downs, RC filters', 'Stash', 1, 0.0, '', 'Electrical', 'Three transducers (10k/15k), battery A, battery B, bus and PDH volts (39k/10k), 100k pull-downs so a cut sensor wire reads as a fault, the speaker tap, a 330 ohm series resistor on each LED data line (no level shifter)', 'Standard FRC stash part; buy only if the stash is out'),
    ('Safety remote: ESP32-C3 SuperMini (one of yours)', 'Owned', 1, 0.0, '', 'Electrical', 'Handheld E-stop (the second mushroom above) plus a status LED that shows the link is up; ESP-NOW to the safety node', "Your spare C3s do ESP-NOW like the S3 Super Mini they replace ($3.79, aliexpress.us/item/3256809624317467). Bluetooth LE only, so they can't be the phone-music board (2026-11-09)"),

    ('RIVETS - first order (Micah, 2026-11-11: "if we order rivets, they should be in the first order")', None),
    ('Rivets: 3/16 in aluminium blind rivets, dome head, 3/16 x 1/4 (6-4, 0.188-0.250 in grip), 100 pcs (B07KPQM2TZ)', 'Amazon', 1, 15.48, 'https://www.amazon.com/dp/B07KPQM2TZ', 'Structure', "About 138 used (one pack: you have plenty more): every waterjet bracket that isn't countersunk (inboard plates, arm knees, top corner gussets, tower plates) into its tube. A 1/8 in plate on a 1/16 in tube wall is 0.188 in, the bottom of this grip", 'Fastenere 6-4, open end, 5052 body. Checked the listing (2026-11-11, L)'),
    ('Rivets: 3/16 in aluminium countersunk blind rivets, 120 deg, 3/16 x 1/4 (0.126-0.250 in grip), 50 pcs (B0B33RF991)', 'Amazon', 3, 14.99, 'https://www.amazon.com/dp/B0B33RF991', 'Structure', 'About 100 used: the side plates (the wheels run right beside them), the bottom corner gussets (the underglow bracket runs right under them) and the bellypan (a smooth underside). Countersink those holes 120 deg after the waterjet', 'Metal Magery, 100% aluminium; 16 left when checked (2026-11-11, L)'),
    ('AUDIO - two siren speakers in the front corners (replaces the horn)', None),
    ('Siren speaker 200 W, 8 ohm, 121-130 dB, aluminium, 5.7 x 5.5 x 2.3 in (Xprite B01DMSR4L4)', 'Amazon', 2, 32.88, 'https://www.amazon.com/dp/B01DMSR4L4', 'Electrical', 'One high in each front-side corner, in a printed cup, aimed 45 deg out and 30 deg up; its L foot bolts through the cup', '4.3 stars (682), 50+ bought last month; 5 lb each. Replaces the SoundAlert ($59.99) (2026-11-04, L)'),
    ('TPA3255 2 x 300 W class-D amp board, 19-50 V DC, 122 x 73 x 30 mm', 'Aliexpress', 1, 22.0, 'https://www.aliexpress.us/item/3256807353596235.html', 'Electrical', 'One channel per speaker; about 70 W each into 8 ohm on 33 V', '$27.00 is your price in the Sheet (2026-11-06; it was $15.27 + $1.99 on 2026-11-04). 727 sold, 4.9 stars. Amazon: B0DSSZZR5Q $25.99'),
    ('1200 W 20 A boost converter, 8-60 V in, 12-80 V out (set to 33 V; pick the "1200W 20A" option)', 'Aliexpress', 1, 10.67, 'https://www.aliexpress.us/item/3256806808745565.html', 'Electrical', 'Feeds the amp from a 40 A PDH channel. At 33 V the amp tops out near 70 W per speaker (about 2 dB under 100 W), so the board stays under the 15 A where the listing asks for extra cooling. The $1.09 price on the listing is a one-time new-shopper offer', 'Pick the "1200W 20A" option (the other is 1500W 30A). The $1.09 shown to new shoppers is a welcome price; $10.67 is the logged-in one. Size not on the listing [UNVERIFIED]: drawn 130 x 55 x 55 mm, the size of the same module on Amazon (B0GJLKX5D2, $15.99, 5.12 x 2.09 x 2.09 in). Listing live (2026-11-10 review, L)'),
    ('Speaker tap: 2 x 1k + 2 x 10 nF low-pass + 1 uF cap (from the kit)', 'Stash', 1, 0.0, '', 'Electrical', "Replaces the PCM5102A: one wire of the board's speaker output (SPK+) through a two-stage 1k/10 nF low-pass and a 1 uF cap into the TPA3255's input (L and R together). Volume and mix are set in software; the amp's gain pot sets the top end", 'Not straight in at low volume: the NS4150B is bridge-tied and filterless, so each speaker wire carries a 5 V square wave at a few hundred kHz plus 2.5 V DC at any volume, and grounding SPK- shorts the amp. SPK- stays unconnected. If the amp still whines, a PCM5102A I2S DAC module ($2.44, aliexpress.us/item/3256809226289251) is the fallback'),
    ('Printed speaker cups (2) and grilles (2)', 'Owned', 1, 0.0, '', 'Structure', "Cup lines each corner notch, 4 x M4 x 8 through its walls into the frame; the speaker's foot bolts through it; grille: 3 walls, no top/bottom layers, 12% gyroid", 'Filament assumed owned'),

    ('DRIVE - old 9 in mecanum wheels on Falcon 500s (owned / stash)', None),
    ('Falcon 500 (owned)', 'Stash', 4, 0.0, '', 'Motion', 'One per wheel, plain PWM from the main controller (no gate: the contactor is the cut-off)', 'Owned'),
    ('12T HTD 15 mm Falcon pulley (WCP-0319)', 'Stash', 4, 0.0, 'https://wcproducts.com/products/wcp-0319', 'Motion', 'Falcon 12T -> 116T printed into the hub (9.67:1)', 'Standard FRC stash part; buy only if the stash is out ($7.99 at WCP)'),
    ('HTD 5M 15 mm drive belt, 140T (700 mm), rubber, 1 pc (uxcell B0DSQWZBVR)', 'Amazon', 4, 8.9, 'https://www.amazon.com/dp/B0DSQWZBVR', 'Motion', "One per wheel: Falcon 12T to the wheel's 116T (9.67:1), as the CAD's drive is drawn. If the old 9 in wheels end up on a different pulley, re-pick the length (the 12T stays)", '4.4 stars (131), $8.90 each (10% off, typically $9.89) (2026-11-11, L). Added so the CAD and the parts list match (Micah)'),
    ('Old 9 in mecanum wheels (owned, for now)', 'Owned', 4, 0.0, '', 'Motion', 'Stand-ins for the printed 10 in vector wheels (Micah, 2026-11-04); belts and hubs depend on how they mount', 'The printed-wheel parts (608s, M8 rod, nylocs, 1/4-20 hub bolts, 140T belts) are off the list until the printed wheels come back'),
    ('Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)', 'Stash', 12, 0.0, 'https://wcproducts.com/products/wcp-0783', 'Motion', '2 per wheel axle (inner + outer rail), 4 at the pivot', 'Standard FRC stash part; buy only if the stash is out ($2.99 each)'),
    ('1/2 in hex shaft: 4 wheel axles (6-3/8 in) + 2 pivot stubs', 'Stash', 1, 0.0, '', 'Motion', "Live axles tapped 10-32 both ends, each ending inside the outer rail in its bearing (the end screw and washer go in through a 14 mm hole in the rail's outer wall, which the bumper covers: no holes in the bumper); one steel stub per cradle plate on the pivot axis (2.7 in left, 2.2 in right), tapped 1/4-20 both ends: a 1/4-20 button head and washer inside the cradle plate and one outside the outer bearing keep each stub from sliding (stash hardware)", 'Standard FRC stash part; buy only if the stash is out'),

    ('SMOKE - custom 12 V fogger (one 200 W core, room for a second), barrel collar, front and rear trail vents', None),
    ('Fog heater core 12 V 200 W, cast heat exchanger 97 x 32 x 36 mm', 'Aliexpress', 1, 26.38, 'https://www.aliexpress.us/item/3256805556610953.html', 'Cosmetic', 'The fogger: about 17.5 A on its own 30 A PDH channel', '$24.39 + $1.99 shipping at your logged-in price now (was $34.39). No thermostat or fuse on the listing: the firmware cut at 245 C on the K probe is the only limit (Micah dropped the KSD301 cutout, 2026-11-11) (2026-11-06, L)'),
    ('Fog fluid pump: Kamoer NKP 12 V peristaltic, 70 mL/min', 'Amazon', 1, 9.98, 'https://www.amazon.com/dp/B07GWJ78FN', 'Cosmetic', 'Feeds the core from the printed tank (a second one comes with a second core)', 'Fine running dry; back-pressure [UNVERIFIED] (2026-11-02, S)'),
    ('Thermocouple amp MAX6675 + K-type probe', 'Aliexpress', 1, 2.03, 'https://www.aliexpress.us/item/3256813189448378.html', 'Electrical', 'Core temperature to the main controller (SPI); hold 220-240 C, firmware cut at 245 C', 'Was $7.69 on Amazon (2026-11-04, L)'),
    ('DS18B20 waterproof temperature probe, 1 m, 5-pack', 'Aliexpress', 1, 4.4, 'https://www.aliexpress.us/item/3256808611802365.html', 'Electrical', '1-Wire on one controller pin: fogger box by the printed tray (heater off at 70 C), electronics shelf, battery bay; 2 spare', 'Was $9.49 on Amazon (2026-11-04, L)'),
    ('12 V 5015 blower, 2-pack (Diann B09W5N73BD, dual ball bearing)', 'Amazon', 1, 5.99, 'https://www.amazon.com/dp/B09W5N73BD', 'Cosmetic', 'Pushes the fog from the cores into the splitter and down the three tubes', "6.5 CFM, 2.16 W; only 10 left; was Gdstime $6.56 on AliExpress (2026-11-10, Kenzo's list, re-checked L)"),
    ('Silicone tube 3 mm ID x 5 mm OD (per metre)', 'Owned', 2, 0.0, 'https://www.aliexpress.us/item/3256808335149485.html', 'Cosmetic', 'Tank -> pumps -> core inlets (zip-tied on the 2.5 mm tubes)', 'Was $5.99 on Amazon (2026-11-04, L)'),
    ('Fog fluid, water-based, medium density, 1 gal (B0DF5RCGJX)', 'Amazon', 1, 20.99, 'https://www.amazon.com/dp/B0DF5RCGJX', 'Cosmetic', 'Fills the printed tank about 9 times', "FogUp went to $23.95 (2026-11-10, Kenzo's list, re-checked L)"),
    ('Silicone tube 3/4 in ID x 1 in OD, 1/8 in wall, 9.84 ft, food grade, -60 to 240 C (Quickun B091SP66Z9, pick the 3/4 x 1 in size)', 'Amazon', 1, 24.99, 'https://www.amazon.com/dp/B091SP66Z9', 'Motion', "The gun's smoke line: splitter, up through the well floor, into the gun core, then dead centre between the two barrels to the smoke collar. 3/4 in ID (Micah: go bigger): about a fifth of the 1/2 in line's pressure loss, so the blower actually pushes fog through it. The barrels are only 25 mm apart, so it squishes to an oval there: every printed hole it passes through is oblong. Some fog always condenses in the line; a wide, short, smooth run with no low sag loses the least, and insulating it barely helps", '4.5 stars (656), in stock. Not the 3/4 x 7/8 thin-wall option (kinks) (2026-11-11, L)'),
    ('MOSFET switch module 5-36 V 15 A, 6 pcs with heat sinks (MTDELE B0D9VWWLCB)', 'Amazon', 1, 5.49, 'https://www.amazon.com/dp/B0D9VWWLCB', 'Electrical', '5 used: light bar (PWM), fog heater (2), fog pump, blower (moved from Order 1)', "5 used; 6-pack instead of a second 10-pack (2026-11-10, Kenzo's list, re-checked L)"),
    ('12 V 40 A relay with pre-wired socket', 'Aliexpress', 2, 2.02, 'https://www.aliexpress.us/item/3256810529693206.html', 'Electrical', 'One per fog core (the second for a second core later); flyback diode on every coil (moved from Order 1)', '4-pin option; 211 sold. Replaces the Nilight 5-pack ($12.14) and the Gebildet 2-pack ($7.99) (2026-11-04, L)'),
    ('M5 aluminium standoffs (stash): 4 under the fog heater bracket', 'Stash', 4, 0.0, '', 'Cosmetic', "Hold the fog heater's aluminium bracket off the smoke tray. Metal, not printed: the core runs at 220-240 C", 'Stash (2026-11-11, L)'),
    ('Flexible fog tube (yours, 2)', 'Owned', 2, 0.0, '', 'Cosmetic', 'Splitter to the front and rear vents (both down through the bellypan)', 'Owned'),
    ('Printed smoke parts: tray, 400 mL tank, 1-to-3 splitter, one-piece smoke collar, front and rear vents (PETG/ASA)', 'Owned', 1, 0.0, '', 'Cosmetic', 'Ducts, vents and the barrel collar', 'Filament assumed owned; the cores sit on an aluminum bracket, never on a print'),

    ('FRAME + BODY - box tube, printed frame, recessed acrylic', None),
    ('Heat-set inserts M4 x 4, brass, OD 5 mm, 100 pcs (M4X4X5mm option): every M4 insert', 'Aliexpress', 2, 3.56, 'https://www.aliexpress.us/item/2251832656703778.html', 'Structure', "About 102 used, so two packs (spares for the ones that go in crooked): panel clips (40), speaker cups (8), the gun (30: 8 in the chamber saddles' sides, 8 in the chamber caps' sides, 12 in the gun core halves' sides, 2 for the core's clamp screws), the in-well rails' screws (10, in the deck's well-edge member), the front light bar rails' screws (4), the 112T ring's 6 printed posts (one at each post's plate end). The holes stay as drawn (4.7 mm, 6.5 deep; 4.6 deep at the 12 tight clips): the insert sits at the top and the screw tip runs on into the plastic below", 'Logged-in price; ships with the M4 x 6 lot (2026-11-04, L). Listing live; 1 -> 2 packs (2026-11-10 review, L)'),
    ('M4 x 12 button head, 304 stainless, 100 pcs', 'Amazon', 1, 7.4, 'https://www.amazon.com/dp/B0DKXQQPWS', 'Structure', "Frame-joint cross screws (40, self-tapping into the tenon's pilot), standoffs, the pivot bearing blocks down onto the in-well rails (4, into T-nuts), the elevation motor bracket up into the right rail (2, into T-nuts), the left axle hub (4, through its flange and the plate into nylocs), the gun core's 2 clamp screws (across the split between the barrels, into inserts)", 'Only 2 left; backup 12.9 black-oxide B0CTH3FQLD $8.86 (2026-11-02, L)'),
    ('M4 x 8 button head, 304 stainless, 100 pcs (B0DKXNTRTW)', 'Amazon', 2, 6.74, 'https://www.amazon.com/dp/B0DKXNTRTW', 'Structure', "About 122: panel clips (28, plus the 12 short ones with a screw cut to 6 mm), speaker cups (8), gun rails (6, through the cradle plates into T-nuts), the light bar's 2 bracket feet, the front rails (4), the 112T ring's 6 printed posts (6, from inside the right cradle plate into the posts' inserts), and the gun's side screws through the cradle plates into inserts (28: 8 into the chamber saddles, 8 into the chamber caps, 12 into the gun core halves)", '4.4 stars (2026-11-04, L)'),
    ('M4 nylon-insert lock nuts, 304 stainless, 100 pcs (B0BHQMBRFX)', 'Owned', 1, 0.0, 'https://www.amazon.com/dp/B0BHQMBRFX', 'Structure', "The left axle hub's 4 bolts (M4 x 12, through its 3 mm flange and the cradle plate)", "Amazon instead of Zoro (Micah: Amazon or AliExpress only) (2026-11-10, Kenzo's list, re-checked L)"),
    ('Foam tape 1/4 in x 1/16 in, white, 2 x 33 ft (Yotache B0CCKJ2ZTV)', 'Amazon', 1, 11.98, 'https://www.amazon.com/dp/B0CCKJ2ZTV', 'Structure', "About 13 m round every panel's acrylic ledge, so the clips clamp the panels instead of letting them rattle (the rebate is 0.7 mm deeper for it). White, so it doesn't read as a dark line through the frosted acrylic", 'Yotache; 4.4 stars (2026-11-04, L)'),
    ('#10-32 heat-set inserts, brass, 3/8 in, 60 pcs (B0DFWTJYHK)', 'Amazon', 1, 9.99, 'https://www.amazon.com/dp/B0DFWTJYHK', 'Structure', "42 used: 13 in the frame (8 in tabs on the side walls' inner faces, 5 in the end walls), 13 in the posts' feet, 16 in the bumper corner brackets", '6.3 mm hole, 10.5 deep; 4.8 stars (2026-11-04, L)'),
    ('Frosted acrylic 1/8 in (owned): 8 panels (the front is one U-shaped sheet round the light bar hole)', 'Owned', 8, 0.0, '', 'Cosmetic', 'Recessed in the printed frame, held by corner clips; cut 1 mm under the rebate outline all round', 'Owned. You found enough for all 8 panels (Micah, 2026-11-11), so the Lesnlok 2-pack ($86.98) is off the list; the cut plan in docs/glacis/acrylic_cuts is for 24 x 48 in sheets'),
    ('Printed body frame: 50 pieces incl. two front cheeks, 58 tapered tenons (40 cross-screwed, 18 glued), 40 corner clips, 14 underglow brackets, 13 frame mount posts, 4 bumper corner brackets (PETG)', 'Owned', 1, 0.0, '', 'Structure', 'Holds the panels; a strip tunnel down every member (the frame glows); each window wall chamfers from the acrylic ledge to its LED strip', 'Filament assumed owned. Frame pieces: 0.6 mm nozzle, 2 walls, 10% gyroid; mounts, brackets, clips: 4 walls, 25%. Plates, PETG and hours in docs/glacis/print_plan.md'),
    ('#10-32 screws (yours): 1/2 in and 2-1/2 in', 'Owned', 1, 0.0, '', 'Structure', "1/2 in x 35: frame to posts (13, up from each post's outer pocket once the bumper ring is off), bumper ring to the side rails (6, from inside the rail), bumper corner brackets (16). 2-1/2 in x 13: posts to rails (up through the rail and gusset)", 'Owned: the geometry is set for 1/2, 1-1/4 and 2-1/2 in (2026-11-04)'),
    ('Epoxy for the 16 glued frame joints (5-minute, any brand)', 'Owned', 1, 0.0, '', 'Tool', "The tapered tenons on the filled LED corners (no cross screw: every way in for a screw head is a surface seen through the acrylic), and the one glued split across the gun well's front. Push a strip offcut through the tunnel across each joint while it cures", 'Owned / shop stock'),
    ('Hand riveter for 3/16 rivets, #11 drill, 120 deg countersink (stash)', 'Stash', 1, 0.0, '', 'Tool', 'Setting every bracket rivet; the countersink for the side plates, bottom corner gussets and bellypan', 'Standard FRC shop tools'),

    ('RAILS - 20x20 T-slot rails (Brophy Borealis): two inside the gun well, two on the gun, two across the front light bar hole', None),
    ('M4 drop-in T-nuts for 20-series (6 mm slot), M4 x 10 x 6, 50 pcs', 'Aliexpress', 1, 2.52, 'https://www.aliexpress.us/item/2251832628044342.html', 'Structure', "14 used: 3 per gun rail, 1 under each light bar bracket foot, 2 under each pivot bearing block (in the in-well rail's top slot), 2 for the elevation motor bracket (the right rail's bottom slot). Drop in from the side after the rail is placed", '$2.90 ($1.09 new-shopper price) (2026-11-09, L)'),
    ('M4 x 30 button head screws, ISO 7380, black 10.9 steel, 30 pcs', 'Aliexpress', 1, 3.39, 'https://www.aliexpress.us/item/3256808326585307.html', 'Structure', "10 used: through holes CNC'd across the in-well rails' core (8 mm head access from the gun well) and the tower plates into inserts in the deck's well-edge member", 'Price per length [UNVERIFIED]: $1.09 showed for the default 50 mm option (2026-11-09). Stash M5s work too'),
    ("20x20 T-slot extrusion (your spares): 2 x 470 mm inside the gun well, 2 x 276 mm inside the gun's cradle plates, 2 x 372 mm across the front light bar hole", 'Owned', 6, 0.0, '', 'Structure', "Gun well: one each side, flush with the towers' outboard face and 2 mm under the deck, one piece over the cut-down tower; the pivot's bearing block sits on it and the tower plate between it and the well-edge member. Gun: one inside each cradle plate along its top edge, flush with it. Front: flat on the frame's inner face behind the light bar hole, one along its bottom (the bar stands on it) and one along its top (free for sensors). All mirrored about the centreline and clear of the 0-90 deg swing; the cross holes in the in-well and front rails are a CNC side operation", "Yours (Micah, 2026-11-10: 'I have a lot to spare'). Cut square; the CAD lengths are the cut lengths"),
    ('Waterjet brackets: 1/8 in aluminium sheet (stash), 36 flat parts on the 12 x 12 waterjet', 'Stash', 1, 0.0, '', 'Structure', 'Nothing bent. Side plates (4: the Falcon and axle plates grown along the inner rail into every post: the rear ones take both sled posts, the tower and the rear tank post), inboard plates (6), arm knees (14), corner gussets (4 top, 4 bottom), tower plates (2) and rail spacer strips (2), (the bellypan is one CNC router piece now)', "From your aluminium (Micah, 2026-11-11). DXFs, the 12 x 12 nest and the table in docs/glacis/waterjet/; everything except the cannon's two side plates is waterjet. Every rivet hole has its matching hole in the tube in the CAD, for the CNC program"),

    ('LIGHTS - panel loops, glowing frame, underglow, front light bar', None),
    ('WS2812B LED strip 5 mm wide, 2020 LEDs, 100 LED/m, 5 m', 'Aliexpress', 2, 14.16, 'https://www.aliexpress.us/item/3256806570121908.html', 'Electrical', '7.6 m: one piece per frame member (the front and rear bottom members have no tunnel: a jumper wire runs round them), LEDs out, bent the easy way up into the feed slot at each end and soldered to the next at the slot mouth', '$13.61 a reel + $1.09 shipping split over the two; 77 sold, 5 stars. Logged-in price (2026-11-04, L)'),
    ('WS2812B LED strip 10 mm, 60 LED/m, 5 m, black PCB, IP30', 'Aliexpress', 3, 7.33, 'https://www.aliexpress.us/item/3256807802893080.html', 'Electrical', '11.2 m: one closed loop per panel on its window wall, centred 25 mm behind the acrylic, LEDs aimed across the panel; 2.5 m of underglow under the bumpers from the rest of the third reel', '3,000+ sold, 4.8 stars, Choice. Logged-in price; was $13.99 a reel on Amazon (2026-11-04, L)'),
    ('Front light bar: Zmoon 12 in single-row LED bar, 72 W spot/flood combo, 12/24 V (your pick)', 'Amazon', 1, 17.99, 'https://www.amazon.com/dp/B07SWZ1LMM', 'Electrical', 'In a plain hole at the bottom of the front slant (Brophy Borealis: from the bumper to 4.5 in above it, open at the bottom, no liner), standing on the lower of two 20x20 rails across the hole on its own end brackets, aimed straight ahead; the upper rail is free for sensors. The main controller switches it (and can PWM-dim it) through a MOSFET channel; about 6 A at 12 V', '72 W, 8000 lm claimed; now $17.99. Size not listed: modelled 330 x 30 x 45 mm [UNVERIFIED] (2026-11-06, L)'),
    ('12/24 V -> 5 V 20 A buck, potted', 'Amazon', 1, 15.99, 'https://www.amazon.com/dp/B089M5R3NJ', 'Electrical', 'LEDs only, on a PDH channel, so they go dark with the PDH', 'About 1,680 LEDs: cap them at about 20% white in firmware; inject 5 V at every frame node (2026-11-02, L)'),
    ('3M double-sided tape, heavy duty, 0.39 in x 15.4 ft, black, 2-pack (Xguider B0GBVMRXM5, pick 0.39")', 'Amazon', 1, 15.99, 'https://www.amazon.com/dp/B0GBVMRXM5', 'Electrical', "Holds the underglow strip on its printed brackets' 45 deg face (the strip's centre just under the bumper's bottom edge), and the 14 brackets onto the rails' bottom wall (no rivnuts): about 4 m used of 9.4 m", "Micah's pick (2026-11-11): the 0.39 in width, 2 rolls. Listing live (2026-11-11, L)"),
    ('3-pin LED wire, 22 AWG stranded tinned copper, 3 colours, 100 ft (AOTOINK B08JTZKN4M)', 'Amazon', 1, 15.99, 'https://www.amazon.com/dp/B08JTZKN4M', 'Electrical', "Every strip's 5 V / data / GND run back to the main LED board, and the jumpers between panels (40 ft is the minimum, 100 ft leaves spare). 22 AWG is enough: the worst plug carries one panel loop, about 1.2 A at the 20% white cap, about 0.2 V drop over a 1.5 m run. The frame runs get their 5 V injected at the frame nodes, so their cable only carries data and a little current", '4.7 stars (941), in stock. Pure tinned copper, not CCA. Check which colour is which before crimping, so every plug has the same pinout (2026-11-11, L)'),
    ('Servo extension leads, JR/Futaba 3-pin, male to female, 15 cm, 22 AWG, 20 pcs (OliYin B07QJSWNFM)', 'Amazon', 1, 9.98, 'https://www.amazon.com/dp/B07QJSWNFM', 'Electrical', 'Cut each lead in half: 20 plug pigtails for the strip ends and 20 socket pigtails for the panel-to-panel outputs. Five board outputs: left panels (front, front side L, battery door L, deck strip L), right panels (rear, front side R, battery door R, deck strip R), left frame, right frame, underglow. Every panel has its own plug in and plug out, so any panel unplugs on its own and every LED stays individually addressable (one data line per chain, nothing in parallel). About 11 plugs and 6 sockets used', '4.8 stars (215), in stock. Solder and heat-shrink each pigtail onto the 22 AWG run (2026-11-11, L)'),

    ('BUMPERS - FRC style ring, slides off downward', None),
    ('Bumper backing: 1x6 board (3/4 x 5-1/2 in actual), two 8 ft lengths (your call, 2026-11-06)', 'Owned', 2, 0.0, '', 'Structure', 'Four strips joined into one ring with printed corner brackets; 6 #10-32s through the side rails hold it and with them out it slides straight down. Replaces the 1/4 in plywood. Modelled in rev D.2. The ring sits 3/16 in off the chassis all round on printed spacers', 'Rip it to 5 in (the foam height); the CAD keeps the 5 in bumper. Hardware-store lumber, not one of your three sellers; $9 each is a guess [ESTIMATE]. 3/4 in is 1/2 in thicker per side, so the foam is cut 1-13/16 in deep (2 in, less the 3/16 in gap to the chassis) to stay 27.75 in wide under the 28 in door limit.'),
    ('#10-32 pronged tee nuts, Hillman 8991, 3-pack (B00G5J0AQY)', 'Amazon', 2, 4.16, 'https://www.amazon.com/dp/B00G5J0AQY', 'Structure', '6 used: x -80, 0, 80 on each side strip, driven in from the foam side, so the screw from inside the rail pulls the flange into the 1x6. With 3/4 in wood the screws become your 1-1/4 in #10-32s', 'Two 3-packs instead of a 100-pack ($10.95); prong count not stated (2026-11-06, L)'),
    ('Bumper foam: GoTo Foam 5 x 24 x 24 in, 43 ILD firm, 1.8 lb density (your pick, B07SDNP781)', 'Amazon', 1, 19.99, 'https://www.amazon.com/dp/B07SDNP781', 'Structure', 'Replaces the pool noodles: cut strips 5 in tall x 1-13/16 in deep x 24 in (1-13/16 in so the 3/16 in gap between the ring and the chassis keeps the robot 27.75 in wide). The ring needs about 120 in (two 27.75 in ends, two 32.2 in sides): 6 strips of the 12 a block gives', '5 in H x 24 W x 24 L, firm 43 ILD, CertiPUR, made in the USA; in stock. Cut with an electric knife or band saw; butt joints hide under the canvas (2026-11-06, L)'),
    ('Canvas: HYVAKUPPA 12 oz cotton duck, 59 x 72 in (2 yards), white (B0H753QCN1, pick "White", "2 Yards")', 'Amazon', 1, 24.99, 'https://www.amazon.com/dp/B0H753QCN1', 'Cosmetic', 'Bumper covers wrapped round the foam and the 1x6 backing: cut down the middle, two 29.5 x 72 in pieces give 144 in of wrap for the 120 in ring', "Micah's pick (2026-11-11): white, 4.4 stars (29), only 4 left. Was 2 yards of B0H753WH6F at $27.98 (2026-11-11, L)"),

    ("SHIPPING - what the unit prices above don't include", None),

    ('OTHER MATERIALS - your rows (2026-11-06)', None),
    ('PETG filament, white, 4 kg (iSANMATE HF B0FXG1TGYQ)', 'Amazon', 1, 35.99, 'https://www.amazon.com/dp/B0FXG1TGYQ', 'Structure', 'Every printed part, about 6.5 kg sliced: the body frame about 3 kg, the other body prints (clips, posts, brackets, speaker cups) about 2 kg, and about 1.5 kg for the gun (core halves, saddles, caps, end covers, hub, ring pulley), the electronics shelf, battery sleds and smoke parts. One 4 kg bundle plus your 3 kg makes 7 kg, about 0.5 kg for failed prints', "Still the cheapest good white PETG found, $9.00/kg (2026-11-11, L). 2 -> 1 bundle: you have 3 kg (Micah)"),
]

# Micah's Sheet notes (column J) and the answers to them (column K), by item name: kept when the tabs are rewritten
COMMENTS = {}   # all answered and cleared 2026-11-11 (the threads are in git history)

ORDERED = ('Fill check valve',)   # rows ticked Purchased in the Sheet (kept ticked when the tabs are rewritten)


# section title prefix -> order (1: pneumatics, important electronics; 2: materials, LEDs, smoke, audio (Micah, 2026-11-11))
# Part codes (Micah, 2026-11-11: "give every single part a number or code that corresponds to something on the list.
# Acr for white acrylic, ASh for aluminum sheet, ATu for aluminum tubes, AEx for extrusion, and a part and number for
# everything specific corresponding to what system it's a part of ... for 3D printed parts, put 3DP. a pneumatic valve
# could be P24"). A bought or owned part is its system letter and its place in that system on the list (P07); the parts
# we make are coded by material (Acr, ASh, ABr, ATu, AEx, 3DP) and, in Onshape, numbered one by one within it.
SYSTEM_OF = {"PRESSURE SIDE": "P", "RIVETS": "B", "GUN": "P", "DRIVE": "D", "ELEVATION": "E", "CONTROLS": "C", "AUDIO": "S",
             "SMOKE": "F", "FRAME + BODY": "B", "RAILS": "R", "LIGHTS": "L", "BUMPERS": "B", "OTHER MATERIALS": "B",
             "FROM THE OLD CANNON": "P"}
MATERIAL_CODE = (("Frosted acrylic", "Acr"), ("Waterjet brackets", "ASh"), ("Gun cradle plates", "ASh"),
                 ("Breech adapters", "ABr"), ("20x20 T-slot", "AEx"), ("Printed", "3DP"))
SYSTEM_NAMES = {"P": "pneumatics + gun", "D": "drive", "E": "elevation", "C": "controls + power", "S": "sound",
                "F": "fog", "B": "body, bumpers + fasteners", "R": "rails", "L": "lights",
                "Acr": "white acrylic", "ASh": "aluminium sheet", "ABr": "aluminium bar", "ATu": "aluminium tube",
                "AEx": "20x20 extrusion", "3DP": "3D printed"}


def codes():
    """{row name: code}. Codes stay put once given (glacis_bom_codes.json keeps them): a new row takes the next free
    number in its system, so the codes already stamped on Onshape parts and written on parts don't shift."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        prev = json.load(open(os.path.join(here, "glacis_bom_codes.json")))
    except (OSError, ValueError):
        prev = {}
    out, n, sysl = {}, {}, None
    for c in prev.values():
        if c[:1].isalpha() and c[1:].isdigit():
            n[c[0]] = max(n.get(c[0], 0), int(c[1:]))
    for r in ROWS:
        if r[1] is None:
            sysl = next((v for k, v in SYSTEM_OF.items() if r[0].startswith(k)), None)
            continue
        if r[0] in out:                                     # the same part split over both orders keeps one code
            continue
        mat = next((c for k, c in MATERIAL_CODE if r[0].startswith(k)), None)
        if mat:
            out[r[0]] = mat
            continue
        if prev.get(r[0], "")[:1] == sysl and prev[r[0]][1:].isdigit():
            out[r[0]] = prev[r[0]]
            continue
        n[sysl] = n.get(sysl, 0) + 1
        out[r[0]] = f"{sysl}{n[sysl]:02d}"
    return out


ORDER_OF = {"FROM THE OLD CANNON": 1, "RIVETS": 1, "PRESSURE SIDE": 1, "GUN": 1, "DRIVE": 1, "ELEVATION": 1, "CONTROLS": 1,
            "AUDIO": 2, "SHIPPING": 1, "SMOKE": 2, "FRAME + BODY": 2, "RAILS": 2, "LIGHTS": 2, "BUMPERS": 2,
            "OTHER MATERIALS": 2, "LATER": 2, "ALREADY HAVE": 2}
ORDER_TITLES = {1: "Borealis Order 1 - pneumatics, electronics",
                2: "Borealis Order 2 - materials, LEDs, smoke, audio"}


def order_of(section):
    for k, v in ORDER_OF.items():
        if section.startswith(k):
            return v
    raise KeyError(f"section {section!r} has no order")


HAVE = ("Owned", "Stash")       # sellers of rows we already have: listed below each order, not in it


def orders():
    """{1: [rows], 2: [rows]}: each order's sections in ROWS order, with the rows we already have (owned, stash)
    pulled out of their sections into one ALREADY HAVE section at the end; sections left empty are dropped."""
    out, have, cur = {1: [], 2: []}, {1: [], 2: []}, None
    for r in ROWS:
        if r[1] is None:
            cur = order_of(r[0])
            out[cur].append(r)
        elif r[1] in HAVE:
            have[cur].append(r)
        else:
            out[cur].append(r)
    for k in (1, 2):
        rows = out[k]
        rows[:] = [r for i, r in enumerate(rows) if r[1] is not None or (i + 1 < len(rows) and rows[i + 1][1] is not None)]
        if have[k]:
            rows.append(("ALREADY HAVE - owned or FRC stash, $0, nothing to buy", None))
            rows.extend(have[k])
    return out


def _sheet(rows):
    """One order tab, laid out like the Broncobots budget's order tabs (2026-11-09):
    B Item | C Price Per Unit | D Quantity | E Total Price | F Provider | G Notes | H Link | I Purchased? | J Micah's note |
    K the answer, header on row 4, items from row 5.
    Row 2 is the band: C2 "Total Cost (W/ Tax)" =SUM(E5:E)*1.091, E2 "Shipping" (the SHIPPING rows' total, so they
    are not table rows), G2 "Total Cost (W/ Taxes + Shipping)" =F2+D2. Row 3 (added 2026-11-11 by Micah's Mac chat)
    is the per-seller band: B3 "By seller (W/ Tax)", C3 "Amazon" D3 =SUMIF($F$5:$F,C3,$E$5:$E)*1.091, E3
    "Aliexpress" F3 =SUMIF($F$5:$F,E3,$E$5:$E)*1.091, G3 "Other sellers" H3 =ROUND(D2-D3-F3,2); 4 rows frozen.
    Each item's listing notes go in its B cell note."""
    out, kinds, cell_notes, shipping, skip, sub = [], [], {}, 0.0, False, 0.0
    for r in rows:
        if r[1] is None:
            skip = r[0].startswith("SHIPPING")
            if not skip:
                out.append([r[0]] + [""] * 7)
                kinds.append("section")
            continue
        name, seller, q, u, link, typ, purpose, notes = r
        if skip:
            shipping += q * u
            continue
        sub += q * u
        row = 5 + len(out)
        out.append([name, u, q, f"=C{row}*D{row}", seller, purpose, f'=HYPERLINK("{link}","Link")' if link else "",
                    name.startswith(ORDERED)] + list(COMMENTS.get(name, ())))
        kinds.append("item")
        cell_notes[f"B{row}"] = notes
    return dict(rows=out, kinds=kinds, notes=cell_notes, shipping=round(shipping, 2), first_cell="B5",
                codes=[CODES.get(x[0], "") if k == "item" else "" for x, k in zip(out, kinds)],
                last=4 + len(out), items=round(sub, 2))


def main():
    global CODES
    CODES = codes()
    here = os.path.dirname(os.path.abspath(__file__))
    od = orders()
    tot = 0.0
    with open(os.path.join(here, "glacis_bom.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Order", "Name", "Seller", "Amount", "Individual Price", "Price", "Link", "Type", "Purpose",
                    "Alternative/Notes", "Code"])
        for k in (1, 2):
            sub = 0.0
            w.writerow([k, ORDER_TITLES[k]])
            for r in od[k]:
                if r[1] is None:
                    w.writerow([k, r[0]])
                    continue
                name, seller, q, u, link, typ, purpose, notes = r
                sub += q * u
                w.writerow([k, name, seller, q, f"{u:.2f}", f"{q * u:.2f}", link, typ, purpose, notes, CODES[name]])
            w.writerow([k, f"Order {k} total", "", "", "", f"{sub:.2f}"])
            w.writerow([])
            tot += sub
        w.writerow(["", "Total", "", "", "", f"{tot:.2f}"])
    sheets = {str(k): dict(title=ORDER_TITLES[k], **_sheet(od[k])) for k in (1, 2)}
    json.dump(dict(orders=sheets), open(os.path.join(here, "glacis_bom_sheet.json"), "w"))
    json.dump(CODES, open(os.path.join(here, "glacis_bom_codes.json"), "w"), indent=0)
    for k in (1, 2):
        sh = sheets[str(k)]
        print(f"order {k}: {sum(1 for x in sh['kinds'] if x == 'item')} rows, items ${sh['items']:,.2f} + shipping "
              f"${sh['shipping']:,.2f}")
    print(f"{len(ROWS)} rows, total ${tot:,.2f}")


if __name__ == "__main__":
    main()
