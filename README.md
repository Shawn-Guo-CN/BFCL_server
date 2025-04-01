# BFCL_server
Serverised Berkeley Function Calling Leaderboard

## Installation

### Prerequisites

- `Python 3.10+`
- `uv` is installed for dependency management, check [here](https://docs.astral.sh/uv/getting-started/installation/) for an installation guide.

### Installation for serving-only

```bash
git clone git@github.com:Shawn-Guo-CN/BFCL_server.git
cd BFCL_server
uv sync
```


### Installation for development

```bash
git clone git@github.com:Shawn-Guo-CN/BFCL_server.git
cd BFCL_server
# Install development dependencies
uv sync --extra "dev"
# Install pre-commit hooks
pre-commit install --hook-type pre-commit --hook-type pre-push
```

## Quick Start

### Start the server

```bash
uv run bfcl --host 0.0.0.0 --port 1123 --num_workers 8
```

`num_workers` is the number of workers to run the server. You can adjust it according to your machine's CPU cores.

### Run a single tool call

The endpoint for running a single tool call is `/call`.
Examples are provided below.

Note that these calls are all correct, so all of them should return `correct: True`.
For more correct and incorrect examples, please refer to the `src/tests` folder.

```bash
import requests

# example of AST simple
ast_simple_example = {
    "id": "simple_2",
    "completion": '[{"math.hypot": {"x": 4, "y": 5, "z": 0}}]'
}

response = requests.get("http://127.0.0.1:1123/call", json=ast_simple_example)
print('response:', response.json())
print('formatted:', response.json()['formatted'])
print('valid:', response.json()['valid'])
print('correct:', response.json()['correct'])
print('results:', response.json()['results'])
print('errors:', response.json()['errors'])

# example of Irrelevance
irrelevance_example = {
    "id": "live_irrelevance_9-0-9",
    "completion": "I'm sorry, I don't understand. Can you please rephrase your question?"
}
response = requests.get("http://127.0.0.1:1123/call", json=irrelevance_example)
print("correct:", response.json()['correct'])

# example of Relevance
relevance_example = {
    "id": "live_relevance_15-15-0",
    "completion": '[{"test_name": {"arg1": "test_arg1", "arg2": "test_arg2"}}]',
}
response = requests.get("http://127.0.0.1:1123/call", json=relevance_example)
print("correct:", response.json()['correct'])

# example of Java
java_example = {
    "id": "java_2",
    "completion": (
        '[{"FireBirdUtils.getViewSourceWithHeader": {"monitor": "dbMonitor", "view": "EmployeeView", '
        '"source": "SELECT * FROM Employee WHERE status = \'active\'"}}]'
    ),
}
response = requests.get("http://127.0.0.1:1123/call", json=java_example)
print("correct:", response.json()['correct'])

# example of Executable Rest
rest_example = {
    "id": "rest_49",
    "completion": (
        "[\"requests.get('https://api.open-meteo.com/v1/forecast', "
        "params={'latitude': '39.113014', 'longitude': '-105.358887', "
        "'daily': 'temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_sum',"
        "'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'forecast_days': 10, "
        "'timezone': 'auto'})\"]"
    ),
}
response = requests.get("http://127.0.0.1:1123/call", json=rest_example)
print("correct:", response.json()['correct'])

# example of Executable simple
exec_simple_example = {"id": "exec_simple_1", "completion": '["calc_binomial_probability(n=30, k=15, p=0.5)"]'}
response = requests.get("http://127.0.0.1:1123/call", json=exec_simple_example)
print("correct:", response.json()['correct'])
```

### Run multiple tool calls in parallel

The endpoint for running multiple tool calls in parallel is `/calls`.
The input format is a list of tool calls, each with an `id` and a `completion` field.

```bash
import requests

# example of concurrent requests
concurrent_requests_example = [
    {"id": "simple_2", "completion": '[{"math.hypot": {"x": 4, "y": 5, "z": 0}}]'},
    {
        "id": "rest_49",
        "completion": (
            "[\"requests.get('https://api.open-meteo.com/v1/forecast', "
            "params={'latitude': '39.113014', 'longitude': '-105.358887', "
            "'daily': 'temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_sum',"
            "'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'forecast_days': 10, "
            "'timezone': 'auto'})\"]"
        ),
    },
    {
       "id": "java_2",
       "completion": (
           '[{"FireBirdUtils.getViewSourceWithHeader": {"monitor": "dbMonitor", "view": "EmployeeView", '
           '"source": "SELECT * FROM Employee WHERE status = \'active\'"}}]'
       ),
    },
    {"id": "exec_simple_1", "completion": '["calc_binomial_probability(n=30, k=15, p=0.5)"]'},
    {
        "id": "live_irrelevance_9-0-9",
        "completion": "I'm sorry, I don't understand. Can you please rephrase your question?"
    }
]

responses = requests.get("http://127.0.0.1:1123/calls", json=concurrent_requests_example)
print("concurrent responses:", [response['correct'] for response in responses.json()])
```


## Design

### Architecture

We hereby describe the high-level architecture of the project. The main modules are:

- `constants`: contains the constants for running the tool calls.
- `data`: stores the original test prompts and possible answers from [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html).
- `eval`: implements the tool-call runners for each category, including `Irrelevance`, `Executable`, and etc.
- `utils`: contains the utility functions for running the tool calls.
- `main.py`: the main entry of the server, which wraps the tool-call runners as `asgi` apps and parallelise them.

## Features to be added

- [x] Runner for the `AST` category.
- [x] Runner for the `Executable` category.
- [x] Add more examples for function calls in plain json.
- [x] Add example of Executable simple.
- [x] Parallelise the tool-call runners.
- [ ] Support for installing as a dependency.
- [ ] Add entry for constructing prompt set.
- [ ] Runner for the `Multi-Turn` category.
