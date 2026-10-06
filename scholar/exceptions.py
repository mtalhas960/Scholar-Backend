"""
Scholar.io — Custom Exception Handler
Flatten DRF errors into consistent { "error": "message" } shape.
"""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Flatten DRF errors into the consistent { "error": "message" } shape."""
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        messages = []
        for value in response.data.values():
            if isinstance(value, list):
                messages.append(str(value[0]) if value else "")
            else:
                messages.append(str(value))
        text = "; ".join(m for m in messages if m) or "Request failed."
        response.data = {"error": text}

    return response
