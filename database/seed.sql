-- =====================================================================
-- FranchiseOps AI — Expanded Demo / Seed Data (25 Outlets Across India)
-- Run AFTER schema.sql:  psql -U postgres -d franchiseops -f seed.sql
-- Or via python runner:  python seed.py --reset
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. OUTLETS — 25 outlets across 4 regions in India
-- ---------------------------------------------------------------------
INSERT INTO outlets (name, code, city, state, region, address, latitude, longitude, opened_on, status) VALUES
-- South Region (8 outlets)
('Anna Nagar Flagship',   'CHN-001', 'Chennai',    'Tamil Nadu',    'South', 'Anna Nagar 2nd Ave',        13.0850, 80.2101, '2019-03-14', 'active'),
('T. Nagar Central',      'CHN-002', 'Chennai',    'Tamil Nadu',    'South', 'Pondy Bazaar, T. Nagar',    13.0418, 80.2341, '2021-06-10', 'active'),
('Indiranagar Central',   'BLR-001', 'Bengaluru',  'Karnataka',     'South', '100 Feet Road',             12.9716, 77.6412, '2018-07-01', 'active'),
('Koramangala Hub',       'BLR-002', 'Bengaluru',  'Karnataka',     'South', '80 Feet Road, 4th Block',   12.9352, 77.6245, '2020-09-15', 'active'),
('Hitech City',           'HYD-001', 'Hyderabad',  'Telangana',     'South', 'HITEC City Main Road',      17.4435, 78.3772, '2019-09-08', 'active'),
('Gachibowli Financial',  'HYD-002', 'Hyderabad',  'Telangana',     'South', 'Financial District',        17.4126, 78.3498, '2022-01-20', 'active'),
('Madurai Junction',      'MDU-001', 'Madurai',    'Tamil Nadu',    'South', 'Station Road',              9.9252,  78.1198, '2022-02-18', 'active'),
('MG Road Commercial',    'COK-001', 'Kochi',      'Kerala',        'South', 'MG Road, Ernakulam',        9.9723,  76.2784, '2021-11-05', 'active'),

-- West Region (6 outlets)
('Bandra West',           'MUM-001', 'Mumbai',     'Maharashtra',   'West',  'Linking Road',              19.0596, 72.8295, '2020-01-20', 'active'),
('Lower Parel High Street','MUM-002','Mumbai',     'Maharashtra',   'West',  'Senapati Bapat Marg',       19.0012, 72.8256, '2021-08-14', 'active'),
('Koregaon Park',         'PUN-001', 'Pune',       'Maharashtra',   'West',  'North Main Road',           18.5362, 73.8938, '2020-11-02', 'active'),
('Viman Nagar',           'PUN-002', 'Pune',       'Maharashtra',   'West',  'Viman Nagar Datta Mandir',  18.5679, 73.9143, '2022-04-12', 'active'),
('CG Road Commercial',    'AMD-001', 'Ahmedabad',  'Gujarat',       'West',  'CG Road, Navrangpura',      23.0331, 72.5623, '2021-03-25', 'active'),
('Ring Road Hub',         'SUR-001', 'Surat',      'Gujarat',       'West',  'Ring Road, Majura Gate',    21.1702, 72.8311, '2022-07-19', 'active'),

-- North Region (7 outlets)
('Connaught Place',       'DEL-001', 'New Delhi',  'Delhi',         'North', 'CP Inner Circle',           28.6315, 77.2167, '2017-11-05', 'active'),
('Saket District Centre', 'DEL-002', 'New Delhi',  'Delhi',         'North', 'Press Enclave Road',        28.5284, 77.2189, '2020-05-18', 'active'),
('Cyber Hub',             'GUG-001', 'Gurgaon',    'Haryana',       'North', 'DLF Cyber City',            28.4950, 77.0895, '2019-12-01', 'active'),
('Sector 18 Market',      'NOI-001', 'Noida',      'Uttar Pradesh', 'North', 'Sector 18, Noida',          28.5708, 77.3261, '2021-09-30', 'active'),
('Sector 17 Plaza',       'CHD-001', 'Chandigarh', 'Punjab',        'North', 'Sector 17 Plaza',           30.7410, 76.7828, '2021-08-19', 'active'),
('MI Road Heritage',      'JAI-001', 'Jaipur',     'Rajasthan',     'North', 'MI Road, Panch Batti',      26.9154, 75.8115, '2022-03-10', 'active'),
('Hazratganj Promenade',  'LKO-001', 'Lucknow',    'Uttar Pradesh', 'North', 'Hazratganj Main Road',      26.8467, 80.9462, '2022-10-05', 'active'),

-- East Region (4 outlets)
('Salt Lake Sector V',    'KOL-001', 'Kolkata',    'West Bengal',   'East',  'Sector V, Bidhannagar',     22.5726, 88.3639, '2021-05-11', 'active'),
('Park Street',           'KOL-002', 'Kolkata',    'West Bengal',   'East',  'Park Street',               22.5535, 88.3526, '2023-01-15', 'active'),
('Saheed Nagar',          'BBI-001', 'Bhubaneswar','Odisha',        'East',  'Janpath, Saheed Nagar',     20.2961, 85.8245, '2022-06-20', 'active'),
('GS Road Hub',           'GAU-001', 'Guwahati',   'Assam',         'East',  'GS Road, Christian Basti',  26.1445, 91.7362, '2022-11-12', 'active')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 2. SUPPLIERS
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
-- 3. PRODUCTS — 50 products across 8 categories
-- ---------------------------------------------------------------------
INSERT INTO products (sku, name, category, unit_price, cost_price, reorder_level, supplier_id) VALUES
-- Food
('SKU-001', 'Paneer Tikka Wrap',        'Food',          180.00,  95.00, 30, 1),
('SKU-003', 'Veg Biryani Bowl',         'Food',          220.00, 110.00, 25, 1),
('SKU-004', 'Multigrain Salad',         'Food',          150.00,  80.00, 20, 1),
('SKU-006', 'Cheese Nachos',            'Food',          160.00,  70.00, 25, 1),
('SKU-007', 'Chicken Tikka Roll',       'Food',          210.00, 115.00, 30, 1),
('SKU-008', 'Falafel Bowl',             'Food',          195.00, 100.00, 20, 1),
('SKU-009', 'Masala Dosa',              'Food',          130.00,  60.00, 35, 1),
('SKU-010', 'Butter Chicken Combo',     'Food',          280.00, 150.00, 20, 1),
('SKU-043', 'Chole Bhature Combo',      'Food',          190.00,  95.00, 25, 1),
('SKU-044', 'Grilled Club Sandwich',    'Food',          170.00,  85.00, 30, 1),
-- Beverage
('SKU-002', 'Cold Coffee',              'Beverage',      120.00,  45.00, 40, 2),
('SKU-005', 'Herbal Iced Tea',          'Beverage',      110.00,  40.00, 20, 2),
('SKU-011', 'Fresh Lime Soda',          'Beverage',       80.00,  25.00, 45, 2),
('SKU-012', 'Mango Smoothie',           'Beverage',      140.00,  55.00, 30, 2),
('SKU-013', 'Masala Chai',              'Beverage',       50.00,  15.00, 60, 2),
('SKU-014', 'Filter Coffee',            'Beverage',       60.00,  18.00, 55, 2),
('SKU-015', 'Packaged Mineral Water',   'Beverage',       20.00,   8.00, 100, 2),
('SKU-016', 'Cola 500ml',               'Beverage',       45.00,  22.00, 80, 2),
('SKU-045', 'Matcha Green Latte',       'Beverage',      160.00,  65.00, 20, 2),
('SKU-046', 'Rose Lassi 300ml',         'Beverage',       95.00,  35.00, 35, 2),
-- Bakery
('SKU-017', 'Chocolate Croissant',      'Bakery',         90.00,  35.00, 25, 3),
('SKU-018', 'Whole Wheat Bread Loaf',   'Bakery',         55.00,  22.00, 20, 3),
('SKU-019', 'Blueberry Muffin',         'Bakery',         85.00,  32.00, 20, 3),
('SKU-020', 'Butter Cookies Pack',      'Bakery',         70.00,  28.00, 30, 3),
('SKU-021', 'Red Velvet Slice',         'Bakery',        120.00,  48.00, 15, 3),
('SKU-022', 'Garlic Breadsticks',       'Bakery',         65.00,  25.00, 25, 3),
('SKU-047', 'Almond Tart',              'Bakery',        110.00,  45.00, 15, 3),
-- Dairy
('SKU-023', 'Fresh Paneer 200g',        'Dairy',          80.00,  40.00, 25, 4),
('SKU-024', 'Greek Yogurt Cup',         'Dairy',          65.00,  28.00, 30, 4),
('SKU-025', 'Cheese Slices Pack',       'Dairy',         140.00,  65.00, 20, 4),
('SKU-026', 'Butter 100g',              'Dairy',          55.00,  25.00, 25, 4),
('SKU-027', 'Flavoured Milk 200ml',     'Dairy',          35.00,  15.00, 50, 4),
('SKU-028', 'Cottage Cheese Cubes',     'Dairy',          95.00,  45.00, 20, 4),
('SKU-048', 'Organic Cow Milk 1L',      'Dairy',          75.00,  45.00, 40, 4),
-- Snacks
('SKU-029', 'Masala Peanuts Pack',      'Snacks',         45.00,  18.00, 40, 5),
('SKU-030', 'Potato Chips 100g',        'Snacks',         40.00,  16.00, 60, 5),
('SKU-031', 'Trail Mix Pouch',          'Snacks',         90.00,  38.00, 25, 5),
('SKU-032', 'Roasted Makhana',          'Snacks',        110.00,  48.00, 20, 5),
('SKU-033', 'Banana Chips',             'Snacks',         50.00,  20.00, 35, 5),
('SKU-034', 'Popcorn Tub',              'Snacks',         75.00,  28.00, 30, 5),
('SKU-049', 'Samosa Chat Pack',         'Snacks',         65.00,  25.00, 35, 5),
-- Frozen
('SKU-035', 'Frozen Veg Momos (12pc)',  'Frozen',        180.00,  85.00, 20, 6),
('SKU-036', 'Frozen French Fries',      'Frozen',        120.00,  55.00, 25, 6),
('SKU-037', 'Frozen Paratha Pack',      'Frozen',        100.00,  45.00, 25, 6),
('SKU-038', 'Vanilla Ice Cream Tub',    'Frozen',        160.00,  70.00, 15, 6),
('SKU-039', 'Frozen Chicken Nuggets',   'Frozen',        190.00,  90.00, 20, 6),
('SKU-050', 'Frozen Corn Patties',      'Frozen',        130.00,  60.00, 20, 6),
-- Packaging & Personal Care
('SKU-040', 'Takeaway Container Set',   'Packaging',      60.00,  30.00, 50, 5),
('SKU-041', 'Paper Napkins Pack',       'Packaging',      25.00,  10.00, 80, 5),
('SKU-042', 'Hand Sanitizer 100ml',     'Personal Care',  45.00,  18.00, 40, 5)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 4. INVENTORY (25 Outlets x 50 Products = 1,250 Rows)
-- ---------------------------------------------------------------------
INSERT INTO inventory (outlet_id, product_id, quantity, warehouse_status, last_restocked)
SELECT o.id, p.id,
       (15 + (o.id * 11 + p.id * 7) % 120)                             AS quantity,
       CASE WHEN (o.id + p.id) % 11 = 0 THEN 'out_of_stock'
            WHEN (o.id + p.id) % 6  = 0 THEN 'low_stock'
            WHEN (o.id + p.id) % 9  = 0 THEN 'overstock'
            ELSE 'in_stock' END                                        AS warehouse_status,
       now() - ((o.id + p.id) || ' days')::interval                    AS last_restocked
FROM outlets o CROSS JOIN products p
ON CONFLICT DO NOTHING;

UPDATE inventory SET quantity = 0 WHERE warehouse_status = 'out_of_stock';

-- ---------------------------------------------------------------------
-- 5. INVENTORY BATCHES (Batches with expired, near-expiry, and fresh dates)
-- ---------------------------------------------------------------------
INSERT INTO inventory_batches (inventory_id, batch_number, quantity, manufactured_on, expiry_date)
SELECT
    i.id,
    'BATCH-' || i.outlet_id || '-' || i.product_id || '-' || CASE
        WHEN i.id % 13 = 0 THEN 'X'
        WHEN i.id % 7  = 0 THEN 'N'
        ELSE 'F'
    END,
    GREATEST(i.quantity, 5),
    CASE
        WHEN i.id % 13 = 0 THEN CURRENT_DATE - 120
        WHEN i.id % 7  = 0 THEN CURRENT_DATE - 80
        ELSE CURRENT_DATE - 20
    END,
    CASE
        WHEN i.id % 13 = 0 THEN CURRENT_DATE - 5
        WHEN i.id % 7  = 0 THEN CURRENT_DATE + 6
        ELSE CURRENT_DATE + 90
    END
FROM inventory i
JOIN products p ON p.id = i.product_id
WHERE p.category IN ('Food', 'Dairy', 'Bakery', 'Frozen')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 6. EMPLOYEES (8 Employees per Outlet x 25 Outlets = 200 Employees)
-- ---------------------------------------------------------------------
INSERT INTO employees (outlet_id, full_name, designation, date_joined, status)
SELECT o.id,
       (ARRAY['Aarav','Ananya','Rohan','Priya','Karthik','Deepika','Vikram','Sneha','Rahul','Divya'])[1 + (gs % 10)] || ' ' ||
       (ARRAY['Sharma','Iyer','Verma','Nair','Patel','Mukherjee','Gupta','Reddy','Singh','Rao'])[1 + ((o.id + gs) % 10)],
       (ARRAY['Outlet Manager','Shift Supervisor','Head Chef','Assistant Chef','Cashier','Server','Delivery Executive','Cleaner'])[1 + ((gs - 1) % 8)],
       CURRENT_DATE - ((gs * 45 + o.id * 15) || ' days')::interval,
       'active'
FROM outlets o CROSS JOIN generate_series(1, 8) gs
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 7. ATTENDANCE (30 Days of Shift Attendance)
-- ---------------------------------------------------------------------
INSERT INTO attendance (employee_id, date, status)
SELECT e.id, d::date,
       CASE WHEN (e.id + extract(day from d)::int) % 17 = 0 THEN 'absent'
            WHEN (e.id + extract(day from d)::int) % 23 = 0 THEN 'leave'
            ELSE 'present' END
FROM employees e
CROSS JOIN generate_series(CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '1 day', INTERVAL '1 day') d
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 8. SALES (180 Days of History Across 25 Outlets x 50 Products)
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
        generate_series(1, 2) AS n,
        now() - (gs || ' days')::interval + (random() * interval '18 hours') AS sale_ts,
        (1 + floor(random() * 4))::int AS qty,
        round((random() * 12)::numeric, 2) AS discount
    FROM generate_series(0, 179) gs
    WHERE (o.id + p.id + gs) % 3 = 0
) t(n, sale_ts, qty, discount)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 9. MARKETING CAMPAIGN DATA (35 Campaigns across regions & channels)
-- ---------------------------------------------------------------------
INSERT INTO marketing_campaigns (outlet_id, name, channel, campaign_type, start_date, end_date, budget, ad_cost, revenue_generated, customer_reach, leads, conversions, coupon_code, coupon_redemptions, status)
VALUES
(1,    'Weekend Biryani Fest',        'social',   'promotional', CURRENT_DATE - 30, CURRENT_DATE - 16, 50000, 42000, 118000, 24000, 3200, 640,  'BIRYANI20', 640, 'completed'),
(2,    'Chennai Coffee Culture',      'social',   'promotional', CURRENT_DATE - 40, CURRENT_DATE - 10, 35000, 30000,  85000, 18000, 2400, 480,  'CHNCOFFEE', 480, 'completed'),
(3,    'Monsoon Coffee Combo',        'in-store', 'seasonal',    CURRENT_DATE - 20, CURRENT_DATE - 5,  30000, 27000,  71000, 15000, 2100, 410,  'MONSOON10', 410, 'completed'),
(4,    'Koramangala Techie Lunch',    'email',    'promotional', CURRENT_DATE - 15, CURRENT_DATE + 15, 25000, 15000,  58000, 12000, 1800, 390,  'TECHLUNCH', 390, 'active'),
(5,    'Hyderabad Biryani Bonanza',   'social',   'promotional', CURRENT_DATE - 50, CURRENT_DATE - 20, 60000, 52000, 165000, 35000, 4200, 910,  'HYDBIRYANI',910, 'completed'),
(6,    'Financial District Express',  'in-store', 'launch',      CURRENT_DATE - 60, CURRENT_DATE - 30, 40000, 35000,  92000, 22000, 2800, 550,  'FINEXPRESS',550, 'completed'),
(7,    'Madurai Traditional Delight', 'print',    'seasonal',    CURRENT_DATE - 25, CURRENT_DATE - 5,  20000, 18000,  42000, 10000, 1200, 240,  'MDUSPECIAL',240, 'completed'),
(8,    'Kochi Sea Breeze Festival',   'social',   'seasonal',    CURRENT_DATE - 18, CURRENT_DATE + 12, 32000, 20000,  64000, 16000, 2100, 420,  'KOCHIBREEZE',420,'active'),
(9,    'Mumbai Loyalty Rewards',      'email',    'loyalty',     CURRENT_DATE - 45, CURRENT_DATE - 15, 25000, 12000,  68000, 9000,  1500, 720,  'LOYAL15',   720, 'completed'),
(10,   'Lower Parel Gourmet Launch',  'social',   'launch',      CURRENT_DATE - 35, CURRENT_DATE - 5,  75000, 68000, 195000, 45000, 5800, 1250, 'GOURMET20',1250, 'completed'),
(11,   'Pune Student Discount',       'in-store', 'promotional', CURRENT_DATE - 14, CURRENT_DATE + 16, 15000,  9000,  38000, 6000,  900,  310,  'STUDENT10', 310, 'active'),
(12,   'Viman Nagar Youth Fest',      'social',   'promotional', CURRENT_DATE - 22, CURRENT_DATE + 8,  28000, 18000,  62000, 14000, 1900, 410,  'YOUTHFEST', 410, 'active'),
(13,   'Ahmedabad Festive Snacks',    'print',    'seasonal',    CURRENT_DATE - 40, CURRENT_DATE - 10, 45000, 40000, 110000, 26000, 3100, 690,  'AMDDIWALI', 690, 'completed'),
(14,   'Surat Textile Hub Special',   'in-store', 'promotional', CURRENT_DATE - 30, CURRENT_DATE - 2,  30000, 25000,  78000, 17000, 2200, 510,  'SURATFEST', 510, 'completed'),
(15,   'Delhi Winter Specials',       'print',    'seasonal',    CURRENT_DATE - 60, CURRENT_DATE - 30, 40000, 38000,  41000, 11000, 1800, 210,  'WINTER25',  210, 'completed'),
(16,   'Saket Mall Shopping Combo',   'social',   'promotional', CURRENT_DATE - 20, CURRENT_DATE + 10, 50000, 35000, 105000, 28000, 3600, 780,  'SAKETMALL', 780, 'active'),
(17,   'Gurgaon Corporate Pass',      'email',    'loyalty',     CURRENT_DATE - 50, CURRENT_DATE - 10, 45000, 32000, 135000, 30000, 4100, 950,  'CORPPASS',  950, 'completed'),
(18,   'Noida Sector 18 Rush',        'social',   'promotional', CURRENT_DATE - 25, CURRENT_DATE + 5,  35000, 24000,  79000, 19000, 2500, 540,  'NOIDARUSH', 540, 'active'),
(19,   'Chandigarh Grand Opening',    'print',    'launch',      CURRENT_DATE - 200, CURRENT_DATE - 185, 70000, 55000, 61000, 25000, 3000, 220,  'CHDOPEN',   220, 'completed'),
(20,   'Jaipur Heritage Flavours',    'social',   'promotional', CURRENT_DATE - 35, CURRENT_DATE - 5,  38000, 32000,  88000, 21000, 2700, 590,  'JAIPURHER', 590, 'completed'),
(21,   'Lucknow Royal Treat',         'in-store', 'seasonal',    CURRENT_DATE - 28, CURRENT_DATE + 2,  29000, 21000,  67000, 15000, 1900, 430,  'LKOROYAL',  430, 'active'),
(22,   'Kolkata Festive Push',        'social',   'seasonal',    CURRENT_DATE - 25, CURRENT_DATE - 5,  35000, 30000,  95000, 18000, 2600, 590,  'FEST2026',  590, 'completed'),
(23,   'Park Street Evening Lights',  'social',   'launch',      CURRENT_DATE - 12, CURRENT_DATE + 18, 45000, 22000,  33000, 14000, 1900, 260,  'PARKPRE',   260, 'active'),
(24,   'Bhubaneswar Temple Fest',     'print',    'seasonal',    CURRENT_DATE - 45, CURRENT_DATE - 15, 22000, 19000,  51000, 12000, 1400, 320,  'BHUBFEST',  320, 'completed'),
(25,   'Guwahati Tea & Treats',       'in-store', 'promotional', CURRENT_DATE - 30, CURRENT_DATE + 0,  20000, 16000,  48000, 11000, 1300, 290,  'GAUCOMM',   290, 'active'),
(NULL, 'App Launch Campaign',         'social',   'launch',      CURRENT_DATE - 10, CURRENT_DATE + 10, 80000, 35000,  96000, 52000, 4800, 980,  'APP2026',   980, 'active'),
(NULL, 'Network-wide Referral Push',  'email',    'loyalty',     CURRENT_DATE - 7,  CURRENT_DATE + 23, 20000,  8000,  29000, 7000,  1100, 260,  'REFER2026', 260, 'active'),
(NULL, 'National Loyalty Tier Launch','email',    'loyalty',     CURRENT_DATE - 120, CURRENT_DATE - 90, 55000, 20000,  88000, 30000, 3600, 890,  'TIERUP',    890, 'completed')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 10. AUDIT DATA (50+ Audits across all 25 outlets)
-- ---------------------------------------------------------------------
INSERT INTO audits (outlet_id, scheduled_date, completed_date, status, compliance_score, risk_score, verification_score, approval_score, approval_stage, auditor_name) VALUES
(1,  CURRENT_DATE - 40,  CURRENT_DATE - 38, 'completed', 92.5, 12.0, 94.0, 90.0, 'approved',           'S. Narayanan'),
(2,  CURRENT_DATE - 35,  CURRENT_DATE - 33, 'completed', 88.0, 18.5, 90.0, 86.0, 'approved',           'S. Narayanan'),
(3,  CURRENT_DATE - 60,  CURRENT_DATE - 58, 'completed', 94.0, 8.0,  95.0, 93.0, 'approved',           'A. Deshmukh'),
(4,  CURRENT_DATE - 90,  CURRENT_DATE - 88, 'completed', 61.0, 45.0, 58.0, 55.0, 'manager_approval',   'P. Iyer'),
(5,  CURRENT_DATE - 20,  CURRENT_DATE - 18, 'completed', 91.0, 14.0, 92.0, 89.0, 'approved',           'A. Deshmukh'),
(6,  CURRENT_DATE - 100, CURRENT_DATE - 97, 'completed', 54.0, 58.0, 50.0, 48.0, 'changes_requested',  'P. Iyer'),
(7,  CURRENT_DATE - 55,  CURRENT_DATE - 52, 'completed', 79.0, 28.0, 80.0, 76.0, 'supervisor_review',  'R. Krishnan'),
(8,  CURRENT_DATE - 15,  CURRENT_DATE - 12, 'completed', 87.0, 19.0, 88.0, 85.0, 'approved',           'S. Narayanan'),
(9,  CURRENT_DATE - 70,  CURRENT_DATE - 67, 'completed', 96.0, 6.0,  97.0, 95.0, 'approved',           'R. Krishnan'),
(10, CURRENT_DATE - 45,  CURRENT_DATE - 42, 'completed', 93.5, 11.0, 95.0, 92.0, 'approved',           'V. Kulkarni'),
(11, CURRENT_DATE - 30,  CURRENT_DATE - 28, 'completed', 86.0, 22.0, 87.0, 84.0, 'approved',           'V. Kulkarni'),
(12, CURRENT_DATE - 50,  CURRENT_DATE - 47, 'completed', 89.5, 16.0, 91.0, 88.0, 'approved',           'V. Kulkarni'),
(13, CURRENT_DATE - 65,  CURRENT_DATE - 62, 'completed', 78.0, 31.0, 80.0, 76.0, 'supervisor_review',  'M. Patel'),
(14, CURRENT_DATE - 80,  CURRENT_DATE - 77, 'completed', 82.0, 24.0, 83.0, 80.0, 'approved',           'M. Patel'),
(15, CURRENT_DATE - 10,  CURRENT_DATE - 8,  'completed', 95.0, 9.0,  96.0, 94.0, 'approved',           'P. Iyer'),
(16, CURRENT_DATE - 25,  CURRENT_DATE - 22, 'completed', 90.0, 15.0, 92.0, 88.0, 'approved',           'P. Iyer'),
(17, CURRENT_DATE - 38,  CURRENT_DATE - 35, 'completed', 97.0, 5.0,  98.0, 96.0, 'approved',           'P. Iyer'),
(18, CURRENT_DATE - 42,  CURRENT_DATE - 39, 'completed', 84.0, 25.0, 85.0, 82.0, 'approved',           'R. Krishnan'),
(19, CURRENT_DATE - 75,  CURRENT_DATE - 72, 'completed', 91.5, 13.0, 93.0, 90.0, 'approved',           'R. Krishnan'),
(20, CURRENT_DATE - 85,  CURRENT_DATE - 82, 'completed', 83.0, 26.0, 84.0, 81.0, 'approved',           'R. Krishnan'),
(21, CURRENT_DATE - 95,  CURRENT_DATE - 92, 'completed', 77.0, 33.0, 78.0, 75.0, 'supervisor_review',  'R. Krishnan'),
(22, CURRENT_DATE - 18,  CURRENT_DATE - 15, 'completed', 88.5, 17.0, 90.0, 86.0, 'approved',           'K. Banerjee'),
(23, CURRENT_DATE - 28,  CURRENT_DATE - 25, 'completed', 92.0, 12.0, 93.0, 90.0, 'approved',           'K. Banerjee'),
(24, CURRENT_DATE - 62,  CURRENT_DATE - 59, 'completed', 80.0, 29.0, 81.0, 78.0, 'approved',           'K. Banerjee'),
(25, CURRENT_DATE - 72,  CURRENT_DATE - 69, 'completed', 85.0, 21.0, 86.0, 83.0, 'approved',           'K. Banerjee')
ON CONFLICT DO NOTHING;

INSERT INTO audit_reports (audit_id, category, finding, severity, is_violation, resolved, responsible_person, due_date, resolution) VALUES
(4,  'hygiene',   'Storage temperature log missing for 3 days',              'medium',   TRUE, FALSE, 'Outlet Manager, Connaught Place', CURRENT_DATE + 7,  NULL),
(4,  'financial', 'Cash register reconciliation mismatch of ₹1,200',         'high',     TRUE, FALSE, 'Outlet Manager, Connaught Place', CURRENT_DATE + 3,  NULL),
(6,  'safety',    'Fire extinguisher inspection overdue',                    'critical', TRUE, FALSE, 'Outlet Manager, Madurai Junction', CURRENT_DATE - 2, NULL),
(6,  'inventory', 'Stock count variance exceeding 8% threshold',             'high',     TRUE, FALSE, 'Outlet Manager, Madurai Junction', CURRENT_DATE + 5,  NULL),
(7,  'hygiene',   'Minor: staff hygiene checklist not signed for one shift', 'low',      FALSE, TRUE,  'Shift Supervisor, Hitech City',    CURRENT_DATE - 10, 'Checklist retroactively signed and process corrected.'),
(13, 'inventory', 'Labeling mismatch on 5 frozen items',                     'medium',   TRUE, FALSE, 'Outlet Manager, CG Road',          CURRENT_DATE + 4,  NULL)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------
-- 11. AI INSIGHTS, RECOMMENDATIONS & ALERTS
-- ---------------------------------------------------------------------
INSERT INTO ai_insights (outlet_id, category, title, summary, confidence) VALUES
(1,  'sales',       'Peak Weekend Surge',           'Anna Nagar sales increase 42% on Saturdays between 7 PM and 10 PM.', 94.5),
(3,  'inventory',   'Coffee Supply Optimization',   'Indiranagar cold coffee bean inventory projected to run low in 4 days.', 91.0),
(9,  'marketing',   'High ROAS Campaign',           'Lower Parel Gourmet Launch achieved 2.87x ROAS, outperforming West region avg.', 96.2),
(17, 'staff',       'High Staff Efficiency',        'Cyber Hub staff productivity score reached 98/100 during lunch hours.', 93.8),
(NULL,'intelligence','Franchise Growth Trend',      'Network-wide Q3 revenue expanded 18.4% YoY led by South and West regions.', 95.0)
ON CONFLICT DO NOTHING;

INSERT INTO recommendations (outlet_id, title, description, priority, category, status) VALUES
(6,  'Resolve Safety Audit Violation',   'Replace expired fire extinguisher and complete staff safety briefing.', 'critical', 'audit',     'open'),
(4,  'Reconcile Cash Discrepancy',       'Audit daily cash register logs at Connaught Place to resolve ₹1,200 mismatch.', 'high', 'finance',   'in_progress'),
(3,  'Reorder Cold Coffee Beans',        'Replenish SKU-002 to avoid stockout prior to upcoming weekend.', 'medium',   'inventory', 'open'),
(11, 'Extend Student Promo Campaign',    'Pune Student Discount campaign showing 4.2x ROI; recommend 15-day extension.', 'low', 'marketing', 'resolved')
ON CONFLICT DO NOTHING;

INSERT INTO alerts (outlet_id, type, message, severity, is_read) VALUES
(6,  'audit_due',      'Critical audit violation: Fire extinguisher inspection overdue at Madurai Junction.', 'critical', FALSE),
(4,  'poor_performance','Cash register variance of ₹1,200 flagged at Connaught Place.', 'high', FALSE),
(3,  'low_stock',      'Cold Coffee (SKU-002) below reorder threshold at Indiranagar Central.', 'medium', FALSE),
(13, 'expiring',       'Almond Tart batch expiring in 6 days at CG Road Commercial.', 'low', FALSE)
ON CONFLICT DO NOTHING;
