# ShelfTrack: Bookstore Inventory Manager (Python + SQLite)

ShelfTrack is a command-line application for managing a small bookstore's inventory. It stores books and their authors in a local SQLite database and lets you add, update, delete, search and view records from an interactive menu.

## Features

- **Add a book:** enter a book ID, title, author and quantity. If the author doesn't exist yet, you are prompted to create them on the spot.
- **Update a book:** change the title, quantity, linked author, or the author's name and country. Press Enter to keep any current value.
- **Delete a book** by its ID.
- **Search for a book** by its ID and see its title and quantity.
- **View all books** with their author's name and country (uses an SQL `INNER JOIN`).
- **Input validation:** IDs must be 4-digit integers, quantities must be positive whole numbers, and text fields can't be empty. The program keeps asking until the input is valid.
- **Relational data:** a `book` table linked to an `author` table through a foreign key, with foreign key enforcement switched on.
- **Automatic setup:** the database, tables and starter data are created the first time you run the program.

## Database Design

The database file `ebookstore.db` is created automatically in the folder where you run the script.

**`author` table**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `name` | TEXT | Author's name |
| `country` | TEXT | Author's country |

**`book` table**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `title` | TEXT | Book title |
| `authorID` | INTEGER | Foreign key referencing `author(id)` |
| `qty` | INTEGER | Quantity in stock |

On first run, both tables are seeded with five authors and five books. The seed uses `INSERT OR IGNORE`, so restarting the program won't create duplicates.

## Requirements

- Python 3.6 or higher
- No external packages are needed. The script uses only the standard library (`sqlite3`).

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# 2. Run the program
python shelftrack.py
```

## Usage

When the program starts you will see this menu:

```
Select a number to do one of the following options:
        1. Enter a book
        2. Update book
        3. Delete book
        4. Search books
        5. View details of all books
        0. Exit
        :
```

| Option | What it does |
|--------|--------------|
| `1` | Add a new book (and optionally a new author) |
| `2` | Update an existing book and/or its author's details |
| `3` | Delete a book by ID |
| `4` | Look up a book by ID |
| `5` | List every book with its author and country |
| `0` | Exit the program |

### Example session

```
Please enter the 4-digit id of the book you are looking for: 3001

ID: 3001 | Title: A Tale of Two Cities | Quantity: 30
```

## Project Structure

```
.
├── shelftrack.py     # The application
├── ebookstore.db     # SQLite database (generated on first run)
└── README.md
```

## How the Code Is Organised

| Function | Purpose |
|----------|---------|
| `get_valid_id`, `get_valid_int`, `get_valid_text` | Reusable input validation helpers |
| `connect_db` | Opens the database connection and enables foreign keys |
| `create_tables`, `populate_tables` | Build the schema and insert starter data |
| `show_authors`, `add_new_author` | Author helpers used by the add and update flows |
| `add_book`, `update_book`, `delete_book`, `search_book`, `view_all_books` | The menu actions |
| `main` | Sets up the database and runs the menu loop |

Queries use parameterised statements (`?` placeholders) rather than string formatting, which protects against SQL injection.

## Things to Know

- Updating a book's author name or country changes that **author's record**, so it applies to every book linked to that author.
- Deleting a book removes it immediately, so there is no undo.
- Book and author IDs must be exactly four digits (for example `3001`).
- Searching is by ID only, not by title.


## Author

**Siboniso Zikhali**

