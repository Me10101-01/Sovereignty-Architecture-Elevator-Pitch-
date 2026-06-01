from importlib import import_module

PASS_ORDER = [
    ("src.passes.material_pass",    "MaterialPass"),
    ("src.passes.labor_pass",       "LaborPass"),
    ("src.passes.production_pass",  "ProductionPass"),
    ("src.passes.chrono_pass",      "ChronoPass"),
    ("src.passes.bid_pass",         "BidPass"),
]

def load_passes():
    passes = []
    for module_path, class_name in PASS_ORDER:
        mod = import_module(module_path)
        passes.append(getattr(mod, class_name)())
    return passes
