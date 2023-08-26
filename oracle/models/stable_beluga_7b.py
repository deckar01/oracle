from oracle.models import TransformersModel


class Model(TransformersModel):
    name = 'StableBeluga-7B'
    model_id = 'stabilityai/StableBeluga-7B'
    max_tokens = 4096
