"""Part numbers for every part (Micah, 2026-11-11: "give every single part a number or code that corresponds to
something on the list. Acr for white acrylic, ASh for aluminum sheet, ATu for aluminum tubes, AEx for extrusion, and a
part and number for everything specific corresponding to what system it's a part of ... for 3D printed parts, put 3DP.
a pneumatic valve could be P24 ... make every part uniquely numbered ... just make it intuitive").

Scheme (the list's codes are in bom/glacis_bom_codes.json and column A of the Sheet):
- a bought or owned part: its list row's code and which one it is, e.g. P23-1 and P23-2 are the two firing valves
- a part we make: material, system letter, number: 3DP-B014 (printed, body), ASh-D02 (aluminium sheet, drive),
  ATu-D05 (aluminium tube), AEx-R03 (20x20 extrusion), ABr-P1 (aluminium bar), Acr-B04 (white acrylic)
System letters: P pneumatics + gun, D drive + chassis, E elevation + pivot, C controls + power, S sound, F fog,
B body + bumpers, R rails, L lights.

Writes out/part_codes.json ({STEP file: {part name: code}}) and out/part_codes.csv.
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.path.join(HERE, "out", "step")

# CAD label (start of the part's bom text) -> list row (start of its name)
ROW_OF = [
    ("1 in NPT close nipple", "1 in NPT close nipple"), ("1 in cam-buckle strap", "1 in cam-buckle strap"),
    ("1/4 NPT brass 90 deg elbow", "1/4 NPT brass 90 deg elbow"), ("1/4 NPT brass close nipple", "1/4 NPT brass close nipple"),
    ("1/4 NPT brass cross", "1/4 NPT brass cross"), ("Rear manifold: 1/4 NPT brass crosses", "1/4 NPT brass cross"),
    ("1/4 NPT brass nipple x 2-1/2", "1/4 NPT brass nipple 2-1/2"), ("1/4 NPT brass plug", "1/4 NPT plug, 304"),
    ("1/4 NPT brass street elbow", "1/4 NPT brass street elbow"), ("10k linear pot", "10k linear pot"),
    ("12 V 40 A SPDT relay", "12 V 40 A relay"), ("12 V 5015 blower", "12 V 5015 blower"),
    ("12->5 V 20 A buck", "12/24 V -> 5 V 20 A buck"), ("120 A main breaker", "REV PDH + ATO breakers"),
    ("Anderson SB50 pair", "REV PDH + ATO breakers"), ("REV PDH", "REV PDH + ATO breakers"),
    ("1200 W 20 A boost", "1200 W 20 A boost"), ("ADS1115", "ADS1115"), ("Air tank", "Air tank"),
    ("Anderson SB50 panel-mount", "Anderson SB50 flush-mount"), ("Contactor + battery relays", "Contactor + battery relays"),
    ("DOT push-to-connect 1/4 tube x 1/4 NPT (Boeray)", "DOT push-to-connect 1/4 tube x 1/4 NPT male, straight"),
    ("DOT push-to-connect swivel elbow", "DOT push-to-connect swivel elbow"), ("ESP32-S3-DevKitC", "ESP32-S3 boards"),
    ("FRC 12 V 18 Ah battery", "FRC 12 V battery"), ("Falcon 500", "Falcon 500"), ("Fill check valve", "Fill check valve"),
    ("Firing valve", "Firing valves"), ("Flanged bearing", "Flanged bearing"), ("Fog fluid pump", "Fog fluid pump"),
    ("Fog heater core", "Fog heater core"), ("Front light bar", "Front light bar"), ("Light bar end bracket", "Front light bar"),
    ("G1/4 BSPP male x 1/4 NPT male", "Adapters: G1/4"), ("HTD 5M 9 mm belt", "HTD 5M 9 mm belt"), ("HTD 5M 15 mm belt", "HTD 5M 15 mm drive belt"),
    ("In valve: GOGO", "In valves: GOGO"), ("Latching mushroom E-stop", "Latching mushroom E-stop"),
    ("Logic supply", "Logic supply"),
    ("M5 aluminum standoff", "M5 aluminium standoffs"), ("MOSFET switch module 5-36 V 15 A, 3.3-20 V", "MOSFET switch module 5-36 V 15 A, 3.3-20 V"),
    ("MOSFET switch module 5-36 V 15 A with heat sink", "MOSFET switch module 5-36 V 15 A, 6 pcs"),
    ("ULN2803A", "ULN2803A"), ("Thermocouple amp MAX6675", "Thermocouple amp MAX6675"),
    ("Inline ATO fuse holder", "Inline ATO fuse holder"), ("DS18B20", "DS18B20"), ("Thermal cutout KSD301", "Thermal cutout KSD301"),

    ("Main controller", "Main controller"), ("Main valve", "Main valve"), ("PWM expander", "PWM expander"),
    ("Panel-mount USB-C", "Panel-mount USB-C"), ("Pressure transducer", "Pressure transducer"),
    ("Fill plug:", "Fill plug:"), ("REV Spark MAX", "REV Spark MAX"), ("Relief valve", "Relief valve"),
    ("Siren speaker", "Siren speaker"), ("TPA3255", "TPA3255"), ("WCP-0319 12T", "12T HTD 15 mm Falcon pulley"),
    ("goBILDA 5203", "goBILDA 5203"), ("Chamber end disc", "Chamber end plates"), ("1/2 in hex shaft", "1/2 in hex shaft"),
    ("Barrel: clear polycarbonate", "Barrels:"), ("Bumper backing", "Bumper backing"),
    ("Bumper fabric cover", "Canvas: HYVAKUPPA"), ("Bumper foam strip", "Bumper foam"),
    ("Chamber inlet", "Chamber inlets"), ("Chamber outlet", "Chamber outlets"), ("Chamber: 3 in Sch 40", "Chambers:"),
    ("DOT nylon tube", "DOT nylon air line"), ("Fog tube (owner's", "Flexible fog tube"),
    ("Silicone tube 1/2 ID", "Silicone tube 3/4 in ID"), ("Silicone tube 3/4 ID", "Silicone tube 3/4 in ID"), ("WS2812B strip 10 mm", "WS2812B LED strip 10 mm"),
    ("WS2812B strip 5 mm", "WS2812B LED strip 5 mm"),
]
NOT_LISTED = ("M8 threaded rod", "Mecanum ")   # the printed wheels' parts (deferred)


def system(tab, name):
    n = name.lower()
    if any(k in n for k in ("fog", "smoke")):
        return "F"
    if any(k in n for k in ("speaker", "grille")):
        return "S"
    if any(k in n for k in ("tower", "pivot", "bearing block", "elevation")):
        return "E"
    if tab.startswith(("gun_pivots", "pneumatics")):
        return "P"
    if tab.startswith("add_on_rails"):
        return "R"
    if tab.startswith("power_electronics"):
        return "C"
    if tab.startswith(("bumpers", "body_")):
        return "B"
    if tab.startswith("lights_speakers"):
        return "L"
    return "D"                                   # chassis, drive, wheels


def material(p):
    b, k, n = p.get("bom") or "", p.get("kind") or "", p["name"]
    if k == "print":
        return "3DP"
    if k == "acrylic" or n.startswith("Panel "):
        return "Acr"
    if "box tube" in b:
        return "ATu"
    if "40x40 T-slot" in b or "20x20 T-slot" in b:
        return "AEx"
    if "Breech puck" in b or "Breech adapter" in b:
        return "ABr"
    if "1/8 Al" in b or "(1/8 Al" in n:
        return "ASh"
    return None


def main():
    codes = json.load(open(os.path.join(HERE, "..", "..", "bom", "glacis_bom_codes.json"), encoding="utf-8"))
    man = json.load(open(os.path.join(ST, "manifest.json")))
    out, rows, count, missing = {}, [], {}, {}
    for m in man:
        f = m["file"]
        if f.startswith("visuals"):                  # show-off visuals: not parts, no codes
            continue
        tab = f[:-5]
        out[f] = {}
        for p in json.load(open(os.path.join(ST, tab + ".names.json"), encoding="utf-8")):
            b = p.get("bom") or p["name"]
            mat = material(p)
            if mat:
                key = f"{mat}-{system(tab, p['name'])}"
                count[key] = count.get(key, 0) + 1
                code, row = f"{key}{count[key]:03d}" if mat == "3DP" else f"{key}{count[key]:02d}", mat
            else:
                lst = next((r for c, r in ROW_OF if b.startswith(c)), None)
                rc = next((v for k, v in codes.items() if lst and k.startswith(lst)), None)
                if rc is None:
                    tag = "X" if not b.startswith(NOT_LISTED) else "W"     # W: the deferred printed wheels' parts
                    missing[b] = missing.get(b, 0) + 1
                    rc = tag
                count[rc] = count.get(rc, 0) + 1
                code, row = f"{rc}-{count[rc]}", rc
            out[f][p["name"]] = code
            rows.append((code, p["name"], tab, b))
    json.dump(out, open(os.path.join(HERE, "out", "part_codes.json"), "w", encoding="utf-8"), indent=0)
    with open(os.path.join(HERE, "out", "part_codes.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Part number", "Part", "Tab", "CAD label"])
        for r in sorted(rows, key=lambda r: (re.sub(r"\d+$", "", r[0]), [int(x) for x in re.findall(r"\d+", r[0])])):
            w.writerow(r)
    print(f"{len(rows)} parts coded; not on the list: {missing}")
    return out


if __name__ == "__main__":
    main()
