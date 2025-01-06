from abc import ABC, abstractmethod


class IStorage(ABC):
    @abstractmethod
    def list_movies(self):
        """
        Abstract class for listing movies
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def add_movie(self, title: str, year: int, rating: float, poster) -> None:
        """
        Abstract method for adding movie
        :param title:
        :type title:
        :param year:
        :type year:
        :param rating:
        :type rating:
        :param poster:
        :type poster:
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def delete_movie(self, title: str) -> None:
        """
        Remove movie from storgae
        :param title:
        :type title:
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def update_movie(self, title: str, rating: float) -> None:
        """
        Update movie in storage
        :param title:
        :type title:
        :param rating:
        :type rating:
        :return:
        :rtype:
        """
        pass
