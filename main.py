import logging
import os
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)

# Fetch API credentials from environment variables
RAKUTEN_APP_ID = os.environ['RAKUTEN_APP_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    logging.info(f"Received message: {user_message}")

    # Get a book suggestion from ChatGPT (using OpenAI)
    chatgpt_response = get_chatgpt_suggestion(user_message)
    book_title = chatgpt_response.get('title')

    # Fetch the first relevant result from Rakuten API using the book title
    books = fetch_books_from_rakuten(book_title)

    return jsonify({
        'response': chatgpt_response.get('response'),
        'books': books
    })

def get_chatgpt_suggestion(query):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=100,
            n=1,
            stop=None,
        )

        logging.info(f"ChatGPT API Response: {response}")

        suggestion = response.choices[0].message.content.strip()

        logging.info(f"ChatGPT Suggestion: {suggestion}")

        if '"' in suggestion:
            book_title = suggestion.split('"')[1]
        else:
            book_title = suggestion

        return {
            'response': f"Here's a suggestion: {suggestion}",
            'title': book_title
        }

    except Exception as e:
        logging.error(f"Error interacting with OpenAI: {e}")
        return {
            'response': "Sorry, I couldn't fetch a suggestion at the moment.",
            'title': None
        }

def fetch_books_from_rakuten(book_title):
    if not book_title:
        return []

    # URL-encode the book title
    keyword = book_title.replace(' ', '%20')

    params = {
        'applicationId': RAKUTEN_APP_ID,
        'format': 'json',
        'keyword': keyword,
        'booksGenreId': '000',  # Genre ID for all genres
        'hits': 1  # Number of results to return
    }

    logging.info(f"Fetching books from Rakuten with title: {book_title}")

    try:
        response = requests.get('https://app.rakuten.co.jp/services/api/BooksTotal/Search/20170404', params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        logging.info(f"Rakuten API Response: {data}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from Rakuten API: {e}")
        return []

    items = data.get('Items', [])

    if items:
        first_item = items[0].get('Item', {})
        return [{
            'title': first_item.get('title'),
            'author': first_item.get('author'),
            'imageUrl': first_item.get('largeImageUrl'),
            'price': first_item.get('itemPrice'),
            'url': first_item.get('itemUrl')  # Adding URL of the book
        }]

    return []

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
