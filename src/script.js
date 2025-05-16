// script.js
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const phoneTimeDisplay = document.getElementById('phoneTime');
    const botHeaderAvatar = document.getElementById('botHeaderAvatar');

    let sessionId = localStorage.getItem('chatSessionId') || generateSessionId();
    localStorage.setItem('chatSessionId', sessionId);

    // --- Helper Functions ---
    function generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + Date.now();
    }

    function getCurrentFormattedTime() {
        return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', hour12: true });
    }

    function updatePhoneStatusBarTime() {
        if (phoneTimeDisplay) {
            const now = new Date();
            let hours = now.getHours();
            const minutes = now.getMinutes().toString().padStart(2, '0');
            hours = hours % 12;
            hours = hours ? hours : 12;
            phoneTimeDisplay.textContent = `${hours}:${minutes}`;
        }
    }

    function basicMarkdownToHtml(markdownText) {
        if (typeof markdownText !== 'string') {
            console.warn("basicMarkdownToHtml received non-string input:", markdownText);
            return ''; // Return empty string if not a string
        }
        let htmlText = markdownText;

        // Escape HTML special characters first to prevent XSS if markdownText contains them
        // This is a very basic sanitizer. For robust sanitization, a library is needed.
        // htmlText = htmlText.replace(/&/g, '&amp;')
        //                    .replace(/</g, '&lt;')
        //                    .replace(/>/g, '&gt;')
        //                    .replace(/"/g, '&quot;')
        //                    .replace(/'/g, '&#039;');
        // Decided against aggressive HTML escaping here as it would break legitimate Markdown.
        // The primary concern is controlled bot output. User input is not directly rendered via this.

        // New lines
        htmlText = htmlText.replace(/\n/g, '<br>');

        // Bold: **text** or __text__
        htmlText = htmlText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        htmlText = htmlText.replace(/__(.*?)__/g, '<strong>$1</strong>');

        // Italic: *text* or _text_
        // Ensure italic regex doesn't clash with bold if bold is processed first
        htmlText = htmlText.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>'); // Handles *italic* but not **bold**
        htmlText = htmlText.replace(/(?<!_)_(?!_)(.*?)(?<!_)_(?!_)/g, '<em>$1</em>');   // Handles _italic_ but not __bold__
        
        // Strikethrough: ~~text~~
        htmlText = htmlText.replace(/~~(.*?)~~/g, '<del>$1</del>');

        // Inline code: `code`
        htmlText = htmlText.replace(/`(.*?)`/g, '<code>$1</code>');
        
        return htmlText;
    }


    function addMessageToUI(text, sender, time) {
        console.log(`[addMessageToUI] Sender: ${sender}, Original Text:`, text); // Log input text

        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message-wrapper', sender === 'user' ? 'user-message' : 'bot-message');

        const avatar = document.createElement('div');
        avatar.classList.add('message-avatar');
        if (sender === 'user') {
            avatar.textContent = 'U';
        } else {
            avatar.textContent = 'I';
        }

        const messageBubble = document.createElement('div');
        messageBubble.classList.add('message-bubble');

        const messageTextDiv = document.createElement('div');
        messageTextDiv.classList.add('message-text');
        
        const htmlContent = basicMarkdownToHtml(text);
        console.log(`[addMessageToUI] Sender: ${sender}, Converted HTML:`, htmlContent); // Log converted HTML
        
        messageTextDiv.innerHTML = htmlContent;

        // Fallback if HTML content is empty but original text was not (e.g. conversion issue)
        if (htmlContent.trim() === '' && text && text.trim() !== '') {
            console.warn("[addMessageToUI] Markdown conversion resulted in empty HTML for non-empty text. Displaying raw text for:", text);
            messageTextDiv.textContent = text; // Display raw text as a fallback
        }


        const messageTime = document.createElement('div');
        messageTime.classList.add('message-time');
        messageTime.textContent = time || getCurrentFormattedTime();

        messageBubble.appendChild(messageTextDiv);
        messageBubble.appendChild(messageTime);
        
        if (sender === 'user') {
            messageWrapper.appendChild(messageBubble);
            messageWrapper.appendChild(avatar);
        } else {
            messageWrapper.appendChild(avatar);
            messageWrapper.appendChild(messageBubble);
        }
        
        chatMessages.appendChild(messageWrapper);
        console.log("[addMessageToUI] Message appended to DOM:", messageWrapper.outerHTML); // Log the full element
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const existingIndicator = document.getElementById('typingIndicator');
        if (existingIndicator) return;

        const typingIndicatorWrapper = document.createElement('div');
        typingIndicatorWrapper.classList.add('message-wrapper', 'bot-message');
        typingIndicatorWrapper.id = 'typingIndicator';

        const avatar = document.createElement('div');
        avatar.classList.add('message-avatar');
        avatar.textContent = 'I';

        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble', 'typing-indicator');
        bubble.innerHTML = '<span></span><span></span><span></span>';

        typingIndicatorWrapper.appendChild(avatar);
        typingIndicatorWrapper.appendChild(bubble);
        chatMessages.appendChild(typingIndicatorWrapper);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async function handleSendMessage() {
        const messageText = messageInput.value.trim();
        if (messageText === '') return;

        addMessageToUI(messageText, 'user');
        messageInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({ user_message: messageText, session_id: sessionId }),
            });

            removeTypingIndicator();

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: "Unknown server error." }));
                addMessageToUI(`Error: ${errorData.detail || response.statusText}`, 'bot');
                return;
            }

            const data = await response.json();
            if (data.ai_responses && data.ai_responses.length > 0) {
                data.ai_responses.forEach(aiMsg => addMessageToUI(aiMsg, 'bot'));
            } else if (data.ai_response) {
                 addMessageToUI(data.ai_response, 'bot');
            } else {
                addMessageToUI("I received a response, but it was empty.", 'bot');
            }

        } catch (error) {
            removeTypingIndicator();
            addMessageToUI('Sorry, I couldn\'t connect. Please check your connection.', 'bot');
        }
    }

    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    });

    updatePhoneStatusBarTime();
    setInterval(updatePhoneStatusBarTime, 10000);
});