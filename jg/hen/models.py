from datetime import datetime
from enum import StrEnum, auto
from typing import Any, Self

from githubkit.rest import FullRepository
from pydantic import BaseModel, field_serializer


class Status(StrEnum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    DONE = auto()


class Outcome(BaseModel):
    rule: str
    status: Status
    message: str
    docs_url: str


class Insight(BaseModel):
    name: str
    value: Any
    collect: bool = False


class Project(BaseModel):
    name: str
    title: str | None
    source_url: str
    live_url: str | None
    description: str | None
    priority: int | None
    start_at: datetime
    end_at: datetime
    topics: list[str]


class Summary(BaseModel):
    username: str
    outcomes: list[Outcome]
    insights: dict[str, Any]
    error: Exception | None = None

    class Config:
        arbitrary_types_allowed = True

    @field_serializer("error")
    def error_to_str(error: Exception) -> str | None:  # type: ignore
        return str(error) if error else None

    @classmethod
    def create(
        cls,
        username: str,
        results: list[Outcome | Insight],
        error: Exception | None = None,
    ) -> Self:
        return cls(
            username=username,
            outcomes=[result for result in results if isinstance(result, Outcome)],
            insights={
                result.name: result.value
                for result in results
                if isinstance(result, Insight)
            },
            error=error,
        )


class RepositoryContext(BaseModel):
    repo: FullRepository
    readme: str | None
    is_profile: bool
    pin: int | None
