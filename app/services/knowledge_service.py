import json
from langchain_core.documents import Document


class KnowledgeBaseService:
    def __init__(self):
        with open("app/data/knowledge_base.json", "r", encoding="utf-8") as f:
            items = json.load(f)
        
        self.documents = [
            Document(
                page_content=f"{item['title']}: {item['content']}",
                metadata={"category": item["category"]},
            )
            for item in items
        ]
    
    def search(self, query: str, k: int = 2) -> str:
       
        if not self.documents:
            return "No knowledge base available."
        
        context = "\n".join([doc.page_content for doc in self.documents[:k]])
        return context

kb_service = KnowledgeBaseService()