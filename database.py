import sqlite3

# Function to create the database and users table
def create_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Function to register a new user
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO users (username, password)
            VALUES (?, ?)
        ''', (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Username '{username}' is already taken.")
    finally:
        conn.close()


# Function to verify user login
def verify_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    user = c.fetchone()

    conn.close()
    return user is not None
