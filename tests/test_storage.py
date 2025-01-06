from storage import StorageJson
import os


class TestStorage:

    JSON_DATA = os.path.join(os.path.dirname(__file__), "..", "movies.json")
    test_json_storage = StorageJson(JSON_DATA)

    def test_load_to_local(self):
        self.test_json_storage._load_to_local()
        for key, value in self.test_json_storage.local_storage.items():
            print(key, value)
        assert self.test_json_storage.local_storage  # Check if it's not empty
        assert (
            "Gone with the Wind" in self.test_json_storage.local_storage
        )  # Check if a specific movie is present
        assert (
            self.test_json_storage.local_storage["Gone with the Wind"][
                "rating"
            ]
            == 8.8
        )
