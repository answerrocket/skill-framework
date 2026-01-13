from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class Metadata(BaseModel):
    name: str
    value: str


class LLMFunctionCall(BaseModel):
    name: str
    arguments: str


class LLMMessage(BaseModel):
    role: str
    content: str
    name: str | None = None
    function_call: LLMFunctionCall | None = None


class LLMAvailableFunction(BaseModel):
    name: str
    description: str
    parameters: dict


class LLMDiagnosticPrompt(BaseModel):
    prompt_id: UUID
    variables: str


class DiagnosticItem(BaseModel):
    title: Optional[str] = None
    json: Optional[dict] = None
    functions: Optional[list[LLMAvailableFunction]] = None
    metadata: Optional[list[Metadata]] = None
    debug_platform: Optional[dict] = None
    llm_activity_trace_id: Optional[UUID] = None


class Diagnostic(BaseModel):
    title: str
    # TODO be more specific about allowed types, and make some more generic types for pipelines devs to leverage in the process
    type: str
    items: list[DiagnosticItem]
    skill_id: Optional[UUID] = None

