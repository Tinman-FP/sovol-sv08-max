"""C3 Z upgrade clearance check against the full stock SV08 Max and the C3 gantry.

1. Static, stock pose: every new Z part vs the stock printer. Removed from the stock set: the parts the upgrade
   replaces (Z carriage seats, pressure plates and their screws, 9 mm belts, tensioner blocks, idlers, Z drive pulleys,
   40 mm motors, and the two motor screws the end support replaces), plus the parts c3_check already removes.
2. Z sweep: the new carriage plates and clamp covers, first layer to 500 mm, vs the fixed stock frame, the new fixed
   Z parts and the 12 mm free belt runs.
3. Gantry sweep: the whole C3 gantry vs the 12 mm belt runs and the new fixed Z parts (the belts are 3 mm wider).
Writes c3/C3_Z_CLEARANCE.json. Run with FreeCAD's Python (C2_STOCK_CACHE set as for c3_check).
"""
import sys, os, re, json
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0'); os.environ.setdefault('C3_ENCLOSURE', '0')
import c3_build as B
import c3_zdrive as ZD
from c3_params import GANTRY_DROP, GANTRY_RISE
V = App.Vector

labels = json.loads((B.STOCK_CACHE / 'stock_keep_labels.json').read_text()); kids = Part.read(str(B.STOCK_CACHE / 'stock_keep.brep')).childShapes()
STOCK = [(l, k, s) for (l, k), s in zip(labels, kids)]
def gone_c3(l, k, s):                                   # as c3_check: drag chain plate, camera, filament guide
    b = s.BoundBox
    if 'drag chain fixing plate' in l or (re.search(r'm3x20|m3x5', l) and -200 < b.XMin and b.XMax < -140 and -60 < b.YMin and b.YMax < -36 and b.ZMin > 160):
        return True
    if 'camera kit' in k:
        return True
    return 'top kit' in k and ('guiding element' in l or 'pu-4 gas pipe fitting' in l or ('m3x14' in l and b.XMax < -330 and 250 < b.YMin < 290))
def replaced(l, k, s):
    if 'z axis kit' not in k:
        return False
    b = s.BoundBox
    if 'mounting seat' in l and 'ab' in l and (b.YMin > 594.9 or b.YMax < -47.9):                 # Z carriage seats (not the arms)
        return True
    if ('belt pressure plate' in l and b.ZMin > 100) or '2gt-9mm z' in l or 'tensioning wheel mounting bl' in l or 'tensioning wheel mounting se' in l or 'tensioning mounting seat' in l:
        return True
    if 'idler gear' in l or '02001-02-a' in l or '42-40 step motor' in l:
        return True
    if 'set screw' in l and 312 < abs((b.XMin + b.XMax) / 2) < 329 and -130 < b.ZMin and b.ZMax < -110 and (597 < b.YMin < 612 or -65 < b.YMax < -50):   # old Z pulley grub
        return True
    if 'm3x10' in l and '70.2' in l and b.ZMin > 100:                                               # pressure plate screws
        return True
    c = ((b.XMin + b.XMax) / 2, (b.ZMin + b.ZMax) / 2)                                               # the two +X motor screws (now M3 x 30)
    for (cx, cz) in ((ZD.MOTOR_AX[0] + 15.5, ZD.MOTOR_AX[1] + 15.5), (ZD.MOTOR_AX[0] + 15.5, ZD.MOTOR_AX[1] - 15.5)):
        for mxs in (1, -1):
            if re.search(r'm3x', l) and abs(c[0] - mxs * cx) < 2.0 and abs(c[1] - cz) < 2.0 and b.ZMax < -80:
                return True
    return False
block_parts = [s for l, k, s in STOCK if 'z 1 z axis kit' in k and 'tensioning wheel mounting bl' in l]
seat_parts = [s for l, k, s in STOCK if 'z 1 z axis kit' in k and 'tensioning wheel mounting se' in l]
STOCK = [x for x in STOCK if not gone_c3(*x)]
REMOVED = [x[0] for x in STOCK if replaced(*x)]
STOCK = [x for x in STOCK if not replaced(*x)]

def moves(l, k, s):
    if 'z axis kit' not in k:
        return False
    if re.search(r'mgn9hz1c|ab axis mounting seat|belt pressure plate', l):
        return True
    b = s.BoundBox
    return bool(re.search(r'm3x|m4x|m2x', l)) and 125 < b.ZMin < 200 and b.ZMax < 205 and not ('m3x6' in l and (b.YMin > 608.5 or b.YMax < -61.5))   # rail screws stay fixed
MOVING = [x for x in STOCK if moves(*x)]; FIXED = [x for x in STOCK if not moves(*x)]

Z = ZD.zdrive_parts(block_parts, seat_parts)
def overlaps(news, olds, tol=0.5, dz=0.0, skip=lambda a, b: False):
    hits = []
    for n, m, s, g in news:
        sb = s.BoundBox
        if dz:
            sb = App.BoundBox(sb.XMin, sb.YMin, sb.ZMin + dz, sb.XMax, sb.YMax, sb.ZMax + dz)
        for lab, kit, t in olds:
            if not sb.intersect(t.BoundBox) or skip(n, lab):
                continue
            ss = s
            if dz:
                ss = s.copy(); ss.translate(V(0, 0, dz))
            try:
                v = ss.common(t).Volume
            except Exception:
                v = -1
            if v > tol or v < 0:
                hits.append((round(v, 2), n, lab[:60], dz))
    return hits

rep = {'removed_stock': len(REMOVED), 'new_parts': len(Z)}
# 1. static: new Z parts vs the stock printer (moving and fixed) at the stock pose
skip_static = lambda a, b: ('clamped run' in a and ('carriage plate' in b or 'clamp cover' in b))
new_solids = [p for p in Z if p[3] != 'zbelt']
def skip_static(a, b):
    # model artefacts: the motor model has no tapped holes or shaft flat (its own M3 x 8 screws and the 12T pulley's grubs and bore)
    return 'z motor 17hm19' in a and ('set screw' in b or 'm3x8' in b or 'gt-12t' in b)
rep['static'] = sorted(overlaps(new_solids, STOCK, skip=skip_static), reverse=True)
# contacts Sovol's own model already has: our tensioner seat and block are Sovol's bodies with slots cut, so their overlaps
# with Sovol's springs, screws, idler shaft and top frame seat are inherited; report them apart with the stock value
INHERITED = ('spring', 'idler shaft', 'top fixed seat', 'm3x6 -500 hexagon socket countersunk', 'm3x8')
rep['static_inherited'] = [h for h in rep['static'] if ('tensioner seat' in h[1] or 'tensioner block' in h[1]) and any(k in h[2] for k in INHERITED)]
rep['static'] = [h for h in rep['static'] if h not in rep['static_inherited']]
rep['belts_static'] = sorted(overlaps([p for p in Z if p[3] == 'zbelt'], STOCK, tol=1.0), reverse=True)
rep['internal'] = sorted(overlaps([p for p in Z if p[3] == 'zbelt'], [(n, '', s) for n, m, s, g in new_solids],
                                  tol=1.0, skip=lambda a, b: ('clamped run' in a and ('carriage plate' in b or 'clamp cover' in b)) or 'idler 20t' in b or 'drive pulley 20t' in b), reverse=True)   # runs drawn to the wheel axes
# new Z parts against each other (fixed vs fixed, carriage vs carriage): the purchased wheels sit on their shafts in printed parts
zf = [p for p in Z if p[3] == 'zfixed']; zc = [p for p in Z if p[3] == 'zcarriage']
pairs = []
for grp in (zf, zc):
    for i in range(len(grp)):
        pairs += overlaps([grp[i]], [(n, '', s) for n, m, s, g in grp[i + 1:]], skip=lambda a, b: ('mr105' in a and 'end support' in b) or ('end support' in a and 'mr105' in b))
rep['new_vs_new'] = sorted(pairs, reverse=True)
print('new vs new', len(rep['new_vs_new']), flush=True)
print('static', len(rep['static']), 'inherited from Sovol', len(rep['static_inherited']), 'belts static', len(rep['belts_static']), 'belts vs new parts', len(rep['internal']), flush=True)
# 2. Z sweep of the carriage parts
DZS = [float(d) for d in range(-int(GANTRY_DROP) - 1, int(GANTRY_RISE) + 5, 5)] + [-GANTRY_DROP, GANTRY_RISE]
fixed_all = FIXED + [(n, 'new-fixed', s) for n, m, s, g in Z if g == 'zfixed' or 'free run' in n]
sweep = []
for p in [p for p in Z if p[3] == 'zcarriage']:
    sb = p[2].BoundBox
    cand = [(l, k, t) for l, k, t in fixed_all if t.BoundBox.XMin <= sb.XMax and t.BoundBox.XMax >= sb.XMin and t.BoundBox.YMin <= sb.YMax and t.BoundBox.YMax >= sb.YMin]
    for dz in DZS:
        zc = [(l, k, t) for l, k, t in cand if t.BoundBox.ZMax >= sb.ZMin + dz and t.BoundBox.ZMin <= sb.ZMax + dz]
        if zc:
            sweep += overlaps([p], zc, dz=dz)
rep['carriage_sweep'] = sweep
print('carriage sweep', len(sweep), flush=True)
# 3. the C3 gantry swept past the 12 mm belts and the new fixed Z parts
P, _ = B.build_pose(270.0, -5.0)
gantry = [p for p in P if p[3] in ('frame', 'docks', 'bridge', 'head')]
targets = [(n, 'z', s) for n, m, s, g in Z if g in ('zfixed', 'zbelt')]
gs = []
for p in gantry:
    sb = p[2].BoundBox
    cand = [(l, k, t) for l, k, t in targets if t.BoundBox.XMin <= sb.XMax and t.BoundBox.XMax >= sb.XMin and t.BoundBox.YMin <= sb.YMax and t.BoundBox.YMax >= sb.YMin]
    for dz in DZS:
        zc = [(l, k, t) for l, k, t in cand if t.BoundBox.ZMax >= sb.ZMin + dz and t.BoundBox.ZMin <= sb.ZMax + dz]
        if zc:
            gs += overlaps([p], zc, dz=dz, skip=lambda a, b: False)
agg = {}
for v, n, lab, dz in gs:
    a = agg.setdefault((n, lab), [v, dz, dz]); a[0] = max(a[0], v); a[1] = min(a[1], dz); a[2] = max(a[2], dz)
rep['gantry_sweep'] = sorted([(round(a[0], 1), n, lab, a[1], a[2]) for (n, lab), a in agg.items()], reverse=True)
print('gantry sweep', len(rep['gantry_sweep']), flush=True)
(B.OUT / 'C3_Z_CLEARANCE.json').write_text(json.dumps(rep, indent=1))
for sec in ('static', 'new_vs_new', 'belts_static', 'internal', 'carriage_sweep', 'gantry_sweep'):
    for h in rep[sec][:12]:
        print(sec, h)
