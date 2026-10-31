#!/usr/bin/env python3
"""Offline checks for the SV08 Max C3 Klipper/Kalico config. Reads files only; never talks to a printer.

Checks:
  1. parse      - Klipper-style include resolution and parsing (later sections override earlier ones)
  2. options    - every option in every section is read by the mainline Klipper / indx_klipper / Beacon module that owns it
  3. pins       - Kraken pins are valid STM32H723 pins and none is used twice (SPI bus pins excepted);
                  indxmcu pins are aliases Bondtech's indx_klipper module registers
  3b. homing    - c3_homing.cfg's [homing_override] is Bondtech's, except G28 X / G28 Y -> _C3_HOME_AXIS
  4. templates  - every G-code template compiles with Klipper's Jinja settings
  5. behaviour  - the C3 macros rendered against a mocked printer: START_PRINT order, chamber HVAC
                  decisions, heat-soak comparison, Z home source, fans, and a move-by-move simulation of
                  the wiper-station macros against the front keep-out

Usage:
  check_config.py CONFIG_DIR --klippy KLIPPER_KLIPPY_DIR --indx INDX_KLIPPER_HOST_DIR --beacon BEACON_PY --mainsail CLIENT_CFG [--json OUT]
"""
import argparse, ast, configparser, glob, json, os, re, shlex, sys
import jinja2

# ------------------------------------------------------------------ 1. parse
def read_config(path, mainsail):
    """Klipper's configfile: includes are expanded in place, files read in order into one parser."""
    parser = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(';', '#'))
    origin, order = {}, []
    def parse_file(fn, visited):
        fn = os.path.abspath(fn)
        if fn in visited:
            raise RuntimeError('recursive include ' + fn)
        visited = visited | {fn}
        buf = []
        def flush():
            if buf:
                text = '\n'.join(buf)
                before = {s: set(parser.options(s)) if parser.has_section(s) else set() for s in parser.sections()}
                parser.read_string(text, fn)
                for s in parser.sections():
                    if re.search(r'^\[\s*' + re.escape(s) + r'\s*\]', text, re.M):
                        origin.setdefault(s, []).append(os.path.basename(fn))
                buf.clear()
        for line in open(fn).read().split('\n'):
            m = re.match(r'^\s*\[include\s+(.+?)\]\s*$', line)
            if m:
                flush()
                inc = m.group(1)
                target = mainsail if inc == 'mainsail.cfg' else os.path.join(os.path.dirname(fn), inc)
                for f in sorted(glob.glob(target)) or [None]:
                    if f is None:
                        raise RuntimeError('include not found: ' + inc)
                    order.append(os.path.basename(f))
                    parse_file(f, visited)
            else:
                buf.append(line)
        flush()
    order.append(os.path.basename(path))
    parse_file(path, set())
    return parser, origin, order

# ------------------------------------------------------------------ 2. options
OPT_RE = re.compile(r"""\.(?:get|getint|getfloat|getboolean|getchoice|getlist|getintlist|getfloatlist|getlists|get_float|get_int)\(\s*['"]([A-Za-z0-9_]+)['"]""")
# Helper-style reads: floatParamHelper(config, "x"), load_template(config, "x"), parse_config_pair(config, "x")
HELPER_RE = re.compile(r"""\(\s*config\s*,\s*['"]([A-Za-z0-9_]+)['"]""", re.S)
FSTR_RE = re.compile(r"""\.(?:get|getint|getfloat|getboolean|getchoice|getlist|getintlist|getfloatlist|getlists)\(\s*f?['"]([A-Za-z0-9_]*)(?:%[sd]|\{)""")

def module_options(files):
    opts, prefixes = set(), set()
    for f in files:
        if not os.path.exists(f):
            raise RuntimeError('missing source ' + f)
        t = open(f).read()
        opts |= {o.lower() for o in OPT_RE.findall(t)}
        opts |= {o.lower() for o in HELPER_RE.findall(t)}
        prefixes |= {p.lower() for p in FSTR_RE.findall(t) if p}
    return opts, prefixes

def section_sources(sec, K, beacon, IX):
    e = lambda *n: [os.path.join(K, 'extras', x) for x in n]
    stepper = [os.path.join(K, 'stepper.py')]
    temp = e('heaters.py', 'thermistor.py', 'adc_temperature.py', 'temperature_mcu.py', 'temperature_host.py') + \
        [os.path.join(IX, x) for x in ('sensors.py', 'heater.py', '__init__.py')]
    fan = e('fan.py', 'pulse_counter.py')
    kind = sec.split()[0]
    table = {
        'printer': [os.path.join(K, 'toolhead.py'), os.path.join(K, 'kinematics', 'corexy.py')],
        'mcu': [os.path.join(K, 'mcu.py')],
        'extruder': [os.path.join(K, 'kinematics', 'extruder.py')] + stepper + temp,
        'heater_bed': e('heater_bed.py') + temp, 'heater_generic': e('heater_generic.py') + temp,
        'verify_heater': e('verify_heater.py'), 'thermistor': e('thermistor.py'),
        'temperature_sensor': e('temperature_sensor.py') + temp,
        'fan': fan, 'fan_generic': e('fan_generic.py') + fan, 'heater_fan': e('heater_fan.py') + fan,
        'controller_fan': e('controller_fan.py') + fan, 'output_pin': e('output_pin.py'),
        'tmc5160': e('tmc5160.py', 'tmc.py', 'tmc2130.py', 'bus.py'), 'tmc2240': e('tmc2240.py', 'tmc.py', 'tmc2130.py', 'bus.py'),
        'bed_mesh': e('bed_mesh.py'), 'quad_gantry_level': e('quad_gantry_level.py', 'z_tilt.py', 'probe.py'),
        'gcode_macro': e('gcode_macro.py'), 'delayed_gcode': e('delayed_gcode.py'), 'homing_override': e('homing_override.py'),
        'idle_timeout': e('idle_timeout.py'), 'resonance_tester': e('resonance_tester.py'), 'input_shaper': e('input_shaper.py', 'shaper_defs.py'),
        'gcode_arcs': e('gcode_arcs.py'), 'force_move': e('force_move.py'), 'exclude_object': e('exclude_object.py'),
        'save_variables': e('save_variables.py'), 'respond': e('respond.py'), 'virtual_sdcard': e('virtual_sdcard.py'),
        'pause_resume': e('pause_resume.py'), 'display_status': e('display_status.py'),
        'neopixel': e('neopixel.py'), 'lis2dw': e('lis2dw.py', 'bus.py'), 'angle': e('angle.py', 'bus.py'),
        'load_cell_probe': e('load_cell_probe.py', 'load_cell.py', 'ads131m0x.py', 'probe.py', 'bus.py'),
        'indx': [os.path.join(IX, x) for x in os.listdir(IX) if x.endswith('.py')],
        'beacon': [beacon],
    }
    if re.match(r'stepper_[xyz]\d*$', kind):
        return stepper
    return table.get(kind)

# Options built from loops or helper calls that the regex cannot see, checked by hand in the sources
DYNAMIC = [r'temperature\d', r'resistance\d', r'pid_k[pid]', r'variable_.+', r'driver_[a-z0-9_]+', r'shaper_(type|freq)_[xy]',
           r'damping_ratio_[xy]', r'spi_(bus|speed|software_[a-z]+_pin)', r'i2c_(mcu|bus|address|speed)', r'cs_pin', r'run_current', r'hold_current',
           r'sense_resistor', r'interpolate', r'stealthchop_threshold', r'microsteps', r'step_pin', r'dir_pin', r'enable_pin',
           r'rotation_distance', r'full_steps_per_rotation', r'gear_ratio', r'endstop_pin', r'position_(endstop|min|max)',
           r'homing_(speed|retract_dist|retract_speed|positive_dir)', r'second_homing_speed', r'gcode', r'description', r'rename_existing',
           r'tachometer_(pin|ppr|poll_interval)', r'sensor_(type|pin)', r'pullup_resistor', r'min_temp', r'max_temp', r'serial', r'restart_method',
           r'samples(_result|_tolerance|_tolerance_retries)?', r'sample_retract_dist', r'lift_speed', r'speed', r'horizontal_move_z', r'points',
           r'chain_count', r'pin', r'rref']

def check_options(parser, K, beacon, IX):
    unknown, unchecked, cache = [], [], {}
    for sec in parser.sections():
        src = section_sources(sec, K, beacon, IX)
        if src is None:
            unchecked.append(sec)
            continue
        key = tuple(src)
        if key not in cache:
            cache[key] = module_options(src)
        opts, prefixes = cache[key]
        for o in parser.options(sec):
            if o in opts or any(o.startswith(p) for p in prefixes) or any(re.fullmatch(d, o) for d in DYNAMIC):
                continue
            unknown.append(f'[{sec}] {o}')
    return unknown, unchecked

# ------------------------------------------------------------------ 3. pins
STM_PIN = re.compile(r'^P[A-G](?:[0-9]|1[0-5])$')
def strip_pin(v):
    return v.strip().lstrip('^~!').strip()

def check_pins(parser, IX):
    used, errors, indx_pins = {}, [], []
    aliases = set(re.findall(r'alias_pin\(\s*["\']([a-z0-9_]+)["\']', open(os.path.join(IX, 'toolboard.py')).read()))
    for sec in parser.sections():
        for o in parser.options(sec):
            if not (o == 'pin' or o.endswith('_pin')) or o.startswith('spi_software_'):
                continue
            v = strip_pin(parser.get(sec, o))
            if ':' in v:
                chip, name = [x.strip() for x in v.split(':', 1)]
                if chip == 'indxmcu':
                    indx_pins.append(name)
                    if name not in aliases:
                        errors.append(f'[{sec}] {o}: indxmcu:{name} is not an indx_klipper alias')
                    used.setdefault(v.replace(' ', ''), []).append(f'[{sec}] {o}')
                continue
            if not STM_PIN.match(v):
                errors.append(f'[{sec}] {o}: "{v}" is not an STM32H723 pin')
                continue
            used.setdefault(v, []).append(f'[{sec}] {o}')
    dupes = {p: s for p, s in used.items() if len(s) > 1}
    return used, dupes, errors, sorted(set(indx_pins)), sorted(aliases)

# ------------------------------------------------------------------ 3b. homing override fidelity
def check_homing(parser, config_dir):
    bt = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(';', '#'))
    bt.read(os.path.join(config_dir, 'indx', 'homing.cfg'))
    want = bt.get('homing_override', 'gcode').replace('\nG28 Y\n', '\n_C3_HOME_AXIS AXIS=Y\n').replace('\nG28 X\n', '\n_C3_HOME_AXIS AXIS=X\n')
    have = parser.get('homing_override', 'gcode')
    same = want == have and bt.get('homing_override', 'axes') == parser.get('homing_override', 'axes')
    return {'identical_except_g28_xy': same, 'g28_xy_left': [l for l in have.splitlines() if l.strip() in ('G28 X', 'G28 Y')]}

# ------------------------------------------------------------------ 4. templates
ENV = jinja2.Environment('{%', '%}', '{', '}', extensions=['jinja2.ext.do'])
STRICT = jinja2.Environment('{%', '%}', '{', '}', extensions=['jinja2.ext.do'], undefined=jinja2.StrictUndefined)
TEMPLATE_OPTS = re.compile(r'^(gcode|.*_gcode)$')

def check_templates(parser):
    bad, count = [], 0
    for sec in parser.sections():
        for o in parser.options(sec):
            if TEMPLATE_OPTS.match(o):
                count += 1
                try:
                    ENV.from_string(parser.get(sec, o))
                except jinja2.TemplateSyntaxError as ex:
                    bad.append(f'[{sec}] {o}: line {ex.lineno}: {ex.message}')
    return count, bad

# ------------------------------------------------------------------ 5. behaviour
class MacroError(Exception):
    pass

def raise_error(msg):
    raise MacroError(msg)

class Sim:
    """Renders C3 macros against a mocked printer, expands nested C3 macros, and tracks the toolhead."""
    EXPAND = re.compile(r'^(_?C3_[A-Z0-9_]+|START_PRINT|END_PRINT|M10[67]|M14[01]|M191|_INDX_HOME_Z_PROBE|LIGHTS_[A-Z]+)$')
    NO_EXPAND = {'_C3_CAL_TOOL_Z_STORE'}

    def __init__(self, parser, state, expand=True):
        self.p, self.state, self.expand = parser, state, expand
        self.out, self.moves = [], []
        self.abs = True
        self.saved = {}
        self.macros = {}
        for sec in parser.sections():
            if sec.startswith('gcode_macro '):
                name = sec.split(None, 1)[1].upper()
                var = {o[9:]: ast.literal_eval(parser.get(sec, o)) for o in parser.options(sec) if o.startswith('variable_')}
                self.macros[name] = (sec, var)
                state.setdefault('gcode_macro ' + name, {}).update({k: v for k, v in var.items() if k not in state.get('gcode_macro ' + name, {})})

    def render(self, name, params):
        sec, _ = self.macros[name]
        ctx = {'printer': self.state, 'params': params, 'rawparams': ' '.join(f'{k}={v}' for k, v in params.items()),
               'action_raise_error': raise_error, 'action_respond_info': lambda m: '', 'action_emergency_stop': raise_error}
        ctx.update(self.state['gcode_macro ' + name])
        return STRICT.from_string(self.p.get(sec, 'gcode')).render(ctx)

    def run(self, name, params=None, depth=0):
        for raw in self.render(name, params or {}).split('\n'):
            line = raw.strip()
            if not line:
                continue
            cmd, _, rest = line.partition(' ')
            cmd = cmd.upper()
            args = {}
            if rest and cmd not in ('M117', 'RESPOND'):
                try:
                    toks = shlex.split(rest)
                except ValueError as ex:
                    raise MacroError(f'unparseable arguments in "{line}": {ex}')
                for tok in toks:
                    if '=' in tok:
                        k, v = tok.split('=', 1)
                        args[k.upper()] = v
                    elif re.match(r'^[A-Z][-0-9.]', tok.upper()):
                        args[tok[0].upper()] = tok[1:]
            elif cmd == 'RESPOND':
                shlex.split(rest)
            self.out.append((depth, line))
            if self.expand and self.EXPAND.match(cmd) and cmd in self.macros and cmd not in self.NO_EXPAND and depth < 6:
                self.run(cmd, args, depth + 1)
            else:
                self.apply(cmd, args)

    def apply(self, cmd, a):
        th, gm, st = self.state['toolhead'], self.state['gcode_move'], self.state
        if cmd == 'G90':
            self.abs = True
        elif cmd == 'G91':
            self.abs = False
        elif cmd in ('G0', 'G1'):
            o = gm['homing_origin']
            start = dict(th['position'])
            for ax in 'xyz':
                if ax.upper() in a:
                    v = float(a[ax.upper()])
                    th['position'][ax] = (v + o[ax]) if self.abs else th['position'][ax] + v
            if 'E' in a:
                st.setdefault('_extruded', []).append(float(a['E']))
            self.moves.append((start, dict(th['position']), cmd))
        elif cmd == 'SAVE_GCODE_STATE':
            self.saved[a.get('NAME')] = self.abs
        elif cmd == 'RESTORE_GCODE_STATE':
            self.abs = self.saved.get(a.get('NAME'), True)
        elif cmd == 'SET_GCODE_VARIABLE':
            st['gcode_macro ' + a['MACRO'].upper()][a['VARIABLE'].lower()] = ast.literal_eval(a['VALUE'])
        elif cmd == 'SAVE_VARIABLE':
            st['save_variables']['variables'][a['VARIABLE'].lower()] = ast.literal_eval(a['VALUE'])
        elif cmd == 'SET_FAN_SPEED':
            st['fan_generic ' + a['FAN']]['speed'] = float(a['SPEED'])
        elif cmd == 'SET_HEATER_TEMPERATURE':
            st['heater_generic ' + a['HEATER']]['target'] = float(a['TARGET'])

def base_state(parser):
    s = {
        'toolhead': {'position': {'x': 300.0, 'y': 200.0, 'z': 20.0, 'e': 0.0}, 'homed_axes': 'xyz',
                     'axis_minimum': {'x': -5.6, 'y': -5.0, 'z': -5.0}, 'axis_maximum': {'x': 499.5, 'y': 502.1, 'z': 495.0}},
        'gcode_move': {'homing_origin': {'x': 0.2, 'y': -0.15, 'z': 0.05}, 'gcode_position': {'x': 300.0, 'y': 200.0, 'z': 20.0}},
        'save_variables': {'variables': {'active_tool': 0}},
        'extruder': {'temperature': 240.0, 'target': 240.0},
        'heater_bed': {'temperature': 100.0, 'target': 100.0},
        'heater_generic chamber_temp': {'temperature': 25.0, 'target': 0.0, 'power': 0.0},
        'fan_generic chamber_circulation': {'speed': 0.0}, 'fan_generic exhaust_fan': {'speed': 0.0},
        'output_pin chamber_light': {'value': 1.0},
        'quad_gantry_level': {'applied': True},
        'bed_mesh': {'probed_matrix': [[0.0, 0.01], [0.02, 0.03]], 'profile_name': ''},
        'probe': {'last_z_result': 0.012},
        'beacon': {'model': 'default', 'last_probe_result': 'ok'},
        'configfile': {'warnings': [], 'settings': {
            'extruder': {'min_extrude_temp': 170.0, 'max_temp': 350.0},
            'heater_bed': {'max_temp': 110.0},
            'beacon': {'contact_max_hotend_temperature': 180.0}}},
    }
    tp = {o[9:]: ast.literal_eval(parser.get('gcode_macro TOOL_POSITIONS', o)) for o in parser.options('gcode_macro TOOL_POSITIONS') if o.startswith('variable_')}
    s['gcode_macro TOOL_POSITIONS'] = tp
    s['gcode_macro _INDX_HOME_Z'] = {'z_faked': 0}
    s['gcode_macro _TOOLCHANGE_VARS'] = {'homing_busy': 0}
    return s

def behaviour(parser):
    results = []
    def case(name, fn):
        try:
            fn()
            results.append({'case': name, 'ok': True})
        except AssertionError as ex:
            results.append({'case': name, 'ok': False, 'detail': str(ex)})
        except MacroError as ex:
            results.append({'case': name, 'ok': False, 'detail': 'macro error: ' + str(ex)})

    def lines(sim):
        return [l for _, l in sim.out]

    def order_of(ls, items):
        idx, pos = [], 0
        for it in items:
            found = next((i for i in range(pos, len(ls)) if ls[i].startswith(it)), None)
            assert found is not None, f'"{it}" missing or out of order after line {pos}'
            idx.append(found)
            pos = found + 1
        return idx

    def start_abs():
        st = base_state(parser)
        sim = Sim(parser, st, expand=False)
        sim.run('START_PRINT', {'BED': '100', 'TOOL': '2', 'TEMP': '270', 'FILAMENT': 'PC'})
        ls = lines(sim)
        order_of(ls, ['M140 S100', 'G28', 'M190 S100', 'M191 S55', 'QUAD_GANTRY_LEVEL', '_C3_ADAPTIVE_HEAT_SOAK ADAPTIVE=1',
                      'QUAD_GANTRY_LEVEL', '_C3_CONTACT_GATE', '_C3_FINAL_Z_HOME', 'BED_MESH_CALIBRATE ADAPTIVE=1',
                      '_C3_FINAL_GEOMETRY_GATE', 'CHANGE_TOOL TOOL=2 TEMP=270', 'M109 S270', 'C3_PURGE'])
        assert any(l.startswith('SET_GCODE_VARIABLE MACRO=_C3_CHAMBER_STATE VARIABLE=cap VALUE=0') for l in ls), 'cap not cleared for a heated chamber'
    case('START_PRINT, PC: bed first, chamber 55 after the bed, soak, gates, mesh, tool, purge in order', start_abs)

    def start_pla():
        st = base_state(parser)
        sim = Sim(parser, st, expand=False)
        sim.run('START_PRINT', {'BED': '60', 'TOOL': '0', 'TEMP': '215', 'FILAMENT': 'PLA', 'CHAMBER': '0'})
        ls = lines(sim)
        assert 'M141 S0' in ls and not any(l.startswith('M191') for l in ls), 'PLA should not heat the chamber'
        assert not any(l.startswith('_C3_ADAPTIVE_HEAT_SOAK') for l in ls), 'no heat soak without chamber heat'
        assert 'SET_GCODE_VARIABLE MACRO=_C3_CHAMBER_STATE VARIABLE=cap VALUE=35.0' in ls, 'PLA ceiling 35 C not set'
    case('START_PRINT, PLA: no chamber heat, no soak, 35 C ceiling', start_pla)

    def start_slicer_chamber():
        st = base_state(parser)
        sim = Sim(parser, st, expand=False)
        sim.run('START_PRINT', {'BED': '100', 'TOOL': '1', 'TEMP': '255', 'FILAMENT': 'ABS', 'CHAMBER': '70'})
        assert 'M191 S55.0' in lines(sim), 'slicer chamber 70 must be capped to 55'
    case('START_PRINT: slicer CHAMBER=70 is capped at 55 C', start_slicer_chamber)

    for label, params, expect in (('TOOL=5 (only T0-T4)', {'BED': '60', 'TOOL': '5', 'TEMP': '215'}, 'not configured'),
                                  ('TEMP=320 (INDX 300 C limit)', {'BED': '60', 'TOOL': '0', 'TEMP': '320'}, 'INDX limit'),
                                  ('BED=110 (Sovol 100 C rating)', {'BED': '110', 'TOOL': '0', 'TEMP': '215'}, 'outside'),
                                  ('TEMP missing', {'BED': '60', 'TOOL': '0'}, 'missing')):
        def refuse(params=params, expect=expect):
            sim = Sim(parser, base_state(parser), expand=False)
            try:
                sim.run('START_PRINT', params)
            except MacroError as ex:
                assert expect in str(ex), f'wrong error: {ex}'
                return
            raise AssertionError('START_PRINT did not refuse')
        case(f'START_PRINT refuses {label}', refuse)

    def hvac(target, temp, power, cooling=False, cap=0.0, warm=False, exhaust=0.0, circ=0.0):
        st = base_state(parser)
        st['heater_generic chamber_temp'].update(target=target, temperature=temp, power=power)
        st['fan_generic exhaust_fan']['speed'] = exhaust
        st['fan_generic chamber_circulation']['speed'] = circ
        sim = Sim(parser, st, expand=False)
        st['gcode_macro _C3_CHAMBER_STATE'].update(cooling_active=cooling, cap=cap, last_target=target)
        st['gcode_macro M191']['warmup_active'] = warm
        st['gcode_macro _C3_EXHAUST_PURGE']['active'] = False
        sim.run('_C3_HVAC_STEP')
        return st
    def hvac_cases():
        st = hvac(45, 46.0, 0.0)
        assert st['fan_generic exhaust_fan']['speed'] == 0.15 and st['gcode_macro _C3_CHAMBER_STATE']['cooling_active'], 'overshoot 1.0 with heater off: exhaust 15 %'
        st = hvac(45, 46.0, 0.4)
        assert st['fan_generic exhaust_fan']['speed'] == 0.0, 'heater on: no exhaust (no fighting)'
        st = hvac(45, 48.5, 0.0, cooling=True, exhaust=0.15)
        assert abs(st['fan_generic exhaust_fan']['speed'] - 0.5) < 1e-6, 'overshoot 3.5: exhaust capped at 50 %'
        st = hvac(45, 46.9, 0.0, cooling=True, exhaust=0.15)
        want = 0.15 + (1.9 - 0.8) * 0.35 / 2.2
        assert abs(st['fan_generic exhaust_fan']['speed'] - want) < 0.002, f'proportional band: {st["fan_generic exhaust_fan"]["speed"]} vs {want}'
        st = hvac(45, 45.5, 0.0, cooling=True, exhaust=0.3)
        assert st['fan_generic exhaust_fan']['speed'] == 0.0 and not st['gcode_macro _C3_CHAMBER_STATE']['cooling_active'], 'stop at +0.55'
        st = hvac(45, 40.0, 0.9, warm=True, circ=0.8)
        assert st['fan_generic chamber_circulation']['speed'] == 1.0, 'warm-up: circulation 100 %'
        st = hvac(45, 45.0, 0.3, circ=1.0)
        assert st['fan_generic chamber_circulation']['speed'] == 0.8, 'after warm-up: circulation 80 %'
        st = hvac(0, 36.0, 0.0, cap=35.0)
        assert st['fan_generic exhaust_fan']['speed'] == 0.15, 'PLA ceiling: exhaust above 35.8 C'
        st = hvac(0, 30.0, 0.0, cap=35.0)
        assert st['fan_generic exhaust_fan']['speed'] == 0.0, 'PLA ceiling: quiet below it'
    case('Chamber HVAC: interlock, proportional exhaust, stop band, circulation, PLA ceiling', hvac_cases)

    def soak_compare():
        st = base_state(parser)
        sim = Sim(parser, st, expand=False)
        soak = st['gcode_macro _C3_ADAPTIVE_HEAT_SOAK']
        soak.update(max_iterations=35, threshold=0.010, stable=0)
        st['bed_mesh']['probed_matrix'] = [[0.0, 0.1], [0.2, 0.3]]
        sim.run('_C3_SOAK_COMPARE', {'ITER': '1'})
        assert soak['stable'] == 0
        st['bed_mesh']['probed_matrix'] = [[0.0, 0.12], [0.2, 0.3]]
        sim.run('_C3_SOAK_COMPARE', {'ITER': '2'})
        assert soak['stable'] == 0 and abs(soak['last_delta'] - 0.02) < 1e-9, 'delta 0.02 is still moving'
        st['bed_mesh']['probed_matrix'] = [[0.0, 0.125], [0.205, 0.3]]
        sim.run('_C3_SOAK_COMPARE', {'ITER': '3'})
        assert soak['stable'] == 1, 'delta 0.005 should be stable'
        soak.update(stable=0, max_iterations=4)
        st['bed_mesh']['probed_matrix'] = [[0.0, 0.2], [0.205, 0.3]]
        try:
            sim.run('_C3_SOAK_COMPARE', {'ITER': '4'})
        except MacroError as ex:
            assert 'after 4 passes' in str(ex)
            return
        raise AssertionError('no fail-closed at the pass limit')
    case('Heat soak: baseline, still moving, stable at 0.005 mm, fail closed at the limit', soak_compare)

    def z_source():
        for method, nozzle, want in (('beacon_contact', 25.0, '_C3_BEACON_CONTACT_HOME'), ('beacon_contact', 200.0, 'G28 Z'), ('load_cell', 25.0, 'G28 Z')):
            st = base_state(parser)
            st['extruder']['temperature'] = nozzle
            sim = Sim(parser, st, expand=False)
            st['gcode_macro _C3_VARS']['z_home_method'] = method
            sim.run('_INDX_HOME_Z_PROBE')
            ls = lines(sim)
            assert want in ls, f'{method} at {nozzle} C: expected {want}'
            other = 'G28 Z' if want != 'G28 Z' else '_C3_BEACON_CONTACT_HOME'
            assert other not in ls, f'{method} at {nozzle} C: unexpected {other}'
            assert ls[0].startswith('G90') and ls[1].startswith('G0 X252.500 Y252.500'), 'probe XY'
            assert any(l.startswith('SAVE_VARIABLE VARIABLE=z_home_tool') for l in ls), 'Bondtech tail kept'
        st = base_state(parser)
        sim = Sim(parser, st, expand=False)
        st['gcode_macro _C3_VARS']['beacon_autocal'] = 'unhomed'
        sim.run('_C3_BEACON_CONTACT_HOME')
        assert 'BEACON_AUTO_CALIBRATE SKIP_MODEL_CREATION=1' in lines(sim), 'homed + model + unhomed policy: skip model'
        st['gcode_macro _C3_VARS']['beacon_autocal'] = 'always'
        sim.out.clear(); sim.run('_C3_BEACON_CONTACT_HOME')
        assert 'BEACON_AUTO_CALIBRATE SKIP_MODEL_CREATION=0' in lines(sim), 'always: model refresh'
    case('Z home source: Beacon contact cold, load cell when hot or selected, model policy', z_source)

    def keepout_check(sim, label, need_z=None):
        cv = sim.state['gcode_macro _C3_VARS']
        lanes = cv['station_x']
        th = sim.state['toolhead']
        for a, b, cmd in sim.moves:
            for p in (a, b):
                assert -4.5 - 1e-6 <= p['x'] <= 499.5 + 1e-6 and -5.0 - 1e-6 <= p['y'] <= 501.5 + 1e-6, f'{label}: outside the CAD-checked travel {p}'
            dx = abs(b['x'] - a['x'])
            lo_y = min(a['y'], b['y'])
            in_lane = all(min(abs(p['x'] - s) for s in lanes) <= cv['station_side'] + 1e-6 for p in (a, b))
            if lo_y < 30.8 and 61.5 <= min(a['x'], b['x']) and max(a['x'], b['x']) <= 441.5:
                assert in_lane, f'{label}: move {a} -> {b} enters the front keep-out outside a station lane'
            if dx > 2 * cv['station_side'] + 1e-6:
                # CAD keep-out line (c3/C3_PURGE_KEEPOUT.json), independent of the macro's own approach_y
                assert lo_y >= 30.8 - 1e-6, f'{label}: X travel {a} -> {b} in front of Y 30.8'
            if need_z is not None and lo_y < 30.8:
                assert a['z'] >= need_z - 1e-6 and b['z'] >= need_z - 1e-6, f'{label}: at the station below Z {need_z}'

    def wipe():
        for start in ({'x': 300.0, 'y': 200.0, 'z': 20.0}, {'x': 120.0, 'y': 33.0, 'z': 14.0}, {'x': 470.0, 'y': 480.0, 'z': 60.0}):
            st = base_state(parser)
            st['toolhead']['position'].update(start)
            sim = Sim(parser, st)
            sim.run('C3_WIPE')
            keepout_check(sim, f'C3_WIPE from {start}', need_z=12.0)
            ys = [m[1]['y'] for m in sim.moves]
            assert min(ys) == -5.0 and max(m[1]['y'] for m in sim.moves if m[1]['y'] < 28) == 17.3, 'purge point -5 and wipe line 17.3'
            end = st['toolhead']['position']
            assert abs(end['y'] - 33.0) < 1e-6 and abs(end['z'] - start['z']) < 1e-6, f'ends at the lane exit, same Z: {end}'
            nearest = min(st['gcode_macro _C3_VARS']['station_x'], key=lambda s: abs(s - start['x']))
            assert abs(st['gcode_macro _C3_STATION']['x'] - nearest) < 1e-6, 'nearer station'
        st = base_state(parser)
        st['toolhead']['position']['z'] = 8.0
        sim = Sim(parser, st)
        sim.run('C3_WIPE')
        assert not sim.moves and any('skipped' in l for _, l in sim.out), 'below Z 12: skipped'
    case('C3_WIPE: lanes only, purge Y -5 / wipe Y 17.3, back to Y 33, skips below Z 12', wipe)

    def purge():
        st = base_state(parser)
        st['toolhead']['position'].update({'x': 252.5, 'y': 300.0, 'z': 2.0})
        sim = Sim(parser, st)
        sim.run('C3_PURGE')
        keepout_check(sim, 'C3_PURGE', need_z=30.0)
        assert st.get('_extruded') == [25.0], f'purge length {st.get("_extruded")}'
        st = base_state(parser)
        st['extruder']['temperature'] = 120.0
        sim = Sim(parser, st)
        try:
            sim.run('C3_PURGE')
        except MacroError:
            return
        raise AssertionError('cold purge not refused')
    case('C3_PURGE: raises to Z 30, purges 25 mm at the station, refuses a cold nozzle', purge)

    def load():
        st = base_state(parser)
        st['toolhead']['position'].update({'x': 210.5, 'y': 33.0, 'z': 5.0})
        sim = Sim(parser, st)
        sim.run('C3_LOAD_FILAMENT', {'TOOL': '3', 'TYPE': 'PLA'})
        ls = lines(sim)
        order_of(ls, ['CHANGE_TOOL TOOL=3', '_C3_LOAD_AT_STATION', 'G0 Z', '_C3_STATION_GO', 'LOAD_FILAMENT TOOL=3 TYPE=PLA MEASURE=0', '_C3_STATION_WIPE_OUT', 'M104 S0'])
        keepout_check(sim, 'C3_LOAD_FILAMENT', need_z=30.0)
    case('C3_LOAD_FILAMENT: pickup, Z 30, station, INDX load there, wipe, heater off', load)

    def fans():
        st = base_state(parser)
        st['heater_generic chamber_temp']['target'] = 45.0
        sim = Sim(parser, st)
        sim.run('M106', {'P': '3', 'S': '255'})
        assert st['fan_generic exhaust_fan']['speed'] == 0.0 and any('ignored' in l for _, l in sim.out), 'HVAC owns P3'
        st['heater_generic chamber_temp']['target'] = 0.0
        sim.run('M106', {'P': '3', 'S': '127.5'})
        assert st['fan_generic exhaust_fan']['speed'] == 0.5, 'P3 to exhaust when idle'
        sim.out.clear(); sim.run('M106', {'S': '200'})
        assert lines(sim)[0] == 'M99106 S200.0', 'part fan passes through'
        sim.out.clear(); sim.run('M107')
        assert lines(sim)[0] == 'M99107'
    case('M106/M107: part fan passthrough, P2/P3 mapping, HVAC ownership', fans)

    def end():
        st = base_state(parser)
        st['heater_generic chamber_temp']['target'] = 50.0
        sim = Sim(parser, st)
        sim.run('END_PRINT')
        ls = lines(sim)
        order_of(ls, ['M400', 'M83', 'G1 E-1.0', 'G91', 'G0 Z5.0', 'G90', 'PARK_TOOL', 'G90', 'G0 X252.5 Y470.0', '_C3_END_COMMON HEATED=1',
                      'TURN_OFF_HEATERS', 'M141 S0', 'M107', 'SET_GCODE_VARIABLE MACRO=_C3_CHAMBER_STATE VARIABLE=cap VALUE=0', 'BED_MESH_CLEAR',
                      '_C3_EXHAUST_PURGE MINUTES=5', 'M84'])
        st = base_state(parser)
        st['extruder']['temperature'] = 60.0
        st['toolhead']['position']['z'] = 493.0
        sim = Sim(parser, st)
        sim.run('END_PRINT')
        ls = lines(sim)
        assert not any(l.startswith('G1 E') for l in ls), 'no retract with a cold nozzle'
        assert any(l.startswith('G0 Z1.0 ') for l in ls), 'lift limited by Z max'
    case('END_PRINT: retract, lift, park tool, heaters off, exhaust run after a heated chamber', end)

    def m191():
        st = base_state(parser)
        st['heater_generic chamber_temp'].update(temperature=49.0, target=0.0)
        sim = Sim(parser, st, expand=False)
        sim.run('M191', {'S': '45'})
        ls = lines(sim)
        order_of(ls, ['SET_FAN_SPEED FAN=chamber_circulation SPEED=1.0', 'SET_HEATER_TEMPERATURE HEATER=chamber_temp TARGET=0',
                      'SET_FAN_SPEED FAN=exhaust_fan SPEED=0.40', 'TEMPERATURE_WAIT SENSOR="heater_generic chamber_temp" MAXIMUM=45.55',
                      'SET_FAN_SPEED FAN=exhaust_fan SPEED=0', 'SET_HEATER_TEMPERATURE HEATER=chamber_temp TARGET=45.0'])
        try:
            Sim(parser, base_state(parser), expand=False).run('M191', {'S': '60'})
        except MacroError:
            return
        raise AssertionError('M191 S60 not refused')
    case('M191: hot entry exhausts down first; targets above 55 refused', m191)

    def contact_gate():
        st = base_state(parser)
        sim = Sim(parser, st, expand=False)
        sim.run('_C3_CONTACT_GATE')
        ls = lines(sim)
        assert any(l.startswith('BEACON_PROBE PROBE_METHOD=contact SAMPLES=3 SAMPLES_RESULT=median') for l in ls), 'gate must probe with Beacon contact'
        assert not any(l.startswith('PROBE ') for l in ls), 'gate must not use the load cell'
        st['beacon']['last_z_result'] = 0.0100
        sim.out.clear(); sim.run('_C3_CONTACT_GATE_REPORT', {'FIRST': '0.0200'})
        assert any('gate passed' in l for l in lines(sim))
        try:
            sim.run('_C3_CONTACT_GATE_REPORT', {'FIRST': '0.0500'})
        except MacroError as ex:
            assert 'differ by 0.0400' in str(ex)
            return
        raise AssertionError('a 0.040 mm spread must fail the gate')
    case('Contact gate: Beacon contact medians, 0.025 mm limit', contact_gate)

    def tool_z():
        st = base_state(parser)
        st['extruder']['temperature'] = 30.0
        sim = Sim(parser, st, expand=False)
        sim.run('C3_CAL_TOOL_Z')
        ls = lines(sim)
        ones = [l for l in ls if l.startswith('_C3_CAL_TOOL_Z_ONE')]
        assert len(ones) == 5 and ones[0].startswith('_C3_CAL_TOOL_Z_ONE TOOL=0 X=252.5 Y=282.5'), f'5 tools from T0 at X252.5 Y282.5: {ones[:1]}'
        sim.out.clear(); sim.run('_C3_CAL_TOOL_Z_ONE', {'TOOL': '3', 'X': '252.5', 'Y': '282.5', 'SAMPLES': '5'})
        ls = lines(sim)
        order_of(ls, ['G0 Z20', 'CHANGE_TOOL TOOL=3 SKIP_Z_CORRECTION=1', 'G0 X252.5 Y282.5', 'G0 Z5', 'BEACON_PROBE PROBE_METHOD=contact SAMPLES=5', '_C3_CAL_TOOL_Z_STORE TOOL=3'])
        sv = st['save_variables']['variables']
        sv.update({'t0_offset_z': 0.05, 'c3_bz_0': 0.100, 'c3_bz_1': 0.250, 'c3_bz_2': 0.040, 'c3_bz_3': 0.100, 'c3_bz_4': -0.020})
        sim.out.clear(); sim.run('_C3_CAL_TOOL_Z_FINISH', {'N': '5'})
        want = {0: 0.05, 1: 0.2, 2: -0.01, 3: 0.05, 4: -0.07}
        for i, w in want.items():
            assert abs(sv['t%d_offset_z' % i] - w) < 1e-9, f't{i}_offset_z {sv["t%d_offset_z" % i]} vs {w} (Bondtech sign: t0_off + zN - z0)'
        st['extruder']['temperature'] = 200.0
        try:
            Sim(parser, st, expand=False).run('C3_CAL_TOOL_Z')
        except MacroError:
            return
        raise AssertionError('hot nozzle not refused')
    case('C3_CAL_TOOL_Z: Beacon contact per tool, offsets stored with Bondtech sign, refuses a hot nozzle', tool_z)

    def home_axis():
        for ax, want_away in (('X', 'G0 X10.00 F3000'), ('Y', 'G0 Y-10.00 F3000')):
            sim = Sim(parser, base_state(parser), expand=False)
            sim.run('_C3_HOME_AXIS', {'AXIS': ax})
            order_of(lines(sim), [f'G28 {ax}', 'G91', want_away, 'G90', 'M400', 'G4 P2000', 'M400'])
        try:
            Sim(parser, base_state(parser), expand=False).run('_C3_HOME_AXIS', {'AXIS': 'Z'})
        except MacroError:
            return
        raise AssertionError('AXIS=Z not refused')
    case('_C3_HOME_AXIS: single touch, 10 mm back-off away from the stop, 2 s for StallGuard to clear', home_axis)

    return results

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config_dir')
    ap.add_argument('--klippy', required=True, help='mainline Klipper klippy/ directory (sources read as text)')
    ap.add_argument('--indx', required=True, help="Bondtech indx_klipper host/ directory")
    ap.add_argument('--beacon', required=True, help="Beacon's beacon.py")
    ap.add_argument('--mainsail', required=True, help="mainsail-config client.cfg (stands in for mainsail.cfg)")
    ap.add_argument('--json')
    a = ap.parse_args()

    parser, origin, order = read_config(os.path.join(a.config_dir, 'printer.cfg'), a.mainsail)
    unknown, unchecked = check_options(parser, a.klippy, a.beacon, a.indx)
    used, dupes, pin_errors, indx_pins, aliases = check_pins(parser, a.indx)
    homing = check_homing(parser, a.config_dir)
    n_templates, bad_templates = check_templates(parser)
    beh = behaviour(parser)
    overrides = {s: f for s, f in origin.items() if len(f) > 1}

    report = {
        'files_in_order': order, 'sections': len(parser.sections()),
        'sections_defined_more_than_once': overrides,
        'unknown_options': unknown, 'sections_without_option_check': unchecked,
        'kraken_pins': {p: s for p, s in sorted(used.items()) if ':' not in p}, 'pin_conflicts': dupes, 'pin_errors': pin_errors,
        'indxmcu_pins_used': indx_pins,
        'homing_override': homing,
        'templates_compiled': n_templates, 'template_errors': bad_templates,
        'behaviour': beh,
    }
    ok = not unknown and not dupes and not pin_errors and not bad_templates and all(r['ok'] for r in beh) and homing['identical_except_g28_xy'] and not homing['g28_xy_left']
    report['result'] = 'PASS' if ok else 'FAIL'
    if a.json:
        json.dump(report, open(a.json, 'w'), indent=1)
    print(f"files: {' > '.join(order)}")
    print(f"sections {len(parser.sections())}; defined more than once: {overrides}")
    print(f"unknown options: {unknown or 'none'}")
    print(f"sections not option-checked: {unchecked}")
    print(f"Kraken pins used: {len([p for p in used if ':' not in p])}; conflicts: {dupes or 'none'}; pin errors: {pin_errors or 'none'}")
    print(f"indxmcu pins: {indx_pins}")
    print(f"homing override: {homing}")
    print(f"templates compiled: {n_templates}; errors: {bad_templates or 'none'}")
    for r in beh:
        print(('PASS ' if r['ok'] else 'FAIL ') + r['case'] + ('' if r['ok'] else '  -> ' + r['detail']))
    print('RESULT', report['result'])
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
