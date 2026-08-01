# Quiz App Configuration

# API Settings
API_SETTINGS = {
    "base_url": "https://opentdb.com/api.php",
    "amount": 10,  # Number of questions per quiz
    "difficulty": "medium",  # easy, medium, hard
    "type": "multiple"  # Question type
}

# Categories (Open Trivia Database)
CATEGORIES = {
    "general": 9,
    "books": 10,
    "film": 11,
    "music": 12,
    "science": 17,
    "sports": 21,
    "geography": 22,
    "history": 23,
    "politics": 24,
    "technology": 18,
    "random": None  # Random category
}

# UI Settings
UI_SETTINGS = {
    "window_width": 900,
    "window_height": 650,
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "bg_header": "#0f3460",
    "color_accent": "#00d4ff",
    "color_success": "#00ff00",
    "color_error": "#ff6b6b"
}
