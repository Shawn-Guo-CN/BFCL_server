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

    @classmethod
    def from_json_dict(cls, json_dict: Dict[str, Any]) -> "ToolCall":
        """Convert a JSON dictionary to a tool call."""
        assert len(json_dict) == 1, "The JSON dictionary must contain exactly one key-value pair."
        return cls(function_name=list(json_dict.keys())[0], parameters=list(json_dict.values())[0])


class ToolCallList(BaseModel):
    tool_calls: List[ToolCall]

    def __len__(self) -> int:
        return len(self.tool_calls)

    def __getitem__(self, index: int) -> ToolCall:
        return self.tool_calls[index]

    @classmethod
    def from_ground_truth(cls, ground_truth: List[Dict[str, Any]]) -> "ToolCallList":
        """Convert the ground truth to a list of tool calls."""
        return cls(tool_calls=[ToolCall.from_ground_truth(item) for item in ground_truth])

    @classmethod
    def from_json_dict_list(cls, json_dict_list: List[Dict[str, Any]]) -> "ToolCallList":
        """Convert a JSON list of dictionaries to a list of tool calls."""
        return cls(tool_calls=[ToolCall.from_json_dict(item) for item in json_dict_list])
