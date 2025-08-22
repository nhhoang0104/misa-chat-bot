from typing import TypedDict, Sequence, Union

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep, RemainingSteps
from pydantic import BaseModel
from typing_extensions import Annotated

StructuredResponse = Union[dict, BaseModel]

import os


class UploadedFileInfo:
    def __init__(self, uploaded_file):
        self.name: str = uploaded_file.name
        self.type: str = uploaded_file.type
        self.bytes: bytes = uploaded_file.read()
        self.ext: str = os.path.splitext(uploaded_file.name)[1].lower()

    @property
    def is_image(self) -> bool:
        return self.ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]

    @property
    def is_pdf(self) -> bool:
        return self.ext == ".pdf"

    @property
    def is_docx(self) -> bool:
        return self.ext == ".docx"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "bytes": self.bytes,
            "ext": self.ext,
        }


class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]

    is_last_step: IsLastStep

    remaining_steps: RemainingSteps

    structured_response: StructuredResponse

    next: str

    current: str = None

    file: UploadedFileInfo = None
