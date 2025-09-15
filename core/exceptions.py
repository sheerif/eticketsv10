from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from django.conf import settings

def exception_handler(exc, context):
    resp = drf_exception_handler(exc, context)
    if resp is not None:
        return resp
    payload = {"ok": False, "error": "internal_error"}
    if settings.DEBUG:
        payload["detail"] = str(exc)
    return Response(payload, status=500)
