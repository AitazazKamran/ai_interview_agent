import os
from openai import OpenAI
from typing import Optional


class SpeechTranscriber:
    def __init__(self, api_key: str, model_name: str = "whisper-large-v3-turbo"):
        """
        Initialize Whisper transcriber using Groq API via OpenAI client.
        
        Args:
            api_key: Groq API key
            model_name: Whisper model to use (whisper-large-v3-turbo for production)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        
    def load_model(self) -> bool:
        """
        Initialize OpenAI client with Groq endpoint.
        
        Returns:
            True if client initialized successfully, False otherwise
        """
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            print("ERROR: GROQ_API_KEY not configured in .env file", flush=True)
            return False
        
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            print("Groq API configured.", flush=True)
            return True
        except Exception as e:
            print(f"Error initializing Groq client: {e}", flush=True)
            return False
    
    def transcribe(self, audio_file: str) -> Optional[str]:
        """
        Transcribe audio file to text using Groq Whisper API.
        
        Args:
            audio_file: Path to the WAV audio file
            
        Returns:
            Transcribed text or None if transcription fails
        """
        if self.client is None:
            if not self.load_model():
                return None
        
        if not os.path.exists(audio_file):
            print(f"Audio file not found: {audio_file}", flush=True)
            return None
        
        try:
            with open(audio_file, 'rb') as audio:
                transcript = self.client.audio.transcriptions.create(
                    file=audio,
                    model=self.model_name
                )
                
                transcription = transcript.text.strip()
                return transcription
            
        except Exception as e:
            print(f"Error during transcription: {e}", flush=True)
            return None
