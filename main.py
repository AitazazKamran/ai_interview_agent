import os
import sys
import random
from typing import List, Dict
from dotenv import load_dotenv

from audio import AudioRecorder
from transcriber import SpeechTranscriber
from evaluator import ResponseEvaluator
from tts import TextToSpeech
from code_evaluator import CodeEvaluator


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
        self.code_evaluator = CodeEvaluator(api_key=groq_api_key)
        
        self.role_questions = {
            "Software Engineer": [
                "Tell me about a challenging technical project you've worked on recently.",
                "How do you approach debugging a complex issue in production?",
                "Explain the difference between synchronous and asynchronous programming.",
                "What is your experience with version control systems like Git?",
                "How do you ensure code quality and maintainability in your projects?"
            ],
            "Data Analyst": [
                "How do you approach data cleaning and preprocessing?",
                "Can you explain the difference between correlation and causation?",
                "What data visualization tools have you used and which do you prefer?",
                "Describe a time when you used data to solve a business problem.",
                "How do you handle missing or incomplete data in your analysis?"
            ],
            "Cloud Engineer": [
                "What is your experience with cloud platforms like AWS, Azure, or GCP?",
                "How do you ensure security and compliance in cloud deployments?",
                "Explain the concept of Infrastructure as Code and why it's important.",
                "How do you approach designing scalable and fault-tolerant systems?",
                "What monitoring and logging strategies do you use for cloud applications?"
            ],
            "HR Screening": [
                "How do you handle deadlines or work pressure?",
                "Can you describe a challenge you faced at work and how you solved it?",
                "Do you prefer working independently or in a team? Why?",
                "What motivates you in your professional career?",
                "Tell me about a time when you had to adapt to a significant change at work."
            ],
            "Coding Test": [
                "Write a function to reverse a string without using built-in reverse methods.",
                "Given an array of integers, find two numbers that add up to a target sum.",
                "Write a function to check if a string is a valid palindrome (ignoring spaces and case)."
            ]
        }
        
        self.selected_role = None
        self.questions = []
        
        self.all_scores = []
        self.interview_data = []
        
    def select_role(self) -> bool:
        """
        Ask user to select interview role.
        
        Returns:
            True if role selected successfully, False otherwise
        """
        print("=" * 50)
        print("AI INTERVIEW AGENT")
        print("=" * 50)
        print()
        
        print("Select the interview role:")
        print("1. 💻 Software Engineer")
        print("2. 📊 Data Analyst")
        print("3. ☁️  Cloud Engineer")
        print("4. 🧠 HR Screening (non-technical)")
        print("5. 👨‍💻 Coding Test")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (1-5): ").strip()
                
                role_map = {
                    "1": "Software Engineer",
                    "2": "Data Analyst",
                    "3": "Cloud Engineer",
                    "4": "HR Screening",
                    "5": "Coding Test"
                }
                
                if choice in role_map:
                    self.selected_role = role_map[choice]
                    print(f"\nSelected: {self.selected_role}")
                    print()
                    
                    if self.selected_role == "Coding Test":
                        self.questions = self.role_questions[self.selected_role]
                    else:
                        self.questions = random.sample(self.role_questions[self.selected_role], 3)
                    return True
                else:
                    print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                    
            except KeyboardInterrupt:
                print("\n\nInterview cancelled.")
                return False
            except Exception as e:
                print(f"Error: {e}")
                return False
    
    def setup(self) -> bool:
        """
        Set up the interview environment.
        
        Returns:
            True if setup successful, False otherwise
        """
        
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
    
    def ask_coding_question(self, question_num: int, question: str) -> bool:
        """
        Ask a coding question and evaluate the submitted code.
        
        Args:
            question_num: Question number (1-indexed)
            question: The coding problem statement
            
        Returns:
            True if question processed successfully, False otherwise
        """
        print("-" * 40)
        print(f"CODING PROBLEM {question_num}:")
        print(question)
        print()
        
        code_file = f"solution_{question_num}.txt"
        
        with open(code_file, 'w') as f:
            f.write(f"# Problem {question_num}: {question}\n")
            f.write("# Write your code below:\n\n")
        
        print(f"A text file '{code_file}' has been created.")
        print("Write your code solution in this file.")
        print()
        
        if os.name == 'nt':
            os.system(f'notepad {code_file}')
        else:
            print(f"Please edit {code_file} in your preferred text editor.")
        
        input("Press Enter when you've finished writing your code...")
        print()
        
        if not os.path.exists(code_file):
            print("Code file not found.", flush=True)
            return False
        
        with open(code_file, 'r') as f:
            code = f.read()
        
        print("CODE SUBMITTED:")
        print(code)
        print()
        
        print("Evaluating your code...", flush=True)
        evaluation = self.code_evaluator.evaluate_code(question, code)
        
        print("EVALUATION:")
        print(f"- Correctness: {evaluation['correctness']}/5")
        print(f"- Code Quality: {evaluation['code_quality']}/5")
        print(f"- Efficiency: {evaluation['efficiency']}/5")
        print(f"- Overall Score: {evaluation['overall_score']}/5")
        print()
        print(f"FEEDBACK: {evaluation['feedback']}")
        print()
        
        scores = {
            "Correctness": evaluation['correctness'],
            "Code Quality": evaluation['code_quality'],
            "Efficiency": evaluation['efficiency'],
            "Overall": evaluation['overall_score']
        }
        
        self.all_scores.append(scores)
        self.interview_data.append({
            "question": question,
            "code": code,
            "scores": scores,
            "feedback": evaluation['feedback']
        })
        
        return True
    
    def conduct_interview(self) -> bool:
        """
        Conduct the full interview with all questions.
        
        Returns:
            True if interview completed successfully, False otherwise
        """
        if self.selected_role == "Coding Test":
            print("The coding test will consist of 3 problems.")
            print("For each problem, a text file will open for you to write your solution.")
            print()
            
            for i, question in enumerate(self.questions, start=1):
                if not self.ask_coding_question(i, question):
                    print(f"Error processing problem {i}. Aborting test.", flush=True)
                    return False
        else:
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
        if not self.select_role():
            print("Role selection failed. Exiting.", flush=True)
            sys.exit(1)
        
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
