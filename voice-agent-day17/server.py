import os
import asyncio
import websockets
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent, TurnEvent, TerminationEvent, StreamingError,
    StreamingClient, StreamingClientOptions, StreamingParameters,
    StreamingSessionParameters, StreamingEvents
)

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def on_begin(self, event):
    print(f"Session started: {event.id}")

def on_turn(self, event: TurnEvent):
    print(f"Transcript: {event.transcript} (end_of_turn={event.end_of_turn})")

    if event.end_of_turn and not event.turn_is_formatted:
        self.set_params(StreamingSessionParameters(format_turns=True))

    # Send transcript back to client safely from thread
    if hasattr(self, "loop") and self.loop.is_running():
        asyncio.run_coroutine_threadsafe(
            self.websocket.send(event.transcript),
            self.loop
        )

def on_terminated(self, event: TerminationEvent):
    print(f"Session terminated — processed {event.audio_duration_seconds} seconds of audio")

def on_error(self, error: StreamingError):
    print("Error occurred:", error)

async def handler(websocket):
    print("Client connected")

    client = StreamingClient(
        StreamingClientOptions(api_key=aai.settings.api_key)
    )

    # Attach loop + websocket to client so callbacks can use them
    client.websocket = websocket
    client.loop = asyncio.get_running_loop()

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    client.connect(
        StreamingParameters(sample_rate=16000, formatted_finals=True)
    )

    try:
        async for message in websocket:
            if message == "END":
                break
            client.stream(message)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        client.disconnect(terminate=True)

async def main():
    async with websockets.serve(handler, "localhost", 8000):
        print("Server listening on ws://localhost:8000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
