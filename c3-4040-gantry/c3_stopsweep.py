"""C3 sensorless-homing hard stops: sweep the head (X) and the gantry (Y, rear) past the travel limits and report first contacts. Writes c3/C3_HARD_STOP_SWEEP.json. Run with FreeCAD's Python, C2_STOCK_CACHE set as for c3_check.py."""
import sys, os, json, re
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
from pathlib import Path
C = str(Path(__file__).resolve().parent)
sys.path.insert(0, C); os.environ['C2_EXPORT'] = '0'
import FreeCAD as App, Part
import c3_build as B
from c3_params import *
V = App.Vector
cache = B.STOCK_CACHE
labels = json.loads((cache / 'stock_keep_labels.json').read_text()); kids = Part.read(str(cache / 'stock_keep.brep')).childShapes()
STOCK = [(l, k, s) for (l, k), s in zip(labels, kids) if 'camera kit' not in k and 'drag chain' not in l]
def hits(movers, fixed, d, skip):
    out = []
    for n, s in movers:
        sb = s.BoundBox; sb = App.BoundBox(sb.XMin + d[0], sb.YMin + d[1], sb.ZMin, sb.XMax + d[0], sb.YMax + d[1], sb.ZMax)
        for m, t in fixed:
            if skip(n, m) or not sb.intersect(t.BoundBox): continue
            ss = s.copy(); ss.translate(V(d[0], d[1], 0))
            try: v = ss.common(t).Volume
            except Exception: v = -1
            if v > 0.005: out.append((round(v, 3), n, m))
    return sorted(out, reverse=True)
res = {}
def sweep(label, base, groups_move, step_vec, steps, skip):
    P, _ = B.build_pose(*base)
    solids = [p for p in P if p[3] != 'belts']
    mov = [(p[0], p[2]) for p in solids if p[3] in groups_move]
    fix = [(p[0], p[2]) for p in solids if p[3] not in groups_move and p[3] != 'enclosure'] + [(l[:50], s) for l, k, s in STOCK]
    first = None; log = []
    for i in steps:
        d = (step_vec[0] * i, step_vec[1] * i)
        h = hits(mov, fix, d, skip)
        log.append((i, h[:4]))
        print(label, i, h[:3], flush=True)
        if h and first is None: first = (i, h[:6])
        if first is not None and i >= first[0] + 1.0: break
    res[label] = {'base': base, 'first_contact': first, 'log': log}
sk = lambda a, b: ('x block' in a and 'x rail' in b) or ('y block' in a and 'y rail' in b) or 'belt' in a or 'belt' in b
steps = [0.25 * k for k in range(1, 41)]
sweep('X+ (left)', (270.0, 252.0), ('head',), (1, 0), steps, sk)
sweep('X- (right)', (270.0, -252.0), ('head',), (-1, 0), steps, sk)
sweep('Y rear, head centre', (Y_XB_MIN, 0.0), ('head', 'bridge'), (0, -1), steps, sk)
sweep('Y rear, head X+', (Y_XB_MIN, 252.0), ('head', 'bridge'), (0, -1), steps, sk)
json.dump(res, open(os.path.join(C, 'c3', 'C3_HARD_STOP_SWEEP.json'), 'w'), indent=1, default=str)
print('EXIT')
