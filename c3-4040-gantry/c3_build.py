"""C3 (AWD): clean 4040 CoreXY gantry for the SV08 Max with the Bondtech INDX (5 tools), Beacon Rev H and 12 mm Gates belts.

Layout (see c3_params.py for every number):
  * 4040 side beams and X beam at the same height; MGN12 Y rails on the side beams' inner faces; 4040 rear cross beam.
  * Printed XY joints: one L-shaped part per side, bolted to the Y block and clamping the X beam end; the two X-turn
    pulleys sit above the side beam so the carriage reaches the full bed width.
  * Belts: both 12 mm levels run above the beams (X runs just above the MGN12H block).
  * AWD: four LDO 42STH48-2004MAH(S80), two per belt. Rear motors hang below the rear corners (180 deg wrap with a
    reverse idler); front motors hang below the front corners in place of C2's front idlers, on sliders that tension
    the belts from the front. Every motor has a 625ZZ above its pulley (double shear) and a cover over the long shaft.
  * Front corners: a cradle ties the (shortened) side beam to the Z-carriage arm around the motor; the base on the arm
    carries the 15x15 dock rail bracket.
  * Printed X carriage: INDX Smart Head bolt pattern, MGN12H 20x20, integral toothed belt clamps, Beacon tongue.
  * Five Bondtech 1515 docks on the dock rail, inside the frame front face.
Run with FreeCAD's Python:  /Applications/FreeCAD.app/Contents/Resources/bin/python c3_build.py
"""
import sys, os, math, json, re
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, Import, Mesh, MeshPart
from pathlib import Path
V = App.Vector
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from c3_params import *
import c3_purge as PG                                 # purge/wipe stations, station bar, purge trays
import c3_routing as RT                               # cable chains, harness, rear mast, piano-wire arcs (2026-11-01)

INP = HERE / 'inputs'; OUT = HERE / 'c3'; OUT.mkdir(exist_ok=True)
STOCK_CACHE = Path(os.environ.get('C2_STOCK_CACHE', str(OUT / '_cache')))
POSE = dict(y_xb=float(os.environ.get('C2_Y_XB', 270.0)), xn=float(os.environ.get('C2_XN', -5.0)))
EXPORT = os.environ.get('C2_EXPORT', '1') == '1'

# ---------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def rbox(x0, x1, y0, y1, z0, z1, r=2.0):
    """Box with its vertical edges rounded."""
    b = box(x0, x1, y0, y1, z0, z1)
    try:
        return b.makeFillet(r, [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6])
    except Exception:
        return b
def cyl(r, z0, z1, x, y):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))
def cylx(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))
def cyly(r, y0, y1, x, z):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))
def mir(s):
    return s.mirror(V(0, 0, 0), V(1, 0, 0))
def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()
def cut(s, tools):
    for t in tools:
        s = s.cut(t)
    return s

M3_CLR, M4_CLR, M5_CLR = 1.7, 2.25, 2.75            # clearance radii
M3_CB, M4_CB, M5_CB = 3.0, 4.0, 5.0                  # counterbore radii
M3_INSERT, M5_NUT = 2.0, 4.6                         # heat-set insert pocket radius, M5 nut circumradius

parts = []                                            # (name, material, shape, group)
def add(name, mat, shape, group):
    parts.append((name, mat, shape, group))

# ---------------------------------------------------------------- purchased: 4040, rails, blocks
def profile4040(length, axis, start, yc, zc):
    """4040 slot 8 (Misumi HFS8-4040 class): 8 mm slots 4.5 deep at +-10 on each face, 6.8 centre bore."""
    s = Part.makeBox(length, 40, 40, V(0, -20, -20))
    for c in (-10, 10):
        for dy, dz, w, h in ((c - 4, 20 - 4.5, 8, 4.5), (c - 4, -20, 8, 4.5), (20 - 4.5, c - 4, 4.5, 8), (-20, c - 4, 4.5, 8)):
            s = s.cut(Part.makeBox(length, w, h, V(0, dy, dz)))
    s = s.cut(Part.makeCylinder(3.4, length, V(0, 0, 0), V(1, 0, 0)))
    if axis == 'y':
        s.rotate(V(0, 0, 0), V(0, 0, 1), 90)
        s.translate(V(yc, start, zc))
    else:
        s.translate(V(start, yc, zc))
    return s

SIDE_XC = (SIDE_X[0] + SIDE_X[1]) / 2
for s_ in (-1, 1):
    add(f'side beam 4040 {"xn" if s_<0 else "xp"} {SIDE_Y[1]-SIDE_Y[0]:.1f}', 'al-6063 4040', profile4040(SIDE_Y[1] - SIDE_Y[0], 'y', SIDE_Y[0], s_ * SIDE_XC, ZB), 'frame')
    x0, x1 = sorted((s_ * YR_X[0], s_ * YR_X[1]))
    add(f'y rail mgn12 {"xn" if s_<0 else "xp"} {YR_Y[1]-YR_Y[0]:.0f}', 'steel', box(x0, x1, YR_Y[0], YR_Y[1], YR_Z - 6, YR_Z + 6), 'frame')
add(f'rear beam 4040 {2*REAR_BEAM_HALF:.0f}', 'al-6063 4040', profile4040(2 * REAR_BEAM_HALF, 'x', -REAR_BEAM_HALF, sum(REAR_BEAM_Y) / 2, ZB), 'frame')

def bridge_parts(y_xb):
    """Everything that moves with the X beam in Y."""
    out = []
    out.append((f'x beam 4040 {2*XB_HALF:.0f}', 'al-6063 4040', profile4040(2 * XB_HALF, 'x', -XB_HALF, y_xb, ZB)))
    F = y_xb + 20.0
    out.append((f'x rail mgn12 {2*XR_HALF:.0f}', 'steel', box(-XR_HALF, XR_HALF, F, F + 8, RAIL_Z - 6, RAIL_Z + 6)))
    for s_ in (-1, 1):
        x0, x1 = sorted((s_ * (YR_X[0] - 3.0), s_ * YB_FACE))
        out.append((f'y block mgn12h {"xn" if s_<0 else "xp"}', 'steel', box(x0, x1, y_xb - 22.7, y_xb + 22.7, YR_Z - 13.5, YR_Z + 13.5)))
    return out

# ---------------------------------------------------------------- purchased: pulleys, idlers, bearings, motors
def toothed_idler(x, y, level):
    z0 = level[0] - 2.0
    return fuse([cyl(7.5, z0, z0 + 1.5, x, y), cyl(6.11, z0 + 1.5, z0 + 14.5, x, y), cyl(7.5, z0 + 14.5, z0 + 16, x, y)]).cut(cyl(2.5, z0, z0 + 16, x, y))
def smooth_idler(x, y, level):
    z0 = (level[0] + level[1]) / 2 - 9.0
    return fuse([cyl(9.5, z0, z0 + 1, x, y), cyl(7.5, z0 + 1, z0 + 17, x, y), cyl(9.5, z0 + 17, z0 + 18, x, y)]).cut(cyl(2.5, z0, z0 + 18, x, y))
def drive_pulley(x, y, level, hub_up):
    t0, t1 = level[0] - 0.5, level[1] + 0.5
    s = fuse([cyl(7.5, t0 - 1, t0, x, y), cyl(6.11, t0, t1, x, y), cyl(7.5, t1, t1 + 1, x, y),
              cyl(7.0, t1 + 1, t1 + 8, x, y) if hub_up else cyl(7.0, t0 - 8, t0 - 1, x, y)])
    return s.cut(cyl(2.5, t0 - 8, t1 + 8, x, y))
def bearing_625(x, y, z0):
    return cyl(8, z0, z0 + 5, x, y).cut(cyl(2.5, z0, z0 + 5, x, y))
def motor_42sth48(x, y, face):
    body = box(x - 21.15, x + 21.15, y - 21.15, y + 21.15, face - 48, face)
    body = body.makeChamfer(3.0, [e for e in body.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1])
    return fuse([body, cyl(11, face, face + 2, x, y), cyl(2.5, face, face + SHAFT, x, y)])

y1_rear = YM + 2 * R_T + 2 * R_S
FM_X = A_RUN + R_T                                   # front motor axes |X| (the C2 front idler position)
for s_ in (-1, 1):
    lvl = LEVEL[s_]; oth = LEVEL[-s_]; tag = 'xn' if s_ < 0 else 'xp'
    mot = 'B' if s_ < 0 else 'A'
    add(f'motor {mot} ldo 42sth48-2004mah s80 {tag}', 'purchased', motor_42sth48(s_ * XM, YM, MOTOR_FACE_Z[s_]), 'frame')
    add(f'drive pulley 2gt 20t 12mm {tag}', 'purchased', drive_pulley(s_ * XM, YM, lvl, hub_up=(s_ < 0)), 'frame')
    add(f'bearing 625zz double shear {tag}', 'purchased', bearing_625(s_ * XM, YM, BEARING_Z[s_][0]), 'frame')
    # AWD front motors (B2 at x<0 on the upper belt, A2 at x>0 on the lower belt) in place of the C2 front idlers
    add(f'motor {mot}2 ldo 42sth48-2004mah s80 front {tag}', 'purchased', motor_42sth48(s_ * FM_X, Y_FM, FACE_F), 'frame')
    add(f'drive pulley 2gt 20t 12mm front {tag}', 'purchased', drive_pulley(s_ * FM_X, Y_FM, lvl, hub_up=(s_ > 0)), 'frame')
    add(f'bearing 625zz double shear front {tag}', 'purchased', bearing_625(s_ * FM_X, Y_FM, BEARING_F[s_][0]), 'frame')
    add(f'idler toothed rear {tag}', 'purchased', toothed_idler(s_ * (P_RUN - R_T), y1_rear, lvl), 'frame')
    add(f'idler smooth reverse {tag}', 'purchased', smooth_idler(s_ * X_I2, y1_rear - R_T - R_S, lvl), 'frame')
    add(f'idler toothed turn {tag}', 'purchased', toothed_idler(s_ * (A_RUN - R_T), YM, oth), 'frame')

def joint_pulleys(y_xb):
    yx = y_xb + X_RUN_DY; out = []
    for s_ in (-1, 1):
        tag = 'xn' if s_ < 0 else 'xp'
        # the pulley that turns its belt forward sits at yx+R, the rearward one at yx-R (see c3_params.belt_paths)
        fwd, back = (L_UP, L_LO) if s_ < 0 else (L_LO, L_UP)
        out.append((f'idler toothed joint fwd {tag}', 'purchased', toothed_idler(s_ * (A_RUN - R_T), yx + R_T, fwd)))
        out.append((f'idler toothed joint back {tag}', 'purchased', toothed_idler(s_ * (A_RUN - R_T), yx - R_T, back)))
    return out

# ---------------------------------------------------------------- belts from the solver
def belt_solid(path, level):
    segs, arcs, L = path; z0 = level[0]; h = level[1] - level[0]; ht = BELT_T / 2; out = []
    for a, b, p1, p2, t in segs:
        ln = math.dist(p1, p2)
        if ln < 1e-6:
            continue
        s = Part.makeBox(ln, BELT_T, h, V(0, -ht, 0))
        s.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(math.atan2(t[1], t[0]))); s.translate(V(p1[0], p1[1], z0)); out.append(s)
    for name, c, r, d, p_in, p_out, ang in arcs:
        if ang < 1e-4:
            continue
        th0 = math.atan2((p_in if d > 0 else p_out)[1] - c[1], (p_in if d > 0 else p_out)[0] - c[0])
        s = Part.makeCylinder(r + ht, h, V(c[0], c[1], z0), V(0, 0, 1), math.degrees(ang)).cut(
            Part.makeCylinder(r - ht, h, V(c[0], c[1], z0), V(0, 0, 1), math.degrees(ang)))
        s.rotate(V(c[0], c[1], z0), V(0, 0, 1), math.degrees(th0)); out.append(s)
    return Part.makeCompound(out), L

# ---------------------------------------------------------------- Bondtech INDX (vendor STEP), proper rotation
_bt = App.newDocument('INDX'); Import.insert(str(INP / 'vendor_references/bondtech/INDX_simplified_1.19.step'), _bt.Name)
def bt_group(prefix):
    g = [o for o in _bt.Objects if o.Label.startswith(prefix)][0]; out = []
    def walk(o):
        for k in getattr(o, 'Group', []):
            if k.TypeId == 'Part::Feature':
                s = k.Shape.copy(); s.Placement = k.getGlobalPlacement(); out.append((k.Label, s))
            walk(k)
    walk(g); return out
BT_M = App.Matrix(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1)      # bt (x,y,z) -> printer (-x, z, y), det +1
def bt_to_printer(s, xn, y_xb):
    """Bondtech frame (x to the head's right, y up, z toward the docks) -> printer frame at nozzle X xn, X beam y_xb.
    Bondtech block top face z -33.7 lands on the block top (Y_XB+33); block centre y 8.5 on RAIL_Z."""
    s = s.transformGeometry(BT_M); s.translate(V(xn, y_xb + 66.7, RAIL_Z - 8.5)); return s
HEAD_SRC = []
for gp in ('INDX Toolhead', 'INDX Front cover left', 'INDX Front cover right', 'INDX Strain relief'):
    HEAD_SRC += bt_group(gp)
HEAD_SRC += [(o.Label, (lambda o: (lambda s: (setattr(s, 'Placement', o.getGlobalPlacement()), s)[1])(o.Shape.copy()))(o)) for o in _bt.Objects if o.Label.startswith('INDX PCB Cover')]
TOOL_HELD = bt_group('INDX Nozzle tool closed')
TOOL_PARKED = bt_group('INDX Nozzle tool open')
DOCK_SRC = bt_group('INDX Tool Dock 1515')

# ---------------------------------------------------------------- Beacon Rev H Normal (vendor STEP)
_bc = App.newDocument('BEACON')
Import.insert(str(INP / 'vendor_references/beacon/Beacon_RevH_Assm_Normal.STEP'), _bc.Name)
BEACON_SRC = []
for o in _bc.Objects:
    if o.TypeId == 'Part::Feature' and not o.Shape.isNull() and o.Shape.Volume > 1:
        s = o.Shape.copy(); s.Placement = o.getGlobalPlacement()
        for so in s.Solids:
            bb = so.BoundBox
            if (bb.ZMax > 15 and bb.ZMin > -1) or (bb.ZMax < -1.5 and bb.XMax < 9):   # vendor keep-out cone, recess marker
                continue
            BEACON_SRC.append(so)
_bbx = BEACON_SRC[0].BoundBox
for so in BEACON_SRC[1:]:
    _bbx.add(so.BoundBox)
BEACON_DY = 26.0                       # coil centre Y_XB + 26 (40 mm behind the nozzle); Beacon turned 90 deg
NOZZLE_Z = RAIL_Z - 8.5 - 31.5
BEACON_Z0 = NOZZLE_Z + 2.6 + 1.6108    # PCB top so the bed-facing PCB face sits 2.6 mm above the nozzle tip
def beacon_at(xn, y_xb):
    out = []
    for so in BEACON_SRC:
        t = so.copy(); t.rotate(V(0, 0, 0), V(0, 0, 1), 90); t.translate(V(xn, y_xb + BEACON_DY, BEACON_Z0)); out.append(t)
    return Part.makeCompound(out)

# ---------------------------------------------------------------- printed: X carriage (designed in the Bondtech frame)
def x_carriage_bt():
    """Plate on the MGN12H (same envelope and Smart Head pattern as Bondtech 02PRT00364), toothed 12 mm belt clamps
    for both levels on side wings, and a tongue below that carries the Beacon behind the head."""
    zb, zf = -33.7, -28.7                                          # plate back (block top face) and front (head face)
    plate = box(-24.0, 24.0, -13.0, 23.4, zb, zf)
    for bx, by in ((20.0, 25.0), (-20.0, 27.45)):                       # upper Smart Head bolt bosses between the PCB cover fingers
        plate = plate.fuse(Part.makeCylinder(3.6, zf - zb, V(bx, by, zb))).fuse(box(bx - 3.6, bx + 3.6, 20.0, by, zb, zf))
    lo = (L_LO[0] - (RAIL_Z - 8.5), L_LO[1] - (RAIL_Z - 8.5)); up = (L_UP[0] - (RAIL_Z - 8.5), L_UP[1] - (RAIL_Z - 8.5))
    zw0 = -45.0                                                    # wing back, 1.7 mm clear of the beam face plane
    zbelt = X_RUN_DY - 66.7                                        # belt pitch line in bt z
    wings = []
    for sx in (-1, 1):
        xa, xb = sorted((sx * 25.2, sx * 40.0))
        w = rbox(xa, xb, lo[0] - 3.0, up[1] + 3.0, zw0, zf, 1.5)
        yb0 = (RAIL_Z + 6.0 + 1.0) - (RAIL_Z - 8.5)                  # 1 mm above the X rail top
        brg = box(*sorted((sx * 23.2, sx * 40.0)), yb0, lo[0] - 1.0, zw0, zb).fuse(box(*sorted((sx * 22.0, sx * 40.0)), yb0, lo[0] - 1.0, zb, zf))
        gus = Part.makePolygon([V(sx * 24.0, yb0, 0), V(sx * 40.0, yb0, 0), V(sx * 24.0, yb0 - 16.0, 0), V(sx * 24.0, yb0, 0)])
        gus = Part.Face(gus).extrude(V(0, 0, zf - (X_RUN_DY + 1.0 - 66.7))); gus.translate(V(0, 0, X_RUN_DY + 1.0 - 66.7))   # 45 deg, clear of the X rail
        sh = Part.Face(Part.makePolygon([V(sx * 20.0, -13.0, 0), V(sx * 24.0, -13.0, 0), V(sx * 20.0, -17.0, 0), V(sx * 20.0, -13.0, 0)])).extrude(V(0, 0, zf + 44.7))
        sh.translate(V(0, 0, -44.7))
        wings += [w, brg, gus, sh]
    yb_ = BEACON_Z0 - (RAIL_Z - 8.5); zc = BEACON_DY - 66.7               # Beacon PCB top and coil, bt frame
    tongue = rbox(-20.0, 20.0, yb_, -12.0, -44.7, zf, 2.0)                     # front face flush: it extends the head seat
    arm_r = rbox(-8.5, 1.5, yb_, yb_ + 3.8, zc - 15.8 - 4.5, -44.6, 2.0)   # under the X beam, 2 mm below it
    arm_f = rbox(-8.5, 1.5, yb_, yb_ + 3.8, zf - 0.6, zc + 15.8 + 3.0, 2.0)   # under the head's tapered bottom
    body = fuse([plate] + wings + [tongue, arm_r, arm_f])
    holes = []
    for x, y in ((-10, -1.5), (10, -1.5), (-10, 18.5), (10, 18.5)):          # MGN12H, counterbored from the head side
        holes += [Part.makeCylinder(M3_CLR, 6, V(x, y, zb - 0.5)), Part.makeCylinder(M3_CB, 3.0, V(x, y, zf - 3.0))]
    for x, y in ((19, -8), (-19, -8), (20, 25), (-20, 27.45)):              # Smart Head M3x16, heads on the back
        holes += [Part.makeCylinder(M3_CLR, 6, V(x, y, zb - 0.5)), Part.makeCylinder(M3_CB, 1.8, V(x, y, zb - 0.01))]
    for sx in (-1, 1):                                                        # toothed belt slots, belt ends at |x| 26
        for lv in (lo, up):
            xa, xb = sorted((sx * CLAMP_X, sx * 40.5))
            holes.append(box(xa, xb, lv[0] - 0.4, lv[1] + 0.4, zbelt - 0.75, zbelt + 0.85))
            for k in range(7):                                                # 2 mm pitch teeth pockets on the back wall
                xt = sx * (CLAMP_X + 1.0 + 2 * k)
                holes.append(box(*sorted((xt, xt + sx * 1.1)), lv[0] - 0.4, lv[1] + 0.4, zbelt - 1.5, zbelt - 0.7))
    for z in (zc - 15.8, zc + 15.8):                                          # Beacon M3 x3 heat-set inserts (turned 90 deg)
        holes.append(Part.makeCylinder(M3_INSERT, 3.4, V(-3.5, yb_ - 0.01, z), V(0, 1, 0)))
    holes.append(box(-19.6, -12.6, yb_ - 4.0, yb_ + 9.0, -46.5, -34.9))       # Normal/LP connector pocket
    holes.append(box(-19.6, -10.6, yb_ - 0.1, yb_ + 1.3, -60.0, -21.0))       # top-side component strip
    body = cut(body, holes)
    for lab, s in HEAD_SRC:                                                   # interlock with the Smart Head PCB cover
        if 'PCB' in lab:
            body = body.cut(s)
    body = body.removeSplitter()
    if len(body.Solids) > 1:                                                  # keep the main body; report any sliver the cut leaves
        print('x carriage: dropped slivers', [round(so.Volume, 1) for so in sorted(body.Solids, key=lambda so: -so.Volume)[1:]])
        body = sorted(body.Solids, key=lambda so: -so.Volume)[0]
    return body
X_CARRIAGE_BT = x_carriage_bt()

# ---------------------------------------------------------------- printed: XY joints
def xy_joint(s_, y_xb):
    """Two printed parts per side, built for x<0 and mirrored.
    Plate: bolts to the Y block and clamps the X beam end with flanges over and under it (prints block face down).
    Pulley carrier: two decks and an outboard post holding the X-turn pulleys above the side beam; bolts to the plate's
    outboard face above the Y block (prints back face down)."""
    Y = y_xb; xp = -(A_RUN - R_T)
    ZT = L_UP[1] + 6.5                                           # joint top
    plate = box(-YB_FACE, -XB_HALF, Y - 19.0, Y + 20.0, ZB - 26.0, ZT)
    fl_lo = rbox(-XB_HALF - 0.01, -XB_HALF + 28.0, Y - 16.0, Y + 3.0, ZB - 26.0, ZB - 20.0, 2.0)   # behind the carriage's under-beam arm and Beacon (Y+5.7) at the X ends
    fl_up = rbox(-XB_HALF - 0.01, -XB_HALF + 28.0, Y - 16.0, Y + 16.0, ZB + 20.0, ZB + 24.5, 2.0)
    jp = fuse([plate, fl_lo, fl_up])
    holes = []
    for dy in (-10, 10):                                         # Y block M3, counterbored from the beam side
        for dz in (-10, 10):
            holes += [cylx(M3_CLR, -YB_FACE - 0.5, -XB_HALF + 0.5, Y + dy, YR_Z + dz), cylx(M3_CB, -XB_HALF - 3.6, -XB_HALF + 0.5, Y + dy, YR_Z + dz)]
    for dy in (-10, 10):                                         # M5 into the X beam bottom and top slots (T-nuts)
        if dy < 0:                                               # one bottom M5 (the flange stops short of the carriage's path)
            holes += [cyl(M5_CLR, ZB - 26.5, ZB - 19.5, -XB_HALF + 13.0, Y + dy), cyl(M5_CB, ZB - 26.5, ZB - 23.0, -XB_HALF + 13.0, Y + dy)]
        holes += [cyl(M5_CLR, ZB + 19.5, ZB + 25.0, -XB_HALF + 13.0, Y + dy), cyl(M5_CB, ZB + 22.0, ZB + 25.0, -XB_HALF + 13.0, Y + dy)]
    CARRIER_BOLTS = ((Y + 15.0, ZB + 34.0), (Y + 15.0, ZB + 54.0), (Y - 8.0, ZB + 44.0))
    for yy, zz in CARRIER_BOLTS:                                 # M3 heat-set inserts for the carrier
        holes.append(cylx(M3_INSERT, -YB_FACE - 0.01, -YB_FACE + 4.5, yy, zz))
    jp = cut(jp, holes)
    def deck(z0, z1):
        return fuse([rbox(-314.0, -293.0, Y + 10.0, Y + 42.0, z0, z1, 2.0), box(-293.5, -YB_FACE, Y + 10.0, Y + 20.0, z0, z1)])
    deck_lo = deck(ZB + 21.5, L_LO[0] - 2.0)
    deck_up = deck(L_UP[1] + 2.0, ZT)
    post = rbox(-314.0, -310.8, Y + 23.0, Y + 33.0, L_LO[0] - 2.1, L_UP[1] + 2.1, 1.0)
    back = box(-YB_FACE - 6.0, -YB_FACE, Y - 12.0, Y + 20.0, ZB + 21.5, ZT)
    pc = fuse([deck_lo, deck_up, post, back])
    holes = []
    for yy, zz in CARRIER_BOLTS:
        holes += [cylx(M3_CLR, -YB_FACE - 6.5, -YB_FACE + 0.5, yy, zz), cylx(M3_CB, -YB_FACE - 6.5, -YB_FACE - 3.0, yy, zz)]
    for dy in (X_RUN_DY - R_T, X_RUN_DY + R_T):                  # pulley axles: M5 from the top into a nut inserted from below
        holes += [cyl(M5_CLR, ZB + 21.0, ZT + 0.5, xp, Y + dy), cyl(M5_CB, ZT - 2.5, ZT + 0.5, xp, Y + dy), cyl(M5_NUT, ZB + 21.4, ZB + 25.6, xp, Y + dy)]
    pc = cut(pc, holes)
    if s_ > 0:
        jp, pc = mir(jp), mir(pc)
    return jp.removeSplitter(), pc.removeSplitter()

# ---------------------------------------------------------------- printed: rear corners (lower motor mount + upper cap)
def rear_corner(s_):
    """x<0 geometry, mirrored for x>0. Lower part: arm pad (2x M4 to the stock Z-carriage arm), motor plate, grips on the
    side beam end and rear beam end, idler axle bosses. Upper part: cap with the 625ZZ and the idler axle tops."""
    face = MOTOR_FACE_Z[s_]; lvl = LEVEL[s_]; oth = LEVEL[-s_]
    xm, ym = -XM, YM
    xi1, yi1 = -(P_RUN - R_T), y1_rear
    xi2, yi2 = -X_I2, y1_rear - R_T - R_S
    xt, yt = -(A_RUN - R_T), YM
    pl0, pl1 = face, face + 7.0                                   # motor plate
    pad = rbox(-344.0, -300.5, -48.5, -33.5, Z_ARM, pl1, 2.0)
    over_beam = rbox(-344.0, -300.5, -33.5, 4.0, ZB + 20.0, pl1, 2.0)
    outer = box(-344.0, -338.0, -31.5, 4.0, ZB - 12.0, ZB + 20.0)
    plate = rbox(-300.5 - 0.01, -216.0, -66.0, -22.6, pl0, pl1, 3.0)            # front edge clear of the joints at the rear limit
    on_rear = box(-REAR_BEAM_HALF, -216.0, -66.0, -26.0, ZB + 20.0, pl1)
    # Y hard stop for sensorless homing: the XY joint plate (|X| 278..285) lands on this pad 0.5 mm past the rear
    # travel limit, 1.5 mm before the X beam could reach the motor cans (c3_stopsweep.py)
    y_stop = box(-286.0, -277.0, -22.6 - 0.01, -22.6 + Y_STOP_PAD, pl0, pl1)
    lower = fuse([pad, over_beam, outer, plate, on_rear, y_stop])
    # idlers stand on M5 aluminium spacers, so the plate top stays flat (prints top face down, no supports)
    holes = [cyl(11.3, pl0 - 0.5, pl1 + 0.5, xm, ym)]                              # motor boss
    for dx in (-15.5, 15.5):
        for dy in (-15.5, 15.5):
            holes += [cyl(M3_CLR, pl0 - 0.5, pl1 + 0.5, xm + dx, ym + dy), cyl(M3_CB, pl1 - 3.0, pl1 + 0.5, xm + dx, ym + dy)]
    for x in (-ARM_HOLES_X[0], -ARM_HOLES_X[1]):                                    # stock arm M4 holes
        holes += [cyl(M4_CLR, Z_ARM - 0.5, pl1 + 0.5, x, ARM_Y['rear']), cyl(M4_CB, Z_ARM + 12.0, pl1 + 0.5, x, ARM_Y['rear'])]
    for x in (-SIDE_XC - 10, -SIDE_XC + 10):                                       # side beam top slots
        holes += [cyl(M5_CLR, ZB + 19.5, pl1 + 0.5, x, -12.0), cyl(M5_CB, ZB + 26.0, pl1 + 0.5, x, -12.0)]
    holes += [cylx(M5_CLR, -344.5, -337.5, -12.0, ZB - 10.0), cylx(M5_CB, -344.5, -341.0, -12.0, ZB - 10.0)]  # outer slot
    for y in (sum(REAR_BEAM_Y) / 2 - 10, sum(REAR_BEAM_Y) / 2 + 10):                 # rear beam top slots
        holes += [cyl(M5_CLR, ZB + 19.5, pl1 + 0.5, -REAR_BEAM_HALF + 10.0, y), cyl(M5_CB, ZB + 26.0, pl1 + 0.5, -REAR_BEAM_HALF + 10.0, y)]
    for x, y in ((xi1, yi1), (xi2, yi2), (xt, yt)):                                # M5 heat-set inserts for the axles
        holes += [cyl(3.2, pl1 - 6.5, pl1 + 0.1, x, y), cyl(M5_CLR, pl1 - 0.01, BEARING_Z[-1][1] + 10.0, x, y)]
    holes.append(box(-328.5, -299.0, -64.5, -50.5, 100, 300))                        # stock Z belt runs and its loop strip (full sweep)
    lower = cut(lower, holes)
    # ---- upper cap: posts and a deck above the top wheel, 625ZZ pocket over the motor
    ztop = max(BEARING_Z[s_][1], lvl[1] + 3.0) + 3.0
    zc0 = max(L_UP[1] + 3.5, (L_UP[0] + L_UP[1]) / 2 + 9.5)
    # cap arms run motor -> each wheel; near the turn idler it stays inside |X| 307 (stock Z-belt top blocks at full height)
    deck = None
    for (xa, ya), w in (((xi1, yi1), 14.0), ((xi2, yi2), 14.0), ((xt, yt), 11.0), ((-329.0, -25.0), 10.0), ((-226.0, -38.0), 10.0)):
        ln = math.dist((xm, ym), (xa, ya)); ang = math.degrees(math.atan2(ya - ym, xa - xm))
        seg = Part.makeBox(ln, w, ztop - zc0, V(0, -w / 2, 0)); seg.rotate(V(0, 0, 0), V(0, 0, 1), ang); seg.translate(V(xm, ym, zc0))
        deck = seg if deck is None else deck.fuse(seg)
    for (x, y), r in (((xi1, yi1), 9.0), ((xi2, yi2), 9.0), ((xt, yt), 5.5), ((xm, ym), 12.0)):
        deck = deck.fuse(cyl(r, zc0, ztop, x, y))
    posts = [rbox(-334.0, -324.0, -30.0, -20.0, pl1 + 0.05, ztop, 2.0), rbox(-231.0, -221.0, -43.0, -33.0, pl1 + 0.05, ztop, 2.0)]
    cap = fuse([deck] + posts)
    ch = [cyl(8.05, zc0 - 1, BEARING_Z[s_][1] + 0.05, xm, ym), cyl(4.0, zc0 - 1, ztop + 1, xm, ym)]   # 625ZZ presses in from below
    for x, y in ((xi1, yi1), (xi2, yi2), (xt, yt)):
        ch += [cyl(M5_CLR, zc0 - 1, ztop + 1, x, y), cyl(M5_CB, ztop - 3.0, ztop + 1, x, y)]
    for x, y in ((-329.0, -25.0), (-226.0, -38.0)):
        ch += [cyl(M4_CLR, pl1 - 1, ztop + 1, x, y), cyl(M4_CB, ztop - 4.0, ztop + 1, x, y)]
        lower = lower.cut(cyl(2.0, pl1 - 8.0, pl1 + 0.1, x, y))           # M4 heat-set in the lower part
    ch.append(cyl(4.5, ztop - 3.0, ztop + 1, xm, ym))                    # seat for the printed shaft cover (S80 shaft)
    cap = cut(cap, ch + [box(-328.5, -299.0, -64.5, -50.5, 100, 300)])
    # wheel envelopes must stay clear (axle bosses end at the flanges)
    if s_ > 0:
        lower, cap = mir(lower), mir(cap)
    return lower.removeSplitter(), cap.removeSplitter()

# ---------------------------------------------------------------- printed: front corners (AWD motor, cradle, base) and dock rail
DOCK_RAIL = dict(y=(594.0, 609.0), z=(RAIL_Z - 8.5 + 7.0, RAIL_Z - 8.5 + 22.0), x=294.0)
M4_INSERT = 2.8
WEB_O, WEB_I = (-344.0, -337.0), (-292.0, -286.5)            # cradle webs beside the front motor body (x<0)
SLOT_Y = (549.0, 568.0)                                       # slider clamp bolts (fixed in the webs)
WEB_I_Y0 = 538.5                                              # inner web and plate start: the X carriage wing passes at the front limit
def front_corner(s_):
    """x<0 geometry, mirrored for x>0. Three printed parts per front corner:
    base: arm pad (2x M4 to the stock Z-carriage arm), front wall, dock-rail end bracket and two tongues that lap onto
      the cradle webs; prints arm face down (as installed).
    cradle: grips the side beam end (outer face and bottom slots) and runs forward around the motor body to the arm:
      outer web, inner web and a floor; the slider sits on the web tops; prints floor down (as installed).
    motor slider: plate on the motor face, two posts beside the pulley, cap with the 625ZZ and a closed hood over the
      S80 shaft; slides -1..+3 mm in Y on the web tops, pulled forward by an M3 screw from the front; prints plate down."""
    xf, yf = -FM_X, Y_FM
    zr0, zr1 = DOCK_RAIL['z']; yse = SIDE_Y[1]
    pl0, pl1 = FACE_F, FACE_F + 6.0
    xs = (sum(WEB_O) / 2, sum(WEB_I) / 2)                     # bolt columns over the webs
    # ---- base on the Z-carriage arm
    pad = rbox(-344.0, -300.5, 580.5, 595.0, Z_ARM, pl0, 2.0)                 # stops short of the stock Z-carriage plate (Y 595.5)
    wall = rbox(-344.0, -300.5, 584.5, 595.0, pl0 - 0.01, pl0 + 20.0, 2.0)
    tongue_o = box(WEB_O[0], WEB_O[1], 556.0, 580.6, Z_ARM, pl0)
    tongue_i = box(WEB_I[0], WEB_I[1], 556.0, 587.3, Z_ARM, pl0)
    bracket = fuse([rbox(-307.5, -DOCK_RAIL['x'] + 15.0, 587.2, 598.8, Z_ARM, zr1 + 4.0, 2.0),
                    rbox(-298.6, -DOCK_RAIL['x'] + 15.0, 587.2, 612.0, Z_ARM, zr1 + 4.0, 2.0)])
    base = fuse([pad, wall, tongue_o, tongue_i, bracket])
    holes = []
    for x in (-ARM_HOLES_X[0], -ARM_HOLES_X[1]):              # stock arm M4, heads in the front wall
        holes += [cyl(M4_CLR, Z_ARM - 0.5, pl0 + 20.5, x, ARM_Y['front']), cyl(M4_CB, Z_ARM + 10.0, pl0 + 20.5, x, ARM_Y['front'])]
    holes.append(box(-DOCK_RAIL['x'] - 0.2, -DOCK_RAIL['x'] + 15.2, DOCK_RAIL['y'][0] - 0.2, DOCK_RAIL['y'][1] + 0.2, zr0 - 0.2, zr1 + 0.2))
    holes.append(cylx(1.7, -DOCK_RAIL['x'] - 12.0, -DOCK_RAIL['x'] + 0.5, sum(DOCK_RAIL['y']) / 2, (zr0 + zr1) / 2))
    for x in xs:                                              # tongues: the slider's front clamp bolts pass through into the webs
        holes.append(cyl(M4_CLR, Z_ARM - 0.5, pl0 + 0.5, x, SLOT_Y[1]))
    holes += [cyl(M4_CLR, Z_ARM - 0.5, zr1 + 4.5, xs[1], 589.5), cyl(M4_CB, zr1 - 1.0, zr1 + 4.5, xs[1], 589.5)]   # bracket to cradle
    holes.append(cyly(M3_CLR, 583.0, 599.0, -303.0, 180.0))  # M3 tension screw, head on the bracket front face
    holes.append(box(-328.5, -312.5, 597.5, 611.5, 100, 300))  # stock Z belt runs
    base = cut(base, holes)
    # ---- cradle: side beam end -> around the motor -> Z-carriage arm
    g0 = yse - 24.0
    grip_o = box(-344.0, -338.0, g0, yse + 0.01, ZB - 20.0, ZB + 20.0)
    grip_b = box(-344.0, -300.0, g0, yse + 0.01, 116.0, ZB - 20.0)
    web_o = fuse([box(WEB_O[0], WEB_O[1], yse, 556.0, 116.0, pl0), box(WEB_O[0], WEB_O[1], 555.99, 580.0, 116.0, Z_ARM)])
    web_i = fuse([box(WEB_I[0], WEB_I[1], WEB_I_Y0, 556.0, 116.0, pl0), box(WEB_I[0], WEB_I[1], 555.99, 596.5, 116.0, Z_ARM)])
    floor_ = box(WEB_O[0], WEB_I[1], yse, 580.0, 116.0, 121.0)
    cradle = fuse([grip_o, grip_b, web_o, web_i, floor_])
    holes = []
    for y in (g0 + 7.0, g0 + 17.0):                           # M5 into the side beam's outer face slots
        for z in (ZB - 10.0, ZB + 10.0):
            holes += [cylx(M5_CLR, -344.5, -337.5, y, z), cylx(M5_CB, -344.5, -341.0, y, z)]
    for x in (-SIDE_XC - 10.0, -SIDE_XC + 10.0):              # M5 up into the bottom slots, heads in counterbores
        holes += [cyl(M5_CLR, 115.5, ZB - 19.5, x, g0 + 12.0), cyl(M5_CB, 115.5, 125.0, x, g0 + 12.0)]
    for x in xs:                                              # M4 heat-set inserts: slider clamps (and tongues at SLOT_Y[1])
        holes.append(cyl(M4_INSERT, pl0 - 8.0, pl0 + 0.1, x, SLOT_Y[0]))
        holes.append(cyl(M4_INSERT, Z_ARM - 8.0, Z_ARM + 0.1, x, SLOT_Y[1]))
    holes.append(cyl(M4_INSERT, Z_ARM - 8.0, Z_ARM + 0.1, xs[1], 589.5))
    holes.append(box(WEB_I[0] - 0.5, WEB_I[1] + 0.5, 538.0, 568.0, 121.5, 142.0))   # motor connector window (connector faces inboard)
    holes += PG.cradle_insert_holes(-1)                       # station bar clip (purge/wipe stations)
    cradle = cut(cradle, holes)
    # ---- motor slider
    zc0, zc1 = BEARING_F[s_][0] - 0.5, BEARING_F[s_][1] + 2.5
    plate = rbox(WEB_O[0], WEB_I[1], yf - 22.0, 580.0, pl0, pl1, 3.0)
    posts = [rbox(-336.0, -325.0, yf - 4.0, yf + 8.0, pl1 - 0.01, zc0 + 0.01, 1.5),
             rbox(-304.0, -296.0, yf - 4.0, yf + 8.0, pl1 - 0.01, zc0 + 0.01, 1.5)]
    capf = rbox(-336.0, -296.0, yf - 10.5, yf + 10.5, zc0, zc1, 3.0)
    zdeck = L_UP[1] + 6.5 + 0.5                                  # joint carriers' top deck (+0.5) at the docking pose
    hood = cyl(6.0, max(zc1, zdeck) - 0.01, FACE_F + SHAFT + 2.0, xf, yf)
    if zc1 < zdeck:                                              # slim where the carriers pass at the docking pose
        hood = hood.fuse(cyl(4.5, zc1 - 0.01, zdeck, xf, yf))
    boss = rbox(-306.0, -300.0, 574.0, 580.0, pl1 - 0.01, 187.0, 1.0)
    slider = fuse([plate] + posts + [capf, hood, boss])
    holes = [cyl(11.3, pl0 - 0.5, pl1 + 0.5, xf, yf)]
    for dx in (-15.5, 15.5):                                  # motor M3, heads sunk flush (the joints pass over at docking)
        for dy in (-15.5, 15.5):
            holes += [cyl(M3_CLR, pl0 - 0.5, pl1 + 0.5, xf + dx, yf + dy), cyl(M3_CB, pl1 - 3.0, pl1 + 0.5, xf + dx, yf + dy)]
    for x in xs:                                              # clamp slots for the travel FM_SLIDE
        for y in SLOT_Y:
            y0, y1 = y - FM_SLIDE[1], y - FM_SLIDE[0]
            holes.append(fuse([box(x - M4_CLR, x + M4_CLR, y0, y1, pl0 - 0.5, pl1 + 0.5), cyl(M4_CLR, pl0 - 0.5, pl1 + 0.5, x, y0), cyl(M4_CLR, pl0 - 0.5, pl1 + 0.5, x, y1)]))
    holes += [cyl(8.05, zc0 - 0.5, BEARING_F[s_][1] + 0.05, xf, yf), cyl(3.0, zc0 - 0.5, FACE_F + SHAFT + 0.5, xf, yf)]   # 625ZZ from below, blind hood
    holes.append(cyly(M3_INSERT, 573.5, 580.5, -303.0, 180.0))   # tension screw insert
    holes.append(box(-293.5, WEB_I[1] + 1.0, yf - 23.0, WEB_I_Y0 + FM_SLIDE[1] - FM_SLIDE[0] - 1.0, pl0 - 0.5, pl1 + 0.5))   # X carriage wing clearance
    slider = cut(slider, holes)
    if s_ > 0:
        base, cradle, slider = mir(base), mir(cradle), mir(slider)
    return base.removeSplitter(), cradle.removeSplitter(), slider.removeSplitter()

def shaft_cover(x, y, z_top, shaft_end):
    """Printed cup over the S80 shaft end, pressed into the rear bearing cap's top counterbore."""
    return fuse([cyl(4.4, z_top - 3.0, z_top + 0.01, x, y), cyl(6.0, z_top, shaft_end + 2.0, x, y)]).cut(cyl(3.0, z_top - 3.5, shaft_end + 0.5, x, y))

# ---------------------------------------------------------------- assemble at the requested pose
def build_pose(y_xb, xn, with_static=True):
    P = []
    if with_static:
        P += parts
    for n, m, s in bridge_parts(y_xb) + joint_pulleys(y_xb):
        P.append((n, m, s, 'bridge'))
    for s_ in (-1, 1):
        jp, pc = xy_joint(s_, y_xb); tag = 'xn' if s_ < 0 else 'xp'
        P.append((f'xy joint plate {tag}', 'pps-cf', jp, 'bridge')); P.append((f'xy joint pulley carrier {tag}', 'pps-cf', pc, 'bridge'))
    car = bt_to_printer(X_CARRIAGE_BT, xn, y_xb)
    P.append(('x carriage', 'pps-cf', car, 'head'))
    P.append(('umbilical head saddle', 'pps-cf', RT.head_clamp(xn, y_xb), 'head'))
    P.append(('x block mgn12h', 'steel', box(xn - 22.7, xn + 22.7, y_xb + 23.0, y_xb + 33.0, RAIL_Z - 13.5, RAIL_Z + 13.5), 'head'))
    for lab, s in HEAD_SRC:
        P.append(('indx smart head ' + lab.lower()[:28], 'purchased', bt_to_printer(s, xn, y_xb), 'head'))
    for lab, s in TOOL_HELD:
        P.append(('indx tool on head ' + lab.lower()[:24], 'purchased', bt_to_printer(s, xn, y_xb), 'head'))
    P.append(('beacon revh normal', 'purchased', beacon_at(xn, y_xb), 'head'))
    paths = belt_paths(y_xb, xn); lens = {}
    for k, lvl in (('B', L_UP), ('A', L_LO)):
        sol, L = belt_solid(paths[k], lvl); lens[k] = round(L + 2 * TAIL, 1)
        P.append((f'belt {k} gates 2mgt 12mm', 'purchased', sol, 'belts'))
    if os.environ.get('C3_ARCS', '1') == '1':                    # piano-wire arcs for this head position (c3_routing)
        P += RT.arc_parts(xn, y_xb)
    return P, lens

if True:
    for s_ in (-1, 1):
        tag = 'xn' if s_ < 0 else 'xp'
        lo_, cap_ = rear_corner(s_); add(f'rear corner {tag} motor mount', 'pps-cf', lo_, 'frame'); add(f'rear corner {tag} bearing cap', 'pps-cf', cap_, 'frame')
        ztop = max(BEARING_Z[s_][1], LEVEL[s_][1] + 3.0) + 3.0
        add(f'rear shaft cover {tag}', 'pps-cf', shaft_cover(s_ * XM, YM, ztop, MOTOR_FACE_Z[s_] + SHAFT), 'frame')
        fb_, fc_, fs_ = front_corner(s_); add(f'front corner base {tag}', 'pps-cf', fb_, 'frame'); add(f'front cradle {tag}', 'pps-cf', fc_, 'frame')
        add(f'front motor slider {tag}', 'pps-cf', fs_, 'frame')
    add('dock rail 1515 588', 'al-6063 1515', box(-DOCK_RAIL['x'], DOCK_RAIL['x'], DOCK_RAIL['y'][0], DOCK_RAIL['y'][1], DOCK_RAIL['z'][0], DOCK_RAIL['z'][1]), 'docks')
    for i, x in enumerate(DOCK_X, 1):
        for lab, s in DOCK_SRC:
            add(f'bondtech dock {i} ' + lab.lower()[:22], 'purchased', bt_to_printer(s, x, Y_XB_DOCK), 'docks')
        for lab, s in TOOL_PARKED:
            add(f'indx tool parked {i} ' + lab.lower()[:20], 'purchased', bt_to_printer(s, x, Y_XB_DOCK), 'docks')
    if os.environ.get('C3_PURGE', '1') == '1':
        for n, m, s, g in PG.purge_parts():
            add(n, m, s, g)

import c3_enclosure as ENC
import c3_zdrive as ZD                                # 12 mm Z upgrade parts (built and checked by c3_zcheck.py)
def _stock_camera():
    labf, brep = STOCK_CACHE / 'stock_keep_labels.json', STOCK_CACHE / 'stock_keep.brep'
    if not brep.exists():
        return []
    labels = json.loads(labf.read_text()); kids = Part.read(str(brep)).childShapes()
    return [(l, s) for (l, k), s in zip(labels, kids) if 'camera kit' in k]
if os.environ.get('C3_ENCLOSURE', '1') == '1':
    for n, m, s, g in ENC.camera_parts(_stock_camera()) + ENC.top_hat_parts() + ENC.umbilical_parts() + RT.chain_parts(0.0):
        add(n, m, s, g)

if __name__ == '__main__':
    ALL, BELT_LEN = build_pose(POSE['y_xb'], POSE['xn'])

    # ---------------------------------------------------------------- quick report + exports
    def bbox_of(shapes):
        b = shapes[0].BoundBox
        for s in shapes[1:]:
            b.add(s.BoundBox)
        return b
    rep = dict(pose=POSE, belt_length_mm=BELT_LEN, parts=len(ALL),
               nozzle_z=NOZZLE_Z, dock_rail=DOCK_RAIL,
               beacon_source_bbox=[round(v, 2) for v in (_bbx.XMin, _bbx.XMax, _bbx.YMin, _bbx.YMax, _bbx.ZMin, _bbx.ZMax)])
    for g in ('frame', 'bridge', 'head', 'docks', 'belts', 'enclosure'):
        b = bbox_of([s for n, m, s, gg in ALL if gg == g])
        rep[f'bbox_{g}'] = [round(v, 1) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]
    # internal overlaps between new parts (printed vs purchased / printed vs printed), excluding intended contacts
    pairs = []
    solids = [(n, m, s, g) for n, m, s, g in ALL if g != 'belts']
    for i in range(len(solids)):
        for j in range(i + 1, len(solids)):
            a, b = solids[i], solids[j]
            if not a[2].BoundBox.intersect(b[2].BoundBox):
                continue
            if a[1] != 'pps-cf' and b[1] != 'pps-cf':
                continue
            try:
                v = a[2].common(b[2]).Volume
            except Exception:
                v = -1
            if v > 1.0:
                pairs.append((round(v, 1), a[0], b[0]))
    rep['printed_overlaps'] = sorted(pairs, reverse=True)[:60]
    (OUT / 'C3_BUILD_REPORT.json').write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if k != 'printed_overlaps'}, indent=1))
    print('printed overlaps', len(pairs)); [print('  ', p) for p in rep['printed_overlaps'][:40]]
    if EXPORT:
        doc = App.newDocument('C3'); objs = []
        for n, m, s, g in ALL:
            o = doc.addObject('Part::Feature', 'P'); o.Label = f'{n} [{m}]'; o.Shape = s; objs.append(o)
        doc.recompute(); doc.saveAs(str(OUT / 'C3_GANTRY.FCStd'))
        Import.export(objs, str(OUT / 'C3_GANTRY.step'))
        print('exported', len(objs))
