import logging
import asyncio
import os
import json
from piper.voice import PiperVoice

logger = logging.getLogger(__name__)

class TTSClient:
    def __init__(self, voice_name="jarvis-high", on_speach=None, timeout=3):
        self.voice_name = voice_name
        self.on_speach = on_speach
        self.timeout = timeout
        self.voice = None
        self.load_voice()

    def load_voice(self):
        try:
            config_path = os.path.join("config", "voices.json")
            with open(config_path, "r", encoding="utf-8") as f:
                self.voices = json.load(f)
                
            try:
                for name, alias in self.voices.items():
                    if self.voice_name == alias:
                        self.voice_name = name
                        break
                model_path = os.path.join("voices", self.voice_name + ".onnx")
                config_path = os.path.join("voices", self.voice_name + ".onnx.json")
                self.voice = PiperVoice.load(model_path, config_path)
                logger.info(f"Loaded Piper voice: {self.voice_name}")
            except Exception as e:
                logger.error(f"Failed to load Piper voice: {e}")
        except FileNotFoundError:
            logger.error(f"Voice configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from voice configuration file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading voice: {e}")

    async def speak(self, text):

        if not self.voice:
            logger.error("Voice model not loaded.")
            return

        logger.info(f"Synthesizing and streaming: {text}")

        def generate_chunks():
            # This is a blocking generator
            return list(self.voice.synthesize_stream_raw(text))

        try:
            chunks = await asyncio.to_thread(generate_chunks)
            for chunk in chunks:
                if self.on_speach:
                    if asyncio.iscoroutinefunction(self.on_speach):
                        await self.on_speach(chunk)
                    else:
                        self.on_speach(chunk)
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")

    def stop(self):
        # No process to stop; included for API compatibility
        logger.info("TTSClient stopped (no process to terminate).")