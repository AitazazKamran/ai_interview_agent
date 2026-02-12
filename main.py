import os
import sys
import random
from typing import List, Dict
from dotenv import load_dotenv

from audio import AudioRecorder
from transcriber import SpeechTranscriber
from evaluator import ResponseEvaluator
from tts import TextToSpeech


class InterviewAgent:
    def __init__(self):
        """Initialize the interview agent with all components."""
        load_dotenv()
        
        groq_api_key = os.getenv("GROQ_API_KEY", "")
        
        self.audio_recorder = AudioRecorder(
            sample_rate=16000,
            silence_threshold=0.01,
            silence_duration=2.0,
            max_duration=60.0
        )
        self.transcriber = SpeechTranscriber(
            api_key=groq_api_key,
            model_name="whisper-large-v3-turbo"
        )
        self.evaluator = ResponseEvaluator(api_key=groq_api_key)
        self.tts = TextToSpeech(voice="en-US-GuyNeural")
        
        self.question_bank = [
            "Tell me about a challenging technical project you've worked on recently.",
            "How do you approach debugging a complex issue in production?",
            "Explain the difference between synchronous and asynchronous programming.",
            "How do you handle deadlines or work pressure?",
            "Can you describe a challenge you faced at work and how you solved it?",
            "Do you prefer working independently or in a team? Why?"
        ]
        
        self.questions = random.sample(self.question_bank, 3)
        
        self.all_scores = []
        self.interview_data = []
        
    def setup(self) -> bool:
        """
        Set up the interview environment.
        
        Returns:
            True if setup successful, False otherwise
        """
        print("=" * 50)
        print("AI INTERVIEW AGENT")
        print("=" * 50)
        print()
        
        print("Testing microphone...", flush=True)
        if not self.audio_recorder.test_microphone():
            print("ERROR: Microphone not accessible.", flush=True)
            return False
        print("Microphone ready.", flush=True)
        print()
        
        if not self.transcriber.load_model():
            print("ERROR: Failed to load transcription model.", flush=True)
            return False
        print()
        
        return True
    def ask_question(self, question_num: int, question: str) -> bool:
        """
        Ask a single interview question and process the response.
        
        Args:
            question_num: Question number (1-indexed)
            question: The question text
            
        Returns:
            True if question processed successfully, False otherwise
        """
        print("-" * 40)
        print(f"QUESTION {question_num}:")
        print(question)
        print()
        
        print("Speaking question...", flush=True)
        self.tts.speak(question)
        print()
        
        audio_file = f"recording_{question_num}.wav"
        audio_file = f"recording_{question_num}.wav"
        
        input("Press Enter when ready to answer...")
        print()
        
        if not self.audio_recorder.record_audio(audio_file):
            print("Failed to record audio.", flush=True)
            return False
        
        print("Recording complete. Transcribing...", flush=True)
        print()
        
        transcription = self.transcriber.transcribe(audio_file)
        
        if transcription is None:
            print("Transcription failed.", flush=True)
            return False
        
        print("TRANSCRIPTION:")
        print(transcription)
        print()
        
        if not self.evaluator.is_answer_sufficient(transcription):
            print("Follow-up needed: Please provide a more detailed answer.")
            print()
            
            audio_file_followup = f"recording_{question_num}_followup.wav"
            input("Press Enter when ready to continue...")
            print()
            
            if self.audio_recorder.record_audio(audio_file_followup):
                print("Recording complete. Transcribing follow-up...", flush=True)
                print()
                
                followup_transcription = self.transcriber.transcribe(audio_file_followup)
                if followup_transcription:
                    transcription = transcription + " " + followup_transcription
                    print("UPDATED TRANSCRIPTION:")
                    print(transcription)
                    print()
                
                try:
                    os.remove(audio_file_followup)
                except:
                    pass
        
        scores = self.evaluator.evaluate_response(question, transcription)
        
        print("SCORES:")
        for category, score in scores.items():
            print(f"- {category}: {score}/5")
        print()
        
        self.all_scores.append(scores)
        self.interview_data.append({
            "question": question,
            "transcription": transcription,
            "scores": scores
        })
        
        try:
            os.remove(audio_file)
        except:
            pass
        
        return True
    
    def conduct_interview(self) -> bool:
        """
        Conduct the full interview with all questions.
        
        Returns:
            True if interview completed successfully, False otherwise
        """
        print("The interview will consist of 3 questions.")
        print("After each question, you will have up to 60 seconds to respond.")
        print("Recording will automatically stop after 2 seconds of silence.")
        print()
        
        for i, question in enumerate(self.questions, start=1):
            if not self.ask_question(i, question):
                print(f"Error processing question {i}. Aborting interview.", flush=True)
                return False
        
        return True
    
    def print_final_summary(self):
        """Print the final interview summary with recommendations."""
        print("-" * 40)
        print("FINAL SUMMARY")
        print("-" * 40)
        print()
        
        average_scores = self.evaluator.calculate_final_scores(self.all_scores)
        
        print("AVERAGE SCORES:")
        for category, avg_score in average_scores.items():
            print(f"- {category}: {avg_score}/5")
        print()
        
        recommendation = self.evaluator.get_recommendation(average_scores)
        print(f"OVERALL RECOMMENDATION: {recommendation}")
        print()
        
        print("=" * 50)
        print("INTERVIEW COMPLETE")
        print("=" * 50)
    
    def run(self):
        """Main entry point to run the interview agent."""
        if not self.setup():
            print("Setup failed. Exiting.", flush=True)
            sys.exit(1)
        
        if not self.conduct_interview():
            print("Interview incomplete.", flush=True)
            sys.exit(1)
        
        self.print_final_summary()


if __name__ == "__main__":
    agent = InterviewAgent()
    agent.run()
