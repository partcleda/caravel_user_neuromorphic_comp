# ---------------- pdn_override_compat_v2.tcl ----------------
# Compatible with older OpenROAD PDNGen (uses set_voltage_domain & pdngen)

# 1) Global power/ground pin connects (if available in your tree)
if {[info exists ::env(SCRIPTS_DIR)]} {
  set _gg "$::env(SCRIPTS_DIR)/openroad/common/set_global_connections.tcl"
  if {[file exists $_gg]} {
    source $_gg
    set_global_connections
  }
}

# 2) Ensure primary nets exist (defaults if envs missing)
if {![info exists ::env(VDD_NET)]} { set ::env(VDD_NET) vccd1 }
if {![info exists ::env(GND_NET)]} { set ::env(GND_NET) vssd1 }

# Optional: collect secondary rails if present in the DB
set secondary {}
if {![catch {ord::get_db_block}]} {
  foreach n {vdda1 vssa1 vccd2 vssd2} {
    set db_net [[ord::get_db_block] findNet $n]
    if {$db_net ne "NULL"} { lappend secondary $n }
  }
}

# 3) Voltage domain (older API)
#    -secondary_power can be empty; pass the list constructed above.
set_voltage_domain -name CORE -power $::env(VDD_NET) -ground $::env(GND_NET) \
  -secondary_power $secondary

# 4) Core PDN grid & ring (met4/met5); keep ring INSIDE die (8 Âµm)
define_pdn_grid -name core -starts_with POWER -voltage_domain CORE

# Older PDNGen accepts 2 numbers for -core_offset (horz vert). If yours
# needs 4 numbers (l b r t), change "8 8" to "8 8 8 8".
add_pdn_ring -grid core \
  -layers   "met4 met5" \
  -widths   "6 6" \
  -spacings "2 2" \
  -core_offset "8 8"

add_pdn_stripe -grid core -layer met1 -width 0.48 -offset 80 -followpins -starts_with POWER

# Minimal MET2: only 1-2 thin stripes for connectivity, positioned at die edges
# Use narrow width (1.6um) and place near boundaries where routing is lighter
add_pdn_stripe -grid core -layer met2 -width 1.6 -pitch 2800 -offset 100 -starts_with POWER

# 5) Power distribution on upper metals
add_pdn_stripe -grid core -layer met3 -width 4 -pitch 180 -offset 20 -starts_with POWER -extend_to_core_ring
add_pdn_stripe -grid core -layer met4 -width 4 -pitch 180 -offset 20 -starts_with POWER -extend_to_core_ring
add_pdn_stripe -grid core -layer met5 -width 4 -pitch 180 -offset 46 -starts_with POWER -extend_to_core_ring

# 6) Macro grid
define_pdn_grid -macro -default -name macro -starts_with POWER -halo "5 5"

# 7) Sequential layer connections with high max_rows to minimize via density
add_pdn_connect -grid core  -layers "met1 met2" -max_rows 50
add_pdn_connect -grid core  -layers "met2 met3"
add_pdn_connect -grid core  -layers "met3 met4"
add_pdn_connect -grid core  -layers "met4 met5"
add_pdn_connect -grid macro -layers "met3 met4"



