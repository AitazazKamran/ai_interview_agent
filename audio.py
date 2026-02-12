import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time
from typing import Optional


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000, silence_threshold: float = 0.01, 
                 silence_duration: float = 10.0, max_duration: float = 60.0):
        """
        Initialize audio recorder with configurable parameters.
        
        Args:
            sample_rate: Audio sample rate in Hz
            silence_threshold: RMS threshold below which audio is considered silence
            silence_duration: Seconds of silence before auto-stopping
            max_duration: Maximum recording duration in seconds
        """
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.channels = 1
        
    def record_audio(self, output_file: str) -> bool:
        """
        Record audio from microphone with automatic silence detection.
        
        Args:
            output_file: Path to save the WAV file
            
        Returns:
            True if recording successful, False otherwise
        """
        print("Listening...", flush=True)
        
        try:
            recording = []
            silence_start = None
            start_time = time.time()
            
            def callback(indata, frames, time_info, status):
                """Callback function for audio stream processing."""
                if status:
                    print(f"Status: {status}", flush=True)
                recording.append(indata.copy())
            
            with sd.InputStream(samplerate=self.sample_rate, 
                              channels=self.channels, 
                              callback=callback,
                              dtype='float32'):
                
                while True:
                    current_time = time.time()
                    elapsed = current_time - start_time
                    
                    if elapsed >= self.max_duration:
                        break
                    
                    if len(recording) > 0:
                        recent_audio = recording[-1]
                        rms = np.sqrt(np.mean(recent_audio**2))
                        
                        if rms < self.silence_threshold:
                            if silence_start is None:
                                silence_start = current_time
                            elif current_time - silence_start >= self.silence_duration:
                                break
                        else:
                            silence_start = None
                    
                    time.sleep(0.1)
            
            if not recording:
                print("No audio recorded.", flush=True)
                return False
            
            audio_data = np.concatenate(recording, axis=0)
            audio_data_int16 = np.int16(audio_data * 32767)
            write(output_file, self.sample_rate, audio_data_int16)
            
            return True
            
        except Exception as e:
            print(f"Error recording audio: {e}", flush=True)
            return False
    
    def test_microphone(self) -> bool:
        """
        Test if microphone is available.
        
        Returns:
            True if microphone is accessible, False otherwise
        """
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            if default_input:
                return True
            return False
        except Exception as e:
            print(f"Microphone test failed: {e}", flush=True)
            return False
