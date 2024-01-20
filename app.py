import sqlite3
from flask import Flask, request, jsonify, g, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
import requests

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret_key'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

DATABASE = 'C:\\Users\\Lenovo\\Desktop\\Project\\data.db'

@app.route('/')
def index():
    return render_template('index.html')

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close database connection on app context teardown
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to authenticate user credentials
def authenticate(username, password):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[2], password):
            return {'user_id': user[0], 'username': user[1]}, True
        else:
            return None, False

    except sqlite3.Error as e:
        print(f'Error: {e}')
        return None, False

# Registration route
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required!'}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return jsonify({'message': 'Username already taken. Choose a different username.'}), 400

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        insert_sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        cursor.execute(insert_sql, (username, password_hash))
        conn.commit()

        return jsonify({'message': 'Registration successful!'})

    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'Error: {e}'}), 500

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required!'}), 400

        user, is_authenticated = authenticate(username, password)

        if is_authenticated:
            access_token = create_access_token(identity=user['username'])
            return jsonify({'message': 'Login successful!', 'access_token': access_token})
        else:
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'message': f'Error: {e}'}), 500

# Route to get game information
@app.route('/game-info/<game_name>', methods=['GET'])
@jwt_required()
def get_game_info(game_name):
    app.logger.info(f"Received request for game: {game_name}")
    
    try:
        api_url = f'https://api.rawg.io/api/games'
        params = {
            'key': '9a9a1713a1014000b4a288e8cd18697f',
            'search': game_name,
        }

        response = requests.get(api_url, params=params)
        data = response.json()

        if 'results' in data and data['results']:
            game_info = {
                'name': data['results'][0]['name'],
                'platforms': [{'-': platform['platform']['name']} for platform in data['results'][0]['platforms']],
                'genres': [{'-': genre['name']} for genre in data['results'][0]['genres']],
                'release_date': data['results'][0]['released'],
            }

            return jsonify({'game_info': game_info})
        else:
            return jsonify({'message': 'No results found for the specified game name'})

    except Exception as e:
        return jsonify({'message': f'Error: {e}'}), 500

# Route to add a review
@app.route('/add_review', methods=['POST'])
@jwt_required()
def add_review():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        game_name = data.get('game_name')
        rating = data.get('rating')
        review_text = data.get('review')

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO reviews (username, game_name, rating, review) VALUES (?, ?, ?, ?)",
                       (current_user, game_name, rating, review_text))
        conn.commit()

        conn.close()

        return jsonify({'message': 'Review added successfully'})

    except sqlite3.Error as e:
        return jsonify({'message': f'Error: {e}'}), 500

# Route to update a review
@app.route('/update_review/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        new_rating = data.get('rating')
        new_review = data.get('review')

        user, is_authenticated = authenticate(username, password)

        if not is_authenticated or user['username'] != username:
            return jsonify({'message': 'Invalid username or password.'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM reviews WHERE id=?", (review_id,))
        review_owner = cursor.fetchone()

        if not review_owner or review_owner[0] != username:
            return jsonify({'message': 'You are not allowed to update this review.'}), 403

        cursor.execute("UPDATE reviews SET rating=?, review=? WHERE id=?", (new_rating, new_review, review_id))
        conn.commit()

        conn.close()

        return jsonify({'message': 'Review updated successfully'})

    except sqlite3.Error as e:
        return jsonify({'message': f'Error: {e}'}), 500

# Route to delete a review
@app.route('/delete_review/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user, is_authenticated = authenticate(username, password)

        if not is_authenticated or user['username'] != username:
            return jsonify({'message': 'Invalid username or password.'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM reviews WHERE id=?", (review_id,))
        review_owner = cursor.fetchone()

        if not review_owner or review_owner[0] != username:
            return jsonify({'message': 'You are not allowed to delete this review.'}), 403

        cursor.execute("DELETE FROM reviews WHERE id=?", (review_id,))
        conn.commit()

        conn.close()

        return jsonify({'message': 'Review deleted successfully'})

    except sqlite3.Error as e:
        return jsonify({'message': f'Error: {e}'}), 500

# Route to get reviews by game
@app.route('/reviews/<game_name>', methods=['GET'])
@jwt_required()
def get_reviews_by_game(game_name):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT username, rating, review FROM reviews WHERE game_name=?", (game_name,))
        reviews = cursor.fetchall()

        conn.close()

        return jsonify({'reviews': reviews})

    except sqlite3.Error as e:
        return jsonify({'message': f'Error: {e}'}), 500

# Route to get average rating and message
@app.route('/average_rating/<game_name>', methods=['GET'])
@jwt_required()
def get_average_rating(game_name):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT AVG(rating) FROM reviews WHERE game_name=?", (game_name,))
        average_rating = cursor.fetchone()[0]

        conn.close()

        message = f"The average rating for {game_name} is {average_rating:.2f}."

        if average_rating >= 9.0:
            message += " Outstanding! This game is a masterpiece that captivates players with its exceptional qualities."
        elif 7.0 <= average_rating < 9.0:
            message += " Excellent! Players highly appreciate the quality and enjoyment provided by this game."
        elif 5.0 <= average_rating < 7.0:
            message += " Good. The game has positive aspects, but there is room for improvement."
        else:
            message += " Needs improvement. The game has received mixed reviews, and enhancements may be beneficial."

        return jsonify({'message': message, 'average_rating': average_rating})

    except sqlite3.Error as e:
        return jsonify({'message': f'Error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
