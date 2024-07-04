document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const messagesContainer = document.getElementById('messages');

    const room = 'customer_room';
    const username = 'Customer';

    let hasJoined = false;

    socket.emit('join', { room, username });

    function displayMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.textContent = text;
        messageDiv.classList.add('message');
        
        if (sender.toLowerCase() === 'customer') {
            messageDiv.classList.add('user-message');
        } else if (sender.toLowerCase() === 'system') {
            messageDiv.classList.add('system-message');
        } else {
            messageDiv.classList.add('agent-message');
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            socket.emit('message', { room, message, live_agent: false });
            userInput.value = '';
        }
    }

    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    socket.on('message', data => {
        displayMessage(data.sender, data.message);
    });

    socket.on('join', data => {
        if (!hasJoined) {
            displayMessage('system', `${data.username} has joined the room.`);
            hasJoined = true;
        }
    });

    window.addEventListener('beforeunload', () => {
        socket.emit('leave', { room, username });
    });

    // Typing indicator
    let typingTimer;
    userInput.addEventListener('input', () => {
        clearTimeout(typingTimer);
        socket.emit('typing', { room, username });
        typingTimer = setTimeout(() => {
            socket.emit('stop_typing', { room, username });
        }, 1000);
    });

    socket.on('typing', data => {
        if (data.username !== username) {
            const typingIndicator = document.createElement('div');
            typingIndicator.textContent = `${data.username} is typing...`;
            typingIndicator.classList.add('typing-indicator');
            messagesContainer.appendChild(typingIndicator);
        }
    });

    socket.on('stop_typing', data => {
        if (data.username !== username) {
            const typingIndicators = document.querySelectorAll('.typing-indicator');
            typingIndicators.forEach(indicator => indicator.remove());
        }
    });
});