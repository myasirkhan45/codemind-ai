from pydantic import BaseModel, Field

REPO_PATTERN = r"^[\w.-]+$"


class IngestRequest(BaseModel):
    url: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    repo: str = Field(pattern=REPO_PATTERN, max_length=100)
    file: str | None = None


class AgentRequest(BaseModel):
    task: str = Field(min_length=3)
    repo: str = Field(pattern=REPO_PATTERN, max_length=100)
    file: str | None = None


class AgentResponse(BaseModel):
    answer: str
    sources: list[str]