document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const sendButton = document.getElementById('send-button');
    const agentInput = document.getElementById('agent-input');
    const messagesContainer = document.getElementById('messages');
    const fileInput = document.getElementById('file-input');
    const attachmentButton = document.getElementById('attachment-button');
    const typingIndicator = document.getElementById('typing-indicator');

    const room = 'customer_room';
    const username = 'Agent';
    let typingTimeout;

    socket.emit('join', { room, username });

    function displayMessage(sender, text, isAgent, timestamp) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', isAgent ? 'agent' : 'user');
        
        // Adding profile picture
        const avatar = document.createElement('img');
        avatar.src = isAgent ? 'static/agent-avatar.jpg' : 'static/customer-avatar.jpg';
        avatar.alt = `${sender} Avatar`;
        avatar.classList.add('avatar');
        messageDiv.appendChild(avatar);
        
        const textContent = document.createElement('span');
        textContent.textContent = `${text}`;
        messageDiv.appendChild(textContent);

        // Adding timestamp
        const time = document.createElement('span');
        time.classList.add('timestamp');
        time.textContent = timestamp;
        messageDiv.appendChild(time);

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function sendMessage() {
        const message = agentInput.value.trim();
        if (message) {
            const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            socket.emit('message', { room, message, from_agent: true });
            
            agentInput.value = '';
        }
    }

    sendButton.addEventListener('click', sendMessage);

    agentInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form submission
            sendMessage();
        } else {
            socket.emit('typing', { room, from_agent: true });
        }
    });

    attachmentButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const base64Data = event.target.result;
                socket.emit('file', { room, file: base64Data, filename: file.name, from_agent: true });
            };
            reader.readAsDataURL(file);
        }
    });

    socket.on('message', data => {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        displayMessage(data.sender, data.message, data.sender === 'Agent', timestamp);
    });

    socket.on('typing', data => {
        if (data.from_agent !== true) {
            typingIndicator.style.display = 'flex';
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {
                typingIndicator.style.display = 'none';
            }, 1000);
        }
    });

    window.addEventListener('beforeunload', () => {
        socket.emit('leave', { room, username });
    });
});
