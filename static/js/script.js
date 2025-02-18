document.addEventListener('DOMContentLoaded', function() {
  const chatInput = document.getElementById('chatInput');
  const sendButton = document.getElementById('sendButton');
  const chatMessages = document.getElementById('chatMessages');
  let chatHistory = [];

  async function sendMessage() {
    const message = chatInput.value.trim();
    console.log('message:', message);
    if (message) {
      // Append user message to chat history
      chatHistory.push({ role: 'user', content: message });
      
      console.log('chatHistory:', chatHistory);

      // Append user message to chat window
      const userMessage = document.createElement('p');
      userMessage.classList.add('user-message');
      userMessage.innerHTML = `<strong>You:</strong> ${message}`;
      chatMessages.appendChild(userMessage);

      // Append temporary bot response to chat window
      const botMessage = document.createElement('p');
      botMessage.classList.add('bot-message');
      botMessage.innerHTML = `<strong>Bot:</strong> Processing your query...`;
      chatMessages.appendChild(botMessage);
      
      console.log('chatHistory:', chatMessages);
      
      chatInput.value = '';
      chatMessages.scrollTop = chatMessages.scrollHeight;

      try {
        // Send the chat history to the API and wait for the response
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ messages: chatHistory })
        });

        if (response.ok) {
          const data = await response.json();
          console.log('data:', data);
          console.log('data.response:', data.response);
          botMessage.innerHTML = `<strong>Bot:</strong> ${data.response}`;
          // Append bot response to chat history
          chatHistory.push({ role: 'bot', content: data.response });
          console.log('chatHistory:', chatHistory);
        } else {
          botMessage.innerHTML = `<strong>Bot:</strong> Sorry, there was an error processing your query.`;
        }
      } catch (error) {
        botMessage.innerHTML = `<strong>Bot:</strong> Sorry, there was an error processing your query.`;
      }

      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  sendButton.addEventListener('click', sendMessage);

  chatInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      sendMessage();
    }
  });
});