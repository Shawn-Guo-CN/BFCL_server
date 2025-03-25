"""
Utils for the executable test category.

Reference: https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/bfcl/eval_checker/eval_runner_helper.py
"""

from tqdm import tqdm

from bfcl.constants.config import (
    EXECTUABLE_API_GROUND_TRUTH_FILE_PATH,
    RED_FONT,
    RESET,
    REST_API_GROUND_TRUTH_FILE_PATH,
)
from bfcl.utils._apply_function_credential_config import apply_function_credential_config
from bfcl.utils.exceptions import BadAPIStatusError
from bfcl.utils.ops import load_file, write_list_of_dicts_to_file


def api_status_sanity_check_rest():
    # We only need to import the executable_checker_rest in this function. So a local import is used.
    from bfcl.eval.exec.checkers import executable_checker_rest

    ground_truth_dummy = load_file(REST_API_GROUND_TRUTH_FILE_PATH)

    # Use the ground truth data to make sure the API is working correctly
    apply_function_credential_config(input_path=REST_API_GROUND_TRUTH_FILE_PATH)

    ground_truth_replaced = load_file(REST_API_GROUND_TRUTH_FILE_PATH)
    write_list_of_dicts_to_file(REST_API_GROUND_TRUTH_FILE_PATH, ground_truth_dummy)

    correct_count = 0
    errors = []
    for idx, data in tqdm(
        enumerate(ground_truth_replaced),
        total=len(ground_truth_replaced),
        desc="API Status Test (REST)",
    ):
        status = executable_checker_rest(data["ground_truth"], idx)
        if status["valid"]:
            correct_count += 1
        else:
            errors.append((data, status))

    if correct_count != len(ground_truth_replaced):
        raise BadAPIStatusError(
            errors,
            f"{len(ground_truth_replaced) - correct_count} / {len(ground_truth_replaced)}",
        )


def api_status_sanity_check_executable():
    from bfcl.eval.exec.checkers import executable_checker_simple

    ground_truth = load_file(EXECTUABLE_API_GROUND_TRUTH_FILE_PATH)
    correct_count = 0
    errors = []
    for data in tqdm(ground_truth, total=len(ground_truth), desc="API Status Test (Non-REST)"):
        status = executable_checker_simple(
            data["ground_truth"][0],
            data["execution_result"][0],
            data["execution_result_type"][0],
            True,
        )
        if status["valid"]:
            correct_count += 1
        else:
            errors.append((data, status))

    if correct_count != len(ground_truth):
        raise BadAPIStatusError(errors, f"{len(ground_truth) - correct_count} / {len(ground_truth)}")


def display_api_status_error(rest_error, executable_error, display_success=False):
    if not rest_error and not executable_error:
        if display_success:
            print("🟢 All API Status Test Passed!")
        return None

    print(f"\n{RED_FONT}{'-' * 18} Executable Categories' Error Bounds Based on API Health Status {'-' * 18}{RESET}\n")

    if rest_error:
        print(
            "❗️ Warning: Unable to verify health of executable APIs used in executable test category (REST). "
            "Please contact API provider.\n"
        )
        print(f"{rest_error.error_rate} APIs affected:\n")
        for data, status in rest_error.errors:
            print(f"  - Test Case: {data['ground_truth']}")
            print(f"    Error Type: {status['error_type']}\n")

    if executable_error:
        print(
            "❗️ Warning: Unable to verify health of executable APIs used in executable test categories (Non-REST). "
            "Please contact API provider.\n"
        )
        print(f"{executable_error.error_rate} APIs affected:\n")
        for data, status in executable_error.errors:
            print(f"  - Test Case: {data['ground_truth'][0]}")
            print(f"    Error Type: {status['error_type']}\n")

    print(f"{RED_FONT}{'-' * 100}\n{RESET}")


def get_executable_expected_output(prompt_file_path):
    # Before we run the evaluation, we need to add the "execution_result" field to the prompt file,
    # using the ground truth data.
    prompt_content = load_file(prompt_file_path)
    exec_dict = {}
    for item in tqdm(prompt_content, desc="Getting Executable Expected Output"):
        execution_result = []
        ground_truth = item["ground_truth"]
        for i in range(len(ground_truth)):
            exec(
                "from bfcl.eval_checker.executable_eval.data.executable_python_function import *"
                + "\nresult="
                + ground_truth[i],
                exec_dict,
            )
            execution_result.append(exec_dict["result"])
        item["execution_result"] = execution_result

    write_list_of_dicts_to_file(prompt_file_path, prompt_content)
