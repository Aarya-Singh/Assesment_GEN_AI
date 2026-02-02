const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');
const welcomeMessage = document.querySelector('.welcome-message');

// Session management
let threadId = localStorage.getItem('chat_thread_id') || 'session_' + Math.random().toString(36).substr(2, 9);
localStorage.setItem('chat_thread_id', threadId);
let chatHistory = [];

function addMessage(text, type) {
    welcomeMessage.classList.add('hidden');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const textSpan = document.createElement('span');

    // Use marked for bot messages to render markdown correctly
    if (type === 'bot') {
        textSpan.innerHTML = marked.parse(text);
    } else {
        textSpan.innerText = text;
    }

    messageDiv.appendChild(textSpan);
    messagesContainer.appendChild(messageDiv);

    // Store in history
    chatHistory.push({ role: type === 'user' ? 'user' : 'assistant', content: text });
    if (chatHistory.length > 10) chatHistory.shift();

    scrollDown();
}

function scrollDown() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(text) {
    if (!text.trim()) return;

    addMessage(text, 'user');
    userInput.value = '';

    // Show typing
    typingIndicator.classList.remove('hidden');
    scrollDown();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: text,
                thread_id: threadId,
                history: chatHistory
            })
        });

        const data = await response.json();

        // Hide typing
        typingIndicator.classList.add('hidden');

        addMessage(data.response, 'bot');
    } catch (error) {
        typingIndicator.classList.add('hidden');
        addMessage("Sorry, I'm having trouble connecting to the server.", 'bot');
    }
}

sendBtn.addEventListener('click', () => sendMessage(userInput.value));

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage(userInput.value);
});

function sendSuggestion(text) {
    sendMessage(text);
}
