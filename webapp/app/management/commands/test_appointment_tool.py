import os
from django.core.management.base import BaseCommand

from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType, Tool
from langchain.agents.initialize import initialize_agent

from app.chatbot.tools import AppointmentTool, AppointmentToolInputModel


class Command(BaseCommand):
    help = "Runs my script"

    def handle(self, *args, **options):
        tool = AppointmentTool()
        tools = [
            Tool(
                name=tool.name,
                func=tool.run,
                description=tool.description,
            )
        ]
        llm = ChatOpenAI(temperature=0)
        json_text = """{
        "name": "A test appointment created by a tool",
        "date": "2023-05-01",
        "time": "15:30:00",
        "description": "This is a description of the appointment."
        }"""
        agent = initialize_agent(
            tools,
            llm,
            AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )
        res = agent.run(json_text)
        print(res)
