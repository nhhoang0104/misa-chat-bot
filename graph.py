import os

from dotenv import load_dotenv
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

from agent_state import AgentState
from system_prompt import system_prompt
from tools.extract_file import extract_file

# Load .env file
load_dotenv()

# Get values
api_key = os.getenv("GEMINI_API_KEY")
graph = StateGraph(AgentState)

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Model ngôn ngữ lớn"
    temperature=0.5,  # Mức độ sáng tạo của model, từ 0 tới 1.
    max_tokens=None,  # Giới hạn token của Input, Output. Thường nên để tối đa 32K.
    timeout=None,
    max_retries=3,
    google_api_key=api_key  # API key đã lấy ở trên
)

tools = [extract_file]
tools_by_name = {tool.name: tool for tool in tools}

agent = model.bind_tools(tools)


# Define our tool node
def call_tools(state: AgentState):
    outputs = []

    for tool_call in state["messages"][-1].tool_calls:
        tool_name = tool_call["name"]

        if tool_name not in tools_by_name:
            continue

        args = tool_call["args"]

        # Nếu tool cần file -> inject file từ session
        if tool_name == "extract_file":
            # lấy file cuối cùng user upload từ session
            file_dict = None
            # for m in reversed(st.session_state.messages):
            #     if "file" in m:
            #         file_dict = m["file"]
            #         file_dict["bytes"] = open(m["file"]["name"], "rb").read()  # HOẶC cache bytes lại
            #         break
            if file_dict:
                args["file"] = file_dict

        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])

        outputs.append(
            ToolMessage(
                content=tool_result,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": outputs}


# Define call_model
def call_model(
        state: AgentState,
        config: RunnableConfig,
):
    list_input = [SystemMessage(content=system_prompt)]

    for msg in state["messages"]:
        list_input.append(msg)

    # Invoke the model with the system prompt and the messages
    response = agent.invoke(list_input, config)

    # We return a list, because this will get added to the existing messages state using the add_messages reducer
    return {"messages": [response]}


# Define the conditional edge that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]

    # If the last message is not a tool call, then we finish
    if not messages[-1].tool_calls:
        return "end"

    # default to continue
    return "continue"


graph.add_node("ask_question", call_model)
graph.add_node("call_tools", call_tools)

graph.set_entry_point("ask_question")
graph.add_conditional_edges("ask_question", should_continue, {"continue": "call_tools", "end": END})
graph.add_edge("call_tools", "ask_question")

memory = MemorySaver()
graph_builder = graph.compile(checkpointer=memory)
