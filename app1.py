from flask import Flask, request, jsonify
from audio_analysis import extract_acoustic_features, classify_acoustic_features

app = Flask(__name__)

@app.route('/analyze_audio', methods=['POST'])
def analyze_audio():
    try:
        # Save uploaded audio file
        file = request.files['audio']
        file_path = f"./uploaded_audio/{file.filename}"
        file.save(file_path)

        # Extract features
        features = extract_acoustic_features(file_path)

        # Classify features
        result = classify_acoustic_features(features)

        # Return response
        return jsonify({"result": result, "features": features})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
