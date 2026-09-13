from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


MAX_DATE_RANGE_DAYS = 92


class AnalyticsDateRange(BaseModel):
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def _validate_range(cls, end_date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date must not be before start_date")
        if start_date and (end_date - start_date).days > MAX_DATE_RANGE_DAYS:
            raise ValueError(f"date range cannot exceed {MAX_DATE_RANGE_DAYS} days")
        return end_date


class ChannelBreakdown(BaseModel):
    channel: str
    conversation_count: int
    message_count: int


class AnalyticsOverviewResponse(BaseModel):
    organization_id: int
    start_date: date
    end_date: date

    total_conversations: int
    total_messages: int
    ai_resolved_conversations: int
    ai_resolution_rate: float

    avg_first_response_seconds: Optional[float] = None
    avg_resolution_seconds: Optional[float] = None
    avg_messages_per_conversation: float

    channel_breakdown: list[ChannelBreakdown]

    generated_at: datetime
    cached: bool = False


class ConversationVolumePoint(BaseModel):
    bucket_date: date
    conversation_count: int
    ai_resolved_count: int
    escalated_count: int


class ConversationAnalyticsResponse(BaseModel):
    organization_id: int
    start_date: date
    end_date: date

    total_conversations: int
    ai_resolved_conversations: int
    escalated_conversations: int
    open_conversations: int

    avg_first_response_seconds: Optional[float] = None
    avg_resolution_seconds: Optional[float] = None

    daily_volume: list[ConversationVolumePoint]

    generated_at: datetime
    cached: bool = False
    
    


class AIPerformancePoint(BaseModel):
    bucket_date: date
    total_conversations: int
    ai_resolved_count: int
    escalated_count: int
    ai_resolution_rate: float


class AIPerformanceResponse(BaseModel):
    organization_id: int
    start_date: date
    end_date: date

    total_conversations: int
    ai_resolved_conversations: int
    escalated_conversations: int
    ai_resolution_rate: float
    escalation_rate: float

    daily_trend: list[AIPerformancePoint]

    generated_at: datetime
    cached: bool = False


class ChannelMetric(BaseModel):
    channel: str
    conversation_count: int
    message_count: int
    share_pct: float
    ai_resolved_count: int
    ai_resolution_rate: float


class ChannelAnalyticsResponse(BaseModel):
    organization_id: int
    start_date: date
    end_date: date

    total_conversations: int
    channels: list[ChannelMetric]

    generated_at: datetime
    cached: bool = False


class ResponseTimeByChannel(BaseModel):
    channel: str
    avg_first_response_seconds: Optional[float] = None
    avg_resolution_seconds: Optional[float] = None
    conversation_count: int


class ResponseTimeResponse(BaseModel):
    organization_id: int
    start_date: date
    end_date: date

    avg_first_response_seconds: Optional[float] = None
    avg_resolution_seconds: Optional[float] = None
    by_channel: list[ResponseTimeByChannel]

    generated_at: datetime
    cached: bool = False    