# Oracle

A local chatbot with context search.

![Screenshots](oracle/gradio/screenshots.png)

## Features

- Streaming responses
- Convenient debug info
- Working examples
- Hardware agnostic
- Open user registration
- Session persistence

## Requirements

- Python 3.10+

## Setup

```sh
# https://docs.python.org/3/library/venv.html#how-venvs-work
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Index the example source
python -m oracle.contexts.self.index
```

Install `pytorch` via https://pytorch.org/get-started/locally/ for hardware acceleration.

## Running

```sh
python -m oracle.gradio
```

The server configuration is located in `oracle/gradio/__init__.py`.
Logs are in `.history/`.

Models set to automatically download from HuggingFace may take quite
a while to download the first time they are selected.

## Adding a new language generation model

Add a module in  `oracle/models/` that defines:

- `class Model:`
    - `name: str` - The model name to show in the GUI.
    - `reply(message: str, **kwargs) -> Iterator[str]` - Reply to the message (preferably by yielding chunks).
        - `motive: str` - Add a system prompt.
        - `context: List[str]` - Add context to the prompt.
        - `style: str` - Request a repsonse style.
    - `log: Optional[str]` - Any information useful for debugging the last `reply()` call
        (preferably the complete prompt and response).

The easiest way to do this is to subclass `oracle.models.TransformersModel` with:

- `class Model(oracle.models.TransformersModel):`
    - `name: str` - The model name to show in the GUI.
    - `model_id: str` - The Model ID hosted by HuggingFace.
        (This also accepts a local path to a pretrained model.)
    - `max_tokens: int` - The maximum number of tokens that the model supports.


See `oracle/models/stable_beluga_7b.py` for an example.

## Adding new sources of context

Add a module in `oracle/contexts/` that defines:

- `class Context`
    - `name: str` - The source name to show in the GUI.
    - `motive: str` - The default system prompt for caoching the model on
        using the context.
    - `find(message: str): -> Iterator[str]` - The method for finding sources of context
        for a given message.

See the files in `oracle/contexts/self/` for an example.

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
    class leans heavily on `AutoTokenizer` and `AutoModelForCausalLM`
    from `transformers` to simplify loading a large language model
    from HuggingFace. The model builds a prompt string, then runs
    the model in a separate thread to stream the response.
- `oracle.contexts` contains sources of context used to improve
    responses with domain specific information. Since the input size
    of models are finite, the context should break the information
    down into coherent snippets.
- `oracle.contexts.self.index` contains an example context that allows
    this project to chat about its own source code. The files are
    split into chunks, embedded into vectors using `BAAI/bge-base-en`,
    stored in a Chroma database, and indexed for fast searching.
