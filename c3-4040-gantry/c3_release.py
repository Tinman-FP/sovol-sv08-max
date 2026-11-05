"""C3 (AWD) release files: one STEP and one STL per printed part (print orientation), masses and the BOM.

Writes c3/print/<part>.stl|.step, c3/C3_BOM.json and c3/C3_BOM.md. Run with FreeCAD's Python after c3_build.py.
"""
import sys, os, json, math
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, Mesh, MeshPart
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0'); os.environ['C3_TUBES'] = '0'
import c3_build as B
import c3_routing as RT
from c3_params import *
V = App.Vector
PRINT = B.OUT / 'print'; PRINT.mkdir(exist_ok=True)
RHO = {'pps-cf': 1.30, 'asa': 1.07}       # g/cm3 (solid volume; thin walls print solid anyway)

def orient(s, rot):
    """rot: list of (axis, degrees); then drop the part onto Z 0 and centre it on the plate."""
    t = s.copy()
    for ax, deg in rot:
        t.rotate(V(0, 0, 0), V(*ax), deg)
    b = t.BoundBox; z0 = t.optimalBoundingBox().ZMin   # exact drop: the plain BoundBox can be a mm or two loose on cut parts
    t.translate(V(-(b.XMin + b.XMax) / 2, -(b.YMin + b.YMax) / 2, -z0)); return t

# printed parts in their print orientation (largest flat face down, no supports where the geometry allows)
P, _ = B.build_pose(270.0, 0.0)
by = {n: (s, m) for n, m, s, g in P if m in RHO}
X180 = [((1, 0, 0), 180)]
plan = {'x carriage': [], 'xy joint plate xn': [((0, 1, 0), -90)], 'xy joint plate xp': [((0, 1, 0), 90)],
        'xy joint pulley carrier xn': [((0, 1, 0), 90)], 'xy joint pulley carrier xp': [((0, 1, 0), -90)]}
for t in ('xn', 'xp'):
    plan.update({f'rear corner {t} motor mount': X180, f'rear corner {t} bearing cap': X180, f'rear shaft cover {t}': X180,
                 f'front corner base {t}': [], f'front cradle {t}': [], f'front motor slider {t}': []})
plan.update({'camera mount front right': [((1, 0, 0), 90)],
             'top hat corner front right display': [], 'top hat corner front left': [], 'top hat corner rear right': [],
             'top hat corner rear left': [], 'top hat front': [], 'top hat rear': [], 'top hat side right': [], 'top hat side left': [],
             })
# routing (c3_routing.py, 2026-11-01): one file per distinct part; mirrored left/right parts are separate files
plan.update({'umbilical head saddle': [], 'umbilical roof clamp': X180,
             'chain bracket motor rear right': X180, 'chain bracket motor rear left': X180,
             'chain anchor motor rear right': [], 'chain anchor motor rear left': [],
             'chain entry motor rear right': [], 'chain entry motor rear left': []})
for t in ('xn', 'xp'):                    # purge/wipe stations (c3_purge.py)
    plan.update({f'station bar clip {t}': []})
# the five stations and trays are identical: one print file each, printed five times
plan.update({'wiper station bracket t1': [((1, 0, 0), -90)], 'wiper station slider t1': X180,
             'purge tray': X180})       # rim down: the floor sits on feet, so floor-down would start in mid-air
# (print-file name, quantity, the model's identical copies it stands for)
SAME = {'wiper station bracket t1': ('wiper station bracket', 5, [f'wiper station bracket t{k}' for k in range(2, 6)]),
        'wiper station slider t1': ('wiper station slider', 5, [f'wiper station slider t{k}' for k in range(2, 6)]),
        'chain bracket motor rear right': ('chain bracket motor right', 2, ['chain bracket motor front right']),
        'chain bracket motor rear left': ('chain bracket motor left', 2, ['chain bracket motor front left']),
        'chain anchor motor rear right': ('chain anchor cable right', 2, ['chain anchor motor front right']),
        'chain anchor motor rear left': ('chain anchor cable left', 2, ['chain anchor motor front left']),
        'chain entry motor rear right': ('chain entry cable right', 2, ['chain entry motor front right']),
        'chain entry motor rear left': ('chain entry cable left', 2, ['chain entry motor front left'])}
missing = [k for k in plan if k not in by]; assert not missing, missing
covered = {c for v in SAME.values() for c in v[2]}
unplanned = [n for n in by if n not in plan and n not in covered]
assert not unplanned, unplanned          # every printed part in the model gets a print file
rows = []
for name, rot in plan.items():
    shp, mat = by[name]
    s = orient(shp, rot)
    label, qty = SAME.get(name, (name, 1, []))[:2]
    fn = label.replace(' ', '_').upper() + '_' + mat.upper()
    s.exportStep(str(PRINT / f'{fn}.step'))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.3, Relative=False); m.write(str(PRINT / f'{fn}.stl'))
    b = s.BoundBox
    rows.append(dict(part=label, qty=qty, material=mat, file=fn, volume_cm3=round(s.Volume / 1000, 1), mass_g=round(s.Volume / 1000 * RHO[mat], 0),
                     print_size_mm=[round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)], valid=s.isValid(), solids=len(s.Solids)))
    print(rows[-1])
L = B.build_pose(270.0, 0.0)[1]['A']
bom = {
  'printed': rows,
  'purchased': [
    ('4040 slot 8 extrusion, side beams', f'2 x {SIDE_Y[1]-SIDE_Y[0]:.0f} mm'), ('4040 slot 8 extrusion, X beam', f'1 x {2*XB_HALF:.0f} mm'),
    ('4040 slot 8 extrusion, rear beam', f'1 x {2*REAR_BEAM_HALF:.0f} mm'),
    ('15x15 extrusion (1515), dock rail, ends tapped M3', f'1 x {2*B.DOCK_RAIL["x"]:.0f} mm'),
    ('MGN12 rail, X', f'1 x {2*XR_HALF:.0f} mm'), ('MGN12 rail, Y', f'2 x {YR_Y[1]-YR_Y[0]:.0f} mm'), ('MGN12H carriage block', '3'),
    ('LDO 42STH48-2004MAH(S80) motor, 0.9 deg, 80 mm shaft (owned, set of 4)', '4'),
    ('Gates 2GT 20T 5 mm bore 12 mm pulley (KB3D G2GT-20-5-12)', '4'),
    ('Gates 2GT 20T 12 mm toothed idler (KB3D G2GT-I-20-12)', '8'),
    ('Gates 2GT 12 mm smooth idler (KB3D G2GT-I-S-12), on the axles laid out for 15 mm (c3_idlercheck.py)', '2'), ('625ZZ bearing (double shear, one per motor)', '4'),
    (f'Gates 2MGT 12 mm open belt (needs {L:.0f} mm each incl. clamp tails)', '2 x 2.6 m minimum'),
    ('Bondtech INDX Smart Head, 5 tools, Link Board, Link cable (owned)', '1 kit'), ('Bondtech INDX Tool Dock 1515 with hardware (owned)', '5'),
    ('Beacon Rev H (owned)', '1'), ('Stock SV08 Max camera, reused on the new mount', '1'),
    ('iPistBit 7 inch 1024x600 HDMI touch display (owner, Amazon B0CRRB1GFN), about 165 x 125 x 15 mm', '1'),
    ('Sovol top cover (owned), moved from the frame top to the top hat; drilled at its centre for the umbilical roof clamp', '1'),
    ("PC4-M10 push-fit coupler (owned: BIQU 20 pack), one per tool in the top hat's right side wall (tap the pads M10 x 1 or let the coupler cut its thread)", '5'),
    ('PG9 cable gland, top hat rear wall (display and other cables)', '1'),
    ('Micro cable chain 7 x 7 mm inside, at most 11.5 mm wide outside (it hangs in a 16 mm gap), bend radius 18 mm, one per motor', f'4 x {RT.chain_len():.0f} mm + end links'),
    ('PTFE tube 4 mm OD x 2 mm ID, one continuous length per tool: filament box -> side-wall coupler -> tool', f"5 x {max(RT.line_length(l) for l in RT.TOOL_DOCK) / 1000 + 0.05:.2f} m inside + the run to the filament box"),
    ('Piano (music) wire 1.4 mm for the umbilical (as the Rat Rig V-Core 4; 1.2 mm sags onto belt B at full height)', f"1 x {RT.line_length('umb') / 1000 + 0.1:.1f} m"),
    ('Split loom or braided sleeve 10-13 mm: umbilical (wire, INDX Link cable, Beacon USB)', '1 m'),
    ('INDX Link cable, Link Board (on the top cover) to the head through the umbilical (owned)', f"1 (about {RT.line_length('umb') / 1000 + 0.15:.1f} m needed)"),
    ('Beacon USB cable, head to the USB hub on the top cover, through the umbilical', f"1 (about {RT.line_length('umb') / 1000 + 0.15:.1f} m needed)"),
    ('M5 slot 8 T-nut + M5 x 10 SHCS (chain brackets)', '4'),
    ('M3 x 16 SHCS + M3 nut: chain anchors through the side panels (drill 3.4 mm, with the entry plate as the template)', '8'),
    ('M3 x 8 SHCS: chain end links to their brackets and anchors (check the chain\'s end-link holes)', '16'),
    ('M3 x 12 SHCS + washer + nut: umbilical roof clamp through the top cover (drill 4 x 3.4 mm with the clamp as the template, and 16 mm in the middle for the cables)', '4'),
    ('M3 heat-set insert + M3 x 6 set screw (piano-wire clamps: roof clamp and head saddle)', '2 + 2'),
    ('VHB tape, for the umbilical saddle on the INDX PCB cover', 'a strip'),
    ('Link Board and USB hub on top of the cover beside the cable hole (VHB or your own mount)', '-'),
    ('Zip ties 2.5 mm (umbilical cables to the wire)', '15'),
    ('M5 slot 8 T-nut (28 gantry: rear corners 2 x 5, front cradles 2 x 6, XY joints 2 x 3)', '28'), ('M5 heat-set insert (rear idler axles)', '6'),
    ('M4 heat-set insert (rear caps 4, front cradles 10)', '14'), ('M3 heat-set insert (joints 6, Beacon 2, sliders 2, camera 1, display 4)', '15'),
    ('M5 aluminium spacer 5.2 ID x 8 OD, below and above each rear idler (lengths in c3/C3_SMOOTH_IDLER_CHECK.json)', '11 pieces'),
    ('M5 aluminium sleeve 5.2 ID x 8 OD, cut so each XY-joint idler sits on its belt level (33 mm between the carrier decks minus the idler width)', '4'),
    ('M3 x 8 SHCS (MGN12H blocks)', '12'),
    ('M3 x 10 SHCS + M3 T-nut for 4040 slot 8 (MGN12 rails: X 552 on the X beam, Y 2 x 555 on the side beams; 22 holes per rail at 25 mm pitch, every other hole is acceptable)', '66 + 66'), ('M3 x 10 SHCS (motors 16, joint carriers 6)', '22'), ('M3 x 6 (Beacon)', '2'), ('M3 x 16 SHCS (INDX Smart Head to the X carriage, heads on the back)', '4'),
    ('M3 x 40 SHCS (front tension screws)', '2'), ('M3 x 12 (dock rail ends)', '2'), ('M3 x 10 (camera pinch screw)', '1'),
    ('M3 x 16 SHCS + nut (top hat joints)', '16'), ('M4 x 12 SHCS (rear arms)', '4'), ('M4 x 18 SHCS (front arms, through the base wall)', '4'),
    ('M4 x 35 SHCS (rear bearing caps)', '4'), ('M4 x 12 SHCS + washer (front slider clamps, rear slots)', '4'),
    ('M4 x 16 SHCS + washer (front slider clamps through the base tongues)', '4'), ('M4 x 25 SHCS (dock bracket to cradle)', '2'),
    ('M5 x 10 SHCS (beam T-nuts: rear corners 2 x 4, front cradles 2 x 4, XY joints 2 x 3)', '22'), ('M5 x 20 SHCS (cradle bottom slots)', '4'), ('M5 x 12 SHCS (rear outer slots)', '2'),
    ('M5 x 45 SHCS + nyloc (joint pulley axles)', '4'), ('M5 SHCS for rear idler axles, length to the cap: 3 per corner', '6'),
    ('Zip ties 2.5 mm (camera)', '2'),
    ('Qidi Plus 4 / Q2 silicone nozzle wiper, 27 x 15 x 4.7 mm high (Qidi "Plus4 Wiper Silicone Case", 5 pack: 5 pads, one per station; a second pack for spares)', '2 packs'),
    ('High-temperature red RTV silicone (Permatex Hi-Temp Red or similar), glues the pads into the sliders', '1 tube'),
    ('15x15 extrusion (1515, same profile as the dock rail), station bar, ends plain', '1 x 566 mm'),
    ('3 mm x 20 mm steel dowel pin (wiper slider guides, pressed into the brackets)', '10'),
    ('M3 T-nut for 1515 (station brackets 10, bar clips 2)', '12'), ('M3 x 8 SHCS (station brackets to the bar)', '10'),
    ('M3 x 6 SHCS (bar clips to the bar)', '2'), ('M3 x 8 countersunk FHCS (bar clips to the front cradle webs)', '4'),
    ('M3 heat-set insert, short (3-4 mm long), front cradle inner webs', '4'),
    ('M3 x 8 set screw, cup point (wiper rest-height stops, tapped into the bracket lugs)', '10'),
  ],
}
(B.OUT / 'C3_BOM.json').write_text(json.dumps(bom, indent=1))
md = ['# C3 BOM (AWD 4040 gantry, SV08 Max, INDX, top hat)', '', '## Printed (Qidi Plus 4; PPS-CF unless noted, top hat in ASA)', '', '| Part | Qty | Material | File | Volume cm3 (each) | Mass g (each) | Print size mm |', '|---|---|---|---|---|---|---|']
md += [f"| {r['part']} | {r['qty']} | {r['material'].upper()} | {r['file']}.stl | {r['volume_cm3']} | {r['mass_g']:.0f} | {' x '.join(str(v) for v in r['print_size_mm'])} |" for r in rows]
md += ['', f"Printed total: PPS-CF {sum(r['mass_g'] * r['qty'] for r in rows if r['material']=='pps-cf'):.0f} g, ASA {sum(r['mass_g'] * r['qty'] for r in rows if r['material']=='asa'):.0f} g", '', '## Purchased', '', '| Item | Qty |', '|---|---|']
md += [f'| {a} | {q} |' for a, q in bom['purchased']]
(B.OUT / 'C3_BOM.md').write_text('\n'.join(md) + '\n')
print('printed total g', {m: sum(r['mass_g'] * r['qty'] for r in rows if r['material'] == m) for m in RHO})
