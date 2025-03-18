from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# import openai
# setx OPENAI_API_KEY "your_api_key_here" remember to do this in the terminal.
# there might be issues here with the openai library.
# pip install openai remember to do this locally beforehand. Also update requirements.txt
# from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Placeholder for MongoDB client setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client['crownbot']
# users_collection = db['users']
# chat_collection = db['chats']

# In-memory user storage for demonstration purposes
users = {}

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    # Placeholder for loading user from MongoDB
    # user_data = users_collection.find_one({"_id": user_id})
    # if user_data:
    #     return User(user_data['_id'], user_data['username'], user_data['password'])
    return users.get(user_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder for checking if username exists in MongoDB
        # if users_collection.find_one({"username": username}):
        if username in users:
            flash('Username already exists')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password, method='sha256')
        user_id = str(len(users) + 1)
        # Placeholder for inserting new user into MongoDB
        # users_collection.insert_one({"_id": user_id, "username": username, "password": hashed_password})
        users[user_id] = User(user_id, username, hashed_password)
        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder for finding user in MongoDB
        # user_data = users_collection.find_one({"username": username})
        user = next((u for u in users.values() if u.username == username), None)
        # if user_data and check_password_hash(user_data['password'], password):
        if user and check_password_hash(user.password, password):
            # Placeholder for creating User object from MongoDB data
            # user = User(user_data['_id'], user_data['username'], user_data['password'])
            login_user(user)
            return redirect(url_for('chat'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    data = request.get_json()
    messages = data.get('messages')

    # Placeholder for storing chat history in MongoDB
    # chat_collection.insert_one({"user_id": current_user.get_id(), "messages": messages})

    # Call OpenAI API to get the response
    # response = openai.ChatCompletion.create(
    #     model="gpt-4o-mini",
    #     messages=messages
    # )

    # bot_response = response.choices[0].message['content']
    bot_response = "This is a placeholder response."

    # Placeholder for storing bot response in MongoDB
    # chat_collection.update_one({"user_id": current_user.get_id()}, {"$push": {"messages": {"role": "bot", "content": bot_response}}})

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)