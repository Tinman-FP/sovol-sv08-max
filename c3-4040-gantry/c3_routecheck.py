"""C3 routing check (run with FreeCAD's Python after c3_build.py): the motor chains over the Z travel, and the free PTFE
tubes and the head umbilical at every gantry height.

c3_check.py covers the parts fixed to the frame, the cover or the gantry (chain anchors, entries and brackets, the wall
couplers and the roof clamp) at its seven poses and over the Z sweep. This script adds:
1. Motor chains: each chain's shape at 13 gantry heights from the first layer to 500 mm print height, against the gantry
   (three bridge positions) and the fixed frame, top hat and anchors. Its own anchor and bracket are skipped.
2. Tubes and umbilical, solved as elastic rods (c3_elastica) from their fixed ends: at the first layer and every 50 mm
   of print height up to 500 mm (11 heights; until 2026-11-05 only the first layer, 250 and 500 mm, which missed a
   tube on the top hat's front corner at 350-400 mm), and for each tool on the head in turn at 25 bed positions (a
   5 x 5 grid; the 3 x 3 grid used until 2026-11-04 missed the tubes passing the roof clamp's stalk) and its own dock:
   the active tube, the umbilical and the four parked tubes against the gantry (head, bridge, belts, docks and parked
   tools) and against the fixed frame, top hat, couplers and roof clamp; the arches' tops against the Sovol cover (the
   top hat's top). Each line's first and last 15 mm (its coupler or clamp, and its tool or saddle) are left out.
   Contacts are split in two:
   * clashes: with anything that moves against the line or has edges (head, bridge, belts, docks, the gantry's
     parts, the stock frame, the couplers): these must be none;
   * rubs: a line resting on a smooth printed surface that it slides along (the top hat's walls, the umbilical roof
     clamp's round stalk and plate) or on a parked tool's top. The free tubes carry about 500 mm of spare length at
     full height and lean on these somewhere, as tube does on tube; they are reported, not counted as clashes.
   Tube-on-tube gaps are reported too: free tubes cross and rub, as on any multi-tool printer. They are split by kind
   (parked-parked, active-parked, tube-umbilical) and by how the two meet at the closest point: side by side (within
   30 deg) or crossing.
   Each height runs in its own process (about 25 minutes in all on 12 cores).
3. Each tube's total bend from its coupler to its tool (the capstan angle for friction), and the free lengths.
Writes c3/C3_ROUTE_CHECK.json.
"""
import sys, os, re, json, math, time, subprocess
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part
import numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
os.environ.setdefault('C2_EXPORT', '0'); os.environ['C3_TUBES'] = '0'
import c3_build as B
import c3_routing as RT
import c3_enclosure as ENC
from c3_params import *
V = App.Vector
TOL = 0.2
T0 = time.time()
HEIGHTS = ['first layer'] + [f'{h} mm' for h in range(50, 501, 50)]
def dz_of(name):
    """Gantry offset from the model pose: -GANTRY_DROP at the first layer, +GANTRY_RISE at 500 mm print height."""
    return -GANTRY_DROP if name == 'first layer' else float(name.split()[0]) - (500.0 - GANTRY_RISE)
RUB_PARTS = ('top hat', 'umbilical roof clamp', 'indx tool parked')
is_rub = lambda part: part.startswith(RUB_PARTS)
WORKER = sys.argv[sys.argv.index('--height') + 1] if '--height' in sys.argv else None

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

def line_hits(Q, r, items, chunk=10):
    """Tube of radius r along the points Q against (name, shape, bbox) items, 10 cylinders (60 mm) at a time so each
    chunk's box only meets the parts near it. Returns {name: volume}."""
    out = {}
    segs = [(a, b) for a, b in zip(Q[:-1], Q[1:]) if np.linalg.norm(b - a) > 1e-6]
    for i in range(0, len(segs), chunk):
        ch = segs[i:i + chunk]
        pts = np.array([p for ab in ch for p in ab]); lo, hi = pts.min(axis=0) - r, pts.max(axis=0) + r
        bb = App.BoundBox(*lo, *hi)
        cands = [(n, t) for n, t, tb in items if n not in out and bb.intersect(tb)]
        if not cands:
            continue
        sol = Part.makeCompound([Part.makeCylinder(r, float(np.linalg.norm(b - a)), V(*a), V(*(b - a))) for a, b in ch])
        for n, t in cands:
            try:
                v = sol.common(t).Volume
            except Exception:
                v = -1.0
            if v > TOL or v < 0:
                out[n] = round(v, 2)
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

P0, _ = B.build_pose(270.0, 0.0)
ENCL = [(n, s) for n, m, s, g in P0 if g == 'enclosure']
MOVING_G = ('frame', 'bridge', 'head', 'docks', 'belts')
R = {'umb': 6.0}
r_of = lambda line: R.get(line, 2.0)
def trimmed(X):
    return RT.resample(X, 3.0)[5:-5]                            # leave out the clamp and the end (15 mm each)

# ---------------------------------------------------------------- 2. tubes and umbilical at one height (a worker)
def run_height(zname):
    dz = dz_of(zname)
    out = dict(lines=[], cover=[], not_converged=[], top={}, bends={l: [] for l in RT.TOOL_DOCK}, gaps=[])
    FIXED = [(n, s, s.BoundBox) for n, s in STOCK + ENCL]
    STATIC_MOV = [(n, s, s.BoundBox) for n, m, s, g in P0 if g in ('frame', 'docks')]   # ride on the gantry, same at every XY
    bed = [(x, y) for x in (-252.0, -126.0, 0.0, 126.0, 252.0) for y in (64.4, 190.0, 314.0, 440.0, 563.5)]
    poses = [('bed', x, y - NOZZLE_DY, None) for x, y in bed] + [('dock', DOCK_X[k], Y_XB_DOCK, line) for line, k in RT.TOOL_DOCK.items()]

    def record(line, X, where, items_moving):
        """Check one line shape: moving items in gantry coordinates (the line is shifted by -dz), fixed items as is."""
        Q = trimmed(X); r = r_of(line)
        out['top'][line] = max(out['top'].get(line, -1e9), float(X[:, 2].max()) + r)
        if X[:, 2].max() + r > RT.ROOF_Z:
            out['cover'].append(dict(line=line, **where, over=round(float(X[:, 2].max()) + r - RT.ROOF_Z, 1)))
        for n, v in line_hits(Q - np.array([0.0, 0.0, dz]), r, items_moving).items():
            out['lines'].append(dict(line=line, **where, vol=v, part=n))
        for n, v in line_hits(Q, r, FIXED).items():
            out['lines'].append(dict(line=line, **where, vol=v, part=n, fixed=True))

    def solve(line, end, where):
        X, ok = RT.line_nodes(line, end)
        if not ok:
            out['not_converged'].append(dict(line=line, **where))
        return X

    # parked tubes: depend only on the gantry height; checked against the static gantry parts here, the head per pose below
    parked = {}
    for line, k in RT.TOOL_DOCK.items():
        where = dict(height=zname, tool=line, head='parked')
        X = solve(line, RT.tool_end(DOCK_X[k], Y_XB_DOCK, True, dz), where); parked[line] = X
        record(line, X, where, STATIC_MOV); out['bends'][line].append(RT.total_bend(X))
    for kind, xn, y_xb, own in poses:
        P, _ = B.build_pose(y_xb, xn, with_static=False)
        HEADG = [(n, s, s.BoundBox) for n, m, s, g in P if g in ('bridge', 'head', 'belts')]
        pos = (kind, xn, round(y_xb + NOZZLE_DY, 1))
        X = solve('umb', RT.umb_end(xn, y_xb, dz), dict(height=zname, pose=pos))
        record('umb', X, dict(height=zname, line_to='head', pose=pos), STATIC_MOV + HEADG)
        for pl, Xp in parked.items():                           # parked tubes against the head here (the rest: above)
            if pl == own:
                continue
            for n, v in line_hits(trimmed(Xp) - np.array([0.0, 0.0, dz]), r_of(pl), HEADG).items():
                out['lines'].append(dict(line=pl, height=zname, tool=pl, head='parked', pose=pos, vol=v, part=n))
        for line, k in RT.TOOL_DOCK.items():
            if kind == 'dock' and line != own:
                continue                                       # at a dock only that dock's tool is picked up
            where = dict(height=zname, tool=line, head=pos)
            Xa = solve(line, RT.tool_end(xn, y_xb, False, dz), where)
            record(line, Xa, where, STATIC_MOV + HEADG); out['bends'][line].append(RT.total_bend(Xa))
            S = dict(parked); S.pop(line); S[line + ' active'] = Xa; S['umb'] = X
            names = list(S)
            for i in range(len(names)):                         # tube-on-tube: centreline gap minus both radii
                for j in range(i + 1, len(names)):
                    a, b = trimmed(S[names[i]]), trimmed(S[names[j]])
                    Dm = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
                    p, q = np.unravel_index(np.argmin(Dm), Dm.shape); d = float(Dm[p, q])
                    ta = a[min(p + 1, len(a) - 1)] - a[max(p - 1, 0)]; tb = b[min(q + 1, len(b) - 1)] - b[max(q - 1, 0)]
                    ang = math.degrees(math.acos(min(1.0, abs(float(ta @ tb)) / (np.linalg.norm(ta) * np.linalg.norm(tb)))))
                    ri = r_of(names[i].split()[0]); rj = r_of(names[j].split()[0])
                    out['gaps'].append((round(d - ri - rj, 1), zname, line, pos, names[i], names[j], round(ang)))
    out['free_length_mm'] = {k: round(v) for k, v in RT._LEN.items()}
    return out

if WORKER:
    res = run_height(WORKER)
    Path(sys.argv[sys.argv.index('--out') + 1]).write_text(json.dumps(res, default=str))
    print('height', WORKER, 'lines', len(res['lines']), round(time.time() - T0), 's', flush=True)
    sys.exit(0)

# ---------------------------------------------------------------- the heights, each in its own process
TMP = B.OUT / '_cache' / 'routecheck'; TMP.mkdir(parents=True, exist_ok=True)
NPROC = max(1, min(len(HEIGHTS), (os.cpu_count() or 4) - 2))
queue = list(HEIGHTS); running = {}; parts = {}
def launch():
    while queue and len(running) < NPROC:
        h = queue.pop(0); f = TMP / (h.replace(' ', '_') + '.json')
        if f.exists() and os.environ.get('C3_RC_REUSE') == '1':      # rerun the merge only, from the last workers' results
            parts[h] = json.loads(f.read_text()); continue
        if f.exists():
            f.unlink()
        log = open(TMP / (h.replace(' ', '_') + '.log'), 'w')
        running[h] = (subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--height', h, '--out', str(f)], stdout=log, stderr=subprocess.STDOUT), f, log)
launch()

# ---------------------------------------------------------------- 1. motor chains over the Z travel (meanwhile, here)
rep = {'note': __doc__.split('\n')[0], 'heights': HEIGHTS, 'chains': [], 'clashes': [], 'rubs': [], 'cover': [], 'not_converged': [],
       'loop_top': {}, 'cover_underside': round(RT.ROOF_Z, 1), 'crossings': {}, 'free_length_mm': {}, 'bend_deg': {}}
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
            own = n.replace('cable chain ', '')
            for h in hits(c, mv + (fixed_side if y_xb == 270.0 else []), lambda x, own=own: x.endswith(own)):
                rep['chains'].append(dict(chain=n, dz=round(dz, 1), y_xb=y_xb, vol=h[0], part=h[1]))
    print('chains at y_xb', y_xb, 'clashes so far', len(rep['chains']), round(time.time() - T0), 's', flush=True)

while running or queue:
    for h, (p, f, log) in list(running.items()):
        if p.poll() is not None:
            log.close(); del running[h]
            if p.returncode != 0 or not f.exists():
                raise SystemExit(f'height {h} failed (exit {p.returncode}); see {TMP}')
            parts[h] = json.loads(f.read_text())
            print('height', h, 'done:', len(parts[h]['lines']), 'contacts', round(time.time() - T0), 's', flush=True)
    launch()
    time.sleep(2.0)

# ---------------------------------------------------------------- merge
top, bends, gaps = {}, {l: [] for l in RT.TOOL_DOCK}, []
for h in HEIGHTS:
    r = parts[h]
    for x in r['lines']:
        (rep['rubs'] if is_rub(x['part']) else rep['clashes']).append(x)
    rep['cover'] += r['cover']; rep['not_converged'] += r['not_converged']
    for k, v in r['top'].items():
        top[k] = max(top.get(k, -1e9), v)
    for k, v in r['bends'].items():
        bends[k] += v
    gaps += [tuple(g) for g in r['gaps']]
    rep['free_length_mm'] = r['free_length_mm']
rep['loop_top'] = {k: round(v, 1) for k, v in top.items()}
rep['bend_deg'] = {k: [round(min(v)), round(max(v))] for k, v in bends.items()}
count = lambda L: dict(sorted({p: sum(1 for x in L if x['part'] == p) for p in {x['part'] for x in L}}.items(), key=lambda kv: -kv[1]))
rep['rubs_by_part'] = count(rep['rubs']); rep['clashes_by_part'] = count(rep['clashes'])
touch = [g for g in gaps if g[0] < 0]
kind_of = lambda g: 'tube-umbilical' if 'umb' in (g[4], g[5]) else 'active-parked' if 'active' in g[4] + g[5] else 'parked-parked'
rep['crossings'] = dict(pairs_checked=len(gaps), touching=len(touch), min_gap=min(g[0] for g in gaps),
                        touching_by_height={z: sum(1 for g in touch if g[1] == z) for z in HEIGHTS},
                        parked_pairs_touching=sorted({(g[1], g[4], g[5]) for g in touch if 'active' not in g[4] + g[5] and 'umb' not in (g[4], g[5])}),
                        touching_by_kind={k: sum(1 for g in touch if kind_of(g) == k) for k in ('parked-parked', 'active-parked', 'tube-umbilical')},
                        crossing=sum(1 for g in touch if g[6] >= 30),
                        parked_crossing=sum(1 for g in touch if kind_of(g) == 'parked-parked' and g[6] >= 30),
                        worst=sorted(touch)[:12])
(B.OUT / 'C3_ROUTE_CHECK.json').write_text(json.dumps(rep, indent=1, default=str))
print('chains', len(rep['chains']), 'clashes', len(rep['clashes']), 'rubs', len(rep['rubs']), 'over the cover', len(rep['cover']), 'not converged', len(rep['not_converged']))
print('rubs by part', rep['rubs_by_part']); print('clashes by part', rep['clashes_by_part'])
print('loop tops', rep['loop_top'], 'cover underside', rep['cover_underside'])
print('free lengths', rep['free_length_mm'], 'bend (deg)', rep['bend_deg'])
print('crossings', {k: v for k, v in rep['crossings'].items() if k != 'worst'})
for sec in ('chains', 'clashes', 'rubs', 'cover', 'not_converged'):
    for h in rep[sec][:30]:
        print(sec, h)
print('done', round(time.time() - T0), 's')
