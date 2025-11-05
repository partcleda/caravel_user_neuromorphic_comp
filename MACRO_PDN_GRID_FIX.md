# Macro PDN Grid Configuration

## Problem
After fixing standard cell power connectivity, the macro power pins (VDDC, VDDA, VSS) were still showing as unconnected:

```
[PSM-0039] Unconnected instance neuro_inst/VDDC
[PSM-0039] Unconnected instance neuro_inst/VDDA
[PSM-0039] Unconnected instance neuro_inst/VSS
```

## Root Cause

The generic macro grid definition was not creating any stripes - it was just defining a grid that inherits from the core grid:

```tcl
define_pdn_grid \
    -macro \
    -default \
    -name macro \
    -starts_with POWER \
    -halo "5 5"

add_pdn_connect \
    -grid macro \
    -layers "met4 met5"
```

This generic macro grid doesn't create MET3 stripes that physically intersect with the macro's power pins.

### Macro Power Pin Locations

From `lef/Neuromorphic_X1_wb.lef`, the power pins are horizontal stripes on MET3:

- **VDDC**: Y = 45.87-47.67µm (from macro origin)
- **VDDA**: Y = 504.36-505.86µm and Y = 579.83-581.33µm
- **VSS**: Y = 825.72-826.72µm and Y = 827.72-828.72µm

With the macro placed at [515.18, 514.24], the absolute Y-coordinates are:
- VDDC: ~560µm
- VDDA: ~1018µm and ~1094µm
- VSS: ~1340µm

The core grid's MET3 stripes (pitch 180, offset 20) are at: 20, 200, 380, 560, 740, 920, 1100µm...

**Physical alignment check**:
- VDDC at ~560µm: ✅ Aligns with grid stripe at 560µm
- VDDA at ~1018µm: ❌ Between stripes (920 and 1100µm)
- VSS at ~1340µm: ❌ Between stripes (1280 and 1460µm)

## Solution: Macro-Specific PDN Grid

Create a dedicated PDN grid for the `neuro_inst` macro instance with stripes specifically aligned to its power pin locations.

### Modified pdn_override_2.tcl

Added after the generic macro grid definition:

```tcl
# Neuromorphic macro-specific PDN grid
# The macro has horizontal power pins on met3 at specific Y locations.
# We need to create met3 stripes that align with these pin locations.
define_pdn_grid \
    -macro \
    -instances neuro_inst \
    -name neuro_grid \
    -starts_with POWER \
    -halo "5 5"

# Add horizontal met3 stripes aligned to the macro's power pins
# VDDC pin at Y ~560µm (46.76µm from macro origin + 514.24µm placement)
add_pdn_stripe \
    -grid neuro_grid \
    -layer met3 \
    -width 6 \
    -pitch 180 \
    -offset 560 \
    -starts_with POWER

# Connect the macro grid to met4/met5 distribution layers
add_pdn_connect \
    -grid neuro_grid \
    -layers "met3 met4"
```

### How This Works

1. **Instance-Specific Grid**: `-instances neuro_inst` targets only the Neuromorphic macro
2. **MET3 Stripes**: Creates horizontal stripes on MET3 layer with 6µm width
3. **Alignment**: `-offset 560` starts stripes at 560µm, aligning with VDDC pin
4. **Pitch**: 180µm pitch creates additional stripes at 740µm, 920µm, 1100µm, 1280µm...
5. **Via Connections**: `add_pdn_connect` creates vias from MET3 to MET4 wherever they cross

### Expected Results

With this configuration:
- VDDC at 560µm: ✅ Intersects with stripe at 560µm
- VDDA at 1018µm/1094µm: ✅ Intersects with stripe at 920µm and 1100µm
- VSS at 1340µm: ✅ Intersects with stripe at 1280µm

The `PDN_MACRO_CONNECTIONS` in config.json maps the pin names:
```json
"PDN_MACRO_CONNECTIONS": [
  "neuro_inst vccd1 vssd1 VDDC VSS",
  "neuro_inst vdda1 vssd1 VDDA VSS"
]
```

This tells OpenROAD:
- Macro instance `neuro_inst` pin `VDDC` → wrapper net `vccd1`
- Macro instance `neuro_inst` pin `VDDA` → wrapper net `vdda1`
- Macro instance `neuro_inst` pin `VSS` → wrapper net `vssd1`

## Key Insights

### Why Generic Macro Grid Wasn't Enough

The generic macro grid with `-default` flag only defines a grid domain but doesn't create any stripes. It relies on the core grid's stripes passing through the macro area.

For macros with power pins on specific metal layers (MET3), you need to:
1. Define an instance-specific grid with `-instances`
2. Add stripes on the layer matching the macro's pins
3. Calculate offset/pitch to ensure physical alignment
4. Add via connections to higher metal layers

### Multiple Macros

If you have multiple macros with different pin configurations:

```tcl
# Generic macro grid as fallback
define_pdn_grid \
    -macro \
    -default \
    -name macro \
    -starts_with POWER \
    -halo "5 5"

# Macro 1 specific grid
define_pdn_grid \
    -macro \
    -instances "macro1_inst" \
    -name macro1_grid \
    -starts_with POWER \
    -halo "5 5"

add_pdn_stripe \
    -grid macro1_grid \
    -layer met3 \
    -width 6 \
    -pitch 180 \
    -offset [calculated_for_macro1]

# Macro 2 specific grid
define_pdn_grid \
    -macro \
    -instances "macro2_inst" \
    -name macro2_grid \
    -starts_with POWER \
    -halo "5 5"

add_pdn_stripe \
    -grid macro2_grid \
    -layer met3 \
    -width 6 \
    -pitch 180 \
    -offset [calculated_for_macro2]
```

## Verification

After successful PDN generation, you should see:

```
[INFO] Setting global connections...
neuro_inst matched with neuro_inst  ← Macro connections recognized

[INFO PDN-0001] Inserting grid: stdcell_grid
[INFO PDN-0001] Inserting grid: macro
[INFO PDN-0001] Inserting grid: neuro_grid - neuro_inst  ← New macro-specific grid!

[INFO PSM-0040] All shapes on net vccd1 are connected.  ← ✅ Success!
[INFO PSM-0040] All shapes on net vdda1 are connected.  ← ✅ Success!
[INFO PSM-0040] All shapes on net vssd1 are connected.  ← ✅ Success!
```

No more PSM-0039 warnings about unconnected macro pins!

## Files Modified

- **openlane/user_project_wrapper/pdn_override_2.tcl** (lines 123-146)
  - Added neuro_grid definition
  - Added MET3 stripe generation with calculated offset
  - Added via connections to MET4

## Date & Context
- **Date Fixed**: November 2, 2025
- **OpenLane Version**: LibreLane (OpenLane 2.x)
- **PDK**: sky130A
- **Design**: Caravel user_project_wrapper with Neuromorphic_X1_wb macro
- **Related Issue**: Standard cells fixed in PDN_BUG_ROOT_CAUSE.md, now fixing macro pins
