-- Manufacturing Defect Traceability and Prediction System (MDTPS)
-- MySQL schema: 3NF relational design with PKs, FKs, and constraints.

CREATE DATABASE IF NOT EXISTS mdtps
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE mdtps;

-- Drop in child-to-parent order so foreign keys do not block recreation.
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS defect;
DROP TABLE IF EXISTS production_unit;
DROP TABLE IF EXISTS machine_maintenance;
DROP TABLE IF EXISTS batch;
DROP TABLE IF EXISTS machine;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS app_user;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------------
-- Users (login). Passwords are stored as Werkzeug hashes, never plain text.
-- ---------------------------------------------------------------------------
CREATE TABLE app_user (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(50)  NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    full_name      VARCHAR(100) NOT NULL,
    role           VARCHAR(30)  NOT NULL DEFAULT 'ADMIN',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- Product
-- ---------------------------------------------------------------------------
CREATE TABLE product (
    product_id    VARCHAR(20)  NOT NULL,
    product_name  VARCHAR(100) NOT NULL,
    product_type  VARCHAR(80)  NOT NULL,
    description   VARCHAR(255) NULL,
    PRIMARY KEY (product_id),
    UNIQUE KEY uq_product_name (product_name)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- Machine
-- ---------------------------------------------------------------------------
CREATE TABLE machine (
    machine_id    VARCHAR(20)  NOT NULL,
    machine_name  VARCHAR(100) NOT NULL,
    machine_type  VARCHAR(80)  NOT NULL,
    location      VARCHAR(80)  NOT NULL,
    status        VARCHAR(40)  NOT NULL,
    operating_hours INT        NOT NULL DEFAULT 0,
    PRIMARY KEY (machine_id),
    CONSTRAINT chk_machine_status
        CHECK (status IN ('OPERATIONAL', 'MAINTENANCE_REQUIRED', 'UNDER_MAINTENANCE', 'IDLE'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- Batch  (Product 1:M Batch, Machine 1:M Batch)
-- ---------------------------------------------------------------------------
CREATE TABLE batch (
    batch_id         VARCHAR(20) NOT NULL,
    product_id       VARCHAR(20) NOT NULL,
    machine_id       VARCHAR(20) NOT NULL,
    production_date  DATE        NOT NULL,
    quantity         INT         NOT NULL,
    shift            VARCHAR(20) NOT NULL,
    temperature_c    DECIMAL(6,2) NOT NULL,
    pressure_bar     DECIMAL(6,2) NOT NULL,
    PRIMARY KEY (batch_id),
    CONSTRAINT fk_batch_product
        FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_batch_machine
        FOREIGN KEY (machine_id) REFERENCES machine(machine_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_batch_qty CHECK (quantity > 0),
    CONSTRAINT chk_batch_shift CHECK (shift IN ('Morning', 'Afternoon', 'Night'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- Production unit  (Batch 1:M ProductionUnit)
-- serial_number is a candidate key (UNIQUE).
-- ---------------------------------------------------------------------------
CREATE TABLE production_unit (
    unit_id          VARCHAR(20) NOT NULL,
    batch_id         VARCHAR(20) NOT NULL,
    serial_number    VARCHAR(40) NOT NULL,
    production_time  DATETIME    NOT NULL,
    status           VARCHAR(20) NOT NULL,
    PRIMARY KEY (unit_id),
    UNIQUE KEY uq_serial_number (serial_number),
    CONSTRAINT fk_unit_batch
        FOREIGN KEY (batch_id) REFERENCES batch(batch_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_unit_status CHECK (status IN ('OK', 'DEFECTIVE', 'QUARANTINE'))
) ENGINE=InnoDB;

CREATE INDEX idx_unit_batch ON production_unit(batch_id);
CREATE INDEX idx_unit_status ON production_unit(status);

-- ---------------------------------------------------------------------------
-- Defect  (ProductionUnit 1:0..M Defect)
-- ---------------------------------------------------------------------------
CREATE TABLE defect (
    defect_id      VARCHAR(20)  NOT NULL,
    unit_id        VARCHAR(20)  NOT NULL,
    defect_type    VARCHAR(80)  NOT NULL,
    severity       VARCHAR(20)  NOT NULL,
    description    VARCHAR(255) NULL,
    detected_date  DATE         NOT NULL,
    PRIMARY KEY (defect_id),
    CONSTRAINT fk_defect_unit
        FOREIGN KEY (unit_id) REFERENCES production_unit(unit_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_defect_severity CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
) ENGINE=InnoDB;

CREATE INDEX idx_defect_unit ON defect(unit_id);
CREATE INDEX idx_defect_severity ON defect(severity);
CREATE INDEX idx_defect_type ON defect(defect_type);

-- ---------------------------------------------------------------------------
-- Machine maintenance  (Machine 1:M Maintenance)
-- ---------------------------------------------------------------------------
CREATE TABLE machine_maintenance (
    maintenance_id    VARCHAR(20)  NOT NULL,
    machine_id        VARCHAR(20)  NOT NULL,
    maintenance_date  DATE         NOT NULL,
    maintenance_type  VARCHAR(80)  NOT NULL,
    status            VARCHAR(30)  NOT NULL,
    notes             VARCHAR(255) NULL,
    PRIMARY KEY (maintenance_id),
    CONSTRAINT fk_maint_machine
        FOREIGN KEY (machine_id) REFERENCES machine(machine_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_maint_status CHECK (status IN ('COMPLETED', 'OVERDUE', 'SCHEDULED'))
) ENGINE=InnoDB;
