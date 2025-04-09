﻿from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.decimal128 import Decimal128
from dotenv import load_dotenv
import openai
import os
import re
import traceback

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Connect to MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client.get_database("CrownBot")
students_collection = db["Students"]
account_collection = db["AccountInfo"]

# Test MongoDB connection
try:
    client.admin.command('ping')
    print("\u2705 Connected to MongoDB!")
except Exception as e:
    print(f"\u274C MongoDB Connection Error: {e}")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory user store (used for Flask-Login session tracking)
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
    return users.get(user_id)

@app.before_request
def clear_session_on_restart():
    if not session.get('initialized'):
        session.clear()
        session['initialized'] = True
        session.modified = True

# ---------------- Auth Routes ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']  # student ID
        password = request.form['password']

        if account_collection.find_one({'username': username}):
            flash('Username already exists')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='sha256')
        account_collection.insert_one({'username': username, 'password': hashed_password})

        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['username']
        password = request.form['password']

        account = account_collection.find_one({'username': student_id})
        if account and check_password_hash(account['password'], password):
            student = students_collection.find_one({'StudentID': student_id}, {'_id': 0})
            if not student:
                flash("Student information not found.")
                return redirect(url_for('login'))

            student['TuitionOwed'] = float(student['TuitionOwed'].to_decimal())
            session['student_info'] = student
            session['student_verified'] = True
            session.modified = True

            user = User(str(account['_id']), student_id, account['password'])
            users[user.id] = user
            login_user(user)

            return redirect(url_for('chat'))

        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    session.modified = True
    flash("You have been logged out.")
    return redirect(url_for('home'))

# ---------------- Main Routes ----------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

# ---------------- Chat API ----------------
@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    data = request.get_json()
    messages = data.get('messages', [])
    if not messages:
        return jsonify({'response': "No messages provided."}), 400

    user_message = messages[-1]['content'].lower()

    student_info = session.get('student_info')
    if not session.get('student_verified', False) or not student_info:
        return jsonify({'response': "Please log in using your student ID before chatting."})

    if "my name" in user_message:
        return jsonify({'response': f"Your name is {student_info['FName']} {student_info['LName']}."})
    if "tuition" in user_message:
        return jsonify({'response': f"Your tuition balance is ${student_info['TuitionOwed']}."})

    memory = [{
        "role": "system",
        "content": f"User is {student_info['FName']} {student_info['LName']}, Student ID: {student_info['StudentID']}, owes ${student_info['TuitionOwed']} in tuition."
    }]

    try:
        full_messages = memory + [
            {**msg, 'role': 'assistant' if msg['role'] == 'bot' else msg['role']} for msg in messages
        ]

        print("\U0001F9E0 Sending to OpenAI:", full_messages)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=full_messages
        )

        bot_response = response.choices[0].message.content
        return jsonify({'response': bot_response})

    except Exception as e:
        traceback.print_exc()
        print("\u274C OpenAI error:", e)
        return jsonify({'response': "Sorry, there was an error processing your query."}), 500

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
