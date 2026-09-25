"""
Traceability engine: Unit -> Product, Batch, Machine, Date, Shift, Defect.

This is the core answer to the problem statement:
"Which product, batch, and machine are associated with this defective unit?"
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.database import db
from app.models import RecordNotFoundError, ValidationError


class TraceabilityService:
    def _ph(self) -> str:
        return db.placeholder

    def find_unit(self, unit_or_serial: str) -> Dict[str, Any]:
        token = (unit_or_serial or "").strip()
        if not token:
            raise ValidationError("Enter a Unit ID or serial number.")
        ph = self._ph()
        sql = f"""
            SELECT
                u.unit_id,
                u.serial_number,
                u.status AS unit_status,
                u.production_time,
                b.batch_id,
                b.production_date,
                b.quantity,
                b.shift,
                b.temperature_c,
                b.pressure_bar,
                p.product_id,
                p.product_name,
                p.product_type,
                m.machine_id,
                m.machine_name,
                m.machine_type,
                m.location,
                m.status AS machine_status,
                m.operating_hours
            FROM production_unit u
            JOIN batch b ON u.batch_id = b.batch_id
            JOIN product p ON b.product_id = p.product_id
            JOIN machine m ON b.machine_id = m.machine_id
            WHERE u.unit_id = {ph} OR u.serial_number = {ph}
        """
        row = db.query_one(sql, (token, token))
        if not row:
            raise RecordNotFoundError(
                f"No production unit found for '{token}'. Check the Unit ID or serial number."
            )
        return row

    def defects_for_unit(self, unit_id: str) -> List[Dict[str, Any]]:
        ph = self._ph()
        return db.query(
            f"""
            SELECT defect_id, unit_id, defect_type, severity, description, detected_date
            FROM defect
            WHERE unit_id = {ph}
            ORDER BY detected_date DESC, defect_id
            """,
            (unit_id,),
        )

    def last_maintenance(self, machine_id: str) -> Optional[Dict[str, Any]]:
        ph = self._ph()
        return db.query_one(
            f"""
            SELECT maintenance_id, machine_id, maintenance_date, maintenance_type, status, notes
            FROM machine_maintenance
            WHERE machine_id = {ph}
            ORDER BY maintenance_date DESC
            LIMIT 1
            """,
            (machine_id,),
        )

    def trace(self, unit_or_serial: str) -> Dict[str, Any]:
        unit = self.find_unit(unit_or_serial)
        defects = self.defects_for_unit(unit["unit_id"])
        maint = self.last_maintenance(unit["machine_id"])
        primary = defects[0] if defects else None

        possible_source = f"Machine {unit['machine_id']} / Batch {unit['batch_id']}"
        note = (
            "This is recorded association from the database join path "
            "Unit → Batch → Machine. Association is not the same as proven causation."
        )
        return {
            "unit": unit,
            "defects": defects,
            "primary_defect": primary,
            "last_maintenance": maint,
            "possible_source": possible_source,
            "causation_note": note,
            "chain": [
                unit["unit_id"],
                unit["product_name"],
                unit["batch_id"],
                unit["machine_id"],
                str(unit["production_date"]),
                unit["shift"],
                primary["defect_type"] if primary else "None recorded",
                primary["severity"] if primary else "N/A",
            ],
        }

    def dashboard_stats(self) -> Dict[str, Any]:
        products = db.query_one("SELECT COUNT(*) AS n FROM product")["n"]
        batches = db.query_one("SELECT COUNT(*) AS n FROM batch")["n"]
        machines = db.query_one("SELECT COUNT(*) AS n FROM machine")["n"]
        units = db.query_one("SELECT COUNT(*) AS n FROM production_unit")["n"]
        defective = db.query_one(
            "SELECT COUNT(*) AS n FROM production_unit WHERE status = 'DEFECTIVE'"
        )["n"]
        rate = round((defective / units) * 100, 2) if units else 0.0
        return {
            "total_products": products,
            "total_batches": batches,
            "total_machines": machines,
            "total_units": units,
            "total_defective": defective,
            "defect_rate": rate,
        }

    def chart_defects_by_machine(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT m.machine_id, m.machine_name, COUNT(d.defect_id) AS defect_count
            FROM machine m
            LEFT JOIN batch b ON b.machine_id = m.machine_id
            LEFT JOIN production_unit u ON u.batch_id = b.batch_id
            LEFT JOIN defect d ON d.unit_id = u.unit_id
            GROUP BY m.machine_id, m.machine_name
            ORDER BY m.machine_id
            """
        )

    def chart_defects_by_batch(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT b.batch_id, COUNT(d.defect_id) AS defect_count
            FROM batch b
            LEFT JOIN production_unit u ON u.batch_id = b.batch_id
            LEFT JOIN defect d ON d.unit_id = u.unit_id
            GROUP BY b.batch_id
            ORDER BY b.batch_id
            """
        )

    def chart_defects_by_product(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT p.product_id, p.product_name, COUNT(d.defect_id) AS defect_count
            FROM product p
            LEFT JOIN batch b ON b.product_id = p.product_id
            LEFT JOIN production_unit u ON u.batch_id = b.batch_id
            LEFT JOIN defect d ON d.unit_id = u.unit_id
            GROUP BY p.product_id, p.product_name
            ORDER BY p.product_id
            """
        )

    def chart_defects_by_type(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT defect_type, COUNT(*) AS defect_count
            FROM defect
            GROUP BY defect_type
            ORDER BY defect_count DESC
            """
        )

    def chart_defects_by_severity(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT severity, COUNT(*) AS defect_count
            FROM defect
            GROUP BY severity
            ORDER BY FIELD(severity, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW')
            """
            if db.engine == "mysql"
            else """
            SELECT severity, COUNT(*) AS defect_count
            FROM defect
            GROUP BY severity
            ORDER BY CASE severity
                WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3 ELSE 4 END
            """
        )

    def chart_defects_over_time(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT detected_date AS defect_date, COUNT(*) AS defect_count
            FROM defect
            GROUP BY detected_date
            ORDER BY detected_date
            """
        )

    def machine_analysis(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT
                m.machine_id,
                m.machine_name,
                m.status,
                COUNT(u.unit_id) AS total_units,
                SUM(CASE WHEN u.status = 'DEFECTIVE' THEN 1 ELSE 0 END) AS defective_units,
                (
                    SELECT MAX(mm.maintenance_date)
                    FROM machine_maintenance mm
                    WHERE mm.machine_id = m.machine_id
                ) AS last_maintenance
            FROM machine m
            LEFT JOIN batch b ON b.machine_id = m.machine_id
            LEFT JOIN production_unit u ON u.batch_id = b.batch_id
            GROUP BY m.machine_id, m.machine_name, m.status
            ORDER BY defective_units DESC, m.machine_id
            """
        )

    def batch_analysis(self) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT
                b.batch_id,
                p.product_name,
                m.machine_id,
                m.machine_name,
                b.production_date,
                b.quantity,
                b.shift,
                COUNT(u.unit_id) AS total_units,
                SUM(CASE WHEN u.status = 'DEFECTIVE' THEN 1 ELSE 0 END) AS defective_units
            FROM batch b
            JOIN product p ON p.product_id = b.product_id
            JOIN machine m ON m.machine_id = b.machine_id
            LEFT JOIN production_unit u ON u.batch_id = b.batch_id
            GROUP BY b.batch_id, p.product_name, m.machine_id, m.machine_name,
                     b.production_date, b.quantity, b.shift
            ORDER BY b.production_date, b.batch_id
            """
        )


traceability = TraceabilityService()
