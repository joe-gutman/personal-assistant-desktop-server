import os
import json
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
    def __init__(self, model="large-v2", device="cuda", language="en", on_transcript=None, sample_rate=48000):
        self.model_name = model
        self.device = device
        self.language = language
        self.on_transcript = on_transcript
        self.sample_rate = sample_rate
        self.audio_buffer = np.array([], dtype=np.int16) 
        self.last_text = ""
        self.listening = False
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            config_path = os.path.join("config", "models.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            stt_config = config.get("stt", {})
            selected_model = stt_config.get(self.model_name)

            if not selected_model:
                logger.error(f"Model '{self.model_name}' not found in config.")
                return

            model_foldername = selected_model.get("foldername")

            if not model_foldername:
                logger.error(f"No foldername specified for model '{self.model_name}'.")
                return

            model_path = os.path.join("models", "stt", model_foldername)
            self.model = WhisperModel(model_path, device=self.device)
            logger.info(f"Loaded STT model '{self.model_name}' ({model_foldername}) on device '{self.device}'")

        except FileNotFoundError:
            logger.error(f"STT configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from STT configuration file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading STT model: {e}")

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
