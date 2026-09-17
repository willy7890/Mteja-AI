import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import select
from app.models.training_data import TrainingData

logger = logging.getLogger(__name__)


class KnowledgeBaseService:

    def __init__(self) -> None:
        self.documents: List[Dict[str, str]] = []
        self.load_from_file()

    def load_from_file(self) -> None:
        """Load the repository JSON and CSV knowledge sources."""
        data_path = Path(__file__).resolve().parents[1] / "data"
        json_path = data_path / "knowledge_base.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.documents.extend(
                        self._normalize_item(item) for item in json.load(f)
                    )
            except Exception as e:
                logger.error(f"Failed to load JSON knowledge base: {e}")

        for csv_path in data_path.glob("*.csv"):
            try:
                with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                    self.documents.extend(
                        self._normalize_item(row) for row in csv.DictReader(f)
                    )
            except Exception as e:
                logger.error("Failed to load CSV knowledge base %s: %s", csv_path, e)

    @staticmethod
    def _normalize_item(item: Dict[str, Any]) -> Dict[str, str]:
        question = str(item.get("question") or item.get("customer") or "").strip()
        answer = str(item.get("answer") or item.get("answers") or "").strip()
        category = str(item.get("category") or "").strip()
        return {
            "question": question,
            "answer": answer,
            "category": category,
            "content": f"{question} {answer} {category}".strip(),
        }

    async def load_from_db(self, db_session) -> None:
        """Load knowledge base dynamically from database TrainingData table."""
        try:
            result = await db_session.execute(select(TrainingData))
            rows = result.scalars().all()
            if rows:
                self.documents = [
                    {
                        "question": row.question,
                        "answer": row.answer,
                        "category": str(row.category or ""),
                        "content": f"{row.question} {row.answer}",
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to load KB from DB: {e}")

    def search(self, query: str, k: int = 3) -> str:
        """Search relevant Q&A matches for the given query."""
        if not self.documents:
            return "No knowledge base available."

        query_terms = set(query.lower().split())
        
        # Rank documents based on matching keyword count in content
        ranked_documents = sorted(
            self.documents,
            key=lambda doc: sum(
                term in doc["content"].lower() for term in query_terms
            ),
            reverse=True,
        )

        if not ranked_documents or not any(
            term in ranked_documents[0]["content"].lower() for term in query_terms
        ):
            return "No relevant knowledge base answer available."

        top_matches = ranked_documents[:k]
        
        # Return cleanly formatted Q&A blocks
        return "\n\n".join(
            f"Q: {doc['question']}\nA: {doc['answer']}"
            for doc in top_matches
            if doc["question"] or doc["answer"]
        )

    def best_answer(self, query: str) -> str | None:
        """Return the highest-overlap imported answer, when one exists."""
        if not self.documents:
            return None

        query_terms = set(query.lower().split())
        best_document = max(
            self.documents,
            key=lambda doc: sum(
                term in doc["content"].lower() for term in query_terms
            ),
        )
        score = sum(term in best_document["content"].lower() for term in query_terms)
        return best_document["answer"] if score and best_document["answer"] else None


kb_service = KnowledgeBaseService()