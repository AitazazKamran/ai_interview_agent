# AI Interview Agent

Production-quality terminal-based interview agent with speech recognition, text-to-speech, and LLM-powered evaluation.

## Features

- **5 Interview Modes:**
  - 💻 Software Engineer (technical coding questions)
  - 📊 Data Analyst (data analysis & visualization)
  - ☁️ Cloud Engineer (cloud infrastructure & DevOps)
  - 🧠 HR Screening (behavioral, non-technical)
  - 👨‍💻 Coding Test (LeetCode-style problems)

- **Voice Interview (Modes 1-4):**
  - Real-time microphone audio recording
  - Automatic silence detection
  - Text-to-speech questions (Microsoft Edge TTS)
  - Groq Whisper large-v3-turbo transcription
  - Automated follow-up for insufficient answers

- **Coding Test (Mode 5):**
  - Opens text editor (Notepad) for code solutions
  - 3 LeetCode-style easy problems
  - LLM-powered code evaluation
  - Scores: Correctness, Code Quality, Efficiency

- **LLM Evaluation:**
  - Groq llama-3.3-70b-versatile for intelligent scoring
  - Multi-dimensional scoring (Relevance, Clarity, Confidence, Technical Accuracy)
  - Detailed feedback and recommendations

- **Final Report:**
  - Average scores per category (1-5 scale)
  - Overall hiring recommendation
  - Role-specific assessment

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:
```
GROQ_API_KEY=gsk_your_groq_api_key_here
```

Get your free Groq API key from: https://console.groq.com

## Usage

```bash
# Activate virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# Run the interview agent
python main.py
```

Select your interview mode (1-5), then:
- **For voice interviews:** Speak your answers after each question
- **For coding test:** Write solutions in the text files that open

## System Requirements

- Python 3.10+
- Working microphone (for voice interviews)
- Internet connection (for Groq API)
- Windows/Linux/macOS

## Architecture

```
interview agent/
├── main.py                  # Main orchestration & interview flow
├── audio.py                 # Audio recording with silence detection
├── transcriber.py           # Groq Whisper speech-to-text
├── evaluator.py             # LLM-based response evaluation
├── code_evaluator.py        # LLM-based code evaluation
├── tts.py                   # Microsoft Edge TTS
├── requirements.txt         # Python dependencies
└── .env                     # API keys (create this)
```

## Output Format

### Voice Interview
Each question displays:
- Question text (spoken aloud)
- Transcription of candidate response
- Scores across 4 dimensions (1-5 scale)

### Coding Test
Each problem displays:
- Problem statement
- Submitted code
- Evaluation scores (Correctness, Quality, Efficiency)
- Detailed feedback

### Final Summary
- Average scores per category
- Overall recommendation:
  - Voice: "Strong Hire" / "Hire" / "Borderline" / "Reject"
  - Coding: "Excellent" / "Good" / "Average" / "Below Average"

## Interview Questions

**Software Engineer:** Technical projects, debugging, async programming, Git, code quality

**Data Analyst:** Data cleaning, correlation vs causation, visualization tools, business problems

**Cloud Engineer:** AWS/Azure/GCP, security, Infrastructure as Code, scalability, monitoring

**HR Screening:** Deadlines, challenges, teamwork, motivation, adaptability

**Coding Test:**
1. Reverse a string without built-in methods
2. Two sum problem
3. Palindrome validation

## API Usage

- **Speech-to-Text:** Groq Whisper API (whisper-large-v3-turbo)
- **Evaluation:** Groq LLaMA 3.3 70B (llama-3.3-70b-versatile)
- **Text-to-Speech:** Microsoft Edge TTS (free, local)

## License

MIT
