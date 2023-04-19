import os
import re

from datetime import datetime
from typing import List, Union

import chromadb
from langchain import FewShotPromptTemplate, PromptTemplate, OpenAI
from langchain.agents import Tool, AgentOutputParser, load_tools
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import (
    BaseChatPromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import AgentAction, AgentFinish, HumanMessage
from langchain.vectorstores import Chroma

from .tools import AppointmentTool, AppointmentToolInputModel


def init_retriever():
    EMBEDDINGS = OpenAIEmbeddings()
    PERSIST_DIRECTORY = "../../../vector_db"
    ABS_PATH = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(ABS_PATH, PERSIST_DIRECTORY)
    CONDITIONS = "conditions"

    settings = chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=DB_DIR,
        anonymized_telemetry=False,
    )
    db = Chroma(
        collection_name=CONDITIONS,
        embedding_function=EMBEDDINGS,
        client_settings=settings,
        persist_directory=DB_DIR,
    )
    try:
        return db.as_retriever(search_type="mmr")
    except:
        raise Exception(
            "Could not load vector database. Please run `python write_data_to_vector_db.py` to create it."
        )


def get_intent_prompt():
    INTENT_EXAMPLES = [
        {"input": "Hey, I have a headache", "intent": "symptom"},
        {"input": "What about May 5th", "intent": "appointment"},
        {"input": "I want to see a doctor this week", "intent": "appointment"},
        {"input": "Tomorrow works?", "intent": "appointment"},
        {"input": "I don't feel good", "intent": "symptom"},
        {"input": "hey, how are you?", "intent": "None"},
        {"input": "how does this shit work?", "intent": "None"},
        {"input": "I love you!", "intent": "None"},
        {"input": "this is bullshit", "intent": "None"},
        {"input": "a random stuff", "intent": "None"},
    ]
    example_formatter_template = """
    input: {input}\n
    intent: {intent}\n
    """

    example_prompt = PromptTemplate(
        input_variables=["input", "intent"],
        template=example_formatter_template,
    )
    few_shot_prompt = FewShotPromptTemplate(
        examples=INTENT_EXAMPLES,
        example_prompt=example_prompt,
        prefix="You are an intent classification bot.",
        suffix="You should output only an intent name without accompanying texts.",
        input_variables=[],
        example_separator="\n\n",
    )
    system_message_prompt = SystemMessagePromptTemplate(prompt=few_shot_prompt)
    human_prompt = PromptTemplate(
        input_variables=["input"], template="input: {input}\nintent: "
    )
    human_message_prompt = HumanMessagePromptTemplate(prompt=human_prompt)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    return chat_prompt


def get_symptoms_qa_prompt():
    prompt_template = """Use the following pieces of context to answer the symptoms question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    After answering the question, ask if they want to schedule an appointment with a doctor.

    {context}

    Question: {question}
    Helpful Answer:"""
    return PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )


def get_general_chat_prompt():
    template = """You are a care coordinator bot that makes sure that users are healthy
    and offers to schedule an appointment with a doctor."""
    prompt = PromptTemplate(
        template=template,
        input_variables=[],
    )
    system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    return chat_prompt


class AppointmentsPromptTemplate(BaseChatPromptTemplate):
    template: str
    tools: List[Tool]

    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]


class AppointmentsOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(
            tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output
        )


def get_appointment_tools(stream_manager):
    appointment_tool = AppointmentTool()
    human_tool = load_tools(
        ["human"],
        callback_manager=stream_manager,
        prompt_func=print,
        vervose=True,
    )[0]
    tools = [
        Tool(
            name=appointment_tool.name,
            func=appointment_tool.run,
            description=appointment_tool.description,
        ),
        Tool(
            name=human_tool.name,
            description=human_tool.description,
            func=human_tool.run,
        ),
    ]
    # print("@@@@", human_tool)
    return tools


def get_appointment_chat_prompt(tools: List[Tool]):
    template = """You are a care coordinator bot that makes sure that users
    can schedule an appointment with a doctor. Your job is to ask the user for details
    if user provides complete information, you should output a JSON string without any accompanying texts.

    You have access to the following tools:
    {tools}

    You should call the appointments tool only if you have enough information to form an appointment JSON.
    The appointments tool accepts a JSON string of the following format:
    ```json
    {{
        "name": "A helpful name for the appointment",
        "date": "YYYY-MM-DD",
        "time": "HH:MM",
        "description": "You can put information about the user's health condition here"
    }}
    ```
    else if user didn't provide complete information, you should ask the user for the missing information.

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now have enough information to form an appointment JSON
    Final Answer: I have formed a JSON string, created an appointment using the provided tool.

    Begin! Remember to ask for appointment details.

    Question: {input}
    {agent_scratchpad}"""

    return AppointmentsPromptTemplate(
        template=template, tools=tools, input_variables=["input", "intermediate_steps"]
    )


def get_appointment_json_prompt():
    template = """You are a care coordinator bot's appointments tool.
    You should take Current conversation and Human input
    and return a JSON string WITHOUT ANY ACCOMPANYING TEXTS.
    JSON fields:
    name: appointment title. Come up with it based on the conversation history
    date: appointment date. Leave empty if not provided. Don't make it up!
    time: appointment time. Leave empty if not provided. Don't make it up!
    description: put here user's complaints (health condition messages).

    Under "Current conversation:" below there might be name, date or time.
    Reuse them ONLY if relevant info is there: name, date, time, or description.
    Output format (see, no accompanying text, just JSON):
    ```
    {{
        "name": "Appointment title derived from the current conversation",
        "date": "YYYY-MM-DD",
        "time": "HH:MM",
        "description": "put here user's complaints (health condition messages)"
    }}
    ```
    Remember to return a JSON with data derived from conversation!
    Don't make up answers!
    
    Current date and time is: %s
    
    Current conversation:
    {history}
    Human: {input}
    """ % (
        datetime.now()
    )
    prompt = PromptTemplate(
        template=template,
        input_variables=["history", "input"],
    )
    system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)
    human_template = "{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    return chat_prompt
