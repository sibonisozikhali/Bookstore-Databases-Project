import sqlite3


# ===== Input validation =====
def get_valid_id(prompt):
    """Prompt the user until a valid 4-digit integer ID is entered."""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and len(value) == 4:
            return int(value)
        print(
            "\nInvalid input. ID must be a 4-digit integer"
            " (e.g. 3001). Please try again.\n"
        )


def get_valid_int(prompt):
    """Prompt the user until a valid positive integer is entered."""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and int(value) > 0:
            return int(value)
        print("\nInvalid input. Please enter a positive whole number.\n")


def get_valid_text(prompt):
    """Prompt the user until a non-empty text string is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(
            "\nInvalid input. This field cannot be left empty."
            " Please try again.\n"
        )


# ===== Database connection =====
def connect_db():
    """Return a database connection with foreign keys enabled."""
    db = sqlite3.connect('ebookstore.db')
    db.execute("PRAGMA foreign_keys = ON")
    return db


# ===== Table creation =====
def create_tables(db):
    """Create the author and book tables if they don't already exist."""
    cursor = db.cursor()

    # Author table must be created first — book references it via FOREIGN KEY
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY,
            title TEXT,
            authorID INTEGER,
            qty INTEGER,
            FOREIGN KEY (authorID) REFERENCES author(id)
        )
        '''
    )

    db.commit()


def populate_tables(db):
    """Insert initial data into author and book tables if not present."""
    cursor = db.cursor()

    # Author data inserted first so book foreign keys have valid references
    author_data = [
        (1290, 'Charles Dickens', 'England'),
        (8937, 'J.K Rowling', 'England'),
        (2356, 'C.S Lewis', 'Ireland'),
        (6380, 'J.R.R Tolkien', 'South Africa'),
        (5620, 'Lewis Carroll', 'England')
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO author (id, name, country) VALUES(?, ?, ?)',
        author_data
    )

    table_data = [
        (3001, 'A Tale of Two Cities', 1290, 30),
        (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
        (3003, 'The Lion, the Witch and the Wardrobe', 2356, 25),
        (3004, 'The Lord of the Rings', 6380, 37),
        (3005, "Alice's Adventures in the Wonderland", 5620, 12)
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO book'
        ' (id, title, authorID, qty) VALUES(?, ?, ?, ?)',
        table_data
    )

    db.commit()
    print("\nThe tables 'author' and 'book' have been populated.\n")


# ===== Helper =====
def show_authors(db):
    """Print all authors currently in the database."""
    cursor = db.cursor()
    cursor.execute('SELECT id, name, country FROM author')
    rows = cursor.fetchall()
    if rows:
        print("\nAvailable authors:")
        print("-" * 40)
        for author_id, name, country in rows:
            print(f"  ID: {author_id} | {name} ({country})")
        print("-" * 40)
    else:
        print("\nNo authors found in the database.\n")


def add_new_author(db):
    """Prompt the user for details and insert a new author."""
    cursor = db.cursor()
    print("\nNo author with that ID exists. Add a new author instead.")
    author_id = get_valid_id(
        "Enter a 4-digit ID for the new author: "
    )
    cursor.execute('SELECT id FROM author WHERE id = ?', (author_id,))
    if cursor.fetchone():
        print(
            f"\nAn author with ID '{author_id}' already exists."
            " Please use a different ID.\n"
        )
        return None
    name = get_valid_text("Enter the author's name: ")
    country = get_valid_text("Enter the author's country: ")
    cursor.execute(
        'INSERT INTO author (id, name, country) VALUES (?, ?, ?)',
        (author_id, name, country)
    )
    db.commit()
    print(f"\nAuthor '{name}' has been added with ID '{author_id}'.\n")
    return author_id


# ===== Menu options =====
def add_book(db):
    """Prompt the user for book details and insert a new book."""
    cursor = db.cursor()

    book_id = get_valid_id(
        "Please enter the 4-digit id of the book you would like to add: "
    )

    # Check if a book with this ID already exists
    cursor.execute('SELECT id FROM book WHERE id = ?', (book_id,))
    if cursor.fetchone():
        print(
            f"\nA book with id '{book_id}' already exists"
            " in the database.\n"
        )
        return

    title = get_valid_text("Please enter the title of the book: ")

    # Show existing authors so the user can pick a valid ID
    show_authors(db)
    author_id = get_valid_id(
        "Please enter the 4-digit authorID for the book: "
    )

    # If the author doesn't exist, offer to create one
    cursor.execute('SELECT id FROM author WHERE id = ?', (author_id,))
    if not cursor.fetchone():
        author_id = add_new_author(db)
        if author_id is None:
            print("\nBook was not added due to invalid author ID.\n")
            return

    qty = get_valid_int("Please enter book quantity: ")

    try:
        cursor.execute(
            'INSERT INTO book (id, title, authorID, qty) VALUES(?, ?, ?, ?)',
            (book_id, title, author_id, qty)
        )
        db.commit()
        print(
            f"\nThe book '{title}' has been successfully"
            " added to the database.\n"
        )
    except sqlite3.IntegrityError as e:
        print(f"\nDatabase error — book could not be added: {e}\n")
    except sqlite3.Error as e:
        print(f"\nUnexpected database error: {e}\n")


def update_book(db):
    """Allow the user to update a book's title, qty, authorID, or author."""
    cursor = db.cursor()

    book_id = get_valid_id(
        "Please enter the 4-digit id of the book you would like to update: "
    )

    cursor.execute(
        '''
        SELECT book.title, book.qty, author.id,
               author.name, author.country
        FROM book
        INNER JOIN author ON book.authorID = author.id
        WHERE book.id = ?
        ''',
        (book_id,)
    )

    row = cursor.fetchone()

    if not row:
        print(f"\nNo book with ID '{book_id}' was found in the database.\n")
        return

    current_title, current_qty, current_author_id, \
        current_name, current_country = row

    print(f"\nCurrent title         : {current_title}")
    print(f"Current quantity      : {current_qty}")
    print(f"Current author ID     : {current_author_id}")
    print(f"Current author name   : {current_name}")
    print(f"Current author country: {current_country}")

    # --- Book-level fields ---
    new_title = input(
        f"\nEnter new title (press Enter to keep '{current_title}'): "
    ).strip()
    new_qty_str = input(
        f"Enter new quantity (press Enter to keep '{current_qty}'): "
    ).strip()

    updated_title = new_title if new_title else current_title

    if new_qty_str:
        while not (new_qty_str.isdigit() and int(new_qty_str) > 0):
            print("\nInvalid input. Please enter a positive whole number.\n")
            new_qty_str = input(
                f"Enter new quantity"
                f" (press Enter to keep '{current_qty}'): "
            ).strip()
            if not new_qty_str:
                break
        updated_qty = int(new_qty_str) if new_qty_str else current_qty
    else:
        updated_qty = current_qty

    # --- Author ID ---
    show_authors(db)
    new_author_id_str = input(
        f"Enter new 4-digit authorID"
        f" (press Enter to keep '{current_author_id}'): "
    ).strip()

    if new_author_id_str:
        while not (new_author_id_str.isdigit()
                   and len(new_author_id_str) == 4):
            print(
                "\nInvalid input. Author ID must be a"
                " 4-digit integer.\n"
            )
            new_author_id_str = input(
                f"Enter new 4-digit authorID"
                f" (press Enter to keep '{current_author_id}'): "
            ).strip()
            if not new_author_id_str:
                break

        if new_author_id_str:
            candidate_id = int(new_author_id_str)
            cursor.execute(
                'SELECT id FROM author WHERE id = ?', (candidate_id,)
            )
            if not cursor.fetchone():
                candidate_id = add_new_author(db)
                if candidate_id is None:
                    print(
                        "\nAuthor ID was not changed"
                        " due to invalid entry.\n"
                    )
                    candidate_id = current_author_id
            updated_author_id = candidate_id
        else:
            updated_author_id = current_author_id
    else:
        updated_author_id = current_author_id

    # --- Author name / country (only for the linked author) ---
    new_name = input(
        f"Enter new author name"
        f" (press Enter to keep '{current_name}'): "
    ).strip()
    new_country = input(
        f"Enter new author country"
        f" (press Enter to keep '{current_country}'): "
    ).strip()

    updated_name = new_name if new_name else current_name
    updated_country = new_country if new_country else current_country

    try:
        cursor.execute(
            '''
            UPDATE book
            SET title = ?, qty = ?, authorID = ?
            WHERE id = ?
            ''',
            (updated_title, updated_qty, updated_author_id, book_id)
        )

        cursor.execute(
            '''
            UPDATE author
            SET name = ?, country = ?
            WHERE id = ?
            ''',
            (updated_name, updated_country, updated_author_id)
        )

        db.commit()
        print(f"\nBook ID '{book_id}' has been successfully updated.\n")

    except sqlite3.IntegrityError as e:
        print(f"\nDatabase error — book could not be updated: {e}\n")
    except sqlite3.Error as e:
        print(f"\nUnexpected database error: {e}\n")


def delete_book(db):
    """Delete a book from the database by its ID after confirming."""
    cursor = db.cursor()

    book_id = get_valid_id(
        "Please enter the 4-digit id of the book"
        " you would like to delete: "
    )

    cursor.execute('SELECT id FROM book WHERE id = ?', (book_id,))
    row = cursor.fetchone()

    if row:
        try:
            cursor.execute('DELETE FROM book WHERE id = ?', (book_id,))
            db.commit()
            print(
                f"\nThe book with id '{book_id}' has been"
                " deleted from the database.\n"
            )
        except sqlite3.Error as e:
            print(f"\nUnexpected database error: {e}\n")
    else:
        print(f"\nNo book with id '{book_id}' was found in the database.\n")


def search_book(db):
    """Search for a book by its ID and display its details if found."""
    cursor = db.cursor()

    book_id = get_valid_id(
        "Please enter the 4-digit id of the book you are looking for: "
    )

    cursor.execute(
        'SELECT id, title, qty FROM book WHERE id = ?', (book_id,)
    )
    row = cursor.fetchone()

    if row:
        print(f"\nID: {row[0]} | Title: {row[1]} | Quantity: {row[2]}\n")
    else:
        print(f"\nNo book found with id '{book_id}'.\n")


def view_all_books(db):
    """Display title, author name, and country for all books."""
    cursor = db.cursor()

    cursor.execute(
        '''
        SELECT book.title, author.name, author.country
        FROM book
        INNER JOIN author ON book.authorID = author.id
        '''
    )

    rows = cursor.fetchall()

    if rows:
        titles, author_names, author_countries = zip(*rows)
        labels = ["Title", "Author's Name", "Author's Country"]

        print("\nDetails")
        for title, name, country in zip(
            titles, author_names, author_countries
        ):
            print("-" * 50)
            for label, value in zip(labels, [title, name, country]):
                print(f"{label}: {value}")
        print("-" * 50)

    else:
        print("\nNo books found in the database.\n")


# ===== Main menu =====
def main():
    """Main entry point: set up the database and run the menu loop."""
    with connect_db() as db:
        create_tables(db)
        populate_tables(db)

        while True:
            try:
                menu = int(input(
                    '\nSelect a number to do one of the following options:\n'
                    '        1. Enter a book\n'
                    '        2. Update book\n'
                    '        3. Delete book\n'
                    '        4. Search books\n'
                    '        5. View details of all books\n'
                    '        0. Exit\n'
                    '        : '
                ))

                if menu == 1:
                    add_book(db)
                elif menu == 2:
                    update_book(db)
                elif menu == 3:
                    delete_book(db)
                elif menu == 4:
                    search_book(db)
                elif menu == 5:
                    view_all_books(db)
                elif menu == 0:
                    print("\nGoodbye!!!")
                    break
                else:
                    print(
                        "\nYou have entered an invalid input."
                        " Please try again.\n"
                    )

            except ValueError:
                print("\nPlease enter a valid number.\n")


if __name__ == "__main__":
    main()
