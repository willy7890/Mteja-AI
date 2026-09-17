ESCALATION_KEYWORDS = [
    "nataka kuongea na mtu", "human", "ongea na msimamizi", "malalamiko",
    "refund", "sheria", "mwanasheria", "nimekasirika", "hii ni upuuzi",
    "manager", "supervisor", "complaint",
]


def should_escalate_by_keywords(message: str) -> str | None:
    lowered = message.lower()
    for keyword in ESCALATION_KEYWORDS:
        if keyword in lowered:
            return f"Customer message contains escalation trigger: '{keyword}'"
    return None


def should_escalate_by_ai_response(ai_reply: str) -> str | None:
    """AI yenyewe inaweza kusema haiwezi kusaidia."""
    uncertainty_phrases = [
        "sijui", "sina uhakika", "let me connect you", "nakuunganisha na",
        "siwezi kukusaidia na hilo",
    ]
    lowered = ai_reply.lower()
    for phrase in uncertainty_phrases:
        if phrase in lowered:
            return "AI expressed uncertainty or inability to help"
    return None