
from abc import ABC, abstractmethod
from typing import Protocol

from library_management.models import Book


class LibraryRepository(ABC):

    @abstractmethod
    def add_book(self, book: Book) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_book(self, isbn: str) -> Book:
        raise NotImplementedError


class BookDisplay(Protocol):

    def __str__(self) -> str:
        ...
