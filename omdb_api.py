import requests
from logger import setup_logger


class MovieDB_API:
    def __init__(self, movie_name):
        self.logger = setup_logger(__name__)
        BASE_URL = "http://www.omdbapi.com/?t="
        API_KEY = "&apikey=f7235079"
        self.URL = BASE_URL + movie_name + API_KEY
        self.movie_name = movie_name

    def _get_movie_data(self) -> dict:
        """
        gets movie data in json from omdb api
        :return:
        :rtype:
        """
        self.logger.info(f"Retrieving {self.movie_name} from OMDB")

        try:
            response = requests.get(self.URL)
            if response.status_code == 200:
                response_json = response.json()
        except Exception as e:
            self.logger.error(
                "Unexpected exception caught", e, response.status_code
            )

        try:
            if response_json["Title"]:
                title = response_json.get("Title")
                date = response_json.get("Year", 0)
                date_int = self._validate_movie_year(date)
                rating = response_json.get("Ratings", [])
                rating_float = self._validate_movie_rating(rating)
                poster_url = response_json.get("Poster", "NA")
                self.logger.info(f"Movie data retrieved for {title}")
                return {
                    "title": title,
                    "date": date_int,
                    "rating": rating_float,
                    "poster_url": poster_url,
                }
        except KeyError as e:
            print("Title missing or incorrect ")
            self.logger.warning("Title missing or incorrect ", e)

    def _validate_movie_year(self, date: str) -> int:
        """
        validates movie year, casts as int
        :param date:
        :type date:
        :return: int - year or 0
        :rtype:
        """
        try:
            return int(date)
        except ValueError:
            self.logger.warning(
                "Invalid date on movie retrieval, substituted with 0"
            )
            return 0

    def _validate_movie_rating(self, rating: list) -> float:
        """
        parses rating and returns as float
        :param rating:
        :type rating:
        :return:
        :rtype:
        """
        imbdb_rating = 0
        if rating:
            imbdb_rating = rating[0]["Value"].split("/")[0]
            try:
                imbdb_rating = float(imbdb_rating)
            except ValueError:
                self.logger.warning(
                    "Invalid rating on movie retrieval, substituted with 0"
                )
                imbdb_rating = 0
        return imbdb_rating
