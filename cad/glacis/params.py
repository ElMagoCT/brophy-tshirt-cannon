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
MEM_W, MEM_H = 26.0, 24.0                   # printed member: width on each panel, depth inward
REBATE_W = 14.0                             # panel edge overlaps the member by this much
CLIP_T = 2.5                                # printed corner clips sit flush, panel sits CLIP_T below the face
REBATE_D = CLIP_T + ACRYLIC_T + 0.3
CLIP_R = 10.0
NODE_SETBACK = 48.0
PRINT_MAX = 240.0
TENON = (6.5, 6.5, 12.0, 0.5)
TENON_CLEAR = 0.15
LED_CH = (10.8, 4.2, 2.0)                   # LED channel under the panel overlap: width, depth, outer shoulder
LED_LIP = 1.2                               # lip on the window side that keeps the strip in its channel
CORE_DEPTH = 15.0                           # tenons sit this deep, below the LED channel

Y_S = OUTER_RAIL_Y[1] + MEM_H               # side wall outer face at its bottom edge
TUMBLE = 8.0                                # side walls lean in this much
Z_WALL_BOT = BUMP_Z[1] + 1.5
Z_TOP = 630.0                               # flat deck
FRONT_ANGLE = 60.0                          # one front slant, from horizontal
REAR_ANGLE = 80.0                           # the back leans in too
X_TOP_FRONT = FRAME_X - (Z_TOP - Z_WALL_BOT) / math.tan(math.radians(FRONT_ANGLE))
X_TOP_REAR = -FRAME_X + (Z_TOP - Z_WALL_BOT) / math.tan(math.radians(REAR_ANGLE))
SIDE_OUTLINE = [
    (FRAME_X, Z_WALL_BOT),                  # nose, on the bumper
    (X_TOP_FRONT, Z_TOP),                   # front slant top
    (X_TOP_REAR, Z_TOP),                    # flat deck
    (-FRAME_X, Z_WALL_BOT),                 # back slant
]
SIDE_SPLIT_X = -150.0                       # both side walls split here: the rear panels are the battery doors


def wall_y(z, inner=False):
    """Outer face of the side wall at height z (inner face of the frame with inner=True)."""
    y = Y_S - (z - Z_WALL_BOT) * math.tan(math.radians(TUMBLE))
    return y - MEM_H / math.cos(math.radians(TUMBLE)) if inner else y


def rear_x(z, inner=False):
    x = -FRAME_X + (z - Z_WALL_BOT) / math.tan(math.radians(REAR_ANGLE))
    return x + MEM_H / math.sin(math.radians(REAR_ANGLE)) if inner else x


def front_x(z, inner=False):
    x = FRAME_X - (z - Z_WALL_BOT) / math.tan(math.radians(FRONT_ANGLE))
    return x - MEM_H / math.sin(math.radians(FRONT_ANGLE)) if inner else x


# ------------------------------------------------------------------ gun (rev C): two in-line cannons
# Each cannon: chamber tank -> 1 in stainless solenoid valve -> polycarbonate barrel, all on one axis.
# The two cannons stack; the pivot axle passes between them, at the gun's centre of mass.
BARREL_OD, BARREL_WALL, BARREL_LEN = 3.0 * IN, 0.125 * IN, 22.5 * IN   # clear polycarbonate tube
N_BARRELS = 2
VALVE = dict(L=82.6, W=66.0, BODY=(-28.0, 30.0), COIL_R=25.0, COIL_TOP=86.0)  # Atlantic Valves SZW-25 (1 in NPT)
CH_D, CH_L = 6.0 * IN, 11.0 * IN            # chamber: 1 gal 200 psi ASME steel tank, 1 in NPT end port
CH_BOSS = 15.0                              # end-port boss on the front dome
GUN_GAP = 12.0                              # between the two chamber tanks
PITCH = CH_D + GUN_GAP                      # cannons at z = +/- PITCH / 2 about the axle
X_VALVE = 67.0                              # valve centre ahead of the axle (from the balance calc, see gun.py)
CH_FIT_X = (-110.0, -170.0, -230.0)         # tank fittings along the top (bottom) of each tank, axle-relative:
                                            # fill push-to-connect, 125 psi relief, transducer
ELEV_RANGE = (0.0, 90.0)
ELEV_SHOW = 20.0
ELEV_T = (16, 56)                           # goBILDA pinion -> pulley on the right axle end (HTD 5M 9 mm)
ELEV_BELT_T = 100
ELEV_PULLEY_Y = (95.0, 108.0)               # |y| of the elevation pulley, just outside the gun
Y_GUN = CH_D / 2 + 3.5 + PLATE_T            # half width of the gun over its cradle plates

PIVOT = (-40.0, 572.0)                      # axle between the cannons; high enough that the gun's swing
                                            # clears the Falcons' inboard ends
Y_SLOT = 112.0                              # gun well half width (the elevation pulley turns inside it)
X_SLOT_REAR = -2000.0                       # the well is open at the back: at 0 deg the chambers reach the rear face

# towers: 1x1 on the inner rails behind the pivot (clear of the rear Falcons); a printed bearing block
# runs forward from each to the axle
TOWER_X = (-182.7, -157.3)
TOWER_L_X = TOWER_R_X = TOWER_X
BEARING_BLOCK_Y = (ELEV_PULLEY_Y[1] + 1.0, INNER_RAIL_Y[1])
ELEV_MOTOR_Z = 490.0
ELEV_C = centre_for_belt(ELEV_BELT_T, pd(ELEV_T[0]), pd(ELEV_T[1]))
ELEV_MOTOR_X = PIVOT[0] + math.sqrt(ELEV_C ** 2 - (PIVOT[1] - ELEV_MOTOR_Z) ** 2)

# ------------------------------------------------------------------ pneumatics / power
TANK_D, TANK_L = 152.0, 360.0               # owner's AliExpress 6 L / 1.6 gal 200 psi tank (bare shell)
TANK_SIDE = (66.0, 169.0, 364.0)            # (x, |y|, z): reservoirs lying along x, left and right, above the
                                            # front wheels
BATT = (7.13 * IN, 3.01 * IN, 6.57 * IN)    # FRC battery L, W, H
BELLY_Z = RAIL_Z[0]
BATT_Z = 287.8                              # battery bottoms on their sleds (over the rear wheels)
BATT_X = (-336.0, -336.0 + BATT[0])         # one battery each side, long axis along x
BATT_Y = (160.0, 160.0 + BATT[1])           # |y|: they slide out the side walls
ELEC_BAY = ((-380.0, -192.0), (-125.0, 125.0), (BELLY_Z, 250.0))   # back bottom
FOG_BOX = ((200.0, 360.0), (-60.0, 60.0), (BELLY_Z + 6.0, BELLY_Z + 136.0))   # 12 V automotive smoke machine, front bay (placeholder box)


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
