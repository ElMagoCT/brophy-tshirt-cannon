"""Glacis rev B parts list (2026-11-02): source of the "Glacis BOM" tab in the parts-list Google Sheet.

    python glacis_bom.py            # writes glacis_bom.csv and glacis_bom_sheet.json (rows for the sheet)

Row = (name, seller, qty, unit $, link, type, purpose, notes). A row with qty None is a section header.
Quantities come from cad/glacis/out/parts_from_cad.csv. Sellers: McMaster, Amazon and AliExpress first.
Prices were read on 2026-11-01/02 (L = live page, S = search snippet). Aluminum (box tube, sheet, bar),
acrylic, prints, Falcons and standard FRC stash parts are $0 or left off. Anything the old T-shirt
cannon has comes off this list once its parts list is in.
"""
import csv
import json
import os

D = "2026-11-02"
STASH = "Standard FRC stash part; buy only if the stash is out"
ROWS = [
    ("PRESSURE SIDE - tanks, rear manifold, fill valve (200 psi)", None),
    ("Air tank 6 L / 1.6 gal, 200 psi, 1/4 NPT (your pick)", "Aliexpress", 2, 56.31,
     "https://www.aliexpress.us/item/3256804024554756.html", "Motion", "Left tank lying over the front-left wheel; rear tank standing",
     f"Check the old cannon first ({D}, L)"),
    ("Relief valve 200 psi, 1/4 MNPT, pull ring (Interstate V200-4)", "Amazon", 1, 16.30, "https://www.amazon.com/dp/B00ABZ0JP0",
     "Motion", "Hardware relief on the tank zone (rear manifold)", f"Listing doesn't say ASME; Milton S-1090-200 ($17.99) is ASME, no ring ({D}, L)"),
    ("Pressure transducer 0-300 psi, 0.5-4.5 V, 1/8 NPT (FUSCH)", "Amazon", 1, 17.69, "https://www.amazon.com/dp/B0CRQWKDNC",
     "Electrical", "Tank pressure to the STM32", f"316 stainless, harness included ({D}, L)"),
    ("Tank fill valve (Schrader) 1/4 MNPT, Milton S-684-4, 2-pack", "Amazon", 1, 9.15, "https://www.amazon.com/dp/B001PLI4BA",
     "Motion", "Precharge from a shop compressor through the rear panel", f"200 psi max, sold by Amazon ({D}, L)"),
    ("Mini ball valve 1/4 FNPT (Nigo 240)", "Amazon", 1, 12.29, "https://www.amazon.com/dp/B08LV6KBN1",
     "Motion", "Manual tank bleed, lever through the rear panel", f"600 WOG ({D}, L)"),
    ("Fill / metering valve, Aignep 02F 2/2 NC direct-acting 12 V DC, 1/4 NPTF", "Hose Warehouse", 1, 41.36,
     "https://www.hosewarehouse.com/search?q=02F03102N0N10201", "Electrical", "Meters tank air into the fill cross (580 psi body)",
     f"No 12 V, 200 psi, zero-differential valve at McMaster or Amazon; Vixen VXA7164 ($19.08) is a horn valve with a 1/8 outlet. "
     f"Confirm the coil + DIN plug are included ({D}, L); link is a store search"),
    ("1/4 NPT brass cross (4-way), 3-pack (ChillWaves)", "Amazon", 2, 12.99, "https://www.amazon.com/dp/B0FCMV6ML9",
     "Motion", "4 used: rear manifold (3) and the fill cross", "NPT, 1200 psi (2026-11-02, L)"),
    ("1/4 NPT brass close nipple 7/8 in, 5-pack (Legines)", "Amazon", 2, 7.99, "https://www.amazon.com/dp/B07L5G7CN3",
     "Motion", "About 9 used: inlet blocks, dump valves, rear manifold, fill valve", "NPT, 1200 psi (2026-11-02, L)"),
    ("1/4 NPT brass nipple 1-1/2 in, 5-pack (Legines)", "Amazon", 1, 10.99, "https://www.amazon.com/dp/B07L5HNKQC",
     "Motion", "Fill port and bleed through the rear panel", "NPT, 1200 psi (2026-11-02, L)"),
    ("1/4 NPT brass hex plug, 5-pack (Legines)", "Amazon", 1, 7.99, "https://www.amazon.com/dp/B0757HRRX9",
     "Motion", "5 used: spare tank ports (left front one = future pump inlet), fill cross end", f"1200 psi ({D}, L)"),
    ("1/4 x 1/8 NPT brass hex bushing, 2-pack (Legines)", "Amazon", 2, 6.49, "https://www.amazon.com/dp/B0747CJ2LV",
     "Motion", "4 transducers", f"1200 psi ({D}, L)"),
    ("DOT nylon air-brake tube 1/4 in OD, SAE J844, 50 ft", "eBay", 1, 21.49, "https://www.ebay.com/itm/153495754001",
     "Motion", "Every air line (plastic wherever the pressure allows)", ">10 available (2026-11-01, L)"),
    ("DOT push-to-connect 1/4 tube x 1/4 NPT, straight, 10-pack (Boeray)", "Amazon", 2, 19.99, "https://www.amazon.com/dp/B0D8PX7Z94",
     "Motion", "12 used: manifold, fill valve and cross, inline check valves, gun supply", "In stock (2026-11-01, L)"),
    ("DOT push-to-connect swivel elbow 1/4 tube x 1/4 NPT, 5-pack (Boeray)", "Amazon", 1, 17.99, "https://www.amazon.com/dp/B0D8Q2618F",
     "Motion", "2 tank outlets", "SAE J1131, 250 psi, NPT (2026-11-02, L)"),
    ("Pipe thread sealant, RectorSeal T Plus 2", "Other", 1, 4.25, "https://www.homedepot.com/p/100116773",
     "Tool", "Every NPT joint", "Home Depot (2026-11-01, L)"),
    ("1 in cam-buckle strap 4 ft, 4-pack", "Amazon", 1, 8.99, "https://www.amazon.com/dp/B0GVS7RGTB",
     "Structure", "3 used: left tank (2), rear tank clamp (1)", "1,100 lb (2026-11-02, L)"),

    ("GUN - two polycarbonate barrels, 0.4 L chambers at 150 psi", None),
    ("Quick exhaust valve, Humphrey QE5, 3/4 NPTF", "TECO", 2, 51.75,
     "https://tecotechnology.com/products/humphrey-quick-exhaust-3-4-nptf-qe5", "Motion", "Firing valve, one per barrel",
     f"Rated 1-150 psi. Not on Amazon or McMaster; Amazon's Parker 0R75B is $124.95, McMaster's 3/4 unit is 125 psi ({D}, L)"),
    ("Dump valve, HornBlasters brass 1/4 NPT 12 V air valve (VA-4)", "Amazon", 2, 34.99, "https://www.amazon.com/dp/B006GG2T92",
     "Electrical", "Vents each QEV inlet to fire", f"150-210 psi working, 2.5 mm orifice, sold by HornBlasters ({D}, L)"),
    ("5-port brass block, 1/4 FNPT (Interstate Pneumatics CPT44-5)", "Amazon", 2, 17.97, "https://www.amazon.com/dp/B01N9JJYG0",
     "Motion", "Each barrel's inlet pocket: QEV, dump, supply, relief, transducer", f"Rated 1000 psi. Listing says 5 pieces: may be a 5-pack, so check ({D}, L)"),
    ("Relief valve 150 psi, 1/4 MNPT, ASME, pull ring (Interstate V150-4)", "Amazon", 3, 15.50, "https://www.amazon.com/dp/B0DJWG5SJ3",
     "Motion", "Each chamber + the fill cross; the ring is the manual bleed", f"In stock ({D}, L)"),
    ("Check valve 1/4 FNPT brass, 250 psi (Conrader)", "Amazon", 2, 24.90, "https://www.amazon.com/dp/B0DXLD81BC",
     "Motion", "One per barrel, inline after the fill cross, so one shot can't vent the other chamber",
     f"Horizontal mounting only (both are horizontal); Milton S-1093-4 $34.07 mounts any way ({D}, L)"),
    ("Pressure transducer 0-200 psi, 0.5-4.5 V, 1/8 NPT (FUSCH)", "Amazon", 3, 17.69, "https://www.amazon.com/dp/B0CRQVDJJ7",
     "Electrical", "Both chambers + the fill line to the STM32", f"316 stainless, harness included ({D}, L)"),
    ("Chamber: 4 x 3/4 black malleable hex bushing, 150 lb (Supply Giant CNCV6000)", "Amazon", 2, 17.91,
     "https://www.amazon.com/dp/B016Y8RAPO", "Motion", "Chamber body + QEV connection", f"Sold by Amazon ({D}, L)"),
    ("Chamber: 4 in galvanized malleable cap, Class 150, UL/FM (Nasco)", "Amazon", 2, 38.08, "https://www.amazon.com/dp/B0GWFR88T2",
     "Motion", "Chamber end (0.4 L with the bushing); the top one carries the left trunnion hub",
     f"12 left. McMaster black 44605K392 is $85.50 and lists 150 psi at 72 F ({D}, L)"),
    ("3/4 in black Sch 40 close nipple, 150 psi, 2-pack (Everflow NPBL3400-2)", "Amazon", 2, 10.99,
     "https://www.amazon.com/dp/B07M7L5ZMG", "Motion", "QEV to chamber and QEV to breech adapter (4)", f"({D}, L)"),
    ("3/4 MNPT x 1/4 FNPT brass hex bushing, 2-pack", "Amazon", 1, 7.99, "https://www.amazon.com/dp/B0DQLBHBTH",
     "Motion", "QEV inlet to the 1/4 nipple and port block", f"1200 psi ({D}, L)"),
    ("1/4 NPT brass sintered muffler, 10-pack (Zorfeter)", "Amazon", 1, 9.99, "https://www.amazon.com/dp/B0CP7ZM1XZ",
     "Motion", "2 used: dump outlets", "CAD assumes 22 mm long (2026-11-02, L)"),
    ("Barrels: clear polycarbonate tube 3 in OD x 2-3/4 ID x 1/8 wall, 4 ft (McMaster 8585K38)", "McMaster", 1, 84.48,
     "https://www.mcmaster.com/8585K38/", "Structure", "22.5 + 21.3 in barrels from one 4 ft stick",
     f"No pressure rating published; clamp it, never drill it ({D}, L)"),

    ("DRIVE - Falcons, one-stage belts, 10 in printed mecanum", None),
    ("Falcon 500 (owned)", "Stash", 4, 0.00, "", "Motion", "One per wheel, PWM through the safety gate", "Owned"),
    ("12T HTD 15 mm Falcon pulley (WCP-0319)", "Stash", 4, 0.00, "https://wcproducts.com/products/wcp-0319",
     "Motion", "Falcon 12T -> 120T printed into the hub (10:1)", STASH + " ($7.99 at WCP)"),
    ("HTD 5M 15 mm belt, 140T", "WCP", 4, 15.99, "https://wcproducts.com/products/htd-timing-belts-15mm-width", "Motion",
     "Falcon to wheel, fixed centres", f"In stock ({D}, L)"),
    ("Flanged bearing 1/2 hex bore, 1.125 OD (WCP-0783)", "Stash", 12, 0.00, "https://wcproducts.com/products/wcp-0783",
     "Motion", "2 per wheel axle (inner + outer rail), 4 at the pivot", STASH + " ($2.99 each)"),
    ("1/2 in hex shaft: 4 wheel axles (6 in) + 2 trunnion stubs", "Stash", 1, 0.00, "", "Motion",
     "Live axles tapped 10-32 both ends; steel stubs for the trunnions", STASH),
    ("685ZZ bearing 5 x 11 x 5 mm, 40-pack", "Amazon", 3, 9.99, "https://www.amazon.com/dp/B0G2XHXQCH",
     "Motion", "2 per roller x 56 rollers = 112", "Backup uxcell 20-pack B07FW26QBV (2026-11-02, L)"),
    ("M5 x 100 socket head cap screw 12.9, 20-pack (SVLING)", "Amazon", 4, 7.70, "https://www.amazon.com/dp/B0GHNNYVDH",
     "Motion", "56 roller axles + 24 hub through-bolts", f"In stock ({D}, L)"),
    ("M5 nylon lock nut, 100-pack", "Amazon", 1, 4.99, "https://www.amazon.com/dp/B0F1MQKZ4M", "Motion", "Roller axles and hub bolts",
     "In stock (2026-11-02, L)"),
    ("Printed drive parts: 4 hubs + 120T (PETG), 56 roller cores (PETG), 56 treads (TPU 95A)", "Owned", 1, 0.00, "", "Motion",
     "Hub prints in one piece, 243 x 246 mm", "Filament assumed owned"),

    ("ELEVATION - FTC motor on a Spark MAX, pot for the angle", None),
    ("goBILDA 5203-2402-0100 Yellow Jacket 99.5:1, 8 mm REX", "goBILDA", 1, 54.99,
     "https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-99-5-1-ratio-24mm-length-8mm-rex-shaft-60-rpm-3-3-5v-encoder/",
     "Motion", "16T -> 56T belt to the right trunnion (3.5:1, 46 N*m stall)", f"$0 if the FTC stash has one. 13.1 N*m stall, 9.2 A ({D}, L)"),
    ("REV Spark MAX (owned)", "Stash", 1, 0.00, "", "Electrical", "Drives the goBILDA in brushed mode from PWM", "Owned"),
    ("HTD 5M 9 mm belt, 145T", "WCP", 1, 9.99, "https://wcproducts.com/products/htd-timing-belts-9mm-width", "Motion",
     "Pinion to the trunnion pulley (CAD loop is exactly 725 mm)", f"In stock ({D}, L)"),
    ("10k pot, 1/4 in shaft (Bourns 81A1A-B28-A15)", "Amazon", 1, 10.70, "https://www.amazon.com/dp/B0CCBWM242",
     "Electrical", "Arm angle on the end of the left trunnion, to the STM32 ADC", f"Confirm >= 270 deg travel ({D}, L)"),

    ("FRAME + BODY - box tube, printed frame, recessed acrylic", None),
    ("3/16 in aluminum blind rivet, 0.126-0.25 grip, 100-pack (McMaster 97447A050)", "McMaster", 2, 10.23,
     "https://www.mcmaster.com/97447A050/", "Structure", "Gussets, drive plates, posts (1/8 gusset + 1/16 wall)", f"#11 drill ({D}, L)"),
    ("Heat-set inserts M2-M6, 400 pcs (Ktehloy)", "Amazon", 1, 15.97, "https://www.amazon.com/dp/B0CLKDPN65",
     "Structure", "42 M3 for panel clips, M4 for frame joints and standoffs", f"In stock ({D}, L)"),
    ("M3 x 8 button head, 304 stainless, 100 pcs", "Amazon", 1, 5.88, "https://www.amazon.com/dp/B0DKXNXLGX",
     "Structure", "42 panel corner clips", f"In stock ({D}, L)"),
    ("M4 x 12 button head, 304 stainless, 100 pcs", "Amazon", 1, 7.40, "https://www.amazon.com/dp/B0DKXQQPWS",
     "Structure", "81 frame-joint cross screws + standoffs", f"Only 2 left; backup 12.9 black-oxide B0CTH3FQLD $8.86 ({D}, L)"),
    ("Frosted acrylic 1/8 in (owned): 9 panels, largest 25.7 x 10.4 in", "Owned", 9, 0.00, "", "Cosmetic",
     "Recessed in the printed frame, held by corner clips", "Owned; outlines in the Onshape panels tab"),
    ("Printed body frame: 72 pieces, 81 tapered tenons, 42 corner clips (PETG/ASA)", "Owned", 1, 0.00, "", "Structure",
     "Frame that holds the panels and LED strips", "Filament assumed owned"),
    ("WS2812B LED strip 5 m, 60 LED/m (BTF-LIGHTING)", "Amazon", 3, 13.99, "https://www.amazon.com/dp/B088FJF9XD",
     "Electrical", "14.8 m of slot round the panel edges", "IP30 is fine inside the body (2026-11-02, L)"),

    ("BUMPERS - FRC style", None),
    ("Pool noodle 2.5 in white, 12-pack", "Amazon", 1, 48.99, "https://www.amazon.com/dp/B0B17MG8JV",
     "Structure", "8 used: two stacked per side", "48 in long (2026-11-02, L)"),
    ("Bumper cloth, white cotton canvas 36 in x 10 ft (your pick)", "Amazon", 1, 40.00, "https://www.amazon.com/dp/B08GV3NKYN",
     "Cosmetic", "Cover wrapped round the noodles and printed backing", "Price from your list, not re-checked"),

    ("CONTROLS, FAILSAFE + POWER", None),
    ("FRC 12 V battery + charger (owned)", "Stash", 2, 0.00, "", "Electrical", "Two in parallel on the slide-out sled", "Owned"),
    ("REV PDH + ATO breakers, 120 A main breaker, SB50s, wire and lugs", "Stash", 1, 0.00, "", "Electrical", "Main power",
     "Owned / " + STASH),
    ("STM32 Nucleo-64 NUCLEO-F446RE", "Amazon", 1, 38.80, "https://www.amazon.com/dp/B07PYY4R5F", "Electrical",
     "Main controller: drive, valves, fill metering, elevation loop, all four transducers", f"Third-party seller, 17 left ({D}, L)"),
    ("ESP32-S3-DevKitC-1 N8R8", "Amazon", 2, 18.99, "https://www.amazon.com/dp/B0H6MHKJXN", "Electrical",
     "1: WiFi bridge for the web UI (UART to the STM32). 2: safety node (ESP-NOW to the remote)", f"In stock ({D}, L)"),
    ("SN74AHCT125N quad buffer, 12-pack", "Amazon", 1, 7.49, "https://www.amazon.com/dp/B0DZGY5MHT", "Electrical",
     "PWM gate to the Falcons and Spark MAX, enabled only by the safety node; also 3.3 -> 5 V for the LEDs",
     f"Unbranded reseller ({D}, L)"),
    ("12 V 40 A SPDT relay + socket, 5-pack (Nilight 50003R)", "Amazon", 1, 12.14, "https://www.amazon.com/dp/B0748F1JK4",
     "Electrical", "Safety relay (valve rail), 2 dumps, fill valve, 1 spare", f"Flyback diode on every coil; sold by Amazon ({D}, L)"),
    ("ULN2803A Darlington driver", "DigiKey", 1, 3.84, "https://www.digikey.com/en/products/detail/stmicroelectronics/ULN2803A/599591",
     "Electrical", "Relay coils from 3.3 V GPIO", "76,298 in stock (2026-11-01, L)"),
    ("12/24 V -> 5 V 20 A buck, potted", "Amazon", 1, 15.99, "https://www.amazon.com/dp/B089M5R3NJ",
     "Electrical", "STM32, ESP32s, LEDs", "Cap LED brightness in firmware (2026-11-02, L)"),
    ("Latching mushroom E-stop 22 mm, 2NC (TWTADE YW1B-V4E02R)", "Amazon", 2, 13.99, "https://www.amazon.com/dp/B07NP44T74",
     "Electrical", "Robot rear face (in series with the safety relay coil) + the handheld remote", f"In stock ({D}, L)"),
    ("Panel-mount USB-C extension (AAOTOKK)", "Amazon", 1, 9.69, "https://www.amazon.com/dp/B08HS6X44P", "Electrical",
     "USB to the STM32 through the rear panel", f"In stock ({D}, L)"),
    ("Safety remote: Adafruit ESP32-S3 Reverse TFT Feather (5691)", "Adafruit", 1, 24.95, "https://www.adafruit.com/product/5691",
     "Electrical", "Handheld E-stop + dead-man trigger, ESP-NOW to the safety node, shows pressures",
     f"Not on Amazon; the plain S3 Feathers are out of stock ({D}, L)"),
    ("Safety remote: LiPo 3.7 V 1200 mAh (Adafruit 258)", "Adafruit", 1, 9.95, "https://www.adafruit.com/product/258",
     "Electrical", "Remote battery (the Feather charges it over USB-C)", f"In stock ({D}, L)"),
    ("Safety remote: 19 mm momentary stainless button, 2-pack (APIELE)", "Amazon", 1, 8.99, "https://www.amazon.com/dp/B079HR5Q4R",
     "Electrical", "Dead-man trigger on the remote", f"IP65 ({D}, L)"),

    ("LATER - spots left in the design, not in the total", None),
    ("12 V compressor ZHSYMX SQ420 (spot reserved in the front bay)", "Amazon", 0, 127.99,
     "https://www.amazon.com/dp/B0D6ZYBT4T", "Motion", "Onboard refill; dropped for now",
     "1.41 CFM free air, 100% duty at 100 psi (seller spec, 2026-11-01)"),
    ("Speaker horn + amp, fog trigger, video (from your list)", "Other", 0, 0.00, "", "Other", "Not designed in yet", "See the Parts List Template tab"),
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
