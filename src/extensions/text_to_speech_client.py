import subprocess
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

class TTSClient:
    def __init__(self, voice_name="en_US-amy-medium", on_speach=None):
        self.piper_path = "./piper/piper"
        self.voice_path = "./piper/voices/" + voice_name + ".onnx"
        self.process = None
        self.on_speach = on_speach
        self.chunk_size = 4096
        self.start_streaming()
        
    def start_streaming(self):
        if not os.path.isfile(self.piper_path):
            logger.error(f"Piper executable not found at {self.piper_path}. Please check the path.")
            return
        if not os.path.isfile(self.voice_path):
            logger.error(f"Voice file not found at {self.voice_path}. Please check the path.")
            return
        
        logger.info(f"Starting Piper TTS with voice '{self.voice_path.split('/')[-1]}' in raw pcm streaming mode.")
        self.process = subprocess.Popen(
            [self.piper_path, "--model", self.voice_path, "--output-raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
        logger.info("Piper streaming mode started.")
        
    async def speak(self, text):
        if not self.process:
            logger.error("TTS process is not running. Please start the TTS client first.")
            return

        try:
            logger.info(f"Sending text to Piper: {text}")
            self.process.stdin.write((text.strip() + "\n").encode('utf-8'))
            self.process.stdin.flush()
            
            while True:
                chunk = await asyncio.to_thread(self.process.stdout.read, self.chunk_size)
                if not chunk:
                    break
                if self.on_speach:
                    await self.on_speach(chunk)

        except Exception as e:
            logger.error(f"Error speaking with Piper: {e}")

    def stop(self):
        if self.process:
            logger.info("Stopping Piper TTS process.")
            self.process.terminate()
            self.process.wait()
            self.process = None
            logger.info("Piper TTS process stopped.")
        else:
            logger.warning("No Piper TTS process to stop.")
            
