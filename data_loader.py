import requests
import json
import html
from config import API_SETTINGS, CATEGORIES

class QuizDataLoader:
    """Fetches quiz questions from Open Trivia Database API"""
    
    def __init__(self):
        self.base_url = API_SETTINGS["base_url"]
        self.amount = API_SETTINGS["amount"]
        self.difficulty = API_SETTINGS["difficulty"]
    
    def fetch_questions(self, category="random"):
        """
        Fetch questions from Open Trivia Database API
        Args:
            category: Quiz category (e.g., 'science', 'history', 'random')
        Returns:
            List of formatted questions
        """
        try:
            # Build API URL
            params = {
                "amount": self.amount,
                "type": "multiple",
                "difficulty": self.difficulty
            }
            
            # Add category if specified
            if category != "random" and category in CATEGORIES:
                params["category"] = CATEGORIES[category]
            
            print(f"📥 Fetching {self.amount} questions from Open Trivia Database...")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["response_code"] != 0:
                print("⚠️  API returned no results. Using fallback questions...")
                return self._get_fallback_questions()
            
            questions = self._format_questions(data["results"])
            print(f"✅ Successfully loaded {len(questions)} questions!\n")
            return questions
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            print("📖 Using fallback local questions...\n")
            return self._get_fallback_questions()
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._get_fallback_questions()
    
    def _format_questions(self, raw_questions):
        """Convert API response to app format"""
        formatted = []
        
        for q in raw_questions:
            # Decode HTML entities
            question = html.unescape(q["question"])
            correct = html.unescape(q["correct_answer"])
            
            # Combine and shuffle options
            options = [correct] + [html.unescape(opt) for opt in q["incorrect_answers"]]
            import random
            random.shuffle(options)
            
            formatted.append({
                "question": question,
                "options": options,
                "answer": correct,
                "explanation": f"Difficulty: {q['difficulty'].capitalize()}",
                "category": q.get("category", "General Knowledge")
            })
        
        return formatted
    
    def _get_fallback_questions(self):
        """Return local questions as fallback when API is unavailable"""
        try:
            with open("questions.json", "r") as f:
                return json.load(f)
        except:
            return []
    
    def get_categories(self):
        """Return available categories"""
        return list(CATEGORIES.keys())
