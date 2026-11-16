
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BookAnonThrottle(AnonRateThrottle):
    rate = "5/min"


class BookUserThrottle(UserRateThrottle):
    rate = "10/min"
