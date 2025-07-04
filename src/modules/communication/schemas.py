from pydantic import BaseModel
from typing import Optional
from enum import Enum

class AudioStatus(str, Enum):
    LISTENING = "LISTENING"
    STOPPED = "STOPPED"

class AudioInputMessage(BaseModel):
    status: AudioStatus 
    audio: Optional[str]