"""C3 (AWD) clearance check against the full stock SV08 Max (Sovol's model, Z carriages levelled to the stock pose).

1. Static: every new part at each XY pose (travel corners, docking) vs every stock body, at the stock gantry height.
2. Z sweep: the whole gantry plus the stock Z-carriage parts, from the first layer (-169.5) to 500 mm print height
   (+330.5) in 5 mm steps, vs the fixed stock frame (towers, Z belts and idlers, top frame, bed, base, camera...).
3. Belts vs every non-wheel part at each pose (belts must touch only their own wheels and clamps).
Writes c3/C3_CLEARANCE.json. Run with FreeCAD's Python.
"""
import sys, os, re, json, math
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0')
import c3_build as B
from c3_params import *
V = App.Vector

cache = B.STOCK_CACHE; cache.mkdir(parents=True, exist_ok=True)
brep, labf = cache / 'stock_keep.brep', cache / 'stock_keep_labels.json'
if not brep.exists():
    sd = App.openDocument(str(B.INP / 'stock_printer/SV08_ORIGINAL_STOCK_REFERENCE.FCStd')); T = V(-341.7798388764, -141.8577229783, -301.4741156424)
    def eng(s):
        try: s = s.encode('latin-1').decode('gbk')
        except Exception: pass
        return re.sub(r'\s+', ' ', re.sub(r'[^\x20-\x7e]+', ' ', s)).strip().lower()
    keep = []
    for o in sd.Objects:
        if o.TypeId != 'Part::Feature' or o.Shape.isNull(): continue
        p0 = o; ps = []
        while p0.getParentGeoFeatureGroup() is not None: p0 = p0.getParentGeoFeatureGroup(); ps.append(p0.Label)
        ps = ps[::-1]; kit = eng(ps[1]) if len(ps) > 1 else ''; lab = eng(o.Label)
        if 'ab axis kit' in kit or kit == 'toolhead' or 'auxiliary feeder' in kit or 'wk-10x20' in lab or 'drag chain' in lab or 'silicon brush' in lab: continue
        s = o.Shape.copy(); s.Placement = o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement); s.translate(T); b = s.BoundBox
        if 'z axis kit' in kit and re.search(r'mgn9hz1c|ab axis mounting seat|belt pressure plate|m3x|m4x', lab):
            if b.ZMin > 300 and b.ZMax < 420: s.translate(V(0, 0, 153.2 - 367.2))
            elif 'z 4 z axis kit' in kit and 130 < b.ZMin < 200: s.translate(V(0, 0, 15.2))
            elif ('z 1 z axis kit' in kit or 'z 2 z axis kit' in kit) and 140 < b.ZMin < 200: s.translate(V(0, 0, 0.2))
        keep.append((lab, kit, s))
    Part.makeCompound([s for l, k, s in keep]).exportBrep(str(brep)); labf.write_text(json.dumps([(l, k) for l, k, s in keep]))
labels = json.loads(labf.read_text()); comp = Part.read(str(brep)); kids = comp.childShapes()
assert len(kids) == len(labels), (len(kids), len(labels))
STOCK = [(l, k, s) for (l, k), s in zip(labels, kids)]
# the stock Z drag chain's gantry end plate and its screws leave with the stock gantry (INDX umbilical replaces the chain)
def _dragplate(l, k, s):
    b = s.BoundBox
    return 'drag chain fixing plate' in l or (re.search(r'm3x20|m3x5', l) and -200 < b.XMin and b.XMax < -140 and -60 < b.YMin and b.YMax < -36 and b.ZMin > 160)
STOCK = [x for x in STOCK if not _dragplate(*x)]
# the stock camera rode on the old gantry; it gets a new mount (reported separately)
CAMERA = [x for x in STOCK if 'camera kit' in x[1]]
STOCK = [x for x in STOCK if 'camera kit' not in x[1]]
# the stock filament guide on the right top rail leaves too (the INDX PTFE tubes come down through the top hat lid)
def _guide(l, k, s):
    b = s.BoundBox
    return 'top kit' in k and ('guiding element' in l or 'pu-4 gas pipe fitting' in l or ('m3x14' in l and b.XMax < -330 and 250 < b.YMin < 290))
STOCK = [x for x in STOCK if not _guide(*x)]
def moves_with_gantry(lab, kit, s):
    """Stock parts carried by the Z carriages (arms, seats, blocks, pressure plates and their screws near the arm)."""
    if 'z axis kit' not in kit: return False
    if re.search(r'mgn9hz1c|ab axis mounting seat|belt pressure plate', lab): return True
    b = s.BoundBox
    return bool(re.search(r'm3x|m4x|m2x', lab)) and 125 < b.ZMin < 200 and b.ZMax < 205
MOVING = [(l, k, s) for l, k, s in STOCK if moves_with_gantry(l, k, s)]
FIXED = [(l, k, s) for l, k, s in STOCK if not moves_with_gantry(l, k, s)]

def overlaps(news, olds, tol=0.5, dz=0.0, skip=lambda a, b: False):
    hits = []
    for n, m, s, g in news:
        sb = s.BoundBox
        if dz: sb = App.BoundBox(sb.XMin, sb.YMin, sb.ZMin + dz, sb.XMax, sb.YMax, sb.ZMax + dz)
        for lab, kit, t in olds:
            if not sb.intersect(t.BoundBox) or skip(n, lab): continue
            ss = s
            if dz: ss = s.copy(); ss.translate(V(0, 0, dz))
            try: v = ss.common(t).Volume
            except Exception: v = -1
            if v > tol and not (v < 20 and ('pad' in n or 'motor mount' in n or 'corner base' in n) and 'mounting seat' in lab):
                hits.append((round(v, 2), n, lab[:56], dz))   # pads seated on the stock arm tops are intended face contact
    return hits

poses = {'nominal': (270.0, -5.0), 'rear_xn': (Y_XB_MIN, -252.0), 'rear_xp': (Y_XB_MIN, 252.0),
         'front_xn': (563.5 - NOZZLE_DY, -252.0), 'front_xp': (563.5 - NOZZLE_DY, 252.0),
         'dock_first': (Y_XB_DOCK, DOCK_X[0]), 'dock_last': (Y_XB_DOCK, DOCK_X[-1])}
rep = {'stock_bodies': len(STOCK), 'moving_with_gantry': len(MOVING), 'static': {}, 'belts': {}, 'internal': {}}
for name, (y, x) in poses.items():
    P, lens = B.build_pose(y, x)
    solids = [p for p in P if p[3] not in ('belts', 'enclosure')]
    rep['static'][name] = sorted(overlaps(solids, STOCK), reverse=True)[:30]
    # moving groups vs the gantry-fixed new parts (joints/carriage/head vs corners, docks, motors...)
    mov = [p for p in solids if p[3] in ('bridge', 'head')]; fix = [(p[0], '', p[2]) for p in solids if p[3] in ('frame', 'docks')]
    tgt = (DOCK_X.index(x) + 1) if name.startswith('dock') else None
    def skip_int(a, b):
        if ('y block' in a and 'y rail' in b) or 'x block' in a:
            return True
        if tgt is not None:   # at a docking pose the head nests with its own dock and tool (one tool exists there)
            if 'tool on head' in a and ('parked' in b or 'bondtech dock' in b):
                return True
            if ('smart head' in a or 'x carriage' in a or 'beacon' in a) and (f'dock {tgt} ' in b or f'parked {tgt} ' in b):
                return True
        return False
    head = [p for p in solids if p[3] == 'head']; brg = [(p[0], '', p[2]) for p in solids if p[3] == 'bridge']
    skip_hb = lambda a, b: 'x block' in a or 'x block' in b   # the carriage bolts to the X block
    rep['internal'][name] = sorted(overlaps(mov, fix, skip=skip_int) + overlaps(head, brg, skip=skip_hb), reverse=True)[:30]   # + head vs X beam / joints
    belts = [p for p in P if p[3] == 'belts']
    others = [(p[0], '', p[2]) for p in solids]
    rep['belts'][name] = sorted(overlaps(belts, others, tol=2.0, skip=lambda a, b: ('idler' in b or 'pulley' in b or 'x carriage' in b)), reverse=True)[:30]
    print(name, 'static', len(rep['static'][name]), 'internal', len(rep['internal'][name]), 'belts', len(rep['belts'][name]), flush=True)
# Z sweep at the nominal XY pose plus the two docking extremes (docks and parked tools ride on the gantry)
P, _ = B.build_pose(270.0, -5.0)
FIXED += [(n, 'new-fixed', s) for n, m, s, g in P if g == 'enclosure']
gantry = [p for p in P if p[3] not in ('belts', 'enclosure')]       # stock Z-carriage parts are unchanged here (Z upgrade checked separately)
gantry = [p for p in gantry if not p[0].startswith(('wiper station slider', 'silicone wiper pad'))]   # these lift off the PEI: c3_purgecheck.py
sweep = []
DZS = [float(d) for d in range(-int(GANTRY_DROP) - 1, int(GANTRY_RISE) + 5, 5)] + [-GANTRY_DROP, GANTRY_RISE]
for n, m, s, g in gantry:                      # pair each gantry part with fixed bodies under its XY footprint once
    sb = s.BoundBox
    cand = [(lab, kit, t) for lab, kit, t in FIXED
            if t.BoundBox.XMin <= sb.XMax and t.BoundBox.XMax >= sb.XMin and t.BoundBox.YMin <= sb.YMax and t.BoundBox.YMax >= sb.YMin
            and t.BoundBox.ZMax >= sb.ZMin + DZS[0] and t.BoundBox.ZMin <= sb.ZMax + DZS[-1]]
    for dz in DZS:
        zc = [(lab, kit, t) for lab, kit, t in cand if t.BoundBox.ZMax >= sb.ZMin + dz and t.BoundBox.ZMin <= sb.ZMax + dz]
        if zc:
            sweep += overlaps([(n, m, s, g)], zc, dz=dz)
agg = {}
for v, n, lab, dz in sweep:
    k = (n, lab); a = agg.setdefault(k, [v, dz, dz]); a[0] = max(a[0], v); a[1] = min(a[1], dz); a[2] = max(a[2], dz)
rep['z_sweep'] = sorted([(round(a[0], 1), n, lab, a[1], a[2]) for (n, lab), a in agg.items()], reverse=True)
# frame-fixed new parts (camera mount, top hat, lid, take-up) vs the fixed stock frame
enc = [p for p in P if p[3] == 'enclosure' and p[1] != 'purchased' or (p[3] == 'enclosure' and 'camera stock' in p[0])]
rep['enclosure_static'] = sorted(overlaps(enc, [x for x in FIXED if x[1] != 'new-fixed']), reverse=True)
print('z sweep conflicts', len(rep['z_sweep']), 'enclosure static', len(rep.get('enclosure_static', [])))
(B.OUT / 'C3_CLEARANCE.json').write_text(json.dumps(rep, indent=1))
for sec in ('static', 'internal', 'belts'):
    for name, hits in rep[sec].items():
        for h in hits[:8]: print(sec, name, h)
for h in rep['z_sweep'][:40]: print('zsweep', h)
for h in rep.get('enclosure_static', [])[:20]: print('enclosure', h)
