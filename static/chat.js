const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message');

function appendMessage(role, text) {
    const div = document.createElement('div');
    div.className = role;
    div.textContent = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function loadHistory() {
    const history = JSON.parse(sessionStorage.getItem('chatHistory') || '[]');
    history.forEach(item => appendMessage(item.role, item.text));
}

function saveMessage(role, text) {
    const history = JSON.parse(sessionStorage.getItem('chatHistory') || '[]');
    history.push({role, text});
    sessionStorage.setItem('chatHistory', JSON.stringify(history));
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;
    appendMessage('user', text);
    saveMessage('user', text);
    messageInput.value = '';
    const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({message: text})
    });
    const data = await resp.json();
    if (data.answer) {
        appendMessage('assistant', data.answer);
        saveMessage('assistant', data.answer);
    } else {
        appendMessage('error', data.error || 'Error');
    }
});

loadHistory();
