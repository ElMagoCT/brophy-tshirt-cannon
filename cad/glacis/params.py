"""Glacis (Mark 5) layout, rev B (2026-11-02): every shared number lives here. Units: mm, degrees.

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


# ------------------------------------------------------------------ frame (1x2 / 1x1 x 1/16 aluminum box tube)
RAIL_W, RAIL_H = 1 * IN, 2 * IN             # 1x2 standing on edge
TUBE_WALL = 0.0625 * IN
PLATE_T = 0.125 * IN                        # gussets, drive plates, cradle plates
FW = 22.25 * IN                             # over the outer rails (27.7 in over the bumpers, door limit 28)

# ------------------------------------------------------------------ drive
WHEEL_R = 5 * IN                            # 10 in printed mecanum
AXLE_Z = WHEEL_R
WB = 20 * IN                                # wheelbase
AX_X = WB / 2
RAIL_Z = (AXLE_Z - RAIL_H / 2, AXLE_Z + RAIL_H / 2)   # rails centred on the axles (1/2 hex live axles)
GROUND_CLEAR = 3 * IN                       # bumper bottom; the bellypan sits at 3.9 in

N_ROLL, ROLL_L, ROLL_R0 = 14, 78.0, 15.0    # rollers per wheel, length, max radius (coverage +8%)
ROLL_BRG = (11.0, 5.0)                      # 685ZZ (5 x 11 x 5) in each roller end, M5 axle
ROLL_ANGLE = 45.0
LUG_OFF = ROLL_L / 2 + 4.0                  # roller axle-end point from the roller centre, along its axis
LUG_R, LUG_T = 6.5, 7.0                     # printed boss round each axle end
WPLATE_T = 0.125 * IN                       # aluminum side plates on the hub
C45 = math.cos(math.radians(ROLL_ANGLE))
A_LUG = LUG_OFF * C45                       # axial offset of the lug planes from the roller centre plane
# wheel-local axial stations (from the roller centre plane, + = outboard)
W_OUTER_PLATE = (A_LUG + 3.5, A_LUG + 3.5 + WPLATE_T)
W_LUG = (A_LUG - 3.5, A_LUG + 3.5)          # lug plate (inner one mirrored)
W_FLANGE = (-A_LUG - 3.5 - 4.0, -A_LUG - 3.5)          # printed outboard belt flange
W_PULLEY = (W_FLANGE[0] - 15.0, W_FLANGE[0])           # 15 mm HTD teeth, integrated in the hub
W_INNER_PLATE = (W_PULLEY[0] - WPLATE_T, W_PULLEY[0])  # aluminum plate = inboard belt flange
W_OUT = A_LUG + 2.47 + LUG_R * C45          # outermost point (lug bosses)

OUTER_RAIL_Y = (FW / 2 - RAIL_W, FW / 2)
YMID = OUTER_RAIL_Y[0] - 3.0 - W_OUT        # roller centre plane of the wheel (left side)
WHEEL_Y = (YMID + W_INNER_PLATE[0], YMID + W_OUT)
DRIVE_PLATE_Y = (WHEEL_Y[0] - 1.5 - PLATE_T, WHEEL_Y[0] - 1.5)
INNER_RAIL_Y = (DRIVE_PLATE_Y[0] - RAIL_W, DRIVE_PLATE_Y[0])

# one stage HTD 5M 15 mm: Falcon 12T -> 120T printed into the wheel hub (10:1)
T_PIN, T_WHEEL = 12, 120
BELT_T = 140
RATIO = T_WHEEL / T_PIN
C1 = centre_for_belt(BELT_T, pd(T_PIN), pd(T_WHEEL))
THETA1 = 30.0                               # Falcon sits up and inboard of the axle


def falcon_xz(front):
    s = 1 if front else -1
    return (s * (AX_X - C1 * math.cos(math.radians(THETA1))), AXLE_Z + C1 * math.sin(math.radians(THETA1)))


FALCON_D, FALCON_L = 60.0, 89.9
FALCON_FREE_RPM = 6380
WHEEL_FREE_FPS = FALCON_FREE_RPM / RATIO * math.pi * 10 / 60 / 12
FRAME_X = AX_X + WHEEL_R + 3.0 + RAIL_W     # outside face of the end rails

# ------------------------------------------------------------------ bumpers (FRC style)
NOODLE_D = 2.5 * IN
BUMP_BACK_T = 6.0
BUMP_DEPTH = BUMP_BACK_T + NOODLE_D
BUMP_Z = (GROUND_CLEAR, GROUND_CLEAR + 2 * NOODLE_D)

# ------------------------------------------------------------------ body (printed frame + recessed acrylic)
ACRYLIC_T = 0.125 * IN
PANEL_MAX = (18 * IN, 36 * IN)
MEM_W, MEM_H = 18.0, 22.0                   # printed member: width on each panel, depth inward
REBATE_W = 8.0                              # panel edge overlaps the member by this much
CLIP_T = 2.5                                # printed corner clips sit flush, panel sits CLIP_T below the face
REBATE_D = CLIP_T + ACRYLIC_T + 0.3
CLIP_R = 10.0
NODE_SETBACK = 48.0
PRINT_MAX = 240.0
TENON = (6.5, 6.5, 12.0, 0.5)
TENON_CLEAR = 0.15
LED_SLOT = (2.6, 10.6)                      # 10 mm strip on edge, right behind the panel at the window edge

Y_S = OUTER_RAIL_Y[1] + MEM_H               # side wall outer face at its bottom edge
TUMBLE = 6.0                                # side walls lean in this much
Z_WALL_BOT = BUMP_Z[1] + 1.5
Z_TOP = 580.0                               # flat deck (the bottom chamber clears it at 90 deg)
Y_SLOT = 85.0                               # gun slot half width (top and floor opening)

PIVOT = (-130.0, 450.0)                     # pivot = axis of the top barrel
Z_SLOT_FLOOR = 270.0
X_SLOT_REAR = -228.0
FRONT_ANGLE = 70.0                          # one front slant, from horizontal
X_TOP_FRONT = FRAME_X - (Z_TOP - Z_WALL_BOT) / math.tan(math.radians(FRONT_ANGLE))
SIDE_OUTLINE = [
    (FRAME_X, Z_WALL_BOT),                  # nose, on the bumper
    (X_TOP_FRONT, Z_TOP),                   # front slant top
    (-FRAME_X + 29.0, Z_TOP),               # flat deck
    (-FRAME_X, Z_TOP - 29.0),               # rear chamfer
    (-FRAME_X, Z_WALL_BOT),
]
SIDE_SPLIT_X = -160.0                       # right side wall: rear panel is the battery door


def wall_y(z, inner=False):
    """Outer face of the side wall at height z (inner face of the frame with inner=True)."""
    y = Y_S - (z - Z_WALL_BOT) * math.tan(math.radians(TUMBLE))
    return y - MEM_H / math.cos(math.radians(TUMBLE)) if inner else y


def front_x(z, inner=False):
    x = FRAME_X - (z - Z_WALL_BOT) / math.tan(math.radians(FRONT_ANGLE))
    return x - MEM_H / math.sin(math.radians(FRONT_ANGLE)) if inner else x


# ------------------------------------------------------------------ gun
BARREL_OD, BARREL_WALL, BARREL_LEN = 3.0 * IN, 0.125 * IN, 22.5 * IN   # clear polycarbonate tube
N_BARRELS = 2
PITCH = 95.0                                # top barrel on the pivot axis, bottom one PITCH below
QX = (0.0, 30.0)                            # QEV x per barrel: the bottom one sits 30 mm forward so the two
                                            # inlet blocks don't face each other (its barrel is 30 mm shorter)
ELEV_RANGE = (0.0, 90.0)
ELEV_SHOW = 20.0
ELEV_T = (16, 56)                           # goBILDA pinion -> pulley on the right stub (HTD 5M 9 mm)
ELEV_BELT_T = 145
ELEV_PULLEY_Y = (158.0, 171.0)              # |y| of the elevation pulley (outboard of the bearing block)

# towers: 1x1 on the inner rails; left one behind the pivot, right one ahead (clear of the chambers)
TOWER_L_X = (PIVOT[0] - 40.0 - 12.7, PIVOT[0] - 40.0 + 12.7)
TOWER_R_X = (PIVOT[0] + 85.0 - 12.7, PIVOT[0] + 85.0 + 12.7)
BEARING_BLOCK_Y = (INNER_RAIL_Y[0] + 0.5, INNER_RAIL_Y[1])
ELEV_MOTOR_Z = 225.0
ELEV_C = centre_for_belt(ELEV_BELT_T, pd(ELEV_T[0]), pd(ELEV_T[1]))
ELEV_MOTOR_X = PIVOT[0] + math.sqrt(ELEV_C ** 2 - (PIVOT[1] - ELEV_MOTOR_Z) ** 2)

# ------------------------------------------------------------------ pneumatics / power
TANK_D, TANK_L = 152.0, 360.0               # owner's AliExpress 6 L / 1.6 gal 200 psi tank (bare shell)
TANK_LEFT = (125.0, 178.0, 366.0)           # lying along x, front left, above the front-left wheel
TANK_REAR = (-307.0, 10.0, 107.6 + TANK_L / 2)   # standing, rear centre, on the bellypan
BATT = (7.13 * IN, 3.01 * IN, 6.57 * IN)    # FRC battery L, W, H
BELLY_Z = RAIL_Z[0]
BATT_Z = 287.8                              # battery bottoms on the sled (over the rear-right wheel)
BATT_X = (-385.0, -229.0)                   # two batteries side by side along x
BATT_Y = (-252.0, -252.0 + BATT[0])         # long side across, they slide out the right side
COMP_BOX = (243.0, 128.0, 181.0)            # ZHSYMX SQ420, spot only
COMP_SPOT = ((150.0, 331.0), (-121.5, 121.5), (BELLY_Z, BELLY_Z + 128.0))   # lying flat, front bay


def summary():
    print(f"ratio {RATIO:.1f}:1, wheel free speed {WHEEL_FREE_FPS:.1f} ft/s, C1 {C1:.1f} mm ({BELT_T}T)")
    print("falcon front", [round(v, 1) for v in falcon_xz(True)])
    print("y bands: outer", OUTER_RAIL_Y, "wheel", [round(v, 1) for v in WHEEL_Y], "plate",
          [round(v, 1) for v in DRIVE_PLATE_Y], "inner", [round(v, 1) for v in INNER_RAIL_Y], "ymid", round(YMID, 1))
    print(f"frame x +/-{FRAME_X:.1f}, top front x {X_TOP_FRONT:.1f}, deck {Z_TOP / IN:.1f} in")
    print(f"elevation C {ELEV_C:.1f}, motor at x {ELEV_MOTOR_X:.1f} z {ELEV_MOTOR_Z}")
    w = 2 * (OUTER_RAIL_Y[1] + BUMP_DEPTH)
    l = 2 * (FRAME_X + BUMP_DEPTH)
    print(f"overall over bumpers {l / IN:.2f} x {w / IN:.2f} in; wall at deck y {wall_y(Z_TOP):.1f}")


if __name__ == "__main__":
    summary()
