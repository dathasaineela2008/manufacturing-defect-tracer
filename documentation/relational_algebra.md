# Relational algebra — MDTPS (DBMS Unit 2)

The page `/relational` runs these operations on tables loaded from the database. Python helpers live in `app/relational.py`.

| Operation | Symbol | Meaning in this project |
| --- | --- | --- |
| Selection | σ | Keep defective units or high-severity defects |
| Projection | π | Keep unit_id only |
| Join | ⋈ | Connect unit, batch, and machine |
| Union | ∪ | Combine OK and DEFECTIVE identifier sets |
| Intersection | ∩ | Identifiers that are both OK and DEFECTIVE (empty in a consistent DB) |
| Difference | − | OK identifiers minus DEFECTIVE identifiers |
| Cartesian product | × | Shown on a 2×2 sample because a full product of 200×30 rows is not useful |

## Traceability expressions

Find defective units:

```text
σ status = 'DEFECTIVE'(ProductionUnit)
```

```sql
SELECT * FROM production_unit WHERE status = 'DEFECTIVE';
```

Find high-severity defects:

```text
σ severity = 'HIGH'(Defect)
```

```sql
SELECT * FROM defect WHERE severity = 'HIGH';
```

Trace unit to batch:

```text
ProductionUnit ⋈ Batch
```

```sql
SELECT * FROM production_unit u JOIN batch b ON u.batch_id = b.batch_id;
```

Trace unit to machine:

```text
ProductionUnit ⋈ Batch ⋈ Machine
```

```sql
SELECT u.unit_id, b.batch_id, m.machine_id, m.machine_name
FROM production_unit u
JOIN batch b ON u.batch_id = b.batch_id
JOIN machine m ON b.machine_id = m.machine_id;
```

Defects produced on a particular machine (example M03):

```text
σ machine_id = 'M03' (ProductionUnit ⋈ Batch ⋈ Machine) ⋈ Defect
```

Defective products in a date range:

```text
σ production_date ≥ d1 ∧ production_date ≤ d2 ∧ status = 'DEFECTIVE'
  (ProductionUnit ⋈ Batch ⋈ Product)
```
