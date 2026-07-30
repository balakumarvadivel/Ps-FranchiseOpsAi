-- =====================================================================
-- FranchiseOps AI — Demo / Seed Data
-- Run AFTER schema.sql:  psql -U postgres -d franchiseops -f seed.sql
--
-- NOTE on users: bcrypt password hashes are intentionally NOT hardcoded
-- here. After the backend is running, create demo accounts via:
--   POST /api/v1/auth/register
--   { "full_name": "Admin User", "email": "admin@franchiseops.ai",
--     "password": "Admin@12345", "role": "admin" }
-- This guarantees the hash matches whatever bcrypt version you installed.
-- =====================================================================

-- ---------------------------------------------------------------------
-- OUTLETS
-- ---------------------------------------------------------------------
INSERT INTO outlets (name, code, city, state, region, address, latitude, longitude, opened_on, status) VALUES
('Anna Nagar Flagship',   'CHN-001', 'Chennai',    'Tamil Nadu',    'South', 'Anna Nagar 2nd Ave',        13.0850, 80.2101, '2019-03-14', 'active'),
('Indiranagar Central',   'BLR-001', 'Bengaluru',  'Karnataka',     'South', '100 Feet Road',             12.9716, 77.6412, '2018-07-01', 'active'),
('Bandra West',           'MUM-001', 'Mumbai',     'Maharashtra',   'West',  'Linking Road',              19.0596, 72.8295, '2020-01-20', 'active'),
('Connaught Place',       'DEL-001', 'New Delhi',  'Delhi',         'North', 'CP Inner Circle',           28.6315, 77.2167, '2017-11-05', 'active'),
('Salt Lake Sector V',    'KOL-001', 'Kolkata',    'West Bengal',   'East',  'Sector V, Bidhannagar',     22.5726, 88.3639, '2021-05-11', 'active'),
('Madurai Junction',      'MDU-001', 'Madurai',    'Tamil Nadu',    'South', 'Station Road',              9.9252,  78.1198, '2022-02-18', 'active')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- SUPPLIERS & PRODUCTS
-- ---------------------------------------------------------------------
INSERT INTO suppliers (name, contact_person, phone, email, rating) VALUES
('Fresh Foods Distributors', 'Ramesh Kumar', '9876543210', 'ramesh@freshfoods.example', 4.5),
('Metro Beverage Supply',    'Anita Rao',    '9876501234', 'anita@metrobev.example',   4.2)
ON CONFLICT DO NOTHING;

INSERT INTO products (sku, name, category, unit_price, cost_price, reorder_level, supplier_id) VALUES
('SKU-001', 'Paneer Tikka Wrap',   'Food',     180.00, 95.00,  30, 1),
('SKU-002', 'Cold Coffee',         'Beverage', 120.00, 45.00,  40, 2),
('SKU-003', 'Veg Biryani Bowl',    'Food',     220.00, 110.00, 25, 1),
('SKU-004', 'Multigrain Salad',    'Food',     150.00, 80.00,  20, 1),
('SKU-005', 'Herbal Iced Tea',     'Beverage', 110.00, 40.00,  20, 2),
('SKU-006', 'Cheese Nachos',       'Food',     160.00, 70.00,  25, 1)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- INVENTORY (one row per outlet x product)
-- ---------------------------------------------------------------------
INSERT INTO inventory (outlet_id, product_id, quantity, warehouse_status, last_restocked)
SELECT o.id, p.id,
       (20 + (o.id * 7 + p.id * 3) % 80)                              AS quantity,
       CASE WHEN (o.id + p.id) % 5 = 0 THEN 'low_stock'
            WHEN (o.id + p.id) % 7 = 0 THEN 'overstock'
            WHEN (o.id + p.id) % 11 = 0 THEN 'out_of_stock'
            ELSE 'in_stock' END                                        AS warehouse_status,
       now() - ((o.id + p.id) || ' days')::interval                   AS last_restocked
FROM outlets o CROSS JOIN products p
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- EMPLOYEES + 30 DAYS OF ATTENDANCE
-- ---------------------------------------------------------------------
INSERT INTO employees (outlet_id, full_name, designation, date_joined, status)
SELECT o.id, 'Employee ' || o.id || '-' || gs, 
       (ARRAY['Cashier','Chef','Manager','Server','Cleaner'])[1 + (gs % 5)],
       CURRENT_DATE - ((gs * 30) || ' days')::interval,
       'active'
FROM outlets o CROSS JOIN generate_series(1, 5) gs
ON CONFLICT DO NOTHING;

INSERT INTO attendance (employee_id, date, status)
SELECT e.id, d::date,
       CASE WHEN random() < 0.9 THEN 'present' ELSE 'absent' END
FROM employees e
CROSS JOIN generate_series(CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '1 day', INTERVAL '1 day') d
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- SALES — 90 days of synthetic transactions per outlet
-- ---------------------------------------------------------------------
INSERT INTO sales (outlet_id, product_id, quantity, unit_price, total_amount, discount, sale_date)
SELECT
    o.id,
    p.id,
    qty,
    p.unit_price,
    (p.unit_price * qty) - discount,
    discount,
    sale_ts
FROM outlets o
CROSS JOIN products p
CROSS JOIN LATERAL (
    SELECT
        generate_series(1, 3) AS n,  -- ~3 transactions per product per outlet per day
        now() - (gs || ' days')::interval
            + (random() * interval '20 hours') AS sale_ts,
        (1 + floor(random() * 5))::int AS qty,
        round((random() * 15)::numeric, 2) AS discount
    FROM generate_series(0, 89) gs
) t(n, sale_ts, qty, discount)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- MARKETING CAMPAIGNS
-- ---------------------------------------------------------------------
INSERT INTO marketing_campaigns (outlet_id, name, channel, start_date, end_date, budget, ad_cost, revenue_generated, customer_reach, coupon_code, coupon_redemptions, status)
VALUES
(1, 'Weekend Biryani Fest',      'social',   CURRENT_DATE - 30, CURRENT_DATE - 16, 50000, 42000, 118000, 24000, 'BIRYANI20', 640, 'completed'),
(2, 'Monsoon Coffee Combo',      'in-store', CURRENT_DATE - 20, CURRENT_DATE - 5,  30000, 27000, 71000,  15000, 'MONSOON10', 410, 'completed'),
(NULL, 'App Launch Campaign',    'social',   CURRENT_DATE - 10, CURRENT_DATE + 10, 80000, 35000, 96000,  52000, 'APP2026',   980, 'active')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- AUDITS
-- ---------------------------------------------------------------------
INSERT INTO audits (outlet_id, scheduled_date, completed_date, status, compliance_score, risk_score, auditor_name) VALUES
(1, CURRENT_DATE - 40, CURRENT_DATE - 38, 'completed', 92.5, 12.0, 'S. Narayanan'),
(2, CURRENT_DATE - 35, CURRENT_DATE - 33, 'completed', 88.0, 18.5, 'S. Narayanan'),
(3, CURRENT_DATE - 60, NULL,              'pending',   NULL, NULL, NULL),
(4, CURRENT_DATE - 90, CURRENT_DATE - 88, 'completed', 61.0, 45.0, 'P. Iyer'),
(5, CURRENT_DATE - 20, NULL,              'pending',   NULL, NULL, NULL),
(6, CURRENT_DATE - 100, CURRENT_DATE - 97, 'completed', 54.0, 58.0, 'P. Iyer')
ON CONFLICT DO NOTHING;

INSERT INTO audit_reports (audit_id, category, finding, severity, is_violation, resolved) VALUES
(4, 'hygiene',   'Storage temperature log missing for 3 days', 'medium', TRUE, FALSE),
(4, 'financial', 'Cash register reconciliation mismatch of ₹1,200', 'high', TRUE, FALSE),
(6, 'safety',    'Fire extinguisher inspection overdue', 'critical', TRUE, FALSE)
ON CONFLICT DO NOTHING;
