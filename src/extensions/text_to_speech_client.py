import logging
import threading
import asyncio
import os
import json
from piper.voice import PiperVoice

logger = logging.getLogger(__name__)

class TTSClient:
    def __init__(self, voice_name="emma", on_speach=None, timeout=3):
        self.voice_name = voice_name
        self.voice_path = None
        self.speaker_id = None
        self.on_speach = on_speach
        self.timeout = timeout
        self.voice = None
        self.load_voice()

    def load_voice(self):
        try:
            config_path = os.path.join("config", "models.json")
            abs_config_path = os.path.abspath(config_path)
            logger.debug(f"Trying to open config at: {abs_config_path}")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            voices_config = config.get("voices", {})
            selected_voice = voices_config.get(self.voice_name)

            if not selected_voice:
                logger.error(f"Voice '{self.voice_name}' not found in config.")
                return

            voice_filename = selected_voice.get("filename")
            speaker_id = selected_voice.get("speaker_id")

            if not voice_filename:
                logger.error(f"No filename specified for voice '{self.voice_name}'.")
                return
            else:
                base_dir = os.path.join("models", "voice")
                self.voice_path = os.path.join(base_dir, f"{voice_filename}.onnx")
                self.config_path = os.path.join(base_dir, f"{voice_filename}.onnx.json")
            
            if not speaker_id:
                logger.error(f"No speaker ID specified for voice '{self.voice_name}'.")
                return
            else: 
                self.speaker_id = speaker_id

            self.voice = PiperVoice.load(self.voice_path, self.config_path)
            logger.info(f"Loaded Piper voice '{self.voice_name}' with speaker ID: {self.speaker_id}")

        except FileNotFoundError as e:
            logger.error(f"File not found: {e.filename}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from voice configuration file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading voice: {e}")

    async def speak(self, text):
        if not self.voice:
            logger.error("Voice model not loaded.")
            return

        logger.info(f"Synthesizing and streaming: {text}")

        try:
            for chunk in self.voice.synthesize(text):
                if self.on_speach:
                    await self.on_speach(chunk)
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")

    def stop(self):
        # No process to stop; included for API compatibility
        logger.info("TTSClient stopped (no process to terminate).")