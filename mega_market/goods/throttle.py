from rest_framework import throttling


class GetReadRateThrottle(throttling.AnonRateThrottle):
    scope = 'read_anon'


class GetModifyRateThrottle(throttling.AnonRateThrottle):
    scope = 'modify_anon'
