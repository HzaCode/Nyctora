from flask import Flask, render_template, jsonify
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_random_quote():
    """Fetch a random quote from an external API."""
    url = "https://api.quotable.io/random"
    try:
        response = requests.get(url, timeout=5, verify=False)  # Disable SSL verification
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
        quote = data.get("content", "No content available")
        author = data.get("author", "Unknown")
        return f'"{quote}" - {author}'
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching quote: {e}")
        return "Error fetching quote"

def translate_to_spanish(text):
    """Translate a given text to Spanish using an external translation API."""
    url = "https://api.mymemory.translated.net/get"
    params = {'q': text, 'langpair': 'en|es'}
    try:
        response = requests.get(url, params=params, timeout=5, verify=False)  # Disable SSL verification
        response.raise_for_status()
        data = response.json()
        translated_text = data['responseData']['translatedText']
        return translated_text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error translating quote: {e}")
        return "Error translating quote"

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/quote')
def quote():
    """API endpoint to get a random quote and its Spanish translation."""
    quote = get_random_quote()
    translated_quote = translate_to_spanish(quote)
    return jsonify({'quote': quote, 'translated_quote': translated_quote})

if __name__ == '__main__':
    app.run(debug=True)
