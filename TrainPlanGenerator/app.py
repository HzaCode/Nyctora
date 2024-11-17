from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import random

app = Flask(__name__)
CORS(app)

@app.route('/get_training_plan', methods=['GET'])
def get_training_plan():
    body_part = request.args.get('body_part')
    categories = {
        "chest": 10,
        "back": 12,
        "shoulders": 13,
        "legs": 9
    }

    if body_part not in categories:
        return jsonify({"error": "Invalid body part"}), 400

    category_id = categories[body_part]
    try:
        exercises_response = requests.get(
            f"https://wger.de/api/v2/exercise/?category={category_id}&language=2&limit=50",
            timeout=5  
        )
        exercises_response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch exercises", "details": str(e)}), 500

    exercises = exercises_response.json().get('results', [])
    random.shuffle(exercises)
    training_plan = []

    for exercise in exercises:
        exercise_id = exercise['id']
        try:
            images_response = requests.get(
                f"https://wger.de/api/v2/exerciseimage/?exercise={exercise_id}",
                timeout=5
            )
            images_response.raise_for_status()
        except requests.RequestException:
            continue

        images_data = images_response.json().get('results', [])
        if images_data:
            random_image = random.choice(images_data)['image']
            exercise_data = {
                "name": exercise['name'],
                "description": exercise.get('description', 'No description available'),
                "images": [random_image]  
            }
            training_plan.append(exercise_data)

        if len(training_plan) >= 6:
            break

    if len(training_plan) < 6:
        return jsonify({
            "error": "Not enough exercises with images found. Please try again."
        }), 500

    return jsonify(training_plan), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
