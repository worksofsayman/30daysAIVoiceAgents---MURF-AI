# server.py
import os
import asyncio
import json
import signal
import websockets
import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient, StreamingClientOptions,
    StreamingParameters, StreamingEvents, TurnEvent, BeginEvent, TerminationEvent, StreamingError
)

AUDIO_SAMPLE_RATE = 16000
HOST = "localhost"
PORT = 8000

API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not API_KEY:
    raise SystemExit("Set ASSEMBLYAI_API_KEY in your environment.")

# We make a per-WS-session audio queue that the SDK will consume from.
class AudioQueueStream:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.closed = False
    def __iter__(self):
        return self
    def __next__(self):
        # This is a sync iterator wrapper around async queue using loop.run_until_complete
        # but we’ll just raise to avoid usage outside the intended async runner.
        raise StopIteration("Use .aiter() via asyncio task")
    async def aiter(self):
        while not self.closed:
            chunk = await self.queue.get()
            if chunk is None:
                break
            yield bytes(chunk)

async def transcribe_and_relay(websocket, audio_queue: asyncio.Queue):
    """
    Connect to AssemblyAI, stream audio from queue, and relay turn events back to browser.
    """
    client = StreamingClient(StreamingClientOptions(api_key=API_KEY, api_host="streaming.assemblyai.com"))

    # Handlers
    def on_begin(self, event: BeginEvent):
        asyncio.create_task(websocket.send(json.dumps({"event": "info", "message": f"session: {event.id}"})))

    def on_turn(self, event: TurnEvent):
        # Relay both partial context and final turns if you want; we only finalize on end_of_turn
        asyncio.create_task(websocket.send(json.dumps({
            "event": "turn" if not event.end_of_turn else "turn_end",
            "transcript": event.transcript,
            "end_of_turn": event.end_of_turn,
            "turn_is_formatted": event.turn_is_formatted
        })))

    def on_terminated(self, event: TerminationEvent):
        asyncio.create_task(websocket.send(json.dumps({"event": "info", "message": "terminated"})))

    def on_error(self, error: StreamingError):
        asyncio.create_task(websocket.send(json.dumps({"event": "info", "message": f"error: {error}"})))

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    # Connect with required params; turns are formatted after EOT
    client.connect(StreamingParameters(sample_rate=AUDIO_SAMPLE_RATE, format_turns=True))

    # Stream audio from the browser queue
    try:
        # consume the async queue in a worker task
        async def run_stream():
            stream = AudioQueueStream(audio_queue)
            async for chunk in stream.aiter():
                client.send_audio(chunk)
        stream_task = asyncio.create_task(run_stream())
        await stream_task
    finally:
        client.disconnect(terminate=True)

async def ws_handler(websocket):
    """
    For each browser connection:
     - Create an audio queue
     - Start AssemblyAI streaming task
     - Receive binary audio frames from browser and push into queue
    """
    audio_queue: asyncio.Queue = asyncio.Queue(maxsize=32)
    relay_task = asyncio.create_task(transcribe_and_relay(websocket, audio_queue))

    try:
        async for message in websocket:
            # Browser sends PCM16 bytes (ArrayBuffer)
            if isinstance(message, (bytes, bytearray)):
                try:
                    audio_queue.put_nowait(message)
                except asyncio.QueueFull:
                    # Drop if backpressured; AssemblyAI handles small gaps
                    pass
            else:
                # Optional: control messages
                data = json.loads(message)
                if data.get("type") == "stop":
                    break
    finally:
        await audio_queue.put(None)  # signal end of stream
        with contextlib.suppress(Exception):
            await relay_task

async def main():
    print(f"WebSocket server listening at ws://{HOST}:{PORT}/stream")
    async with websockets.serve(
        ws_handler,
        HOST,
        PORT,
        ping_interval=20,
        ping_timeout=20,
        max_size=2**20,
        origins=None,
    ):
        # keep running until Ctrl+C
        stop = asyncio.Future()
        loop = asyncio.get_event_loop()
        for s in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(s, lambda: stop.done() or stop.set_result(True))
        await stop


if __name__ == "__main__":
    import contextlib
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
