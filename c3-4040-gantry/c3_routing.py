"""C3 routing, simplified (owner, 2026-11-01 evening: "way too complicated"): PTFE couplers in the top hat's side walls
with the tubes hanging free to the tools, and the head cables straight down from the centre of the top cover.
Replaces the same day's PTFE chains, side masts, rear mast, harness and piano-wire tube arcs.

* The gantry climbs 500 mm, so a coupler has to sit above the gantry's highest point: lower down, a tube would hang
  under the gantry and into the print whenever the gantry is above the coupler. The five PC4-M10 couplers sit in the top
  hat's right side wall, two per bay in the three middle bays between the wall ribs (bay centre +/- 15 mm), 34 deg below
  horizontal and pointing inboard, as the stock SV08 Max feeds its one tube from the right side of the frame top. They
  run front to rear in dock order (T0, nearest the right wall, at the front): seen from above the parked tubes nest
  instead of crossing. With three on the right and two on the left (until 2026-11-04) the parked tubes from the two
  walls met and crossed in the middle; spread one per bay (Y 158-382) the rearmost tube ran into the wall and frame top
  and the front one toward the front wall, so they stay close together around the wall's middle.
* Each tube is one continuous PTFE tube from the filament box, through its coupler, to its tool. A tube is stiff enough
  to hold its own arch (solved as an elastic rod, c3_elastica.py): at the first layer it runs almost straight down to the
  tool; at full height its spare length arches up into the top hat. The couplers sit at frame Z 668 and point 34 deg down:
  lower or flatter, a tube's first stretch runs into the head (saddle, PCB cover, carriage) when the head is at the
  middle of the near side at full height; steeper, it reaches the belt; horizontal couplers send the arches about 70 mm
  above the cover. At 34 deg the arches stay about 7 mm under it.
* Head wiring: the INDX Link cable and the Beacon USB come straight down from the centre of the top cover, in loom on a
  1.4 mm piano wire (as the Rat Rig V-Core 4 umbilical), to the saddle on the INDX PCB cover. The Link Board and the USB
  hub sit on top of the cover. Straight down gives the smallest loop; angled exits send it up against the cover. At full
  height the loop has no single shape: with both ends pointing down it can swing round in plan at the same energy, so it
  has to clear the belts and the top hat's walls in every swung position. With 1.4 mm it clears belt B by 4 mm and the
  walls by 5-10 mm; 1.2 mm (until 2026-11-05) sagged 4.6 mm into belt B, 1.0 mm further, and 1.5 mm with 10 % spare
  length reached the walls. The clamp's round stalk leaves it 66 mm under the cover; a shorter stalk would clear the
  tubes' arches but lengthens the umbilical, whose swung loop then reaches the front and rear walls.
* Motor cables still come up from the base in their own micro chains in the side gaps (the only space the gantry never
  sweeps): one per motor.

Frame: Sovol's model in the stock pose, as c3_params. 'Pose' heights are at the model pose; the gantry moves from
-GANTRY_DROP (first layer) to +GANTRY_RISE (500 mm print height).
"""
import math
import numpy as np
import FreeCAD as App, Part
from c3_params import DOCK_X, Y_XB_DOCK, NOZZLE_DY, GANTRY_DROP, GANTRY_RISE
import c3_elastica as EL
import c3_enclosure as ENC
V = App.Vector

FACE = 354.5                            # frame outer side faces |X|
BEAM_OUT = 338.0                        # side beam outer face |X| (4040 X 298..338, Z 137..177 at the pose)
BEAM_TOP, TOP_SLOT_X = 177.0, 328.0     # side beam top and its outer top slot
PANEL_T = 3.0                           # side panel sheet outside the frame face (assumed; drill through it)

# ---------------------------------------------------------------- motor chains
CH_W, CH_H = 11.0, 10.0                 # micro chain outer width (along X) and height (in its bending plane); 7 x 7 inside
GAP_XC = BEAM_OUT + 2.75 + CH_W / 2     # chain plane |X| 346.25: 2.75 mm to the beam and to the frame face
Z_M = 175.0                             # top of each chain's moving run (pose): the end link hangs from the side-beam bracket
Z_U0 = -28.0                            # U centreline bottom at the first layer: 5 mm above Sovol's carry handles
F_Z = 252.0                             # fixed ends (frame Z; print Z 288.5)
ZM0 = Z_M - GANTRY_DROP
CHAIN_R = 18.0
# per side, from the rear: (name, moving-run Y)
CHAINS = {-1: [('motor rear right', 110.5), ('motor front right', 382.5)],
          1: [('motor rear left', 110.5), ('motor front left', 362.5)]}

def chain_len(R=CHAIN_R):
    return (ZM0 - Z_U0 - R) + (F_Z - Z_U0 - R) + math.pi * R

def u_bottom(dz):
    """U centreline bottom (frame Z) with the gantry at offset dz from the pose: the U moves half as far as the gantry."""
    return Z_U0 + (dz + GANTRY_DROP) / 2.0

# ---------------------------------------------------------------- PTFE wall couplers and the roof clamp
CPL_Y = {'t0': (-1, 351.85), 't1': (-1, 321.85), 't2': (-1, 288.5),   # (side, Y): all in the right wall, two per bay at the
         't3': (-1, 258.5), 't4': (-1, 225.15)}                         # bay centre +/- 15 mm between the ribs (241.8, 305.2,
                                                                        # 368.5; T4 alone at the front of the 178.5-241.8
                                                                        # bay); front to rear in dock order, so they nest
CPL_Z = 668.0                           # coupler axis at the wall's outer face (frame Z; print Z 704.7)
CPL_TILT = 34.0                         # axis below horizontal, pointing inboard
SEAT, BODY = 16.0, 18.0                 # pad seat along the axis from the outer face; coupler body from the seat to the tube
TOOL_DOCK = {'t0': 0, 't1': 1, 't2': 2, 't3': 3, 't4': 4}
ROOF_XY = (0.0, 0.5 * (ENC.OUT_Y[0] + ENC.OUT_Y[1]))   # centre of the top cover: (0, 273.5)
ROOF_Z = ENC.TH_TOP                     # the Sovol top cover sits on the top hat's top band
UMB_START = (ROOF_XY[0], ROOF_XY[1], ROOF_Z - 66.0)
DOWN = np.array([0.0, 0.0, -1.0])

EI_TUBE, W_TUBE = 7400.0, 24.0          # PTFE 4 x 2 with filament; g/m
EI_UMB, W_UMB = 43200.0, 98.2           # Link cable + Beacon USB in loom + 1.4 mm piano wire (39600 for the wire, 12 g/m)
K_TUBE, K_UMB = 1.06, 1.07              # length: the farthest reach plus 6 % (tubes) or 7 % (umbilical)
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

def resample(P, step=4.0):
    P = np.asarray(P, float)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    u = np.linspace(0.0, s[-1], max(3, int(round(s[-1] / step)) + 1))
    return np.stack([np.interp(u, s, P[:, k]) for k in range(3)], axis=1)

def pipe(P, r, step=6.0):
    """Tube of radius r along the points P, as a compound of short cylinders (resampled every 6 mm). B-spline sweeps of
    these 3D paths often fail in OCC, and the ones that work carry bounding boxes metres too big."""
    Q = resample(P, step)
    sols = []
    for a, b in zip(Q[:-1], Q[1:]):
        d = b - a
        if np.linalg.norm(d) > 1e-6:
            sols.append(Part.makeCylinder(r, float(np.linalg.norm(d)), V(*a), V(*d)))
    return Part.makeCompound(sols)

def total_bend(X):
    """Total turning of a polyline in degrees (the capstan angle for friction)."""
    d = np.diff(np.asarray(X, float), axis=0); d /= np.linalg.norm(d, axis=1)[:, None]
    return float(np.degrees(np.arccos(np.clip((d[:-1] * d[1:]).sum(axis=1), -1.0, 1.0))).sum())

# ---------------------------------------------------------------- motor chains: shape at a gantry offset
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
    return [(f'cable chain {name}', 'purchased', chain_solid(s, CHAIN_R, Ym, dz), 'chains')
            for s, L in CHAINS.items() for name, Ym in L]

# ---------------------------------------------------------------- motor chain fittings
def moving_bracket(s, Ym):
    """On the side beam's top outer slot (M5 T-nut), over the gap: holds the chain's end link (2 x M3 into the link's
    holes; check the chain) at Z_M; the motor cable comes straight up and inboard through a slot."""
    x0, x1 = s * (TOP_SLOT_X - 6.0), s * (GAP_XC + CH_W / 2 + 0.5)
    b = fuse([box(x0, x1, Ym - 7.0, Ym + 7.0, BEAM_TOP, BEAM_TOP + 7.0),
              box(s * (GAP_XC - CH_W / 2 - 0.25), x1, Ym - 7.0, Ym + 7.0, Z_M, BEAM_TOP + 7.0)])
    holes = [cylz(2.75, BEAM_TOP - 1.0, BEAM_TOP + 8.0, s * TOP_SLOT_X, Ym)]
    for dy in (-3.0, 3.0):                                    # end-link screws, up from below
        holes.append(cylz(1.6, Z_M - 0.5, Z_M + 6.0, s * GAP_XC, Ym + dy))
    holes.append(box(s * (GAP_XC - 4.0), s * (GAP_XC + 4.0), Ym - 3.5, Ym + 3.5, Z_M - 1.0, BEAM_TOP + 8.0))
    return cut(b, holes).removeSplitter()

def entry_path(s, Yf):
    """Outside -> through the side panel -> down into a chain's fixed end. Built from the chain upward: leaves up,
    curves outward and crosses the panel 30 deg from vertical."""
    d = np.array([s * math.sin(math.radians(30.0)), 0.0, math.cos(math.radians(30.0))])
    P3 = np.array([s * (FACE + PANEL_T + 14.0), Yf, F_Z + 62.0])
    return bez((s * GAP_XC, Yf, F_Z), (0, 0, 1), P3, d, 26.0, 20.0)

def fixed_anchor(s, Yf):
    """Inside the gap: a block holding the chain's fixed end link, through-bolted to the outside plate (2 x M3 through
    the side panel). Outside: a cable slot with a zip-tie bar, on the 30 deg entry line."""
    xi0, xi1 = s * (GAP_XC - CH_W / 2 - 0.25), s * FACE
    inside = box(xi0, xi1, Yf - 8.0, Yf + 8.0, F_Z, F_Z + 34.0)
    xo0, xo1 = s * (FACE + PANEL_T), s * (FACE + PANEL_T + 8.0)
    outside = box(xo0, xo1, Yf - 14.0, Yf + 14.0, F_Z + 4.0, F_Z + 78.0)
    holes = [pipe(entry_path(s, Yf), 4.2)]
    for dy in (-3.0, 3.0):
        holes.append(cylz(1.6, F_Z - 0.5, F_Z + 6.0, s * GAP_XC, Yf + dy))
    for dy, zz in ((-5.5, F_Z + 8.0), (5.5, F_Z + 26.0)):     # 2 x M3 through the panel, beside the cable's passage
        holes.append(cylx(1.7, s * (GAP_XC - 7.0), s * (FACE + PANEL_T + 9.0), Yf + dy, zz))
    inside, outside = cut(inside, holes).removeSplitter(), cut(outside, holes).removeSplitter()
    return inside, outside

# ---------------------------------------------------------------- PTFE wall couplers
def cpl_axis(line):
    """Where the coupler axis crosses the wall's outer face, and its direction (inboard, CPL_TILT down)."""
    s, y = CPL_Y[line]; t = math.radians(CPL_TILT)
    return np.array([s * ENC.OUT_X, y, CPL_Z]), np.array([-s * math.cos(t), 0.0, -math.sin(t)])

def tube_start(line):
    P0, d = cpl_axis(line)
    return P0 + (SEAT + BODY) * d, d

def coupler_pad(line):
    """Pad on the inside of the top hat's side wall (part of the side piece): 22 mm wide, its seat square to the coupler
    axis, its underside at 45 deg so it prints upright with the wall. The PC4-M10 threads into an 8.5 mm hole (tap M10 x 1
    or let the coupler cut its own thread) from inside; the tube passes through the coupler and out through the wall.
    Returns (pad, holes)."""
    s, y = CPL_Y[line]; t = math.radians(CPL_TILT)
    S = (SEAT * math.cos(t), CPL_Z - SEAT * math.sin(t))                  # seat centre (u inboard from the outer face, z)
    p = (math.sin(t), math.cos(t))                                         # along the seat face, up
    B = (S[0] + 9.0 * p[0], S[1] + 9.0 * p[1]); C = (S[0] - 9.0 * p[0], S[1] - 9.0 * p[1])
    prof = [(0.0, CPL_Z + 14.0), B, C, (0.0, C[1] - C[0]), (0.0, CPL_Z + 14.0)]
    g = lambda u, z: V(s * (ENC.OUT_X - u), y - 11.0, z)
    pad = Part.Face(Part.makePolygon([g(u, z) for u, z in prof])).extrude(V(0, 22.0, 0))
    P0, d = cpl_axis(line); Sg = P0 + SEAT * d
    holes = [Part.makeCylinder(4.25, 11.0, V(*(Sg + 1.0 * d)), V(*(-d))),       # M10 x 1, 10 mm deep from the seat
             Part.makeCylinder(2.3, SEAT + 8.0, V(*(P0 - 6.0 * d)), V(*d))]      # tube passage out through the wall
    return pad, holes

def coupler_body(line):
    """PC4-M10 coupler envelope: hex and collet from the seat inward."""
    P0, d = cpl_axis(line)
    return Part.makeCylinder(8.0, BODY, V(*(P0 + SEAT * d)), V(*d))

# ---------------------------------------------------------------- umbilical clamp under the centre of the top cover
def roof_clamp():
    """Under the centre of the Sovol top cover, bolted through it (4 x M3; drill the cover 3.4 mm with the plate as the
    template, and 16 mm in the middle for the cables). The loom comes down a 13.6 mm bore in a round stalk 64 mm long,
    28 mm across, its lower edge rounded (6 mm), so a tube arching past it at full height slides off instead of catching
    on a corner; the plate's corners are rounded too. The 1.4 mm piano wire sits in a blind 1.6 mm bore beside the loom,
    held by an M3 set screw in a heat-set insert. The Link Board and the USB hub sit on top of the cover."""
    x, y = ROOF_XY; z = ROOF_Z
    plate = Part.makeBox(64.0, 64.0, 5.0, V(x - 32.0, y - 32.0, z - 5.0))
    plate = plate.makeFillet(6.0, [e for e in plate.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 4.0])
    stalk = Part.makeCylinder(14.0, 60.0, V(x, y, z - 64.0))
    stalk = stalk.makeFillet(6.0, [e for e in stalk.Edges if abs(e.BoundBox.ZMax - (z - 64.0)) < 1e-6 and e.BoundBox.ZLength < 1e-6])
    b = fuse([plate, stalk])                                                         # plate under the cover, round stalk
    holes = [cylz(6.8, z - 65.0, z + 1.0, x, y),                                    # loom
             cylz(0.8, z - 65.0, z - 8.0, x + 10.0, y),                             # piano wire, blind
             cylx(2.0, x + 10.0, x + 15.0, y, z - 30.0)]                            # M3 insert + set screw onto the wire
    holes += [cylz(1.7, z - 6.0, z + 1.0, x + sx * 24.0, y + sy * 24.0) for sx in (-1, 1) for sy in (-1, 1)]
    return cut(b, holes).removeSplitter()

def head_clamp(xn, y_xb):
    """Umbilical end on the head: a saddle that clips over the INDX PCB cover (X +-25.6, top Z 234 at the pose; fix it
    with VHB tape or Bondtech's own strain relief - check on the real head). Its lips stop at Z 226, above the XY joints
    (top Z 223.5), so the head still reaches both ends of X. The piano wire enters a 1.6 mm bore in a boss from above and
    is held by an M3 set screw; the loom is zip-tied to the boss."""
    x0, y0 = xn + UMB_HEAD[0], y_xb + UMB_HEAD[1]
    plate = box(x0 - 27.4, x0 + 27.4, y_xb + 12.0, y_xb + 37.5, 234.2, 238.0)        # the head body starts at Y_XB + 38
    lips = [box(x0 + sx * 25.8, x0 + sx * 27.4, y_xb + 16.0, y_xb + 36.0, 226.0, 238.0) for sx in (-1, 1)]
    boss = box(x0 - 6.0, x0 + 6.0, y0 - 6.0, y0 + 6.0, 238.0, UMB_HEAD[2])
    b = fuse([plate, boss] + lips)
    holes = [cylz(0.8, 240.0, UMB_HEAD[2] + 1.0, x0, y0), Part.makeCylinder(1.6, 8.0, V(x0 - 7.0, y0, 246.0), V(1, 0, 0)),
             box(x0 - 7.0, x0 + 7.0, y0 - 2.0, y0 + 2.0, 241.0, 243.5)]                # set screw, zip tie
    return cut(b, holes).removeSplitter()

# ---------------------------------------------------------------- free tubes and the umbilical (elastic rods)
def tool_end(x, y_xb, parked, dz=0.0):
    return np.array([x, y_xb + 66.45, (TOOL_TOP['parked'] if parked else TOOL_TOP['head']) + 12.0 + dz])

def umb_end(xn, y_xb, dz=0.0):
    return np.array([xn + UMB_HEAD[0], y_xb + UMB_HEAD[1], UMB_HEAD[2] + 12.0 + dz])

def line_start(line):
    return (np.array(UMB_START), DOWN) if line == 'umb' else tube_start(line)

_BED = [(x, y) for x in (-252.0, -126.0, 0.0, 126.0, 252.0) for y in (64.4, 190.0, 314.0, 440.0, 563.5)]
def line_length(line):
    """Long enough for the line's farthest reach (any bed position or its own dock, any gantry height) plus K_*."""
    A = line_start(line)[0]
    pts = []
    for dz in (-GANTRY_DROP, GANTRY_RISE):
        if line == 'umb':
            pts += [umb_end(x, y - NOZZLE_DY, dz) for x, y in _BED] + [umb_end(d, Y_XB_DOCK, dz) for d in DOCK_X]
        else:
            pts += [tool_end(x, y - NOZZLE_DY, False, dz) for x, y in _BED] + [tool_end(DOCK_X[TOOL_DOCK[line]], Y_XB_DOCK, True, dz)]
    return (K_UMB if line == 'umb' else K_TUBE) * max(float(np.linalg.norm(p - A)) for p in pts)

_LEN = {}
def line_nodes(line, end):
    """Shape of a tube (or the umbilical) from its coupler (clamp) to a tool (the head), as an elastic rod. A planar or
    symmetric start can stall: retry from guesses bowed sideways."""
    if line not in _LEN:
        _LEN[line] = line_length(line)
    ei, w = (EI_UMB, W_UMB) if line == 'umb' else (EI_TUBE, W_TUBE)
    A, d = line_start(line)
    X, ok = EL.solve(A, d, end, DOWN, _LEN[line], ei, w)
    for bow in ((30.0, 0.0, 0.0), (0.0, 30.0, 0.0), (-30.0, 0.0, 0.0), (0.0, -30.0, 0.0), (40.0, 40.0, 0.0), (0.0, 80.0, 20.0), (80.0, 0.0, 20.0)):
        if ok:
            break
        X0 = EL._initial(A, d, end, DOWN, _LEN[line], 36)
        X0[2:-2] += np.outer(np.sin(np.linspace(0.0, math.pi, len(X0) - 4)), bow)
        X, ok = EL.solve(A, d, end, DOWN, _LEN[line], ei, w, X0=X0)
    return X, ok

def line_solid(X, line):
    if line == 'umb':
        return pipe(X, 6.0)
    return pipe(np.vstack([X, X[-1] + np.array([0.0, 0.0, -10.0])]), 2.0)

def line_parts(xn, y_xb, active='t2', dz=0.0):
    """Tubes and umbilical for a head position: the active tool's tube and the umbilical to the head, the others to their
    docks (the model shows a tool in every dock; the active tool's dock has no tube)."""
    out = []
    for line, k in TOOL_DOCK.items():
        end = tool_end(xn, y_xb, False, dz) if line == active else tool_end(DOCK_X[k], Y_XB_DOCK, True, dz)
        X, ok = line_nodes(line, end)
        out.append((f'ptfe tube {line}' + (' active' if line == active else ''), 'purchased', line_solid(X, line), 'tubes'))
    X, ok = line_nodes('umb', umb_end(xn, y_xb, dz))
    out.append(('umbilical', 'purchased', line_solid(X, 'umb'), 'tubes'))
    return out

# ---------------------------------------------------------------- everything fixed to the frame, the gantry or the cover
def routing_parts():
    out = []
    for s, L in CHAINS.items():
        for name, Ym in L:
            ins, outs = fixed_anchor(s, Ym + 2 * CHAIN_R)
            out.append((f'chain anchor {name}', 'pps-cf', ins, 'enclosure'))
            out.append((f'chain entry {name}', 'pps-cf', outs, 'enclosure'))
            out.append((f'chain bracket {name}', 'pps-cf', moving_bracket(s, Ym), 'frame'))
    for line in CPL_Y:
        out.append((f'ptfe wall coupler {line}', 'purchased', coupler_body(line), 'enclosure'))
    out.append(('umbilical roof clamp', 'pps-cf', roof_clamp(), 'enclosure'))
    return out
