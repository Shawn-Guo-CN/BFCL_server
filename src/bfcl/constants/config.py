"""The configuration for running the evaluation.

Reference: https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/bfcl/constants/eval_config.py
"""

from pathlib import Path

PORT = 1123
VLLM_PORT = 1053

REAL_TIME_MATCH_ALLOWED_DIFFERENCE = 0.2

RED_FONT = "\033[91m"
RESET = "\033[0m"

# Construct the full path for other modules to use
script_dir = Path(__file__).parent
# The root directory of the project, relative to the current file location
PROJECT_ROOT = script_dir.parent.parent
PROJECT_ROOT = (script_dir / PROJECT_ROOT).resolve()
BFCL_SRC_ROOT = (PROJECT_ROOT / "bfcl").resolve()

# NOTE: These paths are relative to the PROJECT_ROOT directory.
PROMPT_PATH = (BFCL_SRC_ROOT / "data").resolve()
MULTI_TURN_FUNC_DOC_PATH = (PROMPT_PATH / "multi_turn_func_doc").resolve()
POSSIBLE_ANSWER_PATH = (PROMPT_PATH / "possible_answer").resolve()
DOTENV_PATH = (PROJECT_ROOT / ".venv").resolve()
UTILS_PATH = f"{PROJECT_ROOT}/utils/"

PROMPT_PATH = (PROJECT_ROOT / PROMPT_PATH).resolve()
MULTI_TURN_FUNC_DOC_PATH = (PROJECT_ROOT / MULTI_TURN_FUNC_DOC_PATH).resolve()
POSSIBLE_ANSWER_PATH = (PROJECT_ROOT / POSSIBLE_ANSWER_PATH).resolve()
DOTENV_PATH = (PROJECT_ROOT / DOTENV_PATH).resolve()
UTILS_PATH = (PROJECT_ROOT / UTILS_PATH).resolve()


TEST_IDS_TO_GENERATE_PATH = f"{PROJECT_ROOT}/test_case_ids_to_generate.json"
# These two files are for the API status sanity check
REST_API_GROUND_TRUTH_FILE_PATH = f"{PROJECT_ROOT}/bfcl/eval/exec/data/api_status_check_ground_truth_REST.json"
EXECTUABLE_API_GROUND_TRUTH_FILE_PATH = (
    f"{PROJECT_ROOT}/bfcl/eval/exec/data/api_status_check_ground_truth_executable.json"
)

# This is the ground truth file for the `rest` test category
REST_EVAL_GROUND_TRUTH_PATH = f"{PROJECT_ROOT}/bfcl/eval/exec/data/rest-eval-response_v5.jsonl"
REST_API_GROUND_TRUTH_FILE_PATH = (PROJECT_ROOT / REST_API_GROUND_TRUTH_FILE_PATH).resolve()
EXECTUABLE_API_GROUND_TRUTH_FILE_PATH = (PROJECT_ROOT / EXECTUABLE_API_GROUND_TRUTH_FILE_PATH).resolve()
REST_EVAL_GROUND_TRUTH_PATH = (PROJECT_ROOT / REST_EVAL_GROUND_TRUTH_PATH).resolve()
TEST_IDS_TO_GENERATE_PATH = (PROJECT_ROOT / TEST_IDS_TO_GENERATE_PATH).resolve()
