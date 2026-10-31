# Safety

C3 has not been built yet. Every part, clearance and config value here comes from CAD and offline checks, not from a running machine. Check each step against your own printer, parts and wiring.

## Before you start

* **Unplug the printer from mains** before stripping the stock gantry or opening any electronics.
* **The chamber heater runs on mains.** It stays on Sovol's heater module, which switches mains inside it. Unplug that module from mains before opening it or flashing its board.
* **Check the parts you print against the CAD.** If your printer's frame differs from Sovol's model, re-check the fit. Pay most attention to the Z towers, the top frame and the bed edge.
* **Check the bought parts against the BOM.** The Z idler flanges must be 16 mm or less across. The reworked Z drive pulleys must be 12.6 mm or less long.

## Power

* **Two supplies.** The motors run from a 48 V supply on the Kraken's HV motor input. The Kraken's logic and bed inputs stay at 24 V.
* **Set the motor supply to 48.0 V before you connect it,** then check every input at the board before you plug in any motor.
* **Ground.** Both supplies must share V- and earth.
* **Pinch and crush points.** At 48 V, motors stall with real force. Keep hands out of the gantry whenever the motors are powered.

## First motion

Follow the bring-up order in `c3-4040-gantry/klipper_c3/README.md` one step at a time.

* **Each belt has two motors.** Buzz every motor on its own with the belts slack, before you tension them. A motor wired the wrong way fights its partner.
* **Homing.** X and Y home sensorlessly, against hard stops 0.5–1.25 mm past travel. Tune the stall detection with the carriage starting near the middle, and keep a hand on the power switch.
* **First tool changes.** Run the first tool change and the first wipe at reduced speed. Watch the head clear the docks and the wiper stations.
* **Slicer bed shape.** Leave out the front keep-out strip. That is nozzle Y above 537.5 between X -194 and +186, in Sovol's model frame. Without it, the head can hit the docks or the stations.

## Printing the parts

* **PPS-CF prints hot:** 320 °C nozzle, 110 °C bed and 65 °C chamber. Use an enclosed printer with ventilation or filtration.
* **Use a hardened nozzle.** The carbon fibre wears out brass.
* **ASA gives off fumes.** Print the top hat in an enclosed, ventilated printer.

## In use

* **Wiper pads.** The silicone strip is rated below PPS-CF nozzle temperatures. It only touches the nozzle briefly on each stroke. Replace a pad when it hardens or tears.
* **Purge trays.** Empty them before they reach the gantry: their rims are 1 mm below the lowest gantry part at the first layer.
