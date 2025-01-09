import csv

from istorage import IStorage, File


from typing import override, TextIO
import json


class StorageJson(IStorage):
    def __init__(self, storage):
        super().__init__(storage)
        self.json_storage = storage

    def __repr__(self) -> str:
        """
        string rep of class stuff
        :return: name of database used
        """
        return f"<MovieDatabase(db_path='{self.json_storage} using JSON Storage')>"  # noqa E501

    # DB File handling #

    def _load_to_local(self) -> None:
        self.logger.info("loading json file to local_storage started ...")
        self.local_storage.clear()
        try:
            with open(self.json_storage, "r") as handle:
                self.local_storage = json.load(handle)
            if not self.local_storage:
                self.logger.warning(
                    "Remote database exists but is empty: %s",
                    self.json_storage,
                )
            else:
                self.logger.info("Database loaded into local")
        except FileNotFoundError:
            self.logger.error("DB File not found: %s", self.json_storage)
        except json.JSONDecodeError:
            self.logger.error(
                "Error decoding JSON in the file: %s", self.json_storage
            )
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... loading file to local_storage finished")

    def _save_to_file(self) -> None:
        self.logger.info("Saving local storage to file %s...")
        try:
            if self.json_storage is not None:
                write_handle: TextIO
                with open(self.json_storage, "w") as write_handle:
                    json.dump(self.local_storage, write_handle, indent=4)
                self.logger.info(
                    "Movie DB saved to file: %s", self.json_storage
                )
                # Assertion check: Re-read the file to verify contents
                with open(self.json_storage, "r") as read_handle:
                    file_contents = json.load(read_handle)
                if file_contents == self.local_storage:
                    self.logger.info(
                        "Assertion checked: Remote is synced with Local"
                    )
                else:
                    self.logger.error(
                        "Assertion failed: Remote is not synced with Local!"
                    )
            else:
                self.logger.warning(
                    "Movie DB path is None; skipping save operation"
                )
        except FileNotFoundError:
            self.logger.error("DB File not found: %s", self.json_storage)
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... saving local_storage to file finished")


class StorageCsv(IStorage):
    def __init__(self, storage: File):
        super().__init__(storage)
        self.csv_storage = storage

    def __repr__(self) -> str:
        """
        string rep of class stuff
        :return: name of database used
        """
        return f"<MovieDatabase(db_path='{self.csv_storage} using CSV File')>"

    # DB File handling #

    @override
    def _load_to_local(self) -> None:
        """
        overrides abstract. loads csv file and converts to dict
        :return:
        :rtype:
        """
        self.logger.info("loading csv file to local_storage started ...")
        try:
            with open(self.csv_storage, "r", encoding="utf-8") as handle:
                csv_reader = csv.reader(handle)
                csv_rows = list(csv_reader)
                for row in csv_rows:
                    self.logger.info(f"Found: {row}")
                self.local_storage = self._convert_csv_to_dict(csv_rows)
            if not self.local_storage:
                self.logger.warning(
                    "Remote database exists but is empty: %s",
                    self.csv_storage,
                )
            else:
                self.logger.info("Database loaded into local")
        except FileNotFoundError:
            self.logger.error("DB File not found: %s", self.csv_storage)
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... loading file to local_storage finished")

    @override
    def _save_to_file(self) -> None:
        """
        overrides the abstract - changed to write to csv files
        :return:
        :rtype:
        """
        self.logger.info("Saving local storage to CSV file ...")
        try:
            if self.csv_storage is not None:
                with open(
                    self.csv_storage, "w", newline="", encoding="utf-8"
                ) as write_handle:
                    csv_writer = csv.writer(write_handle)
                    for key, value in self.local_storage.items():
                        csv_writer.writerow(
                            [
                                key,
                                value["date"],
                                value["rating"],
                                value["poster_url"],
                                value["note"],
                            ]
                        )
                self.logger.info(
                    "Movie DB saved to file: %s", self.csv_storage
                )
                self._is_remote_equal_local()
            else:
                self.logger.warning(
                    "Movie DB path is None; skipping save operation"
                )
        except FileNotFoundError:
            self.logger.error("DB File not found: %s", self.csv_storage)
        except Exception as e:
            self.logger.error(
                "Yikes, something went wrong: %s", e, exc_info=True
            )
        self.logger.info("... saving local_storage to file finished")

    def _convert_csv_to_dict(self, csv_rows: list[list[str]]) -> dict:
        """
        Converts CSV content into a dictionary format.
        Each row should follow the format: title, year, rating
        """
        storage_dict = {}
        for row in csv_rows:
            if len(row) != 5:
                self.logger.warning(
                    f"Skipping row with incorrect number of fields: {row}"
                )
                continue  # Skip rows with the wrong number of fields

            title, date, rating, poster_url, note = row

            title = title.strip()
            date = date.strip()
            rating = rating.strip()
            poster_url = poster_url.strip()
            note = note.strip()

            if not title:
                self.logger.warning(f"Skipping row with empty title: {row}")
                continue

            try:
                date = int(date)
                rating = float(rating)

                storage_dict[title] = {
                    "date": date,
                    "rating": rating,
                    "poster_url": poster_url,
                    "note": note,
                }
            except ValueError as e:
                self.logger.warning(
                    f"Skipping row due to error in conversion: {row} | Error: {e}"  # noqa E501
                )

        return storage_dict

    def _is_remote_equal_local(self) -> bool:
        """
        check if remote and local are synced after saving
        :return:
        :rtype:
        """
        try:
            with open(self.csv_storage, "r", encoding="utf-8") as read_handle:
                csv_reader = csv.reader(read_handle)
                reloaded_storage = self._convert_csv_to_dict(csv_reader)

            self.logger.info(
                "Local Storage before saving: %s", self.local_storage
            )
            self.logger.info(
                "Reloaded Storage after reading: %s", reloaded_storage
            )

            if reloaded_storage == self.local_storage:
                self.logger.info(
                    "Assertion checked: Remote is synced with Local"
                )
                return True
            else:
                self.logger.error(
                    "Assertion failed: Remote is not synced with Local!"
                )
                self.logger.debug("Local storage: %s", self.local_storage)
                self.logger.debug("Reloaded storage: %s", reloaded_storage)
                return False
        except Exception as e:
            self.logger.error(
                "Error occurred while comparing remote and local: %s",
                e,
                exc_info=True,
            )
            return False
