"""
Relational algebra demonstration (DBMS Unit 2).

Each operation is executed on in-memory tables loaded from MySQL/SQLite,
so the page shows the algebra, the equivalent SQL, and real result rows.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Set


def selection(table: List[Dict[str, Any]], predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
    """σ — keep rows that satisfy the predicate."""
    return [row for row in table if predicate(row)]


def projection(table: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
    """π — keep listed columns and drop duplicate resulting tuples."""
    seen: Set[tuple] = set()
    out: List[Dict[str, Any]] = []
    for row in table:
        tuple_row = tuple(row.get(col) for col in columns)
        if tuple_row in seen:
            continue
        seen.add(tuple_row)
        out.append({col: row.get(col) for col in columns})
    return out


def cartesian(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """× — every pairing of tuples."""
    out = []
    for a in left:
        for b in right:
            merged = dict(a)
            for key, value in b.items():
                merged[key if key not in merged else f"right_{key}"] = value
            out.append(merged)
    return out


def inner_join(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    left_key: str,
    right_key: str,
) -> List[Dict[str, Any]]:
    """⋈ — join on equality of two attributes."""
    out = []
    for a in left:
        for b in right:
            if a.get(left_key) == b.get(right_key):
                merged = dict(a)
                for key, value in b.items():
                    if key not in merged:
                        merged[key] = value
                out.append(merged)
    return out


def union(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """∪ — set union of tuples."""
    seen: Set[tuple] = set()
    out: List[Dict[str, Any]] = []
    for row in left + right:
        marker = tuple(sorted((str(k), str(v)) for k, v in row.items()))
        if marker in seen:
            continue
        seen.add(marker)
        out.append(row)
    return out


def intersection(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """∩ — tuples that appear in both."""
    right_set = {tuple(sorted((str(k), str(v)) for k, v in row.items())) for row in right}
    out = []
    seen: Set[tuple] = set()
    for row in left:
        marker = tuple(sorted((str(k), str(v)) for k, v in row.items()))
        if marker in right_set and marker not in seen:
            seen.add(marker)
            out.append(row)
    return out


def difference(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """− — tuples in left but not in right."""
    right_set = {tuple(sorted((str(k), str(v)) for k, v in row.items())) for row in right}
    out = []
    for row in left:
        marker = tuple(sorted((str(k), str(v)) for k, v in row.items()))
        if marker not in right_set:
            out.append(row)
    return out


def stringify_rows(rows: List[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
    clipped = []
    for row in rows[:limit]:
        clipped.append({k: ("" if v is None else str(v)) for k, v in row.items()})
    return clipped
