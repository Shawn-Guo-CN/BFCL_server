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
uv sync --extra "dev"
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
    "id": "irrelevance_5",
    "completion": "I don't have the correct tool to answer the question."
}

response = requests.get("http://127.0.0.1:1123/run", json=test_call)
print('Response:', response.json())
print('valid:', response.json()['valid'])
print('correct:', response.json()['correct'])
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

- [ ] Checker for the `Multi-Turn` category.