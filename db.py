import sqlite3
import os
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Function to create the users table with hashed passwords
def create_users_table(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        """

        cursor.execute(create_table_sql)
        conn.commit()

        print("Users table created successfully.")

    except sqlite3.Error as e:
        print(f"Error creating users table: {e}")

    finally:
        if conn:
            conn.close()

# Function to insert users into the table with hashed passwords
def insert_users(db_path, users_data):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        insert_sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        
        # Hash passwords before inserting
        hashed_users_data = [(user[0], bcrypt.generate_password_hash(user[1]).decode('utf-8')) for user in users_data]

        cursor.executemany(insert_sql, hashed_users_data)
        conn.commit()

        print("Users inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error inserting users: {e}")

    finally:
        if conn:
            conn.close()

# Specify the path for the database
db_path = os.path.join("C:\\Users\\Lenovo\\Desktop\\Project", "data.db")

# Create the users table in the specified database with hashed passwords
create_users_table(db_path)


