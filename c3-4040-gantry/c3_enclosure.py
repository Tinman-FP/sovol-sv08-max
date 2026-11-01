"""C3 frame-fixed parts: the stock camera on a fixed front-right mount, and the top hat (sectional walls, iPistBit 7 inch
display, the owner's Sovol top cover moved up onto it, a PG9 gland in the rear wall). The PTFE tubes, cable chains, harness,
rear mast and piano-wire arcs are in c3_routing.py (2026-11-01); the top hat is 195 mm tall to clear the arcs.

Everything here is fixed to the printer frame (it does not ride on the gantry) and goes into c3_build's parts list
with group 'enclosure'; c3_check sweeps the whole gantry against it.
Frame: Sovol's model in the stock gantry pose, as c3_params. The stock frame top is at Z 591.3; its top band is 7.5 mm
of sheet metal (sides |X| 347..354.5, front Y 614.5..622, rear Y -75..-57), with an inner lip on the front profile
(Y 604..616, Z 584.9..587.3).
"""
import math, json
import FreeCAD as App, Part
V = App.Vector

# ---------------------------------------------------------------- shared helpers (same conventions as c3_build)
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def cyl(r, z0, z1, x, y):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))
def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()

FRAME_TOP = 591.3
OUT_X, OUT_Y = 354.5, (-75.0, 622.0)           # frame outer faces (top hat outer faces are flush with them)

# ---------------------------------------------------------------- camera: stock housing on a clip over the front lip
CAM_LENS_OLD = (V(-309.6, 563.8, 141.1), V(0.99, -0.16, 0.0))     # lens centre and axis in the stock (old gantry) pose
CAM_LENS_NEW = V(-276.0, 584.0, 546.0)                            # below the front profile lip, front-right, clear of the LED bar
CAM_TARGET = V(-5.0, 312.0, -36.7)                                # bed centre
LIP = dict(y=(604.0, 616.0), z=(584.9, 587.3))

def _frame(a, up):
    a = V(a).normalize(); c = V(up) - a * (V(up).dot(a)); c.normalize(); b = c.cross(a)
    return a, b, c

def camera_placement():
    """Rigid placement taking the stock camera housing from the old gantry pose to the fixed mount, lens on the bed centre."""
    a0, b0, c0 = _frame(CAM_LENS_OLD[1], V(0, 0, 1))
    a1, b1, c1 = _frame(CAM_TARGET - CAM_LENS_NEW, V(0, 0, 1))
    M0 = App.Matrix(a0.x, b0.x, c0.x, 0, a0.y, b0.y, c0.y, 0, a0.z, b0.z, c0.z, 0, 0, 0, 0, 1)
    M1 = App.Matrix(a1.x, b1.x, c1.x, 0, a1.y, b1.y, c1.y, 0, a1.z, b1.z, c1.z, 0, 0, 0, 0, 1)
    R = M1.multiply(M0.inverse())
    p = R.multVec(CAM_LENS_OLD[0]); R.move(CAM_LENS_NEW - p)
    return R, (a1, b1, c1)

def camera_parts(stock_camera):
    """stock_camera: list of (label, shape) of Sovol's camera kit in the stock pose. Returns parts in the new pose:
    the housing (purchased, reused) and one printed mount: a clip over the front profile lip with an M3 pinch screw,
    an arm, and a cup that holds the back of the housing (two zip-tie slots)."""
    R, (a, b, c) = camera_placement()
    out = []
    housing = []
    for lab, s in stock_camera:
        t = s.copy(); t = t.transformGeometry(R); housing.append(t)
        out.append(('camera stock ' + lab[:30], 'purchased', t, 'enclosure'))
    # cup: in the camera's local frame (a: lens axis, b, c), around the housing's local bounding box
    def local(p):
        d = p - CAM_LENS_NEW; return (d.dot(a), d.dot(b), d.dot(c))
    pts = [local(v.Point) for h in housing for v in h.Vertexes]
    ua, ub = min(p[0] for p in pts), max(p[0] for p in pts)
    va, vb = min(p[1] for p in pts), max(p[1] for p in pts)
    wa, wb = min(p[2] for p in pts), max(p[2] for p in pts)
    def lbox(u0, u1, v0, v1, w0, w1):
        s = Part.makeBox(u1 - u0, v1 - v0, w1 - w0, V(u0, v0, w0))
        M = App.Matrix(a.x, b.x, c.x, 0, a.y, b.y, c.y, 0, a.z, b.z, c.z, 0, 0, 0, 0, 1); M.move(CAM_LENS_NEW)
        return s.transformGeometry(M)
    t = 2.5
    cup = lbox(ua - t, ua + 0.6 * (ub - ua), va - t, vb + t, wa - t, wb + t).cut(lbox(ua - 0.3, ub + 1, va - 0.3, vb + 0.3, wa - 0.3, wb + 0.3))
    for k in (0.2, 0.45):                                            # zip-tie slots across the cup
        uu = ua + k * (ub - ua)
        cup = cup.cut(lbox(uu, uu + 4.0, va - t - 1, vb + t + 1, wa - t - 1, wa - 0.2)).cut(lbox(uu, uu + 4.0, va - t - 1, vb + t + 1, wb + 0.2, wb + t + 1))
    # clip over the lip: top jaw, spine in front of the lip edge, lower jaw with an M3 heat-set insert (pinch screw up)
    x0, x1 = -294.0, -274.5                                         # free lip between the corner seat and the LED bar
    jaw_t = box(x0, x1, 600.0, 613.5, LIP['z'][1] + 0.2, LIP['z'][1] + 2.7)
    spine = box(x0, x1, 600.0, 603.6, 574.0, LIP['z'][1] + 2.7)
    jaw_b = box(x0, x1, 600.0, 613.5, 574.0, LIP['z'][0] - 0.2)
    cb = cup.BoundBox
    arm = box(x0, x1, 600.0, 603.6, min(cb.ZMin + 6.0, 574.0), 574.01)
    mount = fuse([jaw_t, spine, jaw_b, arm, cup]).cut(lbox(ua - 1.0, ub + 1, va - 1.0, vb + 1.0, wa - 1.0, wb + 1.0))   # housing envelope + 1 mm
    mount = mount.cut(cyl(2.0, 574.0 - 0.1, LIP['z'][0] - 0.2 + 0.1, (x0 + x1) / 2, 609.0))     # insert for the M3 pinch screw
    mount = mount.cut(cyl(1.7, 570.0, 574.1, (x0 + x1) / 2, 609.0))
    # the cup's pocket is the housing's own bounding box + 0.3 mm (Sovol's housing solids are not valid B-reps to cut with)
    if len(mount.Solids) > 1:
        mount = sorted(mount.Solids, key=lambda s: -s.Volume)[0]
    out.append(('camera mount front right', 'pps-cf', mount.removeSplitter(), 'enclosure'))
    return out

# ---------------------------------------------------------------- top hat
TH_H = 195.0                                   # clears the piano-wire arcs at full Z (was 136 until 2026-11-01; c3_routecheck.py)
TH_TOP = FRAME_TOP + TH_H
TH_D = 40.0                                    # wall depth (owner's 40 mm sections)
TOP_BAND = 7.5                                 # the top hat's top repeats the frame's 7.5 mm top band: the Sovol cover sits on it
TOP_CLEAR = 20.0                               # nothing else within 20 mm under the top surface (room for the cover's own edges)
TH_SKIN, TH_FOOT = 2.4, 7.5                    # outer skin; foot = width of the frame's top band
LID_T, LEDGE = 4.0, 20.0                       # lid sheet and the ledge it sits on (lid top flush with the walls)
RIB_PITCH = 62.0
PASS_Z = 666.0                                 # PG9 gland height in the rear wall
# joints: (run, coordinate along the run) for the 8 pieces: 4 corner Ls + 4 straights
CORNER_LEG = {'fr': 225.0, 'fl': 210.0, 'rr': 210.0, 'rl': 210.0}   # front-right carries the 7 inch display
DISPLAY = dict(w=165.5, h=125.0, depth=17.0, xc=-228.0)            # iPistBit 7 inch, about 165 x 125 x 15, glass flush

def _section_solid(length):
    """Wall cross-section extruded along +X from 0 to length; outer face at y=0, inside toward +y, z absolute."""
    z0, zt = FRAME_TOP, TH_TOP
    zp = zt - TOP_CLEAR
    parts = [box(0, length, 0, TH_SKIN, z0, zt),                               # outer skin
             box(0, length, 0, TH_FOOT, z0, z0 + 4.0),                         # foot on the frame band
             box(0, length, 0, TOP_BAND, zt - 4.0, zt)]                        # top band, as the frame's: the cover sits here
    # 45 deg plate from the skin up to the inner edge (prints upright without supports)
    p = Part.makePolygon([V(0, TH_SKIN, zp - (TH_D - TH_SKIN)), V(0, TH_D, zp), V(0, TH_D, zp - 4.2),
                          V(0, TH_SKIN, zp - (TH_D - TH_SKIN) - 4.2), V(0, TH_SKIN, zp - (TH_D - TH_SKIN))])
    parts.append(Part.Face(p).extrude(V(length, 0, 0)))
    return fuse(parts)

def _rib(x, extra=0.0):
    """Rib at x (3 mm thick along the run): 40 deep, 45 deg down to the foot width (gantry tops clear below), and only the
    top band's width in the top TOP_CLEAR mm."""
    z0, zt = FRAME_TOP + 4.0, TH_TOP
    zp = zt - TOP_CLEAR
    p = Part.makePolygon([V(0, TH_SKIN - 0.01, z0), V(0, TH_FOOT, z0), V(0, TH_D, z0 + (TH_D - TH_FOOT)), V(0, TH_D, zp),
                          V(0, TOP_BAND, zp), V(0, TOP_BAND, zt - 4.0), V(0, TH_SKIN - 0.01, zt - 4.0), V(0, TH_SKIN - 0.01, z0)])
    s = Part.Face(p).extrude(V(3.0 + extra, 0, 0)); s.translate(V(x, 0, 0)); return s

def _run(length, joints):
    """Straight wall run of the given length with ribs; 'joints' are positions that get paired end ribs."""
    s = _section_solid(length)
    n = max(1, int(round(length / RIB_PITCH)))
    ribs = [_rib(length * k / n - 1.5) for k in range(1, n)]
    return fuse([s] + ribs)

def _place(s, run):
    """Map a run built along +X (outer face y=0) to the printer frame. Runs go counter-clockwise seen from above."""
    t = s.copy()
    L = {'front': 2 * OUT_X, 'rear': 2 * OUT_X, 'xp': OUT_Y[1] - OUT_Y[0], 'xn': OUT_Y[1] - OUT_Y[0]}
    if run == 'front':      # outer face Y 622, inside -Y, along -X... built from x=-354.5 to +354.5
        t.rotate(V(0, 0, 0), V(0, 0, 1), 180); t.translate(V(OUT_X, OUT_Y[1], 0))
    elif run == 'rear':     # outer face Y -75, inside +Y
        t.translate(V(-OUT_X, OUT_Y[0], 0))
    elif run == 'xn':       # outer face X -354.5, inside +X, along -Y
        t.rotate(V(0, 0, 0), V(0, 0, 1), -90); t.translate(V(-OUT_X, OUT_Y[1], 0))
    elif run == 'xp':       # outer face X +354.5, inside -X, along +Y
        t.rotate(V(0, 0, 0), V(0, 0, 1), 90); t.translate(V(OUT_X, OUT_Y[0], 0))
    return t

def _miter_cut(run):
    """The two corner triangles each run loses to its 45 deg miters (a cut works where a common with a wedge does not)."""
    z0, z1 = FRAME_TOP - 1, TH_TOP + 1
    x, y0, y1 = OUT_X, OUT_Y[0], OUT_Y[1]; e, D = 2.0, TH_D + 2.0
    def tri(p, q, r):
        return Part.Face(Part.makePolygon([V(*p, z0), V(*q, z0), V(*r, z0), V(*p, z0)])).extrude(V(0, 0, z1 - z0))
    if run == 'front':
        return [tri((-x - e, y1 + e), (-x + D, y1 - D), (-x - e, y1 - D)), tri((x + e, y1 + e), (x - D, y1 - D), (x + e, y1 - D))]
    if run == 'rear':
        return [tri((-x - e, y0 - e), (-x + D, y0 + D), (-x - e, y0 + D)), tri((x + e, y0 - e), (x - D, y0 + D), (x + e, y0 + D))]
    if run == 'xn':
        return [tri((-x - e, y1 + e), (-x + D, y1 - D), (-x + D, y1 + e)), tri((-x - e, y0 - e), (-x + D, y0 + D), (-x + D, y0 - e))]
    return [tri((x + e, y1 + e), (x - D, y1 - D), (x - D, y1 + e)), tri((x + e, y0 - e), (x - D, y0 + D), (x - D, y0 - e))]

def top_hat_ring():
    runs = {}
    for run, L in (('front', 2 * OUT_X), ('rear', 2 * OUT_X), ('xn', OUT_Y[1] - OUT_Y[0]), ('xp', OUT_Y[1] - OUT_Y[0])):
        t = _place(_run(L, []), run)
        for tr in _miter_cut(run):
            t = t.cut(tr)
        runs[run] = t
    return fuse(list(runs.values()))

def _joints():
    """Joint planes between the 8 pieces: (axis, value, wall outer coordinate, inward sign)."""
    x, (y0, y1) = OUT_X, OUT_Y
    return [('x', -x + CORNER_LEG['fr'], y1, -1), ('x', x - CORNER_LEG['fl'], y1, -1),     # front run
            ('x', -x + CORNER_LEG['rr'], y0, +1), ('x', x - CORNER_LEG['rl'], y0, +1),     # rear run
            ('y', y1 - CORNER_LEG['fr'], -x, +1), ('y', y0 + CORNER_LEG['rr'], -x, +1),    # xn (right) run
            ('y', y1 - CORNER_LEG['fl'], x, -1), ('y', y0 + CORNER_LEG['rl'], x, -1)]      # xp (left) run

def top_hat_parts():
    """Eight printed wall pieces (four corner Ls, four straights), each with 3 mm end ribs at its joints and two M3 bolts
    through each pair of end ribs. Prints upright (as installed) without supports."""
    ring = top_hat_ring()
    z0, zt = FRAME_TOP, TH_TOP
    x, (y0, y1) = OUT_X, OUT_Y
    J = _joints()
    adds, holes = [], []
    zr, zp = z0 + 4.0, zt - TOP_CLEAR
    prof = [(TH_SKIN - 0.01, zr), (TH_FOOT, zr), (TH_D, zr + (TH_D - TH_FOOT)), (TH_D, zp), (TH_SKIN - 0.01, zp), (TH_SKIN - 0.01, zr)]
    for ax, v, w, inward in J:                    # end ribs cut back at 45 deg like the others (gantry parts pass close below)
        for lo, hi in ((v - 3.0, v), (v, v + 3.0)):
            if ax == 'x':
                f = Part.Face(Part.makePolygon([V(lo, w + inward * d, z) for d, z in prof])); adds.append(f.extrude(V(hi - lo, 0, 0)))
            else:
                f = Part.Face(Part.makePolygon([V(w + inward * d, lo, z) for d, z in prof])); adds.append(f.extrude(V(0, hi - lo, 0)))
        for zz in (z0 + 30.0, zt - 40.0):
            if ax == 'x':
                holes.append(Part.makeCylinder(1.7, 12.0, V(v - 6.0, w + inward * 22.0, zz), V(1, 0, 0)))
            else:
                holes.append(Part.makeCylinder(1.7, 12.0, V(w + inward * 22.0, v - 6.0, zz), V(0, 1, 0)))
    ring = fuse([ring] + adds)
    # 7 inch display in the front-right corner (x<0 is the printer's right): glass flush with the front skin
    dz0 = z0 + 2.5; dz1 = dz0 + DISPLAY['h']
    dx0, dx1 = DISPLAY['xc'] - DISPLAY['w'] / 2, DISPLAY['xc'] + DISPLAY['w'] / 2
    ring = ring.cut(box(dx0 - 6.0, dx1 + 6.0, y1 - TH_D, y1 - TH_SKIN, z0 + 4.0, zt - 4.0))           # local: no 45 deg plate or ribs
    ring = ring.fuse(box(dx0 - 6.0, dx1 + 6.0, y1 - DISPLAY['depth'] - 4.0, y1, z0, zt - 4.0))         # frame around the module
    ring = ring.cut(box(dx0, dx1, y1 - DISPLAY['depth'], y1 + 1, dz0, dz1))
    for xx in (dx0 - 3.0, dx1 + 3.0):                                  # M3 heat-set inserts for the rear retainer clips
        for zz in (dz0 + 15.0, dz1 - 15.0):
            ring = ring.cut(Part.makeCylinder(2.0, 6.0, V(xx, y1 - DISPLAY['depth'] - 4.01, zz), V(0, 1, 0)))
    ring = ring.cut(box(dx0 + 20.0, dx1 - 20.0, y1 - DISPLAY['depth'] - 4.5, y1 - DISPLAY['depth'] + 0.1, dz0 + 10.0, dz1 - 10.0))   # cable window
    # a PG9 gland in the rear wall for the display and other cables (tubes and head cables reach the gantry through the
    # side-gap chains: c3_routing)
    pz = PASS_Z
    blk = box(-34.0, -8.0, y0, y0 + 22.0, pz - 16.0, pz + 16.0)
    ring = ring.fuse(blk)
    ring = ring.cut(Part.makeCylinder(7.7, 30.0, V(-20.0, y0 - 1.0, pz), V(0, 1, 0)))
    ring = ring.cut(Part.makeCompound(holes))
    xf = sorted(j[1] for j in J[0:2]); xr = sorted(j[1] for j in J[2:4]); yn = sorted(j[1] for j in J[4:6]); yp = sorted(j[1] for j in J[6:8])
    regions = {
        'top hat corner front right display': box(-1000, xf[0], yn[1], 2000, 0, 1000),
        'top hat corner front left': box(xf[1], 1000, yp[1], 2000, 0, 1000),
        'top hat corner rear right': box(-1000, xr[0], -1000, yn[0], 0, 1000),
        'top hat corner rear left': box(xr[1], 1000, -1000, yp[0], 0, 1000),
        'top hat front': box(xf[0], xf[1], 300, 2000, 0, 1000),
        'top hat rear': box(xr[0], xr[1], -1000, 300, 0, 1000),
        'top hat side right': box(-1000, 0, yn[0], yn[1], 0, 1000),
        'top hat side left': box(0, 1000, yp[0], yp[1], 0, 1000),
    }
    return [(name, 'asa', ring.common(reg).removeSplitter(), 'enclosure') for name, reg in regions.items()]

def umbilical_parts():
    """Cable chains, harness, rear mast and the fixed chain anchors: c3_routing.py (2026-11-01). Until then the top hat
    held a 2020 spine with the head cables' drop ring and the PTFE guides, fed by weighted loops outside."""
    import c3_routing as RT
    return RT.routing_parts()
