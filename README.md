# Oracle

A local AI chatbot with context search.

![Screenshots](oracle/gradio/screenshots.png)

## Features

- Streaming responses
- Convenient debug info
- Working examples
- Hardware agnostic
- Thoughtfully abstracted

## Setup

```sh
# https://docs.python.org/3/library/venv.html#how-venvs-work
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Download the example model (requires git-lfs)
git lfs install
git lfs clone https://huggingface.co/stabilityai/StableBeluga-7B models/StableBeluga-7B

# Index the example source
python -m contexts.oracle.index
```

Install `pytorch` via https://pytorch.org/get-started/locally/ for hardware acceleration.

## Running

```sh
python -m oracle.gradio
```

The server configuration is located in `oracle/gradio/__init__.py`.
Logs are in `history/`.

## Adding models

1. Clone models into the `models` folder.
2. Subclass `ChatModel` in `oracle/models.py`.
3. Import and use your `model` in `oracle/controller.py`.

- `reply(message: str, **kwargs) -> Iterator[str]` - Stream a reply to the message.
    - `motive: str` - Add a system prompt.
    - `context: List[str]` - Add context to the prompt.
    - `style: str` - Request a repsonse style.

See `StableBeluga7B` in `oracle/models.py` for an example.

## Adding sources

Add a module in `contexts/` that defines:

- `class Context`
    - `name: str` - The source name to show in the GUI.
    - `motive: str` - The default system prompt for caoching the model on
        using the context.
    - `find(message: str): -> Iterator[str]` - The method for finding sources of context
        for a given message.

See `contexts/oracle/` for an example.

## Architecture

- `oracle.gradio.gui` uses Gradio to build a web client. The Blocks
    framework declares a component layout and event handlers. This
    renders server-side and streams updates over a websocket.
- `oracle.session` is an event loop for streaming status updates and
    partial results. This is intentionally model and UI agnostic to
    allow customization with minimal API surface area. This handles
    caching, session state, logging, error handling, and mostly
    importantly generating human-friendly status events to explain
    long running model activities.
- `oracle.models` contains low level text generation models. The base
    class and example model lean heavily on `AutoTokenizer` and
    `AutoModelForCausalLM` from `transformers` to simplify loading
    a large language model. The model builds a prompt string, then
    runs the model in a separate thread to stream the response.
- `contexts.oracle.index` contains an example context that allows
    this project to chat about its own source code. The files are
    split into chunks, embedded into vectors using `BAAI/bge-base-en`,
    stored in a Chroma database, and indexed for fast searching.
