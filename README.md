# Steam Analytics

Аналитический pet-project: исследование каталога Steam (125 855 игр) с помощью SQL и Python.

Построен как демонстрация навыков Data Analyst: ETL-пайплайн, нормализованная PostgreSQL-схема, SQL-аналитика с оконными функциями, Python-анализ через pandas/numpy, обнаружение аномалий через z-score.

## Стек

- **Python 3.10** — pandas, numpy, SQLAlchemy
- **PostgreSQL 15** (Docker) — нормализованная схема, индексы, EXPLAIN ANALYZE
- **Jupyter Notebook** — разведочный анализ
- **Docker Compose** — воспроизводимое окружение

## Структура проекта

```
steam-analytics/
├── data/
│   ├── raw/games.csv                  # исходный датасет
│   └── processed/                     # экспорты из БД для Jupyter
├── notebooks/
│   └── 01_exploratory_analysis.ipynb  # разведочный анализ
├── sql/
│   ├── schema.sql                     # схема БД (7 таблиц)
│   └── queries/                       # аналитические запросы
│       ├── 08_genre_dynamics.sql      # динамика релизов LAG + PARTITION BY
│       ├── 09_genre_quality.sql       # рейтинг жанров по отзывам
│       ├── 10_explain_before.sql      # EXPLAIN ANALYZE до индекса
│       ├── 11_add_index.sql           # добавление индекса
│       └── 14_anomalies.sql           # z-score аномалии цен
├── src/
│   ├── etl.py                         # ETL-пайплайн
│   └── anomaly_detection.py          # поиск ценовых аномалий
└── docker-compose.yml
```

## Быстрый старт

```bash
# 1. Поднять PostgreSQL
docker compose up -d

# 2. Создать схему
docker exec -i steam_postgres psql -U steam_user -d steamdb < sql/schema.sql

# 3. Запустить ETL
source venv/bin/activate
python src/etl.py

# 4. Найти аномалии
python src/anomaly_detection.py
```

## Схема базы данных

7 таблиц: `games`, `genres`, `developers`, `publishers`, `game_genres`, `game_developers`, `game_publishers`.

Ключевое решение: жанры вынесены в отдельную таблицу с отношением many-to-many через `game_genres` (338 583 связи).

## Ключевые находки

### Структура каталога
- 125 855 игр, 33 жанра, 338 583 жанровых связей
- 8 423 игры (6.7%) без жанра — плейтесты и служебные страницы
- 7 жанров (Indie, Casual, Action, Adventure, Simulation, Strategy, RPG) составляют **90% каталога** — классический принцип Парето

### Динамика рынка
- Структурный перелом **2014 года**: трёхкратный рост релизов во всех жанрах
- Просадка **2019 года** — синхронно по всем жанрам

### Цены
- Медиана по каталогу: **$3.59**, среднее: **$6.10** — среднее всегда выше медианы из-за выбросов
- Нишевый софт (Video Production, Animation & Modeling) в 3–4 раза дороже игровых жанров
- Популярные жанры дешевле из-за высокой конкуренции, а не наоборот

### Аномалии цен
- 2 863 ценовые аномалии (z-score > 2.0) обнаружено через Python
- Топ: The Leverage Game ($999.98, z=73.22), Ascent VR ($999.00, z=57.86)

### Качество жанров
- MMO (68%) и Early Access (75%) статистически ниже среднего рейтинга (~80%)
- Early Access берёт премию за ранний доступ: медианная цена выше среднерыночной

## ETL: решённая проблема

Исходный CSV содержал дефект заголовка: колонки `Discount` и `DLC count` были склеены в `DiscountDLC count` из-за потерянной запятой. Это сдвигало все последующие колонки, включая `Genres` и `Categories`, что давало 2 922 «жанра» вместо 33.

Решение: `pd.read_csv(header=0, names=COLUMNS)` с явным списком из 40 имён колонок.
