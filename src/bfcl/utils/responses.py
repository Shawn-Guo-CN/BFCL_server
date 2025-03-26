"""The base class for tool-call responses, and its variants.
"""
from typing import Any, List

from pydantic import BaseModel, Field


class BaseError(BaseModel):
    message: List[str] = Field(default_factory=list, description="The error message")
    error_type: str = Field(description="The type of the error")


class WrongFunctionCountError(BaseError):
    message: List[str] = ["Wrong number of functions."]
    error_type: str = "simple_function_checker:wrong_count"


class BaseResponse(BaseModel):
    valid: bool = Field(default=False, description="Whether all tool calls are valid")
    correct: bool = Field(default=False, description="Whether the result is correct if applicable")
    results: List[Any] | None = Field(default=None, description="Results of the tool calls")
    errors: List[BaseError] | None = Field(default=None, description="Errors of the tool calls")
