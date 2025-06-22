from quart import websocket

async def audio_ws():
    print("WebSocket connected")
    try:
        while True:
            data = await websocket.receive()
            print(f"Received: {len(data)} bytes")
    except Exception as e:
        print("WebSocket connection closed:", str(e))