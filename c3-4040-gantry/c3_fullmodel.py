"""The whole SV08 Max as modified for C3: Sovol's model minus the parts that leave or are replaced, plus every new part
(AWD gantry, docks and INDX head at the nominal pose, top hat, camera mount, purge/wipe stations, 12 mm Z upgrade).

New parts are sorted by what the owner does with them; c3_fullmodel_color.json then colours them in SolidCraft:
  PRINT PPS-CF  red     printed in PPS-CF (c3/C3_PPS-CF_Qidi_Plus4_0.6mm.3mf)
  PRINT ASA     orange  the top hat sections (printed, not PPS-CF)
  BUY           yellow  purchased or already owned (motors, pulleys, idlers, bearings, belts, rails and blocks, INDX, Beacon...)
  MACHINE       green   aluminium extrusions cut to length (ends tapped where the BOM says) and the Z drive pulleys
                        (faced down to <= 12.6 mm, or made to size)
Sovol's parts keep their own look; the stock camera is moved to its new mount.
Writes c3/full/SV08_C3_<category>.step (one per category, each part named) for c3_fullmodel_color.json.
Run with FreeCAD's Python, C2_STOCK_CACHE set as for c3_check.
"""
import sys, os, re, json
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0')
import FreeCAD as App, Part, Import
import c3_build as B
import c3_zdrive as ZD

labels = json.loads((B.STOCK_CACHE / 'stock_keep_labels.json').read_text()); kids = Part.read(str(B.STOCK_CACHE / 'stock_keep.brep')).childShapes()
STOCK = [(l, k, s) for (l, k), s in zip(labels, kids)]
# the same removals as c3_check (drag chain plate, camera bracket, filament guide) and c3_zcheck (parts the 12 mm Z replaces)
def gone_c3(l, k, s):                                   # as c3_check / c3_zcheck: drag chain plate, camera, filament guide
    b = s.BoundBox
    if 'drag chain fixing plate' in l or (re.search(r'm3x20|m3x5', l) and -200 < b.XMin and b.XMax < -140 and -60 < b.YMin and b.YMax < -36 and b.ZMin > 160):
        return True
    if 'camera kit' in k:
        return True
    return 'top kit' in k and ('guiding element' in l or 'pu-4 gas pipe fitting' in l or ('m3x14' in l and b.XMax < -330 and 250 < b.YMin < 290))
def replaced(l, k, s):                                  # as c3_zcheck: what the 12 mm Z upgrade replaces
    if 'z axis kit' not in k:
        return False
    b = s.BoundBox
    if 'mounting seat' in l and 'ab' in l and (b.YMin > 594.9 or b.YMax < -47.9):
        return True
    if ('belt pressure plate' in l and b.ZMin > 100) or '2gt-9mm z' in l or 'tensioning wheel mounting bl' in l or 'tensioning wheel mounting se' in l or 'tensioning mounting seat' in l:
        return True
    if 'idler gear' in l or '02001-02-a' in l or '42-40 step motor' in l:
        return True
    if 'set screw' in l and 312 < abs((b.XMin + b.XMax) / 2) < 329 and -130 < b.ZMin and b.ZMax < -110 and (597 < b.YMin < 612 or -65 < b.YMax < -50):
        return True
    if 'm3x10' in l and '70.2' in l and b.ZMin > 100:
        return True
    c = ((b.XMin + b.XMax) / 2, (b.ZMin + b.ZMax) / 2)
    for (cx, cz) in ((ZD.MOTOR_AX[0] + 15.5, ZD.MOTOR_AX[1] + 15.5), (ZD.MOTOR_AX[0] + 15.5, ZD.MOTOR_AX[1] - 15.5)):
        for mxs in (1, -1):
            if re.search(r'm3x', l) and abs(c[0] - mxs * cx) < 2.0 and abs(c[1] - cz) < 2.0 and b.ZMax < -80:
                return True
    return False
block_parts = [s for l, k, s in STOCK if 'z 1 z axis kit' in k and 'tensioning wheel mounting bl' in l]
seat_parts = [s for l, k, s in STOCK if 'z 1 z axis kit' in k and 'tensioning wheel mounting se' in l]
kept = [x for x in STOCK if not gone_c3(*x) and not replaced(*x)]

P, _ = B.build_pose(270.0, -5.0)
P += [(n, m, s, g) for n, m, s, g in ZD.zdrive_parts(block_parts, seat_parts)]

def category(n, m):
    if m == 'pps-cf': return 'PRINT PPS-CF'
    if m == 'asa': return 'PRINT ASA'
    if m.startswith('al-6063') or 'z drive pulley' in n: return 'MACHINE'
    if 'camera stock' in n: return 'SOVOL STOCK'
    return 'BUY'
NOTE = {'side beam': 'cut to 561', 'rear beam': 'cut to 482', 'x beam': 'cut to 556', 'dock rail': 'cut to 588, tap ends M3',
        'station bar': 'cut to 566', 'top hat spine': 'cut to 661', 'z drive pulley': 'face down to <= 12.6 mm or make to size'}
groups = {'SOVOL STOCK': [(f'{l} [sovol stock]', s) for l, k, s in kept]}
for n, m, s, g in P:
    c = category(n, m)
    tag = {'PRINT PPS-CF': 'print PPS-CF', 'PRINT ASA': 'print ASA', 'BUY': 'buy', 'MACHINE': 'machine', 'SOVOL STOCK': 'sovol stock, moved'}[c]
    note = next((v for k, v in NOTE.items() if k in n), '')
    groups.setdefault(c, []).append((f'{n} [{tag}{": " + note if note else ""}]', s))
out = B.OUT / 'full'; out.mkdir(exist_ok=True)
summary = {}
for c, items in groups.items():
    doc = App.newDocument(c.replace(' ', '_').replace('-', '_')); objs = []
    for n, s in items:
        o = doc.addObject('Part::Feature', 'P'); o.Label = n; o.Shape = s; objs.append(o)
    fn = out / f"SV08_C3_{c.replace(' ', '_')}.step"
    Import.export(objs, str(fn)); summary[c] = len(items)
    print(c, len(items), fn.name, flush=True)
(out / 'SV08_C3_CATEGORIES.json').write_text(json.dumps(summary, indent=1))
