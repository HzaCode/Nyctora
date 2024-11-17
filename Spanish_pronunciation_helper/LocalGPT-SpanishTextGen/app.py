from transformers import GPTNeoForCausalLM, AutoTokenizer
import torch
import pyphen
from tqdm import tqdm
from flask import Flask, request, jsonify, render_template


app = Flask(__name__)


# choose model
# model_name = "EleutherAI/gpt-neo-125M" 
# model_name = "EleutherAI/gpt-neo-1.3B"  
model_name = "EleutherAI/gpt-neo-2.7B"  

tokenizer = AutoTokenizer.from_pretrained(model_name)

if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    tokenizer.pad_token = '[PAD]'


model = GPTNeoForCausalLM.from_pretrained(model_name)
model.resize_token_embeddings(len(tokenizer))


device = torch.device("cpu")
model.to(device)

def generate_spanish_text(prompt, min_length=500, max_length=1000):
    try:
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        inputs = inputs.to(device)

        output = model.generate(
            **inputs,
            max_length=max_length,
            min_length=min_length,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            top_k=50,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text
    except Exception as e:
        return f"Error generating Spanish text: {e}"

def split_into_syllables(text):
    try:
        dic = pyphen.Pyphen(lang='es')
        words = text.split()
        syllabified_words = [dic.inserted(word) for word in words]
        return ' '.join(syllabified_words)
    except Exception as e:
        return f"Error splitting syllables: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt', 'La importancia de la amistad')
    min_length = int(request.form.get('min_length', 500))
    max_length = int(request.form.get('max_length', 1000))
    generated_text = generate_spanish_text(prompt, min_length, max_length)
    return render_template('index.html', generated_text=generated_text)

@app.route('/syllables', methods=['POST'])
def syllables():
    text = request.form.get('text', '')
    syllabified_text = split_into_syllables(text)
    return render_template('index.html', syllables=syllabified_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
