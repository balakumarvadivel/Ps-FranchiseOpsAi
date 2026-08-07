-- =====================================================================
-- FranchiseOps AI — PostgreSQL Schema
-- Run: psql -U postgres -d franchiseops -f schema.sql
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------
-- ROLES, PERMISSIONS & USERS (Authentication)
-- ---------------------------------------------------------------------
CREATE TABLE roles (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) UNIQUE NOT NULL,        -- admin | regional_manager | outlet_manager
    description     TEXT
);

CREATE TABLE permissions (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(80) UNIQUE NOT NULL,         -- e.g. 'outlets.write', 'reports.generate'
    description     TEXT
);

CREATE TABLE role_permissions (
    role_id         INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- ---------------------------------------------------------------------
-- REGIONS
-- ---------------------------------------------------------------------
CREATE TABLE regions (
    name            VARCHAR(50) PRIMARY KEY,             -- e.g. 'South' — kept as the PK so outlets.region
                                                            -- can reference it without a breaking column-type change
    description     TEXT
);

CREATE TABLE outlets (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    code            VARCHAR(20) UNIQUE NOT NULL,
    city            VARCHAR(100) NOT NULL,
    state           VARCHAR(100) NOT NULL,
    region          VARCHAR(50) NOT NULL REFERENCES regions(name),
    address         TEXT,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    opened_on       DATE,
    status          VARCHAR(20) DEFAULT 'active',         -- active | inactive | closed
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_outlets_region ON outlets(region);
CREATE INDEX idx_outlets_status ON outlets(status);

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role_id         INTEGER NOT NULL REFERENCES roles(id),
    outlet_id       INTEGER REFERENCES outlets(id),       -- NULL for admin / regional manager
    is_active       BOOLEAN DEFAULT TRUE,
    reset_token     VARCHAR(255),
    reset_token_expires TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);

-- ---------------------------------------------------------------------
-- PRODUCTS, SUPPLIERS, INVENTORY
-- ---------------------------------------------------------------------
CREATE TABLE suppliers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    contact_person  VARCHAR(100),
    phone           VARCHAR(20),
    email           VARCHAR(150),
    address         TEXT,
    rating          NUMERIC(2,1) DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE products (
    id              SERIAL PRIMARY KEY,
    sku             VARCHAR(50) UNIQUE NOT NULL,
    name            VARCHAR(150) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    cost_price      NUMERIC(12,2) NOT NULL,
    reorder_level   INTEGER DEFAULT 20,
    supplier_id     INTEGER REFERENCES suppliers(id),
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_products_category ON products(category);

CREATE TABLE inventory (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity        INTEGER NOT NULL DEFAULT 0,
    warehouse_status VARCHAR(20) DEFAULT 'in_stock',       -- in_stock | low_stock | out_of_stock | overstock
    last_restocked  TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (outlet_id, product_id)
);
CREATE INDEX idx_inventory_outlet ON inventory(outlet_id);
CREATE INDEX idx_inventory_status ON inventory(warehouse_status);

CREATE TABLE inventory_batches (
    id              SERIAL PRIMARY KEY,
    inventory_id    INTEGER NOT NULL REFERENCES inventory(id) ON DELETE CASCADE,
    batch_number    VARCHAR(50) NOT NULL,
    quantity        INTEGER NOT NULL,
    manufactured_on DATE,
    expiry_date     DATE,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_batches_expiry ON inventory_batches(expiry_date);

-- ---------------------------------------------------------------------
-- SALES
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(150),
    phone           VARCHAR(20),
    email           VARCHAR(150),
    outlet_id       INTEGER REFERENCES outlets(id),
    first_visit     DATE,
    last_visit      DATE,
    total_spent     NUMERIC(14,2) DEFAULT 0,
    visit_count     INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_customers_outlet ON customers(outlet_id);

CREATE TABLE sales (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    customer_id     INTEGER REFERENCES customers(id),
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    total_amount    NUMERIC(14,2) NOT NULL,
    discount        NUMERIC(12,2) DEFAULT 0,
    sale_date       TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_sales_outlet_date ON sales(outlet_id, sale_date);
CREATE INDEX idx_sales_product ON sales(product_id);

-- ---------------------------------------------------------------------
-- EMPLOYEES / STAFF
-- ---------------------------------------------------------------------
CREATE TABLE employees (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    user_id         INTEGER REFERENCES users(id),
    full_name       VARCHAR(150) NOT NULL,
    designation     VARCHAR(100),
    date_joined     DATE,
    status          VARCHAR(20) DEFAULT 'active',          -- active | on_leave | resigned
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_employees_outlet ON employees(outlet_id);

CREATE TABLE shifts (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    shift_date      DATE NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    status          VARCHAR(20) DEFAULT 'scheduled'         -- scheduled | completed | missed
);
CREATE INDEX idx_shifts_employee_date ON shifts(employee_id, shift_date);

CREATE TABLE attendance (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    check_in        TIMESTAMPTZ,
    check_out       TIMESTAMPTZ,
    status          VARCHAR(20) DEFAULT 'present',           -- present | absent | half_day | leave
    UNIQUE (employee_id, date)
);
CREATE INDEX idx_attendance_employee ON attendance(employee_id);

CREATE TABLE payroll (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    month           DATE NOT NULL,                          -- first day of the month
    base_salary     NUMERIC(12,2) NOT NULL,
    overtime_pay    NUMERIC(12,2) DEFAULT 0,
    deductions      NUMERIC(12,2) DEFAULT 0,
    net_pay         NUMERIC(12,2) NOT NULL,
    paid_on         DATE,
    UNIQUE (employee_id, month)
);

CREATE TABLE leave_requests (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type      VARCHAR(30) NOT NULL DEFAULT 'casual',   -- casual | sick | earned | unpaid
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    reason          TEXT,
    status          VARCHAR(20) DEFAULT 'pending',            -- pending | approved | rejected
    requested_at    TIMESTAMPTZ DEFAULT now(),
    decided_at      TIMESTAMPTZ,
    decided_by      INTEGER REFERENCES users(id)
);
CREATE INDEX idx_leave_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_status ON leave_requests(status);

-- ---------------------------------------------------------------------
-- MARKETING
-- ---------------------------------------------------------------------
CREATE TABLE marketing_campaigns (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER REFERENCES outlets(id),         -- NULL = network-wide campaign
    name            VARCHAR(150) NOT NULL,
    channel         VARCHAR(50),                            -- social | print | in-store | email
    start_date      DATE NOT NULL,
    end_date        DATE,
    budget          NUMERIC(12,2) NOT NULL,
    ad_cost         NUMERIC(12,2) DEFAULT 0,
    revenue_generated NUMERIC(14,2) DEFAULT 0,
    customer_reach  INTEGER DEFAULT 0,
    coupon_code     VARCHAR(30),
    coupon_redemptions INTEGER DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'active',            -- active | completed | paused
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_campaigns_outlet ON marketing_campaigns(outlet_id);

-- ---------------------------------------------------------------------
-- AUDIT
-- ---------------------------------------------------------------------
CREATE TABLE audits (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    scheduled_date  DATE NOT NULL,
    completed_date  DATE,
    status          VARCHAR(20) DEFAULT 'pending',           -- pending | completed | overdue
    compliance_score NUMERIC(5,2),
    risk_score      NUMERIC(5,2),
    auditor_name    VARCHAR(150),
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_audits_outlet ON audits(outlet_id);
CREATE INDEX idx_audits_status ON audits(status);

CREATE TABLE audit_reports (
    id              SERIAL PRIMARY KEY,
    audit_id        INTEGER NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
    category        VARCHAR(100),                           -- hygiene | financial | safety | inventory
    finding         TEXT NOT NULL,
    severity        VARCHAR(20) DEFAULT 'low',               -- low | medium | high | critical
    is_violation    BOOLEAN DEFAULT FALSE,
    resolved        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------
-- AI, ALERTS, NOTIFICATIONS, RECOMMENDATIONS
-- ---------------------------------------------------------------------
CREATE TABLE ai_insights (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER REFERENCES outlets(id),          -- NULL = network-wide insight
    category        VARCHAR(50) NOT NULL,                    -- sales | inventory | staff | marketing | audit | intelligence
    title           VARCHAR(255) NOT NULL,
    summary         TEXT NOT NULL,
    confidence      NUMERIC(5,2),                             -- 0-100
    generated_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_ai_insights_outlet ON ai_insights(outlet_id);

CREATE TABLE recommendations (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER REFERENCES outlets(id),
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    priority        VARCHAR(20) NOT NULL,                    -- critical | high | medium | low
    category        VARCHAR(50),                             -- inventory | marketing | staff | audit | finance
    status          VARCHAR(20) DEFAULT 'open',               -- open | in_progress | resolved | dismissed
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);

CREATE TABLE alerts (
    id              SERIAL PRIMARY KEY,
    outlet_id       INTEGER REFERENCES outlets(id),
    type            VARCHAR(50) NOT NULL,                    -- low_stock | expiring | poor_performance | staff_shortage | audit_due | cost_spike
    message         TEXT NOT NULL,
    severity        VARCHAR(20) DEFAULT 'medium',             -- critical | high | medium | low
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_alerts_outlet ON alerts(outlet_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);

CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    message         TEXT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_notifications_user ON notifications(user_id);

CREATE TABLE reports (
    id              SERIAL PRIMARY KEY,
    generated_by    INTEGER REFERENCES users(id),
    report_type     VARCHAR(50) NOT NULL,                    -- sales | inventory | staff | marketing | audit | overall
    format          VARCHAR(10) NOT NULL,                    -- pdf | excel | csv
    file_path       TEXT,
    date_from       DATE,
    date_to         DATE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE settings (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    theme           VARCHAR(10) DEFAULT 'light',              -- light | dark
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_alerts    BOOLEAN DEFAULT TRUE,
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------
-- SEED ROLES, REGIONS & PERMISSIONS
-- ---------------------------------------------------------------------
INSERT INTO roles (name, description) VALUES
    ('admin', 'Full system access across all outlets'),
    ('regional_manager', 'Access to all outlets within an assigned region'),
    ('outlet_manager', 'Access limited to a single assigned outlet')
ON CONFLICT DO NOTHING;

INSERT INTO regions (name, description) VALUES
    ('North', 'Northern region outlets'),
    ('South', 'Southern region outlets'),
    ('East', 'Eastern region outlets'),
    ('West', 'Western region outlets')
ON CONFLICT DO NOTHING;

INSERT INTO permissions (code, description) VALUES
    ('outlets.read', 'View outlet data'),
    ('outlets.write', 'Create/edit/delete outlets'),
    ('users.manage', 'Manage user accounts and roles'),
    ('reports.generate', 'Generate and download reports'),
    ('recommendations.refresh', 'Trigger a full recommendation engine refresh'),
    ('audits.manage', 'Schedule audits and record findings'),
    ('data.import', 'Upload and commit validated data')
ON CONFLICT DO NOTHING;

-- admin: everything
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permissions p WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- regional_manager: everything except user management
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permissions p
WHERE r.name = 'regional_manager' AND p.code != 'users.manage'
ON CONFLICT DO NOTHING;

-- outlet_manager: read-only + data import
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permissions p
WHERE r.name = 'outlet_manager' AND p.code IN ('outlets.read', 'data.import')
ON CONFLICT DO NOTHING;
