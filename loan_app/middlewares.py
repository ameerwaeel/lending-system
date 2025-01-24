class CleanURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.path = request.path.rstrip()
        return self.get_response(request)
