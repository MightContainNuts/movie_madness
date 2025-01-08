from __future__ import annotations
from logger import setup_logger
from datetime import datetime
from typing import Optional

import statistics


class MovieUtils:
    """
    utility class, moved out some stuff as it was getting cluttered
    """

    def __init__(self, app):
        """
        for initiating logger and passing to all functions.
        """
        self.app = app
        self.logger = setup_logger(__name__)

    def print_stats(self, movie_stats):
        """
        Create local dictionary to capture ratings and best, worst movies
        display statsL
        Average rating, Median rating, best movies, worst movies
        :return: None
        """
        self.logger.info("Display stats started ...")
        print("Displaying statistics...")
        print("\n\nBest rated movies:")
        print("-" * 70)
        print("MOVIE".ljust(50), "RATING".ljust(5))
        for movie in movie_stats["best_movies"]:
            movie_name = movie[0]
            movie_rating = movie[1]["rating"]
            print(f"{movie_name.ljust(20)} {str(movie_rating).ljust(5)}")

        print("\n\nWorst rated movies:")
        print("-" * 70)
        print("MOVIE".ljust(50), "RATING".ljust(5))
        for movie in movie_stats["worst_movies"]:
            movie_name = movie[0]
            movie_rating = movie[1]["rating"]
            print(f"{movie_name.ljust(50)} {str(movie_rating).ljust(5)}")

        ratings = movie_stats["ratings"]
        self.logger.info("displaying stats: ratings")
        median_rating = statistics.median(ratings)
        average_rating = sum(ratings) / len(ratings)
        print("\n\nRatings:")
        print("-" * 15)
        print("Median".ljust(10), f"{median_rating:.2f}".rjust(5))
        print("Average".ljust(10), f"{average_rating:.2f}".rjust(5))
        self.logger.info("...Stats printed finished")

    def display_menu(self, app):  # app:MovieApp
        """
        :param app instance of MovieApp class:
        :return:
        """
        self.logger.info("Printing options menu...")
        print("\n\nWelcome to MovieMadness ! - the movie app with meaning!")
        print("-" * 70)
        print("OPTION".ljust(8), "DESCRIPTION".ljust(30))
        print("-" * 70)
        for option, details in app.OPTION_LIST.items():
            print(f"{str(option).ljust(8)} {details['DESCRIPTION'].ljust(30)}")

        self.logger.info("...finished printing options")

    def print_movies(self, sorted_movies: dict[str, dict]):
        """
        print sorted menus
        :param sorted_movies:
        :return:
        """
        self.logger.info("Printing movies...")
        print("Movies sorted by rating: Highest first")
        print("-" * 70)
        print(
            "NR.".ljust(5),
            "MOVIE".ljust(50),
            "YEAR".ljust(5),
            "RATING".ljust(5),
            "POSTER URL".ljust(30),
        )
        for idx, (movie, movie_data) in enumerate(
            sorted_movies.items(), start=1
        ):
            print(
                str(idx).ljust(5),
                movie.ljust(50),
                str(movie_data["date"]).ljust(5),
                str(movie_data["rating"]).ljust(10),
                str(movie_data["poster_url"]).ljust(30),
            )
        self.logger.info("...finished printing options")

    def check_movie_title(self):
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
                print("Movie operation canceled.")
                self.logger.info("Movie operation cancelled gracefully")
                return
            if not movie_title:
                self.logger.info("Movie title empty")
                print("Title cannot be empty. Please try again.")
                continue
            break
        self.logger.info("Movie Title checked for validity %s", movie_title)
        self.logger.info("... Title check finished")
        return movie_title

    def check_movie_rating(self, min_rating=None):
        self.logger.info("Start check movie rating ...")
        while True:
            movie_rating = input("Enter movie RATING: ").strip()
            if not movie_rating and not min_rating:
                print("Rating cannot be empty. Please try again.")
                continue
            elif not movie_rating and min_rating:
                print("Checking all ratings")
                self.logger.info("No rating for filtering")
                movie_rating = 0
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

    def check_movie_date(
        self, min_date: Optional[str] = None, max_date: Optional[str] = None
    ) -> int:
        """
        first movie created in 1888
        :param min_date: for filter range
        :param max_date: for filter range
        :return: valid year a int
        """
        self.logger.info("Start check movie date ...")
        current_year = datetime.now().year
        FILM_START = 1888  # historical start of films
        while True:
            movie_date = input("Enter movie DATE (e.g. 1990): ").strip()
            if not any([movie_date, min_date, max_date]):
                print("Date cannot be empty. Please try again.")
                continue
            elif not movie_date and min_date:
                print(f"Using {FILM_START} for min date range")
                self.logger.info(
                    "Filtering using default value %s", FILM_START
                )
                return FILM_START
            elif not movie_date and max_date:
                print(f"Using {current_year} for max date range")
                self.logger.info(
                    "Filtering using default value %s", current_year
                )
                return current_year
            try:
                movie_date = int(movie_date)
            except ValueError as e:
                print("Invalid input. Date needs to be an integer.")
                self.logger.error("ValueError on date %s: %s", movie_date, e)
                continue
            if FILM_START <= movie_date <= current_year:
                self.logger.info(f"Movie year {movie_date} is valid.")
                return movie_date
            else:
                print(
                    f"{movie_date} needs to be between 1888 and {current_year}"
                )
                self.logger.warning(f"Invalid movie year: {movie_date}")

    def movie_in_db(self, movie: str, db_instance: dict[str, dict]) -> bool:
        self.logger.info("starting movie_in_db check...")
        return movie in db_instance
