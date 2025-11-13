from enum import StrEnum
from pydantic import BaseModel

class KnowledgeDocument(BaseModel):
    id: str
    title: str
    content: str

class KnowledgeDomain(StrEnum):
    pass