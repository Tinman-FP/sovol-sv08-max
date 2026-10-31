"""C3 reverse idlers: the ordered Gates 2GT 12 mm smooth idler (12 mm belt surface, 15 mm flanges) on the axles laid out
for a 15 mm idler (c3_params.R_S). Pure Python. Writes c3/C3_SMOOTH_IDLER_CHECK.json.
Only the fixed S-bend runs (rear idler -> reverse idler -> rear motor) touch the reverse idler, so the moving runs and the
CoreXY kinematics are unchanged; this reports how far those fixed runs tilt, the wraps and the belt length change."""
import sys, json, math
from pathlib import Path
C = Path(__file__).resolve().parent
sys.path.insert(0, str(C))
import c3_params as P

R = P.R_T
R_GATES = 6.0 + 0.45                     # 12 mm smooth surface + the same backside pitch-line offset as R_S
Y1 = P.YM + 2 * R + 2 * P.R_S            # axles as built (c3_build.y1_rear)
YI2 = Y1 - R - P.R_S

def paths(rs, y_xb, xn):
    yx = y_xb + P.X_RUN_DY
    B = P.solve((xn - P.CLAMP_X, yx), [
        ('joint xn up', (-P.A_RUN + R, yx + R), R, -1), ('motor B2 pulley', (-P.A_RUN - R, P.Y_FM), R, +1),
        ('rear idler xn', (-P.P_RUN + R, Y1), R, +1), ('reverse idler xn', (-P.X_I2, YI2), rs, -1),
        ('motor B pulley', (-P.XM, P.YM), R, +1), ('turn idler xp', (P.A_RUN - R, P.YM), R, +1),
        ('joint xp up', (P.A_RUN - R, yx - R), R, +1)], (xn + P.CLAMP_X, yx))
    A = P.solve((xn + P.CLAMP_X, yx), [
        ('joint xp lo', (P.A_RUN - R, yx + R), R, +1), ('motor A2 pulley', (P.A_RUN + R, P.Y_FM), R, -1),
        ('rear idler xp', (P.P_RUN - R, Y1), R, -1), ('reverse idler xp', (P.X_I2, YI2), rs, +1),
        ('motor A pulley', (P.XM, P.YM), R, -1), ('turn idler xn', (-P.A_RUN + R, P.YM), R, -1),
        ('joint xn lo', (-P.A_RUN + R, yx - R), R, -1)], (xn - P.CLAMP_X, yx))
    return {'B': B, 'A': A}

rep = {'axles': {'rear_idler_y': round(Y1, 2), 'reverse_idler_y': round(YI2, 2), 'reverse_idler_abs_x': P.X_I2},
       'pitch_radius': {'design_15mm': round(P.R_S, 3), 'gates_12mm': R_GATES}, 'poses': [], 'fixed_runs': [], 'wraps': []}
for y_xb, xn in ((P.Y_XB_MIN, -252), (270, 0), (P.Y_XB_DOCK, 252), (P.Y_XB_DOCK, -252)):
    o, n = paths(P.R_S, y_xb, xn), paths(R_GATES, y_xb, xn)
    for k in 'BA':
        rep['poses'].append({'y_xb': y_xb, 'xn': xn, 'belt': k, 'pitch_length_15mm': round(o[k][2], 2),
                             'pitch_length_gates': round(n[k][2], 2), 'change': round(n[k][2] - o[k][2], 2)})
for k in 'BA':
    segs, arcs, _ = paths(R_GATES, 270, 0)[k]; segs0, arcs0, _ = paths(P.R_S, 270, 0)[k]
    for s, s0 in zip(segs, segs0):
        if 'reverse' in s[0] or 'reverse' in s[1]:
            a, a0 = (math.degrees(math.atan2(t[4][1], t[4][0])) for t in (s, s0))
            tilt = (a - a0 + 180) % 360 - 180
            rep['fixed_runs'].append({'belt': k, 'run': f'{s[0]} -> {s[1]}', 'tilt_deg': round(tilt, 2),
                                      'max_shift_mm': round(max(math.dist(s[2], s0[2]), math.dist(s[3], s0[3])), 2)})
    for w, w0 in zip(arcs, arcs0):
        if 'reverse' in w[0] or ('rear idler' in w[0]) or w[0] in ('motor B pulley', 'motor A pulley'):
            rep['wraps'].append({'belt': k, 'wheel': w[0], 'wrap_15mm_deg': round(math.degrees(w0[6]), 1),
                                 'wrap_gates_deg': round(math.degrees(w[6]), 1)})
# axle stacks: M5 spacer below each idler from the plate top, and above it to the cap's underside (c3_build.rear_corner)
W_TOOTHED = 16.0
W_SMOOTH = float(sys.argv[1]) if len(sys.argv) > 1 else 16.0   # measure the delivered idler; 16 mm assumed until then
CAP = max(P.L_UP[1] + 3.5, (P.L_UP[0] + P.L_UP[1]) / 2 + 9.5)
rep['spacers'] = {'smooth_idler_width_assumed': W_SMOOTH, 'cap_underside_z': CAP, 'stacks': []}
for s_, side in ((-1, 'right (xn, motor B)'), (+1, 'left (xp, motor A)')):
    plate = P.MOTOR_FACE_Z[s_] + 7.0
    for name, lvl, w in (('rear toothed idler', P.LEVEL[s_], W_TOOTHED), ('reverse smooth idler', P.LEVEL[s_], W_SMOOTH),
                         ('turn toothed idler', P.LEVEL[-s_], W_TOOTHED)):
        mid = (lvl[0] + lvl[1]) / 2
        rep['spacers']['stacks'].append({'side': side, 'idler': name, 'below_mm': round(mid - w / 2 - plate, 2),
                                         'above_mm': round(CAP - mid - w / 2, 2)})
moving = {p['change'] for p in rep['poses']}
rep['result'] = ('same change at every pose, so the moving runs are unchanged' if len(moving) == 1 else 'length change varies with pose')
(C / 'c3' / 'C3_SMOOTH_IDLER_CHECK.json').write_text(json.dumps(rep, indent=1))
print(json.dumps({k: rep[k] for k in ('fixed_runs', 'wraps', 'result')}, indent=1), '\nbelt change', moving)
for st in rep['spacers']['stacks']:
    print(f"{st['side']:22s} {st['idler']:22s} spacer below {st['below_mm']:5.1f}  above {st['above_mm']:5.1f}")
