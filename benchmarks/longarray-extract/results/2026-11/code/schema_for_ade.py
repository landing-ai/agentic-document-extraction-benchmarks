"""Translate Extend's LongArray-Extract schemas for ADE Extract.

The published schemas are standard JSON Schema plus two Extend-only keys:
  - "extend:type": "date"  -> Extend's engine normalises the value to an ISO date.
    Translated to ADE's documented equivalent, "format": "YYYY-MM-DD".
  - "extend:type": "currency" -> structural hint only; the object already
    defines amount (number) + iso_4217_currency_code. Dropped.
  - "extend:descriptions" -> one description per enum value (same order).
    Appended to the field's "description" as "Allowed values: A = ...; B = ...".
Nothing else changes: same fields, types, enums and descriptions. ADE ignores
keywords it doesn't support ("required"), as documented.

Usage: python -I schema_for_ade.py  (writes data/schemas_ade/<vertical>.json and prints a diff summary)
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def translate(node, changes: list[str], path: str = "$"):
    if isinstance(node, list):
        return [translate(x, changes, f"{path}[{i}]") for i, x in enumerate(node)]
    if not isinstance(node, dict):
        return node
    out = {}
    for k, v in node.items():
        if k.startswith("extend:"):
            continue
        out[k] = translate(v, changes, f"{path}.{k}")
    et = node.get("extend:type")
    if et == "date":
        out["format"] = "YYYY-MM-DD"
        changes.append(f"{path}: extend:type=date -> format=YYYY-MM-DD")
    elif et is not None:
        changes.append(f"{path}: extend:type={et} dropped (structure already explicit)")
    descs = node.get("extend:descriptions")
    if descs is not None:
        enum = node.get("enum") or []
        pairs = "; ".join(f"{json.dumps(val) if val is None else val} = {d}"
                          for val, d in zip(enum, descs) if d)
        base = (node.get("description") or "").rstrip()
        out["description"] = (base + " " if base else "") + f"Allowed values: {pairs}"
        changes.append(f"{path}: extend:descriptions ({len(descs)}) appended to description")
    return out


def main() -> None:
    src, dst = HERE / "data" / "schemas", HERE / "data" / "schemas_ade"
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.json")):
        changes: list[str] = []
        schema = translate(copy.deepcopy(json.loads(f.read_text())), changes)
        (dst / f.name).write_text(json.dumps(schema, indent=2))
        print(f.stem)
        for c in changes:
            print("  ", c)


if __name__ == "__main__":
    main()
