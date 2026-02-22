document.addEventListener('DOMContentLoaded', () => {
    
    const sendButton = document.getElementById('send-button'); 
    const userInput = document.getElementById('user-input');   
    const chatMessages = document.getElementById('chat-messages'); 
    const chatContainer = document.getElementById('chat-container');
    const inputArea = document.querySelector('.input-area');
    const footer = document.querySelector('footer');
    const header = document.querySelector('header');
    function adjustLayout() {
        const inputH = inputArea ? inputArea.offsetHeight : 0;
        const footerH = footer ? footer.offsetHeight : 0;
        const headerH = header ? header.offsetHeight : 0;
        const root = document.documentElement;
        root.style.setProperty('--input-h', `${inputH}px`);
        root.style.setProperty('--footer-h', `${footerH}px`);
        root.style.setProperty('--header-h', `${headerH}px`);
        if (chatMessages) {
            chatMessages.style.height = '';
            chatMessages.style.maxHeight = '';
        }
    }
    adjustLayout();
    window.addEventListener('resize', adjustLayout);

    let conversationHistory = [
        { role: 'system', content: [
            'You are Komo — a privacy-first multilingual AI assistant.',
            'Default: reply in English. If the user writes in another language, reply in that language.',
            'Translate only when explicitly requested; preserve meaning and tone.',
            'Avoid mixing languages; use clear, natural sentences.',
            'Keep formatting and line breaks; do not add extra commentary.'
        ].join('\\n') }
    ];

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender);
        
        const formattedText = text.split('\n').map(line => {
            if (line.trim() === '') return '<br>'; 
            return `<p>${line}</p>`; 
        }).join(''); 
        
        messageDiv.innerHTML = formattedText;
        chatMessages.appendChild(messageDiv);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
        adjustLayout();
    }

    function getLocalAIResponse(message) {
        const lowerMsg = message.toLowerCase();
        if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) return "Hello! I'm Komo AI (Offline Mode). How can I help you today?";
        if (lowerMsg.includes('help')) return "I'm here to help! Since I'm offline, I can only answer simple questions. Try asking for the time or date.";
        if (lowerMsg.includes('time')) return "The current time is " + new Date().toLocaleTimeString();
        if (lowerMsg.includes('date')) return "Today is " + new Date().toLocaleDateString();
        if (lowerMsg.includes('who are you')) return "I am Komo AI, a privacy-first assistant.";
        return "I'm currently offline, but I received your message: \"" + message + "\". Please ensure the server is running for full capabilities.";
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        
        if (text === '') return;

        addMessage(text, 'user');
        userInput.value = '';

        conversationHistory.push({ role: 'user', content: text });

        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'system');
        loadingDiv.textContent = 'Komo thinking...';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const hostname = window.location.hostname || '127.0.0.1';
        // Use 127.0.0.1 instead of localhost to avoid IPv6 issues
        const host = hostname === 'localhost' ? '127.0.0.1' : hostname;
        const port = window.location.port;
        const API_URL = port === '3040' ? '/chat' : `http://${host}:3040/chat`;

        try {
            const response = await fetch(API_URL, {
                method: 'POST', 
                headers: {
                    'Content-Type': 'application/json', 
                },
                body: JSON.stringify({ 
                    messages: conversationHistory
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            if (chatMessages.contains(loadingDiv)) chatMessages.removeChild(loadingDiv);

            if (data.error) {
                addMessage('Error: ' + data.error, 'system');
            } else {
                addMessage(data.reply, 'ai');
                conversationHistory.push({ role: 'assistant', content: data.reply });
            }

        } catch (error) {
            console.error('Error:', error);
            if (chatMessages.contains(loadingDiv)) chatMessages.removeChild(loadingDiv);
            
            // Fallback to local AI
            const localReply = getLocalAIResponse(text);
            addMessage(localReply, 'ai');
            conversationHistory.push({ role: 'assistant', content: localReply });
        }
    }

    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage(); 
        }
    });

    const saveButton = document.getElementById('save-button');
    if (saveButton) {
        saveButton.addEventListener('click', () => {
            const now = new Date();
            const header = `Komo AI — Chat Transcript\nDate: ${now.toISOString()}\n`;
            const parts = [header];
            for (let i = 1; i < conversationHistory.length; i++) {
                const msg = conversationHistory[i];
                if (msg.role === 'system') continue;
                const role = msg.role === 'user' ? 'User' : 'Komo';
                parts.push(`${role}: ${msg.content}`);
            }
            const chatHistory = parts.join('\n\n');
            const blob = new Blob([chatHistory], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
            a.download = `komo-chat-${timestamp}.txt`;
            
            document.body.appendChild(a); 
            a.click(); 
            document.body.removeChild(a); 
            URL.revokeObjectURL(url); 
        });
    }
});
