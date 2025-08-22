import asyncio
import websockets
import base64

# WebSocket handler
async def send_audio(websocket, path=None):  # make path optional
    print("🎧 Client connected, streaming audio...")

    # Load a sample audio file
    with open("sample.wav", "rb") as f:
        audio_bytes = f.read()

    # Convert to base64
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    # Break into chunks and stream
    chunk_size = 5000
    for i in range(0, len(audio_b64), chunk_size):
        chunk = audio_b64[i:i+chunk_size]
        await websocket.send(chunk)
        print(f"📤 Sent chunk {i // chunk_size + 1}")
        await asyncio.sleep(0.05)  # simulate streaming

    print("✅ Streaming finished!")

# Main entry point
async def main():
    async with websockets.serve(send_audio, "localhost", 8765):  # pass function, not call
        print("🚀 WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # keep server alive

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
