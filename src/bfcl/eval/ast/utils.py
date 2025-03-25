"""The type converters for the AST category.

Refereces:
 - https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/bfcl/eval_checker/ast_eval/type_convertor/java_type_converter.py
 - https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/bfcl/eval_checker/ast_eval/type_convertor/js_type_converter.py

"""

import re
from typing import Dict, List, Union

from bfcl.constants.type_mappings import JAVA_TYPE_CONVERSION, JS_TYPE_CONVERSION


def java_type_converter(value, expected_type, nested_type=None):
    if expected_type not in JAVA_TYPE_CONVERSION:
        raise ValueError(f"Unsupported type: {expected_type}")
    if expected_type == "byte" or expected_type == "short" or expected_type == "integer":
        if not re.match(r"^-?\d+$", value):
            return str(value)  # default to string
        return int(value)
    elif expected_type == "float":
        if not re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?[fF]$", value):
            return str(value)  # default to string
        return float(re.sub(r"[fF]$", "", value))
    elif expected_type == "double":
        if not re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$", value):
            return str(value)  # default to string
        return float(value)
    elif expected_type == "long":
        if not re.match(r"^-?\d+[lL]$", value):
            return str(value)  # default to string
        return int(re.sub(r"[lL]$", "", value))
    elif expected_type == "boolean":
        if value not in ["true", "false"]:
            return str(value)  # default to string
        return parse_java_boolean(value)
    elif expected_type == "char":
        if not re.match(r"^\'.$\'", value):
            return str(value)  # default to string
        return value  # Remove the single quotes
    elif expected_type == "Array" or expected_type == "ArrayList":
        return parse_java_collection(value, expected_type, nested_type)
    elif expected_type == "Set":
        raise NotImplementedError("Set conversion is not implemented")
    elif expected_type == "HashMap":
        return parse_java_collection(value, expected_type, nested_type)
    elif expected_type == "Hashtable":
        raise NotImplementedError("Set conversion is not implemented")
    elif expected_type == "Queue" or expected_type == "Stack":
        raise NotImplementedError(f"{expected_type} conversion is not implemented")
    elif expected_type == "String" or expected_type == "any":
        return str(value)  # we output as string for `any` type
    else:
        raise ValueError(f"Unsupported type: {expected_type}")


def parse_java_boolean(value):
    return value == "true"


def parse_java_collection(input_str: str, type_str: str, nested_type=None) -> Union[List, Dict]:
    if type_str == "ArrayList":
        return parse_arraylist(input_str, nested_type)
    elif type_str == "Array":
        return parse_array(input_str, nested_type)
    elif type_str == "HashMap":
        return parse_hashmap(input_str)
    else:
        raise ValueError(f"Unsupported type: {type_str}")


def parse_arraylist(input_str: str, nested_type=None) -> List:
    match_asList = re.search(r"new\s+ArrayList<\w*>\(Arrays\.asList\((.+?)\)\)", input_str)
    if match_asList:
        elements_str = match_asList.group(1)
        elements = []
        for element_str in elements_str.split(","):
            element_str = element_str.strip()
            if nested_type == "char":
                element = element_str[1:-1]  # Remove the single quotes
            elif nested_type == "String":
                element = element_str[1:-1]  # Remove the double quotes
            else:
                element = (
                    java_type_converter(element_str, nested_type) if nested_type else parse_java_value(element_str)
                )
            elements.append(element)
        return elements

    match_add = re.search(r"new\s+ArrayList<\w*>\(\)\s*\{\{\s*(.+?)\s*\}\}", input_str, re.DOTALL)
    if match_add:
        adds_str = match_add.group(1)
        elements = []
        matches = re.findall(r"add\((.+?)\)", adds_str)
        for match in matches:
            value_str = match.strip()
            if nested_type == "char":
                value = value_str[1:-1]  # Remove the single quotes
            elif nested_type == "String":
                value = value_str[1:-1]  # Remove the double quotes
            else:
                value = java_type_converter(value_str, nested_type) if nested_type else parse_java_value(value_str)
            elements.append(value)
        return elements

    match_empty = re.search(r"new\s+ArrayList<\w*>\(\)", input_str)
    if match_empty:
        return []  # Return an empty list for an empty ArrayList

    return input_str  # default to string


def parse_array(input_str: str, nested_type=None) -> List:
    match = re.search(r"new\s+\w+\[\]\s*\{(.*?)\}", input_str)
    if match:
        elements_str = match.group(1)
        if nested_type:
            elements = [java_type_converter(x.strip(), nested_type) for x in elements_str.split(",") if x.strip()]
        else:
            elements = [parse_java_value(x.strip()) for x in elements_str.split(",") if x.strip()]

        return elements
    else:
        return input_str  # default to string


def parse_hashmap(input_str: str) -> Dict:
    elements = {}
    match = re.search(r"new\s+HashMap<.*?>\s*\(\)\s*\{\s*\{?\s*(.*?)\s*\}?\s*\}", input_str, re.DOTALL)
    if match:
        puts_str = match.group(1)
        if puts_str.strip():
            matches = re.findall(r"put\(\"(.*?)\",\s*(.*?)\)", puts_str)
            for match in matches:
                key = match[0]
                value = parse_java_value(match[1].strip())
                elements[key] = value
        return elements

    match_empty = re.search(r"new\s+HashMap<.*?>\s*\(\)", input_str)
    if match_empty:
        return {}  # Return an empty dictionary for an empty HashMap

    return input_str  # default to string


# This method parses without the information of what each element type is, contrary of the previous
def parse_java_value(value_str: str):
    # check if it's boolean
    if value_str == "true":
        return True
    elif value_str == "false":
        return False
    # check if it's a string
    elif value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    # check if it's a long
    elif re.match(r"^-?\d+[lL]$", value_str):
        return int(value_str[:-1])
    # check if it's a float
    elif re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?[fF]$", value_str):
        return float(re.sub(r"[fF]$", "", value_str))
    # check if it's a integer-like and float-like types (including byte, short, integer, double, etc)
    else:
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                # this assuming all other types are converted to string
                return value_str


# Write tests for the `java_type_converter` function
def test_java_type_converter():
    # Test valid conversions
    assert java_type_converter("true", "boolean") == True
    assert java_type_converter("false", "boolean") == False
    assert java_type_converter("123", "integer") == 123
    assert java_type_converter("-123", "integer") == -123
    assert java_type_converter("3.14f", "float") == 3.14
    assert java_type_converter("-3.14f", "float") == -3.14
    assert java_type_converter("3.14", "double") == 3.14
    assert java_type_converter("-3.14", "double") == -3.14
    assert java_type_converter("123L", "long") == 123
    assert java_type_converter("-123L", "long") == -123
    assert java_type_converter("a", "char") == "a"
    assert java_type_converter("abc", "String") == "abc"
    assert java_type_converter("new int[]{1, 2, 3}", "Array") == [1, 2, 3]
    assert java_type_converter('new ArrayList<>(Arrays.asList("a", "b"))', "ArrayList") == ["a", "b"]
    assert java_type_converter('new HashMap<String, String>() {{ put("key", "value"); }}', "HashMap") == {
        "key": "value"
    }
    assert java_type_converter("3f", "float") == 3.0
    assert java_type_converter("3e3F", "float") == 3e3
    assert java_type_converter("3e-3F", "float") == 3e-3
    assert java_type_converter("3.14e2", "double") == 3.14e2
    assert java_type_converter("3.14e-2", "double") == 3.14e-2
    assert java_type_converter("127", "byte") == 127
    assert java_type_converter("-128", "byte") == -128
    assert java_type_converter("32767", "short") == 32767
    assert java_type_converter("-32768", "short") == -32768
    assert java_type_converter("9223372036854775807L", "long") == 9223372036854775807
    assert java_type_converter("-9223372036854775808L", "long") == -9223372036854775808
    assert java_type_converter("123", "any") == "123"
    assert java_type_converter("abc", "any") == "abc"

    # Test empty collections
    assert java_type_converter("new int[]{}", "Array") == []
    assert java_type_converter("new ArrayList<>()", "ArrayList") == []
    assert java_type_converter("new HashMap<>()", "HashMap") == {}

    # Test collections with mixed types
    assert java_type_converter('new Object[]{1, "abc", true}', "Array") == [
        1,
        "abc",
        True,
    ]
    assert java_type_converter('new ArrayList<>(Arrays.asList(1, "abc", true))', "ArrayList") == [1, "abc", True]
    assert java_type_converter(
        'new HashMap<String, Object>() {{ put("key1", 1); put("key2", "value"); put("key3", true); }}',
        "HashMap",
    ) == {"key1": 1, "key2": "value", "key3": True}

    # Test invalid values
    try:
        java_type_converter("true", "integer")
    except ValueError as e:
        assert str(e) == "Invalid integer value: true"

    try:
        java_type_converter("abc", "integer")
    except ValueError as e:
        assert str(e) == "Invalid integer value: abc"

    try:
        java_type_converter("abc", "long")
    except ValueError as e:
        assert str(e) == "Invalid long value: abc"

    try:
        java_type_converter("3.14", "float")
    except ValueError as e:
        assert str(e) == "Invalid float value: 3.14"

    try:
        java_type_converter("3.14f", "double")
    except ValueError as e:
        assert str(e) == "Invalid double value: 3.14f"

    try:
        java_type_converter("128", "byte")
    except ValueError as e:
        assert str(e) == "Invalid byte value: 128"

    try:
        java_type_converter("32768", "short")
    except ValueError as e:
        assert str(e) == "Invalid short value: 32768"

    try:
        java_type_converter("invalid", "boolean")
    except ValueError as e:
        assert str(e) == "Invalid boolean value: invalid"

    try:
        java_type_converter("abc", "char")
    except ValueError as e:
        assert str(e) == "Invalid char value: abc"

    # Test unsupported types
    try:
        java_type_converter("abc", "Set")
    except NotImplementedError as e:
        assert str(e) == "Set conversion is not implemented"

    try:
        java_type_converter("abc", "Hashtable")
    except NotImplementedError as e:
        assert str(e) == "Set conversion is not implemented"

    try:
        java_type_converter("abc", "Queue")
    except NotImplementedError as e:
        assert str(e) == "Queue conversion is not implemented"

    try:
        java_type_converter("abc", "Stack")
    except NotImplementedError as e:
        assert str(e) == "Stack conversion is not implemented"

    # extra array testing
    assert java_type_converter("new int[]{}", "Array") == []
    assert java_type_converter("new int[] {}", "Array") == []
    assert java_type_converter("new int[] { }", "Array") == []
    assert java_type_converter("new int[]{1,2,3}", "Array") == [1, 2, 3]
    assert java_type_converter("new int[]{1, 2, 3}", "Array") == [1, 2, 3]
    assert java_type_converter("new int[] {1, 2, 3}", "Array") == [1, 2, 3]
    assert java_type_converter("new int[] { 1, 2, 3 }", "Array") == [1, 2, 3]

    # extra hashmap testing
    assert java_type_converter("new HashMap<>()", "HashMap") == {}
    assert java_type_converter("new HashMap<>() {}", "HashMap") == {}
    assert java_type_converter("new HashMap<>() {{}}", "HashMap") == {}
    assert java_type_converter("new HashMap<>() {{ }}", "HashMap") == {}
    assert java_type_converter('new HashMap<String, String>() {{ put("key", "value"); }}', "HashMap") == {
        "key": "value"
    }
    assert java_type_converter('new HashMap<String, String>() {{put("key", "value");}}', "HashMap") == {"key": "value"}
    assert java_type_converter('new HashMap<String, String>() { { put("key", "value"); } }', "HashMap") == {
        "key": "value"
    }
    assert java_type_converter(
        'new HashMap<String, Object>() {{ put("key1", 123); put("key2", true); }}',
        "HashMap",
    ) == {"key1": 123, "key2": True}
    assert java_type_converter(
        'new HashMap<String, Object>() {{ put("key1", "value 1"); put("key2", "value 2"); }}',
        "HashMap",
    ) == {"key1": "value 1", "key2": "value 2"}

    def test_parse_array_long():
        input_str = "new long[]{1L, 2L, 3L}"
        expected_output = [1, 2, 3]
        assert parse_array(input_str, nested_type="long") == expected_output

    def test_parse_array_mixed_long():
        input_str = "new long[]{1L, 2, 3L}"
        expected_output = [1, "2", 3]
        assert parse_array(input_str, nested_type="long") == expected_output

    def test_parse_array_invalid_long():
        input_str = "new long[]{1L, 2.0, 3L}"
        expected_output = [1, "2.0", 3]
        assert parse_array(input_str, nested_type="long") == expected_output

    def test_parse_arraylist_int():
        input_str = "new ArrayList<Integer>(Arrays.asList(1, 2, 3))"
        expected_output = [1, 2, 3]
        assert parse_arraylist(input_str, nested_type="integer") == expected_output

    def test_parse_arraylist_float():
        input_str = "new ArrayList<Float>() {{ add(1.0f); add(2.0f); add(3.0f); }}"
        expected_output = [1.0, 2.0, 3.0]
        assert parse_arraylist(input_str, nested_type="float") == expected_output

    def test_parse_arraylist_double():
        input_str = "new ArrayList<Double>() {{ add(1.0); add(2.0); add(3.0); }}"
        expected_output = [1.0, 2.0, 3.0]
        assert parse_arraylist(input_str, nested_type="double") == expected_output

    def test_parse_arraylist_boolean():
        input_str = "new ArrayList<Boolean>(Arrays.asList(true, false, true))"
        expected_output = [True, False, True]
        assert parse_arraylist(input_str, nested_type="boolean") == expected_output

    def test_parse_arraylist_char():
        input_str = "new ArrayList<Character>() {{ add('a'); add('b'); add('c'); }}"
        expected_output = ["a", "b", "c"]
        print(parse_arraylist(input_str, nested_type="char"))
        assert parse_arraylist(input_str, nested_type="char") == expected_output

    def test_parse_arraylist_string():
        input_str = 'new ArrayList<String>() {{ add("aasdasd"); add("basdasd"); add("casdasd"); }}'
        expected_output = ["aasdasd", "basdasd", "casdasd"]
        print(parse_arraylist(input_str))
        assert parse_arraylist(input_str) == expected_output

    test_parse_array_long()
    test_parse_array_mixed_long()
    test_parse_array_invalid_long()
    test_parse_arraylist_int()
    test_parse_arraylist_float()
    test_parse_arraylist_double()
    test_parse_arraylist_boolean()
    test_parse_arraylist_char()
    test_parse_arraylist_string()
    print("All tests passed successfully!")


def js_type_converter(value, expected_type, nested_type=None):
    if expected_type not in JS_TYPE_CONVERSION:
        raise ValueError(f"Unsupported type: {expected_type}")

    if expected_type == "String":
        if not (value.startswith('"') and value.endswith('"')) and not (value.startswith("'") and value.endswith("'")):
            return str(value)
        return value[1:-1]

    elif expected_type == "integer":
        if not re.match(r"^-?\d+$", value):
            return str(value)  # default to string
        return int(value)
    elif expected_type == "float":
        if not re.match(r"^-?\d+(\.\d+)?$", value):
            return str(value)  # default to string
        return float(value)
    elif expected_type == "Bigint":
        if not re.match(r"^-?\d+n$", value):
            return str(value)  # default to string
        return int(value[:-1])
    elif expected_type == "Boolean":
        if value not in ["true", "false"]:
            return str(value)  # default to string
        return value == "true"
    elif expected_type == "dict":
        return parse_js_collection(value, "dict", nested_type)
    elif expected_type == "array":
        return parse_js_collection(value, "array", nested_type)
    elif expected_type == "any":
        return str(value)
    else:
        raise ValueError(f"Unsupported type: {expected_type}")


def parse_js_collection(code, type_str, nested_type=None):
    code = code.strip()
    if type_str == "array":
        # Regular expression patterns
        array_2d_pattern = r"\[\s*\[.*?\]\s*(,\s*\[.*?\]\s*)*\]|\bnew\s+Array\(\s*\[.*?\]\s*(,\s*\[.*?\]\s*)*\)"
        array_pattern = r"\[(.*?)\]|\bnew\s+Array\((.*?)\)"

        # Check if the code is a 2D array
        array_2d_match = re.match(array_2d_pattern, code)
        try:
            if array_2d_match:
                elements_str = array_2d_match.group(0)
                inner_arrays = re.findall(r"\[(.*?)\]", elements_str)
                elements = []
                for idx, inner_array_str in enumerate(inner_arrays):
                    inner_array_str = inner_array_str.strip()
                    if idx == 0 and inner_array_str.startswith("["):
                        inner_array_str = inner_array_str[1:]
                    inner_array_elements = [e.strip() for e in inner_array_str.split(",")]
                    if nested_type:
                        inner_array = [parse_js_value(e) for e in inner_array_elements]
                    else:
                        inner_array = [parse_js_value(e) for e in inner_array_elements]
                    elements.append(inner_array)
                return elements

            # Check if the code is a 1D array
            array_match = re.match(array_pattern, code)
            if array_match:
                if array_match.group(1) is not None:
                    elements_str = array_match.group(1).strip()
                    if elements_str:
                        elements = elements_str.split(",")
                    else:
                        elements = []
                elif array_match.group(2) is not None:
                    elements_str = array_match.group(2).strip()
                    if elements_str:
                        elements = elements_str.split(",")
                    else:
                        elements = []
                else:
                    elements = []
                if nested_type:
                    elements = [
                        (
                            js_type_converter(e.strip(), nested_type, "String")
                            if (e.strip().startswith("'") or e.strip().startswith('"'))
                            else js_type_converter(e.strip(), nested_type)
                        )
                        for e in elements
                    ]
                else:
                    elements = [parse_js_value(e.strip()) for e in elements]
                return elements
            else:
                return code
        except:
            return code

    elif type_str == "dict":
        if code == "{}":
            return {}  # Return an empty dictionary for an empty object
        dict_pattern = r"\{(.*?)\}"
        # Check if the code is a dictionary
        dict_match = re.match(dict_pattern, code)
        if dict_match:
            try:
                content = dict_match.group(1)
                pairs = re.findall(r"([^:]+):\s*(.*?)(?:,\s*(?=[^,]+:)|$)", content)
                dictionary = {}
                for key, value in pairs:
                    key = key.strip().strip("'\"")
                    value = value.strip()
                    if value.startswith("[") and value.endswith("]"):
                        # Handle array values
                        dictionary[key] = parse_js_collection(value, "array")
                    elif value.startswith("{") and value.endswith("}"):
                        # Handle nested dictionary values
                        dictionary[key] = parse_js_collection(value, "dict")
                    else:
                        dictionary[key] = parse_js_value(value.strip("'\""))
                return dictionary
            except Exception as e:
                print(f"Error parsing dictionary: {e}")
                return code
        else:
            return code  # default to string
    else:
        raise ValueError(f"Unsupported type: {type_str}")


def parse_js_value(value_str: str):
    value_str = value_str.strip()
    if value_str == "true":
        return True
    elif value_str == "false":
        return False
    elif (value_str.startswith('"') and value_str.endswith('"')) or (
        value_str.startswith("'") and value_str.endswith("'")
    ):
        return value_str[1:-1]
    else:
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                return value_str


# Write tests for the `js_type_converter` function
def test_js_type_converter():
    assert js_type_converter("true", "Boolean") == True
    assert js_type_converter("false", "Boolean") == False
    assert js_type_converter("123", "integer") == 123
    assert js_type_converter("3.14", "float") == 3.14
    assert js_type_converter("123n", "Bigint") == 123
    assert js_type_converter("abc", "String") == "abc"
    assert js_type_converter("[1, 2, 3]", "array") == [1, 2, 3]
    assert js_type_converter("new Array(1, 2, 3)", "array") == [1, 2, 3]
    assert js_type_converter("{'key': 'value'}", "dict") == {"key": "value"}
    assert js_type_converter("{'key': 123}", "dict") == {"key": 123}
    assert js_type_converter("{'key': true}", "dict") == {"key": True}

    # Additional test cases
    # Test empty array and dictionary
    assert js_type_converter("[]", "array") == []
    assert js_type_converter("{}", "dict") == {}

    # Test array with mixed types
    assert js_type_converter("[1, 'two', true]", "array") == [1, "two", True]

    # Test dictionary with mixed types
    assert js_type_converter("{'key1': 123, 'key2': 'value', 'key3': false}", "dict") == {
        "key1": 123,
        "key2": "value",
        "key3": False,
    }

    # Test string with special characters

    # Test negative integer and float values
    assert js_type_converter("-123", "integer") == -123
    assert js_type_converter("-3.14", "float") == -3.14

    # Test invalid type
    try:
        js_type_converter("123", "InvalidType")
    except ValueError as e:
        assert str(e) == "Unsupported type: InvalidType"

    # Test invalid integer value
    try:
        js_type_converter("123.45", "integer")
    except ValueError as e:
        assert str(e) == "Invalid integer value: 123.45"

    # Test invalid float value
    try:
        js_type_converter("3.14abc", "float")
    except ValueError as e:
        assert str(e) == "Invalid float value: 3.14abc"

    # Test invalid Bigint value
    try:
        js_type_converter("123", "Bigint")
    except ValueError as e:
        assert str(e) == "Invalid Bigint value: 123"

    # Test invalid boolean value
    try:
        js_type_converter("not_a_boolean", "Boolean")
    except ValueError as e:
        assert str(e) == "Invalid boolean value: not_a_boolean"

    print("All tests passed successfully!")


def test_js_type_converter_nested_array():
    # Test array with nested integers
    assert js_type_converter("[1, 2, 3]", "array", "integer") == [1, 2, 3]
    assert js_type_converter("new Array(4, 5, 6)", "array", "integer") == [4, 5, 6]

    # Test array with nested floats
    assert js_type_converter("[1.1, 2.2, 3.3]", "array", "float") == [1.1, 2.2, 3.3]
    assert js_type_converter("new Array(4.4, 5.5, 6.6)", "array", "float") == [
        4.4,
        5.5,
        6.6,
    ]

    # Test array with nested Bigints
    assert js_type_converter("[1n, 2n, 3n]", "array", "Bigint") == [1, 2, 3]
    assert js_type_converter("new Array(4n, 5n, 6n)", "array", "Bigint") == [4, 5, 6]

    # Test array with nested booleans
    assert js_type_converter("[true, false, true]", "array", "Boolean") == [
        True,
        False,
        True,
    ]
    assert js_type_converter("new Array(false, true, false)", "array", "Boolean") == [
        False,
        True,
        False,
    ]

    # Test array with nested strings
    print(js_type_converter('["hello", "world", "!"]', "array", "String"))
    assert js_type_converter('["hello", "world", "!"]', "array", "String") == [
        "hello",
        "world",
        "!",
    ]
    assert js_type_converter('new Array("foo", "bar", "baz")', "array", "String") == [
        "foo",
        "bar",
        "baz",
    ]

    # Test array with mixed nested types
    assert js_type_converter('[1, "two", true]', "array") == [1, "two", True]
    assert js_type_converter('new Array(3.14, "pi", false)', "array") == [
        3.14,
        "pi",
        False,
    ]

    # Test array with nested arrays
    print(js_type_converter(" [ [1, 2], [3, 4], [5, 6]]", "array", "array"))
    assert js_type_converter(" [ [ 1, 2 ], [ 3,   4], [5, 6]]", "array", "array") == [
        [1, 2],
        [3, 4],
        [5, 6],
    ]  # this example has many weird spacings
    assert js_type_converter("new Array([1, 2], [3, 4], [5, 6])", "array", "array") == [
        [1, 2],
        [3, 4],
        [5, 6],
    ]

    # Test array with nested dictionaries
    assert js_type_converter('[{"key1": 1}, {"key2": 2}, {"key3": 3}]', "array", "dict") == [
        {"key1": 1},
        {"key2": 2},
        {"key3": 3},
    ]
    assert js_type_converter('new Array({"key1": 1}, {"key2": 2}, {"key3": 3})', "array", "dict") == [
        {"key1": 1},
        {"key2": 2},
        {"key3": 3},
    ]

    print("All nested array tests passed successfully!")


def test_js_type_converter_dictionary_with_arrays():
    complex_dict = js_type_converter(
        '{"initialState": initialStateObject, "reducers": reducersMap, "middlewares": ["loggerMiddleware"], "enhancers": ["applyMiddleware", "myMiddleWare"]}',
        "dict",
    )
    assert isinstance(complex_dict, dict)
    assert complex_dict["initialState"] == "initialStateObject"
    assert complex_dict["reducers"] == "reducersMap"
    assert complex_dict["middlewares"] == ["loggerMiddleware"]
    assert complex_dict["enhancers"] == ["applyMiddleware", "myMiddleWare"]
    print("Complex dictionary test passed successfully!")


if __name__ == "__main__":
    test_java_type_converter()
    test_js_type_converter()
    test_js_type_converter_nested_array()
    test_js_type_converter_dictionary_with_arrays()
