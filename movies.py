from movie_storage import MovieDB


def main():
    with MovieDB() as app:
        app.command_menu_options()


if __name__ == "__main__":
    main()
