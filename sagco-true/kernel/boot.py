"""
SAGCO Kernel — Boot Sequence Runner
Executes kernel/boot.sagco on startup, then seeds identity, memory, and scheduler.
This Python file is the runtime shim; the logic lives in .sagco files.
"""

from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

# make language package importable from anywhere
_SAGCO_TRUE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_SAGCO_TRUE_ROOT.parent))

from sagco_true.language.vm.vm import SAGCOVirtualMachine, detect_world
from sagco_true.language.bytecode.compiler import compile_source


KERNEL_DIR = Path(__file__).parent
BOOT_SEQUENCE = [
    "boot.sagco",
    "identity.sagco",
    "memory.sagco",
    "scheduler.sagco",
    "syscall.sagco",
]


def boot(workspace: str | Path = ".") -> SAGCOVirtualMachine:
    workspace = Path(workspace)
    vm = SAGCOVirtualMachine()

    # seed critical pre-boot values
    vm.memory["boot.start"] = time.time()
    vm.memory["boot.workspace"] = str(workspace)
    vm.memory["world"] = detect_world()

    # load and execute each kernel file in order
    for filename in BOOT_SEQUENCE:
        path = KERNEL_DIR / filename
        if not path.exists():
            vm.bus.append(type("Signal", (), {
                "name": "kernel_file_missing",
                "payload": {"file": filename},
                "ts": time.time(),
            })())
            continue
        try:
            source = path.read_text()
            bc = compile_source(source, str(path))
            vm.run(bc)
        except Exception as exc:
            vm.memory[f"boot.error.{filename}"] = str(exc)

    vm.memory["boot.complete"] = True
    vm.memory["boot.end"] = time.time()
    vm.memory["boot.elapsed"] = vm.memory["boot.end"] - vm.memory["boot.start"]
    return vm


def boot_report(vm: SAGCOVirtualMachine) -> dict:
    return {
        "world":     vm.world,
        "elapsed":   round(vm.memory.get("boot.elapsed", 0), 4),
        "signals":   [s.name for s in vm.bus],
        "memory_keys": len(vm.memory),
        "truth":     vm.truth_report(),
        "pids":      vm.pid_dump(),
    }


if __name__ == "__main__":
    vm = boot(".")
    report = boot_report(vm)
    print(json.dumps(report, indent=2))
