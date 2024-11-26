import pytest
from unittest.mock import patch, mock_open, MagicMock
import json
import sys
import os
import importlib

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
MovieDB = importlib.import_module("movie_storage").MovieDB


test_data = {
    "Inception": {"date": "2010", "rating": 8.8},
    "The Matrix": {"date": "1999", "rating": 8.7},
}


class TestMovieDB:
    @pytest.fixture(autouse=True)
    def setup_class(self, mocker):
        """Setup the mock logger and the file data before each test."""
        # Create a mock logger for all test functions
        self.mock_logger = MagicMock()
        # Patch the setup_logger function to return the mock logger
        mocker.patch("logger.setup_logger", return_value=self.mock_logger)

        # Mock the file data
        self.mock_file_data = '{"movie": {"date": "2020", "rating": 8.5}}'
        self.mock_movie_db = "test.json"

        # Create an instance of MovieDB to test
        self.db = MovieDB()
        self.db.MOVIE_DB = self.mock_movie_db
        self.db.logger = self.mock_logger
        self.db.local_storage = test_data

    def test_load_success(self):
        # Mock the open function to read the mock file data
        with patch("builtins.open", mock_open(read_data=self.mock_file_data)):
            self.db.load_to_local()

        # Verify the local_storage is updated
        assert self.db.local_storage == {
            "movie": {"date": "2020", "rating": 8.5}
        }

        # Check if the info log has been called with the expected message
        self.mock_logger.info.assert_any_call("Database loaded into local")

    def test_save_to_mock_json_with_logging(self):
        # Patch open to mock file handling (write mode 'w' and read mode 'r')
        with patch("builtins.open", mock_open()) as mock_file, patch(
            "logger.setup_logger", return_value=self.mock_logger
        ):
            self.db.save_to_file()
            mock_file.assert_any_call(self.mock_movie_db, "w")
            mock_file.assert_any_call(self.mock_movie_db, "r")
            mock_file().write.assert_called_once_with(
                json.dumps(test_data, indent=4)
            )
            self.mock_logger.info.assert_any_call(
                "... saving local_storage to file finished"
            )

    def test_list_movies(self):
        with patch("builtins.open", mock_open(read_data=self.mock_file_data)):
            self.db.list_movies()
            pass
