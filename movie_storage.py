import json
import sys
from logger import setup_logger
from utils import MovieUtils
import re


class MovieDB:
    MOVIE_DB = "data.json"
    local_storage = {}
    TITLE = "title"
    DATE = "date"
    RATING = "rating"

    # magic methods and overrides #

    def __init__(self, MOVIE_DB: str = None) -> None:
        """
        Setup default values for new instance
        :param self: access to class
        :param db_path: optional, defaults to none
        :return: None
        """
        self.OPTION_LIST = {
            1: {
                "DESCRIPTION": "List movies",
                "FUNCTION": lambda: self.list_movies(),
            },
            2: {
                "DESCRIPTION": "Add new movie",
                "FUNCTION": lambda: self.add_movie(),
            },
            3: {
                "DESCRIPTION": "Delete movie from database",
                "FUNCTION": lambda: self.delete_movie(),
            },
            4: {
                "DESCRIPTION": "Update Movie rating",
                "FUNCTION": lambda: self.update_movie(),
            },
            5: {
                "DESCRIPTION": "Print statistics",
                "FUNCTION": lambda: self.display_stats(),
            },
            6: {
                "DESCRIPTION": "Search for movie",
                "FUNCTION": lambda: self.search_movie(),
            },
            0: {
                "DESCRIPTION": "Exit MovieMadness",
                "FUNCTION": lambda: self.quit(),
            },
        }
        self.logger = setup_logger(__name__)
        self.utils = MovieUtils(self)

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

    # Command Menu #
    def command_menu_options(self):
        while True:
            self.utils.display_menu(self)
            try:
                action = int(input("\n\nWhat do you want to do ?   "))
            except Exception as e:
                self.logger.error("Ooops. invalid option chosen  %s", e)

            if (
                isinstance(action, int)
                and action >= 0
                and action in self.OPTION_LIST
            ):
                func = self.OPTION_LIST[action]["FUNCTION"]
                self.logger.info(
                    "Option executed %s",
                    self.OPTION_LIST[action]["DESCRIPTION"],
                )
                func()

    # Movie commands options #
    def list_movies(self):
        print("Listing movies ...")
        self.logger.info("Listing Movies started")
        if self.local_storage:
            self.utils.print_movie_list(self.local_storage)
        else:
            self.logger.error(
                "MovieDB is empty or not loaded correctly: %s", self.MOVIE_DB
            )
        self.logger.info("... Listing Movies finished")

    def add_movie(self):
        """
        Adds a movie to the movies database.
        Loads the information from the JSON file, add the movie,
        and saves it. The function doesn't need to validate the input.
        """
        print("Adding Movie ...")
        self.logger.info("Add Movie started...")
        new_movie_title = self.utils.check_movie_title()
        if not self.utils.movie_in_db(new_movie_title, self.local_storage):
            new_movie_date = self.utils.check_movie_date()
            new_movie_rating = self.utils.check_movie_rating()
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
                    "Error occurred while saving the movie. Please try again."
                )
        else:
            print("Movie exists in db")
        self.logger.info("... Add movie finished")

    def delete_movie(self):
        """
        Deletes a movie from the movies database.
        Loads the information from the JSON file, deletes the movie,
        and saves it. The function doesn't need to validate the input.
        """
        print("Deleting Movie... ")
        self.logger.info("Delete Movie starting...")
        movie_to_delete = self.utils.check_movie_title()
        if self.utils.movie_in_db(movie_to_delete, self.local_storage):
            print(f"Removing {movie_to_delete} from database... ")
            self.logger.info(
                "Attempting to remove film from local storage %s",
                movie_to_delete,
            )
            try:
                del self.local_storage[movie_to_delete]
                print(f"Movie deleted. '{movie_to_delete}'")
                self.logger.info(
                    "Film removed successfully: %s", movie_to_delete
                )
            except KeyError:
                print(f"Unexpected error: '{movie_to_delete}' was not found.")
                self.logger.error(
                    "KeyError: Failed to remove film '%s' - film not found.",
                    movie_to_delete,
                )
            except Exception as e:
                print(f"An error occurred while removing the movie: {e}")
                self.logger.error(
                    "Unexpected error while removing film: %s", e
                )
        else:
            print(f"{movie_to_delete} not in DB")
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
        movie_to_update = self.utils.check_movie_title()
        if self.utils.movie_in_db(movie_to_update, self.local_storage):
            new_rating = self.utils.check_movie_rating()
            old_rating = self.local_storage[movie_to_update]["rating"]
            try:
                self.local_storage[movie_to_update]["rating"] = new_rating
            except Exception as e:
                self.logger.error(
                    "Unexpected error while updating rating: %s",
                    e,
                    exc_info=True,
                )
            self.logger.info(
                "Film %s : rating updated from %s to %s",
                movie_to_update,
                old_rating,
                new_rating,
            )
            print(f"{movie_to_update}': {old_rating} -> {new_rating}")
        else:
            print(f"{movie_to_update} not in DB")
        self.save_to_file()
        self.logger.info("... Update Movie finished")

    def display_stats(self):
        self.logger.info("calculating stats started ...")
        movie_stat_dict = {}
        if not self.local_storage:
            print("No films to display statistics for")
            self.logger.warning("No films in local storage")
            return
        movie_stat_dict["ratings"] = [
            movie_data["rating"] for movie_data in self.local_storage.values()
        ]
        max_rating = max(movie_stat_dict["ratings"])
        min_rating = min(movie_stat_dict["ratings"])
        movie_stat_dict["best_movies"] = [
            movie
            for movie in self.local_storage.items()
            if movie[1]["rating"] == max_rating
        ]
        movie_stat_dict["worst_movies"] = [
            movie
            for movie in self.local_storage.items()
            if movie[1]["rating"] == min_rating
        ]
        self.utils.print_stats(movie_stat_dict)
        self.logger.info("... Calculating stats finished")
        return movie_stat_dict

    def search_movie(self):
        self.logger.info("search movie stats started ...")
        find_movie = self.check_movie_title()
        print(f"Searching for movies matching: {find_movie}")
        try:
            pattern = re.compile(find_movie, re.IGNORECASE)
            matches = {
                title: data
                for title, data in self.local_storage.items()
                if pattern.search(title)
            }
            if matches:
                print("Found matching movies:")
                for title, data in matches.items():
                    print(f"{title} ({data['date']})- : {data['rating']}, ")
            else:
                print("No movies found matching your search.")

        except re.error as e:
            print(f"Invalid regular expression: {e}")
            self.logger.error(
                f"Invalid regex search term: {find_movie} - Error: {e}"
            )

    def quit(self):
        self.logger.info("Quit starting ...")
        print("Exiting MovieMadness...")
        self.save_to_file()
        self.logger.info("Program terminating...")
        print("Bye!!")
        self.logger.info("... quit finished")
        sys.exit()
