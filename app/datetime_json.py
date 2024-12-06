import json
from datetime import date, datetime
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return str(json.JSONEncoder.default(self, obj))
