from quart import websocket
from src.modules.chats.models import Chat
from src.modules.chats.schemas import ChatSchema

async def chat_ws():
    data = await websocket.receive_json()
    response, status = Chat.create_chat(data)
    await websocket.send_json(ChatSchema().dump(response))