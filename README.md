# AI Interview Agent

Production-quality terminal-based interview agent with speech recognition and automated evaluation.

## Features

- Real-time microphone audio recording
- Automatic silence detection
- Whisper large-v3-turbo transcription
- Multi-dimensional scoring (Relevance, Clarity, Confidence, Technical Accuracy)
- Automated follow-up questions for insufficient answers
- Final hiring recommendation

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file (optional for future API integration):
```
OPENAI_API_KEY=your_key_here
```

## Usage

```bash
python main.py
```

## System Requirements

- Python 3.10+
- Working microphone
- ~10GB disk space for Whisper model
- 8GB+ RAM recommended

## Architecture

- `audio.py`: Audio recording with silence detection
- `transcriber.py`: Whisper-based speech-to-text
- `evaluator.py`: Response scoring and evaluation logic
- `main.py`: Main interview orchestration

## Output Format

Each question displays:
- Question text
- Transcription of candidate response
- Scores across 4 dimensions (1-5 scale)

Final summary includes:
- Average scores per category
- Overall recommendation (Strong Hire / Hire / Borderline / Reject)
