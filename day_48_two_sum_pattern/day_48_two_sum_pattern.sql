-- PostgreSQL: Two-sum pattern for transaction reconciliation.
-- Values are stored as integer cents to avoid floating-point currency errors.
-- The schema supports complementary lookups, pair counting, and difference searches.

BEGIN;

DROP VIEW IF EXISTS matching_transaction_pairs;
DROP TABLE IF EXISTS reconciliation_targets CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;

CREATE TABLE transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reference_code TEXT NOT NULL UNIQUE,
    amount_cents BIGINT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'pending',
    CONSTRAINT transactions_reference_nonempty
        CHECK (length(trim(reference_code)) > 0),
    CONSTRAINT transactions_status_valid
        CHECK (status IN ('pending', 'posted', 'reconciled', 'excluded'))
);

CREATE INDEX transactions_amount_lookup_idx
    ON transactions (amount_cents)
    WHERE status <> 'excluded';

CREATE INDEX transactions_recorded_at_idx
    ON transactions (recorded_at DESC);

CREATE TABLE reconciliation_targets (
    target_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    description TEXT NOT NULL,
    target_cents BIGINT NOT NULL,
    required_status TEXT NOT NULL DEFAULT 'posted',
    CONSTRAINT targets_description_nonempty
        CHECK (length(trim(description)) > 0),
    CONSTRAINT targets_status_valid
        CHECK (required_status IN ('pending', 'posted', 'reconciled'))
);

INSERT INTO transactions
    (reference_code, amount_cents, status)
VALUES
    ('TX-104', 12500, 'posted'),
    ('TX-105', 27500, 'posted'),
    ('TX-106', 8000, 'posted'),
    ('TX-107', 20000, 'posted'),
    ('TX-108', 12500, 'posted'),
    ('TX-109', 40000, 'excluded'),
    ('TX-110', -5000, 'pending');

INSERT INTO reconciliation_targets
    (description, target_cents, required_status)
VALUES
    ('Two-line-item settlement', 40000, 'posted'),
    ('Duplicate transaction test', 25000, 'posted'),
    ('Negative adjustment analysis', 3000, 'posted');

-- Complement lookup: return one qualifying pair without pairing a row
-- with itself. The ID ordering gives each unordered pair one representation.
SELECT
    a.transaction_id AS left_id,
    a.reference_code AS left_reference,
    a.amount_cents AS left_amount_cents,
    b.transaction_id AS right_id,
    b.reference_code AS right_reference,
    b.amount_cents AS right_amount_cents,
    a.amount_cents + b.amount_cents AS combined_cents
FROM transactions AS a
JOIN transactions AS b
    ON b.amount_cents = 40000 - a.amount_cents
   AND b.transaction_id > a.transaction_id
WHERE a.status = 'posted'
  AND b.status = 'posted'
ORDER BY a.transaction_id, b.transaction_id;

-- Pair counting: each matching combination of records contributes one.
-- This differs from counting distinct combinations of numeric values.
SELECT COUNT(*) AS matching_record_pair_count
FROM transactions AS a
JOIN transactions AS b
    ON b.amount_cents = 40000 - a.amount_cents
   AND b.transaction_id > a.transaction_id
WHERE a.status = 'posted'
  AND b.status = 'posted';

-- A reusable view represents all valid pairs for the posted transaction set.
CREATE VIEW matching_transaction_pairs AS
SELECT
    a.transaction_id AS left_id,
    a.reference_code AS left_reference,
    a.amount_cents AS left_amount_cents,
    b.transaction_id AS right_id,
    b.reference_code AS right_reference,
    b.amount_cents AS right_amount_cents,
    a.amount_cents + b.amount_cents AS combined_cents
FROM transactions AS a
JOIN transactions AS b
    ON b.transaction_id > a.transaction_id
   AND b.amount_cents = 40000 - a.amount_cents
WHERE a.status = 'posted'
  AND b.status = 'posted';

SELECT * FROM matching_transaction_pairs
ORDER BY left_id, right_id;

-- Pair counts for several targets using a relational join.
SELECT
    target.target_id,
    target.description,
    target.target_cents,
    COUNT(pair.left_id) AS matching_pairs
FROM reconciliation_targets AS target
LEFT JOIN LATERAL (
    SELECT a.transaction_id AS left_id
    FROM transactions AS a
    JOIN transactions AS b
        ON b.transaction_id > a.transaction_id
       AND b.amount_cents = target.target_cents - a.amount_cents
    WHERE a.status = target.required_status
      AND b.status = target.required_status
) AS pair ON TRUE
GROUP BY target.target_id, target.description, target.target_cents
ORDER BY target.target_id;

-- Frequency-based pair counting uses n * (n - 1) / 2 for equal values
-- and frequency(a) * frequency(b) for distinct values.
WITH frequencies AS (
    SELECT amount_cents, COUNT(*)::BIGINT AS frequency
    FROM transactions
    WHERE status = 'posted'
    GROUP BY amount_cents
),
value_pairs AS (
    SELECT
        a.amount_cents AS amount_a,
        b.amount_cents AS amount_b,
        CASE
            WHEN a.amount_cents = b.amount_cents
                THEN a.frequency * (a.frequency - 1) / 2
            ELSE a.frequency * b.frequency
        END AS pair_count
    FROM frequencies AS a
    JOIN frequencies AS b
      ON b.amount_cents = 40000 - a.amount_cents
     AND b.amount_cents >= a.amount_cents
)
SELECT
    amount_a,
    amount_b,
    pair_count
FROM value_pairs
WHERE pair_count > 0
ORDER BY amount_a, amount_b;

-- Signed difference: find ordered pairs where right - left = 7500.
SELECT
    a.reference_code AS lower_position_reference,
    a.amount_cents AS left_amount_cents,
    b.reference_code AS right_position_reference,
    b.amount_cents AS right_amount_cents
FROM transactions AS a
JOIN transactions AS b
    ON b.amount_cents = a.amount_cents + 7500
   AND b.transaction_id <> a.transaction_id
WHERE a.status = 'posted'
  AND b.status = 'posted'
ORDER BY a.transaction_id, b.transaction_id;

-- Absolute difference: either value may be larger.
SELECT
    a.reference_code AS reference_a,
    a.amount_cents AS amount_a,
    b.reference_code AS reference_b,
    b.amount_cents AS amount_b,
    ABS(b.amount_cents - a.amount_cents) AS absolute_difference_cents
FROM transactions AS a
JOIN transactions AS b
    ON b.transaction_id > a.transaction_id
   AND ABS(b.amount_cents::NUMERIC - a.amount_cents::NUMERIC) = 7500
WHERE a.status = 'posted'
  AND b.status = 'posted'
ORDER BY a.transaction_id, b.transaction_id;

-- A transaction boundary demonstrates atomic reconciliation updates.
-- Only posted records are eligible for this operation.
SAVEPOINT before_reconciliation;

WITH chosen_pair AS (
    SELECT left_id, right_id
    FROM matching_transaction_pairs
    ORDER BY left_id, right_id
    LIMIT 1
)
UPDATE transactions AS t
SET status = 'reconciled'
FROM chosen_pair AS pair
WHERE t.transaction_id IN (pair.left_id, pair.right_id)
  AND t.status = 'posted';

SELECT reference_code, amount_cents, status
FROM transactions
ORDER BY transaction_id;

-- Restore the demonstration state so the script can be run repeatedly
-- without leaving sample transactions reconciled.
ROLLBACK TO SAVEPOINT before_reconciliation;
RELEASE SAVEPOINT before_reconciliation;

-- A target with no possible pair returns zero, rather than disappearing.
SELECT
    target.description,
    COUNT(pair.left_id) AS matching_pairs
FROM reconciliation_targets AS target
LEFT JOIN LATERAL (
    SELECT a.transaction_id AS left_id
    FROM transactions AS a
    JOIN transactions AS b
        ON b.transaction_id > a.transaction_id
       AND b.amount_cents = target.target_cents - a.amount_cents
    WHERE a.status = target.required_status
      AND b.status = target.required_status
) AS pair ON TRUE
GROUP BY target.target_id, target.description
ORDER BY target.target_id;

COMMIT;
