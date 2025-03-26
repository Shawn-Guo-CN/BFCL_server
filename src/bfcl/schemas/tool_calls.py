from typing import Any, Dict, List

from pydantic import BaseModel


class ToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

    @classmethod
    def from_ground_truth(cls, ground_truth: Dict[str, Any]) -> List["ToolCall"]:
        """Convert the ground truth to a list of tool calls."""
        assert len(ground_truth) == 1, "Only one tool call is supported for now."
        return cls(tool_name=ground_truth.keys()[0], parameters=ground_truth.values()[0])


class ToolCalls(BaseModel):
    tool_calls: List[ToolCall]

    @classmethod
    def from_ground_truth(cls, ground_truth: List[Dict[str, Any]]) -> "ToolCalls":
        """Convert the ground truth to a list of tool calls."""
        return cls(tool_calls=[ToolCall.from_ground_truth(item) for item in ground_truth])
