"""Glacis (Mark 5) layout: every shared number lives here. Units: mm, degrees.

Frame: X forward, Y left, Z up. Origin on the floor, centred between the axles.
Inch values are written as `n * IN` so they read like the spec.
Run `python params.py` to print the derived layout.
"""
import math

IN = 25.4


# ------------------------------------------------------------------ belts
HTD = 5.0                                   # HTD 5M pitch


def pd(teeth):                              # pitch diameter
    return teeth * HTD / math.pi


def belt_length(c, d1, d2):                 # open belt, pitch line
    b = math.asin((d2 - d1) / (2 * c))
    return 2 * c * math.cos(b) + math.pi / 2 * (d1 + d2) + b * (d2 - d1)


def centre_for_belt(teeth_belt, d1, d2):    # solve centre distance for a stock belt
    target, lo, hi = teeth_belt * HTD, (d2 - d1) / 2 + 1, 2000.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if belt_length(mid, d1, d2) < target else (lo, mid)
    return (lo + hi) / 2


# ------------------------------------------------------------------ drive
WHEEL_R = 6 * IN                            # 12 in printed mecanum
WHEEL_W = 3.25 * IN
AXLE_Z = WHEEL_R
WB = 18 * IN                                # wheelbase
AX_X = WB / 2                               # axles at x = +/-AX_X
N_ROLL, ROLL_L, ROLL_R0 = 16, 82.0, 17.0    # rollers per wheel, length, max radius (4.9 mm between
                                            # neighbours, 7% contact overlap, sweep 78 mm wide)
ROLL_BRG = (11.0, 5.0)                      # 685ZZ (5 x 11 x 5) in each roller end, M5 axle
LUG_R = 6.5                                 # printed boss round each roller axle end
N_ARCS = 4                                  # each lug plate prints as 4 arcs (bed 256)
ROLL_ANGLE = 45.0

FW = 22.25 * IN                             # over the outer rails (27.8 in over the bumpers, door limit 28)
RAIL_W, RAIL_H = 1 * IN, 2 * IN             # 1x2 extrusion standing on edge
RAIL_Z = (AXLE_Z - RAIL_H / 2, AXLE_Z + RAIL_H / 2)
PLATE_T = 0.125 * IN

# side band, outside in (y > 0 side; the left side mirrors it)
OUTER_RAIL_Y = (FW / 2 - RAIL_W, FW / 2)
WHEEL_Y = (OUTER_RAIL_Y[0] - 3.0 - WHEEL_W, OUTER_RAIL_Y[0] - 3.0)
PULLEY_FACE = 21.0                          # 15 mm belt + two 3 mm flanges
P2_Y = (WHEEL_Y[0] - 2.0 - PULLEY_FACE, WHEEL_Y[0] - 2.0)     # wheel pulley + compound small
P1_Y = (P2_Y[0] - 1.5 - PULLEY_FACE, P2_Y[0] - 1.5)          # compound big + Falcon pinion
DRIVE_PLATE_Y = (P1_Y[0] - 1.5 - PLATE_T, P1_Y[0] - 1.5)
INNER_RAIL_Y = (DRIVE_PLATE_Y[0] - RAIL_W, DRIVE_PLATE_Y[0])

# two-stage HTD 5M, 15 mm: Falcon 12T -> 72T, compound 18T -> wheel 120T  (40:1)
T_PIN, T_C_BIG, T_C_SMALL, T_WHEEL = 12, 72, 18, 120
BELT1_T, BELT2_T = 80, 150                  # stock belt tooth counts (150T puts the compound outside the
                                            # wheel's swept circle)
RATIO = (T_C_BIG / T_PIN) * (T_WHEEL / T_C_SMALL)
C2 = centre_for_belt(BELT2_T, pd(T_C_SMALL), pd(T_WHEEL))
C1 = centre_for_belt(BELT1_T, pd(T_PIN), pd(T_C_BIG))
THETA2 = 34.0                               # compound sits up and inboard of the wheel axle
PHI1 = -14.0                                # Falcon sits behind/below the compound (toward the wheel)


def compound_xz(front):                     # front=True for the front corners
    s = 1 if front else -1
    return (s * (AX_X - C2 * math.cos(math.radians(THETA2))),
            AXLE_Z + C2 * math.sin(math.radians(THETA2)))


def falcon_xz(front):
    s = 1 if front else -1
    cx, cz = compound_xz(front)
    return (cx + s * C1 * math.cos(math.radians(PHI1)), cz + C1 * math.sin(math.radians(PHI1)))


FALCON_D, FALCON_L = 60.0, 89.9             # CTRE Falcon 500 user guide (store page says 81 mm long)
FALCON_FREE_RPM = 6380
WHEEL_FREE_FPS = FALCON_FREE_RPM / RATIO * math.pi * 12 / 60 / 12

# frame ends and cross rails (1x2 on edge, running across)
FRAME_X = AX_X + WHEEL_R + 3.0 + RAIL_W     # outside face of the end cross rails
GROUND_CLEAR = 4 * IN

# ------------------------------------------------------------------ bumpers (FRC style)
NOODLE_D = 2.5 * IN
BUMP_BACK_T = 6.0                           # printed backing
BUMP_DEPTH = BUMP_BACK_T + NOODLE_D         # out from the rail face
BUMP_Z = (GROUND_CLEAR, GROUND_CLEAR + 2 * NOODLE_D)        # two noodles stacked

# ------------------------------------------------------------------ body (printed frame + acrylic)
ACRYLIC_T = 0.125 * IN
PANEL_MAX = (18 * IN, 36 * IN)
LIP = 2.0                                   # groove lip in front of the panel
GROOVE_W = ACRYLIC_T + 0.4                  # slip fit
GROOVE_D = 8.0                              # how far a panel edge sits in its groove
MEM_W, MEM_H = 18.0, 22.0                   # printed member: width on each panel, depth inward
NODE_SETBACK = 48.0                         # node block reach from a vertex along each member
PRINT_MAX = 240.0                           # longest straight printed segment (bed is 256)
TENON = (6.5, 6.5, 12.0, 0.5)               # base w, base h, length, taper per side (1.8 mm wall to
                                            # the groove and the LED slot)
TENON_CLEAR = 0.15
LED_SLOT = (2.6, 10.6)                      # 10 mm strip standing on edge: slot width, depth
LINER_SLOT = 2.5                            # denim / aramid liner clamp slot

Y_S = OUTER_RAIL_Y[1] + MEM_H               # side wall outer face
Y_SLOT = 80.0                               # gun slot half width (trunnion discs sit here)
Z_WALL_BOT = BUMP_Z[1] + 1.5                # side walls start on top of the bumpers (cover lip under them)

# gun pivot and the side outline of the body (x, z), front to back along the top
PIVOT = (40.0, 532.0)
Z_SLOT_FLOOR = 330.0
SIDE_OUTLINE = [
    (FRAME_X, Z_WALL_BOT),                  # F0  nose, on the bumper
    (310.0, 330.0),                         # C   glacis top / turret front foot
    (215.0, 745.0),                         # T2  turret front top
    (-120.0, 745.0),                        # T3  turret top rear
    (-175.0, 700.0),                        # T4  turret rear foot / rear deck
    (-FRAME_X + 29.0, 700.0),               # R1  rear deck
    (-FRAME_X, 671.0),                      # R2  rear chamfer
    (-FRAME_X, Z_WALL_BOT),                 # R3  rear bottom
]
X_SLOT_REAR = -175.0

# ------------------------------------------------------------------ gun
BARREL_OD, BARREL_WALL, BARREL_LEN = 3.0 * IN, 0.0625 * IN, 23.5 * IN   # WCP-1275, two per 47 in stick
N_BARRELS = 3
PITCH = 90.0                                # vertical spacing of the stacked barrels
QEV_OFFSET = 0.0                           # QEV/chamber line sits this far behind the pivot (balance)
CRADLE_Y = 45.5                             # cradle plate inner faces at +/- this (between QEV and fittings)
DISC_R = 185.0                              # rotating trunnion disc
DISC_HOLE_R = 190.0                         # its opening in the fixed slot wall
DISC_Y = (Y_SLOT + LIP, Y_SLOT + LIP + 6.0) # disc 6 mm thick, flush with the slot wall panel
TOWER_X = PIVOT[0]
ELEV_RANGE = (0.0, 90.0)
ELEV_SHOW = 20.0                            # pose exported to Onshape
SERVO_RATIO = 3.0                           # 20T -> 60T printed HTD

# ------------------------------------------------------------------ pneumatics / power
TANK_D, TANK_L = 160.0, 432.0               # 2 gal 200 psi (updated in cots.py)
TANK_X = -280.0
TANK_Z = (415.0, 590.0)
BATT = (7.13 * IN, 3.01 * IN, 6.57 * IN)    # FRC battery L, W, H (with terminals)
BATT_GAP = 6.0
BELLY_Z = RAIL_Z[0]                         # bellypan bolted under the inner rails
COMP_BOX = (243.0, 128.0, 181.0)            # ZHSYMX SQ420 footprint, spot only
ELEC_BAY = ((215.0, 378.0), (-120.0, 120.0), (BELLY_Z + 4.0, 300.0))


def summary():
    print(f"ratio {RATIO:.1f}:1, wheel free speed {WHEEL_FREE_FPS:.1f} ft/s")
    print(f"C1 {C1:.1f} mm ({BELT1_T}T belt), C2 {C2:.1f} mm ({BELT2_T}T belt)")
    for f in (True, False):
        print(("front" if f else "rear "), "compound", [round(v, 1) for v in compound_xz(f)],
              "falcon", [round(v, 1) for v in falcon_xz(f)])
    print("y bands: outer", OUTER_RAIL_Y, "wheel", WHEEL_Y, "P2", P2_Y, "P1", P1_Y,
          "plate", DRIVE_PLATE_Y, "inner", INNER_RAIL_Y)
    print(f"interior between inner rails {2 * INNER_RAIL_Y[0]:.1f} mm, frame x +/-{FRAME_X:.1f}")
    w = 2 * (OUTER_RAIL_Y[1] + BUMP_DEPTH)
    l = 2 * (FRAME_X + BUMP_DEPTH)
    print(f"overall over bumpers {l / IN:.2f} x {w / IN:.2f} in")


if __name__ == "__main__":
    summary()

# ------------------------------------------------------------------ elevation drive / towers (added)
ELEV_PULLEY_Y = (232.0, 245.0)              # |y| layer of the 56T pulley, between chamber caps and bearing block
TOWER_XS = (PIVOT[0] - 19.0 - IN, PIVOT[0] - 19.0)   # 1x1 tower just ahead of the pivot bearings
BEARING_BLOCK_Y = (246.0, OUTER_RAIL_Y[1] - 2.0)   # printed block on the tower's back face (liner clear)
SERVO_PINIONS = [(-42.0, 412.0), (100.0, 412.0)]   # x, z of the two STS3215 16T pinions (575 mm loop = 115T)
TANK_D, TANK_L = 152.0, 360.0               # owner's AliExpress 6 L / 1.6 gal 200 psi tank (bare shell)
COMP_SPOT = ((-178.0, -50.0), (95.0, 276.0), (330.0, 573.0))  # ZHSYMX standing in the left turret half,
                                                             # behind the pivot (the middle chamber turns in front)
