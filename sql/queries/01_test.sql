WITH ranked_games AS (
    SELECT
        ge.name AS genre,
        g.name AS game,
        g.positive,
        ROW_NUMBER() OVER (PARTITION BY ge.id ORDER BY g.positive DESC) AS rn
    FROM games g
    JOIN game_genres gg ON g.app_id = gg.game_id
    JOIN genres ge ON ge.id = gg.genre_id
)
SELECT genre, game, positive
FROM ranked_games
WHERE rn <= 3
ORDER BY genre, positive DESC;