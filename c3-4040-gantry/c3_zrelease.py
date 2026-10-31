"""C3 Z upgrade release: one STEP and one STL per printed Z part in print orientation, and the Z BOM.

The front-right and rear-left corners are the same part turned 180 deg (mirrored in X and Y). So are front-left
and rear-right. Each printed part therefore has two variants, A (fr, rl) and B (fl, rr), printed twice each.
Writes c3/print/Z_*.stl|.step and c3/C3_Z_BOM.md|.json. Run with FreeCAD's Python (C2_STOCK_CACHE set).
"""
import sys, os, json
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import c3_zdrive as ZD
V = App.Vector
CACHE = Path(os.environ['C2_STOCK_CACHE'])
OUT = HERE / 'c3'; PRINT = OUT / 'print'; PRINT.mkdir(parents=True, exist_ok=True)
RHO = 1.30

labels = json.loads((CACHE / 'stock_keep_labels.json').read_text()); kids = Part.read(str(CACHE / 'stock_keep.brep')).childShapes()
blk = [s for (l, k), s in zip(labels, kids) if 'z 1 z axis kit' in k and 'tensioning wheel mounting bl' in l]
seat = [s for (l, k), s in zip(labels, kids) if 'z 1 z axis kit' in k and 'tensioning wheel mounting se' in l]
parts = {n: s for n, m, s, g in ZD.zdrive_parts(blk, seat) if m == 'pps-cf'}

def orient(s, rot):
    t = s.copy()
    for ax, deg in rot:
        t.rotate(V(0, 0, 0), V(*ax), deg)
    b = t.BoundBox; t.translate(V(-(b.XMin + b.XMax) / 2, -(b.YMin + b.YMax) / 2, -b.ZMin)); return t

plan = {   # part: (A from 'fr', B from 'fl', rotation for A, rotation for B)
    'z carriage plate': ([], []),                                        # as installed: base down
    'z belt clamp cover': ([((0, 1, 0), 90)], [((0, 1, 0), -90)]),       # outer face down
    'z tensioner block 12mm': ([], []),                                  # as installed, like Sovol's block
    'z tensioner seat 12mm': ([], []),                                   # as installed
    'z motor end support': ([((1, 0, 0), -90)], [((1, 0, 0), -90)]),     # bridge face down
}
rows = []
for name, (ra, rb) in plan.items():
    for var, corner, rot in (('A', 'fr', ra), ('B', 'fl', rb)):
        s = orient(parts[f'{name} {corner}'], rot)
        fn = 'Z_' + name.replace('z ', '', 1).replace(' ', '_').upper() + f'_{var}_PPS-CF'
        s.exportStep(str(PRINT / f'{fn}.step'))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.3, Relative=False).write(str(PRINT / f'{fn}.stl'))
        b = s.BoundBox
        rows.append(dict(part=f'{name} {var} ({"front right + rear left" if var == "A" else "front left + rear right"})', file=fn, qty=2,
                         volume_cm3=round(s.Volume / 1000, 1), mass_g=round(s.Volume / 1000 * RHO, 0),
                         print_size_mm=[round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)], valid=s.isValid(), solids=len(s.Solids)))
        print(rows[-1])
purchased = [
    ('Gates 2MGT 12 mm open belt, Z (loop 1425 mm around 20T + 20T, plus about 30 mm for the clamp ends)', '4 x 1.5 m (1.6 m for margin)'),
    ('StepperOnline 17HM19-2004S1, 0.9 deg, 48 mm, 24 mm full D-cut shaft (owned)', '4'),
    ('20T toothed idler for 12 mm belt, 5 mm bore, flanges <= 16 mm OD, <= 16.4 mm wide (KB3D G2GT-I-20-12 class; check the flange OD)', '4'),
    ('20T 2GT drive pulley for 12 mm belt: 6 mm bore, hubless and flangeless, <= 12.6 mm long, M3 grub through the teeth (custom or modified; see README)', '4'),
    ('MR105ZZ bearing 5 x 10 x 4 (optional motor shaft end support)', '4'),
    ('M3 x 30 SHCS (end supports: replace the two +X motor screws per motor)', '8'),
    ('M3 heat-set insert (carriage plate: 2 arm + 1 cover per corner)', '12'),
    ('M3 x 10 SHCS (clamp covers)', '4'),
    ('Reused from the stock Z: MGW9H block screws, arm M3 x 20, idler shafts, springs, tension screws, cross shafts, reduction pulleys and loops, 12T pulleys, bottom brackets', '-'),
]
bom = {'printed_pps_cf': rows, 'purchased': purchased}
(OUT / 'C3_Z_BOM.json').write_text(json.dumps(bom, indent=1))
md = ['# C3 Z upgrade BOM (12 mm belts, 17HM19-2004S1)', '', '## Printed (PPS-CF, Qidi Plus 4, support-free)', '',
      '| Part | File | Qty | Mass g each | Print size mm |', '|---|---|---|---|---|']
md += [f"| {r['part']} | {r['file']}.stl | {r['qty']} | {r['mass_g']:.0f} | {' x '.join(str(v) for v in r['print_size_mm'])} |" for r in rows]
md += ['', f"Printed total: {sum(r['mass_g'] * r['qty'] for r in rows):.0f} g", '', '## Purchased', '', '| Item | Qty |', '|---|---|']
md += [f'| {a} | {q} |' for a, q in purchased]
(OUT / 'C3_Z_BOM.md').write_text('\n'.join(md) + '\n')
print('printed total g', sum(r['mass_g'] * r['qty'] for r in rows))
