# PDN Bug Root Cause & Fix

## Bug Summary
Macro power pins were not getting connected, and standard cells were unconnected to the power grid, causing connectivity check failures during PDN generation.

---

## Root Cause

When using **custom PDN configuration** (`FP_PDN_CFG`), you bypass OpenLane's default PDN script which automatically creates MET1 power rails for standard cells.

### The Problem Chain:

1. **Custom PDN Override Enabled**
   ```json
   "FP_PDN_CFG": "dir::pdn_override_2.tcl"
   ```
   - This tells OpenLane: "Don't use your default PDN script, use mine instead"
   - Default script includes automatic MET1 rail creation
   - Custom script must recreate ALL PDN functionality

2. **Missing MET1 Power Rails**
   - Original `pdn_override_2.tcl` only created MET3/MET4/MET5 stripes
   - Standard cells connect via VPWR/VGND pins on **MET1**
   - Without MET1 rails, standard cells were completely unpowered

3. **Missing MET1→MET3 Vias**
   - Even with upper metal stripes, no connection path existed from standard cells to the grid
   - Vias only connected MET3→MET4→MET5, leaving MET1 isolated

4. **Missing Macro Connection Flag**
   ```json
   "PDN_CONNECT_MACROS_TO_GRID": true  // This was missing
   ```
   - Without this flag, `set_global_connections()` doesn't process `PDN_MACRO_CONNECTIONS`
   - Macro power pins (VDDC, VDDA, VSS) were not mapped to wrapper nets (vccd1, vdda1, vssd1)

---

## What Standard Flow Does Automatically

In a **normal flow without macros and without custom PDN**, OpenLane's default script includes:

```tcl
# Automatically created by OpenLane's default PDN script:
add_pdn_stripe -grid std_cell -layer met1 -followpins
add_pdn_stripe -grid std_cell -layer met4 -width 1.6 -pitch 153.6
add_pdn_stripe -grid std_cell -layer met5 -width 1.6 -pitch 153.18

add_pdn_connect -grid std_cell -layers "met1 met4"
add_pdn_connect -grid std_cell -layers "met4 met5"
```

**You never see this code** - it just works!

---

## What Was Missing in Custom Script

### Original (Broken) pdn_override_2.tcl
```tcl
# ❌ NO MET1 RAILS - standard cells can't get power!
add_pdn_stripe -grid core -layer met3 -width 6 -pitch 180 -offset 20
add_pdn_stripe -grid core -layer met4 -width 6 -pitch 180 -offset 20
add_pdn_stripe -grid core -layer met5 -width 6 -pitch 180 -offset 46

define_pdn_grid -macro -default -name macro -starts_with POWER -halo "5 5"

# ❌ NO MET1→MET3 CONNECTION - MET1 is isolated!
add_pdn_connect -grid core  -layers "met3 met4"
add_pdn_connect -grid core  -layers "met4 met5"
add_pdn_connect -grid macro -layers "met3 met4"

pdngen
```

### Result:
```
Standard Cells (VPWR/VGND on MET1)
         ↓
      [NOTHING]  ← No MET1 rails!
         ↓
      MET3 ←────────────── Macro pins (VDDC/VDDA/VSS)
       ↓
      MET4
       ↓
      MET5
       ↓
   Core Ring
```

The power grid existed at upper layers, but had **no connection to standard cells**!

---

## The Fix

### 1. Added MET1 Rails to Custom Script

```tcl
# ✅ ADDED: MET1 power rails for standard cells
# This creates power/ground rails on every standard cell row
add_pdn_stripe -grid core -layer met1 -width 0.48 -followpins -starts_with POWER
```

**What this does:**
- `-followpins`: Automatically places rails along standard cell rows
- `-width 0.48`: Matches standard cell power rail width (0.48µm for sky130)
- Creates both POWER and GROUND rails alternating by row

### 2. Added MET1→MET3 Via Connections

```tcl
# ✅ ADDED: Connect MET1 to MET3
# This creates vias wherever MET1 rails cross MET3 stripes
add_pdn_connect -grid core -layers "met1 met3"

# Existing connections (now form complete chain)
add_pdn_connect -grid core -layers "met3 met4"
add_pdn_connect -grid core -layers "met4 met5"
```

### 3. Enabled Macro Connection Processing

**config.json:**
```json
{
  "PDN_CONNECT_MACROS_TO_GRID": true,  // ✅ ADDED
  "PDN_MACRO_CONNECTIONS": [
    "neuro_inst vccd1 vssd1 VDDC VSS",
    "neuro_inst vdda1 vssd1 VDDA VSS"
  ]
}
```

**What this does:**
- Tells `set_global_connections()` to process the macro connection list
- Maps macro pin VDDC → wrapper net vccd1
- Maps macro pin VDDA → wrapper net vdda1
- Maps macro pin VSS → wrapper net vssd1

### Complete Power Delivery Path (After Fix):

```
Standard Cells (VPWR/VGND)
         ↓
      MET1 rails  ← ✅ Now exists!
         ↓
      [via]       ← ✅ Now connects!
         ↓
      MET3 stripes ←────── Macro pins (VDDC/VDDA/VSS)
         ↓
      [via]
         ↓
      MET4 stripes
         ↓
      [via]
         ↓
      MET5 stripes
         ↓
    Core Ring
```

---

## Why This Happens

### The OpenLane PDN Architecture

OpenLane has two PDN modes:

#### Mode 1: Default (No Custom Script)
- Uses built-in script: `scripts/openroad/common/pdn.tcl`
- Automatically includes MET1 rails
- Works for 90% of designs
- **You don't need to understand how it works**

#### Mode 2: Custom Script (For Macros)
- Triggered by: `"FP_PDN_CFG": "dir::your_script.tcl"`
- **Completely replaces** the default script
- **You must recreate everything**, including MET1 rails
- Required when:
  - You have hardened macros
  - Macro power pins are on specific metal layers
  - Multiple power domains (analog/digital)

### The Trap:

When you look at PDN examples online or in documentation, they often show:
```tcl
add_pdn_stripe -layer met3 ...
add_pdn_stripe -layer met4 ...
add_pdn_stripe -layer met5 ...
```

**This looks complete!** But it's not - the MET1 line is assumed/implicit because most examples don't need to show the full script.

---

## Symptoms of This Bug

1. **PSM-0039 Warnings**: "Unconnected instance PHY_EDGE_ROW_*/VPWR"
   - Tap/endcap cells reporting no power connection
   - These are standard cells, need MET1 rails

2. **PSM-0069 Errors**: "Check connectivity failed on vccd1/vssd1"
   - Power grid topology check fails
   - Indicates islands/gaps in power distribution

3. **Macro Pins Unconnected**
   - Even if grid exists, macro pins don't connect
   - Need explicit mapping via `PDN_MACRO_CONNECTIONS`

---

## Lessons Learned

### ⚠️ Gotcha #1: Custom PDN = Full Responsibility
When you set `FP_PDN_CFG`, you're saying "I'll handle ALL power delivery". Don't assume anything is automatic.

### ⚠️ Gotcha #2: MET1 is Critical But Invisible
Most PDN diagrams show MET3/4/5 because they're visible in the floorplan. MET1 is hidden under cells, so it's easy to forget.

### ⚠️ Gotcha #3: Macros Need Explicit Configuration
Unlike standard cells (auto-discovered via VPWR/VGND), macros need:
- Pin name mapping (VDDC → vccd1)
- Instance name mapping (neuro_inst)
- Enable flag (`PDN_CONNECT_MACROS_TO_GRID`)

### ⚠️ Gotcha #4: Via Layers Must Form Complete Chain
If you have layers [MET1, MET3, MET4, MET5], you need connections:
- MET1 → MET3
- MET3 → MET4
- MET4 → MET5

Missing ANY link breaks the chain!

---

## Files Changed

### 1. `openlane/user_project_wrapper/pdn_override_2.tcl`
**Lines 42-44** - Added MET1 power rails:
```tcl
# 5) Standard cell rails (MET1) - CRITICAL for powering standard cells
#    These follow the standard cell rows (every 2.72um = one row height)
add_pdn_stripe -grid core -layer met1 -width 0.48 -followpins -starts_with POWER
```

**Line 57** - Added MET1→MET3 via connections:
```tcl
add_pdn_connect -grid core  -layers "met1 met3"
```

### 2. `openlane/user_project_wrapper/config.json`
**Line 51** - Enabled macro connection processing:
```json
"PDN_CONNECT_MACROS_TO_GRID": true,
```

---

## Verification

After the fix, you should see in the PDN log:

```
[INFO] Setting global connections...
neuro_inst matched with neuro_inst  ← Macro VDDC connection
neuro_inst matched with neuro_inst  ← Macro VDDA connection

[INFO PDN-0001] Inserting grid: core
[INFO PDN-0001] Inserting grid: macro - neuro_inst

[INFO PSM-0040] All shapes on net vccd1 are connected.  ← ✅ Success!
[INFO PSM-0040] All shapes on net vdda1 are connected.  ← ✅ Success!
[INFO PSM-0040] All shapes on net vssd1 are connected.  ← ✅ Success!
```

No more PSM-0039 or PSM-0069 errors!

---

## Reference: Complete Fixed Script

See `openlane/user_project_wrapper/pdn_override_2.tcl` for the complete working version.

Key sections:
1. Lines 5-10: Global connections (processes PDN_MACRO_CONNECTIONS)
2. Lines 42-44: **MET1 rails for standard cells** ← Critical fix!
3. Lines 46-50: MET3/4/5 stripes for distribution
4. Lines 52-53: Macro grid definition
5. Lines 55-60: **Via connections including MET1→MET3** ← Critical fix!

---

## Date & Context
- **Date Fixed**: November 2, 2025
- **OpenLane Version**: LibreLane (OpenLane 2.x)
- **PDK**: sky130A
- **Design**: Caravel user_project_wrapper with Neuromorphic_X1_wb macro
- **Issue Duration**: Multiple runs failed with connectivity errors
- **Root Cause**: MET1 power rails omitted from custom PDN script
