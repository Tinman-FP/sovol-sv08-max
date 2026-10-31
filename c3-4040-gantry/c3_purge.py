"""C3 purge and wipe: five wiper stations, one beside each tool's dock, the station bar that carries them, and one
slide-out purge tray on the chamber floor that runs under all five.

Why it is laid out this way (measured in Sovol's model and the C3 build, stock-pose frame):
* The PEI sheet's front edge is at Y 572 across the middle (X -198..188); two corner tabs reach Y 584. The nozzle's
  furthest forward point is Y 571.0 (the Y rail end at the docking pose), so it never gets past the sheet edge.
  A purge or wipe catcher therefore has to sit under the nozzle over the sheet's front lip, and it rides on the gantry.
* At the first layer the nozzle is 0.2 mm above the PEI, so anything under the nozzle tip over the sheet must get out
  of the way: each station's slider rests on the sheet and rises on two dowel pins (up to 10.8 mm) when the gantry
  is within about 9 mm of the bed. Station wipes are skipped below Z 12 (prime tower only); see the macro notes.
* One station per tool (owner, 2026-10-31): dock, station, dock, station... at a 78 mm pitch. Each station is 42 mm
  on the +X side of its tool's dock and 36 mm from the next dock. The head driving into a lane needs 34.1 mm (+X) /
  40.2 mm (-X) from a dock with its parked tool and 35.0 / 32.4 mm from a station slider lifted for the first layer
  (surface-sampled sweep, c3_lanecheck.py). The stations' brackets must stay inside the PEI's middle zone
  (X -198..188); the row is centred to leave 7 mm at each end. This way round (docks on the -X side) the slicer's
  front strip is narrower than with the docks on the +X side (about 424 mm against 450).
* The station bar is a 1515 in front of the sheet (Y 586..601, clear of the corner tabs) and below the nozzle tip
  (Z tip-13..tip+2, under the head's lowest parts), held by two printed clips on the front cradles' inner webs.

Wiper pad: Qidi Plus 4 / Q2 silicone wiper, 27 x 15 x 4.7 mm high, laid 27 mm across X and glued into the slider
pocket with high-temperature RTV. Its top stands 1.2 mm above the nozzle tip; the nozzle drags across its 15 mm in Y
(station purge position Y 571.0, wipe back to Y 548.7, 3.5 mm past the pad).

Gantry parts go into c3_build with group 'docks' (they ride on the gantry); the trays are frame-fixed ('enclosure').
c3_purgecheck.py checks the lift, the station and wipe poses and the purge trays.
"""
import FreeCAD as App, Part
from c3_params import DOCK_X, Y_XB_DOCK, ZB, BED_TOP, GANTRY_DROP
V = App.Vector

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def rbox(x0, x1, y0, y1, z0, z1, r=1.5):
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
def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()
def cut(s, tools):
    for t in tools:
        s = s.cut(t)
    return s
def prism_yz(pts, x0, x1):
    """Closed Y-Z polygon extruded along X from x0 to x1."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, *pts[0])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))

M3_CLR, M3_INSERT, M3_CB = 1.7, 2.0, 3.0
ZN = ZB + 10.0 - 8.5 - 31.5                 # nozzle tip Z in the build pose (127.0); c3_build.NOZZLE_Z
NOZ_Y = Y_XB_DOCK + 66.7                    # nozzle centre at the docking / station Y (571.0)
PEI_EDGE = 572.0                            # PEI front edge, X -198..188
ST_X = tuple(x + 42.0 for x in DOCK_X)       # station centres (-161, -83, -5, 73, 151), tool k's station beside dock k

# station bar (1515, same profile as the dock rail) and its cradle clips
BAR = dict(y=(586.0, 601.0), z=(ZN - 13.0, ZN + 2.0), x=283.0)
WEB_FACE = 286.5                            # front cradle inner web, inboard face |X| (c3_build.WEB_I)
CLIP_SCREWS = ((589.5, ZN - 8.5), (589.5, ZN - 1.5))   # countersunk M3 into short inserts in the web

# station geometry (x relative to the station centre)
PIN_X, PIN_Y = 23.0, 578.5                  # 3 x 20 mm dowel pins, vertical
LUG_B, LUG_T = (ZN - 19.0, ZN - 16.0), (ZN - 1.5, ZN + 2.0)
LUG_X, LUG_Y = (18.5, 30.0), (575.0, 582.0)
STOP_X = 27.5                               # M3 set screw (rest height adjust) in the bottom lug
BUSH_R, BUSH_H = 3.2, 3.5
REST_Z = LUG_B[1] + 0.2                     # slider bushings sit 0.2 mm above the bottom lug (on the set screws)
TRAVEL = LUG_T[0] - (REST_Z + BUSH_H)       # 10.8 mm
PAD = dict(x=13.5, y=(552.2, 567.2), z=(ZN - 3.5, ZN + 1.2))          # Qidi Plus 4 wiper, 27 x 15 x 4.7
FOOT_Z = ZN - 9.3                           # lowest slider point over the sheet (rests on the PEI at low gantry)
CHUTE_TOP = ((567.2, ZN - 7.0), (PEI_EDGE, ZN - 7.5), (577.0, ZN - 14.6))   # floor top; the purge drops 7 mm
CHUTE_T, CHUTE_W = 1.5, 10.3                # floor thickness, inner half width
WIPE_Y = (NOZ_Y, PAD['y'][0] - 3.5)         # wipe stroke (nozzle Y), back to 548.7
POCKET_Y0 = PAD['y'][0] - 1.5               # rear face of the pad pocket and cheeks (550.7)

# purge trays on the chamber floor (floor top Z -70.7; bed cover plates end at Y 571)
FLOOR_Z = -70.7
TRAY = dict(y=(572.5, 616.0), z=(FLOOR_Z + 1.7, ZN - 19.0 - GANTRY_DROP - 1.5), w=48.0, wall=1.8)


def station_bar():
    return box(-BAR['x'], BAR['x'], BAR['y'][0], BAR['y'][1], BAR['z'][0], BAR['z'][1])

def bar_clip(s_):
    """U channel under the bar end, end plate on the cradle's inner web (2 countersunk M3), M3 up into the bar's bottom
    slot. x<0 geometry, mirrored for x>0. Prints floor down."""
    y0, y1 = BAR['y'][0] - 2.0, BAR['y'][1] + 2.0
    z0, z1 = BAR['z'][0] - 2.0, BAR['z'][1]
    plate = box(-WEB_FACE, -BAR['x'], y0, y1, z0, z1)
    floor_ = box(-BAR['x'] - 0.01, -BAR['x'] + 15.0, y0, y1, z0, BAR['z'][0])
    walls = [box(-BAR['x'] - 0.01, -BAR['x'] + 15.0, y0, BAR['y'][0], z0, z1),
             box(-BAR['x'] - 0.01, -BAR['x'] + 15.0, BAR['y'][1], y1, z0, z1)]
    c = fuse([plate, floor_] + walls)
    holes = []
    for y, z in CLIP_SCREWS:
        holes.append(cylx(M3_CLR, -WEB_FACE - 0.5, -BAR['x'] + 0.5, y, z))
        holes.append(Part.makeCone(M3_CLR, 3.2, 1.6, V(-BAR['x'] - 1.6, y, z), V(1, 0, 0)))   # 90 deg countersink, inner face
    xb = -BAR['x'] + 7.5; yb = sum(BAR['y']) / 2
    holes.append(cyl(M3_CLR, z0 - 0.5, BAR['z'][0] + 0.5, xb, yb))
    c = cut(c, holes)
    return c.mirror(V(0, 0, 0), V(1, 0, 0)) if s_ > 0 else c

def cradle_insert_holes(s_):
    """Two short M3 heat-set insert pockets in the front cradle's inner web for the bar clip (cut by c3_build)."""
    hs = [cylx(M3_INSERT, -WEB_FACE - 4.6, -WEB_FACE + 0.1, y, z) for y, z in CLIP_SCREWS]
    return [h.mirror(V(0, 0, 0), V(1, 0, 0)) for h in hs] if s_ > 0 else hs

def station_bracket(xs):
    """Fixed: back plate on the bar's rear face (2 x M3 + T-nuts), two pin frames (top and bottom lugs) at x +-23,
    M3 set screws tapped into the bottom lugs set the rest height. Everything stays at Y >= 575 (in front of the PEI edge) and
    below Z tip+2. Prints back-plate face down."""
    plate = rbox(xs - LUG_X[1], xs + LUG_X[1], LUG_Y[1], BAR['y'][0], LUG_B[0], BAR['z'][1], 1.5)
    lugs = []
    for sx in (-1, 1):
        x0, x1 = sorted((xs + sx * LUG_X[0], xs + sx * LUG_X[1]))
        lugs += [box(x0, x1, LUG_Y[0], LUG_Y[1] + 0.01, LUG_B[0], LUG_B[1]), box(x0, x1, LUG_Y[0], LUG_Y[1] + 0.01, LUG_T[0], LUG_T[1])]
    b = fuse([plate] + lugs)
    holes = []
    for sx in (-1, 1):
        holes.append(cyl(1.5, LUG_B[0] - 0.5, LUG_B[1] + 0.5, xs + sx * PIN_X, PIN_Y))            # pin press fit (nominal; prints tight)
        holes.append(cyl(1.5, LUG_T[0] - 0.5, LUG_T[0] + 3.0, xs + sx * PIN_X, PIN_Y))            # blind, top lug
        holes.append(cyl(1.25, LUG_B[0] - 0.5, LUG_B[1] + 0.5, xs + sx * STOP_X, PIN_Y))          # M3 tap hole: rest-height set screw
        holes.append(cyly(M3_CLR, LUG_Y[1] - 0.5, BAR['y'][0] + 0.5, xs + sx * 13.0, sum(BAR['z']) / 2))   # to the bar slot
    return cut(b, holes)

def station_slider(xs, lift=0.0):
    """Moving: two bushings on the pins, risers in front of the PEI edge, a pad pocket and a short purge chute that
    reach back over the sheet's front lip. Its lowest point over the sheet is the foot under the pad (FOOT_Z).
    lift raises it along the pins (0 at rest, up to TRAVEL)."""
    parts = []
    for sx in (-1, 1):
        xp = xs + sx * PIN_X
        parts.append(cyl(BUSH_R, REST_Z, REST_Z + BUSH_H, xp, PIN_Y))
        x0, x1 = sorted((xs + sx * PIN_X, xs + sx * (STOP_X + 2.0)))
        parts.append(box(x0, x1, PIN_Y - 2.0, PIN_Y + 2.0, REST_Z, REST_Z + 1.8))                 # tab on the set screw
        x0, x1 = sorted((xs + sx * 14.5, xp))
        parts.append(box(x0, x1, 573.0, PIN_Y, REST_Z, REST_Z + BUSH_H))                          # link to the bushing
        x0, x1 = sorted((xs + sx * 12.0, xs + sx * 16.5))
        parts.append(box(x0, x1, 573.0, 575.0, REST_Z, ZN - 1.0))                                 # riser (stays at Y < 575)
        parts.append(box(x0, x1, POCKET_Y0, 575.0, ZN - 8.8, ZN - 1.0))                           # cheek (top flush with the walls: prints upside down)
    # pad pocket (pad glued in with RTV) and the foot under it
    pocket = box(xs - 16.5, xs + 16.5, POCKET_Y0, 568.6, PAD['z'][0] - 1.5, ZN - 1.0)
    foot = box(xs - 10.0, xs + 10.0, 557.0, 563.0, FOOT_Z, PAD['z'][0] - 1.4)
    try:
        foot = foot.makeFillet(1.5, [e for e in foot.Edges if abs(e.Vertexes[0].Point.z - FOOT_Z) < 1e-6 and abs(e.Vertexes[-1].Point.z - FOOT_Z) < 1e-6])
    except Exception:
        pass
    parts += [pocket, foot]
    # chute: floor polygon (Y, Z) and side walls up to tip-1 (wall bottoms follow the floor bottom)
    top = list(CHUTE_TOP); bot = [(y, z - CHUTE_T) for y, z in top]
    floor_ = prism_yz(top + bot[::-1], xs - CHUTE_W - 1.7, xs + CHUTE_W + 1.7)
    walls = []
    for sx in (-1, 1):
        x0, x1 = sorted((xs + sx * CHUTE_W, xs + sx * (CHUTE_W + 1.7)))
        walls.append(prism_yz(bot + [(bot[-1][0], ZN - 1.0), (bot[0][0], ZN - 1.0)], x0, x1))
    parts += [floor_] + walls
    s = fuse(parts)
    holes = [cyl(1.65, REST_Z - 0.5, REST_Z + BUSH_H + 0.5, xs + sx * PIN_X, PIN_Y) for sx in (-1, 1)]
    holes.append(box(xs - PAD['x'] - 0.15, xs + PAD['x'] + 0.15, PAD['y'][0] - 0.1, PAD['y'][1] + 0.1, PAD['z'][0], ZN + 5.0))
    holes += [cyl(1.5, PAD['z'][0] - 2.0, PAD['z'][0] + 0.1, xs + dx, sum(PAD['y']) / 2) for dx in (-8.0, 0.0, 8.0)]   # RTV keys
    s = cut(s, holes)
    if lift:
        s.translate(V(0, 0, lift))
    return s

def wiper_pad(xs, lift=0.0):
    s = box(xs - PAD['x'], xs + PAD['x'], PAD['y'][0], PAD['y'][1], PAD['z'][0], PAD['z'][1])
    if lift:
        s.translate(V(0, 0, lift))
    return s

TRAY_X = (ST_X[0] - TRAY['w'] / 2, ST_X[-1] + TRAY['w'] / 2)   # one tray under all five chutes, X -185..175 (360 mm)

def tray():
    """One open tray under all five stations (owner, 2026-10-31), the old trays' height and depth. It sits loose on 20 small
    feet, placed where the five single trays had theirs (clear of the floor's screw heads), and slides out through the door
    with no fasteners; two pull tabs. Longer than the Qidi bed: it prints diagonally, rim down."""
    w, t = TRAY['w'], TRAY['wall']; y0, y1 = TRAY['y']; z0, z1 = TRAY['z']; x0, x1 = TRAY_X
    outer = rbox(x0, x1, y0, y1, z0, z1, 3.0)
    inner = rbox(x0 + t, x1 - t, y0 + t, y1 - t, z0 + t, z1 + 1.0, 1.5)
    s = outer.cut(inner)
    feet = [box(x, x + 6.0, y, y + 6.0, FLOOR_Z + 0.05, z0 + 0.01)
            for xc in ST_X for x in (xc - w / 2 + 1.0, xc + w / 2 - 7.0) for y in (y0 + 1.0, 598.0)]   # front feet stop short of the floor screws (Y 606)
    pulls = [box(xp - 10.0, xp + 10.0, y1 - 0.01, y1 + 2.5, z1 - 2.0, z1) for xp in (x0 + (x1 - x0) / 4, x0 + 3 * (x1 - x0) / 4)]
    return fuse([s] + pulls + feet)

def purge_parts():
    """(name, material, shape, group) for c3_build."""
    out = [('station bar 1515 566', 'al-6063 1515', station_bar(), 'docks')]
    for s_, tag in ((-1, 'xn'), (1, 'xp')):
        out.append((f'station bar clip {tag}', 'pps-cf', bar_clip(s_), 'docks'))
    for k, xs in enumerate(ST_X, 1):
        tag = f't{k}'
        out.append((f'wiper station bracket {tag}', 'pps-cf', station_bracket(xs), 'docks'))
        out.append((f'wiper station slider {tag}', 'pps-cf', station_slider(xs), 'docks'))
        out.append((f'silicone wiper pad {tag} qidi plus4', 'purchased', wiper_pad(xs), 'docks'))
        for sx in (-1, 1):
            out.append((f'dowel pin 3x20 {tag} {sx:+d}', 'steel', cyl(1.5, LUG_B[0] + 0.5, LUG_B[0] + 20.5, xs + sx * PIN_X, PIN_Y), 'docks'))
    out.append(('purge tray', 'pps-cf', tray(), 'enclosure'))
    return out
