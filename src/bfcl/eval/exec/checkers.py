"""Checkers for the EXEC category.

Reference: https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/bfcl/eval_checker/executable_eval/executable_checker.py
"""

import time
from typing import List

import requests  # noqa: F401 - requests is used implicitly in eval() function

from bfcl.constants.config import REAL_TIME_MATCH_ALLOWED_DIFFERENCE
from bfcl.schemas.exceptions import NoAPIKeyError
from bfcl.schemas.responses import (
    BaseResponse,
    ExecutionError,
    ExecutionResultCountMismatchError,
    ExecutionResultKeyMismatchError,
    ExecutionResultMismatchError,
    ExecutionResultTypeError,
    ExecutionStatusError,
)


#### Main function ####
def executable_checker_rest(func_call: str, ground_truth: dict | List[dict]):
    if "https://geocode.maps.co" in func_call:
        time.sleep(2)
    if "requests_get" in func_call:
        func_call = func_call.replace("requests_get", "requests.get")
    try:
        response = eval(func_call)
    except Exception as e:
        return BaseResponse(
            valid=False,
            correct=False,
            results=[],
            errors=[ExecutionError(message=[f"Execution failed. {str(e)}"])],
        )

    try:
        if response.status_code == 200:
            try:
                if isinstance(ground_truth, dict):
                    if isinstance(response.json(), dict):
                        if set(ground_truth.keys()) == set(response.json().keys()):
                            return BaseResponse(valid=True, correct=True, results=[response.json()], errors=[])
                        return BaseResponse(
                            valid=False,
                            correct=False,
                            results=[response.json()],
                            errors=[
                                ExecutionResultKeyMismatchError(
                                    message=[
                                        (
                                            f"Key inconsistency between expected ({set(ground_truth.keys())}) and "
                                            f"actual ({set(response.json().keys())})"
                                        )
                                    ]
                                )
                            ],
                        )
                    return BaseResponse(
                        valid=False,
                        correct=False,
                        results=[response.json()],
                        errors=[
                            ExecutionResultTypeError(message=[f"Expected dictionary, but got {type(response.json())}"])
                        ],
                    )
                elif isinstance(ground_truth, list):
                    if isinstance(response.json(), list):
                        if len(ground_truth) != len(response.json()):
                            return BaseResponse(
                                valid=False,
                                correct=False,
                                results=[response.json()],
                                errors=[
                                    ExecutionResultCountMismatchError(
                                        message=[
                                            (
                                                f"Response list length inconsistency between expected "
                                                f"({len(ground_truth)}) and actual ({len(response.json())})"
                                            )
                                        ]
                                    )
                                ],
                            )

                        else:
                            for i in range(len(ground_truth)):
                                if set(ground_truth[i].keys()) != set(response.json()[i].keys()):
                                    return BaseResponse(
                                        valid=False,
                                        correct=False,
                                        results=[response.json()],
                                        errors=[
                                            ExecutionResultKeyMismatchError(
                                                message=[
                                                    (
                                                        f"Key inconsistency between expected "
                                                        f"({set(ground_truth[i].keys())}) and "
                                                        f"actual ({set(response.json()[i].keys())})"
                                                    )
                                                ]
                                            )
                                        ],
                                    )

                            return BaseResponse(valid=True, correct=True, results=[response.json()], errors=[])
                    else:
                        return BaseResponse(
                            valid=False,
                            correct=False,
                            results=[response.json()],
                            errors=[
                                ExecutionResultTypeError(message=[f"Expected list, but got {type(response.json())}"])
                            ],
                        )
                return BaseResponse(
                    valid=False,
                    correct=False,
                    results=[response.json()],
                    errors=[
                        ExecutionResultTypeError(
                            message=[f"Expected dictionary or list, but got {type(response.json())}"]
                        )
                    ],
                )
            except Exception as e:
                return BaseResponse(
                    valid=False,
                    correct=False,
                    results=[response],
                    errors=[
                        ExecutionStatusError(
                            message=[
                                f"Error in execution and type checking. Status code: {response.status_code}. "
                                f"Error: {str(e)}"
                            ]
                        )
                    ],
                )
        else:
            return BaseResponse(
                valid=False,
                correct=False,
                results=[response],
                errors=[
                    ExecutionStatusError(
                        message=[f"Execution result status code is not 200, got {response.status_code}"]
                    )
                ],
            )
    except Exception as e:
        return BaseResponse(
            valid=False,
            correct=False,
            results=[response],
            errors=[ExecutionStatusError(message=[f"Cannot get status code of the response. Error: {str(e)}"])],
        )


def executable_checker_non_rest(
    tool_calls: str | List[str],
    ground_truth: dict | List[dict],
    func_description: dict,
    test_category: str,
) -> BaseResponse:
    if "multiple" in test_category or "parallel" in test_category:
        assert isinstance(tool_calls, list), "Tool calls must be a list for `multiple` and `parallel` categories."
        return executable_checker_parallel_no_order(
            tool_calls,
            ground_truth,
            func_description[0]["execution_result_type"],
        )

    else:
        if isinstance(tool_calls, list) and len(tool_calls) != 1:
            return BaseResponse(
                valid=False,
                correct=False,
                errors=[
                    ExecutionResultCountMismatchError(
                        message=["Wrong number of functions."], error_type="exec_non_rest_checker:wrong_count"
                    )
                ],
            )

        return executable_checker_simple(
            tool_calls[0],
            ground_truth[0],
            func_description[0]["execution_result_type"][0],
            False,
        )


#### Helper functions for Exec ####
def patten_matcher(exec_output, expected_result, function_call, is_sanity_check):
    result = {"valid": True, "error": [], "error_type": "executable_checker:unclear"}

    if type(exec_output) != type(expected_result):
        return BaseResponse(
            errors=[
                ExecutionResultTypeError(
                    message=[
                        f"Wrong execution result type for {repr(function_call)}. "
                        f"Expected type: {type(expected_result)}, but got: {type(exec_output)}."
                    ],
                    error_type="executable_checker:wrong_result_type",
                )
            ],
        )

    if type(exec_output) == dict:
        # We loose the requirement for the sanity check as the expected result used in the sanity check might not be
        # the most up-to-date one. This happens when the key is a timestamp or a random number.
        if is_sanity_check:
            if len(exec_output) != len(expected_result):
                return BaseResponse(
                    errors=[
                        ExecutionResultCountMismatchError(
                            message=[
                                (
                                    f"Wrong execution result pattern for {repr(function_call)}. "
                                    f"Expect type Dict, but wrong number of elements in the output. "
                                    f"Expected length: {len(expected_result)}, but got: {len(exec_output)}."
                                )
                            ],
                            error_type="executable_checker:wrong_result_type:dict_length",
                        )
                    ]
                )
            else:
                return BaseResponse(
                    valid=True,
                    correct=True,
                    results=[exec_output],
                    errors=[],
                )

        for key, _ in expected_result.items():
            if key not in exec_output:
                return BaseResponse(
                    errors=[
                        ExecutionResultKeyMismatchError(
                            message=[
                                (
                                    f"Wrong execution result pattern for {repr(function_call)}. "
                                    f"Expect type Dict, but key {repr(key)} not found in the model output."
                                )
                            ],
                            error_type="executable_checker:wrong_result_type:dict_key_not_found",
                        )
                    ]
                )
        for key, _ in exec_output.items():
            if key not in expected_result:
                return BaseResponse(
                    errors=[
                        ExecutionResultKeyMismatchError(
                            message=[
                                (
                                    f"Wrong execution result pattern for {repr(function_call)}. "
                                    f"Expect type Dict, but key {repr(key)} not expected in the model output."
                                )
                            ],
                            error_type="executable_checker:wrong_result_type:dict_extra_key",
                        )
                    ]
                )

    if type(exec_output) == list:
        if len(exec_output) != len(expected_result):
            return BaseResponse(
                errors=[
                    ExecutionResultCountMismatchError(
                        message=[
                            (
                                f"Wrong execution result pattern for {repr(function_call)}. "
                                f"Expect type list, but wrong number of elements in the output. "
                                f"Expected length: {len(expected_result)}, but got: {len(exec_output)}."
                            )
                        ],
                        error_type="executable_checker:wrong_result_type:list_length",
                    )
                ]
            )

    return result


def exec_function_call(function_call: str):
    func_name = function_call.split("(")[0]
    exec_dict = {}
    try:
        exec(
            (f"from bfcl.eval.exec.executable_python_functions import {func_name}\n" f"result = {function_call}"),
            exec_dict,
        )
        exec_output = exec_dict["result"]
        return exec_output
    except NoAPIKeyError as e:
        raise e
    except Exception as e:
        return BaseResponse(
            valid=False,
            correct=False,
            errors=[
                ExecutionError(
                    message=[f"Error in execution: {repr(function_call)}. Error: {str(e)}"],
                    error_type="executable_checker:execution_error",
                )
            ],
        )


def executable_checker_simple(
    function_call: str,
    ground_truth_call: str,
    expected_result_type: str,
    is_sanity_check=False,
) -> BaseResponse:
    expected_result = exec_function_call(ground_truth_call)
    if isinstance(expected_result, BaseResponse):
        return expected_result

    exec_output = exec_function_call(function_call)
    if isinstance(exec_output, BaseResponse):
        return exec_output

    # We need to special handle the case where the execution result is a tuple and convert it to a list
    # Because when json is stored, the tuple is converted to a list, and so the expected result is a list
    # when loaded from json
    if isinstance(exec_output, tuple):
        exec_output = list(exec_output)

    if expected_result_type == "exact_match":
        if exec_output != expected_result:
            return BaseResponse(
                errors=[
                    ExecutionResultMismatchError(
                        message=[f"Expected: {expected_result}, but got: {exec_output}."],
                        error_type="executable_checker:wrong_result",
                    )
                ],
            )

    elif expected_result_type == "real_time_match":
        # Allow for 5% difference
        if (type(expected_result) == float or type(expected_result) == int) and (
            type(exec_output) == float or type(exec_output) == int
        ):
            if not (
                expected_result * (1 - REAL_TIME_MATCH_ALLOWED_DIFFERENCE)
                <= exec_output
                <= expected_result * (1 + REAL_TIME_MATCH_ALLOWED_DIFFERENCE)
            ):
                return BaseResponse(
                    errors=[
                        ExecutionResultMismatchError(
                            message=[
                                (
                                    f"Expected: {expected_result}, but got: {exec_output}. "
                                    f"{REAL_TIME_MATCH_ALLOWED_DIFFERENCE * 100}% difference allowed."
                                )
                            ],
                            error_type="executable_checker:wrong_result_real_time",
                        )
                    ],
                )
        else:
            return BaseResponse(
                errors=[
                    ExecutionResultTypeError(
                        message=[
                            f"Wrong execution result for {repr(function_call)}. "
                            f"Expected: {expected_result}, but got: {exec_output}. "
                            f"Type needs to be float or int for real time match criteria."
                        ],
                        error_type="executable_checker:wrong_result_real_time",
                    )
                ],
            )

    else:
        # structural match
        pattern_match_result = patten_matcher(exec_output, expected_result, function_call, is_sanity_check)
        if not pattern_match_result["valid"]:
            return pattern_match_result

    return BaseResponse(
        valid=True,
        correct=True,
        results=[exec_output],
        errors=[],
    )


def executable_checker_parallel_no_order(
    decoded_result: list, expected_exec_result: list, expected_exec_result_type: list
) -> BaseResponse:
    if len(decoded_result) != len(expected_exec_result):
        return BaseResponse(
            errors=[
                ExecutionResultCountMismatchError(
                    message=[
                        f"Wrong number of functions provided. "
                        f"Expected {len(expected_exec_result)}, but got {len(decoded_result)}."
                    ],
                    error_type="value_error:exec_result_count",
                )
            ]
        )

    matched_indices = []
    for i in range(len(expected_exec_result)):
        all_errors = []
        for index in range(len(decoded_result)):
            if index in matched_indices:
                continue

            result = executable_checker_simple(
                decoded_result[index],
                expected_exec_result[i],
                expected_exec_result_type[i],
                False,
            )

            if result.valid:
                matched_indices.append(index)
                break
            else:
                all_errors.extend(result.errors)

        if not result.valid:
            considered_indices = [i for i in range(len(decoded_result)) if i not in matched_indices]
            all_errors.insert(
                0,
                ExecutionResultMismatchError(
                    message=[
                        (
                            f"Could not find a matching function among index {considered_indices} "
                            f"of model output for index {i} of possible answers.",
                        )
                    ],
                    error_type="executable_checker:cannot_find_match",
                ),
            )

    return BaseResponse(
        valid=True,
        correct=True,
        results=[decoded_result],
        errors=[],
    )
