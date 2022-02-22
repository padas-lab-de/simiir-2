"""Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "to_json()"
method and uses it to encode the object if found.

This is used to allow us to return a search response object as a JSON string.

Solution from: http://stackoverflow.com/a/18561055
"""
from json import JSONEncoder

def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default # save unmodified default
JSONEncoder.default = _default # replacement