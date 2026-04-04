"""
get_inventory.py

Standalone script: reads the reagent JSON for a given experiment type,
formats it into plain text, and prints to stdout.

Usage:
    python get_inventory.py [experiment_type]

experiment_type options: rpa, rna, storage, amplification, detection, write, read, polya
Defaults to the general inventory if no type is given.
"""

import sys
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

EXPERIMENT_TYPE_MAP = {
    "rpa":           "reagent_RPA.json",
    "rna":           "reagent_RNA.json",
    "storage":       "reagent_storage.json",
    "amplification": "reagent_amplification.json",
    "detection":     "reagent_detection.json",
    "write":         "reagent_write.json",
    "read":          "reagent_read.json",
    "polya":         "reagent_polyA.json",
}
DEFAULT_FILE = "reagent_inventory.json"


def load_inventory(experiment_type: str = "") -> list:
    filename = EXPERIMENT_TYPE_MAP.get(experiment_type.lower(), DEFAULT_FILE)
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def format_reagents(reagents: list) -> str:
    lines = []
    manuals = []

    for reagent in reagents:
        names = [reagent["name"]] + reagent.get("aliases", [])
        name_str = " or ".join(f'"{name}"' for name in names)

        line = f"{name_str}: "

        props = reagent.get("properties", {})
        if "concentration" in props:
            conc = props["concentration"]
            line += f"{conc['value']}{conc['unit']}, "

        if "ph" in props:
            line += f"pH {props['ph']}, "

        if "form" in reagent:
            line += f"{reagent['form'].lower()}, "

        if "components" in reagent:
            parts = []
            for comp in reagent["components"]:
                if isinstance(comp, dict):
                    if "concentration" in comp:
                        parts.append(f"{comp['name']} ({comp['concentration']})")
                    else:
                        parts.append(comp["name"])
                else:
                    parts.append(comp)
            line += f"components: {', '.join(parts)}, "

        if "documentation" in reagent:
            line += f"doc: {', '.join(reagent['documentation'])}, "
            for manual in reagent["documentation"]:
                if manual not in manuals:
                    manuals.append(manual)

        if "notes" in reagent:
            line += f"notes: {reagent['notes']}, "

        line = line.rstrip(", ")
        lines.append(line)

    if manuals:
        lines.append("<manuals> " + ", ".join(manuals))

    return "\n".join(lines)


if __name__ == "__main__":
    experiment_type = sys.argv[1] if len(sys.argv) > 1 else ""
    inventory = load_inventory(experiment_type)
    print(format_inventory := format_reagents(inventory))
