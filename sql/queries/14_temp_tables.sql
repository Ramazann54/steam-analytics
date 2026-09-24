-- Шаг 1: создаём временную таблицу с отфильтрованными играми.
-- Фильтры: после 2015-го, платные, минимум 100 отзывов.
-- positive_pct считаем здесь один раз, чтобы не повторять формулу дальше.
CREATE TEMP TABLE tmp_filtered_games AS
SELECT
    g.app_id,
    g.price,
    g.positive * 100.0 / NULLIF(g.positive + g.negative, 0) AS positive_pct
FROM games g
WHERE g.release_date >= '2015-01-01'
  AND g.price > 0
  AND g.positive + g.negative > 100;

-- Шаг 2: обновляем статистику — обязательно после создания.
ANALYZE tmp_filtered_games;

-- Шаг 3: по готовой таблице считаем рейтинг жанров.
SELECT
    ge.name AS genre,
    COUNT(*) AS games_count,
    ROUND(AVG(t.positive_pct), 2) AS avg_positive_pct,
    ROUND(AVG(t.price), 2) AS avg_price
FROM tmp_filtered_games t
JOIN game_genres gg ON gg.game_id = t.app_id
JOIN genres ge ON ge.id = gg.genre_id
GROUP BY ge.id, ge.name
HAVING COUNT(*) >= 100
ORDER BY avg_positive_pct DESC
LIMIT 10;