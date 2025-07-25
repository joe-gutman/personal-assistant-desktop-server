from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class TTSStatus(str, Enum):
    GENERATING = "GENERATING"
    STREAMING = "STREAMING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class STTStatus(str, Enum):
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class AudioMessage(BaseModel):
    audio: bytes = Field(..., description="Raw audio data in bytes")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    speed: float = Field(default=1.0, description="Playback speed multiplier")
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    speaker_id: Optional[int] = Field(default=None, description="Speaker ID for multi-speaker voices")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")

    @validator('duration', always=True)
    def calculate_duration(cls, v, values):
        """Auto-calculate duration from audio data and sample rate."""
        if v is None and 'audio' in values and 'sample_rate' in values:
            audio = values['audio']
            sample_rate = values['sample_rate']
            if audio and sample_rate:
                return len(audio) / (2 * sample_rate)
        return v

    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        if v <= 0:
            raise ValueError("Sample rate must be positive")
        return v

    @validator('speed')
    def validate_speed(cls, v):
        if v <= 0:
            raise ValueError("Speed must be positive")
        return v


class TranscriptMessage(BaseModel):
    text: str = Field(..., description="Transcribed text")
    confidence: Optional[float] = Field(default=None, description="Transcription confidence score")
    language: Optional[str] = Field(default="en", description="Detected/specified language")
    status: STTStatus = Field(default=STTStatus.COMPLETED, description="STT processing status")


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    speed: float = Field(default=1.0, description="Speech speed multiplier")
    speaker_id: Optional[int] = Field(default=None, description="Speaker ID for multi-speaker voices")


class LLMResponse(BaseModel):
    text: str = Field(..., description="Generated response text")
    model: Optional[str] = Field(default=None, description="Model used for generation")
    confidence: Optional[float] = Field(default=None, description="Response confidence score")
    processing_time: Optional[float] = Field(default=None, description="Generation time in seconds")


class TTSResult(BaseModel):
    """Result from TTS processing - can hold both audio data and metadata"""
    audio: bytes = Field(..., description="Generated audio data")
    sample_rate: int = Field(..., description="Audio sample rate")
    speed: float = Field(default=1.0, description="Speech speed used")
    voice: str = Field(..., description="Voice used for synthesis")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")
    
    @validator('duration', always=True)
    def calculate_duration(cls, v, values):
        """Auto-calculate duration from audio data and sample rate."""
        if v is None and 'audio' in values and 'sample_rate' in values:
            audio = values['audio']
            sample_rate = values['sample_rate']
            if audio and sample_rate:
                return len(audio) / (2 * sample_rate)
        return v
        
