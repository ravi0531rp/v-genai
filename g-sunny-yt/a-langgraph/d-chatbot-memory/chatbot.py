from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, TypedDict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv
load_dotenv()


GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT=os.getenv("LANGCHAIN_PROJECT")


os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GROQ_API_KEY"]= GROQ_API_KEY
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"]=LANGCHAIN_PROJECT


memory = MemorySaver()


@tool
def search(query: str):
    """this is my custom tool that tells the weather of a region"""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

llm=ChatGroq(model_name="llama3-groq-8b-8192-tool-use-preview")

tools=[search]
tool_node=ToolNode(tools)
llm_with_tool=llm.bind_tools(tools)


# node
def call_model(state: MessagesState):
    messages = state['messages']
    response = llm_with_tool.invoke(messages)
    return {"messages": [response]}

# edge
def router_function(state: MessagesState) -> Literal["tools", END]:
    #print(f"here is a state from should continue {state}")
    messages = state['messages']
    last_message = messages[-1]
    #print(f"here is a last message from should continue {last_message}")
    if last_message.tool_calls:
        return "tools"
    return END


# Define a new graph
workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges("agent",router_function,{"tools": "tools", END: END})

workflow.add_edge("tools", 'agent')

looped_app = workflow.compile(checkpointer = memory)

# this is like debug mode ; we can directly invoke too, no need to stream
for output in looped_app.stream({"messages": ["what is the weather in sf"]}):
    for key,value in output.items():
        print(f"here is output from {key}")
        print("_______")
        print(value)
        print("\n")



# Memory usage

config = {"configurable": {"thread_id": "1"}}
events = looped_app.stream(
    {"messages": ["Hi there! My name is Ravi."]}, config, stream_mode="values"
)

events = looped_app.stream(
    {"messages": ["can you tell me what was my name?"]}, config, stream_mode="values"
) # It will remember since we are in the same thread

print(memory.get(config))