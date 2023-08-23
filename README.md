![Oracle](oracle/gradio/icon.png)

# Oracle

A local AI chatbot with context search.

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

## Adding sources

Add a module in `contexts/` that defines:

- `name: str` - The source name to show in the GUI.
- `motive: str` - The system prompt that coaches the model on how to
    use the content.
- `find(str): -> List[str]` - A function for finding sources of context
    for a given question.

See `contexts/oracle/` for an example.
