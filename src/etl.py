import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text 
import ast
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('etl.log'),
        logging.StreamHandler() 
    ]
)
logger = logging.getLogger(__name__)

engine = create_engine(
    'postgresql://steam_user:steam_pass@127.0.0.1:5434/steamdb',
    pool_pre_ping=True,
    connect_args={'connect_timeout': 10}
)

def parse_list_column(value):
    if pd.isna(value) or value=="":
        return []
    try:
        result = ast.literal_eval(value)
        if isinstance(result, list):
            return [str(x) for x in result if x]
        return [str(result).strip()]
    except:
        return [str(value).strip()]
    
def parse_comma_list(value):
    if pd.isna(value) or value == "":
        return []
    return [item.strip() for item in str(value).split(',') if item.strip()] 
    
def parse_date(value):
    try:
        return pd.to_datetime(value).date()
    except:
        return None
    
# Полная, корректная схема из 40 колонок.
# Критично: Discount и DLC count — ДВЕ отдельные колонки (в заголовке CSV
# они склеены в 'DiscountDLC count' из-за потерянной запятой, что и ломало
# выравнивание всех последующих колонок, включая Genres/Categories).
COLUMNS = [
    'AppID', 'Name', 'Release date', 'Estimated owners', 'Peak CCU',
    'Required age', 'Price', 'Discount', 'DLC count', 'About the game',
    'Supported languages', 'Full audio languages', 'Reviews',
    'Header image', 'Website', 'Support url', 'Support email',
    'Windows', 'Mac', 'Linux', 'Metacritic score', 'Metacritic url',
    'User score', 'Positive', 'Negative', 'Score rank', 'Achievements',
    'Recommendations', 'Notes', 'Average playtime forever',
    'Average playtime two weeks', 'Median playtime forever',
    'Median playtime two weeks', 'Developers', 'Publishers',
    'Categories', 'Genres', 'Tags', 'Screenshots', 'Movies'
]

def extract():
    logger.info('Читаем данные из CSV файла...')

    # header=0  -> первая строка файла считается заголовком и отбрасывается
    # names=... -> присваиваем свои 40 имён напрямую по позициям.
    # Так pandas НЕ уводит AppID в индекс и ничего не сдвигает.
    df = pd.read_csv('data/raw/games.csv', header=0, names=COLUMNS)

    # Защита от тихой поломки: если структура файла изменится, падаем сразу.
    if df.shape[1] != len(COLUMNS):
        raise ValueError(
            f'Ожидали {len(COLUMNS)} колонок, получили {df.shape[1]}. '
            f'Проверь структуру CSV.'
        )

    logger.info(f'Данные успешно считаны. Строк: {len(df)}, колонок: {df.shape[1]}')
    return df

def transform(df):
    logger.info('Начинаем трансформацию данных...')
    df = df.rename(columns={
        'AppID': 'app_id',
        'Name': 'name',
        'Release date': 'release_date',
        'Estimated owners': 'estimated_owners',
        'Peak CCU': 'peak_ccu',
        'Price': 'price',
        'Positive': 'positive',
        'Negative': 'negative',
        'Average playtime forever': 'avg_playtime_forever',
        'Median playtime forever': 'median_playtime_forever',
        'Required age': 'required_age',
        'Genres': 'genres',
        'Developers': 'developers',
        'Publishers': 'publishers'
    })
    cols = [
        'app_id', 'name', 'release_date', 'estimated_owners',
        'peak_ccu', 'price', 'positive', 'negative',
        'avg_playtime_forever', 'median_playtime_forever', 'required_age',
        'genres', 'developers', 'publishers'
    ]
    df = df[cols].copy()
    before = len(df)
    df = df.dropna(subset=['app_id'])
    logger.info(f'Удалено строк без app_id: {before - len(df)}')
    df['release_date'] = df['release_date'].apply(parse_date)

    num_cols = [
        'peak_ccu', 'price', 'positive', 'negative',
        'avg_playtime_forever', 'median_playtime_forever',
        'required_age'
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['app_id'] = pd.to_numeric(df['app_id'], errors='coerce')
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=['app_id'])
    df['app_id'] = df['app_id'].astype(int)
    df = df.drop_duplicates(subset=['app_id'], keep='first')
    logger.info(f"После удаления дубликатов app_id: {len(df)}")
   

    logger.info(f"Трансформация завершена. Строк после очистки: {len(df)}")
    return df

def load(df):
    logger.info('Начинаем загрузку данных в базу данных...')

    df = df.copy()
    df['genres_list'] = df['genres'].apply(parse_comma_list)

    try:
        with engine.connect() as conn:
            logger.info('Очищаем таблицы...')
            conn.execute(text(
                'TRUNCATE games, genres, developers, game_genres ' 
                'RESTART IDENTITY CASCADE'
            ))
            conn.commit()
            
            logger.info('Загружаем таблицу games...')
            games_df = df[[
                'app_id', 'name', 'release_date', 'estimated_owners',
                'peak_ccu', 'price', 'positive', 'negative',
                'avg_playtime_forever', 'median_playtime_forever', 'required_age'
            ]].copy()

            games_df.to_sql(
                'games', conn,
                if_exists='append',
                index=False,
                chunksize=500
            )
            conn.commit()

            logger.info(f"Загружено игр: {len(games_df)}")

            logger.info("Загружаем жанры...")
            all_genres = set()
            for genres_list in df['genres_list']:
                all_genres.update(genres_list)
            
            for genres in all_genres:
                 conn.execute(text(
                    "INSERT INTO genres (name) VALUES (:name) "
                    "ON CONFLICT (name) DO NOTHING"
                ), {"name": genres})
            conn.commit()
            
            logger.info(f"Загружено жанров: {len(all_genres)}")

            logger.info("Загружаем разработчиков...")
            all_devs = set()
            for val in df['developers'].dropna():
                for d in str(val).split(','):
                    d = d.strip()
                    if d:
                        all_devs.add(d)
            
            for dev in all_devs:
                conn.execute(text(
                    "INSERT INTO developers (name) VALUES (:name) "
                    "ON CONFLICT (name) DO NOTHING"
                ), {"name": dev})
            conn.commit()
            logger.info(f"Загружено разработчиков: {len(all_devs)}")

            logger.info('Загружаем связи игра-жанр...')
            genre_map = dict(conn.execute(
                text("SELECT name, id FROM genres") 
            ).fetchall())

            game_genres_rows = []
            for app_id, genres_list in zip(df['app_id'], df['genres_list']):
                for g in genres_list:
                    if g in genre_map:
                        game_genres_rows.append({
                            'game_id': app_id,
                            'genre_id': genre_map[g]
                        })

            if game_genres_rows:
                pd.DataFrame(game_genres_rows).to_sql(
                    'game_genres', conn,
                    if_exists='append',
                    index=False,
                    chunksize=500
                )
            conn.commit()
            logger.info(f"Загружено связей игра-жанр: {len(game_genres_rows)}")     
        
        logger.info('ETL процесс завершен успешно.')

    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        raise

if __name__ == "__main__":
    df = extract()
    df = transform(df)
    load(df)


