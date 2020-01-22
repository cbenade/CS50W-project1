import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Import books from csv file to database w/ SCHEMA ( isbn | title | author | year )
with open('books.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Verify that book is not already entered into database
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": row["isbn"]}).fetchone()
        if book is None:
            # Check if author is in 'authors', if not, insert author and get author_id
            author_id = db.execute("SELECT id FROM authors WHERE name = :name", {"name": row["author"]}).fetchone()
            if author_id is None:
                db.execute("INSERT INTO authors (name) VALUES (:name)", {"name": row["author"]})        
                db.commit()
                author_id = db.execute("SELECT id FROM authors WHERE name = :name", {"name": row["author"]}).fetchone()
            db.execute(
                "INSERT INTO books (isbn, title, author_id, year) VALUES (:isbn, :title, :author_id, :year)", 
                {"isbn": row["isbn"], "title": row["title"], "author_id": author_id[0], "year": row["year"]})        
            db.commit()
            print(f'entered book with title: {row["title"]}')
