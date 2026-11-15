
import logging
from time import perf_counter

logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
    """
    Measure request processing time and add a response header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = perf_counter()

        # Request phase: before the view
        response = self.get_response(request)

        # Response phase: after the view
        duration_ms = (perf_counter() - start_time) * 1000

        response["X-Response-Time-ms"] = f"{duration_ms:.2f}"

        logger.info(
            "HTTP %s %s -> %s (%.2f ms)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )

        return response
