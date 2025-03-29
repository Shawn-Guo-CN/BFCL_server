"""This file implements the mappings from the prompt IDs to the categories and ground truth.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from bfcl.constants.category_mappings import TestCategory, TestCollection
from bfcl.constants.config import POSSIBLE_ANSWER_PATH, PROMPT_PATH, REST_EVAL_GROUND_TRUTH_PATH
from bfcl.schemas.tool_calls import ToolCallList

logger = logging.getLogger(__name__)


class IDMapper:
    """The mapper from the prompt IDs to the categories and ground truth."""

    def __init__(self):
        self.id_to_category = {}
        self.id_to_language = {}
        self.id_to_ground_truth = {}
        self.id_to_function_description = {}

        for category in TestCategory:
            with open(Path(PROMPT_PATH) / category.value[2], "r") as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.id_to_category[data["id"]] = category
                    if category in TestCollection.PYTHON.value[2]:
                        self.id_to_language[data["id"]] = "python"
                    else:
                        self.id_to_language[data["id"]] = category.value[1]
            if category.value[3]:
                with open(Path(POSSIBLE_ANSWER_PATH) / category.value[2], "r") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        self.id_to_ground_truth[data["id"]] = ToolCallList.from_ground_truth(data["ground_truth"])
            if category in TestCollection.AST.value[2]:
                with open(Path(PROMPT_PATH) / category.value[2], "r") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        self.id_to_function_description[data["id"]] = data["function"]
            if category == TestCategory.REST:
                with open(Path(REST_EVAL_GROUND_TRUTH_PATH), "r") as f:
                    eval_ground_truth = [json.loads(line.strip()) for line in f]
                for idx, data in enumerate(eval_ground_truth):
                    # ground truth for the rest category is a dict or a list of dicts
                    self.id_to_ground_truth[f"rest_{idx}"] = eval_ground_truth[idx]

    def get_category(self, id: str) -> TestCategory:
        """Get the category of the given ID."""
        return self.id_to_category[id]

    def get_ground_truth(self, id: str) -> ToolCallList:
        """Get the ground truth of the given ID."""
        if id not in self.id_to_ground_truth:
            logger.error(f"No ground truth found for the given ID: {id}")
            raise ValueError(f"No ground truth found for the given ID: {id}")
        return self.id_to_ground_truth[id]

    def get_function_description(self, id: str) -> List[Dict[str, Any]]:
        # TODO: make function description a base model
        """Get the function description of the given ID."""
        if id not in self.id_to_function_description:
            logger.error(f"No function description found for the given ID: {id}")
            raise ValueError(f"No function description found for the given ID: {id}")
        return self.id_to_function_description[id]

    def get_language(self, id: str) -> str:
        """Get the language of the given ID."""
        if id not in self.id_to_language:
            logger.error(f"No language found for the given ID: {id}")
            raise ValueError(f"No language found for the given ID: {id}")
        return self.id_to_language[id]
