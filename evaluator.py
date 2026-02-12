from typing import Dict, List
import re
from openai import OpenAI


class ResponseEvaluator:
    def __init__(self, api_key: str):
        """
        Initialize the response evaluator with LLM-based scoring.
        
        Args:
            api_key: Groq API key for LLM evaluation
        """
        self.score_categories = ["Relevance", "Clarity", "Confidence", "Technical Accuracy"]
        self.client = None
        self.api_key = api_key
        
        if api_key and api_key != "your_groq_api_key_here":
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
            except Exception as e:
                print(f"Warning: Could not initialize LLM client: {e}", flush=True)
        
    def evaluate_response(self, question: str, transcription: str) -> Dict[str, int]:
        """
        Evaluate a candidate's response across multiple dimensions using LLM.
        
        Args:
            question: The interview question asked
            transcription: The candidate's transcribed response
            
        Returns:
            Dictionary with scores for each category (1-5 scale)
        """
        if self.client:
            return self._evaluate_with_llm(question, transcription)
        else:
            return self._evaluate_fallback(question, transcription)
    
    def _evaluate_with_llm(self, question: str, transcription: str) -> Dict[str, int]:
        """
        Use LLM to evaluate the response and provide scores.
        
        Args:
            question: The interview question
            transcription: The candidate's answer
            
        Returns:
            Dictionary with scores for each category
        """
        prompt = f"""You are an expert technical interviewer evaluating a candidate's response.

QUESTION:
{question}

CANDIDATE'S ANSWER:
{transcription}

Evaluate this answer across 4 dimensions on a scale of 1-5 (where 1 is poor and 5 is excellent):

1. **Relevance**: How well does the answer address the question asked?
2. **Clarity**: How clear, structured, and easy to understand is the response?
3. **Confidence**: How confident and certain does the candidate sound?
4. **Technical Accuracy**: How technically accurate and detailed is the answer?

Provide ONLY the scores in this exact format:
Relevance: X
Clarity: X
Confidence: X
Technical Accuracy: X

Replace X with numbers 1-5. No additional text or explanation."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer who provides objective scoring."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            scores = self._parse_llm_scores(result_text)
            
            if scores:
                return scores
            else:
                print("Warning: Could not parse LLM scores, using fallback evaluation", flush=True)
                return self._evaluate_fallback(question, transcription)
                
        except Exception as e:
            print(f"Error during LLM evaluation: {e}", flush=True)
            return self._evaluate_fallback(question, transcription)
    
    def _parse_llm_scores(self, llm_response: str) -> Dict[str, int]:
        """
        Parse scores from LLM response.
        
        Args:
            llm_response: Raw text response from LLM
            
        Returns:
            Dictionary of scores or empty dict if parsing fails
        """
        scores = {}
        
        patterns = {
            "Relevance": r"Relevance:\s*(\d)",
            "Clarity": r"Clarity:\s*(\d)",
            "Confidence": r"Confidence:\s*(\d)",
            "Technical Accuracy": r"Technical Accuracy:\s*(\d)"
        }
        
        for category, pattern in patterns.items():
            match = re.search(pattern, llm_response, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                scores[category] = max(1, min(5, score))
        
        if len(scores) == 4:
            return scores
        return {}
    
    def _evaluate_fallback(self, question: str, transcription: str) -> Dict[str, int]:
        """
        Fallback rule-based evaluation if LLM is unavailable.
        
        Args:
            question: The interview question
            transcription: The candidate's answer
            
        Returns:
            Dictionary with scores for each category
        """
        scores = {}
        
        scores["Relevance"] = self._evaluate_relevance(question, transcription)
        scores["Clarity"] = self._evaluate_clarity(transcription)
        scores["Confidence"] = self._evaluate_confidence(transcription)
        scores["Technical Accuracy"] = self._evaluate_technical_accuracy(question, transcription)
        
        return scores
    
    def _evaluate_relevance(self, question: str, transcription: str) -> int:
        """
        Score how relevant the response is to the question.
        
        Returns: Score 1-5
        """
        if not transcription or len(transcription.strip()) == 0:
            return 1
        
        words = transcription.lower().split()
        question_words = set(question.lower().split())
        
        common_words = {"the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "for", "and", "or"}
        question_keywords = question_words - common_words
        
        overlap = sum(1 for word in words if word in question_keywords)
        
        if len(words) < 5:
            return 2
        elif overlap == 0:
            return 2
        elif overlap <= 2:
            return 3
        elif overlap <= 4:
            return 4
        else:
            return 5
    
    def _evaluate_clarity(self, transcription: str) -> int:
        """
        Score the clarity and structure of the response.
        
        Returns: Score 1-5
        """
        if not transcription or len(transcription.strip()) == 0:
            return 1
        
        words = transcription.split()
        word_count = len(words)
        
        if word_count < 5:
            return 2
        
        sentences = re.split(r'[.!?]+', transcription)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        filler_words = ["um", "uh", "like", "you know", "basically", "actually", "literally"]
        filler_count = sum(transcription.lower().count(filler) for filler in filler_words)
        filler_ratio = filler_count / max(word_count, 1)
        
        if filler_ratio > 0.2:
            clarity_score = 2
        elif filler_ratio > 0.1:
            clarity_score = 3
        elif word_count < 20:
            clarity_score = 3
        elif len(sentences) >= 2 and word_count >= 30:
            clarity_score = 5
        else:
            clarity_score = 4
        
        return clarity_score
    
    def _evaluate_confidence(self, transcription: str) -> int:
        """
        Score the confidence level based on language patterns.
        
        Returns: Score 1-5
        """
        if not transcription or len(transcription.strip()) == 0:
            return 1
        
        uncertain_phrases = [
            "i think", "maybe", "i guess", "i'm not sure", "probably",
            "i don't know", "perhaps", "kind of", "sort of", "i believe"
        ]
        
        confident_phrases = [
            "i know", "definitely", "certainly", "absolutely", "clearly",
            "obviously", "i'm confident", "without a doubt", "i'm certain"
        ]
        
        text_lower = transcription.lower()
        
        uncertain_count = sum(text_lower.count(phrase) for phrase in uncertain_phrases)
        confident_count = sum(text_lower.count(phrase) for phrase in confident_phrases)
        
        words = transcription.split()
        word_count = len(words)
        
        if word_count < 5:
            return 2
        
        if uncertain_count > confident_count + 2:
            return 2
        elif uncertain_count > confident_count:
            return 3
        elif confident_count > uncertain_count:
            return 5
        else:
            return 4
    
    def _evaluate_technical_accuracy(self, question: str, transcription: str) -> int:
        """
        Score technical accuracy based on terminology and depth.
        
        Returns: Score 1-5
        """
        if not transcription or len(transcription.strip()) == 0:
            return 1
        
        technical_indicators = [
            "algorithm", "data structure", "complexity", "optimization", "architecture",
            "design pattern", "api", "database", "system", "framework", "implementation",
            "interface", "method", "function", "class", "object", "variable", "parameter",
            "memory", "performance", "scalability", "security", "testing", "debugging",
            "deployment", "integration", "protocol", "encryption", "authentication"
        ]
        
        text_lower = transcription.lower()
        technical_count = sum(text_lower.count(term) for term in technical_indicators)
        
        words = transcription.split()
        word_count = len(words)
        
        if word_count < 5:
            return 2
        
        if technical_count == 0:
            return 2
        elif technical_count <= 2:
            return 3
        elif technical_count <= 4:
            return 4
        else:
            return 5
    
    def is_answer_sufficient(self, transcription: str) -> bool:
        """
        Check if the answer is sufficient or needs follow-up.
        
        Args:
            transcription: The candidate's response
            
        Returns:
            True if answer is sufficient, False if follow-up needed
        """
        if not transcription:
            return False
        
        words = transcription.split()
        if len(words) < 5:
            return False
        
        return True
    
    def calculate_final_scores(self, all_scores: List[Dict[str, int]]) -> Dict[str, float]:
        """
        Calculate average scores across all questions.
        
        Args:
            all_scores: List of score dictionaries from each question
            
        Returns:
            Dictionary with average scores for each category
        """
        if not all_scores:
            return {cat: 0.0 for cat in self.score_categories}
        
        averages = {}
        for category in self.score_categories:
            total = sum(scores.get(category, 0) for scores in all_scores)
            averages[category] = round(total / len(all_scores), 2)
        
        return averages
    
    def get_recommendation(self, average_scores: Dict[str, float]) -> str:
        """
        Generate hiring recommendation based on average scores.
        
        Args:
            average_scores: Dictionary of average scores per category
            
        Returns:
            Recommendation string: "Strong Hire", "Hire", "Borderline", or "Reject"
        """
        if not average_scores:
            return "Reject"
        
        overall_average = sum(average_scores.values()) / len(average_scores)
        
        if overall_average >= 4.5:
            return "Strong Hire"
        elif overall_average >= 3.5:
            return "Hire"
        elif overall_average >= 2.5:
            return "Borderline"
        else:
            return "Reject"
