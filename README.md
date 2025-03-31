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
uv run bfcl --host 0.0.0.0 --port 1123
```

### Run a tool call

An example of running a tool call is as follows:

```bash
import requests

test_call = {
    "id": "simple_2",
    "completion": '[{"math.hypot": {"x": 4, "y": 5, "z": 0}}]'
}

response = requests.get("http://127.0.0.1:1123/run", json=test_call)
print('response:', response.json())
print('formatted:', response.json()['formatted'])
print('valid:', response.json()['valid'])
print('correct:', response.json()['correct'])
print('results:', response.json()['results'])
print('errors:', response.json()['errors'])
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
- [ ] Add more examples for function calls in plain json.
- [ ] Support for installing as a dependency.
- [ ] Runner for the `Multi-Turn` category.
