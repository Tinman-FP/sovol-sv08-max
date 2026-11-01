"""C3 routing check (run with FreeCAD's Python after c3_build.py): the parts that change shape or move with the head.

c3_check.py covers the routing parts fixed to the frame or the gantry (chain anchors and entries, chain brackets,
harness, posts, rear mast, Link Board) at its seven poses and over the Z sweep. This script adds:
1. Chains: each chain's shape at 13 gantry heights from the first layer to 500 mm print height, against the gantry
   (three bridge positions) and the fixed frame, top hat and anchors. Its own anchor and bracket are skipped.
2. Harness and mast against the head and bridge at a grid of head positions (the rear run passes over the head's
   rearmost reach).
3. Piano-wire arcs, solved as elastic rods (c3_elastica): for each tool on the head in turn, at 12 bed positions and its
   own docking pose, the active tube, the umbilical and the four parked tubes against the gantry, the parked tools and
   the head; at 500 mm print height against the top hat and the frame top. Each arc's first and last 15 mm (its clamp
   and its tool or head clamp) are left out. Tube-on-tube gaps are reported, not counted as clashes: the arcs cross.
Writes c3/C3_ROUTE_CHECK.json.
"""
import sys, os, re, json, math
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part
import numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0'); os.environ['C3_ARCS'] = '0'
import c3_build as B
import c3_routing as RT
from c3_params import *
V = App.Vector
TOL = 0.2

def tight(s):
    try:
        return s.optimalBoundingBox()
    except Exception:
        return s.BoundBox

def hits(a, items, skip=lambda n: False):
    out = []
    ab = tight(a)
    for n, t in items:
        if skip(n) or not ab.intersect(t.BoundBox):
            continue
        try:
            v = a.common(t).Volume
        except Exception:
            v = -1.0
        if v > TOL or v < 0:
            out.append((round(v, 2), n))
    return out

# fixed stock frame, as c3_check (removed: drag chain plate, camera, filament guide, spool holder)
labels = json.loads((B.STOCK_CACHE / 'stock_keep_labels.json').read_text()); kids = Part.read(str(B.STOCK_CACHE / 'stock_keep.brep')).childShapes()
STOCK = []
for (l, k), s in zip(labels, kids):
    b = s.BoundBox
    if 'drag chain fixing plate' in l or 'camera kit' in k or 'filament' in k:
        continue
    if 'top kit' in k and ('guiding element' in l or 'pu-4 gas pipe fitting' in l):
        continue
    if 'z axis kit' in k and (re.search(r'mgn9hz1c|ab axis mounting seat|belt pressure plate', l) or (re.search(r'm3x|m4x|m2x', l) and 125 < b.ZMin < 200 and b.ZMax < 205)):
        continue                                               # rides on the Z carriages
    STOCK.append((l, s))

rep = {'note': __doc__.split('\n')[0], 'chains': [], 'harness_vs_head': [], 'arcs': [], 'arc_top_full_height': None,
       'top_hat_top': None, 'arc_crossings': {}, 'arc_lengths_mm': {}}
P0, _ = B.build_pose(270.0, 0.0)
ENCL = [(n, s) for n, m, s, g in P0 if g == 'enclosure']
rep['top_hat_top'] = round(max(s.BoundBox.ZMax for n, s in ENCL if n.startswith('top hat')), 1)
MOVING_G = ('frame', 'bridge', 'head', 'docks', 'belts')

# ---------------------------------------------------------------- 1. chains over the Z travel
DZS = list(np.linspace(-GANTRY_DROP, GANTRY_RISE, 13))
near_side = lambda s: abs(tight(s).XMin) > 280 or abs(tight(s).XMax) > 280
fixed_side = [(n, s) for n, s in STOCK + ENCL if near_side(s)]
for y_xb in (Y_XB_MIN, 270.0, Y_XB_DOCK):
    P, _ = B.build_pose(y_xb, 0.0)
    mov = [(n, s) for n, m, s, g in P if g in MOVING_G and near_side(s)]
    for dz in DZS:
        mv = []
        for n, s in mov:
            t = s.copy(); t.translate(V(0, 0, dz)); mv.append((n, t))
        for n, m, c, g in RT.chain_parts(dz):
            own = n.replace('cable chain ', '').replace(' and link board power', '')
            line = {c_[0]: c_[3] for L in RT.CHAINS.values() for c_ in L}[n.replace('cable chain ', '')]
            skip = lambda x, own=own, line=line: x.endswith(own) or (line is not None and x == f'harness {line}')
            for h in hits(c, mv + (fixed_side if y_xb == 270.0 else []), skip):
                rep['chains'].append(dict(chain=n, dz=round(dz, 1), y_xb=y_xb, vol=h[0], part=h[1]))
    print('chains at y_xb', y_xb, 'clashes so far', len(rep['chains']), flush=True)

# ---------------------------------------------------------------- 2. harness, posts, mast vs head and bridge
ROUTE_G = [(n, s) for n, m, s, g in P0 if g == 'frame' and n.startswith(('harness', 'rear mast', 'side mast', 'link board', 'umbilical feed', 'chain bracket'))]
grid = [(x, y) for x in (-252.0, -126.0, 0.0, 126.0, 252.0) for y in (64.4, 190.0, 314.0, 440.0, 563.5)]
for x, y in grid:
    P, _ = B.build_pose(y - NOZZLE_DY, x, with_static=False)
    hb = [(n, s) for n, m, s, g in P if g in ('head', 'bridge')]
    for n, s in ROUTE_G:
        for h in hits(s, hb):
            rep['harness_vs_head'].append(dict(part=n, nozzle=(x, y), vol=h[0], other=h[1]))
print('harness vs head/bridge clashes', len(rep['harness_vs_head']), flush=True)

# ---------------------------------------------------------------- 3. arcs
def trimmed(X, line):
    Q = RT.resample(X, 3.0)
    return Q[5:-5]                                              # leave out the clamp and the end (15 mm each)

def arc_test_solid(X, line):
    return RT.pipe(trimmed(X, line), 6.0 if line == 'umb' else 2.2)

def dense(X):
    return RT.resample(X, 3.0)

parked = {}
for line, k in RT.TOOL_DOCK.items():
    X, ok = RT.arc_nodes(line, RT.tool_end(DOCK_X[k], Y_XB_DOCK, True)); parked[line] = (X, ok)
rep['arc_lengths_mm'] = {k: round(v) for k, v in RT._LEN.items()}
fixed_top = [(n, s) for n, s in STOCK + ENCL if s.BoundBox.ZMax > 520]
bed = [(x, y) for x in (-252.0, 0.0, 252.0) for y in (64.4, 230.0, 400.0, 563.5)]
top = 0.0; gaps = []
for active, k in RT.TOOL_DOCK.items():
    poses = [('bed', x, y - NOZZLE_DY) for x, y in bed] + [('dock', DOCK_X[k], Y_XB_DOCK)]
    for kind, xn, y_xb in poses:
        P, _ = B.build_pose(y_xb, xn)
        mov = [(n, s) for n, m, s, g in P if g in MOVING_G]
        arcs = {}
        arcs[active] = RT.arc_nodes(active, RT.tool_end(xn, y_xb, False)) if kind == 'bed' else parked[active]
        arcs['umb'] = RT.arc_nodes('umb', RT.umb_end(xn, y_xb))
        for line in RT.TOOL_DOCK:
            if line != active:
                arcs[line] = parked[line]
        for line, (X, ok) in arcs.items():
            top = max(top, float(X[:, 2].max()))
            if not ok:
                rep['arcs'].append(dict(arc=line, active=active, pose=(kind, xn, round(y_xb + NOZZLE_DY, 1)), part='elastica did not converge'))
            sol = arc_test_solid(X, line)
            for h in hits(sol, mov):
                rep['arcs'].append(dict(arc=line, active=active, pose=(kind, xn, round(y_xb + NOZZLE_DY, 1)), vol=h[0], part=h[1]))
            up = sol.copy(); up.translate(V(0, 0, GANTRY_RISE))
            for h in hits(up, fixed_top):
                rep['arcs'].append(dict(arc=line, active=active, pose=(kind, xn, round(y_xb + NOZZLE_DY, 1)), vol=h[0], part=h[1], at='500 mm print height'))
        names = list(arcs)
        for i in range(len(names)):                             # tube-on-tube: centreline gap minus both radii
            for j in range(i + 1, len(names)):
                a, b = dense(trimmed(arcs[names[i]][0], names[i])), dense(trimmed(arcs[names[j]][0], names[j]))
                d = np.min(np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2))
                r = (6.0 if names[i] == 'umb' else 2.2) + (6.0 if names[j] == 'umb' else 2.2)
                gaps.append((round(float(d - r), 1), active, kind, xn, names[i], names[j]))
    print('arcs with', active, 'on the head: clashes so far', len(rep['arcs']), flush=True)
rep['arc_top_full_height'] = round(top + GANTRY_RISE, 1)
touch = [g for g in gaps if g[0] < 0]
rep['arc_crossings'] = dict(pairs_checked=len(gaps), touching=len(touch), min_gap=min(g[0] for g in gaps),
                            parked_pairs_touching=sum(1 for g in touch if g[4] not in ('umb',) and g[5] not in ('umb',) and g[4] != g[1] and g[5] != g[1]),
                            worst=sorted(touch)[:12])
(B.OUT / 'C3_ROUTE_CHECK.json').write_text(json.dumps(rep, indent=1, default=str))
print('chains', len(rep['chains']), 'harness vs head', len(rep['harness_vs_head']), 'arcs', len(rep['arcs']),
      'arc top at full height', rep['arc_top_full_height'], 'top hat top', rep['top_hat_top'])
print('arc crossings', {k: v for k, v in rep['arc_crossings'].items() if k != 'worst'})
for sec in ('chains', 'harness_vs_head', 'arcs'):
    for h in rep[sec][:15]:
        print(sec, h)
