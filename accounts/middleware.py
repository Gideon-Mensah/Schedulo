from django.utils.deprecation import MiddlewareMixin

class NoStoreForAuthPages(MiddlewareMixin):
    def process_response(self, request, response):
        # Only for logged-in users (protected pages)
        if getattr(request, "user", None) and request.user.is_authenticated:
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        return response
