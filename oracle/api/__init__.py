"""
A Flask API for running the core chat operation and
advertising its parameter options.
"""

import json
from datetime import datetime

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, Response, stream_with_context
from flask_apispec import doc, use_kwargs
from flask_apispec.extension import FlaskApiSpec

from oracle import chat
from .schema import ChatOptions


class Config:
    APISPEC_SPEC  = APISpec(
        title='Oracle',
        version=str(datetime.now()),
        openapi_version='3.0.2',
        plugins=[MarshmallowPlugin()],
    )
    APISPEC_SWAGGER_UI_URL = '/'
    APISPEC_SWAGGER_URL = '/spec'

app = Flask(__name__)
app.config.from_object(Config)
docs = FlaskApiSpec(app, document_options=False)

plain_text = {'text/plain': {'schema': {'type': 'string'}}}

@docs.register
@app.get('/chat')
@doc(tags=['Chat'])
@doc(description='Get a response from the chat bot')
@doc(responses={'200': {'content': plain_text}})
@use_kwargs(ChatOptions, location='query')
def chat_text(**chat_options):
    *_, final = chat(**chat_options)
    return final.get('response', ''), {"Content-Type": "text/plain"}

x_ndjson = {'application/x-ndjson': {'schema': {'type': 'string'}}}

@docs.register
@app.post('/chat')
@doc(tags=['Chat'])
@doc(description='Stream response events from the chat bot')
@doc(responses={'200': {'content': x_ndjson}})
@use_kwargs(ChatOptions, location='query')
def chat_stream(**chat_options):
    return Response(
        stream_with_context(
            json.dumps(event) + '\n'
            for event in chat(**chat_options)
        ),
        content_type="application/x-ndjson",
    )
