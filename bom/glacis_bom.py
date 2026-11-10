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
    ("FROM THE OLD CANNON - reused, $0", None),
    ("Atlantic Valves SZW-25 1 in NPT stainless solenoid valve, NC, Viton (old cannon)", "Owned", 0, 0.00,
     "https://www.electricsolenoidvalves.com/1-inch-12-volt-dc-stainless-steel-electric-solenoid-valve/", "Motion",
     "Spare (rev D.2): the bottom cannon runs to full tank pressure now, and this valve's listing says 0-90 psi", f"{OLD}. 1 in female NPT, Cv 12, 16 W ({V}, L)"),
    ("Grey 1 gal steel ASME air tank with a 1 in NPT end port (old cannon)", "Owned", 0, 0.00, "", "Motion",
     "Not used: too big for the gun (rev D.1); the top chamber is 3 in pipe like the bottom", f"{OLD}; spare"),
    ("Longacre 5 gal aluminum tank, 125 psi (old cannon)", "Owned", 0, 0.00,
     "https://toolsid.com/longacre/5-gal-horizontal-silver-lightweight-air-tank-mpn-52-50305.html", "Motion",
     "Not used: 125 psi is below the 200 psi tank zone", f"{OLD}; spare"),

    ("PRESSURE SIDE - tanks, rear manifold, main valve and in valves (200 psi)", None),
    ('Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT, aluminum (your pick)', 'Aliexpress', 2, 56.60, 'https://www.aliexpress.us/item/3256804024554756.html', 'Motion', 'Two, 12 L: left and right over the front wheels. The CAD test-fit found no room for a third alongside them; 9-15 shots at 120 ft per 150-200 psi charge with a fast top valve, 6-10 with a slow one', f'200 psi, 1/4 NPT female bungs (photos: 2 along the side, one in an end); it ships with welded feet the CAD saddles ignore. $56.60 list; a $46.81 welcome deal shows for new shoppers. 4.9 stars, 90 sold ({V}, L)'),
    ('Relief valve 200 psi, 1/4 NPT male, ASME, ring pull, brass (McMaster 48435K72, set 200 psi)', 'McMaster', 4, 6.67, 'https://www.mcmaster.com/48435K72/', 'Motion', 'Tank zone (rear manifold; its ring at the rear panel is the hand dump), the valve cross, and both chambers (the ring is each chamber\'s bleed)', f'1/4 NPT male, ASME BPVC VIII, silicone seal, -15 to 250 F; set 200 psi in the page\'s Set Pressure box (125 and 200 are both offered at $6.67) ({V}, L)'),
    ("Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT (FUSCH)", "Amazon", 3, 17.69, "https://www.amazon.com/dp/B0CRQWKDNC",
     "Electrical", "One part number for all three: tank and both chambers (rev C.3; the 0-200 psi one is gone)",
     f"1/8-27 NPT male (photo), 0.5-4.5 V on 5 V, +/-1% FS, 316 stainless, ceramic cell, harness included ({V}, L)"),
    ('Fill plug: 303 stainless industrial (M-style) plug, 1/4 coupling, 1/4 NPTF female (McMaster 6718K52)', 'McMaster', 1, 9.97, 'https://www.mcmaster.com/6718K52/', 'Motion', 'Fill port outside the rear panel (Brophy Borealis "better plug"): threads onto the 1-1/2 in nipple through the panel, and your universal couplers (EVOULTES kit) snap on. Stainless, so it will not rust or gall like the plated Milton 728', f'1/4 NPTF female, open flow, 300 psi, "delivers tomorrow" ({B2}, L). Still an open plug, so the check valve behind it stays. No M-style plug with its own shut-off exists: only sockets have one'),
    ('Interior quick disconnects: ISO 7241-1 B plug, 1/4, steel, both halves self-sealing (McMaster 95825K86)', 'McMaster', 5, 14.57, 'https://www.mcmaster.com/95825K86/', 'Motion', 'Brophy Borealis: each subsystem comes apart without venting the rest. 5 pairs: tank line to the main valve, rear manifold to each in valve (2), each in valve to its chamber service loop (2). ISO-B halves will not mate with the M-style fill, so nobody plugs a shop hose into an interior line', f'1/4 NPTF female, 3,500 psi, zinc-plated steel, valved ({B2}, L; stock not shown). Listed for hydraulics: Buna-N poppets are fine for 200 psi air (our judgment). Vent one side before reconnecting. Cheaper: eBay QD0250 ISO-B 1/4 NPT set $13.99 + ship, no rating stated [UNVERIFIED]: buy one and gauge the thread first'),
    ('Interior quick disconnects: ISO 7241-1 B socket, 1/4, sleeve lock, steel (McMaster 95825K81)', 'McMaster', 5, 34.15, 'https://www.mcmaster.com/95825K81/', 'Motion', 'The other half of each of the 5 pairs above: socket on the supply side, so the live side is the one that seals hardest', f'1/4 NPTF female, 3,500 psi, zinc-plated steel, valved ({B2}, L; stock not shown). Brass version 52495K41/52495K61 is $59.88 a pair'),
    ('DOT push-to-connect 1/4 tube x 1/4 NPT male, straight, 10-pack (Boeray) - for the quick disconnects', 'Amazon', 1, 19.99, 'https://www.amazon.com/dp/B0D8PX7Z94', 'Motion', 'Both ISO-B halves are female 1/4 NPT: a male push-to-connect in each of the 10 halves puts them inline on the nylon tube', 'Same listing as the Boeray 10-pack below (the existing 8-used pack has no spares for these) [stock not re-checked today: Amazon blocks automated checks]'),
    ('Fill check valve, brass, 1/4 MNPT x 1/4 MNPT, 250 psi (American Made B076K8SLBZ)', 'Amazon', 1, 15.87, 'https://www.amazon.com/dp/B076K8SLBZ', 'Motion', 'Behind the panel, between the female elbow and the street elbow. Holds the tanks shut when the hose comes off (a plug is an open pipe)', f'Male on both ends (listing photo), not FNPT x MNPT as the old note hoped. 250 psi, 250 F, fluorocarbon O-rings, brass. Fit it with the flow arrow pointing in ({V}, L)'),
    ("In valves: Aignep 02F 2/2 NC direct-acting 12 V DC, 1/4 NPTF, 2 mm (02F03102N0N10201)", "Hose Warehouse", 2, 41.36,
     "https://hosewarehouse.com/products/02f03102n0n10201-aignep-fluidity-series-fluidity-02f-directacting-solenoid-valve-2-2-nc-nbr-seal-1-4-nptf-2-mm-12v-dc",
     "Electrical", "One in valve per chamber, metering it against its transducer; they now hold tank pressure all session",
     f"1/4 FNPT both ends, 2 mm orifice, Kv 0.10, 0-35 bar (507 psi) on the 8 W DC coil, NBR seal, Class H coil; $41.36 (list $56.18). Not at the three sellers: Amazon's $18-20 brass valves don't state 200 psi ({V}, L)"),
    ("Main valve: 1/4 NPT brass ball valve, FNPT x FNPT, 600 WOG (the old cannon's if it fits)", "Owned", 1, 0.00,
     "https://www.zoro.com/dwyer-instruments-brass-ball-valve-600-psi-full-port-14-dbv-00/i/G907144217/", "Motion",
     "Manual tank shut-off (rev C.3): open for a session, closed for transport and before working on the gun; handle at the rear panel",
     "Reuse the old cannon's if it's 1/4 NPT and stamped 200 psi or more (600 WOG is typical); else Dwyer DBV-00 $6.55 at Zoro (2026-11-03, S)"),
    ("1/4 NPT brass cross (4-way), 3-pack (ChillWaves)", "Amazon", 2, 12.99, "https://www.amazon.com/dp/B0FCMV6ML9",
     "Motion", "Rear manifold, the valve cross, and one on the back of each chamber (replaces the 5-port blocks)",
     "NPT, 1200 psi (2026-11-02, L)"),
    ("1/4 NPT brass close nipple 7/8 in, 5-pack (Legines)", "Amazon", 2, 7.99, "https://www.amazon.com/dp/B07L5G7CN3",
     "Motion", "Rear manifold, the three valves to the valve cross, chamber bushings to their crosses", "NPT, 1200 psi (2026-11-02, L)"),
    ("1/4 NPT brass nipple 1-1/2 in (you think you have one)", "Owned", 1, 0.00, "https://www.amazon.com/dp/B07L5HNKQC",
     "Motion", "Through the rear panel: the female plug outside, the female elbow inside. A check valve's 10 mm male end is too short to cross the panel itself", "If not: Legines 5-pack $10.99, or one loose at a hardware store"),
    ('1/4 NPT brass 90 deg elbow, FNPT x FNPT, 2-pack (ChillWaves B0B7544Y62)', 'Amazon', 1, 7.99, 'https://www.amazon.com/dp/B0B7544Y62', 'Motion', 'Fill line behind the panel: the nipple in one side, the male x male check valve in the other (1 spare)', f'1/4 NPT female both ends, barstock brass, 1,200 psi; 8 left ({V}, L)'),
    ('1/4 NPT brass street elbow 90 deg, MNPT x FNPT, 5-pack (B0D8KV5CMM)', 'Amazon', 1, 11.99, 'https://www.amazon.com/dp/B0D8KV5CMM', 'Motion', '2 used: main valve off the rear manifold, and the check valve into the rear manifold (3 spare). The CAD had them; the parts list did not', f'Forged brass, 1/4 MNPT x 1/4 FNPT; no psi on the listing (forged brass 1/4 street elbows are commonly 1,000+ psi: check the box) ({V}, L)'),
    ("1/4 NPT brass hex plug, 5-pack (Legines)", "Amazon", 2, 7.99, "https://www.amazon.com/dp/B0757HRRX9",
     "Motion", "Every open port (rev D.2 audit): 2 rear-manifold ends + up to 3 spare bungs per tank (photos show 3-4 ports; one is the outlet) = 8 of 10. The valve cross and chamber crosses have no open port", f"1/4 NPT male, 1200 psi. Put one tank's lowest plug where water collects: it's the drain ({V}, L)"),
    ('1/4 NPT male x 1/8 NPT female hex bushing, nickel-plated brass (McMaster 9151K91)', 'McMaster', 3, 2.16, 'https://www.mcmaster.com/9151K91/', 'Motion', '3 transducers', 'Was $12.98 for two Amazon 2-packs (2026-11-04, L)'),
    ('DOT nylon air-brake tube 1/4 in OD, SAE J844, 25 ft (B0DT687V3Q)', 'Amazon', 1, 16.16, 'https://www.amazon.com/dp/B0DT687V3Q', 'Motion', 'Every air line, including the two service loops to the gun (about 15 ft used)', f'1/4 OD, SAE J844, max 1,150 psi ({V}, L)'),
    ("DOT push-to-connect 1/4 tube x 1/4 NPT, straight, 10-pack (Boeray)", "Amazon", 1, 19.99, "https://www.amazon.com/dp/B0D8PX7Z94",
     "Motion", "8 used (CAD count with two tanks): rear manifold (2), main valve, valve cross, both in valves, both chamber fill ports", f"1/4 tube x 1/4 NPT male, 250 psi, SAE J1131 + J844, brass; 18 left ({V}, L)"),
    ("DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT, 5-pack (Boeray)", "Amazon", 1, 17.99, "https://www.amazon.com/dp/B0D8Q2618F",
     "Motion", "2 used: tank outlets (3 spare)", f"1/4 tube x 1/4 NPT male, 250 psi, SAE J1131 ({V}, L)"),
    ('Pipe thread sealant, RectorSeal T Plus 2 (B0002YPAFY)', 'Amazon', 1, 8.78, 'https://www.amazon.com/dp/B0002YPAFY', 'Tool', 'Every NPT joint', "Skip it if you have pipe dope or PTFE tape (Home Depot's $4.25 isn't one of your sellers) (2026-11-04, L)"),
    ('1 in cam-buckle strap 1 m, 4-pack', 'Aliexpress', 1, 5.2, 'https://www.aliexpress.us/item/3256813026868231.html', 'Structure', '4 used: two per side tank', 'Free shipping; 12 sold, 5 stars. Was $8.99 on Amazon (2026-11-04, L)'),
    ("GUN (rev D.2) - 3 in pipe chambers: top 1.59 L, bottom 1.35 L, both on HSV04 valves to 190 psi; 36 in barrels", None),
    ("Firing valves: U.S. Solid USS-HSV04, 1 in NPT, 12 V DC, NC, pilot-operated, 1-50 bar (725 psi), PTFE seal", "Other", 2, 98.19,
     "https://ussolid.com/products/high-pressure-solenoid-valve-1-12v-dc-brass-50-bar-300-high-pressure-high-temperature-solenoid-valve-html",
     "Electrical", "One per cannon (rev D.2: the bottom one too, so both run to full tank pressure, capped at 190 under the 200 psi reliefs)",
     f"In stock, one version only. Thread is listed as NPT / G (a dual thread, no option to pick), so true NPT is NOT confirmed: test-fit a 1 in NPT nipple before trusting it at 190 psi. Cv 11.67, 25 mm, PTFE seal, junction box. Opening time unpublished: bench-test before cutting barrels ({V}, L)"),
    ('Chambers: 3 x 1 black malleable reducing coupling, 150-300 psi (MSI Products A203084816)', 'Global Industrial', 4, 27.95, 'https://www.globalindustrial.com/p/3-x-1-150lb-black-malleable-iron-reducing-coupling-150-300-psi', 'Motion', 'Both ends of both chambers, which run to 190 psi. 4.28 in across, which sets the barrel spacing', f'Same class as the Supply Giant one ("up to 150 lb" on Amazon), but this listing states a 150-300 psi working rating (ASME B16.3 gives Class 150 malleable 300 psi up to 150 F); NPT per ASME B1.20.1. Not one of your sellers; shipping not checked ({V}, L)'),
    ('Bottom chamber: 3 in Sch 40 black steel nipple x 10 in (Supply Giant OQCM3010)', 'Amazon', 1, 28.99, 'https://www.amazon.com/dp/B016Y8C7D4', 'Motion', 'Bottom chamber body: about 1.35 L with the couplings, 3.5 in OD', f'3 MNPT both ends, Sch 40 black steel; the listing states no psi ({V}, L)'),
    ('Top chamber: 3 in Sch 40 black steel nipple x 12 in (Supply Giant OQCM3012)', 'Amazon', 1, 26.99, 'https://www.amazon.com/dp/B016Y8CB1C', 'Motion', 'Top chamber body: about 1.59 L with the couplings', f'3 MNPT both ends, Sch 40 black steel; the listing states no psi ({V}, L)'),
    ('1 in MNPT x 1/4 FNPT hex bushing, 304 stainless, 350 psi (B0C7N73YVZ)', 'Amazon', 2, 7.99, 'https://www.amazon.com/dp/B0C7N73YVZ', 'Motion', 'Back of each chamber to its brass cross', f'Replaces the Supply Giant malleable one, whose listing says "up to 150 lb" (the top runs to 190). 350 psi max working pressure ({V}, L)'),
    ('1 in NPT Sch 40 steel nipple x 1-1/2 in (McMaster 44615K416)', 'McMaster', 4, 3.13, 'https://www.mcmaster.com/44615K416/', 'Motion', 'Chamber to valve, valve to breech adapter (2 per cannon)', 'Was $4.05 on Amazon (2026-11-04, L)'),
    ("1 in - 11-1/2 NPT pipe tap", "Amazon", 1, 16.99, "https://www.amazon.com/dp/B0BB3H8ZHP", "Tool",
     "Cuts the 1 in NPT threads inside the two aluminum breech adapters (stash 6061 bar)",
     f"Borrow one if the shop has it. 4.6 stars ({D}, S)"),
    ('MOSFET switch module 5-36 V 15 A, 3.3-20 V trigger, 10-pack (B0GGHY11RL)', 'Amazon', 2, 6.29, 'https://www.amazon.com/dp/B0GGHY11RL', 'Electrical', '11 used: firing valves (2), in valves (2), fog heater (2), fog pump, blower, light bar (PWM), and the contactor coil twice in series (one channel for the main controller, one for the safety node); 9 spare', f'Triggers from 3.3 V, so the controller drives them directly (no buffer). Flyback diode across each valve coil; was two 6-packs $10.98 ({V}, L)'),
    ('Barrels: clear extruded polycarbonate tube 3.00 in OD x 2.75 ID x 1/8 wall x 36 in (K-mac B09NLCGBWB)', 'Amazon', 2, 45.81, 'https://www.amazon.com/dp/B09NLCGBWB', 'Structure', 'Two 36 in barrels as they come. Six smoke holes each', f'Same tube as McMaster 8585K38 ($66.05), free delivery; only 2 left. No pressure rating (none published at McMaster either); clamp it. Not acrylic: it shatters ({V}, L)'),
    ("SMOKE - custom 12 V fogger (one 200 W core, room for a second), barrel collar, front and rear trail vents", None),
    ('Fog heater core 12 V 200 W, cast heat exchanger 97 x 32 x 36 mm', 'Aliexpress', 1, 26.38, 'https://www.aliexpress.us/item/3256805556610953.html', 'Cosmetic', 'The fogger: about 17.5 A on its own 30 A PDH channel', f'$24.39 + $1.99 shipping at your logged-in price now (was $34.39). No thermostat or fuse on the listing; the KSD301 below is the backstop ({V}, L)'),
    ("Fog fluid pump: Kamoer NKP 12 V peristaltic, 70 mL/min", "Amazon", 1, 9.98, "https://www.amazon.com/dp/B07GWJ78FN",
     "Cosmetic", "Feeds the core from the printed tank (a second one comes with a second core)", f"Fine running dry; back-pressure [UNVERIFIED] ({D}, S)"),
    ('Thermocouple amp MAX6675 + K-type probe', 'Aliexpress', 1, 2.03, 'https://www.aliexpress.us/item/3256813189448378.html', 'Electrical', 'Core temperature to the main controller (SPI); hold 220-240 C, firmware cut at 245 C', 'Was $7.69 on Amazon (2026-11-04, L)'),
    ('Fluid level: XKC-Y25-NPN non-contact capacitive level switch, 5-12 V', 'Aliexpress', 1, 4.74, 'https://www.aliexpress.us/item/3256805957656708.html', 'Electrical', 'Stuck to the outside of the printed tank at about 20%: low-fluid warning, and the pump stops about a minute later', 'NPN (5-12 V) option; 5,000+ sold. Reads through up to 20 mm of plastic, so the tank has no hole (2026-11-04, L)'),
    ('DS18B20 waterproof temperature probe, 1 m, 5-pack', 'Aliexpress', 1, 4.4, 'https://www.aliexpress.us/item/3256808611802365.html', 'Electrical', '1-Wire on one controller pin: fogger box by the printed tray (heater off at 70 C), electronics shelf, battery bay; 2 spare', 'Was $9.49 on Amazon (2026-11-04, L)'),
    ('Thermal cutout KSD301 250 C normally closed', 'Aliexpress', 2, 0.86, 'https://www.aliexpress.us/item/2251832771638391.html', 'Electrical', 'Hardware backstop on the core, in its relay coil line (one spare)', '1,000+ sold; self-resetting, so firmware latches the fault (2026-11-04, L)'),

    ('12 V 5015 blower, 2-pack (Gdstime, sleeve bearing)', 'Aliexpress', 1, 6.56, 'https://www.aliexpress.us/item/3256807420529511.html', 'Cosmetic', 'Pushes the fog from the cores into the splitter and down the three tubes', 'Was $8.99 on Amazon (2026-11-04, L)'),
    ('Silicone tube 3 mm ID x 5 mm OD (per metre)', 'Aliexpress', 2, 2.44, 'https://www.aliexpress.us/item/3256808335149485.html', 'Cosmetic', 'Tank -> pumps -> core inlets (zip-tied on the 2.5 mm tubes)', 'Was $5.99 on Amazon (2026-11-04, L)'),
    ('Fog fluid, water-based, medium density, 1 gal (FogUp B09T5X72DH)', 'Amazon', 1, 17.95, 'https://www.amazon.com/dp/B09T5X72DH', 'Cosmetic', 'Fills the printed tank about 9 times', f'Four times the FogWorx quart for the same money. Never oil: it cokes the 2.5 mm core tube ({V}, L)'),
    ("Flexible fog tube (yours, 2)", "Owned", 2, 0.00, "", "Cosmetic", "Splitter to the front and rear vents (both down through the bellypan)", "Owned"),
    ("Silicone tube 3/8 in ID x 1/2 in OD, 10 ft", "Amazon", 1, 12.99, "https://www.amazon.com/s?k=silicone+tubing+3%2F8+ID+1%2F2+OD",
     "Cosmetic", "The gun's smoke line: splitter, up through the well floor, inside the core, along the barrels to the collar",
     f"Fits the valley between the barrels; any food-grade silicone [UNVERIFIED price] ({D}, L)"),
    ("Printed smoke parts: tray, 400 mL tank, 1-to-3 splitter, one-piece smoke collar, front and rear vents (PETG/ASA)", "Owned", 1,
     0.00, "", "Cosmetic", "Ducts, vents and the barrel collar", "Filament assumed owned; the cores sit on an aluminum bracket, never on a print"),

    ("DRIVE - Falcons; the old 9 in mecanum wheels for now (the printed 10 in wheels later)", None),
    ("Falcon 500 (owned)", "Stash", 4, 0.00, "", "Motion", "One per wheel, plain PWM from the main controller (no gate: the contactor is the cut-off)", "Owned"),
    ("12T HTD 15 mm Falcon pulley (WCP-0319)", "Stash", 4, 0.00, "https://wcproducts.com/products/wcp-0319",
     "Motion", "Falcon 12T -> 116T printed into the hub (9.67:1)", STASH + " ($7.99 at WCP)"),
    ("Old 9 in mecanum wheels (owned, for now)", "Owned", 4, 0.00, "", "Motion",
     "Stand-ins for the printed 10 in vector wheels (Micah, 2026-11-04); belts and hubs depend on how they mount",
     "The printed-wheel parts (608s, M8 rod, nylocs, 1/4-20 hub bolts, 140T belts) are off the list until the printed wheels come back"),
    ("Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)", "Stash", 12, 0.00, "https://wcproducts.com/products/wcp-0783",
     "Motion", "2 per wheel axle (inner + outer rail), 4 at the pivot", STASH + " ($2.99 each)"),
    ("1/2 in hex shaft: 4 wheel axles (6 in) + 2 pivot stubs", "Stash", 1, 0.00, "", "Motion",
     "Live axles tapped 10-32 both ends; one steel stub per cradle plate on the pivot axis", STASH),
    ("ELEVATION - 312 rpm FTC motor on a Spark MAX (backdrives when off), pot for the angle", None),
    ("goBILDA 5203-2402-0019 Yellow Jacket 19.2:1 (312 rpm), 8 mm REX (owned)", "Owned", 1, 0.00,
     "https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-19-2-1-ratio-24mm-length-8mm-rex-shaft-312-rpm-3-3-5v-encoder/",
     "Motion", "16T -> 112T belt to the right pivot stub (7:1, about 45 rpm free at the gun, 16.7 N*m stall)",
     "Owned: Micah has every goBILDA motor (2026-11-04)"),
    ("REV Spark MAX (owned)", "Stash", 1, 0.00, "", "Electrical", "Drives the goBILDA in brushed mode from PWM", "Owned"),
    ('HTD 5M 9 mm belt, 150T (750 mm) (uxcell B0DF57XRZ8)', 'Amazon', 1, 7.81, 'https://www.amazon.com/dp/B0DF57XRZ8', 'Motion', 'goBILDA 16T pinion to the printed 112T pivot pulley (CAD loop is exactly 750 mm)', "9 mm to match goBILDA's HTD pulleys (AliExpress only has 10 mm); was $8.99 at WCP (2026-11-04, L)"),
    ('10k linear pot RK097G, 6 mm knurled shaft, 5-pack', 'Aliexpress', 1, 0.64, 'https://www.aliexpress.us/item/2251832817477625.html', 'Electrical', 'Gun angle on the end of the left pivot stub, to the controller ADC', 'About 300 deg travel (RK097 type; not stated on the listing); 495 sold. Was $10.70 for a Bourns (2026-11-04, L)'),
    ("FRAME + BODY - box tube, printed frame, recessed acrylic", None),
    ('Heat-set inserts M4 x 6, brass, OD 5 mm, 100 pcs', 'Aliexpress', 1, 4.04, 'https://www.aliexpress.us/item/2251832656703778.html', 'Structure', 'Panel clips, speaker cups (8), light bar liner, standoffs: 4.7 mm hole, 6.5 deep', 'Was $15.97 for a 400-piece mixed kit (2026-11-04, L)'),
    ('Heat-set inserts M4 x 4, brass, OD 5 mm, 100 pcs (same listing, M4X4X5mm)', 'Aliexpress', 1, 3.56, 'https://www.aliexpress.us/item/2251832656703778.html', 'Structure', 'The 12 clips where two neighbouring panels\' clip screws would meet inside a node, or a slanted face is close: 4.6 mm deep', 'Logged-in price; ships with the M4 x 6 lot (2026-11-04, L)'),
    ('Heat-set inserts M5, brass (same listing, M5 option)', 'Aliexpress', 1, 4.04, 'https://www.aliexpress.us/item/2251832656703778.html', 'Structure', '8 for the chamber caps (2 x M5 each; the screws are stash)', "M5 option's price assumed the same as M4 [UNVERIFIED] (2026-11-04)"),
    ("M4 x 12 button head, 304 stainless, 100 pcs", "Amazon", 1, 7.40, "https://www.amazon.com/dp/B0DKXQQPWS",
     "Structure", "Frame-joint cross screws (35, self-tapping into the tenon's pilot) and standoffs", f"Only 2 left; backup 12.9 black-oxide B0CTH3FQLD $8.86 ({D}, L)"),
    ("M4 x 8 button head, 304 stainless, 100 pcs (B0DKXNTRTW)", "Amazon", 1, 6.74, "https://www.amazon.com/dp/B0DKXNTRTW",
     "Structure", "Panel clips into M4 x 6 inserts, speaker cups (8), light bar liner", "4.4 stars (2026-11-04, L)"),
    ("M4 x 6 button head, 304 stainless, 100 pcs (B0FPG4WXY6)", "Amazon", 1, 6.99, "https://www.amazon.com/dp/B0FPG4WXY6",
     "Structure", "The 12 short clips (into M4 x 4 inserts)", "4.7 stars (2026-11-04, L)"),
    ("Foam tape 1/4 in x 1/16 in closed cell, 65 ft (B07Z4QYYDK)", "Amazon", 1, 11.99, "https://www.amazon.com/dp/B07Z4QYYDK",
     "Structure", "About 13 m on the acrylic ledges, so the clips clamp the panels instead of letting them rattle (the rebate is 0.7 mm deeper for it)",
     "Yotache; 4.4 stars (2026-11-04, L)"),
    ("Frosted acrylic 1/8 in (owned): 9 panels (the front is two halves round the light bar pocket)", "Owned", 9, 0.00, "", "Cosmetic",
     "Recessed in the printed frame, held by corner clips; cut 1 mm under the rebate outline all round",
     "Owned; outlines in the Onshape panels tab. Cut them after a dry assembly of the printed frame"),
    ("Printed body frame: 45 pieces incl. two front cheeks, 51 tapered tenons (33 cross-screwed, 18 glued), 38 corner clips, "
     "2 light bar pocket liner halves, 14 underglow brackets, 14 frame mount posts, 2 turret tower brackets, 4 bumper corner brackets (PETG)",
     "Owned", 1, 0.00, "", "Structure",
     "Holds the panels; a strip tunnel down every member (the frame glows); each window wall chamfers from the acrylic ledge to its LED strip",
     "Filament assumed owned. Frame pieces: 0.6 mm nozzle, 2 walls, 10% gyroid; mounts, brackets, clips: 4 walls, 25%. "
     "Plates, PETG and hours in docs/glacis/print_plan.md"),
    ("#10-32 heat-set inserts, brass, 3/8 in, 60 pcs (B0DFWTJYHK)", "Amazon", 1, 9.99, "https://www.amazon.com/dp/B0DFWTJYHK",
     "Structure", "46 used: 16 in the frame (8 in tabs on the side walls' inner faces, 6 in the end walls, 2 in the deck over the towers), "
     "14 in the posts' feet, 16 in the bumper corner brackets",
     "6.3 mm hole, 10.5 deep; 4.8 stars (2026-11-04, L)"),
    ("#10-32 screws (yours): 1/2 in and 2-1/2 in", "Owned", 1, 0.00, "", "Structure",
     "1/2 in x 42: frame to posts and tower decks (16, up from each post's outer pocket once the bumper ring is off), bumper ring to the "
     "side rails (6, from inside the rail), bumper corner brackets (16), tower brackets into rivnuts (4). 2-1/2 in x 14: posts to rails "
     "(up through the rail and gusset)", "Owned: the geometry is set for 1/2, 1-1/4 and 2-1/2 in (2026-11-04)"),
    ("#10-32 rivnuts, aluminium, flat head, 50 pcs (B0CGLPT66M)", "Amazon", 1, 7.99, "https://www.amazon.com/dp/B0CGLPT66M",
     "Structure", "4 in the turret towers' outer walls for the tower brackets (nothing pokes into the gun well)",
     "Grip range for 1/16 in wall not listed [UNVERIFIED]; needs a rivnut tool (most FRC shops have one). 4.6 stars (2026-11-04, L)"),
    ("Epoxy for the 16 glued frame joints (5-minute, any brand)", "Owned", 1, 0.00, "", "Tool",
     "The tapered tenons on the filled LED corners (no cross screw: every way in for a screw head is a surface seen through the acrylic), "
     "and the one glued split across the gun well's front. Push a strip offcut through the tunnel across each joint while it cures",
     "Owned / shop stock"),
    ("RAILS - 20x20 T-slot add-on rails (Brophy Borealis): two on the deck, two on the gun, for add-ons later", None),
    ("20x20 T-slot extrusion (your spares): 2 x 470 mm on the deck, 2 x 300 mm inside the gun's cradle plates", "Owned", 4, 0.00, "", "Structure",
     "Deck: one each side of the gun well, outboard of the pivot's bearing blocks, on the well-edge frame member. Gun: one inside each cradle plate along its top edge, flush with it. All mirrored about the centreline and clear of the 0-45 deg swing", "Yours (Micah, 2026-11-10: 'I have a lot to spare'). Cut square; the CAD lengths are the cut lengths"),
    ("M5 drop-in T-nuts for 20-series (6 mm slot), nickel-plated, 50 pcs", "Aliexpress", 1, 2.90, "https://www.aliexpress.us/item/3256806678200822.html", "Structure",
     "12 used: 3 per rail. Drop in from the side after the rail is placed", "$2.90 ($1.09 new-shopper price) (2026-11-09, L)"),
    ("M5 button head screws, ISO 7380, 10 mm and 30 mm, 20 pcs each", "Aliexpress", 2, 1.09, "https://www.aliexpress.us/item/3256808326585307.html", "Structure",
     "6 x M5 x 10 through the cradle plates into the gun rails; 6 x M5 x 30 up through the deck member (from inside the gun well) into the deck rails",
     "Price per length [UNVERIFIED]: $1.09 showed for the default 50 mm option (2026-11-09). Stash M5s work too"),

    ("LIGHTS - panel loops, glowing frame, underglow, front light bar", None),
    ('WS2812B LED strip 5 mm wide, 2020 LEDs, 100 LED/m, 5 m', 'Aliexpress', 2, 14.16, 'https://www.aliexpress.us/item/3256806570121908.html', 'Electrical', '7.6 m: one piece per frame member (the front and rear bottom members have no tunnel: a jumper wire runs round them), LEDs out, bent the easy way up into the feed slot at each end and soldered to the next at the slot mouth', '$13.61 a reel + $1.09 shipping split over the two; 77 sold, 5 stars. Logged-in price (2026-11-04, L)'),
    ('WS2812B LED strip 10 mm, 60 LED/m, 5 m, black PCB, IP30', 'Aliexpress', 3, 7.33, 'https://www.aliexpress.us/item/3256807802893080.html', 'Electrical', '11.2 m: one closed loop per panel on its window wall, centred 25 mm behind the acrylic, LEDs aimed across the panel; 2.5 m of underglow under the bumpers from the rest of the third reel', '3,000+ sold, 4.8 stars, Choice. Logged-in price; was $13.99 a reel on Amazon (2026-11-04, L)'),
    ('Front light bar: Zmoon 12 in single-row LED bar, 72 W spot/flood combo, 12/24 V (your pick)', 'Amazon', 1, 17.99, 'https://www.amazon.com/dp/B07SWZ1LMM', 'Electrical', 'Recessed in a pocket in the front slant (Brophy Borealis), 20 mm behind the face, aimed straight ahead, with a 3 in blank band above it in the pocket for crowd sensors later; held by its two back bolts through a printed liner. The main controller switches it (and can PWM-dim it) through a MOSFET channel; about 6 A at 12 V', f'72 W, 8000 lm claimed; now $17.99. Size not listed: modelled 330 x 30 x 45 mm [UNVERIFIED] ({V}, L)'),
    ("12/24 V -> 5 V 20 A buck, potted", "Amazon", 1, 15.99, "https://www.amazon.com/dp/B089M5R3NJ",
     "Electrical", "LEDs only, on a PDH channel, so they go dark with the PDH",
     "About 1,680 LEDs: cap them at about 20% white in firmware; inject 5 V at every frame node (2026-11-02, L)"),

    ("BUMPERS - FRC style ring, slides off downward", None),
    ("Bumper backing: 1x6 board (3/4 x 5-1/2 in actual), two 8 ft lengths (your call, 2026-11-06)", "Other", 2, 9.00, "", "Structure",
     "Four strips joined into one ring with printed corner brackets; 6 #10-32s through the side rails hold it and with them out it slides straight down. "
     "Replaces the 1/4 in plywood. Modelled in rev D.2",
     "Rip it to 5 in (the foam height); the CAD keeps the 5 in bumper. Hardware-store lumber, not one of your three sellers; $9 each is a guess [ESTIMATE]. 3/4 in is 1/2 in thicker per side, so cut the foam 2 in deep "
     "(not 2.5) to stay 27.75 in wide under the 28 in door limit."),
    ("#10-32 pronged tee nuts, Hillman 8991, 3-pack (B00G5J0AQY)", "Amazon", 2, 4.16,
     "https://www.amazon.com/dp/B00G5J0AQY", "Structure",
     "6 used: x -80, 0, 80 on each side strip, driven in from the foam side, so the screw from inside the rail pulls the flange into the 1x6. "
     "With 3/4 in wood the screws become your 1-1/4 in #10-32s",
     f"Two 3-packs instead of a 100-pack ($10.95); prong count not stated ({V}, L)"),
    ('Bumper foam: GoTo Foam 5 x 24 x 24 in, 43 ILD firm, 1.8 lb density (your pick, B07SDNP781)', 'Amazon', 1, 19.99, 'https://www.amazon.com/dp/B07SDNP781', 'Structure', 'Replaces the pool noodles: cut 2 in strips, each 5 in tall x 2 in deep x 24 in (2 in, not 2.5, because the 1x6 backing is 1/2 in thicker). The ring needs about 120 in (two 27.75 in ends, two 32.2 in sides): 6 strips of the 12 a block gives', f'5 in H x 24 W x 24 L, firm 43 ILD, CertiPUR, made in the USA; in stock. Cut with an electric knife or band saw; butt joints hide under the canvas ({V}, L)'),
    ('Heavy-duty 12 oz cotton duck canvas, 59 in wide (per yard) (B0H753WH6F)', 'Amazon', 2, 13.99, 'https://www.amazon.com/dp/B0H753WH6F', 'Cosmetic', 'Bumper covers wrapped round the foam and the 1x6 backing', "Pick white if it's offered [UNVERIFIED colour]; the $10/yd one was canvasetc.com (2026-11-04, S)"),
    ("CONTROLS, FAILSAFE + POWER - back bottom bay", None),
    ("FRC 12 V battery + charger (owned)", "Stash", 2, 0.00, "", "Electrical", "One per side on its own slide-out sled, each through its own battery relay (below)", "Owned"),
    ("REV PDH + ATO breakers, 120 A main breaker, SB50s, wire and lugs", "Stash", 1, 0.00, "", "Electrical", "Main power",
     "Owned / " + STASH),
    ('Anderson SB50 flush-mount bracket + dust cover kit', 'Aliexpress', 1, 3.68, 'https://www.aliexpress.us/item/3256806307889526.html', 'Electrical', 'Standby charge / shore-power port, bottom of the rear panel (a stash SB50 housing goes in it)', '5 stars, 68 sold. Was $9.99 (2026-11-04, L)'),
    ('Main controller: Waveshare ESP32-P4-Module-DEV-KIT, ESP32-P4 + ESP32-C6 (B0FDWZ6KWT)', 'Amazon', 1, 28.79, 'https://www.amazon.com/dp/B0FDWZ6KWT', 'Electrical', 'One board does it all (rev D.2.1): web UI and WebSocket on 2.4 GHz WiFi 6 (the C6 on the board), valves and chamber metering, elevation loop, every LED strip, audio mixing out of its own speaker amp into the siren amp, MIPI camera later, lidar on a UART, the PDH contactor and both battery relays. 5 V from the logic rail on its SH1.0 power header', f'Micah picked it 2026-11-09 over the WTDKP4C5-S1 ($29.29) for the USB plugs: 1 USB-A + 2 USB-C, RJ45 (PoE header), a 40-pin Pi-style header with 28 GPIO (takes Pi HATs), ES8311 codec + NS4150B 2 W speaker amp + mic, speaker included. 2.4 GHz only, so the access point runs 2.4 GHz. Sold by UeeKKoo, 3.6 stars (10); Waveshare store $19.99 + shipping, AliExpress from $27.89 ({W}, L)'),
    ('ADS1115 16-bit 4-channel ADC module, I2C, 2-pack (B0DZSP4CG8)', 'Amazon', 1, 7.99, 'https://www.amazon.com/dp/B0DZSP4CG8', 'Electrical', '#1: the three pressure transducers + the 5 V reference. #2: battery A, battery B, the bus and the PDH volts, so the battery relays compare the two packs to a few mV. Both on I2C to the main controller (its own ADC only reads the pot)', f'Settled call: ESP32 ADCs are too nonlinear for pressure. Two for the price of the single (B0FLPZMQJY, $7.99); 5 stars (3), 50+ bought last month ({W}, L)'),
    ('PWM expander: PCA9685 16-channel, I2C (Dorhea B07RMTN4NZ)', 'Amazon', 1, 5.99, 'https://www.amazon.com/dp/B07RMTN4NZ', 'Electrical', '12 of 16 used: drive PWM to the 4 Falcons and the elevation Spark MAX, fog heater (2), pump, blower, light bar, both battery relays. Valves, LED data and the contactor stay on the board\'s own pins (timing and safety). OE is pulled up and held low by the controller, so a reset or crash turns every output off', f'The 28 header pins can\'t take all ~38 D.2 signals; this frees 12. One PWM frequency for all 16 (about 200 Hz suits the Falcons, Spark MAX and light bar; on/off loads use full-on/full-off). 4.5 stars (104), 200+ bought last month ({W}, L)'),
    ("ESP32-S3 boards (your two)", "Owned", 2, 0.00, "", "Electrical",
     "1: safety node (ESP-NOW to the remote; holds the PDH contactor in only while the remote and the main controller are alive). 2: spare", "Owned"),
    ("Breakout board (your row)", "Other", 1, 0.00, "", "Electrical", "You added this row in the Sheet (2026-11-06): which board and its price are yours to fill in", "Your row"),
    ('Bluetooth music: ESP32-WROOM-32 dev board, USB-C (AITRIP B0DF2YJSHN)', 'Amazon', 1, 8.99, 'https://www.amazon.com/dp/B0DF2YJSHN', 'Electrical', 'A phone pairs to it as a Bluetooth speaker (A2DP). It streams the music by I2S into the main controller, which mixes the horn and effects on top and sends volume and pause back over a UART', f'Only the original ESP32 (and the brand-new S31) do Bluetooth Classic audio; the P4 board\'s C5 is Bluetooth LE only. If it dies, only phone music stops: the horn still works ({V}, S)'),
    ('SN74AHCT125N quad buffer, 10-pack', 'Aliexpress', 1, 2.77, 'https://www.aliexpress.us/item/3256801332816593.html', 'Electrical', 'LED data only now: 3.3 -> 5 V for 8 strip lanes (2 chips). The PWM safety gate is gone (rev D.2): the contactor is the cut-off', '458 sold (2026-11-04, L)'),
    ('12 V 40 A relay with pre-wired socket', 'Aliexpress', 3, 2.02, 'https://www.aliexpress.us/item/3256810529693206.html', 'Electrical', 'Valve arm relay (valve rail, fed from the PDH) and one per fog core (the second for a second core); flyback diode on every coil', '4-pin option; 211 sold. Replaces the Nilight 5-pack ($12.14) and the Gebildet 2-pack ($7.99) (2026-11-04, L)'),
    ('ULN2803A Darlington driver DIP-18, 10-pack', 'Aliexpress', 1, 2.49, 'https://www.aliexpress.us/item/3256810280411957.html', 'Electrical', 'Relay coils from 3.3 V logic: the valve arm relay, the fog core relays and both battery relays (0.15 A coils; COM to +12 V clamps the flyback)', '16 sold. Was $3.84 at DigiKey (2026-11-04, L)'),
    ('Contactor 12 V 200 A continuous duty, isolated coil, 4-pin (B07T48QKQB)', 'Amazon', 1, 12.99, 'https://www.amazon.com/dp/B07T48QKQB', 'Electrical', "The power cut-off: between the main breaker and the PDH. Its coil runs through the rear E-stop, the safety node's switch and the main controller's MOSFET in series, so any one of them kills drive, valves, LEDs, audio and fog", f'200 A continuous, 1.8 W coil, flyback diode across it. One unit instead of a 2-pack ($18.99) ({V}, L)'),
    ('Battery relays: 12 V 200 A continuous duty, same part as the contactor (B07T48QKQB)', 'Amazon', 2, 12.99, 'https://www.amazon.com/dp/B07T48QKQB', 'Electrical', "One in each battery's + lead, between its SB50 and the shared bus. The controller reads both packs and keeps only the fuller one connected until the other is within 0.3 V, so a fresh battery never dumps 20-40 A into a flat one", f'Two relays, not one: with one, a fuller pack on the unswitched side could never be held off. Normally open, 1.8 W (0.15 A) coil on a ULN2803 channel from the PCA9685. Alt: a 2-pack of 120 A split-charge relays (B096QH9DF1) is $17.59, coil not listed ({W}, L)'),
    ('Battery relay bypass: 4.7 ohm 5 W cement resistor, 10-pack (B0FG25KG8C)', 'Amazon', 1, 5.79, 'https://www.amazon.com/dp/B0FG25KG8C', 'Electrical', 'One across each battery relay (2 used): feeds the logic rail and boots the controller while both relays are open (power-up, or a dead controller), and trickle-balances the packs at well under 1 A', f'Under 1 W each in the worst case: a fresh and a flat pack, one relay open, full drive load. 5 stars (7) ({W}, L)'),
    ('Logic supply: 5 V 5 A buck-boost, 3.6-32 V in (diymore)', 'Aliexpress', 1, 8.17, 'https://www.aliexpress.us/item/3256808244937735.html', 'Electrical', 'Always-on 5 V logic rail, tapped ahead of the contactor: main controller (its 5 V header), safety node, music board, every sensor', f'$2.57 + $5.60 shipping. Short-circuit, over-temperature and TVS protection; holds 5 V down to 3.6 V in, so a drive sag can\'t reset the controllers. Was the PM02 at $13.30 ({V}, L)'),
    ("Inline ATO fuse holder + 5 A fuse", "Stash", 1, 0.00, "", "Electrical", "Logic tap, right after the main breaker", STASH),
    ("Resistors and caps (kit): ADC dividers, pull-downs, RC filters", "Stash", 1, 0.00, "", "Electrical",
     "Three transducers (10k/15k), battery A, battery B, bus and PDH volts (39k/10k), 100k pull-downs so a cut sensor wire reads as a fault, the speaker tap", STASH),
    ('Latching mushroom E-stop 22 mm, 2 NC (LA38)', 'Aliexpress', 2, 5.25, 'https://www.aliexpress.us/item/3256806731686244.html', 'Electrical', 'Rear panel: one contact in the contactor coil (kills the PDH), the other in the valve arm relay coil; + the handheld remote', 'Pick the 2 NC option; 180 sold, 4.9 stars. Was $13.99 each (2026-11-04, L)'),
    ('Panel-mount USB-C extension, 10 cm, waterproof', 'Aliexpress', 1, 2.06, 'https://www.aliexpress.us/item/3256809075308882.html', 'Electrical', 'USB to the main controller through the rear panel', '600+ sold. Was $9.69 (2026-11-04, L)'),
    ('Safety remote: ESP32-C3 SuperMini (one of yours)', 'Owned', 1, 0.00, '', 'Electrical', 'Handheld E-stop (the second mushroom above) plus a status LED that shows the link is up; ESP-NOW to the safety node', 'Your spare C3s do ESP-NOW like the S3 Super Mini they replace ($3.79, aliexpress.us/item/3256809624317467). Bluetooth LE only, so they can\'t be the phone-music board (2026-11-09)'),
    ('Safety remote: 18650 battery shield V8 (charging, 5 V out) + a stash 18650 cell', 'Aliexpress', 1, 3.29, 'https://www.aliexpress.us/item/3256807394809647.html', 'Electrical', 'Remote power, charged over USB', '(2026-11-04, L)'),
    ("AUDIO - two siren speakers in the front corners (replaces the horn)", None),
    ('Siren speaker 200 W, 8 ohm, 121-130 dB, aluminium, 5.7 x 5.5 x 2.3 in (Xprite B01DMSR4L4)', 'Amazon', 2, 32.88, 'https://www.amazon.com/dp/B01DMSR4L4', 'Electrical', 'One high in each front-side corner, in a printed cup, aimed 45 deg out and 30 deg up; its L foot bolts through the cup', '4.3 stars (682), 50+ bought last month; 5 lb each. Replaces the SoundAlert ($59.99) (2026-11-04, L)'),
    ('TPA3255 2 x 300 W class-D amp board, 19-50 V DC, 122 x 73 x 30 mm', 'Aliexpress', 1, 27.00, 'https://www.aliexpress.us/item/3256807353596235.html', 'Electrical', 'One channel per speaker; about 100 W each into 8 ohm on 48 V', '$27.00 is your price in the Sheet (2026-11-06; it was $15.27 + $1.99 on 2026-11-04). 727 sold, 4.9 stars. Amazon: B0DSSZZR5Q $25.99'),
    ('1500 W 30 A boost converter, 10-60 V in, 12-97 V out (set to 48 V)', 'Aliexpress', 1, 16.18, 'https://www.aliexpress.us/item/3256806808745565.html', 'Electrical', 'Feeds the amp from a 40 A PDH channel: 20-25 A from the battery at full siren', 'SKU "1500W 30A": $14.19 + $1.99 shipping, logged-in price; 372 g; size not listed, drawn 130 x 76 x 60 [UNVERIFIED]. The $1.09 1200 W SKU is a welcome price. Amazon: Gebildet potted 12->48 V 6 A B0D66NDXLN $15.99 (2026-11-04, L)'),
    ("Speaker tap: 2 x 1k + 2 x 10 nF low-pass + 1 uF cap (from the kit)", "Stash", 1, 0.00, "", "Electrical", "Replaces the PCM5102A: one wire of the board's speaker output (SPK+) through a two-stage 1k/10 nF low-pass and a 1 uF cap into the TPA3255's input (L and R together). Volume and mix are set in software; the amp's gain pot sets the top end", "Not straight in at low volume: the NS4150B is bridge-tied and filterless, so each speaker wire carries a 5 V square wave at a few hundred kHz plus 2.5 V DC at any volume, and grounding SPK- shorts the amp. SPK- stays unconnected. If the amp still whines, the PCM5102A in LATER is the fallback"),
    ("Printed speaker cups (2) and grilles (2)", "Owned", 1, 0.00, "", "Structure",
     "Cup lines each corner notch, 4 x M4 x 8 through its walls into the frame; the speaker's foot bolts through it; grille: 3 walls, no top/bottom layers, 12% gyroid",
     "Filament assumed owned"),

    ("SHIPPING - what the unit prices above don't include", None),
    ('McMaster shipping, one order (estimate)', 'McMaster', 1, 10.0, '', 'Other', 'Relief valves, 1/4 x 1/8 bushings and 1 in nipples in one small box (the barrels moved to Amazon)', 'McMaster bills actual UPS cost; $10 is a guess for a small box [ESTIMATE]'),

    ("LATER - not designed in yet, not in the total", None),
    ("Video (from your list)", "Other", 0, 0.00, "", "Other", "Not designed in yet",
     "Deferred (Micah, 2026-11-03). Rev D.2: the P4 board has a 2-lane MIPI-CSI camera port and a hardware JPEG/H.264 encoder, so a $10-20 camera module can stream from the main board itself"),
    ('PCM5102A I2S DAC module (fallback for the speaker tap)', 'Aliexpress', 0, 2.44, 'https://www.aliexpress.us/item/3256809226289251.html', 'Electrical', 'Only if the speaker tap whines: I2S from a spare port to line level for the amp', '482 sold, 4.9 stars (2026-11-04, L)'),

    ("OTHER MATERIALS - your rows (2026-11-06)", None),
    ("PETG filament (your row)", "Amazon", 1, 40.00, "https://www.amazon.com/dp/B0D86D5SHS", "Structure",
     "Every printed part: the print plan puts the frame at about 3 kg and the other body prints at about 2 kg", "Your row in the Sheet (2026-11-06)"),
    ("Acrylic (your row)", "Other", 1, 150.00, "", "Cosmetic", "Body panels",
     "Your row in the Sheet (2026-11-06); the 'Frosted acrylic (owned)' row under Frame + body stays at $0"),
]
ORDERED = ()   # rows ticked Purchased in the Sheet (keep them ticked when the tabs are rewritten); none as of 2026-11-10


# section title prefix -> order (1: pneumatics, important electronics, speakers; 2: materials, LEDs, smoke)
ORDER_OF = {"FROM THE OLD CANNON": 1, "PRESSURE SIDE": 1, "GUN": 1, "DRIVE": 1, "ELEVATION": 1, "CONTROLS": 1,
            "AUDIO": 1, "SHIPPING": 1, "SMOKE": 2, "FRAME + BODY": 2, "RAILS": 2, "LIGHTS": 2, "BUMPERS": 2,
            "OTHER MATERIALS": 2, "LATER": 2}
ORDER_TITLES = {1: "Borealis Order 1 - pneumatics, electronics, speakers",
                2: "Borealis Order 2 - materials, LEDs, smoke"}


def order_of(section):
    for k, v in ORDER_OF.items():
        if section.startswith(k):
            return v
    raise KeyError(f"section {section!r} has no order")


def orders():
    """{1: [rows], 2: [rows]}: each order's sections in ROWS order."""
    out, cur = {1: [], 2: []}, None
    for r in ROWS:
        if r[1] is None:
            cur = order_of(r[0])
        out[cur].append(r)
    return out


def _sheet(rows):
    """One order tab, laid out like the Broncobots budget's order tabs (2026-11-09):
    B Item | C Price Per Unit | D Quantity | E Total Price | F Provider | G Notes | H Link | I Purchased?, from row 4.
    Row 2 is the band: C2 "Total Cost (W/ Tax)" =SUM(E4:E)*1.091, E2 "Shipping" (the SHIPPING rows' total, so they
    are not table rows), G2 "Total Cost (W/ Taxes + Shipping)" =F2+D2. Each item's listing notes go in its B cell note."""
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
        row = 4 + len(out)
        out.append([name, u, q, f"=C{row}*D{row}", seller, purpose, f'=HYPERLINK("{link}","Link")' if link else "",
                    name.startswith(ORDERED)])
        kinds.append("item")
        cell_notes[f"B{row}"] = notes
    return dict(rows=out, kinds=kinds, notes=cell_notes, shipping=round(shipping, 2), first_cell="B4",
                last=3 + len(out), items=round(sub, 2))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    od = orders()
    tot = 0.0
    with open(os.path.join(here, "glacis_bom.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Order", "Name", "Seller", "Amount", "Individual Price", "Price", "Link", "Type", "Purpose",
                    "Alternative/Notes"])
        for k in (1, 2):
            sub = 0.0
            w.writerow([k, ORDER_TITLES[k]])
            for r in od[k]:
                if r[1] is None:
                    w.writerow([k, r[0]])
                    continue
                name, seller, q, u, link, typ, purpose, notes = r
                sub += q * u
                w.writerow([k, name, seller, q, f"{u:.2f}", f"{q * u:.2f}", link, typ, purpose, notes])
            w.writerow([k, f"Order {k} total", "", "", "", f"{sub:.2f}"])
            w.writerow([])
            tot += sub
        w.writerow(["", "Total", "", "", "", f"{tot:.2f}"])
    sheets = {str(k): dict(title=ORDER_TITLES[k], **_sheet(od[k])) for k in (1, 2)}
    json.dump(dict(orders=sheets), open(os.path.join(here, "glacis_bom_sheet.json"), "w"))
    for k in (1, 2):
        sh = sheets[str(k)]
        print(f"order {k}: {sum(1 for x in sh['kinds'] if x == 'item')} rows, items ${sh['items']:,.2f} + shipping "
              f"${sh['shipping']:,.2f}")
    print(f"{len(ROWS)} rows, total ${tot:,.2f}")


if __name__ == "__main__":
    main()
