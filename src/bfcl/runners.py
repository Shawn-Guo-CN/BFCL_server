"""The Tool-Call Runner class.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import bfcl.eval.ast.checkers as ast_checker
import bfcl.eval.exec.executable_python_functions as exec_funcs
from bfcl.constants.category_mappings import TestCategory
from bfcl.constants.id_mapper import IDMapper
from bfcl.utils.responses import BaseResponse

logger = logging.getLogger(__name__)


class BaseRunner(ABC):
    """The base class for all runners."""

    def __init__(self):
        self._null_response = BaseResponse()
        self.id_mapper = IDMapper()

        self.category_handlers = {
            # relevance and irrelevance
            TestCategory.LIVE_RELEVENCE: self.run_relevance_calls,
            TestCategory.IRRELEVANCE: self.run_irrelevance_calls,
            TestCategory.LIVE_IRRELEVANCE: self.run_irrelevance_calls,
            # TODO: implement the following call functions
            # ast
            # TestCategory.SIMPLE: self.run_ast_calls,
            # TestCategory.LIVE_SIMPLE: self.run_ast_calls,
            # TestCategory.MULTIPLE: self.run_ast_calls,
            # TestCategory.LIVE_MULTIPLE: self.run_ast_calls,
            # TestCategory.PARALLEL: self.run_ast_calls,
            # TestCategory.LIVE_PARALLEL: self.run_ast_calls,
            # TestCategory.PARALLEL_MULTIPLE: self.run_ast_calls,
            # TestCategory.LIVE_PARALLEL_MULTIPLE: self.run_ast_calls,
            # executable
            # TestCategory.EXEC_SIMPLE: self.run_executable_calls,
            # TestCategory.EXEC_PARALLEL: self.run_executable_calls,
            # TestCategory.EXEC_MULTIPLE: self.run_executable_calls,
            # TestCategory.EXEC_PARALLEL_MULTIPLE: self.run_executable_calls,
            # non-python
            # TestCategory.JAVA: self.run_ast_calls,
            # TestCategory.JAVASCRIPT: self.run_ast_calls,
            # TestCategory.REST: self.run_executable_calls,
        }

    def _decode_executable_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any] | None:
        """Decode the tool call for the executable category.

        Args:
            tool_call (Dict[str, Any]): The tool call to decode.

        Returns:
            A dictionary with the following keys
                - tool_name (str): The name of the tool to call.
                - call (str): The call to make to the tool.
        """
        parameter_key_value_list = []
        for parameter_name, parameter_value in tool_call["parameters"].items():
            if type(parameter_value) == float:
                # 0.30000000000000004 -> 0.3
                parameter_value = round(parameter_value, 5)
            elif type(parameter_value) == list and len(parameter_value) > 0:
                # [0.30000000000000004, 0.30000000000000004] -> [0.3, 0.3]
                if type(parameter_value[0]) == float:
                    try:
                        tmp_parameter_value = [round(number, 5) for number in parameter_value]
                        parameter_value = tmp_parameter_value
                    except:
                        pass
            elif "_fibonacci_" in tool_call["tool_name"]:
                # we add logic to filter out extremely large input for _fibonacci_ related functions
                if type(parameter_value) in [float, int]:
                    if parameter_value > 100:  # pyright: ignore [reportOperatorIssue]
                        # set a maximum input value as 100
                        parameter_value = 100
            parameter_key_value_list.append(f"{parameter_name}={repr(parameter_value)}")

        return {
            "tool_name": tool_call["tool_name"],
            "call": f"{tool_call['tool_name']}({', '.join(parameter_key_value_list)})",
        }

    def _exec_single_tool_call(self, tool_call: Dict[str, Any]) -> Any:
        """Execute a single tool call.

        Args:
            tool_call (Dict[str, Any]): The tool call to execute.

        Returns:
            A dictionary with the following keys
                - valid (bool): True if the tool call was valid, False otherwise.
                - result (Any): The result of the tool call, `None` if invalid.
        """
        tool_call = self._decode_executable_tool_call(tool_call)
        result = {"valid": False, "result": None}

        # 1. Check if the tool exists
        try:
            # try importing the function from the module
            func = getattr(exec_funcs, tool_call["tool_name"])
            globals()[tool_call["tool_name"]] = func
        except Exception:
            result["result"] = f"Tool {tool_call['tool_name']} does not exist"
            return result

        # 2. Execute the tool
        try:
            _result = eval(tool_call["call"])
            result["valid"] = True
            result["result"] = _result
        except Exception as e:
            result["result"] = f"Failed to execute tool call: {str(e)}"

        return result

    @abstractmethod
    def validate_raw_completion(self, completion: str) -> bool:
        """Validate the raw completion from the model.

        Args:
            completion (str): The completion to validate.

        Returns:
            True if the completion is valid, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def decode_tool_calls(self, completion: str) -> List[Dict[str, Any]] | None:
        """Decode model completion into a tool call.

        Args:
            raw_completion (str): The raw completion to decode.

        Returns:
            A list of dictionaries with the following keys:
                - tool_name (str): The name of the tool to call.
                - parameters (str): The parameters to pass to the tool.
            or None if the completion cannot be decoded.
        """
        raise NotImplementedError

    def run_relevance_calls(self, tool_calls: List[Dict[str, Any]] | None, category: TestCategory) -> BaseResponse:
        """Run the tool call for the relevance category.

        Args:
            tool_call (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            A `BaseResponse` object

        NOTE: `relevence` checks only the validity of the tool calls, not the correctness. See
        `https://github.com/ShishirPatil/gorilla/berkeley-function-call-leaderboard/bfcl/eval_checker/
        eval_runner.py#L309` for the reference.
        """
        response = BaseResponse()
        response.correct = tool_calls is not None
        return response

    def run_irrelevance_calls(self, tool_calls: List[Dict[str, Any]] | None, category: TestCategory) -> BaseResponse:
        """Run the tool call for the irrelevance category.

        Args:
            tool_call (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            A `BaseResponse` object
        """
        response = BaseResponse()
        response.correct = tool_calls is None or len(tool_calls) == 0
        return response

    def run_executable_calls(self, tool_calls: List[Dict[str, Any]] | None, category: TestCategory) -> BaseResponse:
        """Run the tool call for the executable category.

        Args:
            tool_call (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            A dictionary with the following keys
                - valid (bool): True if the tool call was valid, False otherwise.
                - correct (bool, optional): True if the tool call was correct, False otherwise
                - result (list, optional): List of results from each call.

        TODO: check the correctness of the results
        """
        response = BaseResponse()

        # if tool_calls is None, then it's not executable, thus invalid
        if tool_calls is None:
            return response

        result_list = []
        for tool_call in tool_calls:
            result_list.append(self._exec_single_tool_call(tool_call))

        # TODO: check the correctness of the results
        if all(item.get("valid") for item in result_list):
            response.correct = True
            response.result = [d["result"] for d in result_list]

        return response

    def run_ast_calls(self, tool_calls: List[Dict[str, Any]] | None, category: TestCategory) -> BaseResponse:
        """Run the tool call for the AST category.

        Args:
            tool_call (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            A `BaseResponse` object

        TODO: check the correctness of the results
        """
        self._set_ast_helpers()

        response = BaseResponse()
        if tool_calls is None:
            return response
        if isinstance(tool_calls, dict) and len(tool_calls) != 1:
            return response
        _category = category.category_name.split("_")[-1]  # `simple`, `multiple`, or `parallel`

        q_id = self.question_mapper.get_id(tool_calls[0]["user_question"])
        check_result = None
        try:
            check_result = ast_checker(
                func_description=self.function_mapper.get_func_description(q_id),
                tool_calls=tool_calls,
                ground_truth=self.ground_truth_mapper.get_ground_truth(q_id),
                test_category=_category,
            )

            if check_result["valid"]:
                response.correct = True
                response.result = []
        except Exception as e:
            logger.info(f"Failed to run AST tool calls: {tool_calls}, error: {str(e)}")
            return response

        return response

    def run(self, id: str, completion: str) -> Dict[str, Any]:
        """Run the tool call provided.

        Args:
            id (str): The id of the question to run the tool call for.
            completion (str): The completion to run the tool call for.

        Returns:
            A dictionary with the following keys
                - valid (bool): True if the tool call was valid, False otherwise.
                - correct (bool, optional): True if the tool call was correct, False otherwise
                - result (list, optional): List of results from each call.
        """
        response = BaseResponse()
        response.valid = self.validate_raw_completion(completion)
        if not response.valid:
            return response.model_dump()

        category = self.id_mapper.get_category(id)
        if category is None:
            response.errors[0].message = [f"Category for id {id} is not found."]
            return response.model_dump()

        tool_calls = self.decode_tool_calls(completion)
        handler = self.category_handlers.get(category)
        category_response = handler(tool_calls, category)

        response.correct = category_response.correct
        response.results = category_response.results
        response.errors = category_response.errors
        return response.model_dump()

    def get_category(self, id: str) -> str:
        """Get the category for a given id.

        Args:
            id (str): The id of the question to get the category for.

        Returns:
            A dictionary with the following keys
                - category (str): The category of the user question.
        """
        category = self.id_mapper.get_category(id)
        return category.name


class PlainJsonRunner(BaseRunner):
    """The runner for the plain JSON category.

    In this runner, the raw completion should be a JSON object.
    """

    def __init__(self):
        super().__init__()

    def validate_raw_completion(self, completion: str) -> bool:
        return True

    def decode_tool_calls(self, completion: str) -> List[Dict[str, Any]] | None:
        """Decode the raw completion into a tool call.

        Args:
            completion (str): The raw completion to decode.

        Returns:
            A list of tool calls or None if the completion cannot be decoded.
        """
        try:
            return json.loads(completion)
        except:
            return None  # None for empty tool calls
