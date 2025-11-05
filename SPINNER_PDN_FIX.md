# PDN Bug Root Cause & Fix

## Bug Summary
Macro power pins were not getting connected, and standard cells were unconnected to the power grid, causing connectivity check failures during PDN generation.

## Root Cause
The spinner power pins are vertical stripes on met4, and they must be **physically aligned** with the core PDN grid stripes for electrical connection.

## Solution

### 1. Power Pin Names
- **Spinner LEF has:** VDDC, VSS (correct after rebuild)
- **Config must use:** VDDC, VSS (matching the LEF)

### 2. Critical Placement Calculation
```
Grid stripe locations: 20, 200, 380, 560, ... (pitch=180, offset=20)
Spinner VDDC pin center: 21.84µm from spinner origin
Required spinner X position = 200 - 21.84 = 178.16µm
```

**DO NOT change spinner location from [178.16, 100]**

### 3. Configuration Files

#### `openlane/user_project_wrapper/config.json` line 53:
```json
"spinner_inst": { "location": [178.16, 100], "orientation": "N" }
```

#### `openlane/user_project_wrapper/config.json` line 63:
```json
"spinner_inst vccd1 vssd1 VDDC VSS"
```

#### `openlane/user_project_wrapper/pdn_override_2.tcl` line 48-49:
```tcl
# 6) Macro grid only for mprj (spinner has aligned power pins, uses core grid)
define_pdn_grid -macro -instances "mprj" -name macro -starts_with POWER -halo "5 5"
```

### 4. Spinner Build Config
#### `openlane/spinner/config.json`:
```json
"VDD_PIN": "VDDC",
"GND_PIN": "VSS",
```

## Why This Works
1. Spinner is placed so its VDDC pin (at 21.84µm offset) lands exactly on grid stripe at X=200µm
2. Core PDN grid met4 stripes pass through spinner location
3. No macro grid is created for spinner (only for mprj)
4. PDN_MACRO_CONNECTIONS maps vccd1→VDDC and vssd1→VSS
5. Electrical connection is made where stripe overlaps pin

## Testing
After fixing, you should NOT see these warnings:
- `[PSM-0039] Unconnected instance spinner_inst/VDDC`
- `[PSM-0038] Unconnected node on net vccd1 at location (200.000um, ...)`

## Important
**The location [178.16, 100] is calculated for alignment. Changing it will break PDN connection!**
