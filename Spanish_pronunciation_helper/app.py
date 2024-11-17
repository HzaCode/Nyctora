from flask import Flask, render_template, jsonify
import requests
import logging
import pyphen
from werkzeug.serving import WSGIRequestHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Add CORS headers to allow internal network access
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

def get_random_quote():
    """Fetch a random English quote from an external API."""
    url = "https://api.quotable.io/random"
    try:
        response = requests.get(url, timeout=5, verify=False)  # Disable SSL verification
        response.raise_for_status()
        data = response.json()
        quote = data.get("content", "No content available")
        logger.info(f"Successfully fetched quote: {quote[:50]}...")
        return quote
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching quote: {e}")
        return f"Error fetching quote: {e}"

def translate_to_spanish(text):
    """Translate a given text to Spanish using an external translation API."""
    url = "https://api.mymemory.translated.net/get"
    params = {'q': text, 'langpair': 'en|es'}
    try:
        response = requests.get(url, params=params, timeout=5, verify=False)
        response.raise_for_status()
        data = response.json()
        translated_text = data['responseData']['translatedText']
        logger.info(f"Successfully translated text: {translated_text[:50]}...")
        return translated_text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error translating text: {e}")
        return f"Error translating text: {e}"

def split_into_syllables(text):
    """Split Spanish text into syllables using pyphen."""
    try:
        dic = pyphen.Pyphen(lang='es')
        words = text.split()
        syllabified_words = [dic.inserted(word) for word in words]
        return ' '.join(syllabified_words)
    except Exception as e:
        logger.error(f"Error splitting syllables: {e}")
        return text

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/translate', methods=['GET'])
def translate():
    """API endpoint to get a random English quote, translate it to Spanish, and split into syllables."""
    try:
        # Get a random English quote
        english_text = get_random_quote()
        if english_text.startswith("Error"):
            return jsonify({'error': english_text}), 500

        # Translate text to Spanish
        translated_text = translate_to_spanish(english_text)
        if translated_text.startswith("Error"):
            return jsonify({'error': translated_text}), 500

        # Split translated text into syllables
        syllables = split_into_syllables(translated_text)

        return jsonify({
            'english_text': english_text,
            'translated_text': translated_text,
            'syllables': syllables
        })
    except Exception as e:
        logger.error(f"Unexpected error in translate endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    # Enable logging for Werkzeug
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    # Configure the server to listen on all interfaces
    app.run(
        host='0.0.0.0',  # Listen on all available interfaces
        port=5000,       # Port number
        debug=True,      # Enable debug mode for development
        threaded=True    # Enable threading for better performance
    )