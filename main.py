from movie_app import MovieApp
from storage import StorageJson, StorageCsv
from pathlib import Path
from typing import Tuple

storage_dir = Path(__file__).resolve().parent / "data"
storage_dir.mkdir(parents=True, exist_ok=True)

storage_json = storage_dir / "movies.json"
storage_csv = storage_dir / "movies.csv"


def get_start_params(params: str) -> Tuple[str, str, str]:
    """
    validate args and return correctly
    :param arg_1:
    :type arg_1:
    :param arg_2:
    :type arg_2:
    :return:
    :rtype:
    """
    app_name, storage_name = params.lower().split(".")
    app_name = app_name.strip()
    storage_name = storage_name.strip()
    if _is_valid_storage_type(storage_name):
        storage_class = _return_storage_type(storage_name)
        return params, app_name, storage_class


def _is_valid_storage_type(storage_type: str) -> bool:
    """
    validate storage type
    :param storage_type:
    :type storage_type:
    :return:
    :rtype:
    """
    list_of_storages = ["json", "csv"]
    return storage_type in list_of_storages


def _return_storage_type(storage_name: str) -> str:
    """
    return class object
    :param storage_name:
    :type storage_name:
    :return:
    :rtype:
    """
    storage_mapping = {"json": StorageJson, "csv": StorageCsv}
    return storage_mapping[storage_name]


def main():
    with StorageCsv(storage_csv) as storage:
        app1 = MovieApp(storage)
        app1.run()
    with StorageJson(storage_json) as storage:
        app2 = MovieApp(storage)
        app2.run()


if __name__ == "__main__":
    main()
