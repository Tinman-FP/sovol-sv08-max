"""C3 PTFE tube check (run with FreeCAD's Python after c3_build.py): the tubes that move with the tools.

c3_check covers everything fixed, including the tube spans inside the top hat (c3_ptfe.tube_bodies). Below the dock
guides each tube moves with its tool:
* a parked tool's tube hangs straight down from its guide into the tool;
* the tool on the head has a taut tube from its guide to the top of the head (modelled as a straight line).
For a grid of head positions plus every docking pose, at the first layer and at 500 mm print height, and for each tool
on the head in turn, each tube (a 4 mm rod) is checked against the moving gantry (head, bridge, docks with their parked
tools, belts, frame parts on the gantry) and the fixed top hat parts, and the active tube against the parked ones.
Contacts at a tube's own ends (its guide, its tool, the head top where it plugs in) are skipped.
Writes c3/C3_PTFE_CHECK.json.
"""
import sys, os, json, math
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0')
import c3_build as B
import c3_ptfe as PT
from c3_params import *
V = App.Vector
R_TUBE = 2.0
ZS = {'first_layer': -GANTRY_DROP, 'height_500': GANTRY_RISE}

def rod(a, b, r=R_TUBE):
    d = b - a
    return Part.makeCylinder(r, d.Length, a, d)

def seg_dist(p1, p2, q1, q2):
    """Shortest distance between segments p1p2 and q1q2."""
    u, v, w = p2 - p1, q2 - q1, p1 - q1
    a, b, c, d, e = u.dot(u), u.dot(v), v.dot(v), u.dot(w), v.dot(w)
    D = a * c - b * b; sc = tc = 0.0
    if D < 1e-9:
        sc, tc = 0.0, (e / c if c > 1e-9 else 0.0)
    else:
        sc, tc = (b * e - c * d) / D, (a * e - b * d) / D
    sc, tc = min(1.0, max(0.0, sc)), min(1.0, max(0.0, tc))
    return (w + u * sc - v * tc).Length

def hits(tube, shapes, skip=()):
    out = []
    tb = tube.BoundBox
    for n, s in shapes:
        if any(k in n for k in skip) or not tb.intersect(s.BoundBox): continue
        try: v = tube.common(s).Volume
        except Exception: v = -1.0
        if v > 0.2 or v < 0: out.append((round(v, 2), n))
    return sorted(out, reverse=True)

def exit_pt(k):
    return V(DOCK_X[k], PT.NOZ_Y, PT.GUIDE['exit_z'])

poses = [(x, y) for x in (-252.0, -126.0, 0.0, 126.0, 252.0) for y in (64.4, 314.0, 563.5)]
poses = [('bed', x, y - NOZZLE_DY) for x, y in poses] + [('dock', x, Y_XB_DOCK) for x in DOCK_X]
rep = {'note': __doc__.split('\n')[0], 'contacts': [], 'tube_tube_min_mm': None, 'poses': len(poses) * len(ZS), 'active_tools': 5}
min_tt = 1e9
for kind, xn, y_xb in poses:
    P, _ = B.build_pose(y_xb, xn)
    moving = [(n, s) for n, m, s, g in P if g in ('frame', 'bridge', 'head', 'docks', 'belts')]
    fixed = [(n, s) for n, m, s, g in P if g == 'enclosure' and not n.startswith(('ptfe tube', 'head cables'))]
    head_top = max(s.BoundBox.ZMax for n, s in moving if n.startswith(('indx tool on head', 'indx smart head')))   # tube plugs in on top
    parked_top = {k: max(s.BoundBox.ZMax for n, s in moving if n.startswith(f'indx tool parked {k + 1} ')) for k in range(5)}
    for zname, dz in ZS.items():
        mv = []
        for n, s in moving:
            t = s.copy(); t.translate(V(0, 0, dz)); mv.append((n, t))
        inlet = V(xn, y_xb + NOZZLE_DY, head_top + dz)
        for a in range(5):                                        # tool a on the head, the others parked
            docked_here = kind == 'dock' and abs(xn - DOCK_X[a]) < 1e-6
            tubes = []
            if not docked_here:
                tubes.append(('active', a, exit_pt(a), inlet))
            for k in range(5):
                if k != a or docked_here:
                    tubes.append(('parked', k, exit_pt(k), V(DOCK_X[k], PT.NOZ_Y, parked_top[k] + dz)))
            for role, k, p, q in tubes:
                if q.z >= p.z - 1.0 and role == 'parked':
                    continue                                       # tool top at or above the guide exit: no free tube
                if (q - p).Length < 1.0: continue
                tb = rod(p, q)
                skip = [f'ptfe dock guide {k + 1}']
                if role == 'parked': skip += [f'indx tool parked {k + 1} ', f'bondtech dock {k + 1} ']
                else: skip += ['indx tool on head', 'indx smart head']
                found = hits(tb, mv + fixed, skip)
                if role == 'active' and (q - p).Length > 30.0:     # the tube may not pass through the head away from its inlet
                    found += hits(rod(p, p + (q - p) * (1.0 - 25.0 / (q - p).Length)),
                                  [(n, s) for n, s in mv if n.startswith(('indx smart head', 'indx tool on head'))])
                for h in found:
                    rep['contacts'].append(dict(pose=kind, x=xn, y_nozzle=round(y_xb + NOZZLE_DY, 1), z=zname, tool_on_head=f'T{a}',
                                                tube=f'{role} T{k}', vol_mm3=h[0], part=h[1]))
            act = [t for t in tubes if t[0] == 'active']
            for role, k, p, q in tubes:
                if role == 'parked' and act:
                    min_tt = min(min_tt, seg_dist(act[0][2], act[0][3], p, q))
    print(kind, xn, round(y_xb + NOZZLE_DY, 1), 'contacts so far', len(rep['contacts']), flush=True)
rep['tube_tube_min_mm'] = round(min_tt - 2 * R_TUBE, 1)
rep['summary'] = sorted({(c['tube'].split()[0], c['part'][:40]) for c in rep['contacts']})
(B.OUT / 'C3_PTFE_CHECK.json').write_text(json.dumps(rep, indent=1))
print('contacts', len(rep['contacts']), 'tube-tube min gap', rep['tube_tube_min_mm'], flush=True)
for s in rep['summary'][:40]: print(' ', s)
