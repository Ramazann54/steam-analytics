CREATE INDEX IF NOT EXISTS idx_game_genres_genre_id
    ON game_genres (genre_id);

ANALYZE game_genres;