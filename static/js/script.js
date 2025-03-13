document.addEventListener('DOMContentLoaded', function() {
  const chatInput = document.getElementById('chatInput');
  const sendButton = document.getElementById('sendButton');
  const chatMessages = document.getElementById('chatMessages');
  let chatHistory = [];

  async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Append user message to chat history
    chatHistory.push({ role: 'user', content: message });

    // Display user message in chat window
    const userMessage = document.createElement('p');
    userMessage.classList.add('user-message');
    userMessage.innerHTML = `<strong>You:</strong> ${message}`;
    chatMessages.appendChild(userMessage);

    // Display loading response from bot
    const botMessage = document.createElement('p');
    botMessage.classList.add('bot-message');
    botMessage.innerHTML = `<strong>Bot:</strong> Processing your query...`;
    chatMessages.appendChild(botMessage);
    
    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      // Send request to Flask backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: chatHistory })
      });

      if (response.ok) {
        const data = await response.json();
        botMessage.innerHTML = `<strong>Bot:</strong> ${data.response}`;
        
        // Append bot response to chat history as 'assistant'
        chatHistory.push({ role: 'assistant', content: data.response });
      } else {
        botMessage.innerHTML = `<strong>Bot:</strong> Error processing request.`;
      }
    } catch (error) {
      botMessage.innerHTML = `<strong>Bot:</strong> Server error. Please try again.`;
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Send message on button click
  sendButton.addEventListener('click', sendMessage);

  // Send message on pressing "Enter"
  chatInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      sendMessage();
    }
  });
});