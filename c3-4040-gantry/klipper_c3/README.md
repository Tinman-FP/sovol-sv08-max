# Klipper config for the SV08 Max C3 (BTT Kraken, INDX x 5, Beacon Rev H)

Written 2026-10-30. **Not installed: nothing has been sent to the printer.** The offline check passes (`CHECK_REPORT.json`, `tools/check_config.py`). Every `REPLACE_ME` and every item under "Still open before power-up" still needs the machine or you.

Firmware: **mainline Klipper on every board**, and no Sovol firmware anywhere:
* the Kraken;
* the INDX Smart Head, through Bondtech's `indx_klipper`;
* Sovol's chamber heater board, reflashed once over SWD with Katapult, then updated over CAN.

## Files

| File | What it holds |
|---|---|
| `PIN_ASSIGNMENTS.md` | Every stock function and where it lands on the Kraken, INDX or host; power, jumpers, spare pins |
| `printer_data/config/printer.cfg` | Includes, MCU serials, kinematics limits, input shaper, idle timeout |
| `.../c3_kraken.cfg` | 8 steppers (AWD X/X1/Y/Y1, 4 x Z), TMC2160 settings including sensorless X/Y, bed, bed fan, chamber fans, driver fan, light |
| `.../c3_chamber.cfg` | Sovol's chamber heater controller on the Kraken's CAN bus, `M141` / `M191`, the chamber HVAC loop (heat, circulation, exhaust) |
| `.../c3_indx.cfg` | Smart Head: extruder, induction heater, part fan, LEDs, accelerometer, encoder, load cell |
| `.../indx/indx.cfg` | Bondtech's user file with the C3 dock row (5 tools), probe point and clearance line |
| `.../indx/indx-tc-macros.cfg`, `indx-cal.cfg`, `homing.cfg` | Bondtech's macros, unchanged (github.com/BondtechAB/INDX `macros/`, commit 05018b2, 2026-10-20) |
| `.../c3_homing.cfg` | Bondtech's homing override with G28 X / G28 Y wrapped for sensorless homing (the checker verifies nothing else differs) |
| `.../c3_beacon.cfg` | Beacon, bed mesh, quad gantry level, and the G28 Z source (Beacon contact) |
| `.../c3_macros.cfg` | `_C3_VARS` settings, `START_PRINT` / `END_PRINT`, adaptive heat soak, gates, Beacon per-tool Z offsets, wiper stations, filament load, fans, light |
| `.../KlipperScreen.conf` | KlipperScreen for the iPistBit 7 inch display, with INDX tool and chamber menus |
| `.../moonraker_c3_additions.conf` | Update-manager entries to add to `moonraker.conf` |
| `slicer/ORCA_MACHINE_GCODE.md` | Start, end and tool-change G-code for Orca, bed exclusion, fan notes |
| `tools/check_config.py` | The offline checker |

## How it works

* **Homing:** Bondtech's sequence: Y, then X at the rear (the docks are at the front), then T0 onto the head, then Z at the bed centre.
  * **X and Y are sensorless** (TMC2160 StallGuard on the S1 and S3 DIAG lines).
    * Each axis homes with one touch, backs off 10 mm and waits 2 s so the drivers' stall flags clear before the next axis (`_C3_HOME_AXIS`).
    * Mainline Klipper allows one homing override, so `c3_homing.cfg` carries Bondtech's with only its `G28 Y` and `G28 X` lines replaced.
    * Homing runs at the normal run current. Bondtech's `INDX_DOCK_MEASURE` homes through Klipper directly at run current, so one StallGuard setting has to suit both.
  * **Z** is homed by **Beacon contact**. `c3_beacon.cfg` swaps only Bondtech's Z step. If the nozzle is ever too hot for Beacon contact (above 175 C), that one home falls back to the load cell and says so.
* **Hard stops for sensorless homing**, from a CAD sweep past the travel limits (2026-10-30):
  * **X:** the X carriage meets the XY joint's pulley carrier 1.0-1.25 mm past travel. That's printed part on printed part, about 120 mm2 of face, just before the X block would reach its rail end (1.3 mm). Usable as it is. X homes to X min (the left end), stop about Klipper X -5.6.
  * **Y (rear):** without help, the joint plates met the rear-corner motor plates 1.75 mm past travel, and the X beam reached the motor cans 0.25 mm after that.
    * The rear-corner motor mounts now carry **1.25 mm stop pads** (`c3_build.rear_corner`, `Y_STOP_PAD`). The joint plates land on them 0.5 mm past travel (Klipper Y 502.1), leaving 1.5 mm before the beam could reach a motor.
    * Re-checked with the pads in: the hard-stop sweep, and the clearance check (7 poses, Z sweep, enclosure) all at 0.
    * Print files, print project, coloured model and assembly guide are updated.
* **Roles:**
  * **Beacon:** bed mesh and heat-soak passes (proximity); Z origin, the start-of-print contact gate and the per-tool Z offsets (`C3_CAL_TOOL_Z`) by contact.
  * **INDX load cell:** stays the registered probe, as Bondtech requires. It does QGL and the pickup/park seat checks. Beacon runs with `register_as_probe: False` and `BEACON_`-prefixed probe commands.
* **START_PRINT** carries over your stock machine's qualified sequence and contract:
  1. bed first, then the chamber (the chamber heater never starts before the bed is at target);
  2. QGL;
  3. adaptive heat soak: Beacon mesh passes 60 s apart until two in a row agree within 0.010 mm, up to 35 passes, stopping the print if they never do;
  4. QGL again;
  5. contact gate: two Beacon contact medians within 0.025 mm;
  6. final Z home with T0 at 150 C and wiped;
  7. adaptive mesh, then the final geometry gate;
  8. first tool, heat, purge at a wiper station.
* **Chamber heater:** stays on Sovol's own controller board, which now sits on the Kraken's CAN bus (the Kraken runs as a USB-to-CAN bridge, like the stock main board). The live machine shows why:
  * the module is mains powered with its own cable and switch, and its board switches the heater inside the module;
  * so there is no low-voltage input to move to the Kraken without opening a mains unit.
  * Sovol's thermistor curve, the board's 20 k pull-up and your PID tune carry over unchanged.
* **Chamber control** is your stock machine's HVAC logic (`staging/2026-10-14-*`), ported to the new fan names:
  * PID heater, with your 45 C tune;
  * circulation at 100 % while warming up, 80 % after;
  * exhaust only when the heater is off and the chamber is above target, 15-50 %, proportional;
  * blocking `M191` exhausts a hot chamber down itself.
  * New: a ceiling for unheated filaments (PLA 35 C, PETG 45 C, TPU 40 C) using the same exhaust band. Waits inside `START_PRINT` run the HVAC step every 5 s, because the delayed loop cannot run while a macro holds the queue.
* **Wiper stations:** `C3_WIPE` (after each tool change), `C3_PURGE` (print start) and `C3_LOAD_FILAMENT` follow the CAD rules:
  * X travel only at Y 31 or further back;
  * straight forward in a station lane to Y -5;
  * strokes back to Y 15 within +-8 mm of the station centre;
  * no wipes below Z 12, where the sliders are lifted;
  * purges at Z 30 or higher.

## Settled (owner, 2026-10-30)

* Kraken **V1.1**: S1-S4 `sense_resistor: 0.050` is set.
* **Sensorless X and Y**, no switches. DIAG jumpers on S1 and S3 only. The Smart Head endstop port is free.
* **Beacon** for the bed mesh, **Beacon contact** for the Z offset (Z origin and per-tool offsets).
* Belts ordered: 2 x 2600 mm (gantry), 4 x 1600 mm (Z).
* Kraken and Raspberry Pi outside the chamber on the right side, on mounts you design.
* **Mainline Klipper** on every board; **no Sovol firmware**. Sovol's chamber heater board stays, reflashed once with an ST-Link (Katapult plus Klipper) and updated over CAN after that.
* **Rear Y stop pads** added to the rear-corner motor mounts (CAD and print files).
* **Motor supply: 48.0 V** (adjustable 42-60 V supply). That leaves 12 V below the Kraken's 60 V limit for the voltage eight decelerating motors push back onto the rail, and is the usual choice for 60 V-rated TMC2160/5160 drivers. It still gives these 0.9 deg motors twice the voltage headroom of a 24 V machine.
* **Chamber heater:** keep Sovol's controller and module, on the Kraken's CAN port (from the live machine's config and Sovol's listing, 2026-10-30).

## Still open before power-up

1. **Raspberry Pi model.** I'd use a Pi 5 (4 GB, or 8 GB for a camera with timelapse). Beacon streams fast, the 45 x 45 bicubic mesh and input-shaper analysis are CPU-heavy, and it also runs KlipperScreen and three USB MCUs. See "Host".
2. **INDX heater PID.** Bondtech's README says to set `pid_kp 1.0, pid_ti 0.0`. Their `indx_klipper` module defaults to `pid_kp 4.0` (and Kalico's to `4.0, 0.2`). The config follows the README; ask Bondtech which applies to the current firmware.
3. **Material envelope with these tools.**
   * Bondtech rates the Smart Head and the CHT tools to **300 C nozzle and 60 C ambient**, and CHT tools are for **non-abrasive** filament.
   * So PPS / PPS-CF (above 300 C) and CF/GF filaments need different tools.
   * `START_PRINT` refuses nozzle temperatures above 300 C and bed temperatures above 100 C (Sovol's bed rating), and caps the chamber at 55 C.
4. **Beacon contact on an INDX head.** Neither vendor documents this combination. Beacon contact senses the nozzle stopping, and the INDX tool sits on the load cell's flexure, so its contact may be softer than on a rigid hotend. Bring-up step 10 measures its repeatability before you rely on it.
5. **Beacon offsets** (`x_offset 0`, `y_offset 40.25`) come from the CAD. Check them on the machine before trusting a mesh.
6. **Dock positions** (`indx/indx.cfg`) are CAD values with `dock_y -4.5` placeholders and `docks_calibrated: False`. INDX refuses tool changes until they are measured.
7. **Front strip mesh.** The Beacon coil is 40 mm behind the nozzle and the nozzle must stay at Y >= 28.5 in the dock area, so the mesh starts at Y 70. Prints between Y 28.5 and 70 use the nearest mesh row.



## Host

The Raspberry Pi sits outside the chamber, right side, next to the Kraken.
* **USB devices:** Kraken, INDX Link Board, Beacon, the display's touch and the camera. That's five, and a Pi has four USB-A ports, so use the powered USB hub already planned in the top-hat tray for Beacon, the Link Board and the camera. Run one cable down to the Pi, and connect the Kraken to the Pi directly.
* **Display:** the iPistBit plugs into the Pi over HDMI (a Pi 4 or 5 needs a micro-HDMI to HDMI cable) and USB for touch.
* **Power:** a 24 V to 5 V buck rated 5 A for a Pi 5. A Pi 5 only allows full USB current when it detects a 5 A supply; on a buck add `usb_max_current_enable=1` to `/boot/firmware/config.txt`.
* **Network:** Wi-Fi and Ethernet are on the Pi; nothing in the Klipper config depends on the model.

## Install on the host

1. Mainline Klipper, Moonraker, Mainsail (`mainsail.cfg` comes from mainsail-config) and KlipperScreen, with KIAUH.
2. INDX: `git clone https://github.com/BondtechAB/indx_klipper.git ~/indx_klipper`, then `cd ~/indx_klipper && ./install.sh ~/klipper`. That links the `[indx]` host module into Klipper.
3. Beacon: `git clone https://github.com/beacon3d/beacon_klipper ~/beacon_klipper` and `~/beacon_klipper/install.sh`.
4. Katapult (for the heater board): `git clone https://github.com/Arksine/katapult ~/katapult`.
5. Copy `printer_data/config/*` and `indx/` into `~/printer_data/config/`. Merge `moonraker_c3_additions.conf` into `moonraker.conf`.
6. Fill in the INDX and Beacon serial paths from `ls /dev/serial/by-id/`, and the Kraken and heater board CAN UUIDs from `canbus_query.py can0`. The heater board's UUID is the one already in the Sovol's `chamber_hot.cfg`.

Firmware builds (mainline Klipper in `~/klipper` unless noted):
* Kraken: `make menuconfig`, then STM32H723, 128 KiB bootloader, 25 MHz crystal, communication **USB to CAN bus bridge** (USB on PA11/PA12, CAN on PD0/PD1), CAN bitrate **1000000**. Copy `out/klipper.bin` to an SD card as `firmware.bin` (BTT's method).
* Host CAN interface: `/etc/network/interfaces.d/can0` with `allow-hotplug can0`, `iface can0 can static`, `bitrate 1000000`, `up ip link set $IFACE txqueuelen 128`. Then `canbus_query.py can0` lists the Kraken and the heater board UUIDs.
* INDX Smart Head: from `~/indx_klipper`, `make`, then `make flash FLASH_DEVICE=04d8:e483` with the CAN RESET jumper bridged at power-up (Bondtech README). Remove the jumper and power-cycle afterwards.
* **Sovol chamber heater board, once by ST-Link:**
  * Unplug the heater module from mains before opening it.
  * Sovol's board runs from address 0x08000000 with no bootloader, so it needs one SWD session. Connect the ST-Link to its SWD pads (SWDIO, SWCLK, GND, 3.3 V).
  * **Katapult:** `make menuconfig` in `~/katapult`: STM32F103, 8 MHz crystal, CAN bus on PB8/PB9, CAN speed 1000000, application start offset 8 KiB. Then `make`, `st-flash erase` and `st-flash write out/katapult.bin 0x8000000`. If the chip is read-protected, clear that first with STM32CubeProgrammer; it erases Sovol's firmware, which isn't used.
  * Reconnect the board to the Kraken's CAN bus.
  * **Klipper:** `make menuconfig`: STM32F103, 8 KiB bootloader, 8 MHz crystal, CAN bus on PB8/PB9, CAN speed 1000000. Then `make` and `python3 ~/katapult/scripts/flashtool.py -i can0 -q` to find it, then `python3 ~/katapult/scripts/flashtool.py -i can0 -u <uuid> -f ~/klipper/out/klipper.bin`.
  * Later updates repeat only the Klipper step, over CAN.
* Beacon: its install script keeps the Beacon firmware current.

## Bring-up order

Each step only after the previous one is right.

1. **Power, no motors connected.** Set the motor supply to 48.0 V before it is connected to the Kraken. Then check DCIN (24 V), BED IN (24 V) and HV (48 V) at the board, and that both supplies share V- and earth.
2. **First start.** Check that both CAN boards answer (`canbus_query.py can0`, then Klipper ready). Check that bed, chamber and Kraken temperatures read room temperature. Check that `QUERY_ENDSTOPS` reports the X and Y virtual endstops "open".
3. **Motors, one at a time, belts slack.** `STEPPER_BUZZ STEPPER=stepper_x`, then `stepper_x1`, `stepper_y`, `stepper_y1`. Each AWD pair must pull its belt the same way; flip the `dir_pin` of the one that does not. Z: `STEPPER_BUZZ` on each `stepper_z..z3`; all four corners must move the same way.
4. **CoreXY directions, belts tensioned.** `G28 Y`, then small `G1` moves. If a +X move goes in Y, or either axis runs backwards, use the standard CoreXY table: swap the `stepper_x` and `stepper_y` pins, or invert dir on both motors of a pair.
5. **Sensorless tuning** (Klipper `TMC_Drivers.md`, "Sensorless Homing"; run current, no current change).
   * Start each attempt with the carriage near the middle.
   * Use `SET_TMC_FIELD STEPPER=stepper_x FIELD=sgt VALUE=<n>` and `G28 X` to find the most and least sensitive values that still home with one touch. Set `driver_SGT` to least + (most - least) / 3.
   * Same for Y. The rear-corner mounts must be the new prints with stop pads.
   * Then check repeatability: with the motors left on, run `G28 X Y` ten times and `GET_POSITION` after each. The `mcu:` counts for stepper_x and stepper_y should repeat within a few steps (one step is 0.006 mm).
6. **INDX heater.** `INDX_CALIBRATE` (the heater will not heat until this has run), then `SAVE_CONFIG`.
7. **Load cell.** `CALIBRATE_LOAD_CELL` with an empty head, seat a tool by hand, `CALIBRATE_LOAD_CELL_APPLY GRAMS=1600`, then `SAVE_CONFIG`.
8. **First full home.** Put T0 on the head by hand, run `MANUAL_TOOL_SEAT TOOL=0`, then `G28`. Z homes by Beacon contact; the first one also builds Beacon's proximity model.
9. **Docks.** `CALIBRATE_DOCK_X` and `CAL_SET_DOCK_Y` for each dock (Bondtech README, "Dock Position Calibration"). Enter the values in `indx/indx.cfg`, set `docks_calibrated: True` and `RESTART`. Test one tool change, then `TC_CYCLE_ALL`.
10. **Beacon contact repeatability.** Run `BEACON_AUTO_CALIBRATE SKIP_MODEL_CREATION=1` five times at the bed centre. The spread should be about 0.01 mm or less. If it is much worse, the tool flexure is softening the contact. Tell me, and we'll look at `contact_sensitivity` or the load cell.
11. **Level and offsets.** `QUAD_GANTRY_LEVEL`, then `C3_CAL_TOOL_Z` for the per-tool Z offsets by Beacon contact (cold, clean nozzles). It writes Bondtech's `tN_offset_z` variables with Bondtech's sign. Bondtech's own `CAL_Z` (load cell) is still there as a cross-check. XY tool offsets: print-and-adjust, Nudge or camera (Bondtech README, "Tool Offsets").
12. **PID.** `PID_CALIBRATE HEATER=heater_bed TARGET=100`, then `PID_CALIBRATE HEATER=chamber_temp TARGET=45` with the bed at temperature.
13. **Input shaper.** `SHAPER_CALIBRATE`, which uses the INDX accelerometer.
14. **Wiper stations.** With each tool on the head at Z 20: `C3_WIPE`. Watch the first one at reduced speed (`M220 S25`).
15. **First print.** A single-tool PLA print with `HEAT_SOAK=0`. Then a heated-chamber print, watching the heat soak, chamber temperature, heater power and both chamber fans through one warm-up.

Leave the INDX speed mode at `MODE_NORMAL` or `MODE_SPORT`. `MODE_STEALTH` switches the XY drivers to StealthChop, which TMC2160 stages at this voltage are not tuned for.

## KlipperScreen display

The iPistBit 7 inch (1024 x 600) connects to the host: HDMI for video, USB for touch. Raspberry Pi OS Bookworm usually reads the panel on its own. If the resolution is wrong, add `video=HDMI-A-1:1024x600@60` to `/boot/firmware/cmdline.txt`. Copy `KlipperScreen.conf` to `~/printer_data/config/`. Preheat buttons set the bed and chamber only, because INDX heats a tool only once it is on the head.

## Re-running the check

```
python3 tools/check_config.py printer_data/config --klippy <klipper>/klippy --indx <indx_klipper>/host --beacon <beacon_klipper>/beacon.py --mainsail <mainsail-config>/client.cfg --json CHECK_REPORT.json
```

The checker does six things:
* parses the include chain the way Klipper does;
* checks every option against the mainline Klipper, `indx_klipper` or Beacon source that reads it;
* checks Kraken pins for validity and conflicts, and INDX pins against `indx_klipper`'s alias list;
* confirms `c3_homing.cfg` is Bondtech's homing override with only G28 X / G28 Y replaced;
* compiles all 160 G-code templates;
* runs 19 behaviour cases on a mocked printer: start order and refusals, HVAC decisions, the heat-soak comparison, the Z source switch, fans, end of print, and a move-by-move simulation of the station macros against the front keep-out.

It cannot prove timing, MCU communication or real motion; that is what the bring-up order is for.
