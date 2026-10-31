# Orca Slicer machine G-code for the SV08 Max C3

Printer settings, Machine G-code. Five extruders (T0-T4), nozzle 0.6.

## Machine start G-code

```
START_PRINT BED=[bed_temperature_initial_layer_single] TOOL=[initial_tool] TEMP={nozzle_temperature_initial_layer[initial_tool]} FILAMENT={filament_type[initial_tool]} CHAMBER={chamber_temperature[initial_tool]}
```

* `START_PRINT` does everything in order: bed, home, chamber, QGL, adaptive heat soak, QGL, contact gate, final Z home, adaptive mesh, first tool, purge.
* Turn off Orca's own chamber control ("activate temperature control" and automatic `M191`). `START_PRINT` heats the chamber only after the bed is at target, the electrical rule carried over from the stock machine.
* `CHAMBER` > 0 sets the chamber target. With 0 or nothing, the target comes from the filament type (`_C3_VARS chamber_by_filament`).
* Add `HEAT_SOAK=0` to skip the heat soak, or `MESH=full` for a whole-bed mesh.

## Machine end G-code

```
END_PRINT
```

## Change filament G-code

```
CHANGE_TOOL TOOL=[next_extruder] TEMP={nozzle_temperature[next_extruder]}
C3_WIPE
```

* `C3_WIPE` skips itself below Z 12 mm, where the station sliders are lifted. Use a prime tower for every multi-tool print; it covers those layers.
* Do not set standby or preheat temperatures for idle tools (INDX cannot heat a docked tool).

## Bed shape and exclusions

* Printable area 0..505 x 0..505, but leave out the front strip: nozzle Y < 30.8 between X 61.5 and 485.5 (docks and wiper stations; `c3/C3_PURGE_KEEPOUT.json`). In Orca, use an "excluded bed area" of `61.5x0, 485.5x0, 485.5x30.8, 61.5x30.8`.
* The head's checked travel is X -4.5..499.5 and Y -5.0..501.5 (the homing stops sit just past it), so the last 5.5 mm at the right and 3.5 mm at the rear are not printable.
* Enable "label objects" so `[exclude_object]` and the adaptive mesh see the parts.

## Fans

* Part fan: the INDX radial fan (`M106` / `M107`).
* `M106 P2` and `P3` still reach the chamber circulation and exhaust fans, as on the stock machine. They are ignored while the chamber control owns those fans (heated chamber, or a PLA/PETG/TPU ceiling). Leave Orca's auxiliary fan and exhaust settings off.
