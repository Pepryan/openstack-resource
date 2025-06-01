// AI Chat JavaScript

let messageHistory = [];
let isLoading = false;
const CHAT_STORAGE_KEY = 'openstack_ai_chat_history';
const MAX_STORED_MESSAGES = 50; // Limit stored messages to prevent localStorage overflow

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function() {
    checkApiKeyStatus();
    setupEventListeners();
    loadChatHistory();
    updateChatStatus();
});

function setupEventListeners() {
    // Auto-resize textarea
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function checkApiKeyStatus() {
    fetch('/api/ai-chat/check-api-key')
        .then(response => response.json())
        .then(data => {
            const apiKeySection = document.getElementById('apiKeySection');
            if (data.has_api_key) {
                apiKeySection.classList.add('hidden');
            } else {
                apiKeySection.classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error checking API key status:', error);
        });
}

function saveApiKey() {
    const apiKeyInput = document.getElementById('apiKeyInput');
    const apiKey = apiKeyInput.value.trim();
    
    if (!apiKey) {
        showNotification('Please enter an API key', 'error');
        return;
    }
    
    fetch('/api/ai-chat/save-api-key', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('API key saved successfully!', 'success');
            document.getElementById('apiKeySection').classList.add('hidden');
            apiKeyInput.value = '';
        } else {
            showNotification(data.error || 'Failed to save API key', 'error');
        }
    })
    .catch(error => {
        console.error('Error saving API key:', error);
        showNotification('Error saving API key', 'error');
    });
}

function toggleApiKeySection() {
    const apiKeySection = document.getElementById('apiKeySection');
    apiKeySection.classList.toggle('hidden');
}

function sendMessage() {
    if (isLoading) return;
    
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) {
        showNotification('Please enter a message', 'error');
        return;
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Send message to AI
    isLoading = true;
    updateSendButton(true);
    
    fetch('/api/ai-chat/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingIndicator();
        
        if (data.error) {
            showNotification(data.error, 'error');
            if (data.error.includes('API key')) {
                document.getElementById('apiKeySection').classList.remove('hidden');
            }
        } else {
            addMessage(data.response, 'ai', data.timestamp);
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        hideLoadingIndicator();
        showNotification('Error communicating with AI service', 'error');
    })
    .finally(() => {
        isLoading = false;
        updateSendButton(false);
    });
}

function addMessage(content, sender, timestamp = null) {
    // Add message to DOM
    addMessageToDOM(content, sender, timestamp);
    
    // Scroll to bottom
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Store message
    const messageData = { content, sender, timestamp: timestamp || new Date().toISOString() };
    messageHistory.push(messageData);
    saveChatHistory();
    updateChatStatus();
}

function formatAIResponse(content) {
    // Convert markdown-like formatting to HTML
    let formatted = escapeHtml(content);
    
    // Convert **bold** to <strong>
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em>
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert `code` to <code>
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Convert ```code blocks``` to <pre><code>
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Convert numbered lists
    formatted = formatted.replace(/^(\d+\.)\s(.+)$/gm, '<div style="margin-left: 1rem;">$1 $2</div>');
    
    // Convert bullet points
    formatted = formatted.replace(/^[-*]\s(.+)$/gm, '<div style="margin-left: 1rem;">• $1</div>');
    
    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoadingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.className = 'message flex items-start space-x-3';
    loadingDiv.innerHTML = `
        <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <div class="loading-spinner"></div>
            </div>
        </div>
        <div class="flex-1">
            <div class="ai-message">
                <div class="text-sm typing-indicator">AI is thinking...</div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function updateSendButton(loading) {
    const sendButton = document.getElementById('sendButton');
    if (loading) {
        sendButton.disabled = true;
        sendButton.innerHTML = '<div class="loading-spinner"></div>';
    } else {
        sendButton.disabled = false;
        sendButton.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
        `;
    }
}

function askQuickQuestion(question) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = question;
    sendMessage();
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        const chatMessages = document.getElementById('chatMessages');
        // Keep only the welcome message (first child)
        const welcomeMessage = chatMessages.firstElementChild;
        chatMessages.innerHTML = '';
        if (welcomeMessage) {
            chatMessages.appendChild(welcomeMessage);
        }
        // Clear message history array and localStorage
        messageHistory = [];
        clearChatHistory();
        updateChatStatus();
        showNotification('Chat cleared', 'success');
    }
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
    
    let bgColor, textColor, icon;
    switch (type) {
        case 'success':
            bgColor = 'bg-green-500';
            textColor = 'text-white';
            icon = '✓';
            break;
        case 'error':
            bgColor = 'bg-red-500';
            textColor = 'text-white';
            icon = '✗';
            break;
        default:
            bgColor = 'bg-blue-500';
            textColor = 'text-white';
            icon = 'ℹ';
    }
    
    notification.className += ` ${bgColor} ${textColor}`;
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <span class="font-bold">${icon}</span>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

// Chat history management functions
function saveChatHistory() {
    try {
        // Keep only the last MAX_STORED_MESSAGES to prevent localStorage overflow
        const messagesToStore = messageHistory.slice(-MAX_STORED_MESSAGES);
        localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messagesToStore));
    } catch (error) {
        console.warn('Failed to save chat history to localStorage:', error);
        // If localStorage is full, try to clear old data and save again
        try {
            const recentMessages = messageHistory.slice(-20); // Keep only 20 most recent
            localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(recentMessages));
        } catch (retryError) {
            console.error('Failed to save chat history even after cleanup:', retryError);
        }
    }
}

function loadChatHistory() {
    try {
        const storedHistory = localStorage.getItem(CHAT_STORAGE_KEY);
        if (storedHistory) {
            const parsedHistory = JSON.parse(storedHistory);
            messageHistory = Array.isArray(parsedHistory) ? parsedHistory : [];
            
            // Restore messages to the chat interface
            const chatMessages = document.getElementById('chatMessages');
            messageHistory.forEach(msg => {
                addMessageToDOM(msg.content, msg.sender, msg.timestamp);
            });
            
            // Scroll to bottom if there are messages
            if (messageHistory.length > 0) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Update chat status after loading
            updateChatStatus();
        }
    } catch (error) {
        console.warn('Failed to load chat history from localStorage:', error);
        messageHistory = [];
    }
}

function clearChatHistory() {
    try {
        localStorage.removeItem(CHAT_STORAGE_KEY);
    } catch (error) {
        console.warn('Failed to clear chat history from localStorage:', error);
    }
}

// Separate function to add message to DOM without storing (used for loading history)
function addMessageToDOM(content, sender, timestamp = null) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message flex items-start space-x-3';
    
    if (sender === 'user') {
        const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div class="flex-1 flex justify-end">
                <div class="user-message">
                    <p class="text-sm">${escapeHtml(content)}</p>
                    <div class="message-timestamp text-right">
                        ${timeStr}
                    </div>
                </div>
            </div>
            <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                    </svg>
                </div>
            </div>
        `;
    } else {
        const formattedContent = formatAIResponse(content);
        const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </div>
            </div>
            <div class="flex-1">
                <div class="ai-message">
                    <div class="text-sm">${formattedContent}</div>
                    <div class="message-timestamp">
                        ${timeStr}
                    </div>
                </div>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
 }

// Update chat status display
function updateChatStatus() {
    const messageCountElement = document.getElementById('messageCount');
    const storageStatusElement = document.getElementById('storageStatus');
    
    if (messageCountElement) {
        const count = messageHistory.length;
        messageCountElement.textContent = `${count} message${count !== 1 ? 's' : ''} stored`;
    }
    
    if (storageStatusElement) {
        try {
            // Check localStorage availability and usage
            const testKey = 'test_storage';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            
            // Calculate approximate storage usage
            const chatData = localStorage.getItem(CHAT_STORAGE_KEY);
            const storageSize = chatData ? (chatData.length / 1024).toFixed(1) : '0';
            
            storageStatusElement.textContent = `${storageSize}KB stored`;
        } catch (error) {
            storageStatusElement.textContent = 'Storage unavailable';
        }
    }
}

// Export chat history as JSON file
function exportChatHistory() {
    if (messageHistory.length === 0) {
        showNotification('No chat history to export', 'error');
        return;
    }
    
    try {
        const exportData = {
            exported_at: new Date().toISOString(),
            message_count: messageHistory.length,
            messages: messageHistory,
            metadata: {
                application: 'OpenStack Resource Manager',
                version: '1.0',
                ai_model: 'Gemini 1.5 Flash'
            }
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `openstack-ai-chat-history-${new Date().toISOString().split('T')[0]}.json`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showNotification(`Exported ${messageHistory.length} messages`, 'success');
    } catch (error) {
        console.error('Failed to export chat history:', error);
        showNotification('Failed to export chat history', 'error');
    }
}

// Import chat history from JSON file (can be called manually)
function importChatHistory(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const importData = JSON.parse(e.target.result);
            
            if (importData.messages && Array.isArray(importData.messages)) {
                // Confirm import
                const confirmImport = confirm(
                    `Import ${importData.messages.length} messages?\n` +
                    `This will replace your current chat history.\n` +
                    `Exported: ${new Date(importData.exported_at).toLocaleString()}`
                );
                
                if (confirmImport) {
                    // Clear current chat
                    const chatMessages = document.getElementById('chatMessages');
                    const welcomeMessage = chatMessages.firstElementChild;
                    chatMessages.innerHTML = '';
                    if (welcomeMessage) {
                        chatMessages.appendChild(welcomeMessage);
                    }
                    
                    // Import messages
                    messageHistory = importData.messages;
                    messageHistory.forEach(msg => {
                        addMessageToDOM(msg.content, msg.sender, msg.timestamp);
                    });
                    
                    // Save and update
                    saveChatHistory();
                    updateChatStatus();
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    
                    showNotification(`Imported ${importData.messages.length} messages`, 'success');
                }
            } else {
                showNotification('Invalid chat history file format', 'error');
            }
        } catch (error) {
            console.error('Failed to import chat history:', error);
            showNotification('Failed to import chat history', 'error');
        }
    };
    reader.readAsText(file);
}

// Fullscreen functionality
let isFullscreen = false;

function toggleFullscreen() {
    const chatContainer = document.getElementById('chatContainer');
    const fullscreenIcon = document.getElementById('fullscreenIcon');
    const body = document.body;
    
    if (!isFullscreen) {
        // Enter fullscreen
        chatContainer.classList.add('chat-fullscreen');
        body.style.overflow = 'hidden';
        
        // Change icon to exit fullscreen
        fullscreenIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        `;
        
        isFullscreen = true;
        
        // Add escape key listener
        document.addEventListener('keydown', handleEscapeKey);
        
    } else {
        // Exit fullscreen
        chatContainer.classList.remove('chat-fullscreen');
        body.style.overflow = '';
        
        // Change icon back to fullscreen
        fullscreenIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
        `;
        
        isFullscreen = false;
        
        // Remove escape key listener
        document.removeEventListener('keydown', handleEscapeKey);
    }
    
    // Scroll to bottom after transition
    setTimeout(() => {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 300);
}

function handleEscapeKey(event) {
    if (event.key === 'Escape' && isFullscreen) {
        toggleFullscreen();
    }
}

// Add click outside to exit fullscreen (optional)
function handleClickOutside(event) {
    const chatContainer = document.getElementById('chatContainer');
    if (isFullscreen && !chatContainer.contains(event.target)) {
        toggleFullscreen();
    }
}