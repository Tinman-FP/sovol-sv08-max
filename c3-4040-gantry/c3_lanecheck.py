"""C3 lane spacing (run with FreeCAD's Python): how close a dock or a wiper station may sit beside a lane the head
drives into. Sets the 78 mm dock row (c3_params.DOCK_X, c3_purge.ST_X). Writes c3/C3_LANE_SPACING.json.

Minimum lane spacing, by surface sampling (same idea as the keep-out map).
Each shape is sampled on its surface (<= 0.7 mm) and binned in 1 mm (Y, Z) cells holding min/max X. Head driving into a
lane: the head cells are shifted in Y over the approach (nozzle Y 535 -> docking depth). For a neighbour on the +X side
the spacing needed is max over shared cells of (head max X - neighbour min X); -X side mirrored. Cells widened by one
bin each way (conservative), then +0.5 mm."""
import sys, os, json, math
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ['C2_EXPORT'] = '0'; os.environ['C3_ENCLOSURE'] = '0'
import FreeCAD as App, Part
import c3_build as B, c3_purge as PG
from c3_params import *
V = App.Vector

def cells(shapes, step=0.7):
    c = {}
    for s in shapes:
        pts, tris = s.tessellate(0.15)
        P = [(p.x, p.y, p.z) for p in pts]
        for i, j, k in tris:
            a, b, cc = P[i], P[j], P[k]
            L = max(math.dist(a, b), math.dist(b, cc), math.dist(a, cc))
            n = max(1, int(math.ceil(L / step)))
            for u in range(n + 1):
                for v in range(n + 1 - u):
                    w = n - u - v
                    x = (a[0] * u + b[0] * v + cc[0] * w) / n; y = (a[1] * u + b[1] * v + cc[1] * w) / n; z = (a[2] * u + b[2] * v + cc[2] * w) / n
                    key = (int(math.floor(y)), int(math.floor(z)))
                    lo, hi = c.get(key, (1e9, -1e9))
                    c[key] = (min(lo, x), max(hi, x))
    return c

def widen(c):
    w = {}
    for (y, z), (lo, hi) in c.items():
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                k = (y + dy, z + dz); a, b = w.get(k, (1e9, -1e9)); w[k] = (min(a, lo), max(b, hi))
    return w

def need(head, obst, shifts):
    plus = minus = -1e9
    for sh in shifts:
        for (y, z), (hlo, hhi) in head.items():
            o = obst.get((y - sh, z))            # head moved back by sh
            if o is None: continue
            olo, ohi = o
            plus = max(plus, hhi - olo)          # neighbour on +X: s >= head max X - neighbour min X
            minus = max(minus, ohi - hlo)        # neighbour on -X: s >= neighbour max X - head min X
    return round(plus + 0.5, 1), round(minus + 0.5, 1)

P, _ = B.build_pose(Y_XB_DOCK, 0.0)
head = [s for n, m, s, g in P if g == 'head' or n.startswith('x carriage')]
dock = [s.copy() for n, m, s, g in P if n.startswith(('bondtech dock 3 ', 'indx tool parked 3 '))]
for s in dock: s.translate(V(-DOCK_X[2], 0, 0))
LIFT = 9.6
xs = PG.ST_X[0]
sl = [PG.station_slider(xs, LIFT), PG.wiper_pad(xs, LIFT)]
for s in sl: s.translate(V(-xs, 0, 0))
slr = [PG.station_slider(xs), PG.wiper_pad(xs), PG.station_bracket(xs)]
for s in slr: s.translate(V(-xs, 0, 0))
print('sampling', flush=True)
H = widen(cells(head)); Dk = cells(dock); SL = cells(sl); SR = cells(slr)
print('cells', len(H), len(Dk), len(SL), flush=True)
shifts = list(range(0, 37))           # head moved back 0..36 mm from the docking depth (nozzle 570.55 -> 534.5)
res = {
 'head_into_lane_vs_dock_tool (+X, -X)': need(H, Dk, shifts),
 'head_into_lane_vs_lifted_station_59mm': need(H, SL, shifts),
 'head_into_lane_vs_rest_station_59mm': need(H, SR, shifts),
}
# narrow station: the same slider and pad cut to +-w (an estimate of a slimmer slider: pins moved in front of the pocket)
for w in (20.0, 18.0):
    nb = Part.makeBox(2 * w, 300, 300, V(-w, 400, 0))
    res[f'head_into_lane_vs_lifted_station_{int(2*w)}mm'] = need(H, cells([s.common(nb) for s in sl]), shifts)
# parked tool vs a lifted slider (both still)
Dw = widen(Dk)
res['parked_tool_vs_lifted_station_59mm'] = need(Dw, SL, [0])
print(json.dumps(res, indent=1), flush=True)
(B.OUT / 'C3_LANE_SPACING.json').write_text(json.dumps(res, indent=1))
