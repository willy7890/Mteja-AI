def get_fallback_response(language: str = "swahili") -> str:
    fallbacks = {
        "swahili": "Samahani, sijaweza kuchakata ombi lako kwa sasa. Tafadhali jaribu tena au wasiliana na mhudumu wetu.",
        "english": "Sorry, I couldn't process your request right now. Please try again or contact our support team.",
        "sheng": "Bro samahani, sijaweza process hiyo sasa hivi. Jaribu tena ama ongea na support wetu.",
        "code_switching": "Samahani, sijaweza kuchakata ombi lako kwa sasa. Please try again or contact support.",
    }
    return fallbacks.get(language, fallbacks["swahili"])