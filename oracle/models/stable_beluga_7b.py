"""
An example model that illustrates the simplity of adding
models from HuggingFace.
"""

from .transformers_model import TransformersModel


class Model(TransformersModel):
    name = 'StableBeluga-7B'
    model_id = '../models/StableBeluga-7B'
    max_tokens = 4096

if __name__ == '__main__':
    # Download the model if needed.
    Model()
