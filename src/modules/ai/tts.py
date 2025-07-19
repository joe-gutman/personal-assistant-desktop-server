import logging
import threading
import asyncio
import os
import json
import time
from piper.voice import PiperVoice
from piper.config import SynthesisConfig
from tqdm import tqdm

logger = logging.getLogger(__name__)

class TTS:
    def __init__(self, voice_name="emma", on_speech=None, timeout=3, voices_config=None):
        self.voice_name = voice_name
        self.voice_path = None
        self.speaker_id = None
        self.on_speech = on_speech
        self.timeout = timeout
        self.voice = None
        self.voices_config = voices_config or {}
        self.load_voice()

    def load_voice(self):
        try:
            selected_voice = self.voices_config.get(self.voice_name)

            if not selected_voice:
                logger.error(f"Voice '{self.voice_name}' not found in config.")
                return

            voice_filename = selected_voice.get("filename")
            speaker_id = selected_voice.get("speaker_id")
            
            if speaker_id is not None:
                self.speaker_id = int(speaker_id)

            if not voice_filename:
                logger.error(f"No filename specified for voice '{self.voice_name}'.")
                return
            else:
                base_dir = os.path.join("models", "voice")
                self.voice_path = os.path.join(base_dir, f"{voice_filename}.onnx")
                self.config_path = os.path.join(base_dir, f"{voice_filename}.onnx.json")

            self.voice = PiperVoice.load(self.voice_path, self.config_path)
            if not self.voice:
                logger.error(f"Failed to load voice from {self.voice_path}")
                return
            else:
                logger.info(f"Loaded Piper voice '{self.voice_name}'")

        except Exception as e:
            logger.error(f"Unexpected error loading voice: {e}")
            
    def _generate_speech(self, text):
        try:
            if self.speaker_id is not None:
                syn_config = SynthesisConfig(speaker_id=self.speaker_id)    
                for chunk in self.voice.synthesize(text, syn_config=syn_config):
                    yield chunk
            else:
                for chunk in self.voice.synthesize(text):
                    yield chunk
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")

    async def process(self, text, stream=False):
        if not stream:
            buffer = bytearray()
            
            total_audio_sec = 0.0
            wpm = 180
            word_count = len(text.split())
            expected_total_seconds = (word_count / wpm) * 60
            sample_rate = self.voice.config.sample_rate

            progress_bar = tqdm(
                total=expected_total_seconds,
                unit='s',
                desc='Generating speech',
                smoothing=0.3,
                bar_format='{l_bar}{bar}| {n:.0f}/{total:.0f} [{elapsed}<{remaining}]'
            )
            start_time = time.time()
            
            
            for chunk in self._generate_speech(text):
                if chunk is None:
                    continue
                buffer.extend(chunk.audio_int16_bytes)
                chunk_duration = len(chunk.audio_int16_bytes) / (2 * sample_rate)
                total_audio_sec += chunk_duration
                try:
                    progress_bar.update(chunk_duration)
                except TypeError:
                    pass
            end_time = time.time()
            progress_bar.close()
            rtf = (end_time - start_time) / total_audio_sec if total_audio_sec > 0 else None
            if rtf is not None:
                print(f"\nMeasured RTF: {rtf:.3f}")
            return bytes(buffer)
        
        else:
            if not self.on_speech:
                logger.warning("Streaming requested but no on_speech callback provided.")
                return
            for chunk in self._generate_speech(text):
                if chunk is None:
                    continue
                if self.on_speech:
                    await self.on_speech(bytes(chunk))
        
        
# TO DO: SEPERATE THIS INTO IT's OWN MODULE
# This script is a utility to convert text files into speech using the Piper TTS system with a chosen voice and rate of speech.

import sys
import wave
import subprocess

def save_as_wav(audio_bytes: bytes, path: str, sample_rate: int = 22050, playback_speed: float = 1.0):
    """
    Saves audio at the given playback speed.
    - If 1x speed audio doesn't exist, generate it from audio_bytes.
    - If speed ≠ 1.0, generate it using ffmpeg from the 1x file.
    """
    base_path = path.replace(".wav", "_1x.wav")
    target_path = path if playback_speed == 1.0 else path.replace(".wav", f"_{playback_speed}x.wav")

    # Only write raw audio if 1x doesn't already exist
    if not os.path.exists(base_path):
        with wave.open(base_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_bytes)
        print(f"Base 1x speed audio saved to: {base_path}")
    else:
        print(f"Found existing base audio at: {base_path}")

    # If not 1x, generate transformed speed version
    if playback_speed != 1.0:
        if not os.path.exists(target_path):
            change_audio_speed(base_path, target_path, playback_speed)
            print(f"🎵 {playback_speed}x version saved to: {target_path}")
        else:
            print(f"{playback_speed}x version already exists at: {target_path}")


def change_audio_speed(input_wav: str, output_wav: str, speed: float):
    """
    Adjusts audio speed using ffmpeg without changing pitch.
    Only accepts speeds between 0.5x and 2.0x (inclusive).
    """
    filter_str = f"atempo={speed:.2f}"
    cmd = [
        "ffmpeg", "-y", "-i", input_wav,
        "-filter:a", filter_str,
        output_wav
    ]
    subprocess.run(cmd, check=True)

def main():
    voice_name = "emma"  # High quality voice, great for reading educational content
    
    input_path = os.path.expanduser(input("Enter the full path to a text file: ").strip())
    save_folder = os.path.expanduser(input("Enter the folder to save the audio (default: current directory): ").strip() or ".")

    if not os.path.isfile(input_path):
        print(f"Invalid file path: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    config_path = "metadata/models.json"
    if not os.path.isfile(config_path):
        print(f"Missing config file at {config_path}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        voices_config = json.load(f)
    voices_config = voices_config.get("voices", {})

    tts = TTS(voice_name=voice_name, voices_config=voices_config)
    audio_data = asyncio.run(tts.process(text, stream=False))

    # Load sample rate from voice config
    voice_filename = voices_config[voice_name]["filename"]
    with open(f"models/voice/{voice_filename}.onnx.json", "r", encoding="utf-8") as f:
        voice_config = json.load(f)
    sample_rate = voice_config.get("sample_rate", 22050)

    base_txt_name = os.path.splitext(os.path.basename(input_path))[0]
    filename_base = f"{base_txt_name}_{voice_name}"

    for speed in [1.0, 1.5, 2.0]:
        output_filename = f"{filename_base}.wav"
        output_path = os.path.join(save_folder, output_filename)

        save_as_wav(audio_data, output_path, sample_rate=sample_rate, playback_speed=speed)
        print(f"Speech saved to: {output_path}")
    
if __name__ == "__main__":
    main()