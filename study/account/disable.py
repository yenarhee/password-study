try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # no-op class for Django < 1.10
    class MiddlewareMixin(object):
        pass

class DisableCSRF(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)