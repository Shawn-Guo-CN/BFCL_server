"""This file contains the constants for mapping the test categories to the corresponding files.

Reference: https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/bfcl/constants/category_mapping.py
"""
from enum import Enum

VERSION_PREFIX = "BFCL_v3"

# These are in the PROMPT_PATH
# Commented out ones are not used in the current version of benchmarking
TEST_FILE_MAPPING = {
    "exec_simple": f"{VERSION_PREFIX}_exec_simple.json",
    "exec_parallel": f"{VERSION_PREFIX}_exec_parallel.json",
    "exec_multiple": f"{VERSION_PREFIX}_exec_multiple.json",
    "exec_parallel_multiple": f"{VERSION_PREFIX}_exec_parallel_multiple.json",
    "simple": f"{VERSION_PREFIX}_simple.json",
    "irrelevance": f"{VERSION_PREFIX}_irrelevance.json",
    "parallel": f"{VERSION_PREFIX}_parallel.json",
    "multiple": f"{VERSION_PREFIX}_multiple.json",
    "parallel_multiple": f"{VERSION_PREFIX}_parallel_multiple.json",
    "java": f"{VERSION_PREFIX}_java.json",
    "javascript": f"{VERSION_PREFIX}_javascript.json",
    "rest": f"{VERSION_PREFIX}_rest.json",
    # "sql": f"{VERSION_PREFIX}_sql.json",
    # "chatable": f"{VERSION_PREFIX}_chatable.json",
    # Live Datasets
    "live_simple": f"{VERSION_PREFIX}_live_simple.json",
    "live_multiple": f"{VERSION_PREFIX}_live_multiple.json",
    "live_parallel": f"{VERSION_PREFIX}_live_parallel.json",
    "live_parallel_multiple": f"{VERSION_PREFIX}_live_parallel_multiple.json",
    "live_irrelevance": f"{VERSION_PREFIX}_live_irrelevance.json",
    "live_relevance": f"{VERSION_PREFIX}_live_relevance.json",
    # TODO: support multi-turn
    # Multi-turn Datasets
    # "multi_turn_base": f"{VERSION_PREFIX}_multi_turn_base.json",
    # "multi_turn_miss_func": f"{VERSION_PREFIX}_multi_turn_miss_func.json",
    # "multi_turn_miss_param": f"{VERSION_PREFIX}_multi_turn_miss_param.json",
    # "multi_turn_long_context": f"{VERSION_PREFIX}_multi_turn_long_context.json",
    # "multi_turn_composite": f"{VERSION_PREFIX}_multi_turn_composite.json",
}

TEST_COLLECTION_MAPPING = {
    "all": [
        "exec_simple",
        "exec_parallel",
        "exec_multiple",
        "exec_parallel_multiple",
        "simple",
        "irrelevance",
        "parallel",
        "multiple",
        "parallel_multiple",
        "java",
        "javascript",
        "rest",
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
        # "multi_turn_base",
        # "multi_turn_miss_func",
        # "multi_turn_miss_param",
        # "multi_turn_long_context",
    ],
    # "multi_turn": [
    #     "multi_turn_base",
    #     "multi_turn_miss_func",
    #     "multi_turn_miss_param",
    #     "multi_turn_long_context",
    # ],
    "single_turn": [
        "exec_simple",
        "exec_parallel",
        "exec_multiple",
        "exec_parallel_multiple",
        "simple",
        "irrelevance",
        "parallel",
        "multiple",
        "parallel_multiple",
        "java",
        "javascript",
        "rest",
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
    ],
    "live": [
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
    ],
    "non_live": [
        "exec_simple",
        "exec_parallel",
        "exec_multiple",
        "exec_parallel_multiple",
        "simple",
        "irrelevance",
        "parallel",
        "multiple",
        "parallel_multiple",
        "java",
        "javascript",
        "rest",
    ],
    # TODO: Update this mapping
    "ast": [
        "simple",
        "irrelevance",
        "parallel",
        "multiple",
        "parallel_multiple",
        "java",
        "javascript",
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
    ],
    "executable": [
        "exec_simple",
        "exec_parallel",
        "exec_multiple",
        "exec_parallel_multiple",
        "rest",
    ],
    "non_python": [
        "java",
        "javascript",
    ],
    "python": [
        "exec_simple",
        "exec_parallel",
        "exec_multiple",
        "exec_parallel_multiple",
        "simple",
        "irrelevance",
        "parallel",
        "multiple",
        "parallel_multiple",
        "rest",
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
    ],
    "python_ast": [
        "simple",
        "irrelevance",
        "parallel",
        "multiple",
        "parallel_multiple",
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
    ],
}

MULTI_TURN_FUNC_DOC_FILE_MAPPING = {
    "GorillaFileSystem": "gorilla_file_system.json",
    "MathAPI": "math_api.json",
    "MessageAPI": "message_api.json",
    "TwitterAPI": "posting_api.json",
    "TicketAPI": "ticket_api.json",
    "TradingBot": "trading_bot.json",
    "TravelAPI": "travel_booking.json",
    "VehicleControlAPI": "vehicle_control.json",
}


# TODO: remove the above
class TestCategory(Enum):
    """The categories of the test cases.

    The values are (id, category name, json file of the test prompts, whether ground truth is available)
    """

    # relevance and irrelevance
    LIVE_RELEVENCE = (1, "live_relevence", f"{VERSION_PREFIX}_live_relevance.json", False)
    IRRELEVANCE = (2, "irrelevance", f"{VERSION_PREFIX}_irrelevance.json", False)
    LIVE_IRRELEVANCE = (3, "live_irrelevance", f"{VERSION_PREFIX}_live_irrelevance.json", False)
    # ast
    SIMPLE = (4, "simple", f"{VERSION_PREFIX}_simple.json", True)
    LIVE_SIMPLE = (5, "live_simple", f"{VERSION_PREFIX}_live_simple.json", True)
    MULTIPLE = (6, "multiple", f"{VERSION_PREFIX}_multiple.json", True)
    LIVE_MULTIPLE = (7, "live_multiple", f"{VERSION_PREFIX}_live_multiple.json", True)
    PARALLEL = (8, "parallel", f"{VERSION_PREFIX}_parallel.json", True)
    LIVE_PARALLEL = (9, "live_parallel", f"{VERSION_PREFIX}_live_parallel.json", True)
    PARALLEL_MULTIPLE = (10, "parallel_multiple", f"{VERSION_PREFIX}_parallel_multiple.json", True)
    LIVE_PARALLEL_MULTIPLE = (11, "live_parallel_multiple", f"{VERSION_PREFIX}_live_parallel_multiple.json", True)
    # executable
    EXEC_SIMPLE = (12, "exec_simple", f"{VERSION_PREFIX}_exec_simple.json", True)
    EXEC_PARALLEL = (13, "exec_parallel", f"{VERSION_PREFIX}_exec_parallel.json", True)
    EXEC_MULTIPLE = (14, "exec_multiple", f"{VERSION_PREFIX}_exec_multiple.json", True)
    EXEC_PARALLEL_MULTIPLE = (15, "exec_parallel_multiple", f"{VERSION_PREFIX}_exec_parallel_multiple.json", True)
    # non-python
    JAVA = (16, "java", f"{VERSION_PREFIX}_java.json", True)
    JAVASCRIPT = (17, "javascript", f"{VERSION_PREFIX}_javascript.json", True)
    REST = (18, "rest", f"{VERSION_PREFIX}_rest.json", False)
    # TODO: add multi-turn categories


class TestCollection(Enum):
    """The collections of the test categories."""

    ALL = (0, "all", [cat for cat in TestCategory])
    SINGLE_TURN = (1, "single_turn", [cat for cat in TestCategory if cat.value[0] <= 18])
    LIVE = (2, "live", [cat for cat in TestCategory if cat.name.startswith("LIVE_")])
    NON_LIVE = (3, "non_live", [cat for cat in TestCategory if not cat.name.startswith("LIVE_") and cat.value[0] <= 18])
    AST = (
        4,
        "ast",
        [
            cat
            for cat in TestCategory
            if cat.value[1]
            in [
                # fmt: off
        "simple",
        "irrelevance",
        "parallel",
        "multiple",
        "parallel_multiple",
        "java",
        "javascript",
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
            ]
        ],
    )
    EXECUTABLE = (
        5,
        "executable",
        [cat for cat in TestCategory if cat.value[1].startswith("exec_") or cat.value[1] == "rest"],
    )
    NON_PYTHON = (6, "non_python", [cat for cat in TestCategory if cat.value[1] in ["java", "javascript"]])
    PYTHON = (7, "python", [cat for cat in TestCategory if cat.value[1] not in ["java", "javascript"]])
    PYTHON_AST = (
        8,
        "python_ast",
        [
            cat
            for cat in TestCategory
            if cat.value[1]
            in [
                "simple",
                "irrelevance",
                "parallel",
                "multiple",
                "parallel_multiple",
                "live_simple",
                "live_multiple",
                "live_parallel",
                "live_parallel_multiple",
                "live_irrelevance",
                "live_relevance",
            ]
        ],
    )
    IRRELEVANCE = (9, "irrelevance", [TestCategory.IRRELEVANCE, TestCategory.LIVE_IRRELEVANCE])
    # fmt: on

    def __add__(self, other):
        if isinstance(other, TestCollection):
            return list(self.value[2]) + list(other.value[2])
        raise NotImplementedError


class Category2CollectionMapping:
    """The mapping from the categories to the collections."""

    def __init__(self):
        self.mapping = {}
        for collection in TestCollection:
            for category in collection.value[2]:
                self.mapping[category] = collection

    def get_collection(self, category: TestCategory) -> TestCollection:
        return self.mapping[category]
