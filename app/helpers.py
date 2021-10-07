import json

from aiohttp.web import Response, json_response


class ResponseJSON(Response):
    def __init__(self, data, **kwargs):
        text = json.dumps({"data": data})
        kwargs["text"] = text
        kwargs["content_type"] = "application/json"
        super().__init__(**kwargs)


class ResponseERROR(Response):
    def __init__(self, message, **kwargs):
        text = json.dumps({"message": message})
        kwargs["text"] = text
        kwargs["content_type"] = "application/json"
        super().__init__(**kwargs)
