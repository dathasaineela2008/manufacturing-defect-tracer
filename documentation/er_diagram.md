# ER diagram — MDTPS

Academic conceptual model (DBMS Unit 1). All identifiers are fictional.

## Entity–relationship overview

```text
PRODUCT
   |
   | 1:M   manufactures
   ↓
BATCH
   |
   | M:1   produced_on
   ↓
MACHINE

BATCH
   |
   | 1:M   contains
   ↓
PRODUCTION_UNIT
   |
   | 1:0..M   has
   ↓
DEFECT

MACHINE
   |
   | 1:M   undergoes
   ↓
MAINTENANCE
```

## Entities and attributes

| Entity | Primary key | Attributes | Notes |
| --- | --- | --- | --- |
| PRODUCT | product_id | product_name (UNIQUE), product_type, description | Candidate key: product_name |
| MACHINE | machine_id | machine_name, machine_type, location, status, operating_hours | status constrained |
| BATCH | batch_id | product_id FK, machine_id FK, production_date, quantity, shift, temperature_c, pressure_bar | |
| PRODUCTION_UNIT | unit_id | batch_id FK, serial_number (UNIQUE), production_time, status | serial_number is a candidate key |
| DEFECT | defect_id | unit_id FK, defect_type, severity, description, detected_date | |
| MAINTENANCE | maintenance_id | machine_id FK, maintenance_date, maintenance_type, status, notes | |
| APP_USER | user_id | username UNIQUE, password_hash, full_name, role | login only |

## Cardinality

- One product appears in many batches; one batch belongs to one product.
- One machine produces many batches; one batch is made on one machine.
- One batch contains many units; one unit belongs to one batch.
- One unit may have zero or more defect records.
- One machine has many maintenance records.

## Relationships used for traceability

Unit ID → ProductionUnit → Batch → Product  
Unit ID → ProductionUnit → Batch → Machine  
Unit ID → Defect

That join path is the answer to: *which product, batch, and machine are associated with this defective unit?*
