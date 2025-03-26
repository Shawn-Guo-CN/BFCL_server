"""This file implements the mappings from the prompt IDs to the categories and ground truth.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from bfcl.constants.category_mappings import TestCategory, TestCollection
from bfcl.constants.config import POSSIBLE_ANSWER_PATH, PROMPT_PATH
from bfcl.utils.tool_calls import ToolCalls

logger = logging.getLogger(__name__)


class IDMapper:
    """The mapper from the prompt IDs to the categories and ground truth."""

    def __init__(self):
        self.id_to_category = {}
        self.id_to_ground_truth = {}
        self.id_to_function_description = {}

        for category in TestCategory:
            with open(Path(PROMPT_PATH) / category.value[2], "r") as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.id_to_category[data["id"]] = category
            if category.value[3]:
                with open(Path(POSSIBLE_ANSWER_PATH) / category.value[2], "r") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        self.id_to_ground_truth[data["id"]] = ToolCalls.from_ground_truth(data["ground_truth"])
            if category in TestCollection.AST.value[2]:
                with open(Path(PROMPT_PATH) / category.value[2], "r") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        self.id_to_function_description[data["id"]] = data["function"]

    def get_category(self, id: str) -> TestCategory:
        """Get the category of the given ID."""
        return self.id_to_category[id]

    def get_ground_truth(self, id: str) -> ToolCalls:
        """Get the ground truth of the given ID."""
        if id not in self.id_to_ground_truth:
            logger.error(f"No ground truth found for the given ID: {id}")
            raise ValueError(f"No ground truth found for the given ID: {id}")
        return self.id_to_ground_truth[id]

    def get_function_description(self, id: str) -> List[Dict[str, Any]]:
        """Get the function description of the given ID."""
        if id not in self.id_to_function_description:
            logger.error(f"No function description found for the given ID: {id}")
            raise ValueError(f"No function description found for the given ID: {id}")
        return self.id_to_function_description[id]
