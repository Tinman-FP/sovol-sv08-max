"""C3 routing (owner, 2026-11-01): cable chains in the side gaps, a harness on the gantry up to a mast on the rear beam,
and piano-wire arcs from the mast to every tool and to the head. Replaces the weighted PTFE loops of 2026-10-31.

Why it is laid out this way (measured in the C3 model, see c3_routecheck.py):
* The gantry moves 500 mm in Z and fills the frame: over its travel it sweeps everything inside except a 14-16 mm gap
  between each side beam (outer face |X| 338) and the frame face (|X| 354.5), from Y 97 to 450. The back is full (the X
  beam at its rearmost comes within 4 mm of the rear beam) and so is the front (the docks reach the frame face).
* So every cable and tube reaches the gantry through thin chains hanging in those gaps (7 x 7 mm inside, one tube or
  cable bundle each). Each chain's fixed end sits on the side panel at about print Z 290; its moving end bolts to the
  top outer slot of the side beam; the U hangs below and stays above Sovol's carry handles at the first layer.
* PTFE (as the U1, tubes in from the sides): each tube leaves its chain in one S-bend out of the gap, rises in a side
  mast over the side beam and turns once (155 deg, 35 mm) to leave 65 deg down, heading 30 deg forward of inboard, on
  its own piano wire to its tool. A parked tool's tube comes down into it from above; the active tool's tube follows the head. Routing the
  tubes to one mast at the back instead cost about 200 deg more bending per tube (about twice the drag).
* Head wiring (as the Rat Rig V-Core 4, from the back middle): the Link Board power and the USB cables come up the left
  chains, along the left side beam and over the rear corner to a mast on the middle of the rear beam, which carries the
  Link Board. The INDX Link cable and the Beacon USB leave the mast on a 1.5 mm piano wire in loom to the head.
* Motor cables come up from the base outside the side panels, into their own chains, and out along the side beams.
* The arc shapes are solved as an elastic rod (c3_elastica.py). They need the top hat 195 mm tall (was 136).
* Friction: a tube turns through about 32 deg (entry) + 180 (chain) + 228 (side mast) + 160-340 (arc, depending on where
  the head is): 600-780 deg. By the capstan rule (mu about 0.15) the extruder feels about 5-8 times the spool's own drag.

Frame: Sovol's model in the stock pose, as c3_params. 'Pose' heights are at the model pose; the gantry moves from
-GANTRY_DROP (first layer) to +GANTRY_RISE (500 mm print height).
"""
import math
import numpy as np
import FreeCAD as App, Part
from c3_params import DOCK_X, Y_XB_DOCK, NOZZLE_DY, GANTRY_DROP, GANTRY_RISE
import c3_elastica as EL
V = App.Vector

NOZ_Y = Y_XB_DOCK + NOZZLE_DY          # 570.55: the tools' inlets sit above their nozzles
FACE = 354.5                            # frame outer side faces |X|
BEAM_OUT = 338.0                        # side beam outer face |X| (4040 X 298..338, Z 137..177 at the pose)
BEAM_TOP, TOP_SLOT_X = 177.0, 328.0     # side beam top and its outer top slot
REAR_SLOT_Y = -36.0                     # rear beam (Y -66..-26) front top slot
PANEL_T = 3.0                           # side panel sheet outside the frame face (assumed; drill through it)

# ---------------------------------------------------------------- chains
CH_W, CH_H = 11.0, 10.0                 # micro chain outer width (along X) and height (in its bending plane); 7 x 7 inside
GAP_XC = BEAM_OUT + 2.75 + CH_W / 2     # chain plane |X| 346.25: 2.75 mm to the beam and to the frame face
Z_M = 175.0                             # top of each chain's moving run (pose): the end link hangs from the side-beam bracket
Z_U0 = -28.0                            # U centreline bottom at the first layer: 5 mm above Sovol's carry handles
F_Z = 252.0                             # fixed ends (frame Z; print Z 288.5)
ZM0 = Z_M - GANTRY_DROP
# per side, from the rear: (name, bend radius, moving-run Y, line carried to the harness or None)
CHAINS = {
    -1: [('motor rear right', 18.0, 110.5, None), ('ptfe t2', 28.0, 163.5, 't2'), ('ptfe t1', 28.0, 236.5, 't1'),
         ('ptfe t0', 28.0, 309.5, 't0'), ('motor front right', 18.0, 382.5, None)],
    1: [('motor rear left and link board power', 18.0, 110.5, 'pwr'), ('usb', 18.0, 163.5, 'usb'),
        ('ptfe t4', 28.0, 216.5, 't4'), ('ptfe t3', 28.0, 289.5, 't3'), ('motor front left', 18.0, 362.5, None)]}
LINE_R = {'t0': 2.0, 't1': 2.0, 't2': 2.0, 't3': 2.0, 't4': 2.0, 'pwr': 2.5, 'usb': 3.5}
TOOL_DOCK = {'t0': 0, 't1': 1, 't2': 2, 't3': 3, 't4': 4}

def chain_len(R):
    return (ZM0 - Z_U0 - R) + (F_Z - Z_U0 - R) + math.pi * R

def u_bottom(dz):
    """U centreline bottom (frame Z) with the gantry at offset dz from the pose: the U moves half as far as the gantry."""
    return Z_U0 + (dz + GANTRY_DROP) / 2.0

# ---------------------------------------------------------------- harness and mast
SIDE_X = 308.0                          # harness along each side beam (|X|), above the joint carriers and belts
SIDE_Z = {'t2': 270.0, 't1': 278.0, 't0': 286.0, 'pwr': 270.0, 'usb': 278.0, 't4': 286.0, 't3': 294.0}
CORNER_Y, REAR_Y = 34.0, -16.0          # side run turns inboard (plan radius 50) to run along X at Y -16
RISE_DY = 85.0                          # each line rises out of its chain over 85 mm of Y onto the side run
ARC_D = (0.0, math.cos(math.radians(70.0)), -math.sin(math.radians(70.0)))   # the umbilical leaves the rear mast 70 deg down
MAST_R = 35.0                            # umbilical channel bend radius in the rear mast
MAST_X = 306.0                           # PTFE risers |X|: inboard of the side top rail (at full height) and the top hat wall
RISE_Z, TURN_Z, TURN_R = 270.0, 357.5, 35.0   # S-bend out of the gap ends at RISE_Z; the 140 deg turn starts at TURN_Z
TUBE_TILT, TUBE_FWD = 65.0, 30.0         # tubes leave the side masts 65 deg down, heading 30 deg forward of inboard
UMB_EXIT = (0.0, 12.0, 384.0)            # umbilical clamp exit: the feed comes along -X at Y 0 and turns 90 deg into ARC_D
BOARD = dict(x=(23.0, 133.0), y=(-31.0, -11.0), z=(192.0, 252.0))   # Link Board envelope on the mast plate (check it)

# ---------------------------------------------------------------- arcs
EI_TUBE, W_TUBE = 11640.0, 28.0         # PTFE 4x2 with filament + 0.8 mm piano wire; g/m
EI_UMB, W_UMB = 56000.0, 100.0          # Link cable + Beacon USB in loom + 1.5 mm piano wire
TOOL_TOP = {'parked': 242.6, 'head': 240.1}   # tool inlet (push-fit) tops at the pose
UMB_HEAD = (0.0, 26.0, 252.0)           # umbilical saddle on the INDX PCB cover, relative to (head X, Y_XB): wire end

def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def cylx(r, x0, x1, y, z):
    x0, x1 = sorted((x0, x1)); return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))
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

# ---------------------------------------------------------------- path helpers
def bez(P0, t0, P3, t3, h0, h3, n=40):
    """Cubic Bezier samples from P0 (leaving along t0) to P3 (arriving along t3), handle lengths h0, h3."""
    P0, P3 = np.asarray(P0, float), np.asarray(P3, float)
    P1, P2 = P0 + h0 * np.asarray(t0, float), P3 - h3 * np.asarray(t3, float)
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3

def arc_pts(C, a, b, R, phi0, phi1, n=20):
    """Points C + R (cos phi a + sin phi b) for phi from phi0 to phi1."""
    C, a, b = (np.asarray(v, float) for v in (C, a, b))
    return np.array([C + R * (math.cos(p) * a + math.sin(p) * b) for p in np.linspace(phi0, phi1, n)])

def join(*segs):
    out = [np.asarray(segs[0], float)]
    for s in segs[1:]:
        s = np.asarray(s, float)
        out.append(s[1:] if np.linalg.norm(s[0] - out[-1][-1]) < 1e-6 else s)
    return np.vstack(out)

def min_radius(P):
    """Smallest radius of curvature along a polyline (circumradius of consecutive point triples, resampled to 4 mm)."""
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    u = np.arange(0.0, s[-1], 4.0)
    Q = np.stack([np.interp(u, s, P[:, k]) for k in range(3)], axis=1)
    best = 1e9
    for a, b, c in zip(Q[:-2], Q[1:-1], Q[2:]):
        A, B, C = np.linalg.norm(b - a), np.linalg.norm(c - b), np.linalg.norm(c - a)
        area = np.linalg.norm(np.cross(b - a, c - a)) / 2.0
        if area > 1e-9:
            best = min(best, A * B * C / (4.0 * area))
    return best

def resample(P, step=4.0):
    P = np.asarray(P, float)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    u = np.linspace(0.0, s[-1], max(3, int(round(s[-1] / step)) + 1))
    return np.stack([np.interp(u, s, P[:, k]) for k in range(3)], axis=1)

def pipe(P, r, step=6.0):
    """Tube of radius r along the points P, as a compound of short cylinders (resampled every 6 mm). B-spline sweeps of
    these 3D paths often fail in OCC, and the ones that work carry bounding boxes metres too big, which made every
    clash check slow. At the tightest bends here (30 mm) the gaps between cylinders are under 0.2 mm."""
    Q = resample(P, step)
    sols = []
    for a, b in zip(Q[:-1], Q[1:]):
        d = b - a
        if np.linalg.norm(d) > 1e-6:
            sols.append(Part.makeCylinder(r, float(np.linalg.norm(d)), V(*a), V(*d)))
    return Part.makeCompound(sols)

# ---------------------------------------------------------------- chains: shape at a gantry offset
def chain_centerline(s, R, Ym, dz):
    """Lines and arc of a chain's centreline (frame coords) with the gantry at offset dz: moving run at Ym, fixed run at
    Ym + 2R, U at the bottom."""
    x = s * GAP_XC; zu = u_bottom(dz); zc = zu + R; Yf = Ym + 2 * R; zm = Z_M + dz
    edges = []
    if zm - zc > 0.01:
        edges.append(Part.LineSegment(V(x, Ym, zm), V(x, Ym, zc)).toShape())
    edges.append(Part.Arc(V(x, Ym, zc), V(x, Ym + R, zu), V(x, Yf, zc)).toShape())
    if F_Z - zc > 0.01:
        edges.append(Part.LineSegment(V(x, Yf, zc), V(x, Yf, F_Z)).toShape())
    return Part.Wire(edges)

def chain_solid(s, R, Ym, dz):
    """Chain envelope (CH_W along X, CH_H across in its plane) with the gantry at dz."""
    w = chain_centerline(s, R, Ym, dz)
    e0 = w.Edges[0]; p0 = e0.valueAt(e0.FirstParameter)
    prof = Part.Wire(Part.makePolygon([p0 + V(-CH_W / 2, -CH_H / 2, 0), p0 + V(CH_W / 2, -CH_H / 2, 0),
                                       p0 + V(CH_W / 2, CH_H / 2, 0), p0 + V(-CH_W / 2, CH_H / 2, 0), p0 + V(-CH_W / 2, -CH_H / 2, 0)]))
    ps = Part.BRepOffsetAPI.MakePipeShell(w)
    ps.setBiNormalMode(V(1, 0, 0))
    ps.add(prof, False, False); ps.build(); ps.makeSolid()
    return ps.shape()

def chain_parts(dz=0.0):
    out = []
    for s, L in CHAINS.items():
        for name, R, Ym, line in L:
            out.append((f'cable chain {name}', 'purchased', chain_solid(s, R, Ym, dz), 'chains'))
    return out

# ---------------------------------------------------------------- line paths (gantry-relative, at the pose)
def exit_path(s, Ym, z):
    """From a chain's moving end up out of the gap (inboard of |X| 334.5 by Z 221: the frame's side top rail clears it at
    full height), then up and back onto the side run at |X| SIDE_X, height z, heading -Y."""
    a = bez((s * GAP_XC, Ym, Z_M), (0, 0, 1), (s * 334.0, Ym, 221.0), (0, 0, 1), 18.0, 18.0)
    dy = min(RISE_DY, Ym - CORNER_Y - 8.0)
    b = bez((s * 334.0, Ym, 221.0), (0, 0, 1), (s * SIDE_X, Ym - dy, z), (0, -1, 0), 0.75 * (z - 221.0), 0.65 * dy)
    return join(a, b)

def harness_path(s, Ym, line):
    """Full path of a line on the gantry: a PTFE tube up its side mast (ptfe_path), or the Link Board power and USB:
    chain end -> side run -> corner -> rear run -> Link Board."""
    if line.startswith('t'):
        return ptfe_path(s, Ym)
    z = SIDE_Z[line]
    p = exit_path(s, Ym, z)
    side = np.array([[s * SIDE_X, Ym - min(RISE_DY, Ym - CORNER_Y - 8.0), z], [s * SIDE_X, CORNER_Y, z]])
    xc = s * (SIDE_X - 50.0)
    corner = arc_pts((xc, CORNER_Y, z), (s, 0, 0), (0, -1, 0), 50.0, 0.0, math.pi / 2)    # to (xc, CORNER_Y - 50) heading -sX
    tx = {'pwr': 120.0, 'usb': 100.0}[line]                         # down to the Link Board's top edge
    rear = bez((xc, REAR_Y, z), (-s, 0, 0), (tx, -22.0, 262.0), (-1, 0, -0.3), 60.0, 40.0)
    return join(p, side, corner, rear)

def umbilical_feed():
    """Link cable + Beacon USB from the Link Board's top edge up beside the left channel block, along -X at Y 0 into
    the umbilical channel and its turn, like the tubes."""
    u = np.array([-1.0, 0.0, 0.0]); d = np.array(ARC_D); E = np.array(UMB_EXIT)
    S = E - MAST_R * (u + d); C = S + MAST_R * d
    rise = bez((118.0, -4.0, 256.0), (0, 0, 1), (S[0] + 40.0, S[1], S[2]), u, 110.0, 50.0)
    return join(rise, np.array([[S[0] + 40.0, S[1], S[2]], S]), arc_pts(C, -d, u, MAST_R, 0.0, math.pi / 2), np.array([E, E + 10.0 * d]))

def tube_heading(s):
    """Horizontal heading of a tube leaving its side mast: 30 deg forward of inboard. Straight inboard, a parked tube's
    spare length loops into the middle and meets the other side's tubes; at 60 deg it loops into the top hat's front wall."""
    f = math.radians(TUBE_FWD)
    return np.array([-s * math.cos(f), math.sin(f), 0.0])

def tube_dir(s):
    a = math.radians(TUBE_TILT)
    return math.cos(a) * tube_heading(s) + np.array([0.0, 0.0, -math.sin(a)])

def ptfe_path(s, Ym):
    """A PTFE tube on the gantry: chain end -> one S-bend out of the gap (|X| 346 -> 306; inboard of the side top rail
    by Z 221 and above the belt and joint carriers) -> straight up the side mast -> 140 deg turn -> exit, inboard and
    50 deg down."""
    a = bez((s * GAP_XC, Ym, Z_M), (0, 0, 1), (s * MAST_X, Ym, RISE_Z), (0, 0, 1), 42.0, 42.0)
    b = np.array([[s * MAST_X, Ym, RISE_Z], [s * MAST_X, Ym, TURN_Z]])
    h = tube_heading(s)
    turn = arc_pts(np.array([s * MAST_X, Ym, TURN_Z]) + TURN_R * h, -h, (0, 0, 1), TURN_R, 0.0, math.radians(90.0 + TUBE_TILT))
    E = turn[-1]
    return join(a, b, turn, np.array([E, E + 10.0 * tube_dir(s)]))

# ---------------------------------------------------------------- printed parts
def moving_bracket(s, Ym, line):
    """On the side beam's top outer slot (M5 T-nut), over the gap: holds the chain's end link (2 x M3 into the link's
    holes; check the chain) at Z_M and guides the line up out of the gap."""
    x0, x1 = s * (TOP_SLOT_X - 6.0), s * (GAP_XC + CH_W / 2 + 0.5)
    b = fuse([box(x0, x1, Ym - 7.0, Ym + 7.0, BEAM_TOP, BEAM_TOP + 7.0),
              box(s * (GAP_XC - CH_W / 2 - 0.25), x1, Ym - 7.0, Ym + 7.0, Z_M, BEAM_TOP + 7.0)])
    holes = [cylz(2.75, BEAM_TOP - 1.0, BEAM_TOP + 8.0, s * TOP_SLOT_X, Ym)]
    for dy in (-3.0, 3.0):                                    # end-link screws, up from below
        holes.append(cylz(1.6, Z_M - 0.5, Z_M + 6.0, s * GAP_XC, Ym + dy))
    if line:
        P = harness_path(s, Ym, line)
        holes.append(pipe(P, LINE_R[line] + 1.0))          # same samples as the line itself, so no slivers at the joints
    else:                                                     # motor cable: straight up and inboard through a slot
        holes.append(box(s * (GAP_XC - 4.0), s * (GAP_XC + 4.0), Ym - 3.5, Ym + 3.5, Z_M - 1.0, BEAM_TOP + 8.0))
    return cut(b, holes).removeSplitter()

def entry_path(s, Yf, line):
    """Outside -> through the side panel -> down into a chain's fixed end. Built from the chain upward: leaves up,
    curves outward and crosses the panel 30 deg from vertical."""
    d = np.array([s * math.sin(math.radians(30.0)), 0.0, math.cos(math.radians(30.0))])
    P3 = np.array([s * (FACE + PANEL_T + 14.0), Yf, F_Z + 62.0])
    return bez((s * GAP_XC, Yf, F_Z), (0, 0, 1), P3, d, 26.0, 20.0)

def fixed_anchor(s, Yf, kind):
    """Inside the gap: a block holding the chain's fixed end link, through-bolted to the outside plate (2 x M3 through
    the side panel). Outside: a PC4-M10 coupler (PTFE) or a cable slot with a zip-tie bar, on the 30 deg entry line."""
    xi0, xi1 = s * (GAP_XC - CH_W / 2 - 0.25), s * FACE
    inside = box(xi0, xi1, Yf - 8.0, Yf + 8.0, F_Z, F_Z + 34.0)
    xo0, xo1 = s * (FACE + PANEL_T), s * (FACE + PANEL_T + 8.0)
    outside = box(xo0, xo1, Yf - 14.0, Yf + 14.0, F_Z + 4.0, F_Z + 78.0)
    P = entry_path(s, Yf, kind)
    d = np.array([s * 0.5, 0.0, math.cos(math.radians(30.0))]); tip = P[-1]
    if kind == 'ptfe':                                        # coupler boss on the entry line, M10 thread
        boss = Part.makeCylinder(8.0, 14.0, V(*(tip - 6.0 * d)), V(*d))
        outside = outside.fuse(boss)
    holes = [pipe(P, (2.6 if kind == 'ptfe' else 4.2))]
    if kind == 'ptfe':
        holes.append(Part.makeCylinder(4.25, 12.0, V(*(tip - 2.0 * d)), V(*d)))
    for dy in (-3.0, 3.0):
        holes.append(cylz(1.6, F_Z - 0.5, F_Z + 6.0, s * GAP_XC, Yf + dy))
    for dy, zz in ((-5.5, F_Z + 8.0), (5.5, F_Z + 26.0)):     # 2 x M3 through the panel, beside the line's passage
        holes.append(cylx(1.7, s * (GAP_XC - 7.0), s * (FACE + PANEL_T + 9.0), Yf + dy, zz))
    inside, outside = cut(inside, holes).removeSplitter(), cut(outside, holes).removeSplitter()
    return inside, outside

def side_post(s, y):
    """On the side beam's top outer slot: a column clear of the belt (|X| >= 324), an arm over the joint carriers and
    a cradle under the side run at |X| SIDE_X (the lines are zip-tied in)."""
    z_arm = 232.0; zt = max(SIDE_Z.values()) + 8.0
    col = box(s * (TOP_SLOT_X - 4.0), s * (TOP_SLOT_X + 5.0), y - 6.0, y + 6.0, BEAM_TOP, z_arm + 8.0)
    arm = box(s * (SIDE_X - 6.0), s * (TOP_SLOT_X + 5.0), y - 6.0, y + 6.0, z_arm, z_arm + 8.0)
    cradle = box(s * (SIDE_X - 6.0), s * (SIDE_X + 5.0), y - 6.0, y + 6.0, z_arm, zt)
    p = fuse([col, arm, cradle])
    p = cut(p, [cylz(2.75, BEAM_TOP - 1.0, z_arm + 9.0, s * TOP_SLOT_X, y),
                box(s * (SIDE_X - 9.0), s * (SIDE_X + 4.5), y - 7.0, y + 7.0, SIDE_Z['t2'] - 4.0, zt + 1.0),    # line slot
                box(s * (SIDE_X - 6.5), s * (SIDE_X + 5.5), y - 2.0, y + 2.0, z_arm + 12.0, z_arm + 16.0)])      # zip tie
    return p.removeSplitter()

def rear_post(s, x, z_line):
    """On the rear beam's front top slot: a column just behind the X beam's rearmost reach, holding the rear run."""
    col = box(x - 6.0, x + 6.0, -34.0, -22.0, BEAM_TOP, z_line + 6.0)
    foot = box(x - 10.0, x + 10.0, -46.0, -26.0, BEAM_TOP, BEAM_TOP + 6.0)
    hook = box(x - 6.0, x + 6.0, -22.0, -8.0, z_line - 8.0, z_line - 3.0)
    p = fuse([col, foot, hook])
    return cut(p, [cylz(2.75, BEAM_TOP - 1.0, BEAM_TOP + 7.0, x, REAR_SLOT_Y)]).removeSplitter()

ARMS = {-1: (200.0, 273.0), 1: (190.0, 253.0)}           # side-mast arms, between the chain brackets

def side_mast(s):
    """Side mast over the side beam: two arms from the beam's top outer slot (M5 T-nuts), clear of the belt and over
    the joint carriers, carry a plate at |X| MAST_X with a vertical bore per PTFE tube and a sleeve round each tube's
    155 deg turn; it leaves 65 deg down, heading 30 deg forward of inboard. Each tube's 0.8 mm piano wire runs in a bore beside it and is held by an M3
    set screw in a heat-set insert."""
    ys = [Ym for n, R, Ym, line in CHAINS[s] if line and line.startswith('t')]
    y0, y1 = min(ys + list(ARMS[s])) - 7.0, max(ys + list(ARMS[s])) + 7.0
    z_arm = 232.0
    parts = [box(s * (MAST_X + 2.0), s * (MAST_X + 6.0), y0, y1, z_arm + 13.0, TURN_Z + 1.0),                # web
             box(s * (MAST_X + 2.0), s * (MAST_X + 6.0), y0, y1, z_arm, z_arm + 13.0)]
    for Ym in ys:                                                                                          # per tube:
        parts.append(box(s * (MAST_X - 6.0), s * (MAST_X + 6.0), Ym - 7.0, Ym + 7.0, z_arm + 13.0, TURN_Z + 1.0))   # riser boss
        Q = resample(ptfe_path(s, Ym), 6.0); Q = Q[Q[:, 2] > TURN_Z - 2.0][:-1]                                       # sleeve round the turn
        parts += [Part.makeCylinder(7.0, float(np.linalg.norm(b - a)), V(*a), V(*(b - a))) for a, b in zip(Q[:-1], Q[1:])]
        parts += [Part.makeSphere(7.0, V(*q)) for q in Q[1:-1]]
    for ya in ARMS[s]:
        parts += [box(s * (TOP_SLOT_X - 4.0), s * (TOP_SLOT_X + 5.0), ya - 6.0, ya + 6.0, BEAM_TOP, z_arm + 13.0),
                  box(s * (MAST_X - 7.0), s * (TOP_SLOT_X + 5.0), ya - 6.0, ya + 6.0, z_arm, z_arm + 13.0)]
    m = fuse(parts)
    holes = [cylz(2.75, BEAM_TOP - 1.0, z_arm + 14.0, s * TOP_SLOT_X, ya) for ya in ARMS[s]]
    d = tube_dir(s)
    for Ym in ys:
        P = ptfe_path(s, Ym)
        holes.append(pipe(P, 2.6))                                                   # same samples as the tube
        E = P[-2]
        w0 = E - 22.0 * d + np.array([0.0, 4.5, 0.0])                               # wire bore beside the exit
        holes.append(Part.makeCylinder(0.55, 40.0, V(*w0), V(*d)))
        sp = E - 8.0 * d + np.array([0.0, 4.5, 0.0])
        holes.append(cylz(2.0, sp[2], TURN_Z + TURN_R + 8.0, sp[0], sp[1]))          # M3 insert + set screw onto the wire
    return cut(m, holes)

def mast():
    """Rear mast (the head wiring, from the back middle): base on the rear beam's front top slot (4 x M5 T-nuts),
    column, the Link Board plate, and the umbilical channel: the loom turns 90 deg and leaves 70 deg down; the 1.5 mm
    piano wire is held beside it by an M3 set screw in a heat-set insert, as on the Rat Rig."""
    parts = [box(-35.0, 138.0, -46.0, -26.0, BEAM_TOP, BEAM_TOP + 8.0),            # base
             box(-15.0, 15.0, -34.0, -12.0, BEAM_TOP, 436.0),                       # column
             box(15.0, 138.0, -34.0, -31.0, BEAM_TOP, 258.0),                       # Link Board plate
             box(-12.0, 62.0, -10.0, 26.0, 372.0, 436.0)]                           # umbilical channel block
    m = fuse(parts)
    holes = []
    for x in (-25.0, 25.0, 90.0, 128.0):
        holes.append(cylz(2.75, BEAM_TOP - 1.0, BEAM_TOP + 9.0, x, REAR_SLOT_Y))
    F = umbilical_feed()
    d = np.array(ARC_D)
    holes.append(pipe(F, 6.8))                                                        # umbilical channel (loom 12 mm), same samples
    holes.append(Part.makeCylinder(6.8, 40.0, V(*F[-1]), V(*d)))                       # and out past the block
    E = np.array(UMB_EXIT); d = np.array(ARC_D)
    w0 = E - 22.0 * d + np.array([9.0, 0.0, 0.0])
    holes.append(Part.makeCylinder(0.8, 45.0, V(*w0), V(*d)))                        # 1.5 mm umbilical wire beside the loom
    holes.append(cylz(2.0, E[2] + 2.0, 441.0, 9.0, E[1] - 14.0))
    for zz in (BOARD['z'][0] + 6.0, BOARD['z'][1] - 6.0):                          # Link Board standoff slots (fit to the board)
        holes.append(Part.makeCylinder(1.6, 6.0, V(BOARD['x'][0] + 4.0, -35.0, zz), V(0, 1, 0)))
        holes.append(Part.makeCylinder(1.6, 6.0, V(BOARD['x'][1] - 4.0, -35.0, zz), V(0, 1, 0)))
    for zz in (300.0, 340.0, 380.0):                                               # zip-tie slots for the umbilical feed
        holes.append(box(-16.0, 16.0, -14.5, -11.5, zz, zz + 4.0))
    return cut(m, holes)                                                            # (removeSplitter breaks this solid)

def head_clamp(xn, y_xb):
    """Umbilical end on the head: a saddle that clips over the INDX PCB cover (X +-25.6, top Z 234 at the pose; fix it
    with VHB tape or Bondtech's own strain relief - check on the real head). Its lips stop at Z 226, above the XY joints
    (top Z 223.5), so the head still reaches both ends of X. The 1.5 mm wire enters a boss from above and is held by an
    M3 set screw; the loom is zip-tied to the boss."""
    x0, y0 = xn + UMB_HEAD[0], y_xb + UMB_HEAD[1]
    plate = box(x0 - 27.4, x0 + 27.4, y_xb + 12.0, y_xb + 37.5, 234.2, 238.0)        # the head body starts at Y_XB + 38
    lips = [box(x0 + sx * 25.8, x0 + sx * 27.4, y_xb + 16.0, y_xb + 36.0, 226.0, 238.0) for sx in (-1, 1)]
    boss = box(x0 - 6.0, x0 + 6.0, y0 - 6.0, y0 + 6.0, 238.0, UMB_HEAD[2])
    b = fuse([plate, boss] + lips)
    holes = [cylz(0.8, 240.0, UMB_HEAD[2] + 1.0, x0, y0), Part.makeCylinder(1.6, 8.0, V(x0 - 7.0, y0, 246.0), V(1, 0, 0)),
             box(x0 - 7.0, x0 + 7.0, y0 - 2.0, y0 + 2.0, 241.0, 243.5)]                # set screw, zip tie
    return cut(b, holes).removeSplitter()

def carriage_insert_holes(xn, y_xb):
    return []                                  # the saddle sits on the PCB cover: the X carriage is unchanged
# ---------------------------------------------------------------- arcs
def _side(line):
    return next(s for s, L in CHAINS.items() for c in L if c[3] == line)

def _arc_start(line):
    if line == 'umb':
        return np.array(UMB_EXIT) + 10.0 * np.array(ARC_D)
    s = _side(line); Ym = next(c[2] for c in CHAINS[s] if c[3] == line)
    return ptfe_path(s, Ym)[-1]

def _arc_dir(line):
    return np.array(ARC_D) if line == 'umb' else tube_dir(_side(line))

def tool_end(x, y_xb, parked):
    return np.array([x, y_xb + 66.45, (TOOL_TOP['parked'] if parked else TOOL_TOP['head']) + 12.0])

def umb_end(xn, y_xb):
    return np.array([xn + UMB_HEAD[0], y_xb + UMB_HEAD[1], UMB_HEAD[2] + 12.0])

_BED = [(x, y) for x in (-252.0, -126.0, 0.0, 126.0, 252.0) for y in (64.4, 190.0, 314.0, 440.0, 563.5)]
def arc_length(line):
    """Each line is long enough for its farthest reach (any bed position or its own dock) plus 8 % (tubes) or 10 %
    (umbilical); longer tubes loop into the top hat's front wall when parked."""
    A = _arc_start(line)
    if line == 'umb':
        pts = [umb_end(x, y - NOZZLE_DY) for x, y in _BED] + [umb_end(d, Y_XB_DOCK) for d in DOCK_X]
    else:
        pts = [tool_end(x, y - NOZZLE_DY, False) for x, y in _BED] + [tool_end(DOCK_X[TOOL_DOCK[line]], Y_XB_DOCK, True)]
    return (1.10 if line == 'umb' else 1.08) * max(float(np.linalg.norm(p - A)) for p in pts)

_LEN = {}
def arc_nodes(line, end):
    if line not in _LEN:
        _LEN[line] = arc_length(line)
    ei, w = (EI_UMB, W_UMB) if line == 'umb' else (EI_TUBE, W_TUBE)
    A, d = _arc_start(line), _arc_dir(line)
    X, ok = EL.solve(A, d, end, (0, 0, -1), _LEN[line], ei, w)
    if not ok:                                  # a planar start can stall: retry from a guess bowed sideways
        X0 = EL._initial(A, d, end, np.array([0.0, 0.0, -1.0]), _LEN[line], 36)
        X0[2:-2, 0] += 30.0 * np.sin(np.linspace(0.0, math.pi, len(X0) - 4))
        X, ok = EL.solve(A, d, end, (0, 0, -1), _LEN[line], ei, w, X0=X0)
    return X, ok

def arc_solid(X, line):
    tail = np.array([X[-1], X[-1] + np.array([0.0, 0.0, -10.0])])
    return pipe(np.vstack([X, tail[1:]]) if line != 'umb' else X, 6.0 if line == 'umb' else 2.2)

def arc_parts(xn, y_xb, active='t2'):
    """Piano-wire arcs for a head position: the active tool's tube and the umbilical to the head, the others to their
    docks (the model shows a tool in every dock; the active tool's dock has no tube)."""
    out = []
    for line, k in TOOL_DOCK.items():
        if line == active:
            X, ok = arc_nodes(line, tool_end(xn, y_xb, False))
        else:
            X, ok = arc_nodes(line, tool_end(DOCK_X[k], Y_XB_DOCK, True))
        out.append((f'ptfe arc {line}' + (' active' if line == active else ''), 'purchased', arc_solid(X, line), 'arcs'))
    X, ok = arc_nodes('umb', umb_end(xn, y_xb))
    out.append(('umbilical arc', 'purchased', arc_solid(X, 'umb'), 'arcs'))
    return out

# ---------------------------------------------------------------- everything fixed to the frame or the gantry
def routing_parts():
    out = []
    for s, L in CHAINS.items():
        tag = 'right' if s < 0 else 'left'
        for name, R, Ym, line in L:
            kind = 'ptfe' if line and line.startswith('t') else 'cable'
            ins, outs = fixed_anchor(s, Ym + 2 * R, kind)
            short = name.replace(' and link board power', '')
            out.append((f'chain anchor {short}', 'pps-cf', ins, 'enclosure'))
            out.append((f'chain entry {short}', 'pps-cf', outs, 'enclosure'))
            out.append((f'chain bracket {short}', 'pps-cf', moving_bracket(s, Ym, line), 'frame'))
            if line:
                out.append((f'harness {line}', 'purchased', pipe(harness_path(s, Ym, line), LINE_R[line]), 'frame'))
        out.append((f'side mast {tag}', 'pps-cf', side_mast(s), 'frame'))
    for y in (20.0, 80.0):                                    # the Link Board cables' run along the left side beam
        out.append((f'harness side post left y{y:.0f}', 'pps-cf', side_post(1, y), 'frame'))
    x, zl = 190.0, []                                         # rear post under the lowest of them, over the rear beam
    for name, R, Ym, line in CHAINS[1]:
        if line and not line.startswith('t'):
            P = harness_path(1, Ym, line)
            rear = P[np.abs(P[:, 1] - REAR_Y) < 4.0]
            zl.append(float(rear[np.argmin(np.abs(rear[:, 0] - x)), 2]) - LINE_R[line])
    out.append(('harness rear post left', 'pps-cf', rear_post(1, x, min(zl)), 'frame'))
    out.append(('rear mast', 'pps-cf', mast(), 'frame'))
    out.append(('link board envelope', 'purchased', box(BOARD['x'][0], BOARD['x'][1], BOARD['y'][0], BOARD['y'][1], BOARD['z'][0], BOARD['z'][1]), 'frame'))
    out.append(('umbilical feed', 'purchased', pipe(umbilical_feed(), 6.0), 'frame'))
    return out
