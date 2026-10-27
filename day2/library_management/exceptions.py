
class LibraryError(Exception):
    pass


class BookNotFoundError(LibraryError):
    pass


class BookAlreadyExistsError(LibraryError):
    pass


class BookAlreadyBorrowedError(LibraryError):
    pass


class BookNotBorrowedError(LibraryError):
    pass
