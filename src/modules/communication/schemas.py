from pydantic import BaseModel
from typing import Optional, Union
from enum import Enum



class Source(str, Enum):
    CLIENT = "CLIENT"
    SERVER = "SERVER"

class MessageType(str, Enum):
    AUDIO = "AUDIO"
    TRANSCRIPT = "TRANSCRIPT"
    CHAT = "CHAT"

class AudioStatus(str, Enum):
    LISTENING = "LISTENING"
    STOPPED = "STOPPED"
    SPEAKING = "SPEAKING"

class AudioContent(BaseModel):
    status: AudioStatus
    audio: Optional[str] = None
    
class ChatContent(BaseModel):
    message: str

class Message(BaseModel):
    source: Source
    source_id: Optional[str]
    target_id: Optional[str]
    timestamp: str
    type: MessageType
    content: Union[AudioContent, ChatContent]