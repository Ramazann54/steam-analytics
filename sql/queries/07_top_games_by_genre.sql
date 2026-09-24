WITH ranked_games AS (
    SELECT ge.name as genre_name, g.name as game_name, g.positive as positive, ROW_NUMBER() OVER(PARTITION BY ge.id ORDER BY g.positive DESC) as rn        
    FROM games g
    JOIN game_genres gg ON g.app_id = gg.game_id 
    JOIN genres ge ON ge.id = gg.genre_id
)
SELECT game_name, positive, genre_name
FROM ranked_games
WHERE rn <= 5;
ORDER BY genre_name, rn;
