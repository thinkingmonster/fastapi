from sre_parse import SUCCESS
from fastapi import Body, FastAPI

books = [
    {"title": "The Alchemist", "author": "Paulo Coelho", "category": "Fiction"},
    {"title": "1984", "author": "George Orwell", "category": "Science Fiction"},
    {"title": "Animal Farm", "author": "George Orwell", "category": "Fiction"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "Fiction"},
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "category": "Fiction",
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "category": "Fantasy",
    },
    {
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J.K. Rowling",
        "category": "Fantasy",
    },
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "category": "Fantasy"},
    {
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "category": "Fantasy",
    },
    {"title": "Clean Code", "author": "Robert C. Martin", "category": "Technology"},
    {
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "category": "Technology",
    },
    {"title": "Sapiens", "author": "Yuval Noah Harari", "category": "Non-Fiction"},
    {"title": "Educated", "author": "Tara Westover", "category": "Non-Fiction"},
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "category": "Science Fiction",
    },
    {"title": "Dune", "author": "Frank Herbert", "category": "Science Fiction"},
]

app = FastAPI()


@app.get("/books")
async def get_books(category: str = None):
    if category:
        return [
            book
            for book in books
            if book.get("category").casefold() == category.casefold()
        ]
    return (books, len(books))


# Path parameter example
@app.get("/books/{book_title}")
async def get_book(book_title: str, category: str = None):
    for book in books:
        if book.get("title").casefold() == book_title.casefold():
            print(book["title"].casefold())
            return book
    return "Book not found"


# Query parameter
@app.get("/books/search/")
async def search(author: str = None, category: str = None):
    books_to_return = books
    if author:
        books_to_return = [
            book
            for book in books_to_return
            if book.get("author").casefold() == author.casefold()
        ]
    if category:
        books_to_return = [
            book
            for book in books_to_return
            if book.get("category").casefold() == category.casefold()
        ]
    return books_to_return


@app.post("/books/create")
async def create_book(new_book=Body()):
    books.append(new_book)


@app.put("/books/update")
async def update_book(update=Body()):
    for i, book in enumerate(books):
        if book.get("title").casefold() == update.get("title").casefold():
            books[i] = update
            return {"message": "Book updated successfully", "book": update}

    return {"error": "Book not found"}


@app.delete("/books/delete")
async def update_book(update=Body()):
    for i, book in enumerate(books):
        if book.get("title").casefold() == update.get("title").casefold():
            books.pop(i)
            return {"message": "Book dropped  successfully", "book": update}
    return {"error": "Book not found"}
