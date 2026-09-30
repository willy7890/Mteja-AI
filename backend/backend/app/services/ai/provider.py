from typing import Dict, Any
from app.services.classification_service import classification_service, IntentClassifierService


class ClassificationProvider:
    """Wrapper provider that standardizes classifier instantiation and prediction access."""

    def __init__(self, service: IntentClassifierService = classification_service):
        self.service = service

    def reload_artifact(self) -> None:
        """Reloads the underlying classifier model post-retraining."""
        self.service.load_model()

    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Provides intent classification matching system contract.

        Returns:
            Dict containing:
                - category (str)
                - confidence (float)
        """
        return self.service.predict(raw_text=text)


# Singleton instance for simple imports across services/engines
default_provider = ClassificationProvider()