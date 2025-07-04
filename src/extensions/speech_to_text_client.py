import os
import difflib
import numpy as np
import asyncio
import soundfile as sf
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

save_dir = 'audio_logs'
os.makedirs(save_dir, exist_ok=True)

chunk_counter = 0


class STTClient:
    def __init__(self, model_size="large", device="cuda", language="en", on_transcript=None, sample_rate=48000, chunk_seconds=3, overlap_seconds=1):
        self.model = WhisperModel(model_size, device=device)
        self.language = language
        self.on_transcript = on_transcript
        self.sample_rate = sample_rate
        self.audio_buffer = np.array([], dtype=np.int16) 
        self.chunk_size = int(self.sample_rate * chunk_seconds) 
        self.overlap_size = int(self.sample_rate * overlap_seconds)
        self.last_text = ""
        self.listening = "STOPPED"

    def save_audio(self, audio_sample, sample_rate, chunk_counter,):
        filename = os.path.join(save_dir, f'audio_{chunk_counter}.wav')
        sf.write(filename, audio_sample, sample_rate, subtype='PCM_16')

    def resample_audio(self, audio_np, orig_sr, target_sr=16000):
        from math import gcd
        gcd_sr = gcd(orig_sr, target_sr)
        up = target_sr // gcd_sr
        down = orig_sr // gcd_sr
        return resample_poly(audio_np, up, down)

    def transcribe_audio(self, pcm_bytes: bytes):
        # Convert incoming bytes to int16 samples
        new_samples = np.frombuffer(pcm_bytes, dtype=np.int16)
        self.audio_buffer = np.concatenate((self.audio_buffer, new_samples))

    async def process_buffer(self):
        global chunk_counter
        if len(self.audio_buffer) == 0:
            return

        audio_np = self.audio_buffer.astype(np.float32) / 32768.0
        audio_np_16k = self.resample_audio(audio_np, orig_sr=self.sample_rate, target_sr=16000)
        self.save_audio(audio_np_16k, 16000, chunk_counter)
        chunk_counter += 1

        segments, _ = self.model.transcribe(audio_np, language=self.language)
        text = "".join([seg.text for seg in segments]).strip()
        print(f"[AUDIO] Raw transcribed text: {text}")
        if self.on_transcript and text:
            await self.on_transcript(text)
        self.last_text = text

    async def start_listening(self):
        self.listening = True
        self.audio_buffer = np.array([], dtype=np.int16)

    async def stop_listening(self):
        self.listening = False
        await self.process_buffer()
        self.audio_buffer = np.array([], dtype=np.int16)
    
    async def  get_status(self):
        return self.listening

    def stop(self):
        self.audio_buffer.clear()
