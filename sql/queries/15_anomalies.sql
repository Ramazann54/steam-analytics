-- Поиск ценовых аномалий внутри жанров.
-- Сравниваем цену каждой игры со средним и стандартным отклонением
-- по её жанру — это z-score внутри группы.
-- Z-score > 2 означает: цена отличается от среднего жанра
-- более чем на 2 стандартных отклонения.       

WITH genre_stats AS (
    -- Шаг 1: считаем статистику по каждому жанру
    SELECT
        ge.id AS genre_id,
        ge.name AS genre,
        AVG(g.price) AS avg_price,
        STDDEV(g.price) AS std_price,
        COUNT(*) AS games_count
    FROM games g
    JOIN game_genres gg ON gg.game_id = g.app_id
    JOIN genres ge ON ge.id = gg.genre_id
    WHERE g.price > 0
    GROUP BY ge.id, ge.name
    HAVING COUNT(*) >= 100
),
game_zscores AS (
    -- Шаг 2: для каждой игры считаем z-score относительно её жанра
    SELECT
        g.app_id,
        g.name AS game_name,
        g.price,
        gs.genre,
        gs.avg_price,
        gs.std_price,
        ROUND((g.price - gs.avg_price) / NULLIF(gs.std_price, 0), 2) AS z_score
    FROM games g
    JOIN game_genres gg ON gg.game_id = g.app_id
    JOIN genre_stats gs ON gs.genre_id = gg.genre_id
    WHERE g.price > 0
)
-- Шаг 3: оставляем только аномалии
SELECT DISTINCT ON (game_name)
    game_name,
    genre,
    -- price,
    ROUND(avg_price, 2) AS genre_avg_price,
    z_score
FROM game_zscores
WHERE z_score > 2
ORDER BY game_name, z_score DESC
LIMIT 100;