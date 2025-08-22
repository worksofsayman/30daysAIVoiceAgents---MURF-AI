import os
import uuid
import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# create app
app = FastAPI()

# allow client (HTML/JS) to call server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# make sure recordings dir exists
os.makedirs("recordings", exist_ok=True)


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_id = str(uuid.uuid4())[:6]
    filename = f"recordings/rec-{timestamp}-{file_id}.webm"

    print(f"[WS] Connected -> {filename}")
    total_bytes = 0

    try:
        with open(filename, "wb") as f:
            while True:
                data = await websocket.receive_bytes()
                f.write(data)
                total_bytes += len(data)
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        print(f"[WS] Disconnected. Saved {total_bytes} bytes -> {filename}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
