
from dataclasses import dataclass, field


@dataclass(eq=False)
class Book:
    title: str
    author: str
    isbn: str
    pages: int
    _price: float = field(repr=False)
    is_available: bool = True
    borrowers: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Title cannot be empty")

        if not self.isbn.strip():
            raise ValueError("ISBN cannot be empty")

        if type(self.pages) is not int or self.pages <= 0:
            raise ValueError("Pages must be a positive integer")

        self.price = self._price

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if type(value) not in (int, float) or value < 0:
            raise ValueError("Price must be non-negative")

        self._price = float(value)

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented

        return self.isbn == other.isbn

    def __hash__(self) -> int:
        return hash(self.isbn)

    def __len__(self) -> int:
        return self.pages
