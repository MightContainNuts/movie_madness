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
MovieUtils = importlib.import_module("utils").MovieUtils


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

        # Create an instance of MovieApp to test
        self.db = MovieDB()
        self.db.movie_db = self.mock_movie_db
        self.db.logger = self.mock_logger
        self.db.local_storage = test_data
        self.utils = MovieUtils(self.db)

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

    def test_list_movies_with_data(self):
        # Set up test data in local_storage
        self.db.local_storage = {
            "Inception": {"date": "2010", "rating": 8.8},
            "The Matrix": {"date": "1999", "rating": 8.7},
        }

        # Mock the utils.print_movies method
        with patch.object(self.db.utils, "print_movies") as mock_print_list:
            self.db.list_movies()

            # Verify that print_movie_list was called with the correct data
            mock_print_list.assert_called_once_with(self.db.local_storage)

            # Check if the appropriate logging calls were made
            self.mock_logger.info.assert_any_call("Listing Movies started")
            self.mock_logger.info.assert_any_call(
                "... Listing Movies finished"
            )

    def test_check_movie_title(self, mocker, capsys):

        pass
