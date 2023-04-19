import json

from asgiref.sync import sync_to_async
from langchain import OpenAI
from langchain.chains.base import Chain
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.tools import BaseTool
from pydantic import BaseModel, root_validator
from pydantic import ValidationError

from .schemas import AppointmentSchema

from ..models import create_appointment


class AppointmentJSONException(Exception):
    pass


class AppointmentToolInputModel(BaseModel):
    @root_validator
    def validate_query(cls, json_str: str):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON")


def convert_json_to_obj(json_str: str):
    try:
        appointment = AppointmentSchema.parse_raw(json_str)
        return appointment.dict()
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = ".".join(error["loc"])
            message = error["msg"]
            if "field is required" in message:
                message = f"Please, provide {field} that works for you."
                error_messages.append(message)
            else:
                error_messages.append(f"{field}: {message}")
        final_msg = "\n".join(error_messages)
        raise AppointmentJSONException(final_msg)


def create_appointment_from_json_str(json_str: str) -> str:
    try:
        json_obj = convert_json_to_obj(json_str)
        return create_appointment(json_obj)
    except Exception as e:
        raise AppointmentJSONException(e)


class AppointmentTool(BaseTool):
    name = "Appointment tool"
    description = "Creates an appointment from a valid json string"

    def _run(self, json_str: str) -> str:
        try:
            return create_appointment_from_json_str(json_str)
        except Exception as e:
            return str(e)

    async def _arun(self, json_str: str) -> str:
        try:
            return await sync_to_async(create_appointment_from_json_str)(json_str)
        except Exception as e:
            return str(e)
