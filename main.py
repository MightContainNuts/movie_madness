from movie_app import MovieApp
from storage import StorageJson, StorageCsv
from pathlib import Path

storage_dir = Path(__file__).resolve().parent / "storage"
storage_dir.mkdir(parents=True, exist_ok=True)

storage_json = storage_dir / "movies.json"
storage_csv = storage_dir / "movies.csv"


def main():
    with StorageCsv(storage_csv) as storage:
        app1 = MovieApp(storage)
        app1.run()
    with StorageJson(storage_json) as storage:
        app2 = MovieApp(storage)
        app2.run()


if __name__ == "__main__":
    main()
