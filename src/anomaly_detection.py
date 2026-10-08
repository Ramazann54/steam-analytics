import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
logger = logging.getLogger(__name__)

def load_data():
    """Загружаем даныне из CSV-файлов."""
    df_games = pd.read_csv('data/processed/games_export.csv')
    df_games_paid = df_games[df_games['price'] > 0]
    logger.info(f"Loaded {len(df_games_paid)} paid games.")
    df_genres = pd.read_csv('data/processed/genres_export.csv')
    df_merged = pd.merge(df_games_paid, df_genres, left_on='app_id', right_on='game_id', how='left')
    logger.info(f"Merged data: {len(df_merged)} rows.")
    return df_merged


def calculate_genre_stats(df):
    """Считаем среднее и std цены по каждому жанру."""
    df = df.copy()
    df['mean_price'] = df.groupby('genre')['price'].transform('mean')
    df['std_price'] = df.groupby('genre')['price'].transform('std')
    return df

def find_price_anomalies(df, threshold=2.0):
    """Находим аномалии в цене на основе z-score."""
    df = df.copy()
    df['z_score'] = (df['price'] - df['mean_price']) / df['std_price'].replace(0, np.nan)
    anomalies = df[df['z_score']>threshold].copy()
    logger.info(f"Found {len(anomalies)} anomalies in price.")
    return anomalies.sort_values('z_score', ascending=False)

def main():
    logger.info("Loading data...")
    df = load_data()

    logger.info("Calculating genre statistics...")
    df_stats = calculate_genre_stats(df)

    logger.info("Finding price anomalies...")
    anomalies = find_price_anomalies(df_stats)

    anomalies.round(2).to_csv('data/price_anomalies.csv', index=False)
    logger.info("Anomalies saved to 'data/price_anomalies.csv'.")
    
if __name__ == "__main__":
    main()