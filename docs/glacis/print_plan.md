# Glacis body frame: print plan (estimate, not sliced)

PETG, 0.6 mm nozzle, 0.3 mm layers, 2 walls, 10% gyroid. Elegoo Centauri Carbon (CC1) and Centauri Carbon 2 (CC2), both 256 mm cubed, packed to 250 x 250 mm.

## Totals

- **45 frame pieces on 11 plates**
- **PETG: 2.97 kg** (about $39 at $13/kg), including 145 g of support and 3% for brims and purge
- **Machine time: 73 h** in all; with both printers going, **37 h** (CC1 37 h, CC2 37 h)
- "Hollow to 2 mm" read as walls 2 mm thick is 3 walls: 4.05 kg and 50 h on both printers. Nothing is hollowed in the CAD: the slicer makes every piece a shell over sparse infill already, and a modelled hollow would add inner walls.
- The other printed body parts (clips, mount posts, tower and corner brackets, underglow and light bar brackets, speaker cups and grilles; 4 walls, 25%): 78 parts, 2.03 kg, 6 plates, 27 h on both printers.
- Model: shell = surface area x 1.3 mm, infill 10% of the rest, support from part_report (overhangs with nothing within 8 mm below, at 12%), at 9 mm3/s average plus 6 min a plate. Treat it as +/-25%: a slicer run on the CC's PETG profile will be closer.

## Before the frame

- Print a test joint first on each printer: two 40 mm stubs with one tapered tenon (TENON_CLEAR is 0.3 mm a side for the 0.6 nozzle). If it doesn't seat fully by hand, raise TENON_CLEAR and rebuild before the plates.
- Lit faces: the frame glows through its outer 7 mm. Sparse gyroid there shows as dark lines, so give the 12 mm lip a 100% infill modifier (about +10% plastic) or print the lit pieces at 4 walls. Don't put 4-wall modifiers round the tenons and inserts on lit faces: they show as dark spots.
- Glued joints (the filled LED corners): before the epoxy, push a strip offcut through the tunnel across the joint and pull it out after, so squeeze-out can't block the strip.

## Plates

| Plate | Printer | Pieces | PETG (g) | Time (h) |
|---|---|---|---|---|
| 1 | CC1 | E00S1, E02S1, E03S0+N12, E13S1+N17, E19S1, E21S1, E31S1+N18 | 447 | 11.0 |
| 2 | CC1 | E00S0, E16S1, E19S0, E33S0, E33S1, E37S1 | 319 | 7.9 |
| 3 | CC1 | E01S2+N16, E15S0+N07, E24S0+N08, E37S0+N14 | 307 | 7.5 |
| 4 | CC1 | E05S0+N00a, E30S0, cheek R | 221 | 5.5 |
| 5 | CC1 | E20S0+N03+N05+E34S1, E29S0+N10+E28S0 | 191 | 4.7 |
| 6 | CC2 | E01S1, E12S0, E16S0, E21S0, E23S0, E35S0 | 351 | 8.6 |
| 7 | CC2 | E08S0+N09+E09S0, E13S0, E25S0+N04+N06+E36S1, E31S0 | 336 | 8.3 |
| 8 | CC2 | E14S1, E17S0, E30S1, E32S0, E37S2+N13 | 318 | 7.8 |
| 9 | CC2 | E01S0+N15, E02S0, E34S0+N01, E36S0+N02 | 231 | 5.7 |
| 10 | CC2 | E05S1+N00b, E14S0, cheek L | 221 | 5.5 |
| 11 | CC2 | E07S0+N11 | 32 | 0.9 |

## Pieces

| Piece | Footprint x height (mm) | Volume (cm3) | Support (cm3) | PETG (g) | Time (min) |
|---|---|---|---|---|---|
| E00S0 | 140 x 41 x 39 | 79.8 | 0.9 | 40 | 58 |
| E00S1 | 129 x 44 x 39 | 72.7 | 0.8 | 38 | 56 |
| E01S0+N15 | 234 x 55 x 41 | 84.5 | 1.0 | 60 | 88 |
| E01S1 | 185 x 48 x 13 | 51.9 | 1.0 | 38 | 55 |
| E01S2+N16 | 222 x 55 x 41 | 83.5 | 1.0 | 60 | 87 |
| E02S0 | 140 x 42 x 39 | 79.8 | 0.9 | 40 | 58 |
| E02S1 | 129 x 43 x 39 | 72.7 | 0.8 | 38 | 56 |
| E03S0+N12 | 81 x 48 x 48 | 52.5 | 1.2 | 32 | 47 |
| E05S0+N00a | 223 x 71 x 36 | 109.7 | 2.4 | 66 | 96 |
| E05S1+N00b | 217 x 70 x 36 | 108.7 | 2.3 | 65 | 95 |
| E07S0+N11 | 81 x 48 x 48 | 52.5 | 1.2 | 32 | 47 |
| E08S0+N09+E09S0 | 224 x 94 x 36 | 158.0 | 1.8 | 86 | 125 |
| E12S0 | 197 x 48 x 54 | 143.5 | 1.9 | 68 | 99 |
| E13S0 | 42 x 40 x 191 | 144.6 | 1.2 | 72 | 106 |
| E13S1+N17 | 96 x 66 x 213 | 200.3 | 1.2 | 106 | 154 |
| E14S0 | 233 x 42 x 18 | 86.5 | 3.5 | 59 | 86 |
| E14S1 | 221 x 44 x 48 | 94.7 | 3.2 | 64 | 93 |
| E15S0+N07 | 242 x 50 x 53 | 170.0 | 1.9 | 88 | 129 |
| E16S0 | 194 x 43 x 39 | 118.0 | 1.2 | 58 | 84 |
| E16S1 | 182 x 40 x 39 | 117.0 | 1.1 | 57 | 84 |
| E17S0 | 232 x 42 x 19 | 91.8 | 2.9 | 60 | 88 |
| E19S0 | 225 x 40 x 26 | 93.5 | 6.6 | 64 | 94 |
| E19S1 | 213 x 37 x 26 | 92.9 | 6.5 | 64 | 93 |
| E20S0+N03+N05+E34S1 | 203 x 133 x 54 | 170.9 | 2.9 | 105 | 154 |
| E21S0 | 225 x 40 x 26 | 93.5 | 6.6 | 64 | 94 |
| E21S1 | 213 x 37 x 26 | 92.9 | 6.5 | 64 | 93 |
| E23S0 | 197 x 48 x 54 | 143.5 | 1.9 | 68 | 99 |
| E24S0+N08 | 242 x 50 x 53 | 170.0 | 1.9 | 88 | 129 |
| E25S0+N04+N06+E36S1 | 203 x 133 x 54 | 170.9 | 2.9 | 105 | 154 |
| E29S0+N10+E28S0 | 224 x 94 x 36 | 158.0 | 1.8 | 85 | 125 |
| E30S0 | 233 x 42 x 18 | 86.5 | 3.5 | 59 | 86 |
| E30S1 | 221 x 44 x 48 | 94.7 | 3.2 | 64 | 93 |
| E31S0 | 42 x 40 x 191 | 144.6 | 1.2 | 72 | 106 |
| E31S1+N18 | 96 x 66 x 213 | 200.3 | 1.2 | 106 | 154 |
| E32S0 | 232 x 42 x 19 | 91.8 | 2.9 | 60 | 88 |
| E33S0 | 194 x 43 x 39 | 118.0 | 1.2 | 58 | 84 |
| E33S1 | 182 x 43 x 39 | 117.0 | 1.1 | 57 | 84 |
| E34S0+N01 | 202 x 74 x 36 | 105.9 | 1.5 | 66 | 96 |
| E35S0 | 194 x 34 x 32 | 88.1 | 5.3 | 57 | 82 |
| E36S0+N02 | 202 x 74 x 36 | 105.9 | 1.5 | 66 | 96 |
| E37S0+N14 | 233 x 48 x 47 | 108.6 | 3.6 | 70 | 102 |
| E37S1 | 185 x 44 x 18 | 66.3 | 3.1 | 43 | 63 |
| E37S2+N13 | 221 x 50 x 47 | 107.6 | 3.6 | 70 | 102 |
| cheek L | 216 x 124 x 66 | 157.9 | 5.5 | 97 | 141 |
| cheek R | 216 x 124 x 66 | 157.9 | 5.5 | 97 | 141 |

## Worth a look

- E13S0: only 0.3 cm2 on the bed: use a brim
- E31S0: only 0.3 cm2 on the bed: use a brim
