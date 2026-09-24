-- Основная таблица игр
CREATE TABLE IF NOT EXISTS games (
    app_id INTEGER PRIMARY KEY,
    name VARCHAR(500),
    release_date DATE,
    estimated_owners VARCHAR(50),
    peak_ccu INTEGER DEFAULT 0,
    price NUMERIC(10,2) DEFAULT 0,
    positive INTEGER DEFAULT 0,
    negative INTEGER DEFAULT 0,
    avg_playtime_forever INTEGER DEFAULT 0,
    median_playtime_forever INTEGER DEFAULT 0,
    required_age INTEGER DEFAULT 0
);

-- Таблица жанров
CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Таблица разработчиков
CREATE TABLE IF NOT EXISTS developers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) UNIQUE NOT NULL
);

-- Таблица издателей
CREATE TABLE IF NOT EXISTS publishers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) UNIQUE NOT NULL
);

-- Связь игра-жанр (многие ко многим)
CREATE TABLE IF NOT EXISTS game_genres (
    game_id INTEGER REFERENCES games(app_id),
    genre_id INTEGER REFERENCES genres(id),
    PRIMARY KEY (game_id, genre_id)
);

-- Связь игра-разработчик
CREATE TABLE IF NOT EXISTS game_developers (
    game_id INTEGER REFERENCES games(app_id),
    developer_id INTEGER REFERENCES developers(id),
    PRIMARY KEY (game_id, developer_id)
);

-- Связь игра-издатель
CREATE TABLE IF NOT EXISTS game_publishers (
    game_id INTEGER REFERENCES games(app_id),
    publisher_id INTEGER REFERENCES publishers(id),
    PRIMARY KEY (game_id, publisher_id)
);