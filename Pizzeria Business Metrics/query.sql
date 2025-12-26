CREATE INDEX idx_orders_status ON orders (status);

-- Lost renevue rate

SELECT 
	SUM(oi.pizza_amount) * COUNT(oi.order_id) AS "Lost Revenue Rate"
FROM orders AS o
INNER JOIN order_items AS oi
ON o.id = oi.order_id
WHERE o.status = 'Отменен'
ORDER BY "Lost Revenue Rate" DESC;

-- Deliver Underutilization

WITH courier_stats AS (                                             -- количество выполненных заказов/рабочих дней у курьера за период.
    SELECT
        o.deliver_id,
        SUM(
            CASE 
                WHEN o.status = 'Доставлен' THEN 1 
                ELSE 0 
            END
        ) AS delivered_orders,
        COUNT(DISTINCT DATE(o.date_time)) AS active_days
    FROM orders o
    GROUP BY o.deliver_id
),
courier_load AS (                                                   -- среднее количество заказов курьера в день.
    SELECT
        deliver_id,
        delivered_orders / NULLIF(active_days, 0) AS courier_load
    FROM courier_stats
),
ranked AS (                                                         -- ранг курьера по среднему количеству заказов в день.
    SELECT
        deliver_id,
        courier_load,
        ROW_NUMBER() OVER (ORDER BY courier_load) AS rn,
        COUNT(*) OVER () AS total_cnt
    FROM courier_load
),
benchmark AS (                                                      -- медиана по загруженности.
    SELECT
        AVG(courier_load) AS median_load
    FROM ranked
    WHERE rn IN (
        FLOOR((total_cnt + 1) / 2),
        FLOOR((total_cnt + 2) / 2)
    )
)
SELECT
    r.deliver_id,
    ROUND(r.courier_load, 2) AS courier_load,
    ROUND(b.median_load, 2) AS median_load,
    ROUND(r.courier_load / b.median_load, 2) AS underutilization_ratio
FROM ranked r
CROSS JOIN benchmark b
WHERE r.deliver_id IS NOT NULL
ORDER BY underutilization_ratio;

-- Top-10 Dependency Rate

WITH total_orders_sum AS (
	SELECT 
		SUM(oi.price) AS total
	FROM order_items AS oi
	INNER JOIN orders AS o
	ON oi.order_id = o.id
	WHERE o.status = 'Доставлен'
)
SELECT 
	c.id,
    SUM(oi.price) AS total_customer_sum,
	ts.total,
    ROUND(SUM(oi.price) / ts.total, 2) AS percentage
FROM customer AS c
INNER JOIN orders AS o
ON c.id = o.customer_id
INNER JOIN order_items AS oi
ON o.id = oi.order_id
CROSS JOIN total_orders_sum ts
WHERE o.status = 'Доставлен'
GROUP BY c.id, ts.total
ORDER BY percentage DESC
LIMIT 10;
