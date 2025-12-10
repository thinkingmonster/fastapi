from typing import Optional
from fastapi import Body, FastAPI
from pydantic import BaseModel,Field


class Books():
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating) -> None:
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="Not required during create operations",default=None)
    title: str = Field(min_length=5)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1,max_length=100)
    rating: int = Field(gt=0,lt=16)

    model_config={
        "json_schema_extra":{
            "example":{
                "title": "A new book",
                "author": "Add name of author",
                "description": "A new description of a book",
                "rating": 5
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
    ),
    Books(
        id=2,
        title="1984",
        author="George Orwell",
        description="Science Fiction",
        rating=5,
    ),
    Books(
        id=3,
        title="Animal Farm",
        author="George Orwell",
        description="Fiction",
        rating=5,
    ),
    Books(
        id=4,
        title="To Kill a Mockingbird",
        author="Harper Lee",
        description="Fiction",
        rating=5,
    ),
    Books(
        id=5,
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        description="Fiction",
        rating=4,
    ),
    Books(
        id=6,
        title="Harry Potter and the Sorcerer's Stone",
        author="J.K. Rowling",
        description="Fantasy",
        rating=5,
    ),
    Books(
        id=7,
        title="Harry Potter and the Chamber of Secrets",
        author="J.K. Rowling",
        description="Fantasy",
        rating=5,
    ),
    Books(
        id=8,
        title="The Hobbit",
        author="J.R.R. Tolkien",
        description="Fantasy",
        rating=5,
    ),
    Books(
        id=9,
        title="The Lord of the Rings",
        author="J.R.R. Tolkien",
        description="Fantasy",
        rating=5,
    ),
    Books(
        id=10,
        title="Clean Code",
        author="Robert C. Martin",
        description="Technology",
        rating=5,
    ),
    Books(
        id=11,
        title="The Pragmatic Programmer",
        author="Andrew Hunt",
        description="Technology",
        rating=5,
    ),
    Books(
        id=12,
        title="Sapiens",
        author="Yuval Noah Harari",
        description="Non-Fiction",
        rating=4,
    ),
    Books(
        id=13,
        title="Educated",
        author="Tara Westover",
        description="Non-Fiction",
        rating=4,
    ),
    Books(
        id=14,
        title="Brave New World",
        author="Aldous Huxley",
        description="Science Fiction",
        rating=4,
    ),
    Books(
        id=15,
        title="Dune",
        author="Frank Herbert",
        description="Science Fiction",
        rating=5,
    ),
]


app=FastAPI()

@app.get("/")
def get_books():
    return BOOKS

# @app.post("/create-book")
# async def create_book(book_request: BookRequest):
#     BOOKS.append(book_request)

@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book=Books(**book_request.model_dump())
    new_book.id = 1 if len(BOOKS)==0 else BOOKS[-1].id + 1
    BOOKS.append(new_book)

@app.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book

@app.get("/books/")
async def get_books_by_raiting(rating: int):
    books_to_return=[]
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return

# Update book
@app.put("/books/update_book")
async def update_books(book: BookRequest):
    for i,item in enumerate(BOOKS):
        if item.id ==  book.id:
           updated_book= Books(**book.model_dump())
           BOOKS[i]=updated_book
        else:
            return {"error": f"Book with id {book.id} not found."}

    return updated_book 

