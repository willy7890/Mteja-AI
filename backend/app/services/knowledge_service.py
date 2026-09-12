from sqlalchemy import select
from app.models.training_data import TrainingData


class KnowledgeBaseService:
    def __init__(self) -> None:
        self.documents: list[dict[str, str]] = []

    async def load_from_db(self, db_session) -> None:
        result = await db_session.execute(select(TrainingData))
        rows = result.scalars().all()
        self.documents = [
            {
                "question": row.question,
                "answer": row.answer,
                "category": str(row.category or ""),
                # "content" ndiyo tunayotafuta ndani yake wakati wa search
                "content": f"{row.question} {row.answer}",
            }
            for row in rows
        ]

    def search(self, query: str, k: int = 3) -> str:
        if not self.documents:
            return "No knowledge base available."

        query_terms = set(query.lower().split())
        ranked_documents = sorted(
            self.documents,
            key=lambda document: sum(
                term in document["content"].lower() for term in query_terms
            ),
            reverse=True,
        )

        top_matches = ranked_documents[:k]
        # Tunarudisha Q&A wazi, si maneno yaliyochanganywa tu
        return "\n\n".join(
            f"Q: {doc['question']}\nA: {doc['answer']}" for doc in top_matches
        )


kb_service = KnowledgeBaseService()