"""C3 (AWD) layout parameters and CoreXY belt-path solver (pure Python, no FreeCAD).

Frame: Sovol's SV08 Max model in the stock gantry pose (Z-carriage arm tops at Z 165.2, bed top at Z -36.7).
Y toward the front door, Z up; seen from the front, +X is to the LEFT (x<0 is the printer's right side).
Motor B (Sovol's label) sits at the rear corner x<0 and drives the upper belt; motor A at x>0 drives the lower belt.
AWD: each belt has a second motor at the front corner of the same side (B2 at x<0, A2 at x>0) in place of C2's front
idler. All four are LDO 42STH48-2004MAH(S80) (0.9 deg, 2.0 A, 80 mm shaft), each with a 625ZZ above its pulley.
All dimensions in mm.
"""
import math

# ---------- stock interfaces ----------
Z_ARM = 165.2                       # Z-carriage arm top; two tapped M4 per corner
ARM_HOLES_X = (306.5, 334.0)
ARM_Y = {'rear': -43.5, 'front': 590.0}
ARM_BOX = {'rear': (-49.5, -33.5), 'front': (580.5, 596.5)}   # arm Y extent, X 300.5..344, Z 153.2..165.2
BED_TOP = -36.7
GANTRY_DROP = 163.5                 # gantry moves down this far for the first layer (nozzle 127.0 -> bed)
GANTRY_RISE = 336.3                 # up this far for 500 mm print height

# ---------- 4040 frame ----------
ZB = 157.0                          # beam centre height (X beam and side beams); nozzle 6 mm inside the Z-carriage reach
RAIL_Z = ZB + 10.0                  # X rail in the upper slot of the X beam front face
XB_HALF = 278.0                     # X beam 556
XR_HALF = 276.0                     # X rail MGN12 552
SIDE_X = (298.0, 338.0)             # side beams (|X|)
SIDE_Y = (-32.0, 529.0)             # 561 long: ends behind the front motor (the cradle ties it to the Z-carriage arm)
YR_X = (290.0, 298.0)               # Y rail on the side beam inner face, lower slot
YR_Z = ZB - 10.0
YR_Y = (-27.0, 528.0)               # MGN12 555 (the Y block reaches Y 527.0 at the docking pose)
YB_FACE = 285.0                     # MGN12H block mounting face (|X|)
REAR_BEAM_HALF = 241.0              # rear cross beam 482, between the motors
REAR_BEAM_Y = (-66.0, -26.0)

# ---------- belts (Gates 2MGT 12 mm) ----------
R_T = 20 * 2.0 / (2 * math.pi)      # 20T pitch radius 6.366
R_S = 7.5 + 0.45                    # 15 mm smooth backside idler, belt pitch line radius
BELT_W = 12.0; BELT_T = 1.38
L_LO = (ZB + 31.0, ZB + 43.0)       # lower belt, driven by motor A (x>0)
L_UP = (ZB + 48.0, ZB + 60.0)       # upper belt, driven by motor B (x<0)
LEVEL = {-1: L_UP, +1: L_LO}         # each side's own (driven) level
A_RUN = 308.0                       # joint-side Y runs |X|
P_RUN = A_RUN + 2 * R_T             # passing (outer) Y runs |X| 320.73
X_RUN_DY = 28.0                     # X runs at Y_XB + 28, above the MGN12H block
CLAMP_X = 26.0                      # belt ends at the carriage, |x| from the nozzle
TAIL = 22.0                         # clamp engagement + tail allowance per belt end
Y_FM = 553.0                        # front motor axes (AWD): body between the side beam end and the Z-carriage arm
FM_SLIDE = (-1.0, 3.0)              # front motor slider travel for belt tension (Y), mm
FACE_F = 170.0                      # front motor faces (bodies hang below; plate top 176 stays under the joints at docking)
BEARING_F = {-1: (226.0, 231.0),    # front 625ZZ: B2 (upper belt) above the joint carriers' top deck at the docking pose
             +1: (210.0, 215.0)}    # A2 (lower belt) 1.5 mm over its pulley hub, under the carriers' top deck
SHAFT = 80.0                        # LDO S80 shaft length from the mounting face
YM = -45.0                          # motor axes Y (625ZZ housings stay forward of the rear top frame)
XM = 263.0                          # motor axes |X| (bodies clear the Y rails and blocks)
X_I2 = 244.0                        # reverse (smooth) idlers |X|
MOTOR_FACE_Z = {-1: ZB + 22.0, +1: ZB + 20.0}   # both hang below; x<0 pulley hub up, x>0 pulley hub down
BEARING_Z = {-1: (ZB + 70.0, ZB + 75.0), +1: (ZB + 63.0, ZB + 68.0)}   # rear 625ZZ above each pulley (double shear)

# ---------- head / docking ----------
Y_XB_MIN = -1.85
Y_STOP_PAD = 1.25                   # rear Y stop pads on the rear-corner motor plates (sensorless homing): the joint plate lands 0.5 mm past Y_XB_MIN
Y_XB_DOCK = 504.3                   # dock fronts at Y 619, inside the frame face (Y 622)
NOZZLE_DY = 66.25                   # nozzle Y = Y_XB + 66.25
DOCK_X = (-89.0, -47.0, -5.0, 37.0, 79.0)


def left(t):
    return (-t[1], t[0])


def tangent(c1, r1, d1, c2, r2, d2):
    """Belt tangent from circle 1 to circle 2. d=+1: wheel on the belt's left (CCW wrap), -1: on the right.
    r=0 gives a point. Returns (p1, p2, unit direction)."""
    D = (c2[0] - c1[0], c2[1] - c1[1]); k = d2 * r2 - d1 * r1
    dd = D[0] ** 2 + D[1] ** 2; L = math.sqrt(dd - k * k)
    t = ((L * D[0] + k * D[1]) / dd, (L * D[1] - k * D[0]) / dd); n = left(t)
    p1 = (c1[0] - d1 * r1 * n[0], c1[1] - d1 * r1 * n[1]); p2 = (c2[0] - d2 * r2 * n[0], c2[1] - d2 * r2 * n[1])
    return p1, p2, t


def wrap(t_in, t_out, d):
    a = math.atan2(t_in[0] * t_out[1] - t_in[1] * t_out[0], t_in[0] * t_out[0] + t_in[1] * t_out[1])
    if d > 0:
        return a if a >= 0 else a + 2 * math.pi
    return -a if a <= 0 else 2 * math.pi - a


def solve(start, wheels, end):
    """start/end: points; wheels: list of (name, centre, radius, dir). Returns segments, arcs, total length."""
    nodes = [('start', start, 0.0, 1)] + list(wheels) + [('end', end, 0.0, 1)]
    segs = []
    for a, b in zip(nodes, nodes[1:]):
        p1, p2, t = tangent(a[1], a[2], a[3], b[1], b[2], b[3]); segs.append((a[0], b[0], p1, p2, t))
    arcs = []
    for i, w in enumerate(wheels):
        t_in = segs[i][4]; t_out = segs[i + 1][4]; ang = wrap(t_in, t_out, w[3])
        arcs.append((w[0], w[1], w[2], w[3], segs[i][3], segs[i + 1][2], ang))
    length = sum(math.dist(s[2], s[3]) for s in segs) + sum(a[2] * a[6] for a in arcs)
    return segs, arcs, length


def belt_paths(y_xb, xn):
    """Both belts at gantry pose (y_xb, nozzle x). 'B': upper belt, motor B at x<0. 'A': lower belt, motor A at x>0."""
    yx = y_xb + X_RUN_DY; R = R_T
    y1 = YM + 2 * R + 2 * R_S
    B = solve((xn - CLAMP_X, yx), [
        ('joint xn up', (-A_RUN + R, yx + R), R, -1),
        ('motor B2 pulley', (-A_RUN - R, Y_FM), R, +1),
        ('rear idler xn', (-P_RUN + R, y1), R, +1),
        ('reverse idler xn', (-X_I2, y1 - R - R_S), R_S, -1),
        ('motor B pulley', (-XM, YM), R, +1),
        ('turn idler xp', (A_RUN - R, YM), R, +1),
        ('joint xp up', (A_RUN - R, yx - R), R, +1)], (xn + CLAMP_X, yx))
    A = solve((xn + CLAMP_X, yx), [
        ('joint xp lo', (A_RUN - R, yx + R), R, +1),
        ('motor A2 pulley', (A_RUN + R, Y_FM), R, -1),
        ('rear idler xp', (P_RUN - R, y1), R, -1),
        ('reverse idler xp', (X_I2, y1 - R - R_S), R_S, +1),
        ('motor A pulley', (XM, YM), R, -1),
        ('turn idler xn', (-A_RUN + R, YM), R, -1),
        ('joint xn lo', (-A_RUN + R, yx - R), R, -1)], (xn - CLAMP_X, yx))
    return {'B': B, 'A': A}


if __name__ == '__main__':
    for y_xb, xn in ((Y_XB_MIN, -252), (270, 0), (Y_XB_DOCK, 252), (Y_XB_DOCK, -252)):
        P = belt_paths(y_xb, xn)
        for k, (segs, arcs, L) in P.items():
            print(f'Y_XB {y_xb:6.1f} Xn {xn:5.0f} belt {k}: pitch length {L:7.1f} + tails {2*TAIL:.0f} = {L+2*TAIL:7.1f}')
            if y_xb == 270:
                for a in arcs:
                    print(f'      {a[0]:16s} centre ({a[1][0]:7.2f},{a[1][1]:7.2f}) wrap {math.degrees(a[6]):6.1f} deg')
