# SV08 Max C3 pin assignments: stock SV08 Max (with chamber heater) to BTT Kraken

Firmware: mainline Klipper on every board, no Sovol firmware. Stock pins are from Sovol's SV08 Max config (`Sovol3d/SV08MAX`, `printer.cfg` and `chamber_hot.cfg`). Kraken pins are from BTT's Kraken sample config and manual. The config that uses them is `printer_data/config/`.

## Controllers

| Stock | C3 |
|---|---|
| Sovol main board (`[mcu]`, CAN bridge) | **BTT Kraken V1.1** (`[mcu]`), USB to the host as a USB-to-CAN bridge (1,000,000 bit/s), outside the chamber on the right side |
| Sovol toolhead board (`extra_mcu`, CAN) | **INDX Smart Head** (`indxmcu`, USB through the INDX Link Board, both switches on USB) |
| Sovol chamber heater board (`hot_mcu`, CAN) | **kept**, on the Kraken's CAN port, **reflashed with mainline Klipper** (Katapult, one ST-Link session). The module is mains powered and its board switches the heater inside it (read from the live machine, 2026-10-30) |
| Sovol filament buffer (`buffer_mcu`) | retired; each INDX tool has its own filament path |
| Sovol eddy probe on the toolhead | **Beacon Rev H** (USB) plus the INDX load cell |
| Sovol screen | **iPistBit 7 inch** HDMI + USB touch on the host, KlipperScreen |
| Sovol's built-in host | **Raspberry Pi** (model open) for Wi-Fi, Ethernet and processing, outside the chamber on the right side next to the Kraken (owner's mounts) |

## Power

| Supply | Feeds |
|---|---|
| 24 V (Sovol's PSU) | Kraken **DCIN** (logic, HE0-HE3, fans); Kraken **BED IN** (only switches the bed SSR's control input); INDX Link Board (Bondtech's AWG18 leads); 5 V buck for the host and USB hub |
| Motor supply (adjustable 42-60 V) | **Set to 48.0 V.** Kraken **HV MOTOR** input only: all eight TMC2160 |
| Mains | Bed heater through Sovol's SSR (unchanged); chamber heater module on its own power cable and switch (unchanged) |

* Both DC supplies' V- meet at the Kraken. Earth (PE) both supplies, the frame and the bed.
* 48 V leaves 12 V below the Kraken's 60 V maximum for the voltage that eight motors push back onto the rail when they decelerate hard. Set it on the supply's trim with the supply disconnected from the Kraken, measure 48.0 V at its output, then check it again at the Kraken's HV terminals.
* CAN: the Kraken's CAN port to the heater board's existing CAN cable (CAN-H, CAN-L, 24 V, GND). 120-ohm termination at both ends: the Kraken's termination jumper on, and the heater board as it is on the stock machine.

## Steppers (all eight on HV)

Driver SPI is shared on the board: SCLK PC6, MOSI PC8, MISO PC7.

| Kraken port | Klipper section | Motor | Stock equivalent | Step / Dir / Enable | CS | Rsense | run_current |
|---|---|---|---|---|---|---|---|
| S1 | `stepper_x` | A, rear left (lower belt) | stepper_x: PE1 / PD7 / !PD5, CS PE0, TMC5160 3.0 A | PC14 / PC13 / !PE6 | PD6 | 0.050 (V1.1) | 1.4 A, homing 1.0 A |
| S2 | `stepper_x1` | A2, front left (lower belt) | new (AWD) | PE5 / PE4 / !PE3 | PD5 | 0.050 | 1.4 A, homing 1.0 A |
| S3 | `stepper_y` | B, rear right (upper belt) | stepper_y: PD3 / PD2 / !PD0, CS PD4, TMC5160 3.0 A | PE2 / PE1 / !PE0 | PD4 | 0.050 | 1.4 A, homing 1.0 A |
| S4 | `stepper_y1` | B2, front right (upper belt) | new (AWD) | PB9 / PB8 / !PB7 | PD3 | 0.050 | 1.4 A, homing 1.0 A |
| S5 | `stepper_z` | Z front left, 17HM19-2004S1 | stepper_z: PA8 / PC9 / !PA10, TMC2209 UART PA9 | PG9 / PG10 / !PG13 | PD2 | 0.075 | 1.2 A |
| S6 | `stepper_z1` | Z rear left | stepper_z1: PC6 / !PD15 / !PC8, UART PC7 | PG11 / !PD7 / !PG12 | PA15 | 0.075 | 1.2 A |
| S7 | `stepper_z2` | Z rear right | stepper_z2: PA5 / PA4 / !PA7, UART PA6 | PB4 / PB3 / !PB5 | PA9 | 0.075 | 1.2 A |
| S8 | `stepper_z3` | Z front right | stepper_z3: PB13 / !PB12 / !PB15, UART PB14 | PG15 / !PB6 / !PG14 | PA10 | 0.075 | 1.2 A |
| INDX | `extruder` | Bondtech DX on the Smart Head | extruder: extra_mcu PA8 / PA9 / !PA11, TMC2209 | indxmcu motor_step / motor_dir / !motor_enable | indxmcu motor_cs | rref 24000 (TMC2240) | 0.6 A |

* XY motors: LDO 42STH48-2004MAH(S80), 0.9 deg, `full_steps_per_rotation: 400`, `rotation_distance: 40` (20T).
* Z motors: 17HM19-2004S1, 0.9 deg, `full_steps_per_rotation: 400`, Sovol's `rotation_distance: 40` and `gear_ratio: 80:12`.
* The dir pin polarities are starting guesses (Z follows stock's alternating pattern). Every motor gets checked before the belts carry load (README.md, bring-up).

## Endstops and probes

| Function | Stock | C3 |
|---|---|---|
| X endstop | `^extra_mcu:PA10` (toolhead board switch) | **Sensorless**: `tmc5160_stepper_x:virtual_endstop`, S1 DIAG1 on **PC15** (S1 DIAG jumper on). Homes to X min against the hard stop where the X carriage meets the left XY joint's pulley carrier (CAD, about Klipper X -5.6). |
| Y endstop | `^PD1` (main board switch) | **Sensorless**: `tmc5160_stepper_y:virtual_endstop`, S3 DIAG1 on **PF1** (S3 DIAG jumper on). Homes to the rear (Y max). Needs the rear stop pads on the rear-corner motor plates first (README); then the stop is about Klipper Y 502.1. |
| Z endstop / Z offset | `probe:z_virtual_endstop` (Sovol eddy) | **Beacon contact** at G28 Z (inside Bondtech's homing sequence) and for the per-tool Z offsets (`C3_CAL_TOOL_Z`). `stepper_z` keeps `probe:z_virtual_endstop` (the load cell) only as the hot-nozzle fallback. |
| Probe / mesh | `probe_eddy_current` on extra_mcu i2c2 | Beacon Rev H on USB (bed mesh, contact); INDX load cell `[load_cell_probe]` on indxmcu (QGL and the INDX pickup/park seat checks) |
| Accelerometer | `lis2dw` on extra_mcu (software SPI PB12-PB15) | `lis2dw` on the INDX PCB (indxmcu sercom3) |

The Smart Head's endstop port (`indxmcu:endstop`) is now free.

## Heaters and temperature sensors

| Function | Stock | C3 (Kraken) |
|---|---|---|
| Bed heater (mains, through Sovol's SSR) | PD12 (main) to the SSR | **HB PF5** to the SSR's DC control input |
| Bed thermistor (Sovol table) | PC5 (main) | **TB PB0** |
| Hotend heater | extra_mcu PB7 | INDX induction coil (`indx:heater`) |
| Hotend thermistor | extra_mcu PA5 | INDX IR sensor (`sensor_type: indx`) |
| Chamber heater (mains, inside the module) | hot_mcu PA0 | **unchanged**: hot_mcu PA0, the board now on the Kraken's CAN bus |
| Chamber thermistor (Sovol `chamber_thermistor` curve) | hot_mcu PA5, 20 k pull-up | **unchanged**: hot_mcu PA5, 20 k pull-up |
| Room thermistor | in Sovol's GitHub config (hot_mcu PA4), not on the live machine | none |
| Kraken MCU temperature | main board MCU sensor | `temperature_mcu` |

## Fans

| Function | Stock | C3 |
|---|---|---|
| Part cooling, front and back | extra_mcu PB0 and PA7 | INDX Radial Part Cooling: `indxmcu:part_cooling`, tach `indxmcu:part_cooling_tacho` |
| Hotend fan | extra_mcu PA6, tach PA1 | INDX heatsink fan, run by the INDX module itself |
| Chamber circulation (stock `fan2`) | PB0 (main) | **FAN0 PA0**, 24 V jumper, `fan_generic chamber_circulation` |
| Exhaust (stock `fan3`) | PE11 (main) | **FAN1 PA1**, 24 V jumper, `fan_generic exhaust_fan` |
| Bed fan (`heater_fan`, on at 35 C bed) | PE14, tach PB10 | **FAN2 PA2**, 24 V jumper; tach wire to the **TACH pin of the FAN6 header (PC1)** |
| Driver cooling (new) | none | **FAN3 PA3**, 24 V jumper, `controller_fan kraken_fan` |

## Light

| Function | Stock | C3 |
|---|---|---|
| Chamber LED bar | PD13 (main), on/off | **HE1 PF7**, 24 V, dimmable (`output_pin chamber_light`) |

## Kraken jumpers

* DIAG jumpers: **on for S1 and S3** (sensorless X and Y), **off for S2 and S4-S8**.
* Fan voltage jumpers FAN0-FAN3: **24 V** (check each fan's label first).
* CAN 120-ohm termination jumper: **on** (the Kraken is one end of the bus).
* VUSB: **off** (the board runs from DCIN).

## Spare Kraken I/O after this assignment

| Use | Pins |
|---|---|
| Five runout sensors (T0-T4) later | S2 STOP PF0, S4 STOP PF2, S5 STOP PF3, S6 STOP PF4, S7 STOP PF10 (S8 PC0 also free; S1 and S3 carry the sensorless DIAG lines) |
| Heaters | HE0 PF6, HE2 PF9, HE3 PF8 |
| Thermistors | T0 PB1, T1 PC5, T2 PC4, T3 PA7; MAX31865 PT100/PT1000 on PC9 and PA8 (spi3a) |
| Fans | FAN4 PA4, FAN5 PA5; FAN7 PE8 with tach PG0; FAN6 PA6 (its TACH pin is used by the bed fan) |
| Other | INDX Smart Head endstop port (`indxmcu:endstop`), PS_ON PD10, RGB PF12 and PF11, probe port PD11, servo PE7, BLTouch PG1 / PE9, I2C2 PB10 / PB11, accelerometer SPI4 CS PE10, EXP1 / EXP2 |
