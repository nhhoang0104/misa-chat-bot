import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# Load .env file
load_dotenv()

# Get values
api_key = os.getenv("GEMINI_API_KEY")


class SummaryInput(BaseModel):
    message: str = Field(description="")
    content: str = Field(description="")


@tool("summary", args_schema=SummaryInput,
      description="Tóm tắt sách", return_direct=True)
def summary(message: str, content: str, config: RunnableConfig) -> str:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Model ngôn ngữ lớn"
        temperature=0.5,  # Mức độ sáng tạo của model, từ 0 tới 1.
        max_tokens=None,  # Giới hạn token của Input, Output. Thường nên để tối đa 32K.
        timeout=None,
        max_retries=3,
        google_api_key=api_key  # API key đã lấy ở trên
    )

    response = model.invoke([SystemMessage(content="Tóm tắt nội dung văn bản"), HumanMessage(content=content)], config)

    return response
