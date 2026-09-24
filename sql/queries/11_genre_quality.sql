SELECT ge.name,
    COUNT(*) AS games_count,
    ROUND(AVG(g.positive*100.0/NULLIF(g.positive+g.negative, 0)), 2) as avg_positive
FROM games g
JOIN game_genres gg ON g.app_id = gg.game_id
JOIN genres ge ON ge.id = gg.genre_id
WHERE g.positive + g.negative > 100
GROUP BY ge.id, ge.name
HAVING COUNT(*) > 100
ORDER BY avg_positive asc
LIMIT 10;