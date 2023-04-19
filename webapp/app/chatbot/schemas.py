from datetime import datetime
from pydantic import BaseModel, validator


class ChatResponse(BaseModel):
    """Chat response schema."""

    username: str
    message: str
    type: str

    @validator("username")
    def sender_must_be_bot_or_you(cls, v):
        if v not in ["bot", "you"]:
            raise ValueError("username must be bot or you")
        return v

    @validator("type")
    def validate_message_type(cls, v):
        if v not in ["start", "stream", "end", "error", "info", "clarification"]:
            raise ValueError("type must be start, stream or end")
        return v


class AppointmentSchema(BaseModel):
    name: str
    date: str
    time: str
    description: str = None

    @validator("date")
    def date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError('date field must be in the format "YYYY-MM-DD"')
        return v

    @validator("time")
    def time_required(cls, v):
        if not v:
            raise ValueError("time field is required")
        return v
