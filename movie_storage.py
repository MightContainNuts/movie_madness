import json
import sys
import pandas as pd
import logging
import os


class MovieDB:
    MOVIE_DB = "data.json"
    local_storage = {}
    TITLE = "title"
    DATE = "date"
    RATING = "rating"

    # magic methods and overrides #

    def __init__(self, logging=logging, MOVIE_DB: str = None) -> None:
        """
        Setup default values for new instance
        :param self: access to class
        :param db_path: optional, defaults to none
        :return: None
        """
        self.option_list = {
            1: {
                "DESCRIPTION": "List movies",
                "ARGUMENTS": 0,
                "FUNCTION": lambda: self.list_movies(),
            },
            2: {
                "DESCRIPTION": "Add new movie",
                "ARGUMENTS": 0,
                "FUNCTION": lambda: self.add_movie(),
            },
            3: {
                "DESCRIPTION": "Delete movie from database",
                "ARGUMENTS": 0,
                "FUNCTION": lambda: self.delete_movie(),
            },
            4: {
                "DESCRIPTION": "Update Movie rating",
                "ARGUMENTS": 0,
                "FUNCTION": lambda: self.update_movie(),
            },
            5: {
                "DESCRIPTION": "Print statistics",
                "ARGUMENTS": 0,
                "FUNCTION": lambda: self.print_stats(),
            },
            0: {
                "DESCRIPTION": "Exit MovieMadness",
                "ARGUMENTS": 0,
                "FUNCTION": lambda: self.quit(),
            },
        }

        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,  # Set default logging level to INFO
            filename=log_file,  # Logs will be written to this file
            filemode="a",
            format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
        )
        if MOVIE_DB:
            self.MOVIE_DB = MOVIE_DB
        self.logger.info(
            "New Instance of MovieDB started",
        )

    def __repr__(self) -> str:
        """
        string rep of class stuff
        :return: name of database used
        """
        return f"<MovieDatabase(db_path='{self.MOVIE_DB}')>"

    def __enter__(self) -> "MovieDB":
        """
        setup routine on initialisation
        :return:
        """
        self.load_to_local()
        self.logger.info("Context Manager started")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        tear down, added logger, excepts in case of sad path
        :param exc_type
        :param exc_value:
        :param traceback:
        :param logger:
        :return:
        """
        if exc_type:
            self.logger.error(
                "Exception occurred: %s",
                exc_value,
                exc_info=(exc_type, exc_value, traceback),
            )
            self.save_to_file()
            self.logger.info(
                "Context Manager exited. DB saved to: %s", self.MOVIE_DB
            )

    # DB File handling #

    def load_to_local(self) -> None:
        self.logger.info("loading file to local_storage started ...")
        self.local_storage.clear()
        try:
            with open(self.MOVIE_DB, "r") as handle:
                # Use json.load() to load the data from the file
                self.local_storage = json.load(handle)
            if not self.local_storage:  # Check if dictionary is empty
                self.logger.warning(
                    "Remote database exists but is empty: %s", self.MOVIE_DB
                )
            else:
                self.logger.info("Database loaded into local")
        except FileNotFoundError:
            self.logger.error("DB File not found: %s", self.MOVIE_DB)
        except json.JSONDecodeError:
            self.logger.error(
                "Error decoding JSON in the file: %s", self.MOVIE_DB
            )
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... loading file to local_storage finished")

    def save_to_file(self) -> None:
        self.logger.info("Saving local storage to file ...")
        try:
            if self.MOVIE_DB is not None:
                with open(self.MOVIE_DB, "w") as write_handle:
                    json.dump(self.local_storage, write_handle, indent=4)
                self.logger.info("Movie DB saved to file: %s", self.MOVIE_DB)
                # Assertion check: Re-read the file to verify contents
                with open(self.MOVIE_DB, "r") as read_handle:
                    file_contents = json.load(read_handle)
                if file_contents == self.local_storage:
                    self.logger.info(
                        "Assertion checked: Remote is synced with Local"
                    )
                else:
                    self.logger.error(
                        "Assertion failed: Remote is not synced with Local!"
                    )
            else:
                self.logger.warning(
                    "Movie DB path is None; skipping save operation"
                )
        except FileNotFoundError:
            self.logger.error("DB File not found: %s", self.MOVIE_DB)
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... saving local_storage to file finished")

    # common functions #
    def check_movie_title(self, in_database: bool):
        """
        Checks for valid movie title for the operation
        :param in_database
        True, check if title not exist (add movie)
        False, check if title exist for delete, update
        :return: valid movie
        """
        self.logger.info("starting check_movie_title ...")
        while True:
            # Prompt for title
            movie_title = input(
                'Enter movie TITLE ("exit" to cancel): '
            ).strip()
            if movie_title.lower() == "exit":
                print("Add movie operation canceled.")
                self.logger.info("Movie operation cancelled gracefully")
                return
            if not movie_title:
                print("Title cannot be empty. Please try again.")
                continue
            if in_database:
                if movie_title in self.local_storage:
                    print(
                        f"The movie '{movie_title}' already exists. Try again."
                    )
                    continue
            else:
                if movie_title not in self.local_storage:
                    print(f"'{movie_title}' does not exists. Try again.")
                    continue
            break
        self.logger.info("Movie Title checked for validity %s", movie_title)
        self.logger.info("... Title check finished")
        return movie_title

    def check_movie_rating(self):
        self.logger.info("Start check movie rating ...")
        while True:
            movie_rating = input("Enter movie RATING: ").strip()
            if not movie_rating:
                print("Rating cannot be empty. Please try again.")
                continue
            try:
                movie_rating = float(movie_rating)
            except ValueError:
                print("Rating needs to be a float")
                continue
            if not (0 <= movie_rating <= 10):
                print("Rating needs to be a value between 0 and 10")
                continue
            break
        self.logger.info("Rating checked for validity %s", movie_rating)
        self.logger.info("... Rating check finished")

        return movie_rating

    # Command Menu #

    def command_menu_options(self):
        while True:
            print(
                "\n\nWelcome to MovieMadness ! - the movie app with meaning!"
            )
            print("-" * 60)
            for option, option_data in self.option_list.items():
                print(f'{option:>2}: {option_data["DESCRIPTION"]}')
            try:
                action = int(input("\n\nWhat do you want to do ?   "))
            except Exception as e:
                self.logger.error("Ooops. invalid option chosen  %s", e)

            if (
                isinstance(action, int)
                and action >= 0
                and action in self.option_list
            ):
                func = self.option_list[action]["FUNCTION"]
                self.logger.info(
                    "Option executed %s",
                    self.option_list[action]["DESCRIPTION"],
                )
                func()

    # Movie commands options #
    def list_movies(self):
        print("Listing movies ...")
        self.logger.info("Listing Movies started")
        if self.local_storage:
            print("\n\nFilms in database:")
            print("-" * 65)
            for movie, movie_data in self.local_storage.items():
                if self.local_storage:
                    date = movie_data.get(self.DATE, "N/A")
                    rating = movie_data.get(self.RATING, "N/A")
                    print(f"{movie} ({date}): {rating}")
            print(f"\nTotal films in database: {len(self.local_storage)} ")
            self.logger.info("List Movies: executed successfully")
        else:
            self.logger.error(
                "MovieDB is empty or not loaded correctly: %s", self.MOVIE_DB
            )
        self.logger.info("... Listing Movies finished")
        return self.MOVIE_DB

    def add_movie(self):
        """
        Adds a movie to the movies database.
        Loads the information from the JSON file, add the movie,
        and saves it. The function doesn't need to validate the input.
        """
        print("Adding Movie ...")
        self.logger.info("Add Movie started...")
        new_movie_title = self.check_movie_title(True)
        while True:
            new_movie_date = input("Enter new movie DATE): ").strip()
            if not new_movie_date:
                print("Date cannot be empty. Please try again.")
                continue
            break
        new_movie_rating = self.check_movie_rating()
        # save to local storage
        try:
            self.local_storage[new_movie_title] = {
                self.DATE: new_movie_date,
                self.RATING: new_movie_rating,
            }
            self.logger.info(
                "New movie added: Title: %s, Date: %s, Rating: %s",
                new_movie_title,
                new_movie_date,
                new_movie_rating,
            )
            # sync file
            self.save_to_file()
            print(f"'{new_movie_title}' has been successfully added.")
        except Exception as e:
            self.logger.error(
                "An error occurred while saving the movie: %s",
                e,
                exc_info=True,
            )
            print(
                "An error occurred while saving the movie. Please try again."
            )
        self.logger.info("... Add movie finished")

    def delete_movie(self):
        """
        Deletes a movie from the movies database.
        Loads the information from the JSON file, deletes the movie,
        and saves it. The function doesn't need to validate the input.
        """
        print("Deleting Movie... ")
        self.logger.info("Delete Movie starting...")
        film_to_delete = self.check_movie_title(False)
        print(f"Removing {film_to_delete} from database... ")
        self.logger.info(
            "Attempting to remove film from local storage %s", film_to_delete
        )
        try:
            del self.local_storage[film_to_delete]
            print(
                f"Movie deleted. '{film_to_delete}' removed from the database."
            )
            self.logger.info("Film removed successfully: %s", film_to_delete)
        except KeyError:
            print(f"Unexpected error: '{film_to_delete}' was not found.")
            self.logger.error(
                "KeyError: Failed to remove film '%s' - film not found.",
                film_to_delete,
            )
        except Exception as e:
            print(f"An error occurred while removing the movie: {e}")
            self.logger.error("Unexpected error while removing film: %s", e)
        self.save_to_file()
        self.logger.info("... Delete Movie finished")

    def update_movie(self):
        """
        Updates a movie from the movies database.
        Loads the information from the JSON file, updates the movie,
        and saves it. The function doesn't need to validate the input.
        """
        print("Updating Movie ...")
        self.logger.info("Starting update_movie")
        film_to_update = self.check_movie_title(False)
        new_rating = self.check_movie_rating()
        old_rating = self.local_storage[film_to_update]["rating"]
        try:
            self.local_storage[film_to_update]["rating"] = new_rating
        except Exception as e:
            self.logger.error(
                "Unexpected error while updating rating: %s", e, exc_info=True
            )
        self.logger.info(
            "Film %s : rating updated from %s to %s",
            film_to_update,
            old_rating,
            new_rating,
        )
        print(f"{film_to_update}': {old_rating} -> {new_rating}")
        self.save_to_file()
        self.logger.info("... Update Movie finished")

    def print_stats(self):
        """
        Create local dictionary to capture ratings and best, worst movies
        display statsL
        Average rating, Median rating, best movies, worst movies
        :return: None
        """
        print("Displaying statistics...")
        self.logger.info("displying stats started ...")

        movie_stats = {}

        if not self.local_storage:
            print("No films to display statistics for")
            self.logger.warning("No films in local storage")
            return

        movie_stats["ratings"] = [
            movie_data["rating"] for movie_data in self.local_storage.values()
        ]

        max_rating = max(movie_stats["ratings"])
        min_rating = min(movie_stats["ratings"])

        movie_stats["best_movies"] = [
            movie
            for movie in self.local_storage.items()
            if movie[1]["rating"] == max_rating
        ]

        movie_stats["worst_movies"] = [
            movie
            for movie in self.local_storage.items()
            if movie[1]["rating"] == min_rating
        ]

        if movie_stats["best_movies"]:
            # Create a DataFrame with the movie name and rating
            df = pd.DataFrame(
                [
                    (movie[0], movie[1]["rating"])
                    for movie in movie_stats["best_movies"]
                ],
                columns=["Movie", "Rating"],
            )
            print("\n\nBest rated movies:")
            print("-" * 40)
            print(df)
        else:
            print("No best movies found.")
            self.logger.error(
                "displaying stats: No best_movies found %s",
                movie_stats["best_movies"],
            )

        if movie_stats["worst_movies"]:
            df = pd.DataFrame(
                [
                    (movie[0], movie[1]["rating"])
                    for movie in movie_stats["worst_movies"]
                ],
                columns=["Movie", "Rating"],
            )
            print("\n\nWorst rated movies:")
            print("-" * 40)
            print(df)
        else:
            print("No worst movies found.")
            self.logger.error(
                "displaying stats: No worst_movies found %s",
                movie_stats["worst_movies"],
            )

        if movie_stats["ratings"]:
            self.logger.info("displaying stats: ratings")
            df = pd.DataFrame(movie_stats["ratings"], columns=["Rating"])
            median_rating = df["Rating"].median()
            average_rating = df["Rating"].mean()
            print("\n\nRatings:")
            print("-" * 40)
            print("\nMedian ", median_rating)
            print("Average ", average_rating)
        else:
            print("No worst movies found.")
            self.logger.errorinfo(
                "displaying stats: No ratings found %s", movie_stats["ratings"]
            )
        self.logger.info("...Stats printed finished")

    def quit(self):
        self.logger.info("Quit starting ...")
        print("Exiting MovieMadness...")
        self.save_to_file()
        self.logger.info("Program terminating...")
        print("Bye!!")
        self.logger.info("... quit finished")
        sys.exit()
