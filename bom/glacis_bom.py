"""Glacis rev C parts list (2026-11-02): source of the "Glacis BOM" tab in the parts-list Google Sheet.

    python glacis_bom.py            # writes glacis_bom.csv and glacis_bom_sheet.json (rows for the sheet)

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
STASH = "Standard FRC stash part; buy only if the stash is out"
OLD = "From the old cannon"
ROWS = [
    ("FROM THE OLD CANNON - reused, $0", None),
    ("Atlantic Valves SZW-25 1 in NPT stainless solenoid valve, NC, Viton (old cannon)", "Owned", 1, 0.00,
     "https://www.electricsolenoidvalves.com/1-inch-12-volt-dc-stainless-steel-electric-solenoid-valve/", "Motion",
     "Firing valve, top cannon", f"{OLD}. Read its coil: the 12 V DC coil is rated 0-115 psi (AC coils 0-145)"),
    ("Grey 1 gal steel ASME air tank with a 1 in NPT end port (old cannon)", "Owned", 0, 0.00, "", "Motion",
     "Not used: the chambers are now 0.53 L pipe chambers", f"{OLD}; spare"),
    ("Longacre 5 gal aluminum tank, 125 psi (old cannon)", "Owned", 0, 0.00,
     "https://toolsid.com/longacre/5-gal-horizontal-silver-lightweight-air-tank-mpn-52-50305.html", "Motion",
     "Not used: 125 psi is below the 200 psi tank zone", f"{OLD}; spare"),

    ("PRESSURE SIDE - tanks, rear manifold, main valve and in valves (200 psi)", None),
    ("Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT (your pick)", "Aliexpress", 2, 56.31,
     "https://www.aliexpress.us/item/3256804024554756.html", "Motion", "Left and right, lying over the front wheels",
     f"({D}, L)"),
    ("Relief valve 200 psi, 1/4 MNPT, pull ring (Interstate V200-4)", "Amazon", 2, 16.30, "https://www.amazon.com/dp/B00ABZ0JP0",
     "Motion", "Tank zone (rear manifold; its pull ring at the rear panel is the hand dump) + the valve cross (main to in valves)", f"Listing doesn't say ASME; Milton S-1090-200 ($17.99) is ASME, no ring ({D}, L)"),
    ("Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT (FUSCH)", "Amazon", 3, 17.69, "https://www.amazon.com/dp/B0CRQWKDNC",
     "Electrical", "One part number for all three: tank and both chambers (rev C.3; the 0-200 psi one is gone)",
     f"316 stainless, harness included. 0.08 psi per ADC step is plenty for the chambers ({D}, L)"),
    ("Fill plug: 1/4 MNPT industrial (M-style) plug, brass (Foster 10-3B)", "Other", 1, 4.29,
     "https://www.govets.com/foster-510-g7579629.html", "Motion",
     "Fill port at the rear panel: your universal couplers (EVOULTES kit) snap straight on, same as your tanks",
     "Replaces the Schrader valve (rev C.3). Any M-style plug fits; Milton 727 is the steel one (2026-11-03, S)"),
    ("Fill check valve, brass, 1/4 FNPT x 1/4 MNPT, 250 psi (Control Devices P2525-1WA)", "Other", 1, 7.05,
     "https://www.zoro.com/control-devices-check-valve-14-in-fpt-14-in-mnpt-250-psi-p2525-1wa/i/G2023594/", "Motion",
     "Right behind the plug: a plug is an open pipe, so this is what holds the tanks shut when the hose comes off",
     "Zoro; price from a search snippet [UNVERIFIED] (2026-11-03, S)"),
    ("In valves: Aignep 02F 2/2 NC direct-acting 12 V DC, 1/4 NPTF, 2 mm (02F03102N0N10201)", "Hose Warehouse", 2, 41.36,
     "https://hosewarehouse.com/products/02f03102n0n10201-aignep-fluidity-series-fluidity-02f-directacting-solenoid-valve-2-2-nc-nbr-seal-1-4-nptf-2-mm-12v-dc",
     "Electrical", "One in valve per chamber, metering it against its transducer; they now hold tank pressure all session",
     "Rated 0-35 bar (507 psi) on the 8 W DC coil, brass body. Confirm the DIN plug is included (2026-11-03, L)"),
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
     "Motion", "Fill port through the rear panel", "If not: Legines 5-pack $10.99, or one loose at a hardware store"),
    ("1/4 NPT brass hex plug, 5-pack (Legines)", "Amazon", 1, 7.99, "https://www.amazon.com/dp/B0757HRRX9",
     "Motion", "5 used: spare tank ports (4), top of the rear manifold", f"1200 psi ({D}, L)"),
    ("1/4 x 1/8 NPT brass hex bushing, 2-pack (Legines)", "Amazon", 2, 6.49, "https://www.amazon.com/dp/B0747CJ2LV",
     "Motion", "3 transducers", f"1200 psi. FUSCH's 200 psi transducer only comes in 1/8 NPT, so these stay (2026-11-03, S)"),
    ("DOT nylon air-brake tube 1/4 in OD, SAE J844 Type 3B, 25 ft (HD Value HDV-NT2604BLK25)", "Other", 1, 14.49,
     "https://www.finditparts.com/products/8186847/hd-value-hdv-nt2604blk25", "Motion",
     "Every air line, including the two service loops to the gun (about 15 ft used)", f"FMVSS 106; limited stock at this price (2026-11-03, S)"),
    ("DOT push-to-connect 1/4 tube x 1/4 NPT, straight, 10-pack (Boeray)", "Amazon", 1, 19.99, "https://www.amazon.com/dp/B0D8PX7Z94",
     "Motion", "8 used: rear manifold (3), main valve, both in valves, chamber fill ports (2)", "In stock (2026-11-01, L)"),
    ("DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT, 5-pack (Boeray)", "Amazon", 1, 17.99, "https://www.amazon.com/dp/B0D8Q2618F",
     "Motion", "2 used: tank outlets", "SAE J1131, 250 psi, NPT (2026-11-02, L)"),
    ("Pipe thread sealant, RectorSeal T Plus 2", "Other", 1, 4.25, "https://www.homedepot.com/p/100116773",
     "Tool", "Every NPT joint", "Home Depot (2026-11-01, L)"),
    ("1 in cam-buckle strap 4 ft, 4-pack", "Amazon", 1, 8.99, "https://www.amazon.com/dp/B0GVS7RGTB",
     "Structure", "4 used: side tanks (the chambers now have printed caps)", "1,100 lb (2026-11-02, L)"),

    ("GUN - two in-line cannons 8 mm apart, 0.53 L pipe chambers, 110 psi cap", None),
    ("Firing valve: U.S. Solid USS2-01023, 1 in NPT, 12 V DC, NC", "Amazon", 1, 59.80, "https://www.amazon.com/dp/B0CXWR76GT",
     "Electrical", "Firing valve, bottom cannon (the old SZW-25 is the top)",
     f"Rated 0.8 MPa (116 psi) on the listing, which you checked: above the 110 psi cap. The SZW-25 twin was $127.56 (2026-11-03, L)"),
    ("Chamber: 2 x 1 black malleable reducing coupling, 150 lb, UL/FM (Supply Giant CNSD4005)", "Amazon", 4, 12.99,
     "https://www.amazon.com/dp/B016F1LLOG", "Motion", "Both ends of each chamber (1 in to the valve, 1 in to its cross)",
     f"Factory pressure tested; 18 left ({D}, L)"),
    ("Chamber: 2 in Sch 40 black steel nipple x 8 in (Supply Giant OQCM2080)", "Amazon", 2, 14.99,
     "https://www.amazon.com/dp/B016Y8BZ32", "Motion", "Chamber body: 0.53 L each with the couplings",
     f"4.4 stars ({D}, S)"),
    ("1 x 1/4 NPT black malleable hex bushing (Supply Giant CNCV3003)", "Amazon", 2, 8.99, "https://www.amazon.com/dp/B016Y8R05Y",
     "Motion", "Back of each chamber to its brass cross", f"({D}, S)"),
    ("1 in NPT black Sch 40 close nipple", "Amazon", 4, 4.05, "https://www.amazon.com/dp/B007IBN8T4", "Motion",
     "Chamber to valve, valve to breech adapter (2 per cannon)", f"Check the seller's stock ({D}, S)"),
    ("1 in - 11-1/2 NPT pipe tap", "Amazon", 1, 16.99, "https://www.amazon.com/dp/B0BB3H8ZHP", "Tool",
     "Cuts the 1 in NPT threads inside the two aluminum breech adapters (stash 6061 bar)",
     f"Borrow one if the shop has it. 4.6 stars ({D}, S)"),
    ("Relief valve 125 psi, 1/4 MNPT, ASME, pull ring (Milton 1090-125)", "Milton", 2, 16.87,
     "https://miltonindustries.com/products/1-4-mnpt-asme-safety-valve-125-psi-pop-off-pressure", "Motion",
     "Each chamber; the ring is its manual bleed",
     f"National Board certified, 120 SCFM. Sits above the 110 psi software cap so it never simmers ({D}, L)"),
    ("MOSFET switch module 5-36 V 15 A, 6-pack", "Amazon", 2, 5.49, "https://www.amazon.com/dp/B0D9VWWLCB", "Electrical",
     "9 used: firing valves (2), in valves (2), fog heater (2), fog pump, blower, PDH contactor coil; 2 kept for a second core",
     f"Gates driven at 5 V through the spare 74AHCT125 buffers; flyback diode across each valve coil ({D}, S)"),
    ("Barrels: clear polycarbonate tube 3 in OD x 2-3/4 ID x 1/8 wall, 4 ft (McMaster 8585K38)", "McMaster", 1, 84.48,
     "https://www.mcmaster.com/8585K38/", "Structure", "Two 22.5 in barrels from one 4 ft stick; six smoke holes each, just past the shirt",
     f"No pressure rating published; clamp it. Only the six 5 mm smoke holes are drilled (slowly, deburred) ({D}, L)"),

    ("SMOKE - custom 12 V fogger (one 200 W core, room for a second), barrel collar, front and rear trail vents", None),
    ("Fog heater core 12 V 200 W, cast heat exchanger 97 x 32 x 36 mm", "Aliexpress", 1, 22.42,
     "https://www.aliexpress.us/item/3256805556610953.html", "Cosmetic", "The fogger: about 17.5 A on its own 30 A PDH channel",
     f"One core for now; the tray, bracket and a PDH channel are left for a second (twice the fog). "
     f"5-8 min warm-up; free shipping, 22 sold ({D}, S)"),
    ("Fog fluid pump: Kamoer NKP 12 V peristaltic, 70 mL/min", "Amazon", 1, 9.98, "https://www.amazon.com/dp/B07GWJ78FN",
     "Cosmetic", "Feeds the core from the printed tank (a second one comes with a second core)", f"Fine running dry; back-pressure [UNVERIFIED] ({D}, S)"),
    ("Thermocouple amp MAX6675 + K-type M6 probe (HiLetgo)", "Amazon", 1, 7.69, "https://www.amazon.com/dp/B01HT871SO",
     "Electrical", "Core temperature to the STM32 (SPI); hold 220-240 C, firmware cut at 245 C", f"({D}, S)"),
    ("Fluid level: XKC-Y25-NPN non-contact capacitive level switch, 5-12 V", "Other", 1, 21.95,
     "https://www.fruugo.ca/non-contact-liquid-level-sensor-5-12v-output-npn-interface-xkc-y25-npn-capacitive-water-level-sensing-detector-for-containers-liquids-5xvr4/p-405348419",
     "Electrical", "Stuck to the outside of the printed tank at about 20%: low-fluid warning, and the pump stops about a minute later",
     "Reads through up to 20 mm of plastic, so the tank has no hole. Fruugo price; AliExpress is usually far less [UNVERIFIED] (2026-11-03, S)"),
    ("DS18B20 waterproof temperature probe, 1 m, 5-pack (Aideepen)", "Amazon", 1, 9.49, "https://www.amazon.com/dp/B01LY53CED",
     "Electrical", "1-Wire on one STM32 pin: fogger box by the printed tray (heater off at 70 C), electronics shelf, battery bay; 2 spare",
     "Snippet price, date not shown (2026-11-03, S)"),
    ("Thermal cutout KSD301 250 C normally closed 25 A, 2-pack (uxcell)", "Amazon", 1, 9.99, "https://www.amazon.com/dp/B0FB98L1VZ",
     "Electrical", "Hardware backstop on each core, in its relay coil line", f"Only 2 left; self-resetting, so firmware latches the fault ({D}, S)"),
    ("12 V 40 A relay + harness with diode, 2-pack (Gebildet)", "Amazon", 1, 7.99, "https://www.amazon.com/dp/B078T8CMF6",
     "Electrical", "One per core, upstream of its MOSFETs; coil through the KSD301 and an STM32 enable (pulled low)",
     f"A shorted MOSFET or an STM32 reset can't keep a core hot ({D}, S)"),
    ("12 V 5015 blower, 2-pack (WINSINN)", "Amazon", 1, 8.99, "https://www.amazon.com/dp/B079BMX2S6", "Cosmetic",
     "Pushes the fog from the cores into the splitter and down the four tubes", f"({D}, S)"),
    ("Silicone tube 3 mm ID (Quickun)", "Amazon", 1, 5.99, "https://www.amazon.com/dp/B08BRC5FPB", "Cosmetic",
     "Tank -> pumps -> core inlets (zip-tied on the 2.5 mm tubes)", f"({D}, S)"),
    ("Fog fluid, water-based, 1 qt (FogWorx)", "Amazon", 1, 17.99, "https://www.amazon.com/dp/B0777S56RB", "Cosmetic",
     "Fills the printed tank about twice", f"Never oil: it cokes the 2.5 mm core tube ({D}, S)"),
    ("Flexible fog tube (yours, 4)", "Owned", 4, 0.00, "", "Cosmetic", "Splitter to the barrel collar (2), front vent, rear nozzle", "Owned"),
    ("Printed smoke parts: tray, 400 mL tank, 1-to-4 splitter, two-piece smoke collar, front vent, rear nozzle (PETG/ASA)", "Owned", 1,
     0.00, "", "Cosmetic", "Ducts, vents and the barrel collar", "Filament assumed owned; the cores sit on an aluminum bracket, never on a print"),

    ("DRIVE - Falcons, one-stage belts, 10 in vector-style printed mecanum", None),
    ("Falcon 500 (owned)", "Stash", 4, 0.00, "", "Motion", "One per wheel, PWM through the safety gate", "Owned"),
    ("12T HTD 15 mm Falcon pulley (WCP-0319)", "Stash", 4, 0.00, "https://wcproducts.com/products/wcp-0319",
     "Motion", "Falcon 12T -> 116T printed into the hub (9.67:1)", STASH + " ($7.99 at WCP)"),
    ("HTD 5M 15 mm belt, 140T", "WCP", 4, 15.99, "https://wcproducts.com/products/htd-timing-belts-15mm-width", "Motion",
     "Falcon to wheel, fixed centres", f"In stock ({D}, L)"),
    ("Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)", "Stash", 12, 0.00, "https://wcproducts.com/products/wcp-0783",
     "Motion", "2 per wheel axle (inner + outer rail), 4 at the pivot", STASH + " ($2.99 each)"),
    ("1/2 in hex shaft: 4 wheel axles (6 in) + 2 pivot stubs", "Stash", 1, 0.00, "", "Motion",
     "Live axles tapped 10-32 both ends; one steel stub per cradle plate on the pivot axis", STASH),
    ("608 2RS bearing 8 x 22 x 7 mm, 100-pack (XiKe)", "Amazon", 1, 24.99, "https://www.amazon.com/dp/B081Y32MYV",
     "Motion", "2 per roller x 40 rollers = 80", "Snippet said 'only 1 left'; backup eBay 100-pack $26.92 (2026-11-02, S)"),
    ("M8 x 1.25 threaded rod, zinc, grade 2, 1 m (Zoro Select)", "Other", 5, 9.19,
     "https://www.zoro.com/zoro-select-fully-threaded-rod-m8-125mm-1-m-steel-grade-2-zinc-plated-finish-2373/i/G3652801/",
     "Motion", "40 fixed roller rods cut to 109 mm (9 per rod); slot the outboard ends", f"Bolt Depot was $11.25 (2026-11-03, S)"),
    ("M8 nylon lock nut, zinc, 100-bag (Bolt Depot #4806)", "Other", 1, 7.12, "https://boltdepot.com/Product-Details?product=4806",
     "Motion", "One captured in each outboard cup, 40 used", f"13 mm AF; [UNVERIFIED stock] ({D}, S)"),
    ("1/4-20 x 5-1/2 in hex bolt, zinc (Bolt Depot #9)", "Other", 32, 0.36, "https://boltdepot.com/Product-Details?product=9",
     "Motion", "8 hub through-bolts per wheel (clamp the 3 plates and 2 hub halves)",
     f"M6 x 130 SHCS also fits (#15447, $1.62); [UNVERIFIED stock] ({D}, S)"),
    ("1/4-20 nylon lock nut, zinc (Bolt Depot #2624)", "Other", 32, 0.12, "https://boltdepot.com/Product-Details?product=2624",
     "Motion", "Hub through-bolts", f"[UNVERIFIED stock] ({D}, S)"),
    ("Loctite 243 blue threadlocker (owned)", "Owned", 1, 0.00, "", "Tool", "Roller rods in their captured nylocs", "Owned"),
    ("Printed drive parts: 8 hub halves (the inboard ones carry the 116T), 40 roller cores (PETG-CF), 40 treads (TPU 95A)",
     "Owned", 1, 0.00, "", "Motion", "Each hub half is 242 mm across and prints face down; 12 flat 1/8 in aluminum plates (owned)",
     "Filament and aluminum assumed owned"),

    ("ELEVATION - 60 rpm FTC motor on a Spark MAX, pot for the angle", None),
    ("goBILDA 5203-2402-0100 Yellow Jacket 99.5:1 (60 rpm), 8 mm REX (yours)", "Owned", 1, 0.00,
     "https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-99-5-1-ratio-24mm-length-8mm-rex-shaft-60-rpm-3-3-5v-encoder/",
     "Motion", "16T -> 56T belt to the right pivot stub (3.5:1, about 17 rpm at the gun)", "You have one. 13.1 N*m stall"),
    ("REV Spark MAX (owned)", "Stash", 1, 0.00, "", "Electrical", "Drives the goBILDA in brushed mode from PWM", "Owned"),
    ("HTD 5M 9 mm belt, 100T", "WCP", 1, 7.99, "https://wcproducts.com/products/htd-timing-belts-9mm-width", "Motion",
     "Pinion to the pivot pulley (CAD loop is exactly 500 mm)", f"({D}, L)"),
    ("10k pot, 1/4 in shaft (Bourns 81A1A-B28-A15)", "Amazon", 1, 10.70, "https://www.amazon.com/dp/B0CCBWM242",
     "Electrical", "Gun angle on the end of the left pivot stub, to the STM32 ADC", f"Confirm >= 270 deg travel ({D}, L)"),

    ("FRAME + BODY - box tube, printed frame, recessed acrylic, LED loops and glowing frame", None),
    ("3/16 in aluminum blind rivet, 0.126-0.25 grip, 100-pack (McMaster 97447A050)", "McMaster", 2, 10.23,
     "https://www.mcmaster.com/97447A050/", "Structure", "Gussets, drive plates, posts (1/8 gusset + 1/16 wall)", f"#11 drill ({D}, L)"),
    ("Heat-set inserts M2-M6, 400 pcs (Ktehloy)", "Amazon", 1, 15.97, "https://www.amazon.com/dp/B0CLKDPN65",
     "Structure", "M3 for the panel clips, M4 for frame joints, standoffs and door latches, M5 for the chamber caps",
     f"In stock; the 8 x M5 x 16 screws for the caps come from the stash ({D}, L)"),
    ("M3 x 8 button head, 304 stainless, 100 pcs", "Amazon", 1, 5.88, "https://www.amazon.com/dp/B0DKXNXLGX",
     "Structure", "Panel corner clips (one each)", f"In stock ({D}, L)"),
    ("M4 x 12 button head, 304 stainless, 100 pcs", "Amazon", 2, 7.40, "https://www.amazon.com/dp/B0DKXQQPWS",
     "Structure", "Frame-joint cross screws, standoffs, speaker cups (8)", f"Only 2 left; backup 12.9 black-oxide B0CTH3FQLD $8.86 ({D}, L)"),
    ("Frosted acrylic 1/8 in (owned): 9 panels", "Owned", 9, 0.00, "", "Cosmetic",
     "Recessed in the printed frame, held by corner clips", "Owned; outlines in the Onshape panels tab"),
    ("Printed body frame: 89 pieces, 101 tapered tenons, 40 corner clips, 2 door latches (natural PETG, 15% gyroid)", "Owned", 1, 0.00, "", "Structure",
     "Holds the panels; a strip tunnel down every member (the frame glows) and a leaning LED rail round each window",
     "Filament assumed owned. 4 walls, 15% gyroid: lighter, and the glow is more even"),
    ("WS2812B LED strip 5 mm wide, 2020 LEDs, 100 LED/m, 5 m", "Aliexpress", 2, 15.79,
     "https://www.aliexpress.us/item/3256806565594495.html", "Electrical",
     "9.5 m pushed through the frame tunnels, LEDs out, so the printed frame glows",
     "4.9 stars, 947 sold, 1,648 available, +$1.15 shipping; on sale. PCB colour not stated (2026-11-03, L)"),
    ("WS2812B LED strip 10 mm, 60 LED/m, 5 m (BTF-LIGHTING)", "Amazon", 3, 13.99, "https://www.amazon.com/dp/B088FJF9XD",
     "Electrical", "12.1 m: one closed loop per panel on the leaning rail 1.15 in behind it, LEDs aimed across the panel",
     "IP30 is fine inside the body (2026-11-02, L)"),

    ("BUMPERS - FRC style", None),
    ("White pool noodle 2.5 in (dollar store)", "Other", 8, 1.25, "", "Structure", "Two stacked per side",
     f"Dollar Tree price, not checked live; any 2.5 in noodle 48 in or longer (2026-11-03)"),
    ("Heavy-duty 12 oz cotton duck canvas, white, 60 in wide (per yard)", "Other", 2, 10.00,
     "https://www.canvasetc.com/product/cotton-duck-cloth-white/", "Cosmetic", "Bumper covers wrapped round the noodles and printed backing",
     f"12 oz is heavy duty. Natural 12 oz is $7.68/yd at Big Duck Canvas; white is a little more (2026-11-03, S)"),

    ("CONTROLS, FAILSAFE + POWER - back bottom bay", None),
    ("FRC 12 V battery + charger (owned)", "Stash", 2, 0.00, "", "Electrical", "One per side on its own slide-out sled", "Owned"),
    ("REV PDH + ATO breakers, 120 A main breaker, SB50s, wire and lugs", "Stash", 1, 0.00, "", "Electrical", "Main power",
     "Owned / " + STASH),
    ("Anderson SB50 panel mount with dust cover", "Amazon", 1, 9.99, "https://www.amazon.com/dp/B0D4K5SZR5", "Electrical",
     "Standby charge / shore-power port, bottom of the rear panel", f"4.5 stars ({D}, S)"),
    ("STM32F411 \"Black Pill\" (WeAct V3.1, STM32F411CEU6)", "Other", 1, 7.00,
     "https://www.universal-solder.ca/product/stm32-black-pill-weact-v3-1-stm32f411ceu6-100mhz-512kb-flash/", "Electrical",
     "Main controller on the always-on logic rail: drive, valves, chamber metering, elevation loop, smoke, every sensor, "
     "battery and PDH volts, and the PDH contactor",
     f"C$9.59; the Nucleo-F446RE was $38.80. Same STM32F4 family, USB-C (2026-11-03, S)"),
    ("ESP32-S3 boards (your two)", "Owned", 2, 0.00, "", "Electrical",
     "1: WiFi bridge for the web UI (UART to the STM32). 2: safety node (ESP-NOW to the remote). Both on the logic rail", "Owned"),
    ("SN74AHCT125N quad buffer, 12-pack", "Amazon", 1, 7.49, "https://www.amazon.com/dp/B0DZGY5MHT", "Electrical",
     "PWM gate to the Falcons and Spark MAX, enabled only by the safety node; also 3.3 -> 5 V for the LEDs",
     f"Unbranded reseller ({D}, L)"),
    ("12 V 40 A SPDT relay + socket, 5-pack (Nilight 50003R)", "Amazon", 1, 12.14, "https://www.amazon.com/dp/B0748F1JK4",
     "Electrical", "Safety relay (valve rail), 4 spare (the main valve is manual now)", f"Flyback diode on every coil; sold by Amazon ({D}, L)"),
    ("ULN2803A Darlington driver", "DigiKey", 1, 3.84, "https://www.digikey.com/en/products/detail/stmicroelectronics/ULN2803A/599591",
     "Electrical", "Relay coils from 3.3 V GPIO", "76,298 in stock (2026-11-01, L)"),
    ("12/24 V -> 5 V 20 A buck, potted", "Amazon", 1, 15.99, "https://www.amazon.com/dp/B089M5R3NJ",
     "Electrical", "LEDs only, on a PDH channel, so they go dark with the PDH",
     "About 1,680 LEDs: cap them at about 20% white in firmware; inject 5 V at every frame node (2026-11-02, L)"),
    ("Contactor 12 V 200 A continuous duty, isolated coil, 4 terminal, 2-pack (Hamolar RD-200)", "Amazon", 1, 26.24,
     "https://www.amazon.com/dp/B096QGR24M", "Electrical",
     "Between the main breaker and the PDH (rev C.3): the STM32 switches the whole PDH through a MOSFET channel; the rear E-stop's second contact is in its coil",
     "Coil about 0.7 A, flyback diode across it; one spare. Price from an eBay listing, Amazon [UNVERIFIED]; Cole Hersee 24213 is $74.65 (2026-11-03, S)"),
    ("Logic supply: Pololu S13V30F5 5 V 3 A buck-boost (#4082)", "Pololu", 1, 17.95, "https://www.pololu.com/product/4082",
     "Electrical", "Always-on 5 V logic rail, tapped ahead of the contactor: STM32, both ESP32s, every sensor (and the camera if you add one)",
     "2.8-22 V in, so a drive sag can't reset the controllers; about 3 W standby (2026-11-03, S)"),
    ("Inline ATO fuse holder + 5 A fuse", "Stash", 1, 0.00, "", "Electrical", "Logic tap, right after the main breaker", STASH),
    ("Resistors and caps (kit): ADC dividers, pull-downs, RC filters", "Stash", 1, 0.00, "", "Electrical",
     "Three transducers (10k/15k), battery and PDH volts (39k/10k), 100k pull-downs so a cut sensor wire reads as a fault", STASH),
    ("Latching mushroom E-stop 22 mm, 2NC (TWTADE YW1B-V4E02R)", "Amazon", 2, 13.99, "https://www.amazon.com/dp/B07NP44T74",
     "Electrical", "Rear panel: one contact in the safety relay coil, the other in the contactor coil (kills the PDH); + the handheld remote", f"In stock ({D}, L)"),
    ("Panel-mount USB-C extension (AAOTOKK)", "Amazon", 1, 9.69, "https://www.amazon.com/dp/B08HS6X44P", "Electrical",
     "USB to the STM32 through the rear panel", f"In stock ({D}, L)"),
    ("Safety remote: ESP32-S3 Super Mini", "Aliexpress", 1, 5.00, "", "Electrical",
     "Handheld E-stop (the second mushroom above) plus a status LED that shows the link is up; ESP-NOW to the safety node",
     f"About $4-10 depending on seller (2026-11-03, S)"),
    ("Safety remote: 18650 battery shield (charging, 5 V out) + a stash 18650 cell", "Aliexpress", 1, 4.00, "", "Electrical",
     "Remote power, charged over USB", f"About $2-5 (2026-11-03, S)"),

    ("AUDIO - two siren speakers in the front corners (replaces the horn)", None),
    ("Slim 100 W siren speaker, 11 ohm, 120-130 dB, 5.5 x 5.75 x 2 in (UBL 100W Slim)", "Other", 2, 79.99,
     "https://ultrabrightlightz.com/products/ubl-100w-slim-speaker", "Electrical",
     "One high in each front-side corner, in a printed cup, aimed 45 deg out and 30 deg up",
     "400-4,000 Hz: horn tones and voice, not music bass. Sale price (2026-11-03, S)"),
    ("TPA3116D2 2 x 50 W class-D amp board with volume", "Parts Express", 1, 13.98,
     "https://parts-express.com/TPA3116D2-2x50W-Class-D-Stereo-Amplifier-Board-with-Volume-Control-320-699", "Electrical",
     "One channel per speaker; about 26 W each into 11 ohm on 24 V", f"Parts Express 320-699 (2026-11-03, S)"),
    ("12 -> 24 V 5 A 120 W boost module (EKYLIN or HQRP)", "Amazon", 1, 18.49, "", "Electrical",
     "Feeds the amp from a PDH channel; the amp draws about 2.5 A at 24 V",
     f"HQRP is $14.95 on eBay. Without it the amp gives about 6 W, 6 dB quieter (2026-11-03, S)"),
    ("PCM5102A I2S DAC module, 3-pack", "Other", 1, 6.83, "https://www.walmart.com/ip/17539373801", "Electrical",
     "I2S from the ESP32-S3 WiFi bridge to line level for the amp: horn sounds and clips from the web UI", f"(2026-11-03, S)"),
    ("Printed speaker cups (2) and grilles (2)", "Owned", 1, 0.00, "", "Structure",
     "Cup lines each corner notch (4 x M4 into the speaker bracket holes); grille: 3 walls, no top/bottom layers, 12% gyroid",
     "Filament assumed owned"),

    ("LATER - not designed in yet, not in the total", None),
    ("Video (from your list)", "Other", 0, 0.00, "", "Other", "Not designed in yet",
     "Proposed: Pi Zero 2 W + Camera Module 3 Wide on the logic rail, about $50 (electrical/README.md)"),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "glacis_bom.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Name", "Seller", "Amount", "Individual Price", "Price", "Link", "Type", "Purpose", "Alternative/Notes"])
        tot = 0.0
        for r in ROWS:
            if r[1] is None:
                w.writerow([r[0]])
                continue
            name, seller, q, u, link, typ, purpose, notes = r
            tot += q * u
            w.writerow([name, seller, q, f"{u:.2f}", f"{q * u:.2f}", link, typ, purpose, notes])
        w.writerow([])
        w.writerow(["Total", "", "", "", f"{tot:.2f}"])
    # sheet rows from row 4: section rows and item rows with formulas
    out, kinds = [], []
    for i, r in enumerate(ROWS):
        row = 4 + i
        if r[1] is None:
            out.append([r[0], "", "", "", "", "", "", "", "", ""])
            kinds.append("section")
            continue
        name, seller, q, u, link, typ, purpose, notes = r
        out.append([name, False, seller, q, u, f"=D{row}*E{row}", f'=HYPERLINK("{link}","Link")' if link else "",
                    typ, purpose, notes])
        kinds.append("item")
    json.dump(dict(rows=out, kinds=kinds, last=3 + len(ROWS)), open(os.path.join(here, "glacis_bom_sheet.json"), "w"))
    print(f"{len(ROWS)} rows, total ${tot:,.2f}")


if __name__ == "__main__":
    main()
