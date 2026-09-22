import os
import logging
import joblib
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../models/intent_classifier.pkl")
)


class ClassificationService:
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.pipeline = None
        self.load_model()

    def load_model(self) -> None:
        """Inapakia (load) model ya machine learning kama ipo."""
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                logger.info(f"[CLASSIFICATION] Model imepakiwa kutoka {self.model_path}")
            except Exception as e:
                logger.error(f"[CLASSIFICATION] Imeshindwa kupakia model: {e}")
                self.pipeline = None
        else:
            logger.warning(
                f"[CLASSIFICATION] Model haipatikani kwenye path: {self.model_path}. Inatumia mfumo wa akiba (fallback)."
            )
            self.pipeline = None

    def predict(self, raw_text: str) -> Dict[str, Any]:
        """Inatambua intent na kutoa kiwango cha uaminifu (confidence)."""
        if not raw_text or not raw_text.strip():
            return {"intent": "general_inquiry", "category": "general_inquiry", "confidence": 0.0}

        # Fallback ikiwa model bado haijatengenezwa/kupakiwa
        if self.pipeline is None:
            return {"intent": "general_inquiry", "category": "general_inquiry", "confidence": 0.5}

        cleaned_text = raw_text.strip()

        try:
            # Kutabiri daraja/intent ya ujumbe
            predicted_category = str(self.pipeline.predict([cleaned_text])[0])

            # Kukokotoa kiwango cha uaminifu (confidence score)
            confidence = 0.8
            if hasattr(self.pipeline, "predict_proba"):
                probabilities = self.pipeline.predict_proba([cleaned_text])[0]
                confidence = float(np.max(probabilities))

            return {
                "intent": predicted_category,
                "category": predicted_category,
                "confidence": round(confidence, 4),
            }
        except Exception as e:
            logger.error(f"[CLASSIFICATION] Hitilafu wakati wa predict: {e}")
            return {"intent": "general_inquiry", "category": "general_inquiry", "confidence": 0.5}

    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Njia mbadala (alias) ya kuita predict() kwa utangamano wa mfumo."""
        return self.predict(text)

    def classify_message(self, text: str) -> Dict[str, Any]:
        """Compatibility alias used by the inbound message services."""
        return self.predict(text)


# Instance zinazohitajika kwenye sehemu mbalimbali za mradi
classifier_service = ClassificationService()
classification_service = classifier_service