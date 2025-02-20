from flask import Flask, request, jsonify, render_template
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
# import openai
# setx OPENAI_API_KEY "your_api_key_here" remember to do this in the terminal.
# there might be issues here with the openai library.
# pip install openai remember to do this locally beforehand. Also update requirements.txt

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Get MongoDB URI securely
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Test MongoDB connection
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# Initialize OpenAI client
# client = OpenAI()
# openai.api_key = 'your_openai_api_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    messages = data.get('messages')

    # Call OpenAI API to get the response
    # response = openai.ChatCompletion.create(
    #     model="gpt-4o-mini",
    #     messages=messages
    # )

    # bot_response = response.choices[0].message['content']
    bot_response = "This is a placeholder response."

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)