from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_random_quote():
    url = "https://api.quotable.io/random"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        quote = data["content"]
        author = data["author"]
        return f'"{quote}" - {author}'
    else:
        return "Error fetching quote"

def translate_to_spanish(text):
    url = "https://api.mymemory.translated.net/get"
    params = {'q': text, 'langpair': 'en|es'}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['responseData']['translatedText']
    else:
        return "Translation Error"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/quote')
def quote():
    quote = get_random_quote()
    translated_quote = translate_to_spanish(quote)
    return jsonify({'quote': quote, 'translated_quote': translated_quote})

if __name__ == '__main__':
    app.run(debug=True)
