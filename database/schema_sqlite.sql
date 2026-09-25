-- SQLite schema for local testing when MySQL is not installed.
-- The college DBMS demonstration still targets MySQL (database/schema.sql).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS app_user (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    full_name      TEXT NOT NULL,
    role           TEXT NOT NULL DEFAULT 'ADMIN',
    created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product (
    product_id    TEXT PRIMARY KEY,
    product_name  TEXT NOT NULL UNIQUE,
    product_type  TEXT NOT NULL,
    description   TEXT
);

CREATE TABLE IF NOT EXISTS machine (
    machine_id      TEXT PRIMARY KEY,
    machine_name    TEXT NOT NULL,
    machine_type    TEXT NOT NULL,
    location        TEXT NOT NULL,
    status          TEXT NOT NULL,
    operating_hours INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS batch (
    batch_id        TEXT PRIMARY KEY,
    product_id      TEXT NOT NULL,
    machine_id      TEXT NOT NULL,
    production_date TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    shift           TEXT NOT NULL,
    temperature_c   REAL NOT NULL,
    pressure_bar    REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (machine_id) REFERENCES machine(machine_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS production_unit (
    unit_id         TEXT PRIMARY KEY,
    batch_id        TEXT NOT NULL,
    serial_number   TEXT NOT NULL UNIQUE,
    production_time TEXT NOT NULL,
    status          TEXT NOT NULL,
    FOREIGN KEY (batch_id) REFERENCES batch(batch_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS defect (
    defect_id     TEXT PRIMARY KEY,
    unit_id       TEXT NOT NULL,
    defect_type   TEXT NOT NULL,
    severity      TEXT NOT NULL,
    description   TEXT,
    detected_date TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES production_unit(unit_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS machine_maintenance (
    maintenance_id   TEXT PRIMARY KEY,
    machine_id       TEXT NOT NULL,
    maintenance_date TEXT NOT NULL,
    maintenance_type TEXT NOT NULL,
    status           TEXT NOT NULL,
    notes            TEXT,
    FOREIGN KEY (machine_id) REFERENCES machine(machine_id) ON UPDATE CASCADE ON DELETE RESTRICT
);
