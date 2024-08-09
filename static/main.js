(function() {
    const chatMessages = document.querySelector('.chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const bookRecommendations = document.querySelector('.book-recommendations');
    const loadingIndicator = document.querySelector('.loading-indicator');
    const errorMessage = document.querySelector('.error-message');

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function showLoading() {
        loadingIndicator.style.display = 'block';
    }

    function hideLoading() {
        loadingIndicator.style.display = 'none';
    }

    function showError(message) {
        hideLoading();
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    async function fetchChatResponse(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching chat response:', error);
            throw error;
        }
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            chatInput.value = '';
            showLoading();

            try {
                const data = await fetchChatResponse(message);
                const aiResponse = data.response;
                const books = data.books;

                // Display user message
                displayMessage('User', message);

                // Display AI response
                displayMessage('AI', aiResponse);

                // Display book recommendations
                displayBookRecommendations(books);
            } catch (error) {
                showError('An error occurred while processing your request. Please try again later.');
            } finally {
                hideLoading();
            }
        }
    }

    function displayMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function displayBookRecommendations(books) {
        bookRecommendations.innerHTML = '';
        books.forEach(book => {
            const bookElement = document.createElement('div');
            bookElement.className = 'book-item';
            bookElement.innerHTML = `
                <h3>${book.title}</h3>
                <p><strong>Author:</strong> ${book.author}</p>
                <p><strong>Price:</strong> ${book.price}</p>
                ${book.imageUrl ? `<img src="${book.imageUrl}" alt="${book.title}">` : ''}
            `;
            bookRecommendations.appendChild(bookElement);
        });
    }
})();
