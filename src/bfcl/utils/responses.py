"""The base class for tool-call responses, and its variants.
"""
from typing import Any, List

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    valid: bool = Field(default=False, description="Whether all tool calls are valid")
    correct: bool = Field(default=False, description="Whether the result is correct if applicable")
    result: List[Any] = Field(default_factory=list, description="Results of the tool calls")
