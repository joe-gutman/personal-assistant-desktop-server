import subprocess
import os
import logging

logger = logging.getLogger(__name__)

class TTSClient:
    def __init__(self, voice_name="en_US_amy_medium", on_speach=None):
        self.piper_path = "./piper/piper"
        self.voice_path = "./piper/voices/" + self.voice + ".onnx"
        self.process = None
        self.on_speach = on_speach
        self.start_streaming()
        
    def start_streaming(self):
        if not os.path.isfile(self.piper_path):
            logger.error(f"Piper executable not found at {self.piper_path}. Please check the path.")
            return
        if not os.path.isfile(self.voice_path):
            logger.error(f"Voice file not found at {self.voice_path}. Please check the path.")
            return
        
        logger.info(f"Starting Piper TTS with voice '{self.voice_path.split('/')[-1]}' in streaming mode.")
        self.process = subprocess.Popen(
            [self.piper_path, "--model", self.voice_path, "--stream"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            buffsize=0
        )
        logger.info("Piper streaming mode started.")
        
    def speak(self, text):
        if not self.process:
            logger.error("TTS process is not running. Please start the TTS client first.")
            return
        
        try:
            logger.info(f"Sending text to Piper: {text}")
            self.process.stdin.write((text + "\n").encode('utf-8'))
            self.process.stdin.flush()
        except Exception as e:
            logger.error(f"Error sending text to Piper: {e}")
            
        self.process.stdin.write((text.strip() + "\n").encode('utf-8'))
        self.process.stdin.flush()  
        
        raw_audio = self.process.stdout.read(22050 * 2 * 2)  # ~2s @ 22050Hz, 16-bit
        
        if self.on_speach:
            try:
                self.on_speach(raw_audio)
            except Exception as e:
                logger.error(f"Error in on_speach callback: {e}")

    def stop(self):
        if self.process:
            logger.info("Stopping Piper TTS process.")
            self.process.terminate()
            self.process.wait()
            self.process = None
            logger.info("Piper TTS process stopped.")
        else:
            logger.warning("No Piper TTS process to stop.")
            
