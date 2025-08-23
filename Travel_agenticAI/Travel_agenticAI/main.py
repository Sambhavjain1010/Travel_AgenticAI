import streamlit as st
from agents.agent_orchestrator import create_agent
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="🤖 AI Travel Agent", layout="wide")
st.title("🤖 Your Personal AI Travel Agent")

agent_executor = create_agent()

# Initializing chat history in st.session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(
            content="Hello! I'm your expert AI travel agent. Where are you heading next?"
        )
    ]

# previous messages
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Ask me anything about your travel plans!")

if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)
    
    with st.chat_message("AI"):
        with st.spinner("Thinking..."):
            response = agent_executor.invoke(
                {
                    "input": user_query,
                    "chat_history": st.session_state.chat_history
                }
            )

            st.markdown(response["output"])
    
    st.session_state.chat_history.append(AIMessage(content=response["output"]))
