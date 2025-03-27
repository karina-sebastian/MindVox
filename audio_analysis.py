<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio Analysis Tool</title>
    <style>
        /* Basic styling */
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            text-align: center;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px;
        }
        #status {
            font-size: 18px;
            margin-top: 20px;
        }
    </style>
    <script>
        let mediaRecorder;
        let audioChunks = [];

        // Start Recording function
        function startRecording() {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    mediaRecorder.start();
                    document.getElementById("status").innerText = "Recording... Please speak into the microphone.";
                    document.getElementById("recordButton").disabled = true;
                    document.getElementById("stopButton").disabled = false;
                    document.getElementById("analyseButton").disabled = true;
                })
                .catch(err => {
                    console.error("Error accessing microphone:", err);
                    document.getElementById("status").innerText = "Error accessing microphone!";
                });
        }

        // Stop Recording function
        function stopRecording() {
            mediaRecorder.stop();
            mediaRecorder.onstop = () => {
                const blob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', blob, 'session_audio.wav');

                // Send audio data to backend for analysis
                fetch('/analyse', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById("status").innerText = `Result: ${data.result}, Confidence: ${data.confidence.toFixed(2)}`;
                })
                .catch(err => {
                    console.error("Error analyzing audio:", err);
                    document.getElementById("status").innerText = "Error analyzing audio.";
                });

                document.getElementById("recordButton").disabled = false;
                document.getElementById("stopButton").disabled = true;
                document.getElementById("analyseButton").disabled = false;
            };
        }

        // Analyze Audio function - will be called after stop recording
        function analyseAudio() {
            // This function won't be used now because analysis is triggered after recording stops
        }
    </script>
</head>
<body>
    <h1>Therapy Session Audio Analysis</h1>
    <button id="recordButton" onclick="startRecording()">Start Recording</button>
    <button id="stopButton" onclick="stopRecording()" disabled>Stop Recording</button>
    <p id="status">Status: Idle</p>
</body>
</html>
