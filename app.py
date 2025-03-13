from flask import Flask, request, jsonify, render_template, session
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import openai
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random secret key for session security

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Connect to MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client.get_database("CrownBot")
students_collection = db["Students"]

# Test MongoDB connection
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.before_request
def clear_session_on_restart():
    """Ensure that session data does not persist across application restarts."""
    if not session.get('initialized'):
        session.clear()
        session['initialized'] = True  # Prevents clearing every request

@app.route('/logout')
def logout():
    """Logs out the user by completely clearing their session data."""
    session.pop('student_info', None)  # Remove student data explicitly
    session.pop('student_verified', None)  # Remove verification flag
    session.pop('initialized', None)  # Remove session initialization flag

    return jsonify({'response': "You have been logged out. Please enter a new student ID to continue."})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    messages = data.get('messages', [])

    if not messages:
        return jsonify({'response': "No messages provided."}), 400

    user_message = messages[-1]['content'].lower()  # Get the latest user message
    
    # Extract student ID (numerical IDs like 888888888)
    student_id_match = re.search(r'\b\d{9}\b', user_message)
    student_id = student_id_match.group(0) if student_id_match else None
    
    if student_id:
        student = students_collection.find_one({"StudentID": student_id}, {"_id": 0})
        if student:
            from bson.decimal128 import Decimal128
            student['TuitionOwed'] = float(student['TuitionOwed'].to_decimal())  # Convert Decimal128 to float
            session['student_info'] = student  # Store student data in session
            session['student_verified'] = True  # Mark student as verified
            return jsonify({'response': f"Welcome, {student['FName']} {student['LName']}! How can I assist you today?"})
        else:
            return jsonify({'response': f"No student information found for ID {student_id}."})

    # Prevent access to student info if session was cleared (e.g., after logout)
    if not session.get('student_verified', False):
        return jsonify({'response': "Please enter your student ID before accessing this information."})

    student_info = session.get('student_info')

    if "my name" in user_message:
        return jsonify({'response': f"Your name is {student_info['FName']} {student_info['LName']}."})
    
    if "tuition" in user_message:
        return jsonify({'response': f"Your tuition balance is ${student_info['TuitionOwed']}."})

    try:
        # Include stored student details in the conversation context
        memory = []
        if student_info:
            memory.append({"role": "system", "content": f"User is {student_info['FName']} {student_info['LName']}, Student ID: {student_info['StudentID']}, and owes ${student_info['TuitionOwed']} in tuition."})
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=memory + [{**msg, 'role': 'assistant' if msg['role'] == 'bot' else msg['role']} for msg in messages]
        )
        
        bot_response = response.choices[0].message.content
        return jsonify({'response': bot_response})
    
    except openai.OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        if "insufficient_quota" in str(e):
            return jsonify({'response': "I'm currently out of quota. Please try again later."})
        return jsonify({'response': "Sorry, I couldn't process your request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
