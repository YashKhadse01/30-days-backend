
from django.http import JsonResponse


def health_check(request):
    return JsonResponse(
        {
            "status": "success",
            "message": "Day 21 Django Internals API",
            "middleware": "RequestTimingMiddleware",
        }
    )
