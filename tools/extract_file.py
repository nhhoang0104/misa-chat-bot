import os

import PyPDF2
from PIL import Image
from PyPDF2 import PdfReader
from langchain_core.tools import tool
from pydantic import BaseModel, Field

UPLOAD_FOLDER = "uploads"


class FileInput(BaseModel):
    message: str = Field(description="")
    file_name: str = Field(description="")


@tool("extract_file", args_schema=FileInput,
      description="Trích xuất, lấy dữ liệu từ ảnh hoặc file sách do người dùng cung cấp", return_direct=True)
def extract_file(message: str, file_name: str) -> str:
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
        ext = os.path.splitext(file_name)[1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, file_name)

        # ========== IMAGE ==========
        if ext in [".png", ".jpg", ".jpeg"]:
            img = Image.open(filepath)
            return f"Ảnh {file_name} có kích thước"

        # ========== PDF ==========
        elif ext == ".pdf":
            reader = PdfReader(filepath)
            num_pages = len(reader.pages)
            text_preview = reader.pages[0].extract_text()[:300] if num_pages > 0 else ""

            content = convert_pdf_to_text(filepath)
            return f"Nội dung file: {content}"

        # ========== DOCX ==========
        # elif ext == ".docx":
        #     doc = Document(io.BytesIO(file_bytes))
        #     paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        #     text_preview = "\n".join(paragraphs[:3])
        #     return f"Word {file_name} có {len(paragraphs)} đoạn văn.\nNội dung:\n{text_preview}"

        else:
            return f"File {file_name} có loại chưa hỗ trợ"

    except Exception as e:
        return f"Lỗi khi phân tích file: {str(e)}"


def convert_pdf_to_text(file_path: str) -> str:
    """
    Nhận một đường dẫn PDF, chuyển đổi nó thành văn bản và trả về.
    :param file_path: đường dẫn đến file PDF
    :return: toàn bộ text trong PDF
    """
    try:
        if not file_path.lower().endswith(".pdf"):
            return "File phải là PDF."

        text = ""
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)

            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"

        if not text.strip():
            return "Không thể trích xuất văn bản từ file PDF. File có thể là hình ảnh hoặc bị mã hóa."

        return text

    except PyPDF2.errors.PdfReadError:
        return "File PDF bị hỏng hoặc không hợp lệ."
    except Exception as e:
        return f"Lỗi máy chủ: {str(e)}"
