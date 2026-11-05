# Glacis printed body parts: printability report (from the CAD, not sliced)

Best of the lie-flat orientations tried (each oriented-box face and each of the six largest flat faces down), scored on support, bed contact and height. Support = faces within 45 deg of straight down that aren't on the bed and have no part within 8 mm below them (closer is a bridge). Touches = printed parts within 0.3 mm.

| Part | Vol (cm3) | Oriented box (mm) | Print height | Bed (cm2) | Support (cm2) | Fits 250 | Touches |
|---|---|---|---|---|---|---|---|
| Body frame E00S0 | 79.8 | 140 x 55 x 20 | 39 | 13.8 | 9.5 | yes | Body frame E00S1, Body frame E07S0+N11 |
| Body frame E00S1 | 72.7 | 130 x 63 x 24 | 39 | 13.8 | 8.8 | yes | Body frame E00S0, Body frame E01S0+N15, Body frame E14S1 |
| Body frame E01S0+N15 | 84.5 | 233 x 54 x 43 | 41 | 67.7 | 24.9 | yes | Body frame E00S1, Body frame E01S1, Body frame E14S1, LED light bar bracket right, Panel clip 00-1, Panel clip 01-0 |
| Body frame E01S1 | 51.9 | 185 x 46 x 17 | 13 | 47.4 | 24.0 | yes | Body frame E01S0+N15, Body frame E01S2+N16 |
| Body frame E01S2+N16 | 83.5 | 222 x 54 x 43 | 41 | 67.6 | 24.3 | yes | Body frame E01S1, Body frame E02S1, Body frame E30S1, LED light bar bracket left, Panel clip 00-2, Panel clip 05-2 |
| Body frame E02S0 | 79.8 | 139 x 60 x 20 | 39 | 13.8 | 9.5 | yes | Body frame E02S1, Body frame E03S0+N12 |
| Body frame E02S1 | 72.7 | 130 x 61 x 24 | 39 | 13.8 | 8.8 | yes | Body frame E01S2+N16, Body frame E02S0, Body frame E30S1 |
| Body frame E03S0+N12 | 52.5 | 82 x 61 x 60 | 48 | 21.4 | 6.5 | yes | Body frame E02S0, Body frame E05S1+N00b, Body frame E29S0+N10+E28S0, Panel clip 00-3, Panel clip 05-1, Speaker cup top left |
| Body frame E05S0+N00a | 109.7 | 224 x 67 x 59 | 36 | 22.5 | 21.8 | yes | Body frame E05S1+N00b, Body frame E07S0+N11, Body frame cheek R, Speaker cup top right |
| Body frame E05S1+N00b | 108.7 | 217 x 67 x 60 | 36 | 22.5 | 21.1 | yes | Body frame E03S0+N12, Body frame E05S0+N00a, Body frame cheek L, Speaker cup top left |
| Body frame E07S0+N11 | 52.5 | 83 x 60 x 60 | 48 | 21.4 | 6.5 | yes | Body frame E00S0, Body frame E05S0+N00a, Body frame E08S0+N09+E09S0, Panel clip 00-0, Panel clip 01-1, Speaker cup top right |
| Body frame E08S0+N09+E09S0 | 158.0 | 224 x 98 x 52 | 36 | 31.5 | 22.1 | yes | Body frame E07S0+N11, Body frame E12S0, Speaker cup top right |
| Body frame E12S0 | 143.5 | 197 x 65 x 48 | 54 | 20.7 | 15.1 | yes | Body frame E08S0+N09+E09S0, Body frame E15S0+N07, Body frame cheek R, Panel clip 01-2, Speaker cup top right |
| Body frame E13S0 | 144.6 | 191 x 42 x 40 | 191 | 0.3 | 8.2 | yes | Body frame E13S1+N17, Body frame E15S0+N07 |
| Body frame E13S1+N17 | 200.3 | 216 x 96 x 47 | 213 | 23.3 | 7.7 | yes | Body frame E13S0, Body frame E14S0, Body frame E17S0, Panel clip 01-4, Panel clip 02-3 |
| Body frame E14S0 | 86.5 | 233 x 44 x 25 | 18 | 55.2 | 23.7 | yes | Body frame E13S1+N17, Body frame E14S1 |
| Body frame E14S1 | 94.7 | 221 x 61 x 54 | 48 | 55.2 | 21.2 | yes | Body frame E00S1, Body frame E01S0+N15, Body frame E14S0 |
| Body frame E15S0+N07 | 170.0 | 242 x 67 x 48 | 53 | 27.5 | 18.8 | yes | Body frame E12S0, Body frame E13S0, Body frame E20S0+N03+N05+E34S1, Panel clip 01-3, Panel clip 02-0 |
| Body frame E16S0 | 118.0 | 194 x 60 x 18 | 39 | 20.4 | 13.3 | yes | Body frame E16S1, Body frame E37S2+N13 |
| Body frame E16S1 | 117.0 | 182 x 55 x 19 | 39 | 20.4 | 12.6 | yes | Body frame E16S0, Body frame E20S0+N03+N05+E34S1 |
| Body frame E17S0 | 91.8 | 232 x 44 x 26 | 19 | 59.4 | 20.4 | yes | Body frame E13S1+N17, Body frame E37S2+N13 |
| Body frame E19S0 | 93.5 | 225 x 50 x 26 | 26 | 48.3 | 25.9 | yes | Body frame E19S1, Body frame E20S0+N03+N05+E34S1 |
| Body frame E19S1 | 92.9 | 213 x 47 x 28 | 26 | 48.3 | 25.2 | yes | Body frame E19S0, Body frame cheek R |
| Body frame E20S0+N03+N05+E34S1 | 170.9 | 201 x 134 x 64 | 54 | 30.3 | 31.1 | yes | Body frame E15S0+N07, Body frame E16S1, Body frame E19S0, Body frame E34S0+N01, Panel clip 02-1, Panel clip 03-0, Panel clip 03-3, Panel clip 07-1, Panel clip 07-2 |
| Body frame E21S0 | 93.5 | 225 x 50 x 26 | 26 | 48.3 | 25.9 | yes | Body frame E21S1, Body frame E25S0+N04+N06+E36S1 |
| Body frame E21S1 | 92.9 | 213 x 47 x 28 | 26 | 48.3 | 25.2 | yes | Body frame E21S0, Body frame cheek L |
| Body frame E23S0 | 143.5 | 197 x 65 x 48 | 54 | 20.7 | 15.1 | yes | Body frame E24S0+N08, Body frame E29S0+N10+E28S0, Body frame cheek L, Panel clip 05-0, Speaker cup top left |
| Body frame E24S0+N08 | 170.0 | 242 x 67 x 48 | 53 | 27.5 | 18.8 | yes | Body frame E23S0, Body frame E25S0+N04+N06+E36S1, Body frame E31S0, Panel clip 05-4, Panel clip 06-3 |
| Body frame E25S0+N04+N06+E36S1 | 170.9 | 201 x 134 x 64 | 54 | 30.3 | 31.1 | yes | Body frame E21S0, Body frame E24S0+N08, Body frame E33S1, Body frame E36S0+N02, Panel clip 04-0, Panel clip 04-3, Panel clip 06-2, Panel clip 07-3, Panel clip 07-4 |
| Body frame E29S0+N10+E28S0 | 158.0 | 224 x 98 x 49 | 36 | 31.5 | 22.1 | yes | Body frame E03S0+N12, Body frame E23S0, Speaker cup top left |
| Body frame E30S0 | 86.5 | 233 x 44 x 25 | 18 | 55.2 | 23.7 | yes | Body frame E30S1, Body frame E31S1+N18 |
| Body frame E30S1 | 94.7 | 221 x 61 x 54 | 48 | 55.2 | 21.1 | yes | Body frame E01S2+N16, Body frame E02S1, Body frame E30S0 |
| Body frame E31S0 | 144.6 | 191 x 42 x 40 | 191 | 0.3 | 8.2 | yes | Body frame E24S0+N08, Body frame E31S1+N18 |
| Body frame E31S1+N18 | 200.3 | 216 x 96 x 47 | 213 | 23.3 | 7.7 | yes | Body frame E30S0, Body frame E31S0, Body frame E32S0, Panel clip 05-3, Panel clip 06-0 |
| Body frame E32S0 | 91.8 | 232 x 44 x 26 | 19 | 59.4 | 20.4 | yes | Body frame E31S1+N18, Body frame E37S0+N14 |
| Body frame E33S0 | 118.0 | 194 x 59 x 18 | 39 | 20.4 | 13.3 | yes | Body frame E33S1, Body frame E37S0+N14 |
| Body frame E33S1 | 117.0 | 183 x 59 x 18 | 39 | 20.4 | 12.6 | yes | Body frame E25S0+N04+N06+E36S1, Body frame E33S0 |
| Body frame E34S0+N01 | 105.9 | 203 x 80 x 46 | 36 | 25.9 | 17.9 | yes | Body frame E20S0+N03+N05+E34S1, Body frame E35S0 |
| Body frame E35S0 | 88.1 | 194 x 45 x 29 | 32 | 41.4 | 17.5 | yes | Body frame E34S0+N01, Body frame E36S0+N02 |
| Body frame E36S0+N02 | 105.9 | 203 x 80 x 46 | 36 | 25.9 | 17.9 | yes | Body frame E25S0+N04+N06+E36S1, Body frame E35S0 |
| Body frame E37S0+N14 | 108.6 | 232 x 49 x 48 | 47 | 61.4 | 25.3 | yes | Body frame E32S0, Body frame E33S0, Body frame E37S1, Panel clip 06-1, Panel clip 07-5 |
| Body frame E37S1 | 66.3 | 185 x 46 x 22 | 18 | 41.7 | 22.0 | yes | Body frame E37S0+N14, Body frame E37S2+N13 |
| Body frame E37S2+N13 | 107.6 | 220 x 50 x 49 | 47 | 61.4 | 24.6 | yes | Body frame E16S0, Body frame E17S0, Body frame E37S1, Panel clip 02-2, Panel clip 07-0 |
| Body frame cheek L | 157.9 | 220 x 122 x 68 | 66 | 48.6 | 34.5 | yes | Body frame E05S1+N00b, Body frame E21S1, Body frame E23S0, Panel clip 00-4, Panel clip 04-1, Panel clip 04-2, Panel clip 05-0, Speaker cup top left |
| Body frame cheek R | 157.9 | 220 x 123 x 70 | 66 | 48.6 | 34.5 | yes | Body frame E05S0+N00a, Body frame E12S0, Body frame E19S1, Panel clip 00-5, Panel clip 01-2, Panel clip 03-1, Panel clip 03-2, Speaker cup top right |
| Bumper corner bracket front L | 150.7 | 107 x 92 x 56 | 62 | 73.1 | 0.0 | yes |  |
| Bumper corner bracket front R | 150.7 | 107 x 93 x 56 | 62 | 73.1 | 0.0 | yes |  |
| Bumper corner bracket rear L | 150.7 | 107 x 92 x 56 | 62 | 73.1 | 0.0 | yes |  |
| Bumper corner bracket rear R | 150.7 | 107 x 92 x 56 | 62 | 73.1 | 0.0 | yes |  |
| Frame mount L -205 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount L -280 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount L 100 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount L 280 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount R -205 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount R -280 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount R 100 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount R 280 | 31.8 | 53 x 30 x 28 | 25 | 15.5 | 0.0 | yes |  |
| Frame mount front -170 | 29.6 | 57 x 41 x 30 | 32 | 10.6 | 2.2 | yes |  |
| Frame mount front 0 | 30.9 | 60 x 41 x 30 | 32 | 11.1 | 2.2 | yes |  |
| Frame mount front 170 | 29.6 | 57 x 41 x 30 | 32 | 10.6 | 2.2 | yes |  |
| Frame mount rear -170 | 29.6 | 56 x 38 x 30 | 32 | 10.6 | 2.2 | yes |  |
| Frame mount rear 0 | 30.9 | 58 x 38 x 30 | 32 | 11.1 | 2.2 | yes |  |
| Frame mount rear 170 | 29.6 | 56 x 38 x 30 | 32 | 10.6 | 2.2 | yes |  |
| LED light bar bracket left | 4.6 | 39 x 30 x 15 | 30 | 0.5 | 2.0 | yes | Body frame E01S2+N16 |
| LED light bar bracket right | 4.6 | 39 x 30 x 15 | 30 | 0.5 | 2.0 | yes | Body frame E01S0+N15 |
| Panel clip 00-0 | 1.2 | 29 x 25 x 3 | 3 | 4.6 | 0.0 | yes | Body frame E07S0+N11 |
| Panel clip 00-1 | 1.3 | 30 x 27 x 3 | 3 | 5.0 | 0.0 | yes | Body frame E01S0+N15 |
| Panel clip 00-2 | 1.3 | 30 x 27 x 3 | 3 | 5.0 | 0.0 | yes | Body frame E01S2+N16 |
| Panel clip 00-3 | 1.2 | 29 x 25 x 3 | 3 | 4.6 | 0.0 | yes | Body frame E03S0+N12 |
| Panel clip 00-4 | 1.1 | 30 x 24 x 3 | 3 | 4.6 | 0.0 | yes | Body frame cheek L |
| Panel clip 00-5 | 1.1 | 30 x 24 x 3 | 3 | 4.6 | 0.0 | yes | Body frame cheek R |
| Panel clip 01-0 | 2.1 | 42 x 30 x 3 | 3 | 8.5 | 0.0 | yes | Body frame E01S0+N15 |
| Panel clip 01-1 | 1.2 | 29 x 25 x 3 | 3 | 4.7 | 0.0 | yes | Body frame E07S0+N11 |
| Panel clip 01-2 | 2.6 | 50 x 30 x 3 | 3 | 10.4 | 0.0 | yes | Body frame E12S0, Body frame cheek R |
| Panel clip 01-3 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E15S0+N07 |
| Panel clip 01-4 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E13S1+N17 |
| Panel clip 02-0 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E15S0+N07 |
| Panel clip 02-1 | 1.1 | 30 x 24 x 3 | 3 | 4.6 | 0.0 | yes | Body frame E20S0+N03+N05+E34S1 |
| Panel clip 02-2 | 1.5 | 30 x 30 x 3 | 3 | 6.1 | 0.0 | yes | Body frame E37S2+N13, Panel clip 07-0 |
| Panel clip 02-3 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E13S1+N17 |
| Panel clip 03-0 | 1.1 | 29 x 25 x 2 | 2 | 4.5 | 0.0 | yes | Body frame E20S0+N03+N05+E34S1 |
| Panel clip 03-1 | 1.1 | 29 x 25 x 3 | 2 | 4.5 | 0.0 | yes | Body frame cheek R |
| Panel clip 03-2 | 1.1 | 29 x 25 x 2 | 2 | 4.5 | 0.0 | yes | Body frame cheek R |
| Panel clip 03-3 | 1.1 | 29 x 25 x 2 | 2 | 4.5 | 0.0 | yes | Body frame E20S0+N03+N05+E34S1 |
| Panel clip 04-0 | 1.1 | 29 x 25 x 3 | 2 | 4.5 | 0.0 | yes | Body frame E25S0+N04+N06+E36S1 |
| Panel clip 04-1 | 1.1 | 29 x 25 x 2 | 2 | 4.5 | 0.0 | yes | Body frame cheek L |
| Panel clip 04-2 | 1.1 | 29 x 25 x 2 | 2 | 4.5 | 0.0 | yes | Body frame cheek L |
| Panel clip 04-3 | 1.1 | 29 x 25 x 3 | 2 | 4.5 | 0.0 | yes | Body frame E25S0+N04+N06+E36S1 |
| Panel clip 05-0 | 2.6 | 50 x 30 x 3 | 3 | 10.4 | 0.0 | yes | Body frame E23S0, Body frame cheek L |
| Panel clip 05-1 | 1.2 | 29 x 25 x 3 | 3 | 4.7 | 0.0 | yes | Body frame E03S0+N12 |
| Panel clip 05-2 | 2.1 | 42 x 30 x 3 | 3 | 8.5 | 0.0 | yes | Body frame E01S2+N16 |
| Panel clip 05-3 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E31S1+N18 |
| Panel clip 05-4 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E24S0+N08 |
| Panel clip 06-0 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E31S1+N18 |
| Panel clip 06-1 | 1.5 | 30 x 30 x 3 | 3 | 6.1 | 0.0 | yes | Body frame E37S0+N14, Panel clip 07-5 |
| Panel clip 06-2 | 1.1 | 30 x 24 x 3 | 3 | 4.6 | 0.0 | yes | Body frame E25S0+N04+N06+E36S1 |
| Panel clip 06-3 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E24S0+N08 |
| Panel clip 07-0 | 1.5 | 30 x 30 x 3 | 3 | 6.0 | 0.0 | yes | Body frame E37S2+N13, Panel clip 02-2 |
| Panel clip 07-1 | 1.1 | 30 x 24 x 3 | 3 | 4.6 | 0.0 | yes | Body frame E20S0+N03+N05+E34S1 |
| Panel clip 07-2 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E20S0+N03+N05+E34S1 |
| Panel clip 07-3 | 1.1 | 29 x 25 x 3 | 3 | 4.5 | 0.0 | yes | Body frame E25S0+N04+N06+E36S1 |
| Panel clip 07-4 | 1.1 | 30 x 24 x 3 | 3 | 4.6 | 0.0 | yes | Body frame E25S0+N04+N06+E36S1 |
| Panel clip 07-5 | 1.5 | 30 x 30 x 3 | 3 | 6.0 | 0.0 | yes | Body frame E37S0+N14, Panel clip 06-1 |
| Speaker cup top left | 149.9 | 161 x 158 x 87 | 83 | 237.6 | 0.0 | yes | Body frame E03S0+N12, Body frame E05S1+N00b, Body frame E23S0, Body frame E29S0+N10+E28S0, Body frame cheek L, Speaker grille top left |
| Speaker cup top right | 149.9 | 175 x 169 x 86 | 83 | 237.6 | 0.0 | yes | Body frame E05S0+N00a, Body frame E07S0+N11, Body frame E08S0+N09+E09S0, Body frame E12S0, Body frame cheek R, Speaker grille top right |
| Speaker grille top left | 89.6 | 152 x 147 x 4 | 4 | 223.9 | 0.0 | yes | Speaker cup top left |
| Speaker grille top right | 89.6 | 152 x 147 x 4 | 4 | 223.9 | 0.0 | yes | Speaker cup top right |
| Tower bracket L | 10.5 | 50 x 25 x 24 | 23 | 9.3 | 0.8 | yes |  |
| Tower bracket R | 10.5 | 50 x 25 x 24 | 23 | 9.3 | 0.8 | yes |  |
| Underglow bracket front 1 | 9.8 | 168 x 22 x 19 | 16 | 31.2 | 0.0 | yes |  |
| Underglow bracket front 2 | 18.5 | 167 x 20 x 19 | 16 | 32.0 | 0.0 | yes |  |
| Underglow bracket front 3 | 9.8 | 168 x 22 x 19 | 16 | 31.2 | 0.0 | yes |  |
| Underglow bracket left 1 | 15.6 | 189 x 22 x 20 | 16 | 33.7 | 0.0 | yes |  |
| Underglow bracket left 2 | 21.4 | 189 x 20 x 17 | 16 | 37.3 | 0.0 | yes |  |
| Underglow bracket left 3 | 20.6 | 189 x 20 x 20 | 16 | 35.7 | 0.0 | yes |  |
| Underglow bracket left 4 | 16.4 | 189 x 21 x 20 | 16 | 35.3 | 0.0 | yes |  |
| Underglow bracket rear 1 | 9.8 | 168 x 22 x 19 | 16 | 31.2 | 0.0 | yes |  |
| Underglow bracket rear 2 | 18.5 | 167 x 20 x 18 | 16 | 32.0 | 0.0 | yes |  |
| Underglow bracket rear 3 | 9.8 | 168 x 22 x 19 | 16 | 31.2 | 0.0 | yes |  |
| Underglow bracket right 1 | 15.6 | 189 x 22 x 20 | 16 | 33.7 | 0.0 | yes |  |
| Underglow bracket right 2 | 21.4 | 189 x 20 x 17 | 16 | 37.3 | 0.0 | yes |  |
| Underglow bracket right 3 | 20.6 | 189 x 20 x 20 | 16 | 35.7 | 0.0 | yes |  |
| Underglow bracket right 4 | 16.4 | 189 x 21 x 20 | 16 | 35.3 | 0.0 | yes |  |
