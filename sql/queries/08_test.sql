SELECT COUNT(*) AS games_without_genre, AVG(g.price) AS avg_price, AVG(g.positive*100.0/NULLIF(g.positive+g.negative, 0)) AS positive_percentage
FROM games g
JOIN game_genres gg ON g.app_id = gg.game_id
JOIN genres ge ON ge.id = gg.genre_id
GROUP BY ge.id, ge.name;
