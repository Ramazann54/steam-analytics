WITH games_year AS (
    SELECT 
        EXTRACT(YEAR FROM release_date) AS release_year,
        COUNT(*) AS total_games,
        LAG(COUNT(*)) OVER (PARTITION BY ge.name ORDER BY EXTRACT(YEAR FROM release_date)) AS total_games_last,
        ge.name as genre                       

    FROM games g   
    JOIN game_genres gg ON g.app_id = gg.game_id 
    JOIN genres ge ON ge.id = gg.genre_id
    WHERE release_date IS NOT NULL and EXTRACT(YEAR FROM release_date) <= 2025
    GROUP BY release_year, ge.name
    HAVING COUNT(*) > 50
)
SELECT genre, 
    release_year, 
    total_games, 
    total_games_last, ROUND((total_games - total_games_last)*100.0/NULLIF(total_games_last, 1), 1) AS difference
FROM games_year
ORDER BY genre, release_year


