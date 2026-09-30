from typing import Literal
import re

LanguageType = Literal[
    "swahili",
    "english",
    "sheng",
    "code_switching",
    "mixed",
    "unknown"
]


class LanguageDetectionService:

    # Common Sheng words / patterns (Tanzania + Kenya)
    SHENG_KEYWORDS = {
        "msee", "manze", "bro", "sio", "noma", "poa", "sasa", "bana", "dane",
        "mzinga", "dame", "mresh", "mbao", "keja", "mtaa", "noma", "fala",
        "mbogi", "wazeeya", "msee", "noma", "poa sana", "sasa hivi", "bana",
        "nimechill", "nimefeel", "nimeget", "nimefika", "nimekat", "nimesort",
        "nimeconnect", "nimevibe", "nimechill", "nimeghost", "nimepress",
        "nimepunch", "nimeset", "nimekaanga", "nimekula", "nimeiva",
        "nimeiva", "nimeiva", "noma", "mbaya", "poa", "safi", "fiti",
        "noma", "kibao", "mzinga", "dame", "mresh", "keja", "mtaa"
    }

    SWAHILI_KEYWORDS = {
        "habari", "asante", "karibu", "tafadhali", "ndiyo", "hapana", "sawa",
        "nataka", "nina", "nime", "tuta", "tuna", "mimi", "wewe", "yeye",
        "sisi", "nyinyi", "wao", "leo", "kesho", "jana", "asubuhi", "jioni",
        "usiku", "chakula", "maji", "pesa", "bei", "ngapi", "wapi", "lini",
        "kwa nini", "namna gani", "naomba", "naweza", "ninaweza", "tafadhali"
    }

    ENGLISH_KEYWORDS = {
        "hello", "hi", "please", "thank", "thanks", "yes", "no", "okay", "ok",
        "want", "need", "have", "can", "will", "would", "should", "price",
        "how much", "where", "when", "what", "why", "how", "help", "support",
        "order", "buy", "pay", "delivery", "product", "service"
    }

    @staticmethod
    def detect(text: str) -> dict:
        if not text or not text.strip():
            return {
                "language": "unknown",
                "confidence": 0.0,
                "is_sheng": False,
                "is_code_switching": False,
                "dominant_language": "unknown",
                "details": {}
            }

        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)

        if not words:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "is_sheng": False,
                "is_code_switching": False,
                "dominant_language": "unknown",
                "details": {}
            }

        sheng_count = sum(1 for w in words if w in LanguageDetectionService.SHENG_KEYWORDS)
        swahili_count = sum(1 for w in words if w in LanguageDetectionService.SWAHILI_KEYWORDS)
        english_count = sum(1 for w in words if w in LanguageDetectionService.ENGLISH_KEYWORDS)

        total_keywords = sheng_count + swahili_count + english_count

        # Detect Sheng
        is_sheng = sheng_count >= 2 or (sheng_count >= 1 and (swahili_count + english_count) >= 1)

        # Detect code-switching (Swahili + English in same message)
        is_code_switching = swahili_count >= 1 and english_count >= 1

        # Determine dominant language
        if is_sheng:
            language = "sheng"
            dominant = "sheng"
        elif is_code_switching:
            language = "code_switching"
            dominant = "swahili" if swahili_count >= english_count else "english"
        elif swahili_count > english_count and swahili_count > 0:
            language = "swahili"
            dominant = "swahili"
        elif english_count > 0:
            language = "english"
            dominant = "english"
        else:
            language = "unknown"
            dominant = "unknown"

        confidence = min(0.95, (total_keywords / max(len(words), 1)) + 0.3) if total_keywords > 0 else 0.2

        return {
            "language": language,
            "confidence": round(confidence, 2),
            "is_sheng": is_sheng,
            "is_code_switching": is_code_switching,
            "dominant_language": dominant,
            "details": {
                "sheng_words": sheng_count,
                "swahili_words": swahili_count,
                "english_words": english_count,
                "total_words": len(words)
            }
        }