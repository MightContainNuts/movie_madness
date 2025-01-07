from storage import StorageJson
from pathlib import Path


class TestStorage:

    JSON_DATA = Path(".") / "storage" / "test_data.json"
    print(JSON_DATA)
    test_json_storage = StorageJson(JSON_DATA)

    def test_load_to_local(self):
        self.test_json_storage._load_to_local()
        for key, value in self.test_json_storage.local_storage.items():
            print(key, value)
        assert self.test_json_storage.local_storage  # Check if it's not empty
        assert (
            "Inception" in self.test_json_storage.local_storage
        )  # Check if a specific movie is present
        assert (
            self.test_json_storage.local_storage["The Thing"]["rating"] == 9.0
        )
