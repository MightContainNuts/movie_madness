from logger import setup_logger
import pandas as pd
from datetime import datetime


class MovieUtils:
    def __init__(self, app):
        self.logger = setup_logger(__name__)
        self.app = app

    def print_stats(self, movie_stats):
        """
        Create local dictionary to capture ratings and best, worst movies
        display statsL
        Average rating, Median rating, best movies, worst movies
        :return: None
        """
        self.logger.info("Display stats started ...")
        print("Displaying statistics...")
        if movie_stats["best_movies"]:
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
            self.logger.error(
                "displaying stats: No ratings found %s", movie_stats["ratings"]
            )
        self.logger.info("...Stats printed finished")

    def print_movie_list(self, db_instance):
        self.logger.info("Printing movie data using Pandas...")
        if not db_instance:
            print("No movies available.")
        else:
            print("\nMovies in the database:")
            movie_data = pd.DataFrame.from_dict(db_instance, orient="index")
            movie_data = movie_data[["date", "rating"]].fillna("N/A")
            print(movie_data)
            self.logger.info("...Printing movie data using finished")

    def display_menu(self, app):
        """
        Struggling with pandas, but it's a learning process.
        :param app instance of MovieDB class:
        :return:
        """
        self.logger.info("Printing options menu...")
        print("\n\nWelcome to MovieMadness ! - the movie app with meaning!")
        print("-" * 55)
        option_data = pd.DataFrame.from_dict(app.OPTION_LIST, orient="index")
        option_data_display = option_data[["DESCRIPTION"]]
        option_data_display.index.name = "OPTION"
        print("OPTION".ljust(8), "DESCRIPTION")
        print("-" * 55)
        for index, row in option_data_display.iterrows():
            print(f"{index:<8} {row['DESCRIPTION']}")
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
                print("Add movie operation canceled.")
                self.logger.info("Movie operation cancelled gracefully")
                return
            if not movie_title:
                print("Title cannot be empty. Please try again.")
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

    def check_movie_date(self):
        self.logger.info("Start check movie date ...")
        current_year = datetime.now().year
        while True:
            movie_date = input("Enter new movie DATE (e.g. 1990): ").strip()

            if not movie_date:
                print("Date cannot be empty. Please try again.")
                continue

            try:
                movie_date = int(movie_date)
            except ValueError as e:
                print("Invalid input. Date needs to be an integer.")
                self.logger.error("ValueError on date %s: %s", movie_date, e)
                continue
            if 1888 <= movie_date <= current_year:
                self.logger.info(f"Movie year {movie_date} is valid.")
                return movie_date
            else:
                print(
                    f"{movie_date} needs to be between 1888 and {current_year}"
                )
                self.logger.warning(f"Invalid movie year: {movie_date}")

    def movie_in_db(self, movie: str, db_instance) -> bool:
        self.logger.info("starting movie_in_db check...")
        return movie in db_instance
