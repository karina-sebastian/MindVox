from flask import Flask, render_template, request, jsonify
import numpy as np
import librosa
import os
import tensorflow as tf

app = Flask(__name__)

# Load the pre-trained model
MODEL_PATH = 'models/audio_classification_model.h5'
model = tf.keras.models.load_model(MODEL_PATH)

# Feature extraction function
def extract_acoustic_features(file_path):
    y, sr = librosa.load(file_path, sr=16000)
    features = []

    # Extract MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    features.append(np.mean(mfcc.T, axis=0))

    # Extract Chroma
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    features.append(np.mean(chroma.T, axis=0))

    # Extract Spectral Contrast
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    features.append(np.mean(spectral_contrast.T, axis=0))

    # Combine features
    return np.concatenate(features, axis=0)

# Explanation functions
def explain_depression():
    return {
        "pitch_mean": "Low pitch, lack of vocal energy.",
        "pitch_median": "Consistent low tone, lack of emotional expression.",
        "pitch_range": "Narrow range, voice lacks variation.",
        "intensity_mean": "Low intensity, speaker talks softly.",
        "speech_rate": "Slow speech, lack of motivation.",
        "silence_duration": "Longer pauses, hesitation.",
        "speaking_duration": "Shorter duration, withdrawal from conversation.",
        "mfcc": "Lower values, monotonic and flat voice.",
        "spectral_centroid": "Lower, dull and less bright voice.",
        "spectral_flux": "Low, less rapid frequency change.",
        "spectral_entropy": "Low, predictable and stable spectrum.",
        "hnr": "Lower, more noise in the voice."
    }

def explain_anxiety():
    return {
        "pitch_mean": "Higher pitch due to nervousness.",
        "pitch_median": "High tone, emotional instability.",
        "pitch_range": "Wider range, emotional fluctuations.",
        "intensity_mean": "Higher intensity, increased energy.",
        "speech_rate": "Fast, nervous speech.",
        "silence_duration": "Shorter pauses, avoidance of silence.",
        "speaking_duration": "Longer speaking durations, rambling.",
        "mfcc": "High variability, fluctuating emotions.",
        "spectral_centroid": "Higher, brighter tone.",
        "spectral_flux": "High, rapid frequency changes.",
        "spectral_entropy": "High, unpredictable speech.",
        "hnr": "Lower, more noise due to rapid vocal changes."
    }

def explain_neutral():
    return {
        "pitch_mean": "Moderate, emotionally stable.",
        "pitch_median": "Stable tone, no extremes.",
        "pitch_range": "Moderate, natural speech variation.",
        "intensity_mean": "Moderate, natural loudness.",
        "speech_rate": "Normal, steady speech.",
        "silence_duration": "Average pauses.",
        "speaking_duration": "Normal speaking time.",
        "mfcc": "Balanced, natural speech.",
        "spectral_centroid": "Moderate, clear voice.",
        "spectral_flux": "Moderate, typical speech change.",
        "spectral_entropy": "Moderate, balanced variation.",
        "hnr": "Normal, clear voice with minimal noise."
    }

@app.route('/')
def home():
    return render_template('voxtool.html')

@app.route('/analyse', methods=['POST'])
def analyse_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    file_path = os.path.join('uploaded_audio', audio_file.filename)
    audio_file.save(file_path)

    # Extract features
    features = extract_acoustic_features(file_path)
    features = features / np.max(features)  # Normalize

    # Reshape for model input
    features = features.reshape(1, -1)

    # Predict the class
    prediction = model.predict(features)
    class_idx = np.argmax(prediction)

    # Define class names
    classes = ['Anxiety', 'Depression']
    
    # Assume `prediction` contains the model's output and `classes` contains the labels.
    confidence = np.max(prediction)  # Confidence level of the prediction
    class_idx = np.argmax(prediction)

    ''' if classes[class_idx] == "depression":
       if confidence <= 0.59:
           result = "Depression"  # If it's depression and the confidence is high (>= 60%)
       else:
        result = "Neutral"  # If depression confidence is too low, consider it as "Neutral"
       elif confidence > 0.6:
        result = "Neutral"  # Neutral state if confidence is low
        else:
        result = classes[class_idx] 
       '''
       
    if confidence <= 0.59:
        result = "Depression"  # If confidence is greater than 59%, classify as Depression
    elif 0.60 <= confidence <= 0.68:
        result = "Neutral"  # If confidence is less than or equal to 60%, classify as Neutral
    else:
        result = classes[class_idx]  # For any other case, use the class label



    # Get explanation based on the result
    explanation = {}
    if result == "Depression":
        explanation = explain_depression()
    elif result == "Anxiety":
        explanation = explain_anxiety()
    elif result == "Neutral":
        explanation = explain_neutral()

    return jsonify({'result': result, 'confidence': float(confidence), 'explanation': explanation})

if __name__ == '__main__':
    if not os.path.exists('uploaded_audio'):
        os.makedirs('uploaded_audio')
    app.run(debug=True)
