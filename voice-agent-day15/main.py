from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

# HTML client with unique UI and emojis
html = """
<!DOCTYPE html>
<html>
<head>
<title>🚀 WebSocket Echo</title>
<style>
  body { font-family: 'Segoe UI', sans-serif; text-align: center; background: #1a1a2e; color: #eaeaea; }
  input { padding: 10px; width: 250px; border-radius: 8px; border: none; margin-top: 20px; }
  button { padding: 10px 20px; border-radius: 8px; border: none; background: #ff6f61; color: white; cursor: pointer; }
  ul { list-style: none; padding: 0; }
  li { margin: 10px 0; font-size: 18px; }
  .client { color: #00ffcc; }
  .server { color: #ffd700; }
</style>
</head>
<body>
<h1>🌐 WebSocket Echo 🚀</h1>
<input id="messageText" placeholder="Type a message..."/>
<button onclick="sendMessage()">📤 Send</button>
<ul id="messages"></ul>
<script>
  const ws = new WebSocket("ws://localhost:8000/ws");
  ws.onmessage = function(event) {
      const li = document.createElement('li');
      li.textContent = "🤖 Server: " + event.data;
      li.className = 'server';
      document.getElementById('messages').appendChild(li);
  };
  function sendMessage() {
      const input = document.getElementById("messageText");
      ws.send(input.value);
      const li = document.createElement('li');
      li.textContent = "🧑‍💻 You: " + input.value;
      li.className = 'client';
      document.getElementById('messages').appendChild(li);
      input.value = "";
  }
</script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"{data} ✅")