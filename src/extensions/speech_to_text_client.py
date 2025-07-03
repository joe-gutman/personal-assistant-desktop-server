import os
import difflib
import numpy as np
import asyncio
import soundfile as sf
import librosa
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

save_dir = 'audio_logs'
os.makedirs(save_dir, exist_ok=True)

chunk_counter = 0

class STTClient:
    def __init__(self, model_size="large", device="cpu", language="en", on_transcript=None, sample_rate=48000, chunk_seconds=3, overlap_seconds=1):
        self.model = WhisperModel(model_size, device=device)
        self.language = language
        self.on_transcript = on_transcript
        self.sample_rate = sample_rate
        self.audio_buffer = bytearray()
        self.chunk_size = int(self.sample_rate * 2 * chunk_seconds)  # chunk_seconds of audio
        self.overlap_size = int(self.sample_rate * 2 * overlap_seconds)  # overlap_seconds of audioss
        self.last_text = ""
        self.listening = "STOPPED"

    def save_audio(self, pcm_bytes, sample_rate, chunk_counter, prefix="chunk", raw = False):
        if raw:
            audio_sample = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        else:
            audio_sample = pcm_bytes
        filename = os.path.join(save_dir, f'{prefix}_audio_{chunk_counter}.wav')
        sf.write(filename, audio_sample, sample_rate, subtype='PCM_16')

    def resample_audio(self, audio_np, orig_sr, target_sr=16000):
        from math import gcd
        gcd_sr = gcd(orig_sr, target_sr)
        up = target_sr // gcd_sr
        down = orig_sr // gcd_sr
        return resample_poly(audio_np, up, down)

    def transcribe_audio(self, pcm_bytes: bytes):
        self.audio_buffer.extend(pcm_bytes)
        while len(self.audio_buffer) >= self.chunk_size:
            print(f"[AUDIO] Processing chunk of size {len(self.audio_buffer)} bytes - Preview: {self.audio_buffer[:5]}...")
            chunk = self.audio_buffer[:self.chunk_size]
            self.audio_buffer = self.audio_buffer[self.chunk_size - self.overlap_size:]
            asyncio.create_task(self.process_chunk(chunk))

    def get_stable_prefix(self, prev_text, curr_text):
        prev_words = prev_text.split()
        curr_words = curr_text.split()
        matcher = difflib.SequenceMatcher(None, prev_words, curr_words)
        match = matcher.find_longest_match(0, len(prev_words), 0, len(curr_words))
        if match.size > 0 and match.a == 0 and match.b == 0:
            return " ".join(curr_words[:match.size])
        return ""

    async def process_chunk(self, chunk):
        global chunk_counter


        audio_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
        audio_np_16k = self.resample_audio(audio_np, orig_sr=48000, target_sr=16000)

        
        self.save_audio(chunk, 48000, chunk_counter, "raw", True) # save raw audio
        self.save_audio(audio_np_16k, 16000, chunk_counter, prefix="resampled") # save resampled audio
        chunk_counter += 1

        self.save_audio(audio_np_16k, 16000, chunk_counter)
        segments, _ = self.model.transcribe(audio_np, language=self.language)
        text = "".join([seg.text for seg in segments]).strip()
        print(f"[AUDIO] Raw transcribed text: {text}")
        stable_prefix = self.get_stable_prefix(self.last_text, text)
        if stable_prefix and stable_prefix != self.last_text:
            new_text = stable_prefix[len(self.last_text):].strip()
            if self.on_transcript and new_text:
                await self.on_transcript(new_text)
            self.last_text = stable_prefix

    async def start_listening(self):
        self.listening = True
        while self.listening:
            if self.audio_buffer:
                await self.process_chunk(self.audio_buffer)
                self.audio_buffer.clear()
            await asyncio.sleep(0.1)
    
    async def stop_listening(self):
        self.listening = False
        if self.audio_buffer:
            await self.process_chunk(self.audio_buffer)
            self.audio_buffer.clear()
    
    async def  get_status(self):
        return self.listening

    def stop(self):
        self.audio_buffer.clear()
