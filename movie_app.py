import sys

from logger import setup_logger
from utils import MovieUtils
from storage import IStorage
import re


class MovieApp:
    def __init__(self, storage: IStorage = None) -> None:
        """
        Setup default values for new instance
        :param self: access to class
        :param db_path: optional, defaults to none
        :return: None
        """
        self.logger = setup_logger(__name__)
        self.utils = MovieUtils(self)
        self.storage = storage
        self.OPTION_LIST = {
            0: {
                "DESCRIPTION": "Exit MovieMadness",
                "FUNCTION": lambda: self.quit(),
            },
            1: {
                "DESCRIPTION": "List movies",
                "FUNCTION": lambda: self.storage.list_movies(),
            },
            2: {
                "DESCRIPTION": "Add new movie",
                "FUNCTION": lambda: self.storage.add_movie_from_omdb(),
            },
            3: {
                "DESCRIPTION": "Delete movie from database",
                "FUNCTION": lambda: self.storage.delete_movie(),
            },
            4: {
                "DESCRIPTION": "Update Movie rating - disabled!",
                "FUNCTION": lambda: print(
                    "func disabled"
                ),  # self.storage.update_movie(),
            },
            5: {
                "DESCRIPTION": "Print statistics",
                "FUNCTION": lambda: self.display_stats(),
            },
            6: {
                "DESCRIPTION": "Search for movie",
                "FUNCTION": lambda: self.search_movie(),
            },
            7: {
                "DESCRIPTION": "List movies by rating",
                "FUNCTION": lambda: self.sort_movie_rating(),
            },
            8: {
                "DESCRIPTION": "Filter movies by rating and date",
                "FUNCTION": lambda: self.filter_movies(),
            },
            9: {
                "DESCRIPTION": "Generate web page",
                "FUNCTION": lambda: storage.generate_web_page(),
            },
        }
        self.logger.info(
            "New Instance of MovieApp started",
        )

    # Command Menu #
    def run(self):
        while True:
            self.utils.display_menu(self)
            try:
                action = int(input("\n\nWhat do you want to do ?   "))
            except ValueError as e:
                print(
                    f"invalid option, choose an option between 0 and {len(self.OPTION_LIST) - 1}"  # noqa E501
                )
                self.logger.error("Ooops. invalid option chosen  %s", e)
                continue

            if isinstance(action, int) and 0 <= action <= len(
                self.OPTION_LIST
            ):
                func = self.OPTION_LIST[action]["FUNCTION"]
                self.logger.info(
                    "Option executed %s",
                    self.OPTION_LIST[action]["DESCRIPTION"],
                )
                func()
            else:
                continue

    def display_stats(self):
        self.logger.info("calculating stats started ...")
        movie_stat_dict = {}
        if not self.storage.local_storage:
            print("No films to display statistics for")
            self.logger.warning("No films in local storage")
            return
        movie_stat_dict["ratings"] = [
            movie_data["rating"]
            for movie_data in self.storage.local_storage.values()
        ]
        max_rating = max(movie_stat_dict["ratings"])
        min_rating = min(movie_stat_dict["ratings"])
        movie_stat_dict["best_movies"] = [
            movie
            for movie in self.storage.local_storage.items()
            if movie[1]["rating"] == max_rating
        ]
        movie_stat_dict["worst_movies"] = [
            movie
            for movie in self.storage.local_storage.items()
            if movie[1]["rating"] == min_rating
        ]
        if movie_stat_dict:
            self.utils.print_stats(movie_stat_dict)
        else:
            print("No data for statistics")
            self.logger.warning("No data for statistics %s", movie_stat_dict)
        self.logger.info("... Calculating stats finished")
        return movie_stat_dict

    def search_movie(self):
        self.logger.info("search movie stats started ...")
        find_movie = self.utils.check_movie_title()
        print(f"Searching for movies matching: {find_movie}")
        matches = {}
        try:
            pattern = re.compile(find_movie, re.IGNORECASE)
            matches = {
                movie: movie_data
                for movie, movie_data in self.storage.local_storage.items()
                if pattern.search(movie)
            }
            if matches:
                self.utils.print_movies(matches)
            else:
                print("No movies found matching your search.")

        except re.error as e:
            print(f"Invalid regular expression: {e}")
            self.logger.error(
                f"Invalid regex search term: {find_movie} - Error: {e}"
            )

    def sort_movie_rating(self):
        """
        list movies in order of rating, highest first
        :return:
        """
        self.logger.info("starting to sort movies by rating...")
        sorted_movies = dict(
            sorted(
                self.storage.local_storage.items(),
                key=lambda x: x[1]["rating"],
                reverse=True,
            )
        )
        if sorted_movies:
            self.utils.print_movies(sorted_movies)
        else:
            print("No movies in DB")
            self.logger.warning(
                "No movies in DB %s", self.storage.local_storage
            )
        self.logger.info("...finished sort movies by rating")

    def filter_movies(self):
        """
        prompt for minimum rating, start year, and end year.
        return list of movies
        if prompt empty use limit
        :return:
        """
        self.logger.info("Filtering movies started ...")
        print("Filtering movies...")
        filtered_movies = {}
        if self.storage.local_storage:
            min_rating = self.utils.check_movie_rating(min_rating=True)
            min_date = self.utils.check_movie_date(min_date=True)
            max_date = self.utils.check_movie_date(max_date=True)
            filtered_movies = {
                movie: movie_data
                for movie, movie_data in self.storage.local_storage.items()
                if (
                    movie_data["rating"] >= min_rating
                    and min_date <= movie_data["date"] <= max_date
                )
            }

            if filtered_movies:
                filtered_movies = dict(
                    sorted(filtered_movies.items(), key=lambda x: x[1]["date"])
                )
                self.utils.print_movies(filtered_movies)
            else:
                print("No movies with that criteria")
                self.logger.warning(
                    "no filtered movies %s %s %s",
                    min_rating,
                    min_date,
                    max_date,
                )

        else:
            print("No films in db to filter!")
            self.logger.warning(
                "No films to filter %s", self.storage.local_storage
            )

    def quit(self):
        self.logger.info("Quit starting ...")
        print("Exiting MovieMadness...")
        self.logger.info("Program terminating...")
        print("Bye!!")
        self.logger.info("... quit finished")
        sys.exit()
