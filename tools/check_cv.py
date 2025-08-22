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
    cv: str = Field(description="")
    jd: str = Field(description="")


@tool("check_cv", args_schema=SummaryInput,
      description="Kiểm tra cv", return_direct=True)
def check_cv(cv: str, jd: str, config: RunnableConfig):
    if cv is None or jd is None:
        return ""

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Model ngôn ngữ lớn"
        temperature=0.5,  # Mức độ sáng tạo của model, từ 0 tới 1.
        max_tokens=None,  # Giới hạn token của Input, Output. Thường nên để tối đa 32K.
        timeout=None,
        max_retries=3,
        google_api_key=api_key  # API key đã lấy ở trên
    )

    response = model.invoke([SystemMessage(content=""" Bạn là nhân viên tuyển dụng của một công ty công nghệ.
                            Nhiệm vụ của bạn là từ các chỉ tiêu chính của JD và trọng số cho từng chỉ tiêu, hãy đánh giá CV của ứng viên, đưa ra kết quả và độ phù hợp.
                       """), HumanMessage(content=f"Nội dung JD: {jd}"), HumanMessage(content=f"Nội dung CV: {cv}")],
                            config)

    return response
