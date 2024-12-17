import streamlit as st
import sqlite3

# Function to create the database and table if they don't exist
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

# Call this function to create the database at the start of the app
create_db()

# Connect to the database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Function to check login credentials
def check_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password):
    # Check if the username or password is empty
    if not username or not password:
        st.warning("Username and password cannot be blank. Please create a user.")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
    count = cursor.fetchone()[0]

    if count > 0:
        st.warning("Username already exists. Please choose a different username.")
    else:
        # Insert the new user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        st.success("User registered successfully!")
    
    conn.close()

# Function to log out the user
def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.registering = False
    st.success("Logged out successfully.")

# Login page
def login_page():
    st.title("Login")

    # Show the registration form if the user is registering
    if st.session_state.get("registering", False):
        register_form()
        return  # Skip the login page while registering

    # User login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.error("Please enter both username and password.")  # Add error message if fields are empty
        else:
            user = check_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Login successful, Welcome {username}!")
                st.rerun()  # Trigger rerun to refresh the page and go to the main page
            else:
                st.error("Invalid username or password")

    if st.button("Register"):
        st.session_state.registering = True  # Track registration
        st.write("Please fill out the registration form below.")
        register_form()


def register_form():
    st.subheader("Register a new user")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register", key="register_button"):
        if new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            register_user(new_username, new_password)
            st.success("Registration successful! You can now log in.")
            st.session_state.registering = False  # End the registration state
            st.rerun()  # Refresh the page after registration

# Main app after login
def main_app():
    st.title("Welcome to the Study Question Generator")

    # Show logout button only if logged in
    if st.button("Logout", key="logout_button"):
        logout_user()
        st.rerun()  # Trigger rerun to refresh the page and go to the login page

    # Main content of the app after login
    st.write(f"Hello, {st.session_state.username}! You can now generate study questions.")
