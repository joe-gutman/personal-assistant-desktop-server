import logging
import threading
import asyncio
import os
import json
import time
from piper.voice import PiperVoice
from piper.config import SynthesisConfig
from tqdm import tqdm
from .schemas import AudioMessage, TTSResult


logger = logging.getLogger(__name__)

        
class TTS:
    def __init__(self, voice_name: str = "emma", on_speech: callable = None, config_path: str = "metadata/models.json", worker_count: int = 1):
        self.voice_name = voice_name
        self.speaker_id = None
        self.on_speech = on_speech
        self.voices_config = self._load_config(config_path)
        self.voice = self._load_voice(voice_name)
        
    @staticmethod
    def _format_text_for_tts(text: str) -> str:
        """
        Ensures each non-empty line ends with a punctuation mark to add natural pauses in spoken language (defaults to a period).
        Joins all lines into a single string separated by spaces.
        """
        lines = text.splitlines()
        formatted_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("...")  # Represent empty line with a pause
                continue
            if not stripped.endswith(('.', '!', '?', ',', ';', ':')):
                stripped += '.'
            formatted_lines.append(stripped)
        return ' '.join(formatted_lines)
    
    def _load_config(self, config_path):
        if not os.path.isfile(config_path):
            logger.error(f"Missing config file at {config_path}")
            return {}

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        voices = config.get("voices")
        if not voices:
            logger.error("No 'voices' key found in config.")
            return {}

        return voices

    def _load_voice(self, voice_name=None):
        selected_voice = self.voices_config.get(voice_name)
        if not selected_voice:
            logger.error(f"Voice '{voice_name}' not found in config.")
            return None

        voice_filename = selected_voice.get("filename")
        speaker_id = selected_voice.get("speaker_id")

        if not voice_filename:
            logger.error(f"No filename specified for voice '{voice_name}'.")
            return None

        base_dir = os.path.join("models", "voice")
        voice_path = os.path.join(base_dir, f"{voice_filename}.onnx")
        config_path = os.path.join(base_dir, f"{voice_filename}.onnx.json")

        try:
            voice = PiperVoice.load(voice_path, config_path)
            logger.info(f"Loaded Piper voice '{voice_name}'")

            # Set speaker_id only for the default voice
            if voice_name == self.voice_name:
                self.speaker_id = speaker_id

            return voice
        except Exception as e:
            logger.error(f"Failed to load voice '{voice_name}': {e}")
            return None
            
    def _generate_speech(self, text: str, config: SynthesisConfig, voice: PiperVoice = None):
        if voice is None:
            voice = self.voice
        try:
            for chunk in voice.synthesize(text, syn_config=config):
                yield chunk
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
            

    async def process(self, inputs=None, voice_name=None, speaker_id=None) -> None:
        if not isinstance(inputs, list):
            logger.error("Inputs must be a list of dictionaries.")
            return

        for idx, item in enumerate(inputs, 1):
            text = self._format_text_for_tts(item.get("text", ""))
            speed = item.get("speed", 1.0)
            item_voice_name = item.get("voice_name", voice_name or self.voice_name)

            # Load voice if it has changed
            if item_voice_name != self.voice_name:
                self.voice_name = item_voice_name
                self.voice = self._load_voice(self.voice_name)
                self.speaker_id = self.voices_config.get(self.voice_name, {}).get("speaker_id", self.speaker_id)

            if not self.on_speech:
                logger.warning("Streaming requested but no on_speech callback provided.")
                return

            syn_config = SynthesisConfig(
                speaker_id=self.speaker_id,
                length_scale=round(1.0 / speed, 3),
            )

            for chunk in self._generate_speech(text, config=syn_config):
                if chunk is None:
                    continue

                message = AudioMessage(
                    audio=chunk.audio_int16_bytes,
                    sample_rate=self.voice.config.sample_rate,
                    voice=self.voice_name,
                    speaker_id=self.speaker_id
                )
                await self.on_speech(message)

        
# TO DO: 
#  - Seperate the following code into a seperate script that can be run independently by the AI.
# This script is a utility to convert text files into speech using the Piper TTS system with a chosen voice and rate of speech.

def main():
    import subprocess
    from tqdm import tqdm
    import time
    voices = ["wendy"]
    speed = 1.6
    input_path = "/home/joegutman/documents/class/Introduction_to_Systems_Thinking_and_Applications_D459/text/Chapter_01_Systems_Thinking_and_Applications_D459_no_html_simplified.txt"
    save_folder = "/home/joegutman/documents/class/Introduction_to_Systems_Thinking_and_Applications_D459/audio"

    if not os.path.isfile(input_path):
        print(f"Invalid file path: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    for voice_name in voices:
        base_txt_name = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{base_txt_name}_{voice_name}_streamed.mp3"
        output_path = os.path.join(save_folder, output_filename)

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        word_count = len(text.split())
        wpm = 180
        estimated_duration = (word_count / wpm) * 60  # in seconds

        audio_process = None
        progress_bar = None

        async def on_speech(msg):
            nonlocal audio_process, progress_bar
            if audio_process is None:
                audio_process = subprocess.Popen(
                    [
                        "ffmpeg", "-y",
                        "-f", "s16le", "-ar", str(msg.sample_rate), "-ac", "1", "-i", "pipe:0",
                        "-codec:a", "libmp3lame", "-b:a", "96k",
                        output_path
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                progress_bar = tqdm(
                    total=estimated_duration,
                    unit='s',
                    desc="Streaming",
                    smoothing=0.3,
                    dynamic_ncols=True,
                    leave=True,
                    bar_format='{l_bar}{bar}| {n:.0f}/{total:.0f} [{elapsed}<{remaining}]'
                )

            chunk_duration = len(msg.audio) / (2 * msg.sample_rate)
            if progress_bar.n + chunk_duration <= progress_bar.total:
                progress_bar.update(chunk_duration)
            else:
                progress_bar.update(progress_bar.total - progress_bar.n)

            audio_process.stdin.write(msg.audio)

        tts = TTS(voice_name=voice_name, on_speech=on_speech)

        inputs = [{
            "text": text,
            "speed": speed,
            "voice_name": voice_name
        }]

        start = time.time()
        asyncio.run(tts.process(inputs=inputs))
        duration = time.time() - start

        if audio_process:
            audio_process.stdin.close()
            audio_process.wait()
        if progress_bar:
            progress_bar.close()

        print(f"Saved in {duration:.2f} seconds.")
        print(f"Speech saved to: {output_path}")



if __name__ == "__main__":
    main()