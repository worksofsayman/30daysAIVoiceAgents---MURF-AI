from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(html_code)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Voice Agent - Echo Bot</title>
    <style>
        body {
            background: #0f2027;
            background: linear-gradient(to right, #2c5364, #203a43, #0f2027);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #00ffe7;
            text-shadow: 0 0 10px #00ffe7;
        }

        .section {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
            width: 90%;
            max-width: 600px;
            margin-bottom: 2rem;
        }

        button {
            padding: 10px 20px;
            margin: 10px;
            background-color: #00ffe7;
            border: none;
            border-radius: 5px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #00b3a4;
        }

        audio {
            margin-top: 1rem;
            width: 100%;
        }

        .footer {
            margin-top: auto;
            font-size: 0.9rem;
            color: #ccc;
        }
    </style>
</head>
<body>
    <h1>🎤 Echo Bot</h1>
    <div class="section">
        <p>Click "Start Recording", say something, then click "Stop Recording". Your voice will be echoed back!</p>
        <button id="startBtn">Start Recording</button>
        <button id="stopBtn" disabled>Stop Recording</button>
        <audio id="audioPlayback" controls></audio>
    </div>

    <div class="footer">Day 4 of 30 Days of AI Voice Agents</div>

    <script>
        let mediaRecorder;
        let audioChunks = [];

        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const audioPlayback = document.getElementById('audioPlayback');

        startBtn.onclick = async () => {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = e => {
                audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayback.src = audioUrl;
                audioPlayback.play();
                audioChunks = [];
            };

            mediaRecorder.start();
            startBtn.disabled = true;
            stopBtn.disabled = false;
        };

        stopBtn.onclick = () => {
            mediaRecorder.stop();
            startBtn.disabled = false;
            stopBtn.disabled = true;
        };
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
