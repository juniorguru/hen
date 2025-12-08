from datetime import date
from enum import StrEnum, auto
from typing import Any, Self

from githubkit.exception import RequestFailed
from githubkit.rest import FullRepository
from pydantic import BaseModel, ConfigDict, field_serializer


class Status(StrEnum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    DONE = auto()


class RepositoryContext(BaseModel):
    username: str
    pin_index: int | None
    repo: FullRepository
    readme: str | None
    languages: dict[str, int] | None


class Outcome(BaseModel):
    rule: str
    status: Status
    message: str
    docs_url: str


class Insight(BaseModel):
    name: str
    value: Any
    collect: bool = False


class ProjectInfo(BaseModel):
    name: str
    title: str | None
    source_url: str
    demo_url: str | None
    description: str | None
    priority: int | None
    start_on: date
    end_on: date
    topics: list[str]
    languages: list[str]


class Info(BaseModel):
    name: str | None
    bio: str | None
    email: str | None
    location: str | None
    linkedin_url: str | None
    avatar_url: str
    projects: list[ProjectInfo] = []


class Summary(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: str
    outcomes: list[Outcome]
    info: Info | None = None
    error: Exception | None = None

    @field_serializer("error")
    def error_to_str(error: Exception) -> str | None:  # type: ignore
        if error is None:
            return None
        if isinstance(error, RequestFailed):
            return f"HTTP {error.response.status_code} - {error.request.method.upper()} {error.request.url}"
        return str(error)

    @classmethod
    def create(
        cls,
        username: str,
        results: list[Outcome | Insight],
        error: Exception | None = None,
    ) -> Self:
        outcomes = [result for result in results if isinstance(result, Outcome)]
        insights = {
            result.name: result.value
            for result in results
            if isinstance(result, Insight)
        }
        return cls(
            username=username,
            outcomes=outcomes,
            info=Info(**insights) if insights else None,
            error=error,
        )
