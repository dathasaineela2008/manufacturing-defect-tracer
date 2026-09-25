"""
Create fictional sample manufacturing data.

Writes:
  database/sample_data.sql
  ml/dataset.csv

Run:  python scripts/generate_sample_data.py
"""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
random.seed(2026)

PRODUCTS = [
    ("P01", "Industrial Pump", "Hydraulics", "Centrifugal pump for plant water circuits"),
    ("P02", "Hydraulic Valve", "Hydraulics", "Pressure-control valve assembly"),
    ("P03", "Gear Assembly", "Powertrain", "Helical gear set for conveyor drives"),
    ("P04", "Bearing Housing", "Mechanical", "Cast housing for roller bearings"),
    ("P05", "Conveyor Roller", "Material Handling", "Steel roller with sealed ends"),
    ("P06", "Motor Stator", "Electrical", "Three-phase stator winding pack"),
    ("P07", "Pressure Sensor", "Instrumentation", "0-10 bar industrial sensor"),
    ("P08", "Control Panel", "Electrical", "Operator control enclosure"),
    ("P09", "Shaft Coupling", "Mechanical", "Flexible coupling for motor shafts"),
    ("P10", "Filter Cartridge", "Process", "Replaceable process filter element"),
]

MACHINES = [
    ("M01", "CNC Machine 01", "CNC", "Bay A", "OPERATIONAL", 2100),
    ("M02", "CNC Machine 02", "CNC", "Bay A", "OPERATIONAL", 3400),
    ("M03", "CNC Machine 03", "CNC", "Bay B", "MAINTENANCE_REQUIRED", 5100),
    ("M04", "Press Line 04", "Hydraulic Press", "Bay B", "OPERATIONAL", 2800),
    ("M05", "Lathe Cell 05", "Lathe", "Bay C", "IDLE", 1600),
    ("M06", "Welding Station 06", "Welding", "Bay C", "OPERATIONAL", 4200),
    ("M07", "Assembly Cell 07", "Assembly", "Bay D", "OPERATIONAL", 1900),
    ("M08", "Inspection Rig 08", "Inspection", "Bay D", "OPERATIONAL", 900),
    ("M09", "Heat Furnace 09", "Heat Treatment", "Bay E", "UNDER_MAINTENANCE", 4700),
    ("M10", "Packaging Line 10", "Packaging", "Bay E", "OPERATIONAL", 2500),
]

SHIFTS = ["Morning", "Afternoon", "Night"]
DEFECT_TYPES = [
    ("Surface Crack", "HIGH"),
    ("Dimensional Drift", "MEDIUM"),
    ("Porosity", "MEDIUM"),
    ("Weld Spatter", "LOW"),
    ("Misalignment", "HIGH"),
    ("Contamination", "LOW"),
    ("Overheating Mark", "CRITICAL"),
    ("Thread Damage", "MEDIUM"),
    ("Coating Peel", "LOW"),
    ("Sensor Calibration Error", "HIGH"),
]


def sql_str(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    text = str(value).replace("'", "''")
    return f"'{text}'"


def main() -> None:
    batches = []
    start = date(2026, 8, 1)
    for i in range(1, 31):
        product = PRODUCTS[(i - 1) % 10]
        # Bias later batches onto M03 so analysis has a visible hotspot (association, not causation).
        if i % 5 == 0:
            machine = MACHINES[2]  # M03
        else:
            machine = MACHINES[(i - 1) % 10]
        prod_date = start + timedelta(days=i + (i % 3))
        qty = 6 if i > 20 else 7
        shift = SHIFTS[i % 3]
        temp = round(70 + (i % 7) * 4 + (8 if machine[0] == "M03" else 0), 2)
        pressure = round(4.0 + (i % 5) * 0.7 + (1.5 if machine[0] == "M03" else 0), 2)
        batch_id = f"B2026-{i:03d}"
        # Demo scenario uses B2026-041 in the prompt; map batch 25 label specially.
        if i == 25:
            batch_id = "B2026-041"
            product = PRODUCTS[0]  # P01 Industrial Pump
            machine = MACHINES[2]  # M03 CNC Machine 03
            prod_date = date(2026, 9, 18)
            shift = "Night"
        batches.append(
            {
                "batch_id": batch_id,
                "product_id": product[0],
                "machine_id": machine[0],
                "production_date": prod_date.isoformat(),
                "quantity": qty,
                "shift": shift,
                "temperature_c": temp,
                "pressure_bar": pressure,
            }
        )

    units = []
    unit_no = 1
    for batch in batches:
        for _ in range(batch["quantity"]):
            uid = f"U{10000 + unit_no}"
            serial = f"SN-2026-{unit_no:05d}"
            hour = 6 + (unit_no % 16)
            ptime = datetime.fromisoformat(batch["production_date"] + f"T{hour:02d}:{(unit_no * 7) % 60:02d}:00")
            units.append(
                {
                    "unit_id": uid,
                    "batch_id": batch["batch_id"],
                    "serial_number": serial,
                    "production_time": ptime.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "OK",
                }
            )
            unit_no += 1

    assert len(units) >= 200

    # Ensure U10025 belongs to B2026-041 per the Section 9 specification
    u10025 = next(u for u in units if u["unit_id"] == "U10025")
    u_b41 = next(u for u in units if u["batch_id"] == "B2026-041")
    orig_b = u10025["batch_id"]
    u10025["batch_id"] = "B2026-041"
    u10025["production_time"] = "2026-09-18 22:30:00"
    u_b41["batch_id"] = orig_b
    b_orig = next(b for b in batches if b["batch_id"] == orig_b)
    u_b41["production_time"] = b_orig["production_date"] + " 15:55:00"

    # Choose 50 defective units, always including U10025.
    candidates = [u for u in units if u["unit_id"] != "U10025"]
    defective = [u for u in units if u["unit_id"] == "U10025"]
    random.shuffle(candidates)
    defective.extend(candidates[:49])
    defective_ids = {u["unit_id"] for u in defective}
    for u in units:
        if u["unit_id"] in defective_ids:
            u["status"] = "DEFECTIVE"

    defects = []
    for idx, unit in enumerate(sorted(defective, key=lambda x: x["unit_id"]), start=1):
        if unit["unit_id"] == "U10025":
            dtype, sev = "Surface Crack", "HIGH"
            desc = "Linear surface crack detected during final inspection"
            det = date(2026, 9, 19)
        else:
            dtype, sev = DEFECT_TYPES[(idx + sum(ord(ch) for ch in unit["unit_id"])) % len(DEFECT_TYPES)]
            desc = f"Recorded {dtype.lower()} on unit {unit['unit_id']}"
            batch = next(b for b in batches if b["batch_id"] == unit["batch_id"])
            det = date.fromisoformat(batch["production_date"]) + timedelta(days=1)
        defects.append(
            {
                "defect_id": f"D{idx:03d}",
                "unit_id": unit["unit_id"],
                "defect_type": dtype,
                "severity": sev,
                "description": desc,
                "detected_date": det.isoformat(),
            }
        )

    maintenance = []
    maint_types = ["Preventive", "Corrective", "Calibration", "Lubrication"]
    for i, machine in enumerate(MACHINES, start=1):
        status = "OVERDUE" if machine[4] == "MAINTENANCE_REQUIRED" else "COMPLETED"
        if machine[4] == "UNDER_MAINTENANCE":
            status = "SCHEDULED"
        mdate = date(2026, 9, 1) + timedelta(days=i * 2)
        if status == "OVERDUE":
            mdate = date(2026, 6, 15)
        maintenance.append(
            (
                f"MN{i:03d}",
                machine[0],
                mdate.isoformat(),
                maint_types[i % 4],
                status,
                f"Academic sample maintenance record for {machine[0]}",
            )
        )

    lines = [
        "-- Fictional sample data for MDTPS (academic demonstration only).",
        "-- Demo login is inserted by the Flask seeder (password is hashed, not stored here).",
        "USE mdtps;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "DELETE FROM defect;",
        "DELETE FROM production_unit;",
        "DELETE FROM machine_maintenance;",
        "DELETE FROM batch;",
        "DELETE FROM machine;",
        "DELETE FROM product;",
        "SET FOREIGN_KEY_CHECKS = 1;",
        "",
        "-- Products",
    ]
    for p in PRODUCTS:
        lines.append(
            "INSERT INTO product (product_id, product_name, product_type, description) VALUES "
            f"({sql_str(p[0])}, {sql_str(p[1])}, {sql_str(p[2])}, {sql_str(p[3])});"
        )
    lines.append("\n-- Machines")
    for m in MACHINES:
        lines.append(
            "INSERT INTO machine (machine_id, machine_name, machine_type, location, status, operating_hours) VALUES "
            f"({sql_str(m[0])}, {sql_str(m[1])}, {sql_str(m[2])}, {sql_str(m[3])}, {sql_str(m[4])}, {m[5]});"
        )
    lines.append("\n-- Batches")
    for b in batches:
        lines.append(
            "INSERT INTO batch (batch_id, product_id, machine_id, production_date, quantity, shift, temperature_c, pressure_bar) VALUES "
            f"({sql_str(b['batch_id'])}, {sql_str(b['product_id'])}, {sql_str(b['machine_id'])}, "
            f"{sql_str(b['production_date'])}, {b['quantity']}, {sql_str(b['shift'])}, "
            f"{b['temperature_c']}, {b['pressure_bar']});"
        )
    lines.append("\n-- Production units")
    for u in units:
        lines.append(
            "INSERT INTO production_unit (unit_id, batch_id, serial_number, production_time, status) VALUES "
            f"({sql_str(u['unit_id'])}, {sql_str(u['batch_id'])}, {sql_str(u['serial_number'])}, "
            f"{sql_str(u['production_time'])}, {sql_str(u['status'])});"
        )
    lines.append("\n-- Defects")
    for d in defects:
        lines.append(
            "INSERT INTO defect (defect_id, unit_id, defect_type, severity, description, detected_date) VALUES "
            f"({sql_str(d['defect_id'])}, {sql_str(d['unit_id'])}, {sql_str(d['defect_type'])}, "
            f"{sql_str(d['severity'])}, {sql_str(d['description'])}, {sql_str(d['detected_date'])});"
        )
    lines.append("\n-- Machine maintenance")
    for rec in maintenance:
        lines.append(
            "INSERT INTO machine_maintenance (maintenance_id, machine_id, maintenance_date, maintenance_type, status, notes) VALUES "
            f"({sql_str(rec[0])}, {sql_str(rec[1])}, {sql_str(rec[2])}, {sql_str(rec[3])}, {sql_str(rec[4])}, {sql_str(rec[5])});"
        )

    out_sql = ROOT / "database" / "sample_data.sql"
    out_sql.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ML dataset: one row per unit with batch/machine features + binary label.
    batch_by_id = {b["batch_id"]: b for b in batches}
    machine_by_id = {m[0]: m for m in MACHINES}
    csv_path = ROOT / "ml" / "dataset.csv"
    csv_path.parent.mkdir(exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "unit_id",
                "machine_id",
                "product_id",
                "batch_id",
                "temperature",
                "pressure",
                "operating_hours",
                "shift",
                "previous_defects",
                "maintenance_status",
                "is_defective",
            ]
        )
        prev_by_machine = {m[0]: 0 for m in MACHINES}
        for unit in units:
            batch = batch_by_id[unit["batch_id"]]
            machine = machine_by_id[batch["machine_id"]]
            maint = "OVERDUE" if machine[4] == "MAINTENANCE_REQUIRED" else "COMPLETED"
            if machine[4] == "UNDER_MAINTENANCE":
                maint = "SCHEDULED"
            label = 1 if unit["status"] == "DEFECTIVE" else 0
            writer.writerow(
                [
                    unit["unit_id"],
                    batch["machine_id"],
                    batch["product_id"],
                    batch["batch_id"],
                    batch["temperature_c"],
                    batch["pressure_bar"],
                    machine[5],
                    batch["shift"],
                    prev_by_machine[batch["machine_id"]],
                    maint,
                    label,
                ]
            )
            if label:
                prev_by_machine[batch["machine_id"]] += 1

        # Extra synthetic rows so the decision tree has a clearer academic signal.
        for extra in range(1, 181):
            m = MACHINES[extra % 10]
            p = PRODUCTS[extra % 10]
            hours = m[5] + extra
            temp = 60 + (extra % 40)
            pressure = 3 + (extra % 8)
            prev = extra % 15
            maint = "OVERDUE" if extra % 7 == 0 else "COMPLETED"
            shift = SHIFTS[extra % 3]
            # Synthetic rule used ONLY for the teaching dataset.
            score = 0
            score += 2 if hours > 4000 else 0
            score += 2 if prev >= 8 else 0
            score += 2 if maint == "OVERDUE" else 0
            score += 1 if temp >= 90 else 0
            score += 1 if pressure >= 8 else 0
            score += 1 if shift == "Night" else 0
            label = 1 if score >= 4 else 0
            writer.writerow(
                [
                    f"SYN{extra:03d}",
                    m[0],
                    p[0],
                    f"SYN-B{extra:03d}",
                    temp,
                    pressure,
                    hours,
                    shift,
                    prev,
                    maint,
                    label,
                ]
            )

    print(f"Wrote {out_sql}")
    print(f"Wrote {csv_path}")
    print(f"Products={len(PRODUCTS)} Machines={len(MACHINES)} Batches={len(batches)} "
          f"Units={len(units)} Defects={len(defects)}")


if __name__ == "__main__":
    main()
