# SAGCO Hardware Build — iCE40 / Tang Nano synthesis
# License: SSL-1.0 — Strategickhaos DAO LLC
# Requires: yosys, nextpnr-ice40, icestorm
# Usage:
#   make sagco_fpga     — synthesize sagco_cpu_fpga  (iCE40 HX1K, Breakout Board)
#   make sagco16        — synthesize sagco_cpu16      (iCE40 UP5K, bare core)
#   make sim_fpga       — iverilog simulation, sagco_cpu_fpga
#   make sim16          — iverilog simulation, sagco_cpu16
#   make clean

YOSYS   := yosys
PNR     := nextpnr-ice40
PACK    := icepack
PROG    := iceprog
IVERILOG := iverilog

# iCE40 HX1K — iCEbreaker / iCEstick target
DEVICE_FPGA  := hx1k
PACKAGE_FPGA := tq144

# iCE40 UP5K — bare sovereign core
DEVICE_16  := up5k
PACKAGE_16 := sg48

# ── sagco_cpu_fpga ────────────────────────────────────────────────────────────
sagco_fpga: sagco_cpu_fpga.bin

sagco_cpu_fpga.json: sagco_cpu_fpga.v
	$(YOSYS) -p "synth_ice40 -top sagco_top -json $@" $<

sagco_cpu_fpga.asc: sagco_cpu_fpga.json sagco_cpu_fpga.pcf
	$(PNR) --$(DEVICE_FPGA) --package $(PACKAGE_FPGA) --pcf sagco_cpu_fpga.pcf --json $< --asc $@

sagco_cpu_fpga.bin: sagco_cpu_fpga.asc
	$(PACK) $< $@

flash_fpga: sagco_cpu_fpga.bin
	$(PROG) $<

# ── sagco_cpu16 (bare core — no top wrapper) ──────────────────────────────────
sagco16: sagco_cpu16.json

sagco_cpu16.json: sagco_cpu16.v
	$(YOSYS) -p "synth_ice40 -top sagco_cpu -json $@" $<

# ── Simulation ────────────────────────────────────────────────────────────────
sim_fpga: sagco_cpu_fpga.v
	$(IVERILOG) -o sim_fpga_out $<
	./sim_fpga_out

sim16: sagco_cpu16.v
	$(IVERILOG) -o sim16_out $<
	./sim16_out

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	rm -f *.json *.asc *.bin sim_fpga_out sim16_out

.PHONY: sagco_fpga sagco16 sim_fpga sim16 flash_fpga clean
