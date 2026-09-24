EXPLAIN ANALYZE
SELECT ge.name, COUNT(*)
FROM games g
JOIN game_genres gg ON g.app_id = gg.game_id
JOIN genres ge ON ge.id = gg.genre_id
WHERE ge.name = 'Documentary'
GROUP BY ge.name;