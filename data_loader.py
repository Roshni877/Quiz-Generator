import requests
import json
import html
import random
import threading
from config import API_SETTINGS, CATEGORIES

class QuizDataLoader:
    """Fetches quiz questions instantly from preloaded local database, memory cache, or background API"""
    
    def __init__(self):
        self.base_url = API_SETTINGS.get("base_url", "https://opentdb.com/api.php")
        self.amount = API_SETTINGS.get("amount", 10)
        self.difficulty = API_SETTINGS.get("difficulty", "medium")
        self._cache = {}
        self._local_db = self._load_local_db()

    def _load_local_db(self):
        """Pre-load local question bank into memory for 0ms instant access"""
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[LOCAL] Warning: Could not read questions.json: {e}")
            return []

    def fetch_questions(self, category="random"):
        """
        Fetch questions INSTANTLY (0ms response) from memory cache & local DB bank.
        """
        category_key = str(category).lower().strip()
        
        # 1. Check in-memory cache first for instant response
        if category_key in self._cache and len(self._cache[category_key]) >= self.amount:
            cached = list(self._cache[category_key])
            random.shuffle(cached)
            return cached[:self.amount]
        
        # 2. Return instant local questions matching category
        local_questions = self._get_local_questions(category_key)
        if local_questions and len(local_questions) >= self.amount:
            self._cache[category_key] = local_questions
            # Optional non-blocking background fetch to refresh cache
            threading.Thread(target=self._background_api_fetch, args=(category_key,), daemon=True).start()
            return local_questions[:self.amount]
        
        # 3. If local questions fall short, combine with any available local questions
        all_local = self._get_local_questions("random")
        if all_local:
            combined = local_questions + [q for q in all_local if q not in local_questions]
            random.shuffle(combined)
            res = combined[:self.amount]
            self._cache[category_key] = res
            return res
            
        return []

    def _get_local_questions(self, category="random"):
        """Return category-matched local questions instantly from memory"""
        all_q = self._local_db if self._local_db else self._load_local_db()
        if not all_q:
            return []

        category = str(category).lower().strip()
        matched = []
        others = []

        for q in all_q:
            q_cat = str(q.get("category", "")).lower().strip()
            if category == "random":
                matched.append(dict(q))
            elif q_cat == category or category in q_cat or q_cat in category:
                matched.append(dict(q))
            else:
                others.append(dict(q))

        random.shuffle(matched)
        random.shuffle(others)

        combined = matched + others
        result = combined[:self.amount]
        random.shuffle(result)
        return result

    def _background_api_fetch(self, category_key):
        """Asynchronous API fetch in background without delaying user"""
        try:
            params = {
                "amount": self.amount,
                "type": "multiple"
            }
            if self.difficulty:
                params["difficulty"] = self.difficulty
            
            if category_key != "random" and category_key in CATEGORIES and CATEGORIES[category_key] is not None:
                params["category"] = CATEGORIES[category_key]
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) QuizGenerator/1.0"
            }
            
            response = requests.get(self.base_url, params=params, headers=headers, timeout=0.8)
            if response.status_code == 200:
                data = response.json()
                if data.get("response_code") == 0 and data.get("results"):
                    questions = self._format_questions(data["results"])
                    if questions and len(questions) > 0:
                        self._cache[category_key] = questions
        except Exception:
            pass

    def _format_questions(self, raw_questions):
        """Convert API response to app format"""
        formatted = []
        for q in raw_questions:
            question = html.unescape(q["question"])
            correct = html.unescape(q["correct_answer"])
            options = [correct] + [html.unescape(opt) for opt in q["incorrect_answers"]]
            random.shuffle(options)
            
            formatted.append({
                "question": question,
                "options": options,
                "answer": correct,
                "explanation": f"Category: {q.get('category', 'General')}",
                "category": q.get("category", "General")
            })
        return formatted

    def get_categories(self):
        """Return available categories"""
        return list(CATEGORIES.keys())
