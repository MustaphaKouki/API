import sqlite3
from flask_bcrypt import Bcrypt

DATABASE = 'C:\\Users\\Lenovo\\Desktop\\Project\\data.db'
bcrypt = Bcrypt()

def get_db():
    db = sqlite3.connect(DATABASE)
    return db

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def insert_reviews():
    users = [
        {"username": "john_doe", "password": "johns_password"},
        {"username": "alice_smith", "password": "alices_password"},
        {"username": "bob_jones", "password": "bobs_password"},
    ]

    games_reviews = [
        {"game_name": "Fifa23", "reviews": [{"username": "john_doe", "rating": 8, "review": "Enjoyable game."},
                                             {"username": "alice_smith", "rating": 7, "review": "Great graphics."},
                                             {"username": "bob_jones", "rating": 9, "review": "Love the gameplay."}]},
        {"game_name": "AssassinsCreed", "reviews": [{"username": "john_doe", "rating": 9, "review": "Awesome storyline."},
                                                      {"username": "alice_smith", "rating": 8, "review": "Exciting missions."},
                                                      {"username": "bob_jones", "rating": 7, "review": "Could be more challenging."}]},
        {"game_name": "Cyberpunk2077", "reviews": [{"username": "john_doe", "rating": 6, "review": "Mixed feelings."},
                                                     {"username": "alice_smith", "rating": 5, "review": "Needs more optimization."},
                                                     {"username": "bob_jones", "rating": 7, "review": "Interesting concept."}]},
        {"game_name": "TheWitcher3", "reviews": [{"username": "john_doe", "rating": 9, "review": "Masterpiece."},
                                                   {"username": "alice_smith", "rating": 8, "review": "Captivating story."},
                                                   {"username": "bob_jones", "rating": 9, "review": "Must-play RPG."}]},
        {"game_name": "RedDeadRedemption2", "reviews": [{"username": "john_doe", "rating": 10, "review": "Outstanding."},
                                                         {"username": "alice_smith", "rating": 9, "review": "Immersive open world."},
                                                         {"username": "bob_jones", "rating": 8, "review": "Great character development."}]},
    ]

    conn = get_db()
    cursor = conn.cursor()

    for user in users:
        hashed_password = hash_password(user["password"])
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                       (user["username"], hashed_password))

    for game_review in games_reviews:
        game_name = game_review["game_name"]
        reviews = game_review["reviews"]

        for review in reviews:
            username = review["username"]
            rating = review["rating"]
            review_text = review["review"]

            cursor.execute("INSERT INTO reviews (username, game_name, rating, review) VALUES (?, ?, ?, ?)",
                           (username, game_name, rating, review_text))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    insert_reviews()
    print("Users and reviews inserted successfully.")
