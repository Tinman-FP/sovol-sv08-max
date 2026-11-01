"""C3 PTFE tubes and head cables (owner, 2026-10-31): fixed tube anchors and gravity loops outside, a guide above each dock.

Why it is laid out this way:
* Each INDX tool keeps its own PTFE tube, whether it is parked or on the head. With the gantry travelling 500 mm in Z, a
  tube's length from a fixed point above changes by about 600-800 mm. Loose slack inside the chamber can knock a parked
  tool out of its dock (Bondtech's warning), so each tube runs over a weighted sled outside the printer instead.
* Path of a tube: filament box -> PC4-M10 coupler on the loop head (the collet anchors the tube; it passes through) ->
  down the outside of the frame -> U around its weighted sled -> back up -> a curved guide into its entry hole in the top
  hat side wall -> taut across the inside of the top hat to a guide right above its own dock -> down to the tool. A
  parked tool's tube hangs straight down into it; only the tool on the head has a tube across the chamber.
* The sled halves the travel: about 420 mm of sled travel for the worst tube's 840 mm. The weight keeps every tube under a light,
  constant pull (half the sled's weight per leg).
* Right side (the printer's right, x < 0): tools T0-T2 (docks 1-3) and the head cables (INDX Link cable and Beacon USB,
  bundled) on a bigger sled. Left side: T3, T4 and a spare loop. The lowest entry hole serves the nearest dock.
* The Link Board and USB hub tray moves outside onto the right side of the top hat, next to the cable anchor.

Frame: Sovol's model in the stock pose, as c3_params. Side faces at |X| 354.5; Sovol's front Z profiles (48 x 48, slot
on the outer face at Y 581.6..589.6) carry the weight towers.
"""
import math
import FreeCAD as App, Part
from c3_params import DOCK_X, Y_XB_DOCK, NOZZLE_DY
V = App.Vector

FACE = 354.5                        # frame / top hat outer side faces |X|
FRAME_TOP = 591.3
TH_TOP = FRAME_TOP + 136.0
NOZ_Y = Y_XB_DOCK + NOZZLE_DY       # 570.55: every tool's filament inlet sits above its nozzle
WALL_IN = 46.0                      # entry holes run 46 mm in from the face (40 mm top hat wall + 6 mm)
PROFILE_SLOT_Y = 585.6              # Sovol's front Z profile: outer-face slot centre (tower mounting, M5 T-nuts)

# loops, built in the left side's frame (x > 0, outward +X): name, outward offset of the loop plane from the face,
# U radius, guide (swan neck) radius, entry Z, bore radius, fixed-leg Y, free-leg Y, dock X (None: spare / cables)
def _loops(side):
    if side > 0:
        return [('spare', 28.0, 25.0, 25.0, 608.0, 3.0, NOZ_Y - 50.0, NOZ_Y, None),
                ('t4', 42.0, 25.0, 25.0, 624.0, 3.0, NOZ_Y - 50.0, NOZ_Y, DOCK_X[4]),
                ('t3', 56.0, 25.0, 25.0, 640.0, 3.0, NOZ_Y - 50.0, NOZ_Y, DOCK_X[3])]
    return [('t0', 28.0, 25.0, 25.0, 608.0, 3.0, NOZ_Y - 50.0, NOZ_Y, DOCK_X[0]),
            ('t1', 42.0, 25.0, 25.0, 624.0, 3.0, NOZ_Y - 50.0, NOZ_Y, DOCK_X[1]),
            ('t2', 56.0, 25.0, 25.0, 640.0, 3.0, NOZ_Y - 50.0, NOZ_Y, DOCK_X[2]),
            ('cables', 42.0, 35.0, 35.0, 658.0, 7.0, 400.55, 470.55, None)]
SLED_Z = {25.0: 340.0, 35.0: 200.0}     # nominal sled centres in the model (they float with the head)
TOWER_Z = {1: (-60.0, 555.0), -1: (-60.0, 555.0)}  # weight towers: about 490 mm of sled travel (worst tube swing about 840 mm)
GUIDE = dict(r=25.0, exit_z=597.0, bar_y=(545.0, 560.0), bar_z=(660.0, 675.0), bar_x=310.0)
# guide inlet heights: nearest dock lowest, so each tube passes over the guides nearer its wall
INLET_Z = {DOCK_X[0]: 626.0, DOCK_X[1]: 656.0, DOCK_X[2]: 686.0, DOCK_X[4]: 626.0, DOCK_X[3]: 656.0}
DROP_RING = (50.0, 420.0)            # the cables' drop ring on the spine (c3_enclosure)

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def cylx(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))
def cyly(r, y0, y1, x, z):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))
def cylz(r, z0, z1, x, y):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))
def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()
def cut(s, tools):
    for t in tools:
        s = s.cut(t)
    return s
def mirror_x(s):
    return s.mirror(V(0, 0, 0), V(1, 0, 0))

def _pipe(pts, r):
    """Solid pipe of radius r swept along a planar path given as ('L', a, b) lines and ('A', a, mid, b) arcs (one sweep,
    so no fragile joins between straight and bent pieces)."""
    edges = []
    for seg in pts:
        if seg[0] == 'L':
            edges.append(Part.LineSegment(V(*seg[1]), V(*seg[2])).toShape())
        else:
            edges.append(Part.Arc(V(*seg[1]), V(*seg[2]), V(*seg[3])).toShape())
    w = Part.Wire(edges)
    e0 = w.Edges[0]
    c = Part.Wire(Part.makeCircle(r, e0.valueAt(e0.FirstParameter), e0.tangentAt(e0.FirstParameter)))
    return w.makePipeShell([c], True, True)

def _swan(d, R, ze, y, r, lead=22.0):
    """Path solid (radius r) of a loop's free leg into the top hat, left-side frame: up at X FACE+d, a quarter bend of
    radius R inward, then level at Z ze through the wall to WALL_IN inside the face."""
    x, xc, zc = FACE + d, FACE + d - R, ze - R
    k = R * math.sqrt(0.5)
    segs = [('A', (x, y, zc), (xc + k, y, zc + k), (xc, y, ze)), ('L', (xc, y, ze), (FACE - WALL_IN, y, ze))]
    if lead > 0:
        segs.insert(0, ('L', (x, y, zc - lead), (x, y, zc)))
    return _pipe(segs, r)

def _bell_z(r, z, x, y, up=True, flare=3.0, h=6.0):
    """Bell mouth on a vertical bore: radius r + flare at z, narrowing to r over h (upward if up)."""
    if up:
        return Part.makeCone(r + flare, r, h, V(x, y, z))
    return Part.makeCone(r, r + flare, h, V(x, y, z - h))

def loop_head(side):
    """Loop head (one printed part per side, PPS-CF), built in the left frame and mirrored for the right: back plate on
    the top hat side face and the frame's top band, a shelf with the M10x1 coupler holes (tap after printing) above each
    fixed leg, the cable anchor (right side), and a curved guide for each free leg into its entry hole."""
    L = _loops(side)
    ys = [l[6] for l in L] + [l[7] for l in L]
    y0, y1 = min(ys) - 15.0, max(ys) + 15.0
    umax = max(l[1] for l in L) + 12.0
    back = box(FACE, FACE + 5.0, y0, y1, 555.0, 708.0)
    adds, holes = [back], []
    for yf in sorted({l[6] for l in L}):                     # a shelf tab over each row of fixed legs, gusset under it
        adds.append(box(FACE, FACE + umax, yf - 12.0, yf + 12.0, 696.0, 706.0))
        g = Part.makePolygon([V(FACE, yf - 12.0, 696.0), V(FACE + umax, yf - 12.0, 696.0), V(FACE, yf - 12.0, 696.0 - umax), V(FACE, yf - 12.0, 696.0)])
        adds.append(Part.Face(g).extrude(V(0, 4.0, 0)))
    for name, d, Ru, Rg, ze, rb, yf, yfree, dock in L:
        x = FACE + d
        adds.append(_swan(d, Rg, ze, yfree, rb + 2.5))
        if name == 'cables':                                   # anchor: a slot open to the outside edge, two tie holes
            holes += [box(x - 6.0, FACE + umax + 1.0, yf - 6.0, yf + 6.0, 695.0, 707.0)]
            holes += [box(x - 12.0, x - 9.0, yf - 10.0, yf - 7.0, 695.0, 707.0), box(x - 12.0, x - 9.0, yf + 7.0, yf + 10.0, 695.0, 707.0)]   # tie slots
        else:
            holes.append(cylz(4.5, 695.0, 707.0, x, yf))                      # M10x1 tap drill (9.0 mm)
        holes += [_swan(d, Rg, ze, yfree, rb), cylz(rb, ze - Rg - 30.0, ze - Rg - 21.0, x, yfree)]
        holes.append(_bell_z(rb, ze - Rg - 22.0, x, yfree))
    s = fuse(adds)
    s = s.common(box(FACE, FACE + umax + 1.0, y0, y1, 555.0, 708.0))         # nothing past the shelf or into the face
    for yy, zz in _head_screws(side):
        holes.append(cylx(2.2, FACE - 1.0, FACE + 6.0, yy, zz))               # M4 through the top hat skin, nuts inside
    s = cut(s, holes)
    return s if side > 0 else mirror_x(s)

def _head_screws(side):
    """(Y, Z) of the loop head's four M4 screws: clear of the shelves' gussets and of the top hat joint ribs (Y 394-400)."""
    L = _loops(side)
    ys = [l[6] for l in L] + [l[7] for l in L]
    y0, y1 = min(ys) - 15.0, max(ys) + 15.0
    return [(y0 + 20.0, 600.0), (y0 + 20.0, 690.0), (y1 - 8.0, 600.0), (y1 - 8.0, 690.0)]

def top_hat_cuts():
    """Holes the top hat side walls need (c3_enclosure.top_hat_parts cuts these): each loop's entry hole with a bell mouth
    inside, the loop heads' and the tray's M4 holes."""
    out = []
    for side in (1, -1):
        L = _loops(side)
        for name, d, Ru, Rg, ze, rb, yf, yfree, dock in L:
            h = cylx(rb, FACE - WALL_IN - 1.0, FACE + 1.0, yfree, ze).fuse(Part.makeCone(rb + 2.5, rb, 5.0, V(FACE - WALL_IN, yfree, ze), V(1, 0, 0)))
            out.append(h if side > 0 else mirror_x(h))
        for yy, zz in _head_screws(side):
            h = cylx(2.2, FACE - 12.0, FACE + 1.0, yy, zz)
            out.append(h if side > 0 else mirror_x(h))
    for yy, zz in ((TRAY['y'][0] + 10.0, TRAY['z'][0] + 10.0), (TRAY['y'][0] + 10.0, TRAY['z'][1] - 10.0),
                   (TRAY['y'][1] - 10.0, TRAY['z'][0] + 10.0), (TRAY['y'][1] - 10.0, TRAY['z'][1] - 10.0)):
        out.append(mirror_x(cylx(2.2, FACE - 12.0, FACE + 1.0, yy, zz)))
    return out

def tower_sections(side):
    """Weight tower (ASA), left frame, mirrored for the right: a back plate on the frame face, end walls and one channel
    per sled, open at the top for the legs; a floor at the bottom. Split into sections of at most 230 mm; each has two
    M5 holes into the Z profile's outer slot (T-nuts)."""
    L = _loops(side)
    zb, zt = TOWER_Z[side]
    walls = []
    for name, d, Ru, Rg, ze, rb, yf, yfree, dock in L:
        w = 12.0 if Ru < 30 else 16.0
        ylo, yhi = (yf + yfree) / 2 - Ru - 7.0, (yf + yfree) / 2 + Ru + 7.0
        walls += [(d - w / 2 - 2.0, d - w / 2, ylo, yhi), (d + w / 2, d + w / 2 + 2.0, ylo, yhi)]
    ylo = min(w[2] for w in walls); yhi = max(w[3] for w in walls)
    umax = max(w[1] for w in walls)
    groups = sorted({(round(w[2], 1), round(w[3], 1)) for w in walls})
    n = max(1, math.ceil((zt - zb) / 230.0)); hs = (zt - zb) / n
    out = []
    for k in range(n):
        z0, z1 = zb + k * hs, zb + (k + 1) * hs
        parts = [box(FACE, FACE + 4.0, ylo - 3.0, max(yhi + 3.0, PROFILE_SLOT_Y + 9.0), z0, z1)]
        for u0, u1, a, b in walls:
            parts.append(box(FACE + u0, FACE + u1, a, b, z0, z1))
        for a, b in groups:                                   # end walls of each group of channels
            parts += [box(FACE, FACE + umax, a - 3.0, a, z0, z1), box(FACE, FACE + umax, b, b + 3.0, z0, z1)]
        if k == 0:
            parts.append(box(FACE, FACE + umax, ylo - 3.0, yhi + 3.0, z0, z0 + 3.0))
        s = fuse(parts)
        hl = [cylx(2.75, FACE - 1.0, FACE + 5.0, PROFILE_SLOT_Y, z0 + hs * f) for f in (0.25, 0.75)]
        if k == 0:
            hl += [cylz(4.0, z0 - 1.0, z0 + 4.0, FACE + d, (min(yf, yfree) + max(yf, yfree)) / 2) for _, d, _, _, _, _, yf, yfree, _ in L]
        s = cut(s, hl)
        nm = f'ptfe tower {"left" if side > 0 else "right"} {chr(97 + n - 1 - k)}'      # a = top section
        out.append((nm, s if side > 0 else mirror_x(s)))
    return out

def sled(Ru, thick):
    """Weighted sled: a disc the loop wraps under, groove for the tube (or cable bundle), pockets for M8 nuts."""
    rg = 2.3 if Ru < 30 else 5.6
    s = Part.makeCylinder(Ru + 1.5, thick, V(-thick / 2, 0, 0), V(1, 0, 0))
    t = Part.makeTorus(Ru, rg, V(0, 0, 0), V(1, 0, 0))
    s = s.cut(t)
    pockets = [(0.0, 0.0)] if Ru < 30 else [(0.0, -11.0), (0.0, 11.0)]
    for py, pz in pockets:
        s = s.cut(Part.makeCylinder(7.6, 6.8, V(thick / 2 - 6.8 + 0.01, py, pz), V(1, 0, 0)))   # M8 nut (13 AF), hex fits
    return s

def guide(dx, inlet_z, from_side):
    """Guide above a dock (PPS-CF): the tube arrives level from its wall's side (from_side -1: from -X, +1: from +X),
    bends down (radius 25) and leaves straight down over the tool's inlet with a bell mouth. A web ties it to the bar's
    front face (M3 into a 1515 T-nut)."""
    R, ze = GUIDE['r'], GUIDE['exit_z']
    zc = inlet_z - R
    xc = dx + from_side * R
    def path(r):                                                 # level lead-in from the wall's side, bend, straight down
        k = R * math.sqrt(0.5)
        return _pipe([('L', (xc + from_side * 14.0, NOZ_Y, inlet_z), (xc, NOZ_Y, inlet_z)),
                      ('A', (xc, NOZ_Y, inlet_z), (xc - from_side * k, NOZ_Y, zc + k), (dx, NOZ_Y, zc)),
                      ('L', (dx, NOZ_Y, zc), (dx, NOZ_Y, ze))], r)
    xlo, xhi = min(dx, xc + 14.0 * from_side) - 6.0, max(dx, xc + 14.0 * from_side) + 6.0
    body = fuse([path(5.5), box(xlo, xhi, GUIDE['bar_y'][1], NOZ_Y - 3.0, ze, GUIDE['bar_z'][1]),
                 box(dx - 6.0, dx + 6.0, NOZ_Y - 4.0, NOZ_Y + 4.0, ze, inlet_z)])
    body = body.common(box(xlo, xhi, GUIDE['bar_y'][1], NOZ_Y + 6.0, ze, inlet_z + 6.0))
    body = cut(body, [path(3.0), _bell_z(3.0, ze, dx, NOZ_Y, up=True),
                      cyly(1.7, GUIDE['bar_y'][1] - 1.0, NOZ_Y - 2.9, dx + from_side * (R + 12.0), sum(GUIDE['bar_z']) / 2)])   # M3 into the bar
    return body

def guide_bar():
    x = GUIDE['bar_x']; (y0, y1), (z0, z1) = GUIDE['bar_y'], GUIDE['bar_z']
    return box(-x, x, y0, y1, z0, z1)

def bar_hanger(spine_z0):
    """Holds the guide bar under the 2020 spine (2 x M5 into spine T-nuts, M3 up into the bar's bottom slot)."""
    (y0, y1), (z0, z1) = GUIDE['bar_y'], GUIDE['bar_z']
    ym = (y0 + y1) / 2
    s = fuse([box(-16.0, 16.0, ym - 22.0, ym + 22.0, spine_z0 - 6.0, spine_z0),
              box(-16.0, 16.0, y0 - 4.0, y0, z0 - 4.0, spine_z0), box(-16.0, 16.0, y1, y1 + 4.0, z0 - 4.0, spine_z0),
              box(-16.0, 16.0, y0 - 4.0, y1 + 4.0, z0 - 4.0, z0)])
    s = s.cut(box(-17.0, 17.0, y0, y1, z0, z1 + 0.2))
    s = cut(s, [cylz(2.75, spine_z0 - 7.0, spine_z0 + 0.1, 0.0, yy) for yy in (ym - 15.0, ym + 15.0)] +
               [cylz(1.7, z0 - 5.0, z0 + 0.1, 0.0, ym)])
    return s

TRAY = dict(y=(238.0, 378.0), z=(600.0, 700.0))     # Link Board / USB hub tray on the right side of the top hat (outside)

def tray():
    """Perforated plate (10 mm grid, 2.8 mm holes) for the INDX Link Board and the USB hub, on 8 mm standoffs outside the
    right wall of the top hat, beside the cable anchor. Built for x > 0 and mirrored."""
    (y0, y1), (z0, z1) = TRAY['y'], TRAY['z']
    s = fuse([box(FACE + 8.0, FACE + 12.0, y0, y1, z0, z1)] +
             [box(FACE, FACE + 8.0, yy - 6.0, yy + 6.0, zz - 6.0, zz + 6.0) for yy in (y0 + 10.0, y1 - 10.0) for zz in (z0 + 10.0, z1 - 10.0)])
    holes = [cylx(1.4, FACE + 7.0, FACE + 13.0, y0 + 20.0 + 10 * i, z0 + 15.0 + 10 * j) for i in range(11) for j in range(8)]
    holes += [cylx(2.2, FACE - 1.0, FACE + 13.0, yy, zz) for yy in (y0 + 10.0, y1 - 10.0) for zz in (z0 + 10.0, z1 - 10.0)]
    return mirror_x(cut(s, holes))

def _tube(a, b, r=2.0):
    a, b = V(*a), V(*b); d = b - a
    return Part.makeCylinder(r, d.Length, a, d)

def tube_bodies():
    """The tubes and the cable bundle as installed, for the model and the static checks: outside legs and U turns at the
    nominal sled heights, the swan-neck bores, and the taut spans inside the top hat to the dock guides (and the cables
    to the drop ring). The parts below the guides move with the tools and are checked in c3_ptfecheck.py."""
    out = []
    for side in (1, -1):
        for name, d, Ru, Rg, ze, rb, yf, yfree, dock in _loops(side):
            r = 2.0 if Ru < 30 else 5.0
            zs = SLED_Z[Ru]; x = FACE + d
            legs = [cylz(r, zs, 706.0, x, yf), cylz(r, zs, ze - Rg, x, yfree), _swan(d, Rg, ze, yfree, r, lead=0.0)]
            u = Part.makeTorus(Ru, r, V(x, (yf + yfree) / 2, zs), V(1, 0, 0))     # the U under the sled
            legs.append(u.common(box(x - r - 1.0, x + r + 1.0, yf - Ru - r - 1.0, yfree + Ru + r + 1.0, zs - Ru - r - 1.0, zs)))
            s = fuse(legs)
            nm = 'head cables link and beacon loop' if name == 'cables' else f'ptfe tube {name} loop'
            out.append((nm, s if side > 0 else mirror_x(s)))
            xin = side * (FACE - WALL_IN)
            if name == 'cables':
                out.append(('head cables link and beacon span', _tube((xin, yfree, ze), (DROP_RING[0], DROP_RING[1], 668.0), r)))
            elif dock is not None:
                xg = dock + (-1 if side < 0 else 1) * (GUIDE['r'] + 14.0)
                out.append((f'ptfe tube {name} span', _tube((xin, yfree, ze), (xg, NOZ_Y, INLET_Z[dock]), r)))
    return out

def ptfe_parts(spine_z0):
    """(name, material, shape, group) for c3_build: everything is fixed to the printer frame (group 'enclosure')."""
    out = []
    for side, tag in ((1, 'left'), (-1, 'right')):
        out.append((f'ptfe loop head {tag}', 'pps-cf', loop_head(side), 'enclosure'))
        for nm, s in tower_sections(side):
            out.append((nm, 'asa', s, 'enclosure'))
        for name, d, Ru, Rg, ze, rb, yf, yfree, dock in _loops(side):
            thick = 10.0 if Ru < 30 else 14.0
            s = sled(Ru, thick); s.translate(V(side * (FACE + d), (yf + yfree) / 2, SLED_Z[Ru]))
            out.append(('cable loop sled' if name == 'cables' else f'ptfe loop sled {name}', 'pps-cf', s, 'enclosure'))
    out.append(('ptfe guide bar 1515 620', 'al-6063 1515', guide_bar(), 'enclosure'))
    out.append(('ptfe guide bar hanger', 'pps-cf', bar_hanger(spine_z0), 'enclosure'))
    for k, dx in enumerate(DOCK_X, 1):
        out.append((f'ptfe dock guide {k}', 'pps-cf', guide(dx, INLET_Z[dx], -1 if k <= 3 else 1), 'enclosure'))
    out.append(('link board and usb hub tray', 'pps-cf', tray(), 'enclosure'))
    for nm, s in tube_bodies():
        out.append((nm, 'purchased', s, 'enclosure'))
    return out
