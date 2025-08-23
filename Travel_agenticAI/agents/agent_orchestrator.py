from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from models.llm_generator import build_llm
from agents.tools_define import get_weather_tool, get_flights_tool, get_visa_requirements_tool

def create_agent():

    tools = [
        get_visa_requirements_tool,
        get_weather_tool,
        get_flights_tool
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert AI travel agent. Your goal is to provide comprehensive, helpful, and friendly travel advice.
                
                - You have access to a set of tools to get real-time information on weather, flights, and visa requirements.
                - **You also have a knowledge base you can search for travel tips, destination guides, and cultural information.**
                - When a user asks a question, first understand their intent. Then, decide which tool(s), if any, are necessary to answer the question.
                - Call the tools with the correct inputs to gather the information.
                - Once you have the information, synthesize it into a clear, concise, and helpful response.
                - If you don't have enough information, you can ask clarifying questions.
                - Do not make up information. If a tool fails or doesn't have the answer, state that clearly.
                - Always assume the user's passport is from India unless they specify otherwise.
                - Respond in Markdown format for better readability.""",
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    llm = build_llm()

    agent = create_tool_calling_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent_executor