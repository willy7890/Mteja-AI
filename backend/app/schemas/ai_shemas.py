from pydantic import BaseModel, Field
from typing import Optional, Literal


# ---------- Request Schemas ----------

class GenerateReplyRequest(BaseModel):
    conversation_id: int = Field(..., description="ID of the conversation to reply to")
    organization_id: int = Field(..., description="ID of the organization (tenant)")
    agent_type: Literal["sales", "support", "marketing", "followup"] = Field(
        default="support",
        description="Which agent persona should handle this reply",
    )
    max_tokens: Optional[int] = Field(
        default=500, description="Max tokens for the generated reply"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 42,
                "organization_id": 7,
                "agent_type": "support",
                "max_tokens": 500,
            }
        }


class SampleMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class TestPromptRequest(BaseModel):
    system_prompt: str = Field(..., description="The system prompt to test")
    sample_messages: list[SampleMessage] = Field(
        default_factory=list,
        description="A short fake conversation to test the prompt against",
    )
    max_tokens: Optional[int] = Field(default=500)

    class Config:
        json_schema_extra = {
            "example": {
                "system_prompt": "You are Mteja AI, a support assistant for Acme Ltd...",
                "sample_messages": [
                    {"role": "user", "content": "Bidhaa yenu ina bei gani?"}
                ],
                "max_tokens": 300,
            }
        }


# ---------- Response Schemas ----------

class GenerateReplyResponse(BaseModel):
    success: bool
    reply: str
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "reply": "Karibu! Bei ya bidhaa hii ni Tsh 25,000.",
                "latency_ms": 842.3,
                "tokens_used": 156,
                "error": None,
            }
        }


class TestPromptResponse(BaseModel):
    content: str
    tokens_used: int
    latency_ms: float~