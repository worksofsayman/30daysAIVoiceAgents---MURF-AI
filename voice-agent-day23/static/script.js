const startBtn = document.getElementById("startBtn");
const chat = document.getElementById("chat");

let recognition;

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
} else {
    alert("Your browser does not support Speech Recognition");
}

recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'en-US';

startBtn.addEventListener("click", () => {
    recognition.start();
});

recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    addMessage(transcript, "user");

    // send to server
    const response = await fetch("/query", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: transcript })
    });

    const data = await response.json();
    addMessage(data.reply, "bot");

    // play audio
    const audio = new Audio(data.audio_url);
    audio.play();
};

function addMessage(text, type) {
    const msg = document.createElement("div");
    msg.className = `message ${type}`;
    msg.innerText = text;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}
