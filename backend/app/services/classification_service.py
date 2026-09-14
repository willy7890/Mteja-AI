import os
from pathlib import Path
from typing import Any
import joblib

MODEL_PATH = Path(__file__).resolve().parents[1] / "ml_models" / "mteja_category_classifier.pkl"


class ClassificationService:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = Path(model_path)
        self.model = None
        self._last_mtime: float = 0  # Inahifadhi muda wa mwisho file lilipobadilishwa
        self.load_model()

    def load_model(self) -> None:
        """Yukuta na kupakia model pkl, au ku-reload ikiwa faili limebadilishwa."""
        if not self.model_path.is_file():
            raise FileNotFoundError(f"Trained classifier not found: {self.model_path}")

        current_mtime = os.path.getmtime(self.model_path)
        
        # Kupakia model tu kama bado haijapakiwa au kama faili lime-update (Auto-retrained)
        if self.model is None or current_mtime > self._last_mtime:
            self.model = joblib.load(self.model_path)
            self._last_mtime = current_mtime
            print(f"✅ Loaded updated classifier model from: {self.model_path}")

    def classify_message(self, text: str) -> dict[str, Any]:
        """Return the predicted category and the pipeline confidence."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Message text must be a non-empty string.")

        # Angalia kama kuna model mpya iliyofanyiwa retraining kabla ya ku-predict
        self.load_model()

        normalized_text = text.lower().strip()
        category = str(self.model.predict([normalized_text])[0])
        probabilities = self.model.predict_proba([normalized_text])[0]
        confidence = float(max(probabilities))
        
        return {"category": category, "confidence": confidence}

    def classify_text(self, text: str) -> str:
        """Backward-compatible category-only classifier API."""
        return self.classify_message(text)["category"]


classifier_service = ClassificationService()