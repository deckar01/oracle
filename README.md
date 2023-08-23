# Oracle

A local AI chatbot with context search.

## Setup

```sh
python -m venv .venv
# Run OS specific venv acivate script
pip install -r requirements.txt
# Bootstrap model
git clone https://huggingface.co/stabilityai/StableBeluga-7B models/StableBeluga-7B
# Bootstrap source
python -m contexts.oracle.index
```

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
