document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    
    // Store conversation context
    let conversationContext = {
        currentAccount: null,
        lastQuestion: null
    };

    // Function to add a message to the chat
    function addMessage(text, isUser, quickReplies = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
        
        // Process any account numbers in the message
        const processedText = text.replace(/account (\d{6})/g, '<span class="account-number">account $1</span>');
        messageDiv.innerHTML = processedText;
        
        // Add quick replies if provided and it's a bot message
        if (quickReplies && !isUser && quickReplies.length > 0) {
            const repliesDiv = document.createElement('div');
            repliesDiv.className = 'quick-replies';
            
            quickReplies.forEach(reply => {
                const replyDiv = document.createElement('div');
                replyDiv.className = 'quick-reply';
                replyDiv.textContent = reply.text;
                replyDiv.onclick = function() {
                    sendQuickReply(reply.text, reply.action);
                };
                repliesDiv.appendChild(replyDiv);
            });
            
            messageDiv.appendChild(repliesDiv);
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to hide typing indicator
    function hideTypingIndicator() {
        const typing = document.getElementById('typing');
        if (typing) {
            typing.remove();
        }
    }

    // Function to send quick reply
    window.sendQuickReply = function(text, action = null) {
        if (action) {
            // Handle special actions
            switch(action) {
                case 'set_account_123456':
                    conversationContext.currentAccount = '123456';
                    break;
                case 'set_account_654321':
                    conversationContext.currentAccount = '654321';
                    break;
                case 'clear_account':
                    conversationContext.currentAccount = null;
                    break;
            }
        }
        
        userInput.value = text;
        sendMessage();
    }

    // Function to generate appropriate quick replies based on context
    function generateQuickReplies(responseText) {
        let quickReplies = [];
        
        // Extract account number if mentioned in response
        const accountMatch = responseText.match(/account (\d{6})/);
        if (accountMatch) {
            conversationContext.currentAccount = accountMatch[1];
        }
        
        // Balance-related responses
        if (responseText.includes("balance")) {
            quickReplies = [
                { text: "Show my recent transactions", action: null },
                { text: "What's my card status?", action: null },
                { text: "Do I have any active loans?", action: null }
            ];
            
            if (!conversationContext.currentAccount) {
                quickReplies.unshift(
                    { text: "Use account 123456", action: "set_account_123456" },
                    { text: "Use account 654321", action: "set_account_654321" }
                );
            }
        } 
        // Transaction-related responses
        else if (responseText.includes("transaction") || responseText.includes("transactions")) {
            quickReplies = [
                { text: "What's my current balance?", action: null },
                { text: "How do I transfer money?", action: null },
                { text: "Where are your branches?", action: null }
            ];
        } 
        // Card-related responses
        else if (responseText.includes("card")) {
            quickReplies = [
                { text: "How do I unblock my card?", action: null },
                { text: "What's my account balance?", action: null },
                { text: "Contact customer support", action: null }
            ];
        } 
        // Loan-related responses
        else if (responseText.includes("loan") || responseText.includes("EMI")) {
            quickReplies = [
                { text: "What's my current balance?", action: null },
                { text: "Make a payment", action: null },
                { text: "View payment schedule", action: null }
            ];
        } 
        // Branch/ATM related responses
        else if (responseText.includes("branch") || responseText.includes("ATM")) {
            quickReplies = [
                { text: "What are your working hours?", action: null },
                { text: "Do you have drive-thru ATMs?", action: null },
                { text: "Nearest branch to me", action: null }
            ];
        } 
        // Default quick replies
        else {
            quickReplies = [
                { text: "What's my balance?", action: null },
                { text: "Show recent transactions", action: null },
                { text: "Card status", action: null }
            ];
            
            if (conversationContext.currentAccount) {
                quickReplies.unshift(
                    { text: "Clear account selection", action: "clear_account" }
                );
            }
        }
        
        return quickReplies;
    }

    // Function to send message to server and get response
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Store the last question asked
        conversationContext.lastQuestion = message.toLowerCase();
        
        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: message,
                context: conversationContext
            })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();
            
            // Generate context-aware quick replies
            const quickReplies = generateQuickReplies(data.response);
            
            // Add the bot's response with quick replies
            addMessage(data.response, false, quickReplies);
            
            // If it's a farewell message, disable input after a delay
            if (data.farewell) {
                setTimeout(() => {
                    userInput.disabled = true;
                    sendButton.disabled = true;
                    userInput.placeholder = "Chat session ended. Please refresh to start a new chat.";
                }, 1000);
            }
        })
        .catch(error => {
            hideTypingIndicator();
            addMessage("Sorry, I'm having trouble connecting to the server. Please try again later.", false);
            console.error('Error:', error);
        });
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Auto-focus input on page load
    userInput.focus();
    
    // Add initial quick replies
    const initialQuickReplies = [
        { text: "What's my balance for account 123456?", action: "set_account_123456" },
        { text: "Show transactions for account 654321", action: "set_account_654321" },
        { text: "Is my card active?", action: null },
        { text: "What loans do I have?", action: null }
    ];
    
    // Modify the initial bot message to include quick replies
    const initialMessage = document.querySelector('.bot-message');
    const repliesDiv = document.createElement('div');
    repliesDiv.className = 'quick-replies';
    
    initialQuickReplies.forEach(reply => {
        const replyDiv = document.createElement('div');
        replyDiv.className = 'quick-reply';
        replyDiv.textContent = reply.text;
        replyDiv.onclick = function() {
            sendQuickReply(reply.text, reply.action);
        };
        repliesDiv.appendChild(replyDiv);
    });
    
    initialMessage.appendChild(repliesDiv);
});