-- Количество игр в каждом жанре.
-- Показывает распределение игр Steam по жанрам.

SELECT
    g.name,
    COUNT(gg.game_id) AS games_count
FROM genres g
JOIN game_genres gg ON g.id = gg.genre_id
GROUP BY g.id, g.name
ORDER BY games_count DESC;