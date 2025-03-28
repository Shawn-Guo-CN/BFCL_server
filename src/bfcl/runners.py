"""The Tool-Call Runner class.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import bfcl.eval.exec.executable_python_functions as exec_funcs
from bfcl.constants.category_mappings import TestCategory
from bfcl.constants.id_mapper import IDMapper
from bfcl.eval.ast.checkers import ast_checker
from bfcl.schemas.responses import ASTRunTimeError, BaseResponse
from bfcl.schemas.tool_calls import ToolCallList

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
            TestCategory.SIMPLE: self.run_ast_calls,
            TestCategory.LIVE_SIMPLE: self.run_ast_calls,
            TestCategory.MULTIPLE: self.run_ast_calls,
            TestCategory.LIVE_MULTIPLE: self.run_ast_calls,
            TestCategory.PARALLEL: self.run_ast_calls,
            TestCategory.LIVE_PARALLEL: self.run_ast_calls,
            TestCategory.PARALLEL_MULTIPLE: self.run_ast_calls,
            TestCategory.LIVE_PARALLEL_MULTIPLE: self.run_ast_calls,
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
    def validate_raw_completion_format(self, completion: str) -> bool:
        """Validate the raw completion from the model.

        Args:
            completion (str): The completion to validate.

        Returns:
            True if the completion is valid, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def decode_tool_calls(self, completion: str) -> ToolCallList | None:
        """Decode model completion into a tool call.

        Args:
            raw_completion (str): The raw completion to decode.

        Returns:
            A `ToolCallList` object or None if the completion cannot be decoded.
        """
        raise NotImplementedError

    def run_relevance_calls(
        self, id: str, tool_calls: List[Dict[str, Any]] | None, category: TestCategory
    ) -> BaseResponse:
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
        response.valid = isinstance(tool_calls, ToolCallList)
        response.correct = response.valid
        return response

    def run_irrelevance_calls(
        self, id: str, tool_calls: List[Dict[str, Any]] | None, category: TestCategory
    ) -> BaseResponse:
        """Run the tool call for the irrelevance category.

        Args:
            tool_call (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            A `BaseResponse` object
        """
        response = BaseResponse()
        response.valid = tool_calls is None or not isinstance(tool_calls, ToolCallList)
        response.correct = response.valid
        return response

    def run_executable_calls(
        self, id: str, tool_calls: List[Dict[str, Any]] | None, category: TestCategory
    ) -> BaseResponse:
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

    def run_ast_calls(self, id: str, tool_calls: List[Dict[str, Any]] | None, category: TestCategory) -> BaseResponse:
        """Run the tool call for the AST category.

        Args:
            tool_call (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            A `BaseResponse` object

        TODO: check the correctness of the results
        """
        assert isinstance(tool_calls, ToolCallList), "Tool calls must be a `ToolCallList` object."

        try:
            checker_result = ast_checker(
                func_description=self.id_mapper.get_function_description(id),
                tool_calls=tool_calls,
                possible_answer=self.id_mapper.get_ground_truth(id),
                language=self.id_mapper.get_language(id),
                category_name=category.value[1],
            )
        except Exception as e:
            logger.info(f"Failed to run AST tool calls: {tool_calls}, error: {str(e)}")
            return BaseResponse(
                errors=[ASTRunTimeError(message=["AST checker failed for unknown reason."])],
                results=None,
            )

        return checker_result

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

        # get the category
        category = self.id_mapper.get_category(id)
        if category is None:
            response.errors[0].message = [f"Category for id {id} is not found."]
            return response.model_dump()

        # validate the tool call format for non-irrelevance categories
        if not category in [TestCategory.IRRELEVANCE, TestCategory.LIVE_IRRELEVANCE]:
            response.formatted = self.validate_raw_completion_format(completion)
            if not response.formatted:
                return response.model_dump()
        response.formatted = True

        # decode the tool calls
        tool_calls = self.decode_tool_calls(completion)

        # run the tool calls
        handler = self.category_handlers.get(category)
        if handler is None:
            response.errors[0].message = [f"Handler for category {category} is not supported yet."]
            return response.model_dump()

        category_response = handler(id, tool_calls, category)

        response.valid = category_response.valid
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

    def validate_raw_completion_format(self, completion: str) -> bool:
        try:
            json.loads(completion)
            return True
        except:
            return False

    def decode_tool_calls(self, completion: str) -> List[Dict[str, Any]] | None:
        """Decode the raw completion into a tool call.

        Args:
            completion (str): The raw completion to decode.

        Returns:
            A list of tool calls or None if the completion cannot be decoded.
        """
        try:
            json_dict = json.loads(completion)
            tool_calls = ToolCallList.from_json_dict_list(json_dict)
            return tool_calls
        except:
            return None  # None for empty tool calls
