from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from oracle import Context, Model, Style


class ChatOptions(Schema):
    message = fields.String(required=True)
    context = fields.String(
        load_default='None',
        validate=OneOf(Context.names),
    )
    model = fields.String(
        load_default=Model.names[-1],
        validate=OneOf(Model.names),
    )
    motive = fields.String(
        load_default=Context.map['None'].motive,
        metadata={
            'x-examples': {
                context.name: context.motive
                for context in Context.map.values()
            }
        }
    )
    style = fields.String(
        load_default='None',
        metadata={'x-examples': Style.names}
    )
    use_keywords = fields.Boolean(load_default=False)
