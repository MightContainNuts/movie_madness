from movie_app import MovieApp
from storage import StorageJson
from pathlib import Path

storage_dir = Path.cwd() / "storage"
storage_dir.mkdir(parents=True, exist_ok=True)

storage_json = storage_dir / "movies.json"


def main():
    with StorageJson(storage_json) as storage:
        app = MovieApp(storage)
        app.run()


if __name__ == "__main__":
    main()
