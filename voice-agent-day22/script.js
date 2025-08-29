const playBtn = document.getElementById("playBtn");
const audioPlayer = document.getElementById("player");

playBtn.onclick = async () => {
  const ws = new WebSocket("ws://localhost:8000/ws/audio");
  const mediaSource = new MediaSource();
  audioPlayer.src = URL.createObjectURL(mediaSource);

  mediaSource.addEventListener("sourceopen", () => {
    const sourceBuffer = mediaSource.addSourceBuffer("audio/mpeg");
    ws.binaryType = "arraybuffer";

    ws.onmessage = (event) => {
      const chunk = new Uint8Array(event.data);
      sourceBuffer.appendBuffer(chunk);
    };

    ws.onclose = () => {
      console.log("Stream ended");
      mediaSource.endOfStream();
    };
  });
};
