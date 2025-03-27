from typing import Any, Dict, List

from pydantic import BaseModel


class Parameter(BaseModel):
    name: str
    type: Any
    description: str
    value: Any


class ToolCall(BaseModel):
    function_name: str
    parameters: Dict[str, Any]

    @classmethod
    def from_ground_truth(cls, ground_truth: Dict[str, Any]) -> List["ToolCall"]:
        """Convert the ground truth to a list of tool calls."""
        assert len(ground_truth) == 1, "Only one tool call is supported for now."
        return cls(function_name=list(ground_truth.keys())[0], parameters=list(ground_truth.values())[0])


class ToolCallList(BaseModel):
    tool_calls: List[ToolCall]

    @classmethod
    def from_ground_truth(cls, ground_truth: List[Dict[str, Any]]) -> "ToolCallList":
        """Convert the ground truth to a list of tool calls."""
        return cls(tool_calls=[ToolCall.from_ground_truth(item) for item in ground_truth])
