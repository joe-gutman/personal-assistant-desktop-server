import os
import numpy as np
import soundfile as sf
import logging
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

logger = logging.getLogger(__name__)

save_dir = 'audio_logs'
os.makedirs(save_dir, exist_ok=True)

chunk_counter = 0


class STTClient:
    def __init__(self, model_size="large-v2", device="cuda", language="en", on_transcript=None, sample_rate=48000):
        self.model = WhisperModel(model_size, device=device)
        self.language = language
        self.on_transcript = on_transcript
        self.sample_rate = sample_rate
        self.audio_buffer = np.array([], dtype=np.int16) 
        self.last_text = ""
        self.listening = False

        logger.debug(f"STTClient initialized with model '{model_size}' on device '{device}' for language '{language}'.")

    @property
    def status(self):
        return self.listening

    def save_audio(self, audio_sample, sample_rate, chunk_counter):
        filename = os.path.join(save_dir, f'audio_{chunk_counter}.wav')
        sf.write(filename, audio_sample, sample_rate, subtype='PCM_16')
        logger.debug(f"Saved audio chunk to {filename}")

    def resample_audio(self, audio_np, orig_sr, target_sr=16000):
        from math import gcd
        gcd_sr = gcd(orig_sr, target_sr)
        up = target_sr // gcd_sr
        down = orig_sr // gcd_sr
        logger.debug(f"Resampling audio from {orig_sr} Hz to {target_sr} Hz.")
        return resample_poly(audio_np, up, down)

    def transcribe_audio(self, pcm_bytes: bytes):
        new_samples = np.frombuffer(pcm_bytes, dtype=np.int16)
        self.audio_buffer = np.concatenate((self.audio_buffer, new_samples))
        logger.debug(f"Appended {len(new_samples)} samples to audio buffer (total: {len(self.audio_buffer)} samples).")

    async def process_buffer(self):
        global chunk_counter

        if len(self.audio_buffer) == 0:
            logger.debug("Audio buffer is empty, skipping processing.")
            return

        audio_np = self.audio_buffer.astype(np.float32) / 32768.0
        audio_np_16k = self.resample_audio(audio_np, orig_sr=self.sample_rate, target_sr=16000)

        # Uncomment this if you want to save audio during debugging
        # self.save_audio(audio_np_16k, 16000, chunk_counter)

        chunk_counter += 1

        try:
            segments, _ = self.model.transcribe(audio_np_16k, language=self.language)
            text = "".join([seg.text for seg in segments]).strip()
            logger.info(f"Transcribed text: {text}")

            if self.on_transcript and text:
                await self.on_transcript(text)

            self.last_text = text
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)

    async def start_listening(self):
        self.listening = True
        self.audio_buffer = np.array([], dtype=np.int16)
        logger.debug("STT client started listening.")

    async def stop_listening(self):
        self.listening = False
        logger.debug("STT client stopped listening. Processing buffer...")
        await self.process_buffer()
        self.audio_buffer = np.array([], dtype=np.int16)

    def stop(self):
        self.audio_buffer.clear()
        logger.debug("Audio buffer manually cleared.")
