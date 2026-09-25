"""
OOPJ domain classes for the production-tracking application.

Inheritance is used only where it is natural: Product, Machine, and Batch
share an identity (id + display name), so they extend ProductionEntity.
Defect and ProductionUnit are different concepts, so they are separate.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, Optional


class MDTPSError(Exception):
    """Base application error (shown as a friendly flash message)."""


class RecordNotFoundError(MDTPSError):
    pass


class ValidationError(MDTPSError):
    pass


class DuplicateRecordError(MDTPSError):
    pass


class ProductionEntity(ABC):
    """Abstract base: every tracked manufacturing object has an ID and name."""

    def __init__(self, entity_id: str, name: str) -> None:
        if not entity_id:
            raise ValidationError("Entity ID is required.")
        self._id = str(entity_id).strip()
        self._name = str(name).strip()

    @property
    def entity_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def summary(self) -> str:
        """Polymorphic one-line description used in reports."""

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self._id, "name": self._name}


class Product(ProductionEntity):
    def __init__(self, product_id: str, product_name: str, product_type: str, description: str = "") -> None:
        super().__init__(product_id, product_name)
        self.product_type = product_type
        self.description = description or ""

    @property
    def product_id(self) -> str:
        return self.entity_id

    def summary(self) -> str:
        return f"Product {self.product_id}: {self.name} ({self.product_type})"

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Product":
        return cls(row["product_id"], row["product_name"], row["product_type"], row.get("description") or "")


class Machine(ProductionEntity):
    def __init__(
        self,
        machine_id: str,
        machine_name: str,
        machine_type: str,
        location: str,
        status: str,
        operating_hours: int = 0,
    ) -> None:
        super().__init__(machine_id, machine_name)
        self.machine_type = machine_type
        self.location = location
        self.status = status
        self.operating_hours = int(operating_hours or 0)

    @property
    def machine_id(self) -> str:
        return self.entity_id

    def summary(self) -> str:
        return f"Machine {self.machine_id}: {self.name} [{self.status}]"

    def needs_maintenance(self) -> bool:
        return self.status in {"MAINTENANCE_REQUIRED", "UNDER_MAINTENANCE"}

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Machine":
        return cls(
            row["machine_id"],
            row["machine_name"],
            row["machine_type"],
            row["location"],
            row["status"],
            row.get("operating_hours") or 0,
        )


class Batch(ProductionEntity):
    def __init__(
        self,
        batch_id: str,
        product_id: str,
        machine_id: str,
        production_date: date,
        quantity: int,
        shift: str,
        temperature_c: float = 0,
        pressure_bar: float = 0,
    ) -> None:
        super().__init__(batch_id, batch_id)
        self.product_id = product_id
        self.machine_id = machine_id
        self.production_date = production_date
        self.quantity = int(quantity)
        self.shift = shift
        self.temperature_c = float(temperature_c or 0)
        self.pressure_bar = float(pressure_bar or 0)

    @property
    def batch_id(self) -> str:
        return self.entity_id

    def summary(self) -> str:
        return (
            f"Batch {self.batch_id} | product {self.product_id} | "
            f"machine {self.machine_id} | {self.production_date} | {self.shift}"
        )

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Batch":
        prod_date = row["production_date"]
        if isinstance(prod_date, str):
            prod_date = date.fromisoformat(prod_date[:10])
        return cls(
            row["batch_id"],
            row["product_id"],
            row["machine_id"],
            prod_date,
            row["quantity"],
            row["shift"],
            row.get("temperature_c") or 0,
            row.get("pressure_bar") or 0,
        )


class ProductionUnit:
    def __init__(
        self,
        unit_id: str,
        batch_id: str,
        serial_number: str,
        production_time: datetime,
        status: str,
    ) -> None:
        self._unit_id = unit_id
        self.batch_id = batch_id
        self.serial_number = serial_number
        self.production_time = production_time
        self.status = status

    @property
    def unit_id(self) -> str:
        return self._unit_id

    def is_defective(self) -> bool:
        return self.status == "DEFECTIVE"

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "ProductionUnit":
        ptime = row["production_time"]
        if isinstance(ptime, str):
            ptime = datetime.fromisoformat(ptime.replace(" ", "T"))
        return cls(row["unit_id"], row["batch_id"], row["serial_number"], ptime, row["status"])


class Defect:
    def __init__(
        self,
        defect_id: str,
        unit_id: str,
        defect_type: str,
        severity: str,
        description: str,
        detected_date: date,
    ) -> None:
        self._defect_id = defect_id
        self.unit_id = unit_id
        self.defect_type = defect_type
        self.severity = severity
        self.description = description or ""
        self.detected_date = detected_date

    @property
    def defect_id(self) -> str:
        return self._defect_id

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Defect":
        ddate = row["detected_date"]
        if isinstance(ddate, str):
            ddate = date.fromisoformat(ddate[:10])
        return cls(
            row["defect_id"],
            row["unit_id"],
            row["defect_type"],
            row["severity"],
            row.get("description") or "",
            ddate,
        )


class ProductionRecord:
    """Joined view used by traceability and the B-Tree index payload."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        out = dict(self.data)
        for key, value in list(out.items()):
            if isinstance(value, (date, datetime)):
                out[key] = value.isoformat(sep=" ")
        return out
