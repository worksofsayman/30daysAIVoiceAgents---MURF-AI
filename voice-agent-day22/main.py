from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn, asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def get_index():
    return FileResponse("index.html")

async def audio_streamer(websocket: WebSocket):
    with open("sample.mp3", "rb") as f:
        while chunk := f.read(4096):
            await websocket.send_bytes(chunk)
            await asyncio.sleep(0.1)
    await websocket.close()

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await audio_streamer(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
