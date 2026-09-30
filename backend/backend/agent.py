import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Define graph state with message history
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize model
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Define the node that generates the response using conversation history
def call_model(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build the workflow graph
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

app = workflow.compile()

if __name__ == "__main__":
    print("Mteja AI Agent is ready! Type your question below (type 'exit' to quit):\n")
    chat_history = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        chat_history.append(HumanMessage(content=user_input))
        result = app.invoke({"messages": chat_history})
        assistant_message = result["messages"][-1]
        print(f"\nAI: {assistant_message.content}\n")
        chat_history = result["messages"]