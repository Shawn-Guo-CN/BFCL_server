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
uv run bfcl
```

## Design

### Architecture

We hereby describe the high-level architecture of the project. The main modules are:

- `constants`: contains the constants for running the tool calls.
- `data`: stores the original test prompts and possible answers from [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html).
- `eval`: implements the tool-call runners for each category, including `Irrelevance`, `Executable`, and etc.
- `utils`: contains the utility functions for running the tool calls.
- `main.py`: the main entry of the server, which wraps the tool-call runners as `asgi` apps and parallelise them.

