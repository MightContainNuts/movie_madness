from istorage import IStorage
from logger import setup_logger
from utils import MovieUtils

from typing import override, TextIO, Self, Tuple
import json


class StorageJson(IStorage):

    local_storage: dict[str, dict[str, Tuple[int, float]]] = {}
    TITLE = "title"
    DATE = "date"
    RATING = "rating"

    def __init__(self, json_storage):
        self.utils = MovieUtils(self)
        self.logger = setup_logger(__name__)
        self.json_storage = json_storage

    def __repr__(self) -> str:
        """
        string rep of class stuff
        :return: name of database used
        """
        return f"<MovieDatabase(db_path='{self.json_storage} using JSON')>"

    def __enter__(self) -> Self:
        """
        setup routine on initialisation
        :return:
        """
        self._load_to_local()
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
            self._save_to_file()
            self.logger.info(
                "Context Manager exited. DB saved to: %s", self.json_storage
            )

    # DB File handling #

    @override
    def list_movies(self):
        print("Listing movies ...")
        self.logger.info("Listing Movies started")
        if self.local_storage:
            self.utils.print_movies(self.local_storage)
        else:
            self.logger.error(
                "MovieApp is empty or not loaded correctly: %s",
                self.json_storage,
            )
        self.logger.info("... Listing Movies finished")

    @override
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
                self._save_to_file()
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

    @override
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
        self._save_to_file()
        self.logger.info("... Delete Movie finished")

    @override
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
            print(
                f"{movie_to_update}': {old_rating}->{new_rating}"
            )  # noqa E501
        else:
            print(f"{movie_to_update} not in DB")
        self._save_to_file()
        self.logger.info("... Update Movie finished")

    def _load_to_local(self) -> None:
        self.logger.info("loading file to local_storage started ...")
        self.local_storage.clear()
        try:
            with open(self.json_storage, "r") as handle:
                # Use json.load() to load the data from the file
                self.local_storage = json.load(handle)
            if not self.local_storage:  # Check if dictionary is empty
                self.logger.warning(
                    "Remote database exists but is empty: %s",
                    self.json_storage,
                )
            else:
                self.logger.info("Database loaded into local")
        except FileNotFoundError:
            self.logger.error("DB File not found: %s", self.json_storage)
        except json.JSONDecodeError:
            self.logger.error(
                "Error decoding JSON in the file: %s", self.json_storage
            )
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... loading file to local_storage finished")

    def _save_to_file(self) -> None:
        self.logger.info("Saving local storage to file ...")
        try:
            if self.json_storage is not None:
                write_handle: TextIO
                with open(self.json_storage, "w") as write_handle:
                    json.dump(self.local_storage, write_handle, indent=4)
                self.logger.info(
                    "Movie DB saved to file: %s", self.json_storage
                )
                # Assertion check: Re-read the file to verify contents
                with open(self.json_storage, "r") as read_handle:
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
            self.logger.error("DB File not found: %s", self.json_storage)
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... saving local_storage to file finished")
