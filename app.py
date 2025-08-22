import os
import time
from datetime import datetime, timedelta

import pytz
import streamlit as st

st.set_page_config(layout="wide", page_title="Agent Chat", page_icon="🤖")

import asyncio
import json
from uuid import uuid4
from typing import AsyncGenerator

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_current_time() -> str:
    now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
    if now.weekday() < 6:
        weekday = f"thứ {now.weekday() + 2}"
    else:
        weekday = "chủ nhật"

    current_time = f"{weekday}, ngày {now.day:02d}/{now.month:02d}/{now.year}"
    return current_time


def get_this_week_time() -> dict:
    now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))

    monday = now - timedelta(now.weekday() - 0)
    monday = f"ngày {monday.day:02d}/{monday.month:02d}/{monday.year}"

    sunday = now + timedelta(6 - now.weekday())
    sunday = f"ngày {sunday.day:02d}/{sunday.month:02d}/{sunday.year}"
    return {
        "monday": monday,
        "sunday": sunday
    }


# ========== Page Config ==========
st.title("Chat with Agent")
st.button("Clear message", on_click=lambda: st.session_state.clear(), key="clear_message_btn")

# ========== Init Session State ==========
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "config" not in st.session_state:
    current_time = get_current_time()
    week_time = get_this_week_time()

    st.session_state.config = {
        "configurable": {
            "env": "test",
            "app": "Agent",
            "user_id": "Guest",
            "user_name": "Guest",
            "gender": "Male",
            "x_birthdate": "01/01/2000",
            "response_markdown": True,
            "message_id": "",
            "version": 4,
            "language": "",
            "this_monday": week_time["monday"],
            "this_sunday": week_time["sunday"],
            "current_time": current_time,
            "thread_id": st.session_state.session_id,
        },
        "recursion_limit": 15
    }

# ========== Config UI ==========
with st.expander("Config"):
    config = st.session_state.config["configurable"]
    col1, col2, col3 = st.columns(3)
    config["user_name"] = col1.text_input("User Name", value=config["user_name"])
    config["gender"] = col2.text_input("Gender", value=config["gender"])
    config["x_birthdate"] = col3.text_input("Date of Birth", value=config["x_birthdate"])

    if st.button("Submit Config", key="submit_config_btn"):
        session_id = str(uuid4())
        st.session_state.session_id = session_id

        st.session_state.config = {
            "configurable": config
        }

from graph import graph_builder


# ========== Process Events ==========
async def process_events(inputs: dict) -> AsyncGenerator[str, None]:
    async for event in graph_builder.astream_events(inputs, config=st.session_state.config, version="v1"):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield content

        elif kind == "on_tool_start":
            tool_name = event["name"]
            tool_input = event["data"].get("input", {})
            output = f"\n\n➡️ Tool `{tool_name}` called\n\n"

            if tool_input:  # Only add content if input is not empty
                # Format tool input consistently
                if isinstance(tool_input, str):
                    formatted_input = tool_input
                else:
                    try:
                        formatted_input = json.dumps(tool_input, indent=2, ensure_ascii=False, default=str)
                    except:
                        formatted_input = str(tool_input)

                output += f" with:\n```\n{formatted_input}\n```"

            yield output

        elif kind == "on_tool_end":
            pass


# ========== Async to Sync Generator ==========
def to_sync_generator(async_func, *args, **kwargs):
    async_gen = async_func(*args, **kwargs)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        while True:
            try:
                yield loop.run_until_complete(anext(async_gen))
            except StopAsyncIteration:
                break
    finally:
        loop.close()


# ========== Show Chat History ==========
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict):
            st.json(message["content"])
        else:
            st.markdown(message["content"], unsafe_allow_html=True)

## ========== Chat Input ==========
# if prompt := st.chat_input("What is up?", max_chars=1000):
#     inputs = {"messages": [("user", prompt)]}
#
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)
#
#     with st.chat_message("assistant"):
#         start_time = time.time()
#         response = st.write_stream(to_sync_generator(process_events, inputs))
#         end_time = time.time() - start_time
#
#         response_id = uuid4().hex
#         st.write(f"⏱️ **Processed in**: {round(end_time, 2)}s")
#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": response,
#             "id": response_id,
#             "stars": 0
#         })

# ========== Chat Input + File Upload ==========
with st.container():
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

    col1, col2 = st.columns([6, 2])

    with col1:
        prompt = st.chat_input("Nhập tin nhắn...", max_chars=1000)

    with col2:
        uploaded_file = st.file_uploader(
            "📎",
            type=["png", "jpg", "jpeg", "pdf"],
            key="chat_upload",
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ========== Handle Message ==========
if prompt:  # chỉ gửi khi có text
    user_message = {"role": "user", "content": prompt}

    file_bytes = None
    ext = None
    file_info = ""

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        user_message["file"] = {
            "name": uploaded_file.name,
            "bytes": file_bytes,
            "type": uploaded_file.type
        }

        file_info = f"\n\n[File đính kèm: {uploaded_file.name}, loại {uploaded_file.type}, kích thước {len(file_bytes)} bytes]"

        filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(filepath, "wb") as f:
            f.write(file_bytes)

    # Lưu tin nhắn user
    st.session_state.messages.append(user_message)

    # Hiển thị tin nhắn user
    with st.chat_message("user"):
        st.markdown(prompt)

        if uploaded_file is not None:
            if ext in [".png", ".jpg", ".jpeg"]:
                st.image(file_bytes, caption=uploaded_file.name, use_container_width=True)
            elif ext == ".pdf":
                st.download_button(
                    label=f"📄 Xem {uploaded_file.name}",
                    data=file_bytes,
                    file_name=uploaded_file.name,
                    mime="application/pdf"
                )
            elif ext == ".docx":
                st.download_button(
                    label=f"📄 Tải {uploaded_file.name}",
                    data=file_bytes,
                    file_name=uploaded_file.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    # Chuẩn bị input cho graph
    inputs = {
        "messages": [("user", prompt + " " + file_info)],
    }

    # Assistant trả lời
    with st.chat_message("assistant"):
        start_time = time.time()
        response = st.write_stream(
            to_sync_generator(process_events, inputs)
        )
        end_time = time.time() - start_time

        response_id = uuid4().hex
        st.write(f"⏱️ **Processed in**: {round(end_time, 2)}s")
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "id": response_id,
            "stars": 0
        })
