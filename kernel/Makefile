# SAGCO Kernel Module Build
# License: GPL v2 (kernel module) / SSL-1.0 (SAGCO runtime)
# Usage:
#   make        — build sagco_cpu_mod.ko against running kernel
#   make clean  — remove build artifacts
#   make load   — insmod the module (requires root)
#   make unload — rmmod the module (requires root)
#   make test   — probe version via ioctl (requires sagco_cpu_test binary)

obj-m := sagco_cpu_mod.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

load: sagco_cpu_mod.ko
	sudo insmod sagco_cpu_mod.ko
	@echo "SAGCO_CPU: /dev/sagco_cpu should now be available"

unload:
	sudo rmmod sagco_cpu_mod
	@echo "SAGCO_CPU: module unloaded"

test:
	@echo "SAGCO_CPU VERSION=$(cat /sys/module/sagco_cpu_mod/version 2>/dev/null || echo 'module not loaded')"

.PHONY: all clean load unload test
