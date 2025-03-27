"""The base class for tool-call responses, and its variants.
"""
from typing import Any, List

from pydantic import BaseModel, Field


class BaseError(BaseModel):
    message: List[str] = Field(default_factory=list, description="The error message")
    error_type: str = Field(description="The type of the error")


class FunctionMismatchError(BaseError):
    message: List[str] = ["Function mismatch."]
    error_type: str = "parallel_function_checker_no_order:cannot_find_match"


class IncorrectValueError(BaseError):
    message: List[str] = ["Incorrect value."]
    error_type: str = "dict_checker:incorrect_value"


class IncorrectTypeForParameterError(BaseError):
    message: List[str] = ["Incorrect type for parameter."]
    error_type: str = "simple_function_checker:incorrect_type"


class MissingOptionalParameterError(BaseError):
    message: List[str] = ["Missing optional parameter."]
    error_type: str = "simple_function_checker:missing_optional"


class MissingRequiredParameterError(BaseError):
    message: List[str] = ["Missing required parameter."]
    error_type: str = "simple_function_checker:missing_required"


class UnexpectedParameterError(BaseError):
    message: List[str] = ["Unexpected parameter."]
    error_type: str = "simple_function_checker:unexpected_param"


class WrongFunctionCountError(BaseError):
    message: List[str] = ["Wrong number of functions."]
    error_type: str = "simple_function_checker:wrong_count"


class WrongFunctionNameError(BaseError):
    message: List[str] = ["Function name is not found in model output."]
    error_type: str = "simple_function_checker:wrong_func_name"


class NullCategoryError(BaseError):
    message: List[str] = ["Category is not found."]
    error_type: str = "runner:null_category"


class BaseResponse(BaseModel):
    formatted: bool = Field(default=False, description="Whether a completion is of the correct format")
    valid: bool = Field(default=False, description="Whether all tool calls are of the correct format")
    correct: bool = Field(default=False, description="Whether the result is correct if applicable")
    results: List[Any] | None = Field(default=None, description="Results of the tool calls")
    errors: List[BaseError] | None = Field(default=None, description="Errors of the tool calls")
