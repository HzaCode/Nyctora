from flask import Flask, render_template, jsonify
import requests
import logging
import pyphen  # For improved syllabification

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_random_quote():
    """Fetch a random English quote from an external API."""
    url = "https://api.quotable.io/random"
    try:
        response = requests.get(url, timeout=5, verify=False)  # Disable SSL verification
        response.raise_for_status()
        data = response.json()
        quote = data.get("content", "No content available")
        return quote
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching quote: {e}")
        return f"Error fetching quote: {e}"

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
        logging.error(f"Error translating text: {e}")
        return f"Error translating text: {e}"

def split_into_syllables(text):
    """Split Spanish text into syllables using pyphen."""
    dic = pyphen.Pyphen(lang='es')
    words = text.split()
    syllabified_words = [dic.inserted(word) for word in words]
    return ' '.join(syllabified_words)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/translate', methods=['GET'])
def translate():
    """API endpoint to get a random English quote, translate it to Spanish, and split into syllables."""
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

if __name__ == '__main__':
    app.run(debug=True)
