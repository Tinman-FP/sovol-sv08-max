# C3 parts sourcing

Example sources for the parts to buy: what was ordered or chosen for the first C3 build, from US sellers, with prices as listed on 30-31 Oct 2026. Any part that meets the spec in [C3_BOM.md](C3_BOM.md) and [C3_Z_BOM.md](C3_Z_BOM.md) will do. None of these are affiliate links.

The major components are not linked here (see the BOMs and `klipper_c3/README.md`): the Bondtech INDX kit (Smart Head, tools, Link Board, five 1515 docks), Beacon Rev H, BTT Kraken, four LDO 42STH48-2004MAH(S80) motors, four StepperOnline 17HM19-2004S1 Z motors, the Gates 2MGT 12 mm belts and the 7 inch display.

## Parts with example sources

| Item | Qty needed | Example source | Notes |
|---|---|---|---|
| 4040 extrusion, 8 mm slot | 2 x 561, 1 x 556, 1 x 482 mm | QNK: [4040 European standard, 4 x 600 mm, black](https://www.amazon.com/dp/B0CTQRYW2D) ($56.99 for 4) | Cut 2 x 561, 1 x 556 and 1 x 482 mm from the four 600 mm pieces, ends square. |
| 1515 metric extrusion, 15 mm | 1 x 588 mm (ends tapped M3), 1 x 566 mm | Mssoomm: [1515 European standard, 2 x 1000 mm, silver](https://www.amazon.com/dp/B09KXJR655) ($42.22 for 2) | Cut 588 and 566 mm. Tap both ends of the 588 mm piece M3 (the centre hole should be about 2.5 mm). |
| 2020 extrusion, 6 mm slot | 1 x 661 mm | Iverntech: [2020 European standard, 4 x 700 mm, black](https://www.amazon.com/dp/B07QWS3XCS) ($31.99 for 4) | Cut one 661 mm piece. |
| MGN12 rails with MGN12H blocks | 1 x 552 mm + 2 x 555 mm, one block each | ZHBRING: [MGN12 600 mm + 1 MGN12H, preloaded](https://www.amazon.com/dp/B0D9D5RSPJ) ($31.99 each) | Three needed: cut to 552, 555 and 555 mm. Take half off each end (24 mm, or 22.5 mm for 555) so the end holes stay 13-15 mm from the ends. Leave the block on the rail while cutting and cover it from the grit: a block slid off the rail loses its balls. Clean and grease the blocks. |
| Dowel pins, 3 x 20 mm | 10 (two per station) | uxcell: [Bearing steel dowel pins 3 x 20 mm](https://www.amazon.com/dp/B0F54CPJTV) ($7.79 / 100) |  |
| Gates 2GT 20T pulley, 12 mm belt, 5 mm bore | 4 | Printed Solid: [Gates PowerGrip 2GT pulley, 12 mm / 20T, 5 mm bore](https://www.printedsolid.com/products/gates-powergrip-2gt-pulley?variant=21236966981717) ($3.50 each) |  |
| Gates 2GT 20T toothed idler, 12 mm belt | 12 (8 gantry + 4 Z) | KB-3D: [G2GT-I-20-12 genuine Gates toothed idler](https://kb-3d.com/store/motion/935-gates-powergrip-2gt-idler-12mm-toothed-1634482148249.html) ($5.99 each (12 = $71.88)) | The four for Z need flanges of 16 mm or less: the maker's drawing says 15. |
| Smooth idler for 12 mm belt | 2 | KB-3D: [G2GT-I-S-12 genuine Gates smooth idler](https://kb-3d.com/store/motion/934-gates-powergrip-2gt-idler-12mm-smooth-1688954609211.html) ($5.49 each) | Checked: it fits the existing axles with no part changes (belt runs beside it tilt 1.2 and 4.4 degrees, each belt 4.6 mm shorter). Measure its width when it arrives; the spacer lengths depend on it. |
| 625ZZ bearings | 4 | XIKE BEARINGS USA: [XiKe 625ZZ ABEC-3, 10 pack](https://www.amazon.com/dp/B07JHKKGKT) ($11.49 / 10) |  |
| MR105ZZ bearings | 4 (optional Z motor end supports) | VRCHobbies: [Apex RC 1920M MR105ZZ, 10 pack](https://www.amazon.com/dp/B00XQ9212C) ($8.99 / 10) |  |
| M5 aluminium spacers, 5.2 x 8 mm | 10 pieces (6 spacers + 4 sleeves), cut to length | PATIKIL US: [5.2 x 8 x 30 mm aluminium spacers, 10 pack](https://www.amazon.com/dp/B0CQ53LS2B) ($9.99 / 10) | The rear idlers need a spacer below and above each wheel: 11 pieces, plus the 4 joint sleeves. Six 30 mm pieces give the long ones and their offcuts the short ones. |
| M3 socket head cap screws | x6: 4, x8: 16, x10: 93, x12: 2, x16: 20, x30: 8, x40: 2 | SVLING: [810-piece M3 12.9 kit (x6-x30 + nuts)](https://www.amazon.com/dp/B0GG8MGH1H) ($8.99) | The kit has 40 x M3x10 (93 needed) and no M3x40: both are in the next table. |
| M4 socket head cap screws and washers | x12: 8, x16: 4, x18: 4, x25: 2, x35: 4, washers: 8 | SVLING: [520-piece M4 12.9 kit (x12, x16, x25 + washers)](https://www.amazon.com/dp/B0GG8SZC1W) ($8.99) | The kit has no M4x18 or M4x35: both are in the next table. |
| M5 socket head cap screws and nyloc nuts | x10: 26, x12: 2, x20: 4, x45: 7, x50: 3, nyloc: 4 | Sutemribor: [M5 x 10 12.9, 55 pack](https://www.amazon.com/dp/B0CZRTKS8H) ($3.99 / 55)<br>SVLING: [M5 x 45 12.9, 40 pack](https://www.amazon.com/dp/B0GHN852F3) ($7.19 / 40)<br>SVLING: [M5 x 50 12.9, 40 pack](https://www.amazon.com/dp/B0GHNQFZYR) ($7.59 / 40)<br>PDETVEO: [M5 nyloc SS304, 50 pack](https://www.amazon.com/dp/B0D8THJQNM) ($4.79 / 50) | M5x12 and M5x20 are in the next table. |
| Countersunk, set screws and M3 nuts | M3x8 countersunk: 4, M3x8 cup-point set screw: 10, M3 hex nut: 16 | Amazing Screws: [M3 x 8 cup-point set screws, 50 pack](https://www.amazon.com/dp/B0CG25FMG6) ($6.49 / 50) | The four M3x8 countersunk screws are in the next table. The M3 nuts come with the M3 kit. |
| M3 T-nuts for 4040 slot 8 | 66 | Still Awake: [M3 hammer-head drop-in, 40 series 8 mm slot, 50 pack](https://www.amazon.com/dp/B08ZNGWDG7) ($9.99 / 50 (need 2)) | 66 needed, so two packs of 50. Check they fit the QNK slot. |
| M5 T-nuts for 4040 slot 8 | 28 | Still Awake: [M5 hammer-head, 8 mm slot, 50 pack](https://www.amazon.com/dp/B08ZNFXLT4) ($11.99 / 50) |  |
| M5 T-nuts for 2020 slot 6 | 4 | Mriuuod US: [M5 roll-in spring T-nut, 2020, 70 pack](https://www.amazon.com/dp/B0DPJRHQNH) ($4.99 / 70) |  |
| M3 T-nuts for 1515 metric | 12 | PZRT: [M3 roll-in T-nut for 1515, 24 pack](https://www.amazon.com/dp/B08BRDPBTJ) ($9.99 / 24) |  |
| Heat-set inserts | M3 standard: 27, M3 short (3-4 mm): 4, M4: 14, M5: 6 | ruthex (sold by ruthex): [Assortment: 100 M3x5.7, 50 M4x8.1, 50 M5x9.5 (+70 M2)](https://www.amazon.com/dp/B08K1BVGN9) ($29.99) | The four short M3 inserts are in the next table. |
| Zip ties, 2.5 mm | a few | Amazon: [HS 100 x 2.5 mm black, 200 pack](https://www.amazon.com/dp/B0CZ3Y7YSC) ($4.49 / 200) |  |
| Powered USB hub for the top-hat tray | 1 | Waveshare: [4-port USB 3.2 hub, 7-36 V DC in, metal, wall-mount holes](https://www.amazon.com/dp/B0D97V3N3R) ($27.99) | Check it against the 100 x 140 mm tray. |
| Qidi Plus 4 / Q2 silicone nozzle wiper, 27 x 15 x 4.7 mm | 5 (one per station: one 5 pack, a second for spares) | Qidi: [Plus4 Wiper Silicone Case, 5 pcs](https://us.qidi3d.com/products/plus4-wiper-silicone-case) ($2.99 / 5, 31 Oct 2026) | Glue each into a slider pocket with high-temperature RTV, 27 mm across. |
| PG9 cable gland | 1 | SUMSGOND: [PG9 nylon cable gland 4-8 mm, 20 pack](https://www.amazon.com/dp/B08TCF3S13) ($9.99 / 20) |  |

## Screws, inserts and Z drive pulleys

The screw kits above leave these out. The Z drive pulleys are bought oversize and reworked on a lathe.

| Item | Qty needed | Example source | Notes |
|---|---|---|---|
| M3 x 10 socket head cap screws | 53 more (93 needed, the kit has 40) | zw99 Store: [M3 x 10 12.9, 100 pack](https://www.amazon.com/dp/B07CMSBQ11) ($6.77 / 100) |  |
| M3 x 40 socket head cap screws | 2 | zw99 Store: [M3 x 40 12.9, 50 pack](https://www.amazon.com/dp/B0FLKDZRSK) ($5.96 / 50) |  |
| M4 x 18 socket head cap screws | 4 | zw99 Store: [M4 x 18 12.9, 100 pack](https://www.amazon.com/dp/B07CKVYJ42) ($6.56 / 100) |  |
| M4 x 35 socket head cap screws | 4 | SVLING: [M4 x 35 12.9, 60 pack](https://www.amazon.com/dp/B0GHN4WNBR) ($7.64 / 60) |  |
| M5 x 12 and M5 x 20 socket head cap screws | x12: 2, x20: 4 | SVLING: [290-piece M5 12.9 kit: 12 x M5x12, 8 x M5x20 (+ x8, x10, x16, x25, x30, nuts, washers)](https://www.amazon.com/dp/B0GG8RHBP7) ($7.99) |  |
| M3 x 8 countersunk screws | 4 | HirtuOtter-USA: [M3 x 8 countersunk 10.9, 40 pack](https://www.amazon.com/dp/B0G3H2XQWD) ($5.89 / 40) |  |
| Short M3 heat-set inserts, 3-4 mm long | 4 | ruthex: [RX-M3Sx4.0 short M3, 100 pack](https://www.amazon.com/dp/B09ZHSGHXD) ($9.99 / 100) |  |
| Z drive pulley, 2GT 20T for 12 mm belt, 6 mm bore | 4 | Every Tool DIY: [Generic 2GT 20T 6 mm bore (15 mm belt size), to face down](https://www.amazon.com/dp/B0GN4SPFJ8) ($9.43) | Sold singly: 4 needed. Ships from abroad (delivery shown 17-27 Nov). Rework each one on the lathe: cut off the hub (with its grub screws) and both flanges, then face the teeth to 12.4-12.6 mm long. Drill 2.5 mm and tap M3 into the bottom of one tooth groove, halfway along. Use the grub screw from Sovol's stock 9 mm drive pulley: it is the same 20T, 6 mm bore, so that length sits below the teeth. Deburr the bore and faces. |

## Also needed

* Raspberry Pi 5 (size its 5 V supply to suit)
* Raspberry Pi 5 Active Cooler
* microSD card, 64 GB A2
* 24 V to 5 V, 5 A regulator for the Pi
* Micro-HDMI to HDMI cable, about 1 m
* Short USB-C to USB-A data cable (Link Board to hub) (20 cm or shorter, for Bondtech's 2 m USB limit)
* Kraken-to-Pi and hub-to-Pi cables
* 24 V fan for the Kraken drivers
* High-temperature red RTV silicone
* PC4-M10 push-fit couplers
* Umbilical take-up spring
* Filament for the printed parts: about 1.05 kg PPS-CF and 2.4 kg ASA (top hat)
* Wiring consumables: 24 V / 48 V wire, ferrules, JST-XH and Molex crimps, sleeving
* A spool of 4 mm OD PTFE tube for the five filament paths
* Any spare INDX tools or a CF-rated nozzle tool
