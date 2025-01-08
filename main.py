import sys

from movie_app import MovieApp
from storage import StorageJson, StorageCsv
from pathlib import Path
from typing import Tuple
from logger import setup_logger

logger = setup_logger(__name__)


def get_start_params(params: str) -> Tuple[str, str]:
    """
    validate args and return correctly
    :param arg_1:
    :type arg_1:
    :param arg_2:
    :type arg_2:
    :return:
    :rtype:
    """

    _, storage_name = params.lower().split(".")
    storage_type = storage_name.strip()
    if _is_valid_storage_type(storage_type):
        storage_type = _return_storage_type(storage_name)
        logger.info("Params parsed", storage_name, storage_type)
        return params, storage_type


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


def main(storage_file, storage_type):

    logger.info("New instance started %s, %s", storage_file, storage_type)
    with StorageCsv(storage_file) as storage:
        app = MovieApp(storage)
        logger.info("New instance started %s, %s", storage_file, storage_type)
        app.run()


if __name__ == "__main__":
    storage_dir = Path(__file__).resolve().parent / "data"
    storage_dir.mkdir(parents=True, exist_ok=True)

    storage_json = storage_dir / "default.json"
    storage_csv = storage_dir / "default.csv"

    if len(sys.argv) == 2:
        params = sys.argv[1]
        storage_file, storage_class = get_start_params(params)
        if storage_file and storage_class:
            storage_path = storage_dir / storage_file
    else:
        storage_path = storage_json
        storage_class = StorageJson
    main(storage_path, storage_class)
