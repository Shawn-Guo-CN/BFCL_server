"""The Tool-Call Runner class.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from bfcl.constants.category_mappings import TestCategory, TestCollection
from bfcl.constants.id_mapper import IDMapper
from bfcl.eval.ast.checkers import ast_checker
from bfcl.eval.exec.checkers import executable_checker_non_rest, executable_checker_rest
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
            TestCategory.EXEC_SIMPLE: self.run_executable_calls,
            TestCategory.EXEC_PARALLEL: self.run_executable_calls,
            TestCategory.EXEC_MULTIPLE: self.run_executable_calls,
            TestCategory.EXEC_PARALLEL_MULTIPLE: self.run_executable_calls,
            # non-python
            TestCategory.JAVA: self.run_ast_calls,
            TestCategory.JAVASCRIPT: self.run_ast_calls,
            TestCategory.REST: self.run_executable_calls,
        }

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

    def run_relevance_calls(self, id: str, tool_calls: ToolCallList | None, category: TestCategory) -> BaseResponse:
        """Run the tool call for the relevance category.

        Args:
            tool_call (ToolCallList): The tool calls to execute.

        Returns:
            A `BaseResponse` object

        NOTE: `relevence` checks only the validity of the tool calls, not the correctness. See
        `https://github.com/ShishirPatil/gorilla/berkeley-function-call-leaderboard/bfcl/eval_checker/
        eval_runner.py#L309` for the reference.
        """
        _, __ = id, category
        response = BaseResponse()
        response.valid = isinstance(tool_calls, ToolCallList)
        response.correct = response.valid
        return response

    def run_irrelevance_calls(
        self, id: str, tool_calls: ToolCallList | str | None, category: TestCategory
    ) -> BaseResponse:
        """Run the tool call for the irrelevance category.

        Args:
            tool_call (ToolCallList | str | None): The tool calls to execute.

        Returns:
            A `BaseResponse` object
        """
        _, __ = id, category
        response = BaseResponse()
        try:
            tool_calls = ToolCallList.from_json_dict_list(json.loads(tool_calls))
        except:
            pass
        response.valid = tool_calls is None or not isinstance(tool_calls, ToolCallList)
        response.correct = response.valid
        return response

    def run_executable_calls(self, id: str, tool_calls: str | None | List[str], category: TestCategory) -> BaseResponse:
        """Run the tool call for the executable category.

        Args:
            tool_calls (str): The tool calls to execute as an eval() python code.

        Returns:
            A `BaseResponse` object

        TODO: check the correctness of the results
        """
        response = BaseResponse()
        _, __ = id, category

        ground_truth = self.id_mapper.get_ground_truth(id)

        if category == TestCategory.REST:
            response = executable_checker_rest(tool_calls[0], ground_truth)
        else:
            func_description = self.id_mapper.get_function_description(id)
            ground_truth = self.id_mapper.get_ground_truth(id)
            response = executable_checker_non_rest(tool_calls, ground_truth, func_description, category.value[1])

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

    def run(self, id: str, completion: str) -> BaseResponse:
        """Run the tool call provided.

        Args:
            id (str): The id of the question to run the tool call for.
            completion (str): The completion to run the tool call for.

        Returns:
            A `BaseResponse` object
        """
        response = BaseResponse()

        # get the category
        category = self.id_mapper.get_category(id)
        if category is None:
            response.errors[0].message = [f"Category for id {id} is not found."]
            return response.model_dump()

        # validate the tool call format for non-irrelevance categories
        if not category in TestCollection.IRRELEVANCE + TestCollection.EXECUTABLE:
            response.formatted = self.validate_raw_completion_format(completion)
            if not response.formatted:
                return response.model_dump()
        response.formatted = True

        # decode the tool calls
        tool_calls = self.decode_tool_calls(completion, category)

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

    def decode_tool_calls(self, completion: str, category: TestCategory) -> List[Dict[str, Any]] | str | None:
        """Decode the raw completion into a tool call.

        Args:
            completion (str): The raw completion to decode.

        Returns:
            A list of tool calls or None if the completion cannot be decoded.
        """
        if category in TestCollection.IRRELEVANCE:
            return completion  # for rest category, the completion is an eval() python code
        elif category in TestCollection.EXECUTABLE:
            try:
                tool_calls = json.loads(completion)
                return tool_calls
            except:
                return None
        else:
            try:
                json_dict = json.loads(completion)
                tool_calls = ToolCallList.from_json_dict_list(json_dict)
                return tool_calls
            except:
                return None  # None for empty tool calls
