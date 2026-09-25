"""
In-memory B-Tree index of Unit ID -> production record.

This is the academic ADSA component. MySQL already indexes tables internally;
this tree is rebuilt from the database so students can search and visualise it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from algorithms.btree import BTree
from app.database import db


class BTreeIndex:
    def __init__(self, t: int = 3) -> None:
        self.t = t
        self.tree = BTree(t=t)

    def rebuild(self) -> int:
        self.tree = BTree(t=self.t)
        rows = db.query(
            """
            SELECT
                u.unit_id,
                u.serial_number,
                u.status,
                u.batch_id,
                b.machine_id,
                p.product_name
            FROM production_unit u
            JOIN batch b ON u.batch_id = b.batch_id
            JOIN product p ON b.product_id = p.product_id
            ORDER BY u.unit_id
            """
        )
        for row in rows:
            payload = {
                "unit_id": row["unit_id"],
                "serial_number": row["serial_number"],
                "status": row["status"],
                "batch_id": row["batch_id"],
                "machine_id": row["machine_id"],
                "product_name": row["product_name"],
            }
            self.tree.insert(row["unit_id"], payload)
        return self.tree.size

    def search(self, unit_id: str) -> Optional[Dict[str, Any]]:
        return self.tree.get((unit_id or "").strip())

    def insert(self, unit_id: str, payload: Optional[Dict[str, Any]] = None) -> None:
        self.tree.insert((unit_id or "").strip(), payload or {"unit_id": unit_id})

    def traverse(self) -> List[str]:
        return [key for key, _ in self.tree.inorder()]

    def display(self) -> str:
        return self.tree.display_text()

    def structure(self) -> dict:
        return self.tree.to_dict()


btree_index = BTreeIndex(t=3)
