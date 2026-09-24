SELECT
    CASE
        WHEN g.price = 0 THEN 'FREE'
        WHEN g.price < 10 THEN 'CHEAP'
        WHEN g.price < 30 THEN 'BUDGET'
        ELSE 'PREMIUM'
    END AS price_segment,
    COUNT(*) AS games_count,
    ROUND(AVG(g.positive), 2) AS avg_positive
FROM games g    
GROUP BY price_segment;