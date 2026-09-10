import json
from langchain_core.documents import Document


class KnowledgeBaseService:
    def __init__(self):
        # Load the JSON knowledge base file
        with open("app/data/knowledge_base.json", "r", encoding="utf-8") as f:
            items = json.load(f)
        
        # Create Document objects with title, content, and metadata
        self.documents = [
            Document(
                page_content=f"{item['title']}: {item['content']}",
                metadata={"category": item["category"]},
            )
            for item in items
        ]
    
    def search(self, query: str, k: int = 2) -> str:
        """
        Simple search function that returns the top k documents
        matching the query. For now, returns all documents as context.
        """
        if not self.documents:
            return "No knowledge base available."
        
        # Simple approach: return all documents as context
        # In production, use vector similarity search
        context = "\n".join([doc.page_content for doc in self.documents[:k]])
        return context


# Initialize the knowledge base service
kb_service = KnowledgeBaseService()