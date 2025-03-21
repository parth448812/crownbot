# Maybe convert the image types to jpg or png as they are standard compared to these. 
# Also, talk to team and maybe try new theme as this might be too techy. 
# Maybe fix the 'back to home' button to be better on the chat page.
# Try testing the chatbot with the openai api key to see if you can get a response.
# show this to the guys on Tuesday during class. 


from flask import Flask, request, jsonify, render_template
# import openai
# setx OPENAI_API_KEY "your_api_key_here" remember to do this in the terminal.
# there might be issues here with the openai library.
# pip install openai remember to do this locally beforehand. Also update requirements.txt

app = Flask(__name__)



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