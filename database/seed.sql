-- =====================================================================
-- FranchiseOps AI — Demo / Seed Data
-- Run AFTER schema.sql:  psql -U postgres -d franchiseops -f seed.sql
-- Safe to re-run: every INSERT uses ON CONFLICT DO NOTHING or is guarded
-- by a NOT EXISTS check, so running this twice will not create duplicates.
--
-- NOTE on users: bcrypt password hashes are intentionally NOT hardcoded
-- here. After the backend is running, create demo accounts via:
--   POST /api/v1/auth/register
--   { "full_name": "Admin User", "email": "admin@franchiseops.ai",
--     "password": "Admin@12345", "role": "admin" }
-- This guarantees the hash matches whatever bcrypt version you installed.
-- =====================================================================

-- ---------------------------------------------------------------------
-- OUTLETS — 10 outlets across 4 regions, mixed store ages
-- ---------------------------------------------------------------------
INSERT INTO outlets (name, code, city, state, region, address, latitude, longitude, opened_on, status) VALUES
('Anna Nagar Flagship',   'CHN-001', 'Chennai',    'Tamil Nadu',    'South', 'Anna Nagar 2nd Ave',        13.0850, 80.2101, '2019-03-14', 'active'),
('Indiranagar Central',   'BLR-001', 'Bengaluru',  'Karnataka',     'South', '100 Feet Road',             12.9716, 77.6412, '2018-07-01', 'active'),
('Bandra West',           'MUM-001', 'Mumbai',     'Maharashtra',   'West',  'Linking Road',              19.0596, 72.8295, '2020-01-20', 'active'),
('Connaught Place',       'DEL-001', 'New Delhi',  'Delhi',         'North', 'CP Inner Circle',           28.6315, 77.2167, '2017-11-05', 'active'),
('Salt Lake Sector V',    'KOL-001', 'Kolkata',    'West Bengal',   'East',  'Sector V, Bidhannagar',     22.5726, 88.3639, '2021-05-11', 'active'),
('Madurai Junction',      'MDU-001', 'Madurai',    'Tamil Nadu',    'South', 'Station Road',              9.9252,  78.1198, '2022-02-18', 'active'),
('Hitech City',           'HYD-001', 'Hyderabad',  'Telangana',     'South', 'HITEC City Main Road',      17.4435, 78.3772, '2019-09-08', 'active'),
('Koregaon Park',         'PUN-001', 'Pune',       'Maharashtra',   'West',  'North Main Road',           18.5362, 73.8938, '2020-11-02', 'active'),
('Sector 17',             'CHD-001', 'Chandigarh', 'Punjab',        'North', 'Sector 17 Plaza',           30.7410, 76.7828, '2021-08-19', 'active'),
('Park Street',           'KOL-002', 'Kolkata',    'West Bengal',   'East',  'Park Street',               22.5535, 88.3526, '2023-01-15', 'active')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- SUPPLIERS
-- ---------------------------------------------------------------------
INSERT INTO suppliers (name, contact_person, phone, email, rating) VALUES
('Fresh Foods Distributors',   'Ramesh Kumar',   '9876543210', 'ramesh@freshfoods.example',   4.5),
('Metro Beverage Supply',      'Anita Rao',      '9876501234', 'anita@metrobev.example',      4.2),
('Golden Bakery Wholesale',    'Suresh Iyer',    '9845098450', 'suresh@goldenbakery.example', 4.6),
('Dairy Fresh Co.',            'Priya Menon',    '9900112233', 'priya@dairyfresh.example',    4.3),
('Snack Hub Distributors',     'Vikram Singh',   '9811223344', 'vikram@snackhub.example',     4.0),
('Frozen Valley Foods',        'Neha Sharma',    '9822334455', 'neha@frozenvalley.example',   3.9)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- PRODUCTS — 42 products across 8 categories
-- ---------------------------------------------------------------------
INSERT INTO products (sku, name, category, unit_price, cost_price, reorder_level, supplier_id) VALUES
-- Food (SKU 001-008)
('SKU-001', 'Paneer Tikka Wrap',        'Food',          180.00,  95.00, 30, 1),
('SKU-003', 'Veg Biryani Bowl',         'Food',          220.00, 110.00, 25, 1),
('SKU-004', 'Multigrain Salad',         'Food',          150.00,  80.00, 20, 1),
('SKU-006', 'Cheese Nachos',            'Food',          160.00,  70.00, 25, 1),
('SKU-007', 'Chicken Tikka Roll',       'Food',          210.00, 115.00, 30, 1),
('SKU-008', 'Falafel Bowl',             'Food',          195.00, 100.00, 20, 1),
('SKU-009', 'Masala Dosa',              'Food',          130.00,  60.00, 35, 1),
('SKU-010', 'Butter Chicken Combo',     'Food',          280.00, 150.00, 20, 1),
-- Beverage (SKU 011-018)
('SKU-002', 'Cold Coffee',              'Beverage',      120.00,  45.00, 40, 2),
('SKU-005', 'Herbal Iced Tea',          'Beverage',      110.00,  40.00, 20, 2),
('SKU-011', 'Fresh Lime Soda',          'Beverage',       80.00,  25.00, 45, 2),
('SKU-012', 'Mango Smoothie',           'Beverage',      140.00,  55.00, 30, 2),
('SKU-013', 'Masala Chai',              'Beverage',       50.00,  15.00, 60, 2),
('SKU-014', 'Filter Coffee',            'Beverage',       60.00,  18.00, 55, 2),
('SKU-015', 'Packaged Mineral Water',   'Beverage',       20.00,   8.00, 100, 2),
('SKU-016', 'Cola 500ml',               'Beverage',       45.00,  22.00, 80, 2),
-- Bakery (SKU 017-022)
('SKU-017', 'Chocolate Croissant',      'Bakery',         90.00,  35.00, 25, 3),
('SKU-018', 'Whole Wheat Bread Loaf',   'Bakery',         55.00,  22.00, 20, 3),
('SKU-019', 'Blueberry Muffin',         'Bakery',         85.00,  32.00, 20, 3),
('SKU-020', 'Butter Cookies Pack',      'Bakery',         70.00,  28.00, 30, 3),
('SKU-021', 'Red Velvet Slice',         'Bakery',         120.00,  48.00, 15, 3),
('SKU-022', 'Garlic Breadsticks',       'Bakery',          65.00,  25.00, 25, 3),
-- Dairy (SKU 023-028)
('SKU-023', 'Fresh Paneer 200g',        'Dairy',          80.00,  40.00, 25, 4),
('SKU-024', 'Greek Yogurt Cup',         'Dairy',          65.00,  28.00, 30, 4),
('SKU-025', 'Cheese Slices Pack',       'Dairy',          140.00,  65.00, 20, 4),
('SKU-026', 'Butter 100g',              'Dairy',           55.00,  25.00, 25, 4),
('SKU-027', 'Flavoured Milk 200ml',     'Dairy',           35.00,  15.00, 50, 4),
('SKU-028', 'Cottage Cheese Cubes',     'Dairy',           95.00,  45.00, 20, 4),
-- Snacks (SKU 029-034)
('SKU-029', 'Masala Peanuts Pack',      'Snacks',          45.00,  18.00, 40, 5),
('SKU-030', 'Potato Chips 100g',        'Snacks',          40.00,  16.00, 60, 5),
('SKU-031', 'Trail Mix Pouch',          'Snacks',          90.00,  38.00, 25, 5),
('SKU-032', 'Roasted Makhana',          'Snacks',          110.00,  48.00, 20, 5),
('SKU-033', 'Banana Chips',             'Snacks',           50.00,  20.00, 35, 5),
('SKU-034', 'Popcorn Tub',              'Snacks',           75.00,  28.00, 30, 5),
-- Frozen (SKU 035-039)
('SKU-035', 'Frozen Veg Momos (12pc)',  'Frozen',         180.00,  85.00, 20, 6),
('SKU-036', 'Frozen French Fries',      'Frozen',         120.00,  55.00, 25, 6),
('SKU-037', 'Frozen Paratha Pack',      'Frozen',         100.00,  45.00, 25, 6),
('SKU-038', 'Vanilla Ice Cream Tub',    'Frozen',         160.00,  70.00, 15, 6),
('SKU-039', 'Frozen Chicken Nuggets',   'Frozen',         190.00,  90.00, 20, 6),
-- Packaging / Personal Care (SKU 040-042)
('SKU-040', 'Takeaway Container Set',   'Packaging',       60.00,  30.00, 50, 5),
('SKU-041', 'Paper Napkins Pack',       'Packaging',       25.00,  10.00, 80, 5),
('SKU-042', 'Hand Sanitizer 100ml',     'Personal Care',   45.00,  18.00, 40, 5)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- INVENTORY (one row per outlet x product)
-- ---------------------------------------------------------------------
INSERT INTO inventory (outlet_id, product_id, quantity, warehouse_status, last_restocked)
SELECT o.id, p.id,
       (10 + (o.id * 7 + p.id * 3) % 90)                              AS quantity,
       CASE WHEN (o.id + p.id) % 9 = 0 THEN 'out_of_stock'
            WHEN (o.id + p.id) % 5 = 0 THEN 'low_stock'
            WHEN (o.id + p.id) % 7 = 0 THEN 'overstock'
            ELSE 'in_stock' END                                        AS warehouse_status,
       now() - ((o.id + p.id) || ' days')::interval                   AS last_restocked
FROM outlets o CROSS JOIN products p
ON CONFLICT DO NOTHING;

-- Fix quantity to be consistent with status for the extremes (0 for out_of_stock)
UPDATE inventory SET quantity = 0 WHERE warehouse_status = 'out_of_stock';

-- ---------------------------------------------------------------------
-- INVENTORY BATCHES — realistic expiry scenarios (expired, near-expiry, fresh)
-- ---------------------------------------------------------------------
INSERT INTO inventory_batches (inventory_id, batch_number, quantity, manufactured_on, expiry_date)
SELECT
    i.id,
    'BATCH-' || i.outlet_id || '-' || i.product_id || '-' || CASE
        WHEN i.id % 13 = 0 THEN 'X'   -- already expired
        WHEN i.id % 7  = 0 THEN 'N'   -- near expiry (within 10 days)
        ELSE 'F'                      -- fresh
    END,
    GREATEST(i.quantity, 5),
    CASE
        WHEN i.id % 13 = 0 THEN CURRENT_DATE - 120
        WHEN i.id % 7  = 0 THEN CURRENT_DATE - 80
        ELSE CURRENT_DATE - 20
    END,
    CASE
        WHEN i.id % 13 = 0 THEN CURRENT_DATE - 5     -- expired 5 days ago
        WHEN i.id % 7  = 0 THEN CURRENT_DATE + 6      -- expiring in 6 days
        ELSE CURRENT_DATE + 90                        -- comfortably fresh
    END
FROM inventory i
JOIN products p ON p.id = i.product_id
WHERE p.category IN ('Food', 'Dairy', 'Bakery', 'Frozen')  -- perishables only
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- EMPLOYEES + 30 DAYS OF ATTENDANCE
-- ---------------------------------------------------------------------
INSERT INTO employees (outlet_id, full_name, designation, date_joined, status)
SELECT o.id, 'Employee ' || o.id || '-' || gs,
       (ARRAY['Cashier','Chef','Manager','Server','Cleaner'])[1 + (gs % 5)],
       CURRENT_DATE - ((gs * 30) || ' days')::interval,
       'active'
FROM outlets o CROSS JOIN generate_series(1, 8) gs
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
-- MARKETING CAMPAIGNS — mixed high/average/low performers
-- ---------------------------------------------------------------------
INSERT INTO marketing_campaigns (outlet_id, name, channel, campaign_type, start_date, end_date, budget, ad_cost, revenue_generated, customer_reach, leads, conversions, coupon_code, coupon_redemptions, status)
VALUES
(1,    'Weekend Biryani Fest',        'social',   'promotional', CURRENT_DATE - 30, CURRENT_DATE - 16, 50000, 42000, 118000, 24000, 3200, 640,  'BIRYANI20', 640, 'completed'),
(2,    'Monsoon Coffee Combo',        'in-store', 'seasonal',    CURRENT_DATE - 20, CURRENT_DATE - 5,  30000, 27000,  71000, 15000, 2100, 410,  'MONSOON10', 410, 'completed'),
(NULL, 'App Launch Campaign',         'social',   'launch',      CURRENT_DATE - 10, CURRENT_DATE + 10, 80000, 35000,  96000, 52000, 4800, 980,  'APP2026',   980, 'active'),
(3,    'Mumbai Loyalty Rewards',      'email',    'loyalty',     CURRENT_DATE - 45, CURRENT_DATE - 15, 25000, 12000,  68000, 9000,  1500, 720,  'LOYAL15',   720, 'completed'),
(4,    'Delhi Winter Specials',       'print',    'seasonal',    CURRENT_DATE - 60, CURRENT_DATE - 30, 40000, 38000,  41000, 11000, 1800, 210,  'WINTER25',  210, 'completed'),
(5,    'Kolkata Festive Push',        'social',   'seasonal',    CURRENT_DATE - 25, CURRENT_DATE - 5,  35000, 30000,  95000, 18000, 2600, 590,  'FEST2026',  590, 'completed'),
(7,    'Hyderabad Launch Week',       'social',   'launch',      CURRENT_DATE - 90, CURRENT_DATE - 75, 60000, 45000,  52000, 20000, 2200, 180,  'HYDNEW',    180, 'completed'),
(8,    'Pune Student Discount',       'in-store', 'promotional', CURRENT_DATE - 14, CURRENT_DATE + 16, 15000,  9000,  38000, 6000,  900,  310,  'STUDENT10', 310, 'active'),
(9,    'Chandigarh Grand Opening',    'print',    'launch',      CURRENT_DATE - 200, CURRENT_DATE - 185, 70000, 55000, 61000, 25000, 3000, 220,  'CHDOPEN',   220, 'completed'),
(NULL, 'Network-wide Referral Push',  'email',    'loyalty',     CURRENT_DATE - 7,  CURRENT_DATE + 23, 20000,  8000,  29000, 7000,  1100, 260,  'REFER2026', 260, 'active'),
-- Second wave — covers the remaining outlets and adds repeat campaigns for the busiest ones
(6,    'Madurai Community Meetup',    'in-store', 'promotional', CURRENT_DATE - 18, CURRENT_DATE - 3,  12000,  7000,  21000, 4000,  650,  140,  'MDU10',     140, 'completed'),
(10,   'Kolkata Park Street Preview', 'social',   'launch',      CURRENT_DATE - 12, CURRENT_DATE + 18, 45000, 22000,  33000, 14000, 1900, 260,  'PARKPRE',   260, 'active'),
(1,    'Chennai Loyalty Round 2',     'email',    'loyalty',     CURRENT_DATE - 65, CURRENT_DATE - 35, 18000,  9000,  47000, 8500,  1300, 610,  'LOYAL2X',   610, 'completed'),
(2,    'Bengaluru Brunch Weekends',   'social',   'seasonal',    CURRENT_DATE - 50, CURRENT_DATE - 20, 28000, 24000,  55000, 13000, 1700, 380,  'BRUNCH15',  380, 'completed'),
(3,    'Mumbai Monsoon Combo 2.0',    'in-store', 'seasonal',    CURRENT_DATE - 8,  CURRENT_DATE + 22, 22000, 11000,  19000, 5000,  700,  95,   'MON2X',     95,  'active'),
(5,    'Kolkata New Year Push',       'print',    'seasonal',    CURRENT_DATE - 300, CURRENT_DATE - 285, 32000, 29000, 36000, 9000,  1200, 155,  'NY2025',    155, 'completed'),
(7,    'Hyderabad Anniversary Sale',  'social',   'promotional', CURRENT_DATE - 3,  CURRENT_DATE + 27, 26000, 10000,  14000, 6000,  800,  70,   'ANNIV5',    70,  'active'),
(NULL, 'National Loyalty Tier Launch','email',    'loyalty',     CURRENT_DATE - 120, CURRENT_DATE - 90, 55000, 20000,  88000, 30000, 3600, 890,  'TIERUP',    890, 'completed')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- AUDITS — mixed statuses, scores across the full workflow
-- ---------------------------------------------------------------------
INSERT INTO audits (outlet_id, scheduled_date, completed_date, status, compliance_score, risk_score, verification_score, approval_score, approval_stage, auditor_name) VALUES
(1,  CURRENT_DATE - 40,  CURRENT_DATE - 38, 'completed', 92.5, 12.0, 94.0, 90.0, 'approved',           'S. Narayanan'),
(2,  CURRENT_DATE - 35,  CURRENT_DATE - 33, 'completed', 88.0, 18.5, 90.0, 86.0, 'approved',           'S. Narayanan'),
(3,  CURRENT_DATE - 60,  NULL,              'pending',   NULL, NULL, NULL, NULL, 'auditor_review',     NULL),
(4,  CURRENT_DATE - 90,  CURRENT_DATE - 88, 'completed', 61.0, 45.0, 58.0, 55.0, 'manager_approval',   'P. Iyer'),
(5,  CURRENT_DATE - 20,  NULL,              'pending',   NULL, NULL, NULL, NULL, 'auditor_review',     NULL),
(6,  CURRENT_DATE - 100, CURRENT_DATE - 97, 'completed', 54.0, 58.0, 50.0, 48.0, 'changes_requested',  'P. Iyer'),
(7,  CURRENT_DATE - 55,  CURRENT_DATE - 52, 'completed', 79.0, 28.0, 80.0, 76.0, 'supervisor_review',  'R. Krishnan'),
(8,  CURRENT_DATE - 15,  NULL,              'pending',   NULL, NULL, NULL, NULL, 'auditor_review',     NULL),
(9,  CURRENT_DATE - 70,  CURRENT_DATE - 67, 'completed', 96.0, 6.0,  97.0, 95.0, 'approved',           'R. Krishnan'),
(10, CURRENT_DATE - 5,   NULL,              'pending',   NULL, NULL, NULL, NULL, 'auditor_review',     NULL),
-- Second, older audit per outlet — gives every outlet an audit history, not just one row
(1,  CURRENT_DATE - 220, CURRENT_DATE - 217, 'completed', 85.0, 20.0, 86.0, 82.0, 'approved',           'K. Ramesh'),
(2,  CURRENT_DATE - 210, CURRENT_DATE - 206, 'completed', 90.0, 14.0, 91.0, 88.0, 'approved',           'K. Ramesh'),
(3,  CURRENT_DATE - 240, CURRENT_DATE - 236, 'completed', 72.0, 32.0, 74.0, 70.0, 'approved',           'S. Narayanan'),
(4,  CURRENT_DATE - 250, CURRENT_DATE - 246, 'completed', 58.0, 48.0, 60.0, 55.0, 'approved',           'P. Iyer'),
(5,  CURRENT_DATE - 200, CURRENT_DATE - 196, 'completed', 81.0, 22.0, 83.0, 79.0, 'approved',           'R. Krishnan'),
(6,  CURRENT_DATE - 260, CURRENT_DATE - 256, 'completed', 49.0, 62.0, 52.0, 45.0, 'approved',           'P. Iyer'),
(7,  CURRENT_DATE - 230, CURRENT_DATE - 226, 'completed', 76.0, 30.0, 78.0, 74.0, 'approved',           'R. Krishnan'),
(8,  CURRENT_DATE - 190, CURRENT_DATE - 186, 'completed', 88.0, 16.0, 89.0, 85.0, 'approved',           'S. Narayanan'),
(9,  CURRENT_DATE - 270, CURRENT_DATE - 266, 'completed', 93.0, 9.0,  94.0, 91.0, 'approved',           'K. Ramesh'),
(10, CURRENT_DATE - 180, CURRENT_DATE - 176, 'completed', 68.0, 40.0, 70.0, 65.0, 'approved',           'P. Iyer')
ON CONFLICT DO NOTHING;

INSERT INTO audit_reports (audit_id, category, finding, severity, is_violation, resolved, responsible_person, due_date, resolution) VALUES
(4, 'hygiene',   'Storage temperature log missing for 3 days',              'medium',   TRUE, FALSE, 'Outlet Manager, Connaught Place', CURRENT_DATE + 7,  NULL),
(4, 'financial', 'Cash register reconciliation mismatch of ₹1,200',         'high',     TRUE, FALSE, 'Outlet Manager, Connaught Place', CURRENT_DATE + 3,  NULL),
(6, 'safety',    'Fire extinguisher inspection overdue',                    'critical', TRUE, FALSE, 'Outlet Manager, Madurai Junction', CURRENT_DATE - 2, NULL),
(6, 'inventory', 'Stock count variance exceeding 8% threshold',             'high',     TRUE, FALSE, 'Outlet Manager, Madurai Junction', CURRENT_DATE + 5,  NULL),
(7, 'hygiene',   'Minor: staff hygiene checklist not signed for one shift', 'low',      FALSE, TRUE,  'Shift Supervisor, Hitech City',    CURRENT_DATE - 10, 'Checklist retroactively signed and process corrected.'),
(1, 'financial', 'All financial records verified with no discrepancies',    'low',      FALSE, TRUE,  NULL, NULL, 'No action needed.')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- AUDIT EVIDENCE — mixed verification states + expiry scenarios
-- ---------------------------------------------------------------------
INSERT INTO audit_evidence (audit_id, evidence_type, description, submitted_date, verification_status, verification_score, expiry_date) VALUES
(1, 'checklist', 'Monthly hygiene checklist',              CURRENT_DATE - 39, 'verified', 95.0, NULL),
(1, 'document',  'FSSAI license copy',                     CURRENT_DATE - 39, 'verified', 92.0, CURRENT_DATE + 200),
(2, 'photo',     'Storage area photo evidence',            CURRENT_DATE - 34, 'verified', 90.0, NULL),
(4, 'receipt',   'Cash register daily reconciliation',     CURRENT_DATE - 89, 'rejected', 40.0, NULL),
(4, 'document',  'Fire safety certificate',                CURRENT_DATE - 89, 'pending',  NULL, CURRENT_DATE + 5),
(6, 'document',  'Fire extinguisher service record',       CURRENT_DATE - 98, 'rejected', 30.0, CURRENT_DATE - 15),
(6, 'checklist', 'Stock count sheet',                       CURRENT_DATE - 98, 'pending',  NULL, NULL),
(7, 'photo',     'Kitchen cleanliness photo',               CURRENT_DATE - 53, 'verified', 85.0, NULL),
(9, 'document',  'Trade license renewal',                   CURRENT_DATE - 68, 'verified', 98.0, CURRENT_DATE + 300),
(3, 'checklist', 'Pre-audit self-assessment',                CURRENT_DATE - 58, 'pending',  NULL, NULL)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- AUDIT APPROVALS — 4-stage workflow per audit (mirrors approval_stage above)
-- ---------------------------------------------------------------------
INSERT INTO audit_approvals (audit_id, stage, approver_name, status, decided_at, comments)
SELECT a.id, stage.name, NULL, 'pending', NULL, NULL
FROM audits a
CROSS JOIN (VALUES ('auditor_review'), ('supervisor_review'), ('manager_approval'), ('final_approval')) AS stage(name)
ON CONFLICT DO NOTHING;

-- Mark stages decided for audits that have progressed, matching each audit's approval_stage
UPDATE audit_approvals aa SET
    status = 'approved',
    approver_name = CASE aa.stage
        WHEN 'auditor_review' THEN 'S. Narayanan'
        WHEN 'supervisor_review' THEN 'K. Ramesh (Supervisor)'
        WHEN 'manager_approval' THEN 'A. Fernandes (Regional Manager)'
        WHEN 'final_approval' THEN 'V. Gupta (Admin)'
    END,
    decided_at = now() - (aa.audit_id || ' days')::interval,
    comments = 'Reviewed and approved.'
FROM audits a
WHERE aa.audit_id = a.id
  AND a.approval_stage = 'approved';

UPDATE audit_approvals aa SET
    status = 'changes_requested',
    approver_name = 'K. Ramesh (Supervisor)',
    decided_at = now() - INTERVAL '5 days',
    comments = 'Evidence rejected — resubmission required before proceeding.'
FROM audits a
WHERE aa.audit_id = a.id AND a.approval_stage = 'changes_requested' AND aa.stage = 'supervisor_review';

-- ---------------------------------------------------------------------
-- LEAVE REQUESTS — a few per outlet, mixed statuses
-- ---------------------------------------------------------------------
INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, reason, status, requested_at)
SELECT
    e.id,
    (ARRAY['casual', 'sick', 'earned'])[1 + (e.id % 3)],
    CURRENT_DATE + ((e.id % 10) || ' days')::interval,
    CURRENT_DATE + ((e.id % 10) + 1 || ' days')::interval,
    (ARRAY['Family function', 'Not feeling well', 'Personal work', 'Festival travel'])[1 + (e.id % 4)],
    (ARRAY['pending', 'approved', 'rejected'])[1 + (e.id % 3)],
    now() - ((e.id % 15) || ' days')::interval
FROM employees e
WHERE e.id % 4 = 0  -- roughly one in four employees has a leave request in the seed data
ON CONFLICT DO NOTHING;
