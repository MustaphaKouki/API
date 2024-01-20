import sqlite3

DATABASE_PATH = 'C:\\Users\\Lenovo\\Desktop\\Project\\data.db'

def create_reviews_table():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            game_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        );
        """

        cursor.execute(create_table_sql)
        conn.commit()

        print("Reviews table created successfully.")

    except sqlite3.Error as e:
        print(f"Error creating reviews table: {e}")

    finally:
        if conn:
            conn.close()

def insert_review(username, game_name, rating, comment=None):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        insert_sql = """
        INSERT INTO reviews (username, game_name, rating, comment)
        VALUES (?, ?, ?, ?)
        """

        cursor.execute(insert_sql, (username, game_name, rating, comment))
        conn.commit()

        print("Review inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error inserting review: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_reviews_table()
