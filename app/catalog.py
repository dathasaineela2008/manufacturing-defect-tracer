"""
CRUD helpers for catalog pages. All SQL is parameterized.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from app.database import db
from app.models import DuplicateRecordError, RecordNotFoundError, ValidationError


def _ph() -> str:
    return db.placeholder


def require(value: str, label: str) -> str:
    text = (value or "").strip()
    if not text:
        raise ValidationError(f"{label} is required.")
    return text


def list_products(search: str = "") -> List[Dict[str, Any]]:
    if search:
        like = f"%{search.strip()}%"
        return db.query(
            f"SELECT * FROM product WHERE product_id LIKE {_ph()} OR product_name LIKE {_ph()} OR product_type LIKE {_ph()} ORDER BY product_id",
            (like, like, like),
        )
    return db.query("SELECT * FROM product ORDER BY product_id")


def create_product(product_id: str, name: str, ptype: str, description: str) -> None:
    product_id = require(product_id, "Product ID")
    name = require(name, "Product name")
    ptype = require(ptype, "Product type")
    try:
        db.execute(
            f"INSERT INTO product (product_id, product_name, product_type, description) VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()})",
            (product_id, name, ptype, description.strip()),
        )
    except Exception as exc:
        raise DuplicateRecordError("That product ID or name already exists.") from exc


def list_machines(search: str = "") -> List[Dict[str, Any]]:
    if search:
        like = f"%{search.strip()}%"
        return db.query(
            f"SELECT * FROM machine WHERE machine_id LIKE {_ph()} OR machine_name LIKE {_ph()} OR location LIKE {_ph()} ORDER BY machine_id",
            (like, like, like),
        )
    return db.query("SELECT * FROM machine ORDER BY machine_id")


def create_machine(mid: str, name: str, mtype: str, location: str, status: str, hours: str) -> None:
    mid = require(mid, "Machine ID")
    name = require(name, "Machine name")
    allowed = {"OPERATIONAL", "MAINTENANCE_REQUIRED", "UNDER_MAINTENANCE", "IDLE"}
    status = require(status, "Status")
    if status not in allowed:
        raise ValidationError("Invalid machine status.")
    try:
        hours_i = int(hours or 0)
    except ValueError as exc:
        raise ValidationError("Operating hours must be a whole number.") from exc
    try:
        db.execute(
            f"INSERT INTO machine (machine_id, machine_name, machine_type, location, status, operating_hours) "
            f"VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()})",
            (mid, name, require(mtype, "Machine type"), require(location, "Location"), status, hours_i),
        )
    except Exception as exc:
        raise DuplicateRecordError("That machine ID already exists.") from exc


def list_batches(search: str = "", date_from: str = "", date_to: str = "") -> List[Dict[str, Any]]:
    sql = """
        SELECT b.*, p.product_name, m.machine_name
        FROM batch b
        JOIN product p ON p.product_id = b.product_id
        JOIN machine m ON m.machine_id = b.machine_id
        WHERE 1=1
    """
    params: List[Any] = []
    if search:
        like = f"%{search.strip()}%"
        sql += f" AND (b.batch_id LIKE {_ph()} OR p.product_name LIKE {_ph()} OR m.machine_id LIKE {_ph()})"
        params.extend([like, like, like])
    if date_from:
        sql += f" AND b.production_date >= {_ph()}"
        params.append(date_from)
    if date_to:
        sql += f" AND b.production_date <= {_ph()}"
        params.append(date_to)
    sql += " ORDER BY b.production_date, b.batch_id"
    return db.query(sql, params)


def create_batch(batch_id: str, product_id: str, machine_id: str, prod_date: str, qty: str, shift: str, temp: str, pressure: str) -> None:
    batch_id = require(batch_id, "Batch ID")
    if shift not in {"Morning", "Afternoon", "Night"}:
        raise ValidationError("Shift must be Morning, Afternoon, or Night.")
    try:
        qty_i = int(qty)
        if qty_i <= 0:
            raise ValueError
        temp_f = float(temp or 0)
        pres_f = float(pressure or 0)
    except ValueError as exc:
        raise ValidationError("Quantity must be a positive integer. Temperature and pressure must be numbers.") from exc
    try:
        db.execute(
            f"INSERT INTO batch (batch_id, product_id, machine_id, production_date, quantity, shift, temperature_c, pressure_bar) "
            f"VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()})",
            (batch_id, require(product_id, "Product"), require(machine_id, "Machine"), require(prod_date, "Date"), qty_i, shift, temp_f, pres_f),
        )
    except Exception as exc:
        raise DuplicateRecordError("Could not create batch. Check IDs and uniqueness.") from exc


def list_units(search: str = "", status: str = "") -> List[Dict[str, Any]]:
    sql = """
        SELECT u.*, b.product_id, p.product_name, b.machine_id, m.machine_name, b.production_date, b.shift
        FROM production_unit u
        JOIN batch b ON b.batch_id = u.batch_id
        JOIN product p ON p.product_id = b.product_id
        JOIN machine m ON m.machine_id = b.machine_id
        WHERE 1=1
    """
    params: List[Any] = []
    if search:
        like = f"%{search.strip()}%"
        sql += f" AND (u.unit_id LIKE {_ph()} OR u.serial_number LIKE {_ph()} OR u.batch_id LIKE {_ph()})"
        params.extend([like, like, like])
    if status:
        sql += f" AND u.status = {_ph()}"
        params.append(status)
    sql += " ORDER BY u.unit_id"
    return db.query(sql, params)


def create_unit(unit_id: str, batch_id: str, serial: str, ptime: str, status: str) -> None:
    if status not in {"OK", "DEFECTIVE", "QUARANTINE"}:
        raise ValidationError("Invalid unit status.")
    try:
        db.execute(
            f"INSERT INTO production_unit (unit_id, batch_id, serial_number, production_time, status) "
            f"VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()})",
            (
                require(unit_id, "Unit ID"),
                require(batch_id, "Batch ID"),
                require(serial, "Serial number"),
                require(ptime, "Production time").replace("T", " "),
                status,
            ),
        )
    except Exception as exc:
        raise DuplicateRecordError("Could not create unit. Unit ID and serial number must be unique, and the batch must exist.") from exc


def list_defects(search: str = "", severity: str = "") -> List[Dict[str, Any]]:
    sql = """
        SELECT d.*, u.serial_number, u.batch_id, u.status AS unit_status
        FROM defect d
        JOIN production_unit u ON u.unit_id = d.unit_id
        WHERE 1=1
    """
    params: List[Any] = []
    if search:
        like = f"%{search.strip()}%"
        sql += f" AND (d.defect_id LIKE {_ph()} OR d.unit_id LIKE {_ph()} OR d.defect_type LIKE {_ph()})"
        params.extend([like, like, like])
    if severity:
        sql += f" AND d.severity = {_ph()}"
        params.append(severity)
    sql += " ORDER BY d.detected_date DESC, d.defect_id"
    return db.query(sql, params)


def create_defect(defect_id: str, unit_id: str, dtype: str, severity: str, description: str, detected: str) -> None:
    if severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise ValidationError("Invalid severity.")
    unit = db.query_one(f"SELECT unit_id FROM production_unit WHERE unit_id = {_ph()}", (require(unit_id, "Unit ID"),))
    if not unit:
        raise RecordNotFoundError("That Unit ID does not exist.")
    try:
        db.execute(
            f"INSERT INTO defect (defect_id, unit_id, defect_type, severity, description, detected_date) "
            f"VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()})",
            (require(defect_id, "Defect ID"), unit_id.strip(), require(dtype, "Defect type"), severity, description.strip(), require(detected, "Detected date")),
        )
        db.execute(f"UPDATE production_unit SET status = 'DEFECTIVE' WHERE unit_id = {_ph()}", (unit_id.strip(),))
    except Exception as exc:
        raise DuplicateRecordError("Could not create defect. Defect ID must be unique.") from exc


def get_user(username: str) -> Optional[Dict[str, Any]]:
    return db.query_one(f"SELECT * FROM app_user WHERE username = {_ph()}", (username.strip(),))
