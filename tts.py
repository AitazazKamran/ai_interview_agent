import edge_tts
import asyncio
import os
from typing import Optional
import sounddevice as sd
from scipy.io.wavfile import read as wav_read


class TextToSpeech:
    def __init__(self, voice: str = "en-US-GuyNeural"):
        """
        Initialize Edge TTS for text-to-speech.
        
        Args:
            voice: Voice to use for speech synthesis
        """
        self.voice = voice
        
    async def _generate_speech(self, text: str, output_file: str) -> bool:
        """
        Generate speech from text using Edge TTS.
        
        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)
            return True
        except Exception as e:
            print(f"Error generating speech: {e}", flush=True)
            return False
    
    def speak(self, text: str) -> bool:
        """
        Speak text using Edge TTS and play through speakers.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        temp_audio_file = "temp_tts.mp3"
        
        try:
            asyncio.run(self._generate_speech(text, temp_audio_file))
            
            if not os.path.exists(temp_audio_file):
                return False
            
            self._play_audio(temp_audio_file)
            
            try:
                os.remove(temp_audio_file)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"Error playing speech: {e}", flush=True)
            return False
    
    def _play_audio(self, audio_file: str):
        """
        Play audio file through speakers.
        
        Args:
            audio_file: Path to audio file
        """
        try:
            import subprocess
            
            if os.name == 'nt':
                os.startfile(audio_file)
                import time
                time.sleep(3)
            else:
                subprocess.run(['ffplay', '-nodisp', '-autoexit', audio_file], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Could not play audio: {e}", flush=True)
