"""
DMGT Unit 2 — relations built from actual manufacturing data.

Sets, ordered pairs, domain, range, and an equivalence relation:
units that share the same machine.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from app.database import db


def _pairs(rows: List[Dict[str, Any]], left: str, right: str) -> Set[Tuple[str, str]]:
    return {(str(r[left]), str(r[right])) for r in rows}


def analyze_relation(relation: Set[Tuple[str, str]], universe: Set[str]) -> Dict[str, Any]:
    domain = {a for a, _ in relation}
    rng = {b for _, b in relation}
    reflexive = all((x, x) in relation for x in universe)
    symmetric = all((b, a) in relation for a, b in relation)
    transitive = True
    lookup = {}
    for a, b in relation:
        lookup.setdefault(a, set()).add(b)
    for a in list(lookup):
        for b in list(lookup.get(a, [])):
            for c in lookup.get(b, []):
                if c not in lookup.get(a, set()):
                    transitive = False
                    break
            if not transitive:
                break
        if not transitive:
            break
    equivalence = reflexive and symmetric and transitive
    return {
        "pair_count": len(relation),
        "domain": sorted(domain),
        "range": sorted(rng),
        "reflexive": reflexive,
        "symmetric": symmetric,
        "transitive": transitive,
        "equivalence": equivalence,
        "sample_pairs": sorted(list(relation))[:12],
    }


def dmgt_report() -> Dict[str, Any]:
    products = {r["product_id"] for r in db.query("SELECT product_id FROM product")}
    batches = {r["batch_id"] for r in db.query("SELECT batch_id FROM batch")}
    machines = {r["machine_id"] for r in db.query("SELECT machine_id FROM machine")}
    defects = {r["defect_id"] for r in db.query("SELECT defect_id FROM defect")}
    units = db.query("SELECT unit_id, batch_id, status FROM production_unit")
    unit_ids = {r["unit_id"] for r in units}

    product_batch = _pairs(db.query("SELECT product_id, batch_id FROM batch"), "product_id", "batch_id")
    batch_machine = _pairs(db.query("SELECT batch_id, machine_id FROM batch"), "batch_id", "machine_id")
    unit_defect = _pairs(db.query("SELECT unit_id, defect_id FROM defect"), "unit_id", "defect_id")

    # Equivalence relation on units: same producing machine.
    unit_machine = db.query(
        """
        SELECT u.unit_id, b.machine_id
        FROM production_unit u
        JOIN batch b ON u.batch_id = b.batch_id
        """
    )
    machine_of = {r["unit_id"]: r["machine_id"] for r in unit_machine}
    same_machine: Set[Tuple[str, str]] = set()
    # Full cartesian on 200 units is 40k pairs — correct but huge on screen.
    # Use a representative subset (first 12 units) for the live proof, plus
    # the mathematical claim on the full set.
    sample_units = sorted(machine_of.keys())[:12]
    for a in sample_units:
        for b in sample_units:
            if machine_of[a] == machine_of[b]:
                same_machine.add((a, b))

    same_full_reflexive = all(machine_of[u] == machine_of[u] for u in machine_of)
    same_full_symmetric = True
    same_full_transitive = True  # equality of machine_id is an equivalence

    return {
        "sets": {
            "P (products)": sorted(products),
            "B (batches)": sorted(batches),
            "M (machines)": sorted(machines),
            "U (units)": f"{len(unit_ids)} unit identifiers (U10001 …)",
            "D (defects)": f"{len(defects)} defect identifiers",
        },
        "product_batch": {
            "name": "R_PB ⊆ P × B",
            "meaning": "Product p is manufactured in batch b",
            **analyze_relation(product_batch, products),
            "note": "Not reflexive on P: a product is not a batch.",
        },
        "batch_machine": {
            "name": "R_BM ⊆ B × M",
            "meaning": "Batch b was produced on machine m",
            **analyze_relation(batch_machine, batches),
            "note": "Used to trace a defective unit back to a machine.",
        },
        "unit_defect": {
            "name": "R_UD ⊆ U × D",
            "meaning": "Unit u has recorded defect d",
            **analyze_relation(unit_defect, unit_ids),
            "note": "Partial: many units have no defect pair.",
        },
        "same_machine_sample": {
            "name": "R_same ⊆ U_sample × U_sample",
            "meaning": "Units a and b were produced on the same machine",
            **analyze_relation(same_machine, set(sample_units)),
            "note": (
                f"On the full unit set, same-machine is an equivalence relation "
                f"(reflexive={same_full_reflexive}, symmetric={same_full_symmetric}, "
                f"transitive={same_full_transitive}) because it is equality of machine_id. "
                f"Sample below uses {len(sample_units)} units so the ordered pairs stay readable."
            ),
        },
        "trace_explanation": (
            "To trace a defective unit u: find the unique batch b such that (u, b) "
            "is in the unit-batch relation, then the unique machine m such that (b, m) "
            "is in R_BM, and the product p such that (p, b) is in R_PB. Defect details "
            "come from R_UD."
        ),
    }
