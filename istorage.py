import re
from abc import ABC, abstractmethod
from typing import Self
from logger import setup_logger
from utils import MovieUtils
from omdb_api import MovieDB_API
from pathlib import Path

LocalStorage = dict[str, dict[str, int | float]]
File = str


class IStorage(ABC):
    TITLE = "title"
    DATE = "date"
    RATING = "rating"
    POSTER_URL = "poster_url"
    NOTE = "note"

    def __init__(self, storage_file: File):
        self.local_storage: LocalStorage = {}
        self.utils = MovieUtils(self)
        self.logger = setup_logger(self.__class__.__module__)
        self.json_storage = storage_file

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

    def add_movie_from_omdb(self):
        """
        Adds a movie to the movies database.
        Loads the information from the JSON file, add the movie,
        and saves it. The function doesn't need to validate the input.
        """
        print("Adding Movie ...")
        self.logger.info("Add Movie started...")
        new_movie_title = self.utils.check_movie_title()
        app = MovieDB_API(new_movie_title)
        movie_to_add = app._get_movie_data()
        if movie_to_add:
            new_movie_title = movie_to_add[self.TITLE]

            if not self.utils.movie_in_db(new_movie_title, self.local_storage):
                new_movie_title = movie_to_add[self.TITLE]
                new_movie_date = movie_to_add[self.DATE]
                new_movie_rating = movie_to_add[self.RATING]
                new_poster_url = movie_to_add[self.POSTER_URL]
                new_note = "No Notes"

                # save to local storage
                try:
                    self.local_storage[new_movie_title] = {
                        self.DATE: new_movie_date,
                        self.RATING: new_movie_rating,
                        self.POSTER_URL: new_poster_url,
                        self.NOTE: new_note,
                    }
                    self.logger.info(
                        "New movie added: Title: %s, Date: %s, Rating: %s, URL: %s, Note: %s",  # noqa E501
                        new_movie_title,
                        new_movie_date,
                        new_movie_rating,
                        new_poster_url,
                        new_note,
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
                        "Error occurred while saving the movie. Please retry."
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
        self._save_to_file()
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

        movie_to_update = next(
            (
                key
                for key in self.local_storage
                if key.lower() == movie_to_update.lower()
            ),
            None,
        )
        if movie_to_update:
            new_note = self._get_new_note()
            old_note = self.local_storage[movie_to_update]["note"]
            try:
                self.local_storage[movie_to_update]["note"] = new_note
            except Exception as e:
                self.logger.error(
                    "Unexpected error while updating note: %s",
                    e,
                    exc_info=True,
                )
            self.logger.info(
                "Film %s : rating updated from %s to %s",
                movie_to_update,
                old_note,
                new_note,
            )
            print(f"{movie_to_update}': {old_note}->{new_note}")  # noqa E501
        else:
            print(f"{movie_to_update} not in DB")
        self._save_to_file()
        self.logger.info("... Update Movie finished")

    def generate_web_page(self):
        movie_grid = self._generate_contents_for_webpage()
        url = self._inject_contents_into_web_template(movie_grid)
        print(f"Web Page created at {url}")

    @abstractmethod
    def _load_to_local(self) -> None:
        """
        default method to be overwritten
        uses different file handling according to formats
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def _save_to_file(self) -> None:
        """
        default method to be overwritten
        uses different file handling according to formats
        :return:
        :rtype:
        """
        pass

    @staticmethod
    def _get_new_note() -> str:
        """
        update note for films
        :return:
        :rtype:
        """
        while True:
            new_note = input("Enter Note for movie: ")
            if not new_note:
                continue
            else:
                print(f"Adding new note to movie: \n {new_note}")
                return new_note.strip()

    def _generate_contents_for_webpage(self) -> str:
        """
        get movies from storage and populate html template
        :return:
        :rtype:
        """
        self.logger.info("starting to generate content for grid")
        contents: str = ""
        if self.local_storage:
            for movie in self.local_storage.items():
                movie_title, movie_stats = movie
                poster_url = movie_stats["poster_url"]
                movie_date = movie_stats["date"]
                movie_note = movie_stats["note"]
                movie_rating = movie_stats["rating"]
                img = f'<img class="movie-poster" src="{poster_url} alt= "Movie Poster"/>'  # noqa E501
                img_note = f'<p class="img_note">{movie_note}</p>'
                movie_rating = (
                    f'<p class="movie_rating">Rating: {movie_rating}/10</p>'
                )
                movie = f'<div class="movie-title">{movie_title}</div>'
                date = f'<div class="movie-year">{movie_date}</div>'

                item = f"""
            <li>
                <div class="movie">
                    {img}
                    {img_note}
                    {movie}
                    {date}
                    {movie_rating}
                </div>
            </li>"""

                contents += item
            self.logger.info("New contents created for Web")
            return contents

        else:
            self.logger.warning("Local storage empty, no text generated")

    def _inject_contents_into_web_template(self, movie_grid) -> Path:
        """
        replace placeholder with generated content
        :return:
        :rtype:
        """

        self.logger.info("Replacing placeholder with grid contents")
        DIR = Path(".") / "_static"
        TEMPLATE = DIR / "index_template.html"
        TARGET = DIR / "index.html"

        search_pattern = r"__TEMPLATE_MOVIE_GRID__"

        try:
            with open(TEMPLATE, "r") as read_handle, open(
                TARGET, "w"
            ) as write_handle:
                contents = read_handle.read()
                new_contents = re.sub(search_pattern, movie_grid, contents)
                write_handle.write(new_contents)
                return TARGET
        except IOError:
            print("error on writing new contents to file")
            self.logger.error("IO Error on file handling")
        except re.error:
            print("Error with the regular expression.")
            self.logger.error("RE Error on file handling")
