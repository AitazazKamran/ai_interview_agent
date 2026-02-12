from openai import OpenAI
import os
from typing import Dict, Optional


class CodeEvaluator:
    def __init__(self, api_key: str):
        """
        Initialize code evaluator with LLM.
        
        Args:
            api_key: Groq API key for LLM evaluation
        """
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
    
    def evaluate_code(self, question: str, code: str) -> Dict[str, any]:
        """
        Evaluate submitted code using LLM.
        
        Args:
            question: The coding problem statement
            code: The candidate's code solution
            
        Returns:
            Dictionary with scores and feedback
        """
        if not self.client:
            return {
                "correctness": 3,
                "code_quality": 3,
                "efficiency": 3,
                "overall_score": 3,
                "feedback": "LLM evaluation unavailable"
            }
        
        prompt = f"""You are an expert programming interviewer evaluating a candidate's code submission.

PROBLEM STATEMENT:
{question}

CANDIDATE'S CODE:
{code}

Evaluate this code across the following dimensions on a scale of 1-5 (where 1 is poor and 5 is excellent):

1. **Correctness**: Does the code solve the problem correctly?
2. **Code Quality**: Is the code clean, readable, and well-structured?
3. **Efficiency**: Is the solution efficient in terms of time and space complexity?

Also provide:
- Brief feedback on strengths and areas for improvement
- Overall score (1-5)

Provide your response in this EXACT format:
Correctness: X
Code Quality: X
Efficiency: X
Overall Score: X
Feedback: [Your feedback here]

Replace X with numbers 1-5."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert programming interviewer who provides objective code evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            return self._parse_code_evaluation(result_text)
            
        except Exception as e:
            print(f"Error during code evaluation: {e}", flush=True)
            return {
                "correctness": 3,
                "code_quality": 3,
                "efficiency": 3,
                "overall_score": 3,
                "feedback": "Error during evaluation"
            }
    
    def _parse_code_evaluation(self, llm_response: str) -> Dict[str, any]:
        """
        Parse LLM evaluation response.
        
        Args:
            llm_response: Raw text response from LLM
            
        Returns:
            Dictionary with parsed scores and feedback
        """
        import re
        
        result = {
            "correctness": 3,
            "code_quality": 3,
            "efficiency": 3,
            "overall_score": 3,
            "feedback": ""
        }
        
        correctness_match = re.search(r"Correctness:\s*(\d)", llm_response, re.IGNORECASE)
        if correctness_match:
            result["correctness"] = int(correctness_match.group(1))
        
        quality_match = re.search(r"Code Quality:\s*(\d)", llm_response, re.IGNORECASE)
        if quality_match:
            result["code_quality"] = int(quality_match.group(1))
        
        efficiency_match = re.search(r"Efficiency:\s*(\d)", llm_response, re.IGNORECASE)
        if efficiency_match:
            result["efficiency"] = int(efficiency_match.group(1))
        
        overall_match = re.search(r"Overall Score:\s*(\d)", llm_response, re.IGNORECASE)
        if overall_match:
            result["overall_score"] = int(overall_match.group(1))
        
        feedback_match = re.search(r"Feedback:\s*(.+?)(?:\n\n|\Z)", llm_response, re.IGNORECASE | re.DOTALL)
        if feedback_match:
            result["feedback"] = feedback_match.group(1).strip()
        
        return result
