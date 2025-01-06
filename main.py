from movie_app import MovieApp
from storage import StorageJson


def main():
    with StorageJson("movies.json") as storage:
        app = MovieApp(storage)
        app.run()


if __name__ == "__main__":
    main()
