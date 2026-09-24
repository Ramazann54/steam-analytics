set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Укажи путь к .sql файлу."
    echo "Пример: ./run_sql.sh sql/queries/01_games_by_genre.sql"
    exit 1
fi

docker exec -i steam_postgres psql -U steam_user -d steamdb < "$1"