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


class Message(dict):
    def __init__(self, audio: bytes = None, sample_rate: int = None, speed: float = 1.0, voice: str = None, speaker_id: int = None):
        # Validate required fields
        if audio is None:
            raise ValueError("Audio Message: Audio is required.")
        if sample_rate is None:
            raise ValueError("Audio Message: Sample rate is required.")

        super().__init__(
            audio=audio,
            sample_rate=sample_rate,
            speed=speed,  
            duration=len(audio) / (2 * sample_rate) if audio else 0,
            voice= voice,
            speaker_id=speaker_id
        )

        
class TTS:
    def __init__(self, voice_name: str = "emma", on_speech: callable = None, config_path: str = "metadata/models.json", worker_count: int = 1):
        self.voice_name = voice_name
        self.speaker_id = None
        self.on_speech = on_speech
        self.voices_config = self._load_config(config_path)
        self.voice = self._load_voice(voice_name)
        
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
            
    def _generate_speech(self, text: str, speed: float = 1.0, voice: PiperVoice = None, speaker_id: int = None):
        if voice is None:
            voice = self.voice
            
        try:
            length_scale = round(1.0 / speed, 3)

            syn_config = SynthesisConfig(
                speaker_id= speaker_id or self.speaker_id,
                length_scale=length_scale,
                noise_scale=0.6,
                noise_w_scale=0.8
            )

            for chunk in voice.synthesize(text, syn_config=syn_config):
                yield chunk
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")

    async def process(self, text=None, voice_name=None, speaker_id=None, inputs=None, stream=False):      
        if stream and inputs:
            logger.error("Streaming mode does not support multiple inputs.")
            return None
        
        if inputs is None:
            if not text:
                logger.error("No text provided for TTS processing.")
                return None
            inputs = [{
                "text": text,
                "speed": 1.0,
                "voice_name": voice_name or self.voice_name,
                "speaker_id": speaker_id or self.speaker_id
            }]
        elif not isinstance(inputs, list):
            logger.error("Inputs must be a list of dictionaries.")
            return None
        
        if stream:
            if text is None:
                logger.error("Streaming mode requires text to generate audio.")
            if voice_name is not None and voice_name != self.voice_name:
                self.voice_name = voice_name
                speaker_id = speaker_id or self.speaker_id
                self.voice = self._load_voice(voice_name, speaker_id)
                
            if not self.on_speech:
                logger.warning("Streaming requested but no on_speech callback provided.")
                return
            for chunk in self._generate_speech(text):
                if chunk is None:
                    continue
                if self.on_speech:
                    message = Message(
                        audio=bytes(chunk),
                        sample_rate=self.voice.config.sample_rate,
                        voice=self.voice_name,
                        speaker_id=self.speaker_id
                    )
                    await self.on_speech(message)             
        else:
            sample_rate = self.voice.config.sample_rate
            start_time = time.time()
            
            messages = []

            for idx, item in enumerate(inputs, 1):
                full_audio = bytearray()
                text = item.get("text", "")
                speed = item.get("speed", 1.0)
                voice_name = item.get("voice_name", self.voice_name)
                speaker_id = item.get("speaker_id", self.speaker_id)
                
                task_voice = self.voice
                if voice_name != self.voice_name:
                    task_voice = self._load_voice(voice_name, speaker_id)

                if idx > 1:
                    print()
                    
                word_count = len(text.split())
                wpm = 180
                expected_seconds = (word_count / wpm) * 60 / speed

                progress_bar = tqdm(
                    total=expected_seconds,
                    unit='s',
                    desc=f"Processing {idx}/{len(inputs)}",
                    smoothing=0.3,
                    bar_format='{l_bar}{bar}| {n:.0f}/{total:.0f} [{elapsed}<{remaining}]'
                )

                for chunk in self._generate_speech(text, speed=speed, voice=task_voice, speaker_id=speaker_id):
                    if chunk is None:
                        continue
                    full_audio.extend(chunk.audio_int16_bytes)
                    chunk_duration = len(chunk.audio_int16_bytes) / (2 * sample_rate)
                    try:
                        progress_bar.update(chunk_duration)
                    except TypeError:
                        pass
                
                progress_bar.close()
                
                messages.append(Message(
                    speed=speed,
                    audio=bytes(full_audio),
                    sample_rate=sample_rate,
                    voice=voice_name,
                    speaker_id=speaker_id
                ))

            end_time = time.time()
        return messages
        
        
# TO DO: SEPERATE THIS INTO IT's OWN MODULE
# This script is a utility to convert text files into speech using the Piper TTS system with a chosen voice and rate of speech.

import sys
import wave
import subprocess

def save_as_wav(audio_bytes: bytes, path: str, sample_rate: int = 22050):
    """
    Saves audio at the given playback speed.
    - If 1x speed audio doesn't exist, generate it from audio_bytes.
    - If speed ≠ 1.0, generate it using ffmpeg from the 1x file.
    """
    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)


def main():
    voice_name = "emma"  # High quality voice, great for reading educational content
    speaker_id = None  # Default speaker ID, can be set to a specific ID if needed
    
    # input_path = os.path.expanduser(input("Enter the full path to a text file: ").strip())
    # save_folder = os.path.expanduser(input("Enter the folder to save the audio (default: current directory): ").strip() or ".")
    input_path = "/home/joegutman/class/Introduction_to_Systems_Thinking_and_Applications_D459/text/Chapter_01_Systems_Thinking_and_Applications_D459_formatted_formatted.txt"
    save_folder = "/home/joegutman/class/Introduction_to_Systems_Thinking_and_Applications_D459/audio"


    if not os.path.isfile(input_path):
        print(f"Invalid file path: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    tts = TTS(voice_name=voice_name)
    
    inputs = []
    for speed in [1.0, 1.5, 2.0]:
        inputs.append({
            "text": text,
            "speed": speed,
            "voice_name": voice_name,
            "speaker_id": speaker_id
        })
        
    results = asyncio.run(tts.process(inputs=inputs, stream=False))
    for result in results:
        # Extract audio data and other parameters from the results
        audio_data = result.get("audio", None)
        sample_rate = result.get("sample_rate", 22050)
        speed = result.get("speed", 1.0)
        
        # Generate a unique filename based on the input text and voice name
        base_txt_name = os.path.splitext(os.path.basename(input_path))[0]
        filename_base = f"{base_txt_name}_{voice_name}"
        output_filename = f"{filename_base}_{speed}x.wav"
        
        output_path = os.path.join(save_folder, output_filename)
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        save_as_wav(audio_data, output_path, sample_rate)
        print(f"Speech saved to: {output_path}")
    
if __name__ == "__main__":
    main()