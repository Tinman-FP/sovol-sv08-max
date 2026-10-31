"""C3 purge/wipe stations: clearance checks (run with FreeCAD's Python after c3_build.py).

1. Lift sweep: at every Z-sweep step the slider rests on the PEI when the gantry is low. The lift it needs (foot on
   the sheet) must fit the pin travel, and the lifted slider and pad must clear the fixed frame (stock + trays).
   The fixed purge parts on the gantry (bar, clips, brackets, pins) sweep without lift.
2. Station and wipe poses: the head at each of the five stations (purge position, nozzle Y 571), mid-stroke (centre and
   8 mm toward the tool's own dock) and the end of the wipe stroke,
   head and bridge vs every gantry-fixed part. At the wipe poses only the nozzle may touch the pad (the wipe
   engagement volume is reported apart).
3. Lifted sliders (first layer) vs the head docking at every dock and at the front print corners.
4. Purge trays vs the stock frame.
5. Alone with C3_KEEPOUT=1 (c3/C3_PURGE_KEEPOUT.json): front keep-out map, the furthest-forward nozzle Y per X at which the head clears the
   docks, parked tools and stations (at rest and lifted), for the slicer's bed shape.
Writes c3/C3_PURGE_CLEARANCE.json.
"""
import sys, os, re, json
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0')
import c3_build as B
import c3_purge as PG
from c3_params import *
V = App.Vector

labf, brep = B.STOCK_CACHE / 'stock_keep_labels.json', B.STOCK_CACHE / 'stock_keep.brep'
assert brep.exists(), 'run c3_check.py once to build the stock cache'
STOCK = [(l, k, s) for (l, k), s in zip(json.loads(labf.read_text()), Part.read(str(brep)).childShapes())]
STOCK = [x for x in STOCK if 'camera kit' not in x[1]]                        # camera has its own mount (c3_check)
def _moving(lab, kit, s):                                                     # same rule as c3_check
    if 'z axis kit' not in kit: return False
    if re.search(r'mgn9hz1c|ab axis mounting seat|belt pressure plate', lab): return True
    b = s.BoundBox
    return bool(re.search(r'm3x|m4x|m2x', lab)) and 125 < b.ZMin < 200 and b.ZMax < 205
FIXED = [x for x in STOCK if not _moving(*x)]

def overlaps(news, olds, tol=0.5, skip=lambda a, b: False):
    hits = []
    for n, s in news:
        sb = s.BoundBox
        for lab, t in olds:
            if not sb.intersect(t.BoundBox) or skip(n, lab): continue
            try: v = s.common(t).Volume
            except Exception: v = -1
            if v > tol or v < 0:
                hits.append((round(v, 2), n, lab[:60]))
    return sorted(hits, reverse=True)

MOVING_PURGE = ('wiper station slider', 'silicone wiper pad')
def is_lifting(n): return n.startswith(MOVING_PURGE)
P0, _ = B.build_pose(270.0, -5.0)
purge_g = [(n, s) for n, m, s, g in P0 if g == 'docks' and (n.startswith(('station bar', 'wiper station', 'silicone wiper', 'dowel pin')))]
trays = [(n, s) for n, m, s, g in P0 if n.startswith('purge tray')]
rep = {'travel_mm': round(PG.TRAVEL, 2), 'foot_z': PG.FOOT_Z, 'stations_x': PG.ST_X}

# ---- 5. front keep-out map
# The head only translates with (xn, y_xb) and moves forward into the front parts, so the first contact in any
# (X, Z) column is between the head's front-most surface point and the obstacle's rear-most one. Surfaces are sampled
# (<= 0.8 mm), binned in 1 mm columns, and the obstacle columns are widened by one bin each way (conservative).
if os.environ.get('C3_KEEPOUT', '0') == '1':      # run alone: C3_KEEPOUT=1, writes c3/C3_PURGE_KEEPOUT.json
    import numpy as np
    NOZ_DY = PG.NOZ_Y - Y_XB_DOCK; lifted_max = BED_TOP - (PG.FOOT_Z - GANTRY_DROP - 1.0)
    X0, X1, Z0, Z1 = -420, 420, 90, 420
    def sample(shape, step=0.8):
        out = []
        for so in (shape.Solids or [shape]):
            vs, tris = so.tessellate(0.1)
            P = np.array([(v.x, v.y, v.z) for v in vs]); out.append(P)
            for a, b, c in tris:
                A, Bq, Cq = P[a], P[b], P[c]
                L = max(np.linalg.norm(Bq - A), np.linalg.norm(Cq - A), np.linalg.norm(Cq - Bq))
                n = int(L / step) + 1
                if n < 2: continue
                u, w = np.meshgrid(np.arange(n + 1), np.arange(n + 1)); m = (u + w) <= n
                u, w = u[m] / n, w[m] / n
                out.append(A + np.outer(u, Bq - A) + np.outer(w, Cq - A))
        return np.vstack(out)
    def columns(shapes, front):
        g = np.full((X1 - X0, Z1 - Z0), -np.inf if front else np.inf)
        for s in shapes:
            Q = sample(s); ix = np.floor(Q[:, 0]).astype(int) - X0; iz = np.floor(Q[:, 2]).astype(int) - Z0
            k = (ix >= 0) & (ix < X1 - X0) & (iz >= 0) & (iz < Z1 - Z0)
            (np.maximum if front else np.minimum).at(g, (ix[k], iz[k]), Q[k, 1])
        return g
    HEAD0 = [s for n, m, s, g in B.build_pose(0.0, 0.0, with_static=False)[0] if g == 'head' and 'x block' not in n]
    HY = columns(HEAD0, True)
    front = [(n, s) for n, m, s, g in P0 if g in ('docks', 'frame') and s.BoundBox.YMin > 400]   # parts ahead of the head only
    purge_names = ('station bar', 'wiper station', 'silicone wiper', 'dowel pin')
    sets = {'docks_only': [s for n, s in front if not n.startswith(purge_names)],
            'with_stations': [s for n, s in front],
            'with_stations_lifted': [(lambda t: (t.translate(V(0, 0, lifted_max)), t)[1])(s.copy()) if is_lifting(n) else s for n, s in front]}
    rep['keepout'] = {'note': 'furthest-forward nozzle Y per nozzle X (2 mm steps) at which the head clears the front gantry parts; capped at the rail limit Y %.1f' % PG.NOZ_Y}
    for key, obst in sets.items():
        OY = columns(obst, False)
        W = OY.copy()                                       # widen obstacle columns one bin each way
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                W = np.minimum(W, np.roll(np.roll(OY, dx, 0), dz, 1))
        hx, hz = np.nonzero(np.isfinite(HY))
        row = []
        for xn in range(-252, 253, 2):
            ox = hx + xn; ok = (ox >= 0) & (ox < X1 - X0)
            gap = W[ox[ok], hz[ok]] - HY[hx[ok], hz[ok]]
            dy = float(np.min(gap)) - 0.5 if np.isfinite(gap).any() else 1e9
            row.append((xn, round(min(dy, Y_XB_DOCK) + NOZ_DY, 1)))
        rep['keepout'][key] = row
        print('keepout', key, [r for r in row if r[0] % 24 == 0], flush=True)
    (B.OUT / 'C3_PURGE_KEEPOUT.json').write_text(json.dumps(rep['keepout'], indent=1))
    raise SystemExit(0)


# ---- 1. lift sweep (fixed frame = stock fixed bodies + trays)
fixed_all = [(l, s) for l, k, s in FIXED] + trays
DZS = [float(d) for d in range(-int(GANTRY_DROP) - 1, int(GANTRY_RISE) + 5, 5)] + [-GANTRY_DROP, GANTRY_RISE]
def lift_at(dz):
    return max(0.0, BED_TOP - (PG.FOOT_Z + dz))
sweep, lifts = [], {}
for n, s in purge_g:
    sb = s.BoundBox
    cand = [(l, t) for l, t in fixed_all if t.BoundBox.XMin <= sb.XMax and t.BoundBox.XMax >= sb.XMin and t.BoundBox.YMin <= sb.YMax
            and t.BoundBox.YMax >= sb.YMin and t.BoundBox.ZMax >= sb.ZMin + DZS[0] and t.BoundBox.ZMin <= sb.ZMax + DZS[-1] + PG.TRAVEL]
    for dz in DZS:
        lf = lift_at(dz) if is_lifting(n) else 0.0
        if is_lifting(n): lifts[dz] = round(lf, 2)
        t = s.copy(); t.translate(V(0, 0, dz + lf))
        for h in overlaps([(n, t)], cand):
            sweep.append(h + (dz,))
rep['lift_max_needed'] = max(lifts.values()); rep['lift_fits_travel'] = rep['lift_max_needed'] <= PG.TRAVEL
rep['lift_by_dz'] = {str(k): v for k, v in sorted(lifts.items()) if v > 0}
rep['lift_sweep'] = sweep
print('lift max', rep['lift_max_needed'], 'travel', PG.TRAVEL, 'sweep hits', len(sweep), flush=True)

# ---- 2. station, wipe and existing poses: head + bridge vs gantry-fixed parts (purge at rest)
NOZ_DY = PG.NOZ_Y - Y_XB_DOCK                    # 66.7: nozzle centre Y = Y_XB + 66.7
mid_wipe = sum(PG.PAD['y']) / 2
poses = {}
for k, xs in enumerate(PG.ST_X, 1):              # one station per tool, with docks and stations on both sides
    poses.update({f'station_t{k}': (Y_XB_DOCK, xs), f'wipe_mid_t{k}': (mid_wipe - NOZ_DY, xs),
                  f'wipe_mid_t{k}_own8': (mid_wipe - NOZ_DY, xs - 8.0),      # strokes step 8 mm toward the own (empty) dock only
                  f'wipe_end_t{k}': (PG.WIPE_Y[1] - NOZ_DY, xs)})
poses.update({'front_xn': (563.5 - NOZZLE_DY, -252.0), 'front_xp': (563.5 - NOZZLE_DY, 252.0)})
for i, x in enumerate(DOCK_X, 1):
    poses[f'dock_{i}'] = (Y_XB_DOCK, x)
rep['internal'], rep['wipe_engagement_mm3'], rep['lifted'] = {}, {}, {}
lifted_max = lift_at(-GANTRY_DROP - 1.0)
for name, (y, x) in poses.items():
    P, _ = B.build_pose(y, x)
    mov = [(n, s) for n, m, s, g in P if g in ('bridge', 'head')]
    fix = [(n, s) for n, m, s, g in P if g in ('frame', 'docks')]
    tgt = DOCK_X.index(x) + 1 if name.startswith('dock_') else None
    own = int(name.split('_t')[1][0]) if name.startswith(('station_t', 'wipe_')) else None   # tool k wipes at station k: dock k is empty
    def skip(a, b):
        if ('y block' in a and 'y rail' in b) or 'x block' in a: return True
        if own is not None and f'parked {own} ' in b: return True
        if tgt is not None:
            if 'tool on head' in a and ('parked' in b or 'bondtech dock' in b): return True
            if ('smart head' in a or 'x carriage' in a or 'beacon' in a) and (f'dock {tgt} ' in b or f'parked {tgt} ' in b): return True
        return False
    hits = overlaps(mov, fix, skip=skip)
    if name.startswith('wipe'):
        eng = [h for h in hits if 'tool on head' in h[1] and 'silicone wiper pad' in h[2]]
        rep['wipe_engagement_mm3'][name] = round(sum(h[0] for h in eng), 2)
        hits = [h for h in hits if h not in eng]
    rep['internal'][name] = hits[:30]
    # 3. the sliders lifted as at the first layer, vs the head (not at the stations: no station use below Z 12)
    if not name.startswith(('station', 'wipe')):
        lift = [(n, s.copy()) for n, s in fix if is_lifting(n)]
        for n, s in lift: s.translate(V(0, 0, lifted_max))
        rep['lifted'][name] = overlaps([(n, s) for n, s in mov], lift)[:30]
    print(name, 'internal', len(rep['internal'][name]), 'lifted', len(rep['lifted'].get(name, [])), 'wipe', rep['wipe_engagement_mm3'].get(name), flush=True)

# ---- 4. trays and the gantry purge parts at the build height vs the stock frame
rep['trays_vs_stock'] = overlaps(trays, [(l, s) for l, k, s in FIXED])
rep['purge_static_vs_stock'] = overlaps(purge_g, [(l, s) for l, k, s in STOCK])
print('trays vs stock', len(rep['trays_vs_stock']), 'purge parts vs stock', len(rep['purge_static_vs_stock']), flush=True)

(B.OUT / 'C3_PURGE_CLEARANCE.json').write_text(json.dumps(rep, indent=1))
for k in ('internal', 'lifted'):
    for name, hits in rep[k].items():
        for h in hits[:6]: print(k, name, h)
for h in rep['lift_sweep'][:20]: print('lift sweep', h)
for h in rep['trays_vs_stock'][:10] + rep['purge_static_vs_stock'][:10]: print('static', h)
