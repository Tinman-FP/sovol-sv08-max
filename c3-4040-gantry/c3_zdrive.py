"""C3 Z upgrade: 12 mm Gates 2MGT Z belts and StepperOnline 17HM19-2004S1 motors on the stock SV08 Max Z drive.

Stock drive per corner (front right, Sovol kit "z 1"; the other three mirror it about X 0 and Y 273.5):
* 40 mm NEMA 17 lying along +Y under the base, 12T pulley, 6 mm GT2 186 mm loop, about 80T reduction pulley.
* Stepped cross shaft: 5 mm at two 625ZZ, 6 mm under the pulleys, a 7 mm collar between them.
* 20T hubless drive pulley, grub screw through the teeth.
* 9 mm belt up the tower to a spring-tensioned 20T idler.
* The belt is clamped on the Z carriage ("ab 2" seat + pressure plate). The carriage carries the gantry arm.

12 mm changes (this module):
* Printed Z carriage plate with the same block and arm interfaces, a 12 mm free-run window and a toothed clamp channel for both belt ends, plus a cover plate.
* Printed tensioner block: Sovol's block with the idler gap widened for a 12 mm 20T idler; the stock shaft and seat stay.
* Bottom pulley: only 12.8 mm is free between the shaft collar (Y 598.4) and the bottom bracket's front wall (Y 611.2). A 12 mm pulley must be hubless and flangeless, 20T, 6 mm bore, <= 12.6 mm long, with a grub screw through the teeth. That is not a catalogue part: custom or modified.
* Printed tensioner seat: Sovol's seat with 13 mm slots for both belt runs. Sovol's model shows no belt slots, so the real slots may only be 9-10 mm.
* Optional MR105ZZ end support for the 24 mm motor shaft. It is a printed bridge on two of the motor's own M3 screws (longer screws), in front of the 12T pulley.

Run c3_zcheck.py for clearance and c3_zrelease.py for files. Frame and conventions as c3_params (stock gantry pose).
"""
import FreeCAD as App, Part
V = App.Vector

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def cyly(r, y0, y1, x, z):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))
def cylx(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))
def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()

# ---------------------------------------------------------------- front-right corner (kit z 1) geometry
Y_MIRROR = 273.5                     # the rear corners mirror the front ones about this plane
BELT_YC, BELT_W = 604.55, 12.0       # 12 mm belt centred where Sovol's 9 mm belt was
BY0, BY1 = BELT_YC - BELT_W / 2, BELT_YC + BELT_W / 2
X_AX = -320.5                        # cross shaft and top idler axes
R_P = 20 * 2.0 / (2 * 3.141592653589793)
X_FREE, X_CLAMP = X_AX - R_P, X_AX + R_P   # free run (outer) and clamped run (inner) pitch lines
Z_BOT, Z_TOP = -120.7, 571.8         # bottom pulley and top idler axes
CZ0, CZ1 = 153.0, 193.0              # Z carriage height range at the stock pose
MOTOR_AX = (-279.2, -117.7)          # Z motor axis (X, Z); face at Y 576.7; bracket wall front face Y 580.2
MOTOR_FACE, BRACKET_FACE = 576.7, 582.0          # bracket wall material reaches Y 581.7 at the motor screws
SHAFT_17HM19 = 24.0                  # from the face; full D-cut
M3_CLR, M3_CB, M3_INS = 1.7, 3.0, 2.0

def carriage_plate():
    """Replaces Sovol's "ab 2" seat.
    * MGW9H block: 4x M3, counterbored from the front.
    * Gantry arm: 2x M3 heat-set inserts where the stock tapped holes were.
    * Free-run window for the 12 mm belt.
    * Clamp column: an open channel, teeth on the -X wall, for the upper and lower belt ends. Between them (Z 171-175) one M3 holds the cover plate.
    Prints as installed (Z up)."""
    blk = box(-350.5, -330.5, 595.5, 605.0, CZ0, CZ1)
    webs = [box(-330.6, -325.0, 595.5, 598.0, CZ0, CZ1), box(-330.3, -325.0, 611.0, 612.5, CZ0, CZ1)]   # rear web 0.2 mm off the MGW9H block
    col = box(-325.1, -313.35, 595.5, 612.5, CZ0, CZ1)
    s = fuse([blk] + webs + [col])
    holes = [box(-344.5, -316.5, 595.4, 596.5, CZ0 - 0.1, 165.5)]                  # the arm's rear face is at Y 596.5
    for x in (-348.0, -333.0):                                                     # MGW9H block, same pattern as the stock seat
        for z in (165.0, 181.0):
            holes += [cyly(M3_CLR, 595.4, 605.1, x, z), cyly(M3_CB, 595.4, 601.5, x, z)]
    for x in (-341.0, -321.0):                                                     # arm M3 x 20 into heat-set inserts
        holes.append(cyly(M3_INS, 596.4, 604.6, x, 157.5))   # deep enough for the M3 x 20 tips
    holes.append(box(X_FREE - 1.8, X_FREE + 1.7, BY0 - 0.55, BY1 + 0.45, CZ0 - 0.1, CZ1 + 0.1))   # free run window
    xa = X_CLAMP - 0.8                                                             # channel: belt teeth toward -X
    holes.append(box(xa, X_CLAMP + 0.85, BY0 - 0.3, BY1 + 0.3, CZ0 - 0.1, CZ1 + 0.1))
    z = CZ0 + 0.5
    while z < CZ1 - 1.0:                                                           # 2 mm pitch tooth pockets, both belt ends
        if not (170.5 < z < 175.0):
            holes.append(box(xa - 0.8, xa + 0.01, BY0 - 0.3, BY1 + 0.3, z, z + 1.1))
        z += 2.0
    holes.append(cylx(M3_INS, X_CLAMP - 7.0, xa + 0.01, BELT_YC, 173.0))          # insert for the cover plate screw
    for h in holes:
        s = s.cut(h)
    return s.removeSplitter()

def clamp_cover():
    """Closes the clamp channel and presses both belt ends into the teeth. One M3 x 10 between the belt ends; a tongue
    in the channel's gap stops it turning. Prints on its outer face."""
    xa = X_CLAMP + 0.85
    s = fuse([box(xa, xa + 3.85, 595.5, 612.5, CZ0, CZ1), box(X_CLAMP - 0.75, xa + 0.01, BY0 - 0.15, BY1 + 0.15, 171.3, 174.7)])
    s = s.cut(cylx(M3_CLR, X_CLAMP - 1.0, xa + 4.0, BELT_YC, 173.0)).cut(cylx(M3_CB, xa + 2.35, xa + 4.0, BELT_YC, 173.0))
    return s.removeSplitter()

def tensioner_block(stock_block_parts):
    """Sovol's top tensioner block (all its bodies fused) with the idler gap widened from 13.5 to 17.1 mm for a 12 mm
    20T idler; the stock 5 mm idler shaft, springs, screw and seat are reused."""
    s = fuse([p.copy() for p in stock_block_parts])
    s = s.cut(box(-329.2, -311.8, BELT_YC - 8.55, BELT_YC + 8.55, Z_TOP - 9.8, 580.6))
    if len(s.Solids) > 1:
        s = sorted(s.Solids, key=lambda so: -so.Volume)[0]
    return s.removeSplitter()

def tensioner_seat(stock_seat_parts):
    """Sovol's top tensioner seat (its bodies fused) with 13 mm slots for both 12 mm belt runs; it bolts to the tower as before."""
    s = fuse([p.copy() for p in stock_seat_parts])
    for xr in (X_FREE, X_CLAMP):
        s = s.cut(box(xr - 1.3, xr + 1.3, BELT_YC - 6.5, BELT_YC + 6.5, 540.0, 590.0))
    if len(s.Solids) > 1:
        s = sorted(s.Solids, key=lambda so: -so.Volume)[0]
    return s.removeSplitter()

def idler_12():
    """20T toothed idler for 12 mm belt (KB3D G2GT-I-20-12 class), envelope: flanges <= 16 mm OD (the seat walls are
    8.5 mm from the axis; Sovol's idler is 15 mm), <= 16.4 mm wide."""
    y0, y1 = BELT_YC - 8.2, BELT_YC + 8.2
    s = fuse([cyly(8.0, y0, y0 + 1.5, X_AX, Z_TOP), cyly(6.11, y0 + 1.5, y1 - 1.5, X_AX, Z_TOP), cyly(8.0, y1 - 1.5, y1, X_AX, Z_TOP)])
    return s.cut(cyly(2.5, y0 - 1, y1 + 1, X_AX, Z_TOP))

def bottom_pulley_12():
    """Hubless, flangeless 20T for 12 mm belt, 6 mm bore, 12.6 mm long (Y 598.5-611.1), M3 grub through the teeth."""
    return cyly(6.11, 598.5, 611.1, X_AX, Z_BOT).cut(cyly(3.0, 598.4, 611.2, X_AX, Z_BOT))

def motor_17hm19():
    x, z = MOTOR_AX
    body = box(x - 21.15, x + 21.15, MOTOR_FACE - 48.0, MOTOR_FACE, z - 21.15, z + 21.15)
    return fuse([body, cyly(11.0, MOTOR_FACE, MOTOR_FACE + 2.0, x, z), cyly(2.5, MOTOR_FACE, MOTOR_FACE + SHAFT_17HM19, x, z)])

def end_support():
    """Optional MR105ZZ (5 x 10 x 4) support for the 24 mm motor shaft. Two legs sit on the bracket over the motor's two
    +X screws, which become M3 x 30, and a bridge crosses in front of the 12T pulley with the bearing. Prints bridge face down."""
    x, z = MOTOR_AX
    legs = [(x + 15.5, z + 15.5), (x + 15.5, z - 15.5)]
    s = fuse([box(x - 8.0, x + 17.0, 596.4, 602.0, z - 17.0, z + 17.0)] + [cyly(3.6, BRACKET_FACE, 602.0, lx, lz) for lx, lz in legs])   # inside the bracket walls
    s = s.cut(cyly(5.05, 596.3, 600.6, x, z)).cut(cyly(3.0, 596.3, 602.1, x, z))
    for lx, lz in legs:
        s = s.cut(cyly(M3_CLR, BRACKET_FACE - 0.1, 602.1, lx, lz)).cut(cyly(M3_CB, 599.0, 602.1, lx, lz))
    return s.removeSplitter()

def bearing_mr105():
    x, z = MOTOR_AX
    return cyly(5.0, 596.5, 600.5, x, z).cut(cyly(2.5, 596.4, 600.6, x, z))

def belt_runs(carriage_dz=0.0):
    """12 mm belt as fixed straight runs (wraps sit inside the pulley and idler envelopes): the free run full height and
    the clamped run above and below the carriage at the given gantry offset."""
    t = 0.69
    free = box(X_FREE - t, X_FREE + t, BY0, BY1, Z_BOT, Z_TOP)
    up = box(X_CLAMP - t, X_CLAMP + t, BY0, BY1, CZ1 + carriage_dz, Z_TOP)
    lo = box(X_CLAMP - t, X_CLAMP + t, BY0, BY1, Z_BOT, CZ0 + carriage_dz)
    return free, Part.makeCompound([up, lo])

# ---------------------------------------------------------------- the four corners
CORNERS = {'fr': (False, False), 'fl': (True, False), 'rl': (True, True), 'rr': (False, True)}   # (mirror X, mirror Y)
def place(s, corner):
    mx, my = CORNERS[corner]
    t = s.copy()
    if mx:
        t = t.mirror(V(0, 0, 0), V(1, 0, 0))
    if my:
        t = t.mirror(V(0, Y_MIRROR, 0), V(0, 1, 0))
    return t

def zdrive_parts(stock_block_parts, stock_seat_parts, with_end_support=True):
    """All corners: (name, material, shape, group). Groups: 'zcarriage' moves with the gantry in Z; 'zfixed' does not;
    'zbelt' the belt runs at the stock pose."""
    base = [('z carriage plate', 'pps-cf', carriage_plate(), 'zcarriage'), ('z belt clamp cover', 'pps-cf', clamp_cover(), 'zcarriage'),
            ('z tensioner block 12mm', 'pps-cf', tensioner_block(stock_block_parts), 'zfixed'),
            ('z tensioner seat 12mm', 'pps-cf', tensioner_seat(stock_seat_parts), 'zfixed'),
            ('z idler 20t 12mm', 'purchased', idler_12(), 'zfixed'), ('z drive pulley 20t 12mm hubless', 'purchased', bottom_pulley_12(), 'zfixed'),
            ('z motor 17hm19-2004s1', 'purchased', motor_17hm19(), 'zfixed')]
    if with_end_support:
        base += [('z motor end support', 'pps-cf', end_support(), 'zfixed'), ('z bearing mr105zz', 'purchased', bearing_mr105(), 'zfixed')]
    free, clamped = belt_runs()
    base += [('z belt 12mm free run', 'purchased', free, 'zbelt'), ('z belt 12mm clamped run', 'purchased', clamped, 'zbelt')]
    out = []
    for c in CORNERS:
        for n, m, s, g in base:
            out.append((f'{n} {c}', m, place(s, c), g))
    return out
