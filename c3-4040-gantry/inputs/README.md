# Inputs for the C3 scripts

The FreeCAD scripts in the folder above read these models.

| Folder | What | Source and licence |
|---|---|---|
| `stock_printer/` | `SV08_ORIGINAL_STOCK_REFERENCE.FCStd`: Sovol's "SV08 Max Unmodified" STEP converted to FreeCAD (1,824 bodies), plus its index. The scripts place it in the gantry frame with the translation (-341.7798, -141.8577, -301.4741) mm. | Sovol, [github.com/Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX) (no licence file there) |
| `vendor_references/bondtech/` | `INDX_simplified_1.19.step` (the Smart Head and tools) and the tool-dock STLs | Bondtech, [github.com/BondtechAB/INDX](https://github.com/BondtechAB/INDX), GPL-3.0 (`LICENSE`) |
| `vendor_references/beacon/` | `Beacon_RevH_Assm_Normal.STEP` | Beacon, MIT (`CAD_LICENSE`) |
| `tools/motion_bounds.py` | Swept-clearance helper (FreeCAD/OCC) | This project, GPL-3.0 |

The first run of `c3_check.py` converts the stock model into `c3/_cache/` (or into `$C2_STOCK_CACHE`). The other scripts read that cache.

The manufacturer catalogues and drawings the design was checked against (Gates, HIWIN, igus, LDO, McMaster-Carr, MISUMI, SKF and others) are not included. The design notes cite them by part number.
