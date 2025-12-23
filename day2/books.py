from typing import Optional
from fastapi import Path, Query, FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class Books:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date) -> None:
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(
        description="Not required during create operations", default=None
    )
    title: str = Field(min_length=5)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=16)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Add name of author",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": "Date on which this book was published",
            }
        }
    }


BOOKS = [
    Books(
        id=1,
        title="The Alchemist",
        author="Paulo Coelho",
        description="Fiction",
        rating=5,
        published_date=2015,
    ),
    Books(
        id=2,
        title="1984",
        author="George Orwell",
        description="Science Fiction",
        rating=5,
        published_date=1949,
    ),
    Books(
        id=3,
        title="Animal Farm",
        author="George Orwell",
        description="Fiction",
        rating=5,
        published_date=1945,
    ),
    Books(
        id=4,
        title="To Kill a Mockingbird",
        author="Harper Lee",
        description="Fiction",
        rating=5,
        published_date=1960,
    ),
    Books(
        id=5,
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        description="Fiction",
        rating=4,
        published_date=1925,
    ),
    Books(
        id=6,
        title="Harry Potter and the Sorcerer's Stone",
        author="J.K. Rowling",
        description="Fantasy",
        rating=5,
        published_date=1997,
    ),
    Books(
        id=7,
        title="Harry Potter and the Chamber of Secrets",
        author="J.K. Rowling",
        description="Fantasy",
        rating=5,
        published_date=1998,
    ),
    Books(
        id=8,
        title="The Hobbit",
        author="J.R.R. Tolkien",
        description="Fantasy",
        rating=5,
        published_date=1937,
    ),
    Books(
        id=9,
        title="The Lord of the Rings",
        author="J.R.R. Tolkien",
        description="Fantasy",
        rating=5,
        published_date=1954,
    ),
    Books(
        id=10,
        title="Clean Code",
        author="Robert C. Martin",
        description="Technology",
        rating=5,
        published_date=2008,
    ),
    Books(
        id=11,
        title="The Pragmatic Programmer",
        author="Andrew Hunt",
        description="Technology",
        rating=5,
        published_date=1999,
    ),
    Books(
        id=12,
        title="Sapiens",
        author="Yuval Noah Harari",
        description="Non-Fiction",
        rating=4,
        published_date=2015,
    ),
    Books(
        id=13,
        title="Educated",
        author="Tara Westover",
        description="Non-Fiction",
        rating=4,
        published_date=2018,
    ),
    Books(
        id=14,
        title="Brave New World",
        author="Aldous Huxley",
        description="Science Fiction",
        rating=4,
        published_date=1932,
    ),
    Books(
        id=15,
        title="Dune",
        author="Frank Herbert",
        description="Science Fiction",
        rating=5,
        published_date=1965,
    ),
]


app = FastAPI()


@app.get("/")
def get_books():
    return BOOKS


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Books(**book_request.model_dump())
    new_book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    BOOKS.append(new_book)
    return new_book


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with ID {book_id} not found",
    )


@app.get(
    "/books/",
    summary="Search Books by Rating and/or Publish Date",
    status_code=status.HTTP_200_OK,
)
async def get_books_by_rating(
    rating: Optional[int] = Query(default=None, gt=0, lt=16),
    publish_date: Optional[int] = Query(default=None),
):
    """
    Search for books using optional filters.

    You can filter by:
    - **rating**: Book rating (1-15)
    - **publish_date**: Year of publication (e.g., 2015)
    - **both**: Combine filters to narrow results
    """
    books_to_return = BOOKS

    # Apply rating filter if provided
    if rating:
        books_to_return = [book for book in books_to_return if book.rating == rating]

    # Apply publish_date filter if provided
    if publish_date:
        books_to_return = [
            book for book in books_to_return if book.published_date == publish_date
        ]

    return books_to_return


# Update book
@app.put(
    "/books/update_book",
    status_code=status.HTTP_200_OK,
    description="Updates a book if exists",
)
async def update_books(book: BookRequest):
    for i, item in enumerate(BOOKS):
        if item.id == book.id:
            updated_book = Books(**book.model_dump())
            BOOKS[i] = updated_book
            return updated_book

    # If we reach here, book was not found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with ID {book.id} not found",
    )


@app.delete(
    "/books/delete_book",
    description="Deletes a book based on id",
    status_code=status.HTTP_200_OK,
)
async def delete_book(id: int):
    for i, book in enumerate(BOOKS):
        if book.id == id:
            removed_item = BOOKS.pop(i)
            return {"removed": removed_item}
    raise HTTPException(status_code=404, detail=f"Book with id {id} not found")
