import io
import mimetypes
import os

from PIL import Image
from PyPDF2 import PdfReader
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class FileInput(BaseModel):
    message: str = Field(description="Nội dung cần tìm kiếm trên internet để cập nhật thêm thông tin trả lời.")
    file: dict = Field(description="File")


@tool("extract_file", args_schema=FileInput, return_direct=True)
def extract_file(message: str, file: dict) -> str:
    """
    Mục đích tool: trích xuất thông tin từ file ảnh hoặc pdf
    :param message:
    :param file:
    :return:
    """
    try:
        """
            file = {
                   "name": str,
                   "bytes": bytes,
                   "type": str  # mime type
            }
        """
        file_name = file["name"]
        file_bytes = file["bytes"]
        mime_type = file.get("type") or mimetypes.guess_type(file_name)[0]
        ext = os.path.splitext(file_name)[1].lower()

        # ========== IMAGE ==========
        if ext in [".png", ".jpg", ".jpeg"]:
            image = Image.open(io.BytesIO(file_bytes))
            return f"Ảnh {file_name} có kích thước {image.size[0]}x{image.size[1]} pixel, định dạng {image.format}"

        # ========== PDF ==========
        elif ext == ".pdf":
            reader = PdfReader(io.BytesIO(file_bytes))
            num_pages = len(reader.pages)
            text_preview = reader.pages[0].extract_text()[:300] if num_pages > 0 else ""
            return f"PDF {file_name} có {num_pages} trang.\nNội dung trang đầu:\n{text_preview}"

        # ========== DOCX ==========
        # elif ext == ".docx":
        #     doc = Document(io.BytesIO(file_bytes))
        #     paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        #     text_preview = "\n".join(paragraphs[:3])
        #     return f"Word {file_name} có {len(paragraphs)} đoạn văn.\nNội dung:\n{text_preview}"

        else:
            return f"File {file_name} có loại chưa hỗ trợ ({mime_type})"

    except Exception as e:
        return f"Lỗi khi phân tích file: {str(e)}"
