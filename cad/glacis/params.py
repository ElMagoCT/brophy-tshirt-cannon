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

# rev C wheel, vector style (after the TTB-0010 Micah sent): 10 big rollers, each on two 608 2RS and a
# fixed M8 threaded rod held in printed cups; hub in two PETG halves (the inboard one carries the 116T
# pulley) clamped between three flat 1/8 in aluminum plates by 8 x 1/4-20 through-bolts.
N_ROLL, ROLL_L, ROLL_R0 = 10, 104.0, 21.0   # rollers per wheel, length, max radius (coverage +6%)
ROLL_ANGLE = 45.0
C45 = math.cos(math.radians(ROLL_ANGLE))
ROLL_A = WHEEL_R - ROLL_R0                  # roller axis radius
ROLL_BRG = (22.0, 7.0)                      # 608 2RS (8 x 22 x 7)
BRG_IN = 8.0                                # bearing outer face this far inside the roller end
RECESS_R = 11.3                             # roller end recess the cup stub sits in
TREAD_T = (3.0, 1.8)                        # TPU tread: middle, ends
ROD_D = 8.0
CUP_R, CUP_IN, CUP_OUT = 10.5, 7.0, 6.0     # printed cup on each rod end: radius, stub depth inside the
                                            # roller end, length beyond it
HUB_R = WHEEL_R - 6.0                       # cups, face webs and the outboard plate stop 6 mm inside the tread
FACE_T = 6.0                                # printed face web on each hub half
HUB_BOLT_R, N_HUB_BOLT = 68.0, 8            # 1/4-20 x 5-1/2 through-bolts (6.6 mm holes; M6 x 130 fits too)
WPLATE_T = 0.125 * IN                       # aluminum plates


def _wheel_face():
    t = ROLL_L / 2
    rend = math.sqrt(WHEEL_R ** 2 - (t * C45) ** 2) - ROLL_A
    return round(max(t * C45 + rend * C45, (t + CUP_OUT) * C45 + CUP_R * C45) + 0.5, 1)


# wheel-local axial stations (from the roller centre plane, + = outboard)
W_FACE = _wheel_face()                      # both hub faces
W_OUTER_PLATE = (W_FACE, W_FACE + WPLATE_T)
W_CENTRE_PLATE = (-WPLATE_T / 2, WPLATE_T / 2)
W_PULLEY = (-W_FACE - 16.0, -W_FACE)        # 15 mm belt on 16 mm of printed teeth; the face web is its flange
W_INNER_PLATE = (W_PULLEY[0] - WPLATE_T, W_PULLEY[0])  # aluminum inboard belt flange
W_OUT = W_OUTER_PLATE[1]                    # outermost point

OUTER_RAIL_Y = (FW / 2 - RAIL_W, FW / 2)
YMID = OUTER_RAIL_Y[0] - 3.0 - W_OUT        # roller centre plane of the wheel (left side)
WHEEL_Y = (YMID + W_INNER_PLATE[0], YMID + W_OUT)
DRIVE_PLATE_Y = (WHEEL_Y[0] - 1.5 - PLATE_T, WHEEL_Y[0] - 1.5)
INNER_RAIL_Y = (DRIVE_PLATE_Y[0] - RAIL_W, DRIVE_PLATE_Y[0])

# one stage HTD 5M 15 mm: Falcon 12T -> 116T printed into the wheel hub (9.67:1)
T_PIN, T_WHEEL = 12, 116
BELT_T = 140
RATIO = T_WHEEL / T_PIN
FLANGE_R = pd(T_WHEEL) / 2 + 2.5           # inboard flange, 1.27 in off the floor
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
FOAM_D, FOAM_H = 2.0 * IN, 5.0 * IN          # rev D.2: GoTo Foam 43 ILD strips, 2 in deep x 5 in tall (was 2 stacked 2.5 in noodles)
BUMP_BACK_T = 0.75 * IN                      # rev D.2 (Micah): a 1x6 ripped to 5 in. 1/2 in thicker than the old 1/4 ply, so
                                            # the foam is 2 in deep: still 27.75 in over the bumpers (door limit 28)
BUMP_DEPTH = BUMP_BACK_T + FOAM_D
BUMP_Z = (GROUND_CLEAR, GROUND_CLEAR + FOAM_H)

# ------------------------------------------------------------------ body (printed frame + recessed acrylic)
ACRYLIC_T = 0.125 * IN
PANEL_MAX = (18 * IN, 36 * IN)
MEM_W, MEM_H = 19.0, 24.0                   # printed member: width on each panel, depth inward
REBATE_W = 7.0                              # panel edge overlaps the member by this much (rev C.2 had 14); the outer
                                            # lip stays MEM_W - REBATE_W = 12
CLIP_T = 2.5                                # printed corner clips sit flush, panel sits CLIP_T below the face
GASKET_T = 0.7                              # extra rebate depth for 1/16 in closed-cell foam tape on the ledge, so the
                                            # clips clamp the panel instead of letting it rattle
REBATE_D = CLIP_T + ACRYLIC_T + 0.3 + GASKET_T
PANEL_GAP = 1.0                             # acrylic cut this much under the rebate outline per side (print tolerance)
CLIP_R, CLIP_OVER = 15.0, 6.0               # corner clip: round head radius, how far it laps over the acrylic
INSERT = (2.35, 6.5)                        # M4 x 6 heat-set insert (5 mm OD) hole: radius, depth; clips take M4 x 8
INSERT_SHORT = (2.35, 4.6)                  # M4 x 4 insert, M4 x 6 screw: where two neighbours' clip screws would meet
INSERT_1032 = (3.15, 10.5)                  # #10-32 x 3/8 in heat-set insert hole (6.3 mm drill): frame mounts
TNUT = 3.2                                  # #10-32 4-prong T-nut hole through the bumper plywood (driven from the
                                            # foam side; rev D.2: 3/4 in board, #10-32 x 1-1/4 in screws)
SIDE_MOUNT_X = (-280.0, -205.0, 100.0, 280.0)   # frame mount posts along each outer rail (clear of the x -105 seam
                                            # and of the x -153 frame joint's cross screw)
END_MOUNT_Y = (-170.0, 0.0, 170.0)          # ... and along each end rail (the outer two stand on the corner gussets)
FRONT_MOUNT_Y = (-205.0, 205.0)             # the front end's: the light bar hole (|y| < 175) leaves no frame over the
                                            # middle of the front rail, so two, just outboard of it
BUMP_SIDE_X = (-80.0, 0.0, 80.0)            # bumper screws through each outer rail, between the wheels, driven from
                                            # the open bay under the robot; the four backings are one ring, so the
                                            # ends need none (their rails are behind the wheels, the PDH and the bellypan)
BUMP_CORNER = (50.0, 12.0)                  # printed corner bracket joining the ring: leg length, thickness
MOUNT_TAB = (17.0, 14.0, 28.0)              # side mounts: tab on the frame's inner face over the rail (reach in, height,
                                            # length); the side wall's bottom member sits right on the bumper, so the
                                            # screw can't come up under it
BED = (250.0, 250.0, 250.0)                 # usable print volume, Elegoo Centauri Carbon 1 and 2 (256 cube less margin)
# corner and edge radii, one per kind (rev C.3.1: every corner radius is 2/3 of rev C.3's)
WINDOW_R = 15.0                             # frame window corners (convex and concave)
ACRYLIC_R = 18.7                            # acrylic panel corners, and the rebate they sit in (+0.3)
CLIP_ROUND = 4.0                            # corner clip and clip pocket outline corners
RAIL_EDGE_R = 2.5                           # the LED web's free back edge rounds over to its strip face
NODE_SETBACK = 48.0
PRINT_MAX = 240.0
TENON = (6.5, 6.5, 12.0, 0.5)
TENON_CLEAR = 0.3                           # per side, for a 0.6 mm nozzle (print a test joint first)
# panel light (rev D.1.2, Micah 2026-11-04): the window wall IS the LED surface. Below the acrylic's ledge it runs
# straight back, past the member as a thin web, and its last 10 mm (the strip) leans a little toward the panel on the
# straight runs. No rail, no flange, no step but the ledge the acrylic sits on.
LED_BAND = (10.0, 25.0, 22.5, 2.5)          # strip width (a 10 mm strip; ~8 is enough to stick to), strip centre this
                                            # far behind the acrylic's back face, lean toward the panel (deg) on the
                                            # straight runs, web thickness below the member
LED_STRIP_T = 1.6                           # 60/m strip thickness on the band
LED_SQUARE = 2.0                            # runs stay square this far from each corner (a strip can't bend round a
                                            # cone; the corner arc itself stays square). 0 made OCC build an invalid
                                            # window loft on the rear panel that took the whole frame with it
LED_TWIST = 15.0                            # then the lean ramps in over this (Micah 2026-11-10: lean 5 deg more, reach
                                            # it quicker at the corners, no flat spots; was 40 square + 40 ramp)
WINDOW_IN = dict(coplanar=MEM_W, open=MEM_W, notch=MEM_W, notch_top=MEM_W, slot=24.0, shared=MEM_W)
                                            # window edge (= LED surface) in from each panel edge, before the checks:
                                            # a shared edge then moves in until its web and strip stay on their own side
                                            # of the corner's bisector, so two neighbours' strips meet back to back in a
                                            # point there (Micah, 2026-11-04: "somewhere in between" 19 and 42), and any
                                            # edge whose strip would run into frame (a cheek, the bottom shell) moves in
                                            # a few mm at a time (body._settle_insets). Gun-well edges clear the pivots
LED_GAP = 1.0                               # gap between two neighbours' webs at the bisector
WINDOW_RING = 4.0                           # below the member the window cut is only this ring inside the LED line
                                            # (clears the strip and the corner fills' window side, nothing else)
WINDOW_IN_MAX = 46.0                        # cap on any window inset
LED_AB = CLIP_T + ACRYLIC_T                 # acrylic's back face, in from the outer face
LED_D0 = LED_AB + LED_BAND[1] - LED_BAND[0] / 2   # top and bottom of the strip, in from the outer face
LED_D1 = LED_D0 + LED_BAND[0]
LED_END = LED_D1 + 0.8                      # the web stops just past the strip
FRAME_STRIP = (5.0, 1.0)                    # 100/m strip in each frame tunnel: width, thickness
TUNNEL = (6.0, 2.6)                         # frame light: tunnel for a 5 mm strip (width, height), LEDs facing out
TUNNEL_GAP = 7.05                           # tunnel centre this far outward of the tenon centre (2.5 mm of wall)
FEED = (17.0, 38.0)                         # feed slot from the inside at each end of a tunnel, from the vertex
FRAME_BEND = (8.0, 12.0)                    # frame strip: easy-way bend radius into each feed slot, then this much
                                            # straight up the slot to where it's soldered to the next edge's strip
                                            # (clear of the corner-clip inserts)
TUNNEL_SKIN = 7.0                           # slots and tunnel ends stop this far under any outer face
CORE_DEPTH = 15.5                           # tenons sit this deep, inward of the light tunnel (inside a 19 mm member)

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
SIDE_SPLIT_X = -105.0                       # both side walls split here: the rear panels are the battery doors, wide
                                            # enough between their LED rails for a battery to slide out


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


LIGHT_BAR = (330.0, 30.0, 45.0, 285.0, 120.0)   # front light bar (Zmoon 12 in single row): length, height, depth, z of its
                                            # centre, |y| of its two end bolts
# Brophy Borealis (2026-11-10, Micah): the bar sits in a plain hole in the front slant, open at the bottom, from the
# body's bottom edge (on the bumper) to 4.5 in above the bumper. No liner: two 20x20 rails run across it behind the
# shell (one along its bottom, one along its top), the bar stands on the lower one on its own brackets, and the upper
# one is free for sensors and the like.
BAR_HOLE = dict(height=4.5 * IN, y=175.0, rail_len=372.0, bar_z=241.0, recess=4.0)
                                            # above the bumper's top; half width (the bar and its brackets inside);
                                            # rail length (into the frame members either side, short of the windows'
                                            # LED walls, which reach |y| 186.5 at the hole's top corners); the bar's bottom (above the fogger's top at 237.6); how far
                                            # its face sits behind the slant at its top edge
# 20x20 T-slot rails for add-ons (Micah's spares): one each side of the deck along the gun well, one inside each
# gun cradle plate, all mirrored about y = 0 and clear of the pivot
RAIL20 = 20.0
# Brophy Borealis (Micah, 2026-11-10): the deck rails moved inside the gun well, one piece each side, flush with the
# towers' and bearing blocks' outboard face (|y| 129.35) and 2 mm under the deck; the towers stop under them and the
# bearing blocks sit on them, so the pivot went up 11 mm. M4 x 30s across the rail's core (z 618, under the deck
# member's light tunnel at z 620-623) through the tower plate into inserts in the member's inner face
DECK_RAIL = dict(y=(INNER_RAIL_Y[1] - 20.0, INNER_RAIL_Y[1]), x=(-320.0, 150.0), z=(608.0, 628.0), screw_z=618.0,
                 screws_x=(-290.0, -170.0, -95.0, 40.0, 125.0))




# ------------------------------------------------------------------ speakers (rev C.2)
SPEAKER = (144.8, 139.7, 58.4)              # Xprite 200 W siren speaker (B01DMSR4L4): width, height (with its L foot), depth; 5.7 x 5.5 x 2.3 in from its drawing
SPK_CLEAR, SPK_WALL, SPK_GRILLE = 4.0, 4.0, 4.0   # pocket clearance round it, printed cup wall, grille thickness
SPEAKERS = [  # (tag, end of the front-side corner edge, distance along it, aim out from straight, aim up, seat depth,
              #  slid inboard). A bottom pair (22.5 out, 15 up) doesn't fit: see JUDGMENTS
    ("top", "top", 90.0, 45.0, 30.0, 75.4, 0.0),        # sunk 13 mm deeper in rev C.3, 7.4 more for the Xprite (face unmoved)
]


# ------------------------------------------------------------------ gun (rev C): two in-line cannons
# Each cannon: pipe chamber -> 1 in stainless solenoid valve -> polycarbonate barrel, all on one axis.
# The two cannons stack as close as the barrels allow; the pivot axis runs between them, at the gun's centre of
# mass, on two hex stubs (one per cradle plate) so nothing has to pass between the cannons.
BARREL_OD, BARREL_WALL, BARREL_LEN = 3.0 * IN, 0.125 * IN, 36.0 * IN   # clear polycarbonate tube (rev D: one per 4 ft stick)
N_BARRELS = 2
VALVE = dict(L=82.6, W=66.0, BODY=(-28.0, 30.0), COIL_R=25.0, COIL_TOP=86.0)  # Atlantic Valves SZW-25 (1 in NPT)
HSV04 = dict(L=131.1, W=64.3, BODY=(-27.0, 27.0), COIL_R=24.0, COIL_TOP=75.4)  # U.S. Solid USS-HSV04, 5.16 x 2.53 x 4.03 in
VALVES = (HSV04, HSV04)                     # (top, bottom) firing valves (rev D.2: both HSV04, both to full tank pressure)
# chamber: 2 in Sch 40 x 8 in nipple between two 2 x 1 black malleable reducing couplings (about 0.53 L; a longer
# nipple swings the chamber low enough at the back to open the rear face down through its controls)
CH_PIPE = "3"                               # rev D.1: 3 in Sch 40
# Brophy Borealis (Micah, 2026-11-10): welded chambers. Plain-end pipe between two 3/8 in A36 discs (3.5 in OD, flush
# with the pipe), the valve on half of a 1 x 4 in nipple welded through the front disc, a 1/4 NPT weld bung 1 in
# behind the front disc for the fill line. Top 12.9 in (1.56 L), bottom 10.9 in (1.32 L)
CH_PIPE_L = (12.9 * IN, 10.9 * IN)
CH_DISC_T = 0.375 * IN
CH_TOE_L = 2.0 * IN                         # half of the 1 x 4 in nipple: threaded end into the valve
CH_BUNG_X, CH_BUNG_H = 1.0 * IN, 16.0       # bung centre behind the front disc; its height off the pipe
SMOKE_R = 0.3125 * IN                       # the gun's smoke line: 1/2 in ID x 5/8 in OD silicone (was 3/8 x 1/2)
RED = dict(L=80.8, OD_IN=44.0, OD_OUT=108.7, BAND_IN=16.0, BAND_OUT=28.0, MASS=0.9)   # 3 x 1 malleable reducing coupling
GUN_GAP = 35.8 * 0.70                       # between the barrels (Micah 2026-11-10: "30% closer"; was 35.8 for the old 3 x 1
                                            # couplings side by side, gone since the chambers are welded): 101 mm axes,
                                            # the 3 in chambers 12 mm apart
PITCH = BARREL_OD + GUN_GAP                 # cannons at z = +/- PITCH / 2 about the axis
CRADLE_Y0 = 74.0                            # inner faces of the two cradle plates: the 109 mm couplings plus the fill
                                            # and smoke lines that run beside them
X_VALVE = 190.0                             # valve front faces ahead of the axis (from the balance calc, see gun.py)
CH_SADDLE_S = (233.0, 352.0)                # chamber saddles, distance behind the valve front faces (both pipes there)
ELEV_RANGE = (0.0, 90.0)                    # Brophy Borealis (Micah, 2026-11-10): at least 0-85 deg, 90 if it fits.
                                            # The pass-2 build clears to 95 deg (sweep90 check, B14), so 0-90.
ELEV_SHOW = 20.0
ELEV_T = (16, 112)                          # goBILDA 312 rpm pinion -> pulley on the right axle end (HTD 5M 9 mm), 7:1
ELEV_BELT_T = 150
ELEV_STANDOFF = 10.0                        # Micah 2026-11-10: the gun pulley is a ring on standoffs off the right cradle
                                            # plate, the belt centred between the plate and the bearing block
ELEV_PULLEY_Y = (CRADLE_Y0 + PLATE_T + ELEV_STANDOFF, CRADLE_Y0 + PLATE_T + ELEV_STANDOFF + 13.0)   # |y| of both pulleys
ELEV_MOTOR_FACE_Y = 110.0                   # |y| of the elevation motor's face (unchanged; the pinion moved out on the shaft)
Y_GUN = CRADLE_Y0 + PLATE_T                 # half width of the gun over its cradle plates

PIVOT = (-40.0, 656.0)                      # axle between the cannons; high enough that the gun's swing
                                            # clears the Falcons' inboard ends (Borealis: 645 -> 656, the
                                            # bearing blocks now sit on the in-well rails at z 628)
Y_SLOT = 133.0                              # gun well half width (the elevation pulley turns inside it)
X_SLOT_REAR = -2000.0                       # the well is open at the back: at 0 deg the chambers reach the rear face

# towers: 1x1 on the inner rails behind the pivot (clear of the rear Falcons); a printed bearing block
# runs forward from each to the axle
TOWER_X = (-182.7, -157.3)
TOWER_L_X = TOWER_R_X = TOWER_X
BEARING_BLOCK_Y = (109.0, INNER_RAIL_Y[1])     # inner bearing face (was the old pulley's outer face + 1)
ELEV_MOTOR_Z = 468.0                        # under the top speaker's LED rail, over the side tank
ELEV_C = centre_for_belt(ELEV_BELT_T, pd(ELEV_T[0]), pd(ELEV_T[1]))
ELEV_MOTOR_X = PIVOT[0] + math.sqrt(ELEV_C ** 2 - (PIVOT[1] - ELEV_MOTOR_Z) ** 2)

# ------------------------------------------------------------------ pneumatics / power
TANK_D, TANK_L = 152.0, 360.0               # owner's AliExpress 6 L / 1.6 gal 200 psi tank (bare shell)
TANK_SIDE = (46.0, 163.0, 364.0)            # (x, |y|, z): reservoirs lying along x, left and right, above the
                                            # front wheels
BATT = (7.13 * IN, 3.01 * IN, 6.57 * IN)    # FRC battery L, W, H
BELLY_Z = RAIL_Z[0]
BATT_Z = 287.8                              # battery bottoms on their sleds (over the rear wheels)
BATT_X = (-319.0, -319.0 + BATT[0])         # one battery each side, long axis along x, inside its door's rails
BATT_Y = (145.0, 145.0 + BATT[1])           # |y|: they slide out the side walls
ELEC_BAY = ((-380.0, -192.0), (-100.0, 100.0), (BELLY_Z, 250.0))   # back bottom
FOG_BOX = ((190.0, 350.0), (-60.0, 60.0), (BELLY_Z + 6.0, BELLY_Z + 136.0))   # custom 12 V fogger (2 x 200 W cores), front bay
FOG_VENTS = ((368.0, 80.0), (-140.0, 0.0))  # smoke trails (x, y), both down through the bellypan: front under the bumper,
                                            # rear just ahead of the electronics bay


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
